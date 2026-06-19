"""
Tests for escalation logic - pure functions, no API key needed.

Run with: pytest tests/test_escalator.py -v
"""
from src import config, escalator
from src.memory import ConversationMemory


def test_sensitive_keyword_detection():
    assert escalator.contains_sensitive_topic("I want a refund immediately")
    assert escalator.contains_sensitive_topic("Please delete my account")
    assert not escalator.contains_sensitive_topic("How do I reset my password?")


def test_low_confidence_triggers_escalation():
    low_conf_chunks = [{"source": "x.md", "section": "N/A", "text": "...", "score": 0.1}]
    reasons = escalator.check_escalation("some query", "Technical Expert", low_conf_chunks)
    assert "low_retrieval_confidence" in reasons


def test_high_confidence_no_sensitive_topic_does_not_escalate():
    good_chunks = [{"source": "x.md", "section": "N/A", "text": "...", "score": 0.9}]
    reasons = escalator.check_escalation("how do I reset my password", "Technical Expert", good_chunks)
    assert reasons == []


def test_sensitive_topic_escalates_even_with_high_confidence():
    good_chunks = [{"source": "billing_refund_policy.txt", "section": "N/A", "text": "...", "score": 0.9}]
    reasons = escalator.check_escalation("I demand an immediate refund!", "Frustrated User", good_chunks)
    assert "sensitive_topic" in reasons


def test_repeated_frustration_triggers_escalation():
    memory = ConversationMemory()
    memory.add_turn("this is broken!", "Frustrated User", escalated=False)
    good_chunks = [{"source": "x.md", "section": "N/A", "text": "...", "score": 0.9}]

    reasons = escalator.check_escalation(
        "still nothing works!", "Frustrated User", good_chunks, memory=memory
    )
    assert "repeated_frustration" in reasons


def test_handoff_summary_structure():
    chunks = [{"source": "billing_refund_policy.txt", "section": "N/A", "text": "...", "score": 0.2}]
    reasons = ["low_retrieval_confidence", "sensitive_topic"]
    summary = escalator.build_handoff_summary("I want a refund", "Frustrated User", chunks, reasons)

    assert summary["persona"] == "Frustrated User"
    assert summary["issue_summary"] == "I want a refund"
    assert set(summary["escalation_reasons"]) == set(reasons)
    assert "billing_refund_policy.txt" in summary["documents_consulted"]
    assert len(summary["recommended_next_steps"]) > 0
