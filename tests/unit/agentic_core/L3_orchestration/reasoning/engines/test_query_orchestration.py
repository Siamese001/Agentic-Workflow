"""Tests for query orchestration components."""

import pytest

from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
    HybridSearchEngine,
    HybridSearchResult,
)
from agentic_core.L3_orchestration.reasoning.engines.query_intent_detector import (
    QueryIntent,
    QueryIntentDetector,
)


def test_query_intent_detector_semantic():
    """Test semantic query detection."""
    detector = QueryIntentDetector()

    # Semantic patterns
    assert detector.detect_intent("how to use this function") == QueryIntent.SEMANTIC
    assert detector.detect_intent("what is the purpose of this class") == QueryIntent.SEMANTIC
    assert detector.detect_intent("explain the implementation") == QueryIntent.SEMANTIC


def test_query_intent_detector_structural():
    """Test structural query detection."""
    detector = QueryIntentDetector()

    # Structural patterns
    assert detector.detect_intent("calls this function") == QueryIntent.STRUCTURAL
    assert detector.detect_intent("imports from this module") == QueryIntent.STRUCTURAL
    assert detector.detect_intent("callers of this method") == QueryIntent.STRUCTURAL
    assert detector.detect_intent("depends on this component") == QueryIntent.STRUCTURAL


def test_query_intent_detector_hybrid():
    """Test hybrid query detection."""
    detector = QueryIntentDetector()

    # Mixed patterns
    assert (
        detector.detect_intent("how to use this and what it calls") == QueryIntent.HYBRID
        or detector.detect_intent("how to use this and what it calls") == QueryIntent.SEMANTIC
    )


def test_query_intent_detector_confidence():
    """Test confidence scoring."""
    detector = QueryIntentDetector()

    # High confidence (multiple matches)
    confidence = detector.get_confidence("calls X and imports Y")
    assert confidence >= 0.4  # 2 matches * 0.2 = 0.4

    # Low confidence (no matches)
    confidence = detector.get_confidence("random text without patterns")
    assert confidence == 0.3

    # Medium confidence (single match)
    confidence = detector.get_confidence("calls function")
    assert confidence >= 0.2


def test_query_intent_detector_empty_query():
    """Test query intent detection with empty query."""
    detector = QueryIntentDetector()

    assert detector.detect_intent("") == QueryIntent.SEMANTIC
    assert detector.detect_intent(None) == QueryIntent.SEMANTIC


def test_query_intent_detector_non_string_input():
    """Test query intent detection with non-string input."""
    detector = QueryIntentDetector()

    assert detector.detect_intent(123) == QueryIntent.SEMANTIC
    assert detector.detect_intent([]) == QueryIntent.SEMANTIC


def test_governance_filters_layer():
    """Test governance filter by layer."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(chunk_id="1", content="test1", metadata={"layer": "L2"}),
        HybridSearchResult(chunk_id="2", content="test2", metadata={"layer": "L3"}),
        HybridSearchResult(chunk_id="3", content="test3", metadata={"layer": "Unknown"}),
    ]

    filtered = engine._apply_governance_filters(results, {"layers": ["L2"]})
    assert len(filtered) == 1
    assert filtered[0].chunk_id == "1"


def test_governance_filters_entity_type():
    """Test governance filter by entity type."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(chunk_id="1", content="test1", metadata={"entity_type": "function"}),
        HybridSearchResult(chunk_id="2", content="test2", metadata={"entity_type": "class"}),
        HybridSearchResult(chunk_id="3", content="test3", metadata={"entity_type": "module"}),
    ]

    filtered = engine._apply_governance_filters(results, {"entity_types": ["function", "class"]})
    assert len(filtered) == 2


def test_governance_filters_multiple():
    """Test governance filters with multiple criteria."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(
            chunk_id="1", content="test1", metadata={"layer": "L2", "entity_type": "function"}
        ),
        HybridSearchResult(
            chunk_id="2", content="test2", metadata={"layer": "L3", "entity_type": "function"}
        ),
        HybridSearchResult(chunk_id="3", content="test3", metadata={"layer": "L2", "entity_type": "class"}),
    ]

    filtered = engine._apply_governance_filters(
        results,
        {"layers": ["L2"], "entity_types": ["function"]},
    )
    assert len(filtered) == 1
    assert filtered[0].chunk_id == "1"


def test_context_budget_enforcement():
    """Test context budget enforcement."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(chunk_id=f"{i}", content=f"test{i}", combined_score=0.9 - i * 0.1)
        for i in range(10)
    ]

    # No truncation needed
    filtered = engine.enforce_context_budget(results, max_tokens=2000, avg_tokens_per_chunk=100)
    assert len(filtered) == 10

    # Truncation needed (2000 tokens / 100 per chunk = 20 chunks, but we have 10, so no truncation)
    # Let's use a smaller budget
    filtered = engine.enforce_context_budget(results, max_tokens=500, avg_tokens_per_chunk=100)
    assert len(filtered) == 5  # 500 / 100 = 5 chunks
    assert filtered[0].chunk_id == "0"  # Highest score kept


def test_context_budget_no_truncation():
    """Test context budget when no truncation needed."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(chunk_id="1", content="test1", combined_score=0.9),
        HybridSearchResult(chunk_id="2", content="test2", combined_score=0.8),
    ]

    filtered = engine.enforce_context_budget(results, max_tokens=4000, avg_tokens_per_chunk=100)
    assert len(filtered) == 2


def test_context_budget_division_by_zero():
    """Test context budget with zero avg_tokens_per_chunk."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(chunk_id="1", content="test1", combined_score=0.9),
    ]

    with pytest.raises(ValueError, match="must be positive"):
        engine.enforce_context_budget(results, max_tokens=4000, avg_tokens_per_chunk=0)

    with pytest.raises(ValueError, match="must be positive"):
        engine.enforce_context_budget(results, max_tokens=4000, avg_tokens_per_chunk=-1)


def test_expand_results_with_adg():
    """Test ADG expansion (mock)."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(chunk_id="1", content="test1", combined_score=0.9),
        HybridSearchResult(chunk_id="2", content="test2", combined_score=0.8),
    ]

    # Without ADG connection, should return original results
    expanded = engine.expand_results_with_adg(results, relation_types=["calls"], limit_per_relation=3)
    assert len(expanded) == 2  # No expansion without ADG


def test_expand_results_with_parent_child():
    """Test parent-child expansion (mock)."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(
            chunk_id="1",
            content="test1",
            combined_score=0.9,
            metadata={"parent_id": "parent1"},
        ),
        HybridSearchResult(
            chunk_id="2",
            content="test2",
            combined_score=0.8,
            metadata={},
        ),
    ]

    # Without ChromaDB client, should return original results
    expanded = engine.expand_results_with_parent_child(results, max_depth=1)
    assert len(expanded) == 2  # No expansion without ChromaDB
