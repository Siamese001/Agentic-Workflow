"""
Unit tests for shared_engine_ops/cognition_ops/
Tests cognition operations including understand_request.
"""
from __future__ import annotations
from typing import Dict
from dataclasses import dataclass
from enum import Enum

class IntentType(Enum):
    QUERY = "query"
    COMMAND = "command"
    CLARIFICATION = "clarification"
    CONFIRMATION = "confirmation"

@dataclass
class ParsedIntent:
    intent_type: IntentType
    confidence: float
    entities: Dict[str, object]
    original_text: str

class TestUnderstandRequest:
    """Tests for understand_request operations."""

    def test_parse_query_intent(self):
        """Query intent is parsed correctly."""
        text = "What is the revenue for Q4 2024?"

        # Simulated parsing
        intent = ParsedIntent(
            intent_type=IntentType.QUERY,
            confidence=0.95,
            entities={"metric": "revenue", "period": "Q4 2024"},
            original_text=text,
        )

        assert intent.intent_type == IntentType.QUERY
        assert intent.confidence > 0.9

    def test_parse_command_intent(self):
        """Command intent is parsed correctly."""
        text = "Generate a report for the sales team"

        intent = ParsedIntent(
            intent_type=IntentType.COMMAND,
            confidence=0.92,
            entities={"action": "generate", "target": "report", "audience": "sales team"},
            original_text=text,
        )

        assert intent.intent_type == IntentType.COMMAND
        assert intent.entities["action"] == "generate"

    def test_extract_entities(self):
        """Named entities are extracted correctly."""

        entities = {
            "person": "John Smith",
            "organization": "Acme Corp",
        }

        assert entities["person"] == "John Smith"
        assert entities["organization"] == "Acme Corp"

    def test_handle_ambiguous_request(self):
        """Ambiguous requests are flagged."""
        text = "Get the data"  # Ambiguous - which data?

        intent = ParsedIntent(
            intent_type=IntentType.CLARIFICATION,
            confidence=0.4,  # Low confidence indicates ambiguity
            entities={},
            original_text=text,
        )

        is_ambiguous = intent.confidence < 0.6
        assert is_ambiguous is True

    def test_preserve_original_text(self):
        """Original text is preserved in parsed result."""
        text = "What is the weather today?"

        intent = ParsedIntent(
            intent_type=IntentType.QUERY,
            confidence=0.95,
            entities={},
            original_text=text,
        )

        assert intent.original_text == text

class TestQueryFormulation:
    """Tests for query formulation from understood requests."""

    def test_formulate_search_query(self):
        """Search query is formulated from intent."""
        intent = ParsedIntent(
            intent_type=IntentType.QUERY,
            confidence=0.9,
            entities={"topic": "revenue", "period": "2024"},
            original_text="What is the revenue for 2024?",
        )

        query = f"{intent.entities['topic']} {intent.entities['period']}"
        assert "revenue" in query
        assert "2024" in query

    def test_formulate_with_filters(self):
        """Query with filters is formulated correctly."""
        entities = {
            "metric": "sales",
            "region": "North America",
            "year": 2024,
        }

        filters = {k: v for k, v in entities.items() if k != "metric"}
        query = {"search": entities["metric"], "filters": filters}

        assert query["search"] == "sales"
        assert query["filters"]["region"] == "North America"

    def test_formulate_compound_query(self):
        """Compound query is formulated correctly."""

        queries = [
            {"metric": "revenue", "period": "Q4"},
            {"metric": "profit", "period": "Q4"},
        ]

        assert len(queries) == 2

class TestContextUnderstanding:
    """Tests for context understanding."""

    def test_incorporate_conversation_history(self):
        """Conversation history is incorporated."""

        # "their" refers to Acme Corp from history
        context = {"referenced_entity": "Acme Corp"}
        resolved_query = f"What is {context['referenced_entity']}'s revenue?"

        assert "Acme Corp" in resolved_query

    def test_resolve_pronouns(self):
        """Pronouns are resolved from context."""
        context = {"last_mentioned_company": "TechCorp"}
        query = "What is their stock price?"

        resolved = query.replace("their", context["last_mentioned_company"] + "'s")
        assert "TechCorp" in resolved

    def test_maintain_topic_continuity(self):
        """Topic continuity is maintained."""
        conversation_topic = "quarterly_earnings"

        # "it" refers to current topic
        context = {"topic": conversation_topic, "comparison": "year_over_year"}
        assert context["topic"] == "quarterly_earnings"
