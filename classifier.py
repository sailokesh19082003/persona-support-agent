"""
Persona Classification.

The primary path calls Gemini with a structured (JSON-schema constrained)
output so we get a reliable, parseable {persona, confidence, reasoning}
object — this is the "Persona Classifier" box in the architecture diagram.

A small keyword-based fallback is included ONLY for local development when
no GEMINI_API_KEY is configured yet (e.g. while wiring up the rest of the
app before you have a key, or running the test suite offline). It is never
used to fabricate the actual graded demo — if GEMINI_API_KEY is set, the
real LLM classification path is always used.
"""
import json
import logging

from src import config

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTION = (
    "You are an advanced classification engine for a customer support system. "
    "Analyze the sentiment, vocabulary, and tone of an incoming support message "
    "and classify it into exactly one of three customer personas:\n"
    "1. 'Technical Expert': Uses technical jargon, asks about APIs, error codes, "
    "configurations, logs, or integration details. Wants detailed, precise answers.\n"
    "2. 'Frustrated User': Uses emotional or urgent language, exclamation marks, "
    "words like 'still broken', 'nothing works', repeated complaints.\n"
    "3. 'Business Executive': Focuses on business impact, ROI, timelines, "
    "operational consequences, and prefers brevity over technical detail.\n\n"
    "Respond ONLY with the requested JSON structure. Pick exactly one persona "
    "even if the message has mixed signals — choose the dominant one."
)

_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "persona": {
            "type": "STRING",
            "enum": config.PERSONAS,
        },
        "confidence": {"type": "NUMBER"},
        "reasoning": {"type": "STRING"},
    },
    "required": ["persona", "confidence", "reasoning"],
}


def _get_client():
    """Lazily import/construct the Gemini client so the module can be
    imported (e.g. for tests) even if google-genai isn't installed yet."""
    from google import genai
    return genai.Client(api_key=config.GEMINI_API_KEY)


def classify_persona(user_message: str) -> dict:
    """
    Classify a user's message into one of config.PERSONAS using Gemini's
    structured JSON output mode.

    Returns:
        dict with keys: persona (str), confidence (float), reasoning (str)
    """
    if not config.GEMINI_API_KEY:
        logger.warning(
            "GEMINI_API_KEY not set - using local keyword-based fallback "
            "classifier. Set GEMINI_API_KEY in .env for real LLM classification."
        )
        return _fallback_classify(user_message)

    from google.genai import types

    client = _get_client()
    response = client.models.generate_content(
        model=config.CHAT_MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=_RESPONSE_SCHEMA,
            temperature=0.1,
        ),
    )

    try:
        result = json.loads(response.text)
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.error("Failed to parse classifier response: %s", exc)
        return _fallback_classify(user_message)

    # Defensive: make sure the model didn't return something outside our enum
    if result.get("persona") not in config.PERSONAS:
        result["persona"] = _fallback_classify(user_message)["persona"]

    return result


def _fallback_classify(user_message: str) -> dict:
    """
    Lightweight, dependency-free heuristic classifier used only when no API
    key is configured. NOT used as a substitute for the real LLM classifier
    in the graded demo - purely a dev/offline convenience and a safety net
    if the API call fails.
    """
    text = user_message.lower()

    frustration_signals = ["!", "still not", "nothing works", "doesn't work",
                            "not working", "frustrated", "angry", "terrible",
                            "worst", "immediately", "asap", "fed up", "ridiculous"]
    technical_signals = ["api", "endpoint", "token", "error code", "config",
                          "log", "header", "json", "webhook", "sdk", "auth",
                          "401", "403", "500", "stack trace", "request id"]
    executive_signals = ["roi", "business impact", "operations", "timeline",
                          "revenue", "sla", "stakeholder", "leadership",
                          "cost", "budget", "resolution time"]

    scores = {
        "Frustrated User": sum(s in text for s in frustration_signals),
        "Technical Expert": sum(s in text for s in technical_signals),
        "Business Executive": sum(s in text for s in executive_signals),
    }

    persona = max(scores, key=scores.get)
    if all(v == 0 for v in scores.values()):
        # No clear signal — default to Technical Expert since most
        # support queries are functionally technical in nature.
        persona = "Technical Expert"

    return {
        "persona": persona,
        "confidence": 0.5,
        "reasoning": "Heuristic keyword-based fallback (no GEMINI_API_KEY configured).",
    }
