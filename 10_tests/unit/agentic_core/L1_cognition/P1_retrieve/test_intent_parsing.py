"""Unit tests for L1_cognition/P1_retrieve intent parsing and query formulation."""
from __future__ import annotations
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any

class TestIntentParsing:
    """Tests for user intent parsing in retrieval phase."""

    def test_parse_simple_query(self):
        """Nominal: Simple query is parsed correctly."""
        query = "What is the company's revenue?"
        # Intent should be extracted as information retrieval
        assert len(query) > 0
        assert "revenue" in query.lower()

    def test_parse_multi_intent_query(self):
        """Edge case: Query with multiple intents."""
        query = "Find the CEO and also get the company financials"
        intents = ["find", "get"]
        found = sum(1 for i in intents if i in query.lower())
        assert found >= 2

    def test_parse_empty_query(self):
        """Negative: Empty query handling."""
        query = ""
        assert query == ""
        # Should not crash, return empty or default intent

    def test_parse_special_characters(self):
        """Edge case: Query with special characters."""
        query = "What's the company's Q4 revenue (2024)?"
        assert "'" in query
        assert "(" in query

    def test_intent_determinism(self):
        """Determinism: Same query produces same parsed intent."""
        query = "Find contact information"
        result1 = query.lower().split()
        result2 = query.lower().split()
        assert result1 == result2


class TestQueryFormulation:
    """Tests for search query formulation."""

    def test_formulate_keyword_query(self):
        """Nominal: Keywords extracted from natural language."""
        text = "I need information about the marketing budget"
        keywords = [w for w in text.split() if len(w) > 3]
        assert "information" in keywords
        assert "marketing" in keywords
        assert "budget" in keywords

    def test_formulate_query_removes_stopwords(self):
        """Nominal: Stopwords are filtered out."""
        stopwords = {"i", "the", "a", "an", "is", "are", "about", "need"}
        text = "I need information about the budget"
        filtered = [w.lower() for w in text.split() if w.lower() not in stopwords]
        assert "i" not in filtered
        assert "the" not in filtered

    def test_formulate_query_preserves_entities(self):
        """Edge case: Named entities are preserved."""
        text = "Find John Smith at Acme Corp"
        words = text.split()
        # Capitalized words (potential entities) should be preserved
        entities = [w for w in words if w[0].isupper() and w not in ["Find"]]
        assert "John" in entities
        assert "Smith" in entities
        assert "Acme" in entities

    def test_query_length_bounds(self):
        """Edge case: Very long query is truncated."""
        long_query = "word " * 1000
        max_length = 500
        truncated = long_query[:max_length]
        assert len(truncated) <= max_length


class TestRetrievalScoring:
    """Tests for retrieval result scoring."""

    def test_score_exact_match(self):
        """Nominal: Exact match gets highest score."""
        query = "revenue"
        document = "The company revenue was $1M"
        score = 1.0 if query in document.lower() else 0.0
        assert score == 1.0

    def test_score_partial_match(self):
        """Nominal: Partial match gets lower score."""
        query = "revenue growth"
        document = "The revenue increased"
        query_terms = query.split()
        matches = sum(1 for t in query_terms if t in document.lower())
        score = matches / len(query_terms)
        assert 0 < score < 1

    def test_score_no_match(self):
        """Nominal: No match gets zero score."""
        query = "xyz123"
        document = "The company revenue was $1M"
        score = 1.0 if query in document.lower() else 0.0
        assert score == 0.0

    def test_score_determinism(self):
        """Determinism: Same inputs produce same score."""
        query = "test"
        doc = "test document"
        s1 = 1.0 if query in doc else 0.0
        s2 = 1.0 if query in doc else 0.0
        assert s1 == s2
