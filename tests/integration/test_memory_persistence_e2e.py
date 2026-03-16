"""End-to-end integration test: ADG generate_full_adg.py persistence path.

Simulates the exact call chain that was silently broken:
  generate_full_adg._persist_adg_to_memory
    → ADGMemoryAdapter.ingest_snapshot
      → GraphMemoryBridge (CLI, no mcp11)
        → SqliteMemoryStore → knowledge_graph.sqlite

The test verifies that after the full ingest pipeline, the SQLite database
contains meaningful entity/observation/relation counts — the definitive proof
that no stage in the chain silently swallowed the data.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_memory_persistence_e2e")
_emit_applies_guardrail("p0", "test_memory_persistence_e2e", "p0_governance")
_emit_reads_policy_state("p0", "test_memory_persistence_e2e", "policy_binding")
_emit_snapshots_state("p0", "test_memory_persistence_e2e", "state_snapshot")
emit_replay_key("p0", "test_memory_persistence_e2e")
emit_determinism_digest("p0", "test_memory_persistence_e2e")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Shared mock types (mirror the real ScanResult interface)
# ---------------------------------------------------------------------------

@dataclass
class _MockEdge:
    from_name: str
    to_name: str
    relation_type: str = "imports"
    edge_kind: str = "import"
    source_file: str = "agentic_core/L4_state/foo.py"
    line_no: int = 1
    symbol: str = ""


@dataclass
class _MockScanResult:
    digest: str = "abcdef12" * 8
    modules: list = field(default_factory=list)
    edges: list = field(default_factory=list)


def _make_scan_result(n_modules: int = 10, n_edges: int = 5) -> _MockScanResult:
    """Build a realistic mock ScanResult with N modules and E edges."""
    layers = ["L0_routing", "L1_cognition", "L2_execution", "L3_orchestration",
              "L4_state", "L5_safety", "L6_observability"]
    modules = [
        f"agentic_core/{layers[i % len(layers)]}/module_{i}.py"
        for i in range(n_modules)
    ]
    edges = [
        _MockEdge(
            from_name=modules[i % n_modules],
            to_name=modules[(i + 1) % n_modules],
        )
        for i in range(n_edges)
    ]
    return _MockScanResult(modules=modules, edges=edges)


# ---------------------------------------------------------------------------
# Fixture: isolated bridge + adapter pointing at a temp db
# ---------------------------------------------------------------------------

@pytest.fixture()
def memory_env(tmp_path, monkeypatch):
    """Provide (adapter, db_path) with a fresh temp SQLite store."""
    from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

    db = tmp_path / "kg_e2e.sqlite"
    monkeypatch.setenv("MEMORY_DB", str(db))
    GraphMemoryBridge.reset_instance()

    from agentic_core.adg.adapters.memory_mcp_adapter import ADGMemoryAdapter
    adapter = ADGMemoryAdapter()

    yield adapter, db

    GraphMemoryBridge.reset_instance()


def _counts(db):
    conn = sqlite3.connect(str(db))
    e = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    o = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    r = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
    conn.close()
    return e, o, r


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFullPersistencePipeline:
    def test_ingest_populates_sqlite(self, memory_env):
        """Full pipeline: ingest_snapshot must produce non-zero entity count in SQLite."""
        adapter, db = memory_env
        scan = _make_scan_result(n_modules=10, n_edges=5)

        adapter.ingest_snapshot(scan, ts="20991231T000000Z")

        entities, obs, rels = _counts(db)
        assert entities > 0, (
            f"Expected entities > 0 after ingest, got {entities}. "
            "Full pipeline is silently dropping data."
        )

    def test_snapshot_entity_written(self, memory_env):
        """ADGSnapshot entity must be the anchor node after ingest."""
        adapter, db = memory_env
        ts = "20991231T120000Z"
        adapter.ingest_snapshot(_make_scan_result(), ts=ts)

        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT name, entity_type FROM entities WHERE name LIKE 'ADGSnapshot%'"
        ).fetchone()
        conn.close()

        assert row is not None, f"ADGSnapshot_* entity missing after ingest(ts={ts!r})"
        assert row[1] == "ADGSnapshot"

    def test_layer_entities_written(self, memory_env):
        """At least one ADGLayer entity must exist — layers are the structural backbone."""
        adapter, db = memory_env
        adapter.ingest_snapshot(_make_scan_result(n_modules=20), ts="20991231T000000Z")

        conn = sqlite3.connect(str(db))
        n = conn.execute(
            "SELECT COUNT(*) FROM entities WHERE entity_type='ADGLayer'"
        ).fetchone()[0]
        conn.close()

        assert n > 0, "No ADGLayer entities found — layer structure was not persisted"

    def test_observations_written(self, memory_env):
        """Observations (the descriptive content) must be written, not just entity stubs."""
        adapter, db = memory_env
        adapter.ingest_snapshot(_make_scan_result(), ts="20991231T000000Z")

        entities, obs, _ = _counts(db)
        assert obs > 0, (
            f"0 observations found with {entities} entities. "
            "_call_mcp_add_observations is likely still returning None."
        )

    def test_data_survives_bridge_reset(self, tmp_path, monkeypatch):
        """Data written via ingest must survive a GraphMemoryBridge singleton reset.

        This proves durability: data is in SQLite, not RAM.
        """
        from agentic_core.adg.adapters.memory_mcp_adapter import ADGMemoryAdapter
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

        db = tmp_path / "kg_durable.sqlite"
        monkeypatch.setenv("MEMORY_DB", str(db))

        GraphMemoryBridge.reset_instance()
        adapter1 = ADGMemoryAdapter()
        adapter1.ingest_snapshot(_make_scan_result(), ts="20991231T000000Z")

        entities_before, _, _ = _counts(db)

        GraphMemoryBridge.reset_instance()
        entities_after, _, _ = _counts(db)

        GraphMemoryBridge.reset_instance()

        assert entities_before > 0, "Nothing was written by adapter1"
        assert entities_after == entities_before, (
            "Entity count changed after bridge reset — data was in RAM, not SQLite"
        )

    def test_repeated_ingest_is_idempotent(self, memory_env):
        """Calling ingest_snapshot twice with the same ts must not duplicate entities."""
        adapter, db = memory_env
        scan = _make_scan_result()

        adapter.ingest_snapshot(scan, ts="20991231T000000Z")
        e1, o1, r1 = _counts(db)

        adapter.ingest_snapshot(scan, ts="20991231T000000Z")
        e2, o2, r2 = _counts(db)

        assert e2 == e1, f"Entity count grew from {e1} to {e2} on second identical ingest — not idempotent"


class TestViolationPersistence:
    def test_violation_edges_written(self, memory_env):
        """Violation edges (GV_violates) must be persisted as ADGViolation entities."""

        adapter, db = memory_env

        scan = _MockScanResult(
            modules=["agentic_core/L5_safety/foo.py", "agentic_core/L0_routing/bar.py"],
            edges=[
                _MockEdge(
                    from_name="agentic_core/L5_safety/foo.py",
                    to_name="agentic_core/L0_routing/bar.py",
                    relation_type="violates",
                    edge_kind="violation",
                )
            ],
        )
        adapter.ingest_snapshot(scan, ts="20991231T000000Z")

        conn = sqlite3.connect(str(db))
        n = conn.execute(
            "SELECT COUNT(*) FROM entities WHERE entity_type='ADGViolation'"
        ).fetchone()[0]
        conn.close()

        assert n > 0, "ADGViolation entities not persisted — violation tracking is broken"
