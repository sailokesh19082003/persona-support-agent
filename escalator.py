"""
Escalation Logic & Human Handoff.

check_escalation() implements the three triggers from the assignment brief:
    1. Low retrieval confidence
    2. Sensitive topics (billing/legal/account-modification keywords)
    3. Repeated frustration across consecutive turns

build_handoff_summary() turns an escalation event into the structured JSON
a human agent would actually want to see.
"""
from src import config


def contains_sensitive_topic(query: str) -> bool:
    q = query.lower()
    return any(keyword in q for keyword in config.SENSITIVE_KEYWORDS)


def best_retrieval_score(context_chunks: list[dict]) -> float:
    if not context_chunks:
        return 0.0
    return max(c["score"] for c in context_chunks)


def check_escalation(query: str, persona: str, context_chunks: list[dict],
                      memory=None) -> list[str]:
    """
    Returns a list of triggered escalation reason codes (empty list = no
    escalation needed). A list (rather than a bool) is returned so the
    handoff summary can explain *why* a human is needed.
    """
    reasons = []

    if not context_chunks or best_retrieval_score(context_chunks) < config.RETRIEVAL_CONFIDENCE_THRESHOLD:
        reasons.append("low_retrieval_confidence")

    if contains_sensitive_topic(query):
        reasons.append("sensitive_topic")

    if memory is not None and persona == "Frustrated User":
        # +1 because the current turn hasn't been recorded in memory yet
        # at the point this check normally runs.
        if memory.consecutive_persona_count("Frustrated User") + 1 >= config.MAX_FRUSTRATION_TURNS:
            reasons.append("repeated_frustration")

    return reasons


_REASON_LABELS = {
    "low_retrieval_confidence": "No sufficiently confident match was found in the knowledge base.",
    "sensitive_topic": "Message touches a billing, legal, or account-modification topic that requires human judgment.",
    "repeated_frustration": "User has shown unresolved frustration across multiple consecutive turns.",
}

_RECOMMENDATIONS = {
    "low_retrieval_confidence": "Have a specialist review the query manually; the knowledge base may be missing this topic.",
    "sensitive_topic": "Route to billing/legal/account-security team per policy before taking any account action.",
    "repeated_frustration": "Prioritize a direct human reply; consider a goodwill gesture (e.g. service credit) if appropriate.",
}


def build_handoff_summary(query: str, persona: str, context_chunks: list[dict],
                           reasons: list[str], memory=None) -> dict:
    """
    Build the structured JSON handoff report a human agent receives,
    matching the shape requested in the assignment (persona, issue summary,
    conversation history, retrieved documents, attempted actions,
    recommended next steps).
    """
    history = []
    if memory is not None:
        history = [
            {"user_message": t["user_message"], "persona": t["persona"]}
            for t in memory.recent(5)
        ]

    attempted_sources = sorted({c["source"] for c in context_chunks}) if context_chunks else []

    recommendations = [_RECOMMENDATIONS[r] for r in reasons if r in _RECOMMENDATIONS]
    if not recommendations:
        recommendations = ["Escalate to a human agent for manual review."]

    return {
        "persona": persona,
        "issue_summary": query.strip(),
        "escalation_reasons": reasons,
        "escalation_reasons_explained": [_REASON_LABELS.get(r, r) for r in reasons],
        "conversation_history": history,
        "documents_consulted": attempted_sources,
        "best_retrieval_score": best_retrieval_score(context_chunks),
        "recommended_next_steps": recommendations,
    }
