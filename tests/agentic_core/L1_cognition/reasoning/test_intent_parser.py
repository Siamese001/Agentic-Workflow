"""Tests for intent_parser - user intent classification."""
import pytest
from agentic_core.L1_cognition.reasoning.intent_parser import IntentParser


class TestIntentParser:
    def test_init(self):
        p = IntentParser()
        assert p is not None

    def test_parse_question(self):
        p = IntentParser()
        result = p.parse("What is X?")
        assert result.intent in ("question", "query")

    def test_parse_command(self):
        p = IntentParser()
        result = p.parse("Delete file x.")
        assert result.intent in ("command", "action")

    def test_parse_confidence_score(self):
        p = IntentParser()
        result = p.parse("Hello")
        assert 0.0 <= result.confidence <= 1.0

    def test_parse_with_context(self):
        p = IntentParser()
        result = p.parse("yes", context={"prior": "Run the script?"})
        assert result.intent is not None

    def test_extract_entities(self):
        p = IntentParser()
        result = p.parse("Open file foo.py at line 42")
        assert hasattr(result, "entities")

    def test_unsupported_input(self):
        p = IntentParser()
        result = p.parse("")
        assert result.intent == "unknown"
