"""
Tests for the heuristic fallback classifier - this path is used when no
GEMINI_API_KEY is configured, and is exactly what's exercised here so the
test suite can run fully offline / in CI without secrets.

Run with: pytest tests/test_classifier.py -v
"""
from src.classifier import _fallback_classify
from src import config


def test_technical_message_classified_as_technical():
    result = _fallback_classify("My API token returns a 401 error with this config")
    assert result["persona"] == "Technical Expert"


def test_frustrated_message_classified_as_frustrated():
    result = _fallback_classify("This is still not working and I am so frustrated!!")
    assert result["persona"] == "Frustrated User"


def test_executive_message_classified_as_executive():
    result = _fallback_classify("What is the business impact and resolution timeline for this outage?")
    assert result["persona"] == "Business Executive"


def test_result_has_expected_keys():
    result = _fallback_classify("hello")
    assert "persona" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert result["persona"] in config.PERSONAS
