"""Tests for ADG integration in HybridSearchEngine."""

import pytest
from pathlib import Path

from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchEngine


@pytest.fixture
def mock_adg_db_path(tmp_path: Path) -> str:
    """Create a mock ADG database for testing."""
    import sqlite3

    db_path = tmp_path / "test_adg.sqlite"
    conn = sqlite3.connect(str(db_path))

    # Create tables
    conn.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT,
            resolved_path TEXT,
            entity_type TEXT,
            layer TEXT,
            territory TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE edges (
            src_id INTEGER,
            dst_id INTEGER,
            relation_type TEXT
        )
    """)

    # Insert test nodes
    conn.execute(
        "INSERT INTO nodes (id, adg_name, resolved_path, entity_type, layer, territory) VALUES "
        "(1, 'test_func', 'test.py', 'function', 'L2', 'L2_EXECUTION'),"
        "(2, 'test_class', 'test.py', 'class', 'L2', 'L2_EXECUTION'),"
        "(3, 'caller_func', 'caller.py', 'function', 'L3', 'L3_ORCHESTRATION')"
    )

    # Insert test edges
    conn.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type) VALUES "
        "(3, 1, 'calls'),"
        "(3, 2, 'imports')"
    )

    conn.commit()
    conn.close()

    return str(db_path)


def test_adg_connection_initialization(mock_adg_db_path: str):
    """Test ADG SQLite connection is initialized lazily."""
    engine = HybridSearchEngine(adg_db_path=mock_adg_db_path)

    # Connection should be None initially
    assert engine._adg_conn is None

    # Connection should be created on first query
    node = engine.get_node_by_id(1)
    assert node is not None
    assert engine._adg_conn is not None


def test_get_node_by_id(mock_adg_db_path: str):
    """Test getting ADG node by ID."""
    engine = HybridSearchEngine(adg_db_path=mock_adg_db_path)

    node = engine.get_node_by_id(1)
    assert node is not None
    assert node["adg_name"] == "test_func"
    assert node["layer"] == "L2"

    # Test non-existent node
    node = engine.get_node_by_id(999)
    assert node is None


def test_get_callers(mock_adg_db_path: str):
    """Test getting callers of a node."""
    engine = HybridSearchEngine(adg_db_path=mock_adg_db_path)

    callers = engine.get_callers(1)
    assert len(callers) == 1
    assert callers[0]["adg_name"] == "caller_func"


def test_get_callees(mock_adg_db_path: str):
    """Test getting callees of a node."""
    engine = HybridSearchEngine(adg_db_path=mock_adg_db_path)

    callees = engine.get_callees(3)
    assert len(callees) == 1
    assert callees[0]["adg_name"] == "test_func"


def test_get_importers(mock_adg_db_path: str):
    """Test getting importers of a node."""
    engine = HybridSearchEngine(adg_db_path=mock_adg_db_path)

    importers = engine.get_importers(2)
    assert len(importers) == 1
    assert importers[0]["adg_name"] == "caller_func"


def test_get_imports(mock_adg_db_path: str):
    """Test getting imports of a node."""
    engine = HybridSearchEngine(adg_db_path=mock_adg_db_path)

    imports = engine.get_imports(3)
    assert len(imports) == 1
    assert imports[0]["adg_name"] == "test_class"


def test_get_violations(mock_adg_db_path: str):
    """Test getting violations for a node."""
    engine = HybridSearchEngine(adg_db_path=mock_adg_db_path)

    violations = engine.get_violations(1)
    assert violations == []  # No violations in test data


def test_close_adg_connection(mock_adg_db_path: str):
    """Test closing ADG connection."""
    engine = HybridSearchEngine(adg_db_path=mock_adg_db_path)

    # Initialize connection
    engine.get_node_by_id(1)
    assert engine._adg_conn is not None

    # Close connection
    engine.close_adg_connection()
    assert engine._adg_conn is None


def test_governance_filters_layer():
    """Test governance filter by layer."""
    from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchResult

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
    from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchResult

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
    from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchResult

    engine = HybridSearchEngine()

    results = [
        HybridSearchResult(chunk_id="1", content="test1", metadata={"layer": "L2", "entity_type": "function"}),
        HybridSearchResult(chunk_id="2", content="test2", metadata={"layer": "L3", "entity_type": "function"}),
        HybridSearchResult(chunk_id="3", content="test3", metadata={"layer": "L2", "entity_type": "class"}),
    ]

    filtered = engine._apply_governance_filters(
        results, {"layers": ["L2"], "entity_types": ["function"]}
    )
    assert len(filtered) == 1
    assert filtered[0].chunk_id == "1"
