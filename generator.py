"""
Persona-Adaptive Response Generator.

Combines: user query + classified persona + retrieved context chunks ->
a grounded, persona-styled response, OR an escalation if the
confidence/sensitivity/repeated-frustration checks fail first.

This is intentionally checked BEFORE calling the LLM for the final answer:
there's no point spending a generation call (and risking a hallucinated
answer) on a query we already know should go to a human.
"""
import logging

from src import config, escalator

logger = logging.getLogger(__name__)

_PERSONA_INSTRUCTIONS = {
    "Technical Expert": (
        "You are a Senior Systems Engineer answering a technically fluent user. "
        "Provide precise, structured detail: root-cause explanation, exact "
        "configuration values, API parameters, error codes, and step-by-step "
        "instructions where relevant. Do not oversimplify or pad with reassurance "
        "the user didn't ask for."
    ),
    "Frustrated User": (
        "You are a calm, empathetic Customer Care Specialist speaking to someone "
        "who is frustrated. Open with a brief, genuine acknowledgment of the "
        "inconvenience (one sentence, not over-the-top). Then give simple, "
        "concrete action steps as a short bulleted list. Avoid technical jargon "
        "and avoid long paragraphs."
    ),
    "Business Executive": (
        "You are a concise Client Relations Director speaking to a business "
        "stakeholder. Lead with the direct answer and business impact, then a "
        "brief resolution timeline if relevant. Keep it short - no unnecessary "
        "technical detail or configuration steps unless explicitly asked."
    ),
}

_ESCALATION_MESSAGES = {
    "Technical Expert": (
        "I wasn't able to find a documented resolution for this with sufficient confidence. "
        "I'm escalating this to a human specialist with full technical context attached so they "
        "can dig into logs/configuration directly."
    ),
    "Frustrated User": (
        "I understand this is frustrating, and I don't want to give you a guess instead of a real "
        "answer. I'm connecting you with a human support specialist right now who can resolve this properly."
    ),
    "Business Executive": (
        "This requires manual review before I can give you a reliable answer or timeline. "
        "I'm escalating to a specialist now and they will follow up directly."
    ),
}


def _get_client():
    from google import genai
    return genai.Client(api_key=config.GEMINI_API_KEY)


def generate_response(user_query: str, persona: str, context_chunks: list[dict],
                       memory=None) -> dict:
    """
    Returns:
        {
          "escalated": bool,
          "response": str,
          "handoff_summary": dict | None,
          "escalation_reasons": list[str],
        }
    """
    reasons = escalator.check_escalation(user_query, persona, context_chunks, memory=memory)

    if reasons:
        handoff = escalator.build_handoff_summary(user_query, persona, context_chunks, reasons, memory=memory)
        return {
            "escalated": True,
            "response": _ESCALATION_MESSAGES.get(persona, _ESCALATION_MESSAGES["Technical Expert"]),
            "handoff_summary": handoff,
            "escalation_reasons": reasons,
        }

    persona_instructions = _PERSONA_INSTRUCTIONS.get(persona, _PERSONA_INSTRUCTIONS["Technical Expert"])
    context_text = "\n\n".join(
        f"Source [{c['source']} - {c['section']}]:\n{c['text']}" for c in context_chunks
    )

    full_system_prompt = (
        f"{persona_instructions}\n\n"
        "CRITICAL RULES:\n"
        "- Base your answer ONLY on the FACTUAL CONTEXT DOCUMENTS below.\n"
        "- If the documents don't fully cover something, say so plainly instead of guessing.\n"
        "- Never invent policy details, prices, or steps not present in the context.\n\n"
        f"FACTUAL CONTEXT DOCUMENTS:\n{context_text}"
    )

    if not config.GEMINI_API_KEY:
        # Allows the rest of the app (UI, retrieval, escalation) to be
        # demoed/tested even before a key is added.
        response_text = (
            "[DEV MODE - no GEMINI_API_KEY set] Based on the retrieved context above, "
            "a real Gemini call would generate a persona-styled answer here. "
            f"Top source: {context_chunks[0]['source']} (score {context_chunks[0]['score']})."
        )
    else:
        from google.genai import types
        client = _get_client()
        result = client.models.generate_content(
            model=config.CHAT_MODEL,
            contents=user_query,
            config=types.GenerateContentConfig(
                system_instruction=full_system_prompt,
                temperature=0.2,
            ),
        )
        response_text = result.text

    return {
        "escalated": False,
        "response": response_text,
        "handoff_summary": None,
        "escalation_reasons": [],
    }
