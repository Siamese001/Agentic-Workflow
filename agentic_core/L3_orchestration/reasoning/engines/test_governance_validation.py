"""Governance validation tests for hybrid search."""

from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
    HybridSearchEngine,
    HybridSearchResult,
)


def test_governance_filter_exclude_violations():
    """Test governance filter excluding violations."""
    engine = HybridSearchEngine()

    # Mock results with ADG node IDs
    results = [
        HybridSearchResult(
            chunk_id="1",
            content="test1",
            metadata={"adg_node_id": 1, "layer": "L2"},
        ),
        HybridSearchResult(
            chunk_id="2",
            content="test2",
            metadata={"adg_node_id": 2, "layer": "L3"},
        ),
        HybridSearchResult(
            chunk_id="3",
            content="test3",
            metadata={"adg_node_id": None, "layer": "L2"},
        ),
    ]

    # Without ADG connection, all results pass
    filtered = engine._apply_governance_filters(results, {"exclude_violations": True})
    assert len(filtered) == 3


def test_governance_filter_by_layer():
    """Test governance filter by layer."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(
            chunk_id="1",
            content="test1",
            metadata={"layer": "L2", "entity_type": "function"},
        ),
        HybridSearchResult(
            chunk_id="2",
            content="test2",
            metadata={"layer": "L3", "entity_type": "function"},
        ),
        HybridSearchResult(
            chunk_id="3",
            content="test3",
            metadata={"layer": "L2", "entity_type": "class"},
        ),
    ]

    # Filter to L2 only
    filtered = engine._apply_governance_filters(results, {"layers": ["L2"]})
    assert len(filtered) == 2
    assert all(r.metadata["layer"] == "L2" for r in filtered)


def test_governance_filter_by_entity_type():
    """Test governance filter by entity type."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(
            chunk_id="1",
            content="test1",
            metadata={"layer": "L2", "entity_type": "function"},
        ),
        HybridSearchResult(
            chunk_id="2",
            content="test2",
            metadata={"layer": "L3", "entity_type": "class"},
        ),
        HybridSearchResult(
            chunk_id="3",
            content="test3",
            metadata={"layer": "L2", "entity_type": "module"},
        ),
    ]

    # Filter to functions only
    filtered = engine._apply_governance_filters(results, {"entity_types": ["function"]})
    assert len(filtered) == 1
    assert filtered[0].metadata["entity_type"] == "function"


def test_governance_filter_combined():
    """Test combined governance filters."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(
            chunk_id="1",
            content="test1",
            metadata={"layer": "L2", "entity_type": "function"},
        ),
        HybridSearchResult(
            chunk_id="2",
            content="test2",
            metadata={"layer": "L3", "entity_type": "function"},
        ),
        HybridSearchResult(
            chunk_id="3",
            content="test3",
            metadata={"layer": "L2", "entity_type": "class"},
        ),
        HybridSearchResult(
            chunk_id="4",
            content="test4",
            metadata={"layer": "L3", "entity_type": "class"},
        ),
    ]

    # Filter to L2 AND function
    filtered = engine._apply_governance_filters(
        results,
        {"layers": ["L2"], "entity_types": ["function"]},
    )
    assert len(filtered) == 1
    assert filtered[0].chunk_id == "1"


def test_governance_filter_empty_metadata():
    """Test governance filter with empty metadata."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(
            chunk_id="1",
            content="test1",
            metadata={},
        ),
    ]

    # Filter should handle missing metadata gracefully
    filtered = engine._apply_governance_filters(results, {"layers": ["L2"]})
    assert len(filtered) == 0  # Should be filtered out since layer is not L2


def test_governance_filter_no_filters():
    """Test governance filter with no filters applied."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(
            chunk_id="1",
            content="test1",
            metadata={"layer": "L2"},
        ),
        HybridSearchResult(
            chunk_id="2",
            content="test2",
            metadata={"layer": "L3"},
        ),
    ]

    # No filters should return all results
    filtered = engine._apply_governance_filters(results, {})
    assert len(filtered) == 2


def test_governance_filter_unknown_layer():
    """Test governance filter with unknown layer."""
    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(
            chunk_id="1",
            content="test1",
            metadata={"layer": "Unknown"},
        ),
        HybridSearchResult(
            chunk_id="2",
            content="test2",
            metadata={"layer": "L2"},
        ),
    ]

    # Filter to L2 should exclude Unknown
    filtered = engine._apply_governance_filters(results, {"layers": ["L2"]})
    assert len(filtered) == 1
    assert filtered[0].metadata["layer"] == "L2"
