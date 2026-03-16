"""Behavioral regression tests for GraphMemoryBridge — CLI fallback persistence path.

Previously this file imported non-existent constants (MAX_RETRIES, DEFAULT_SLEEP, etc.)
causing _AVAILABLE=False and every test to be permanently silently skipped. That is
why the four persistence bugs below went undetected.

Bugs covered (must not regress):
  B1 — mcp11 never importable in CLI: bridge must activate SQLite fallback,
       _mcp_available must be True so writes are not silently dropped.
  B2 — _MCPFallbackClient() created fresh per call: entities vanished immediately
       because the in-memory dict was discarded after each create_agent_entity call.
  B3 — _call_mcp_create_relations and _call_mcp_add_observations returned None
       with no fallback: relations and observations were silently dropped.
  B4 — _persist_adg_to_memory printed "persisted" regardless of whether anything
       actually reached storage.
"""
from __future__ import annotations

import dataclasses
import sqlite3

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

_emit_records_execution_trace("p0", "evidence", "test_graph_memory_bridge")
_emit_applies_guardrail("p0", "test_graph_memory_bridge", "p0_governance")
_emit_reads_policy_state("p0", "test_graph_memory_bridge", "policy_binding")
_emit_snapshots_state("p0", "test_graph_memory_bridge", "state_snapshot")
emit_replay_key("p0", "test_graph_memory_bridge")
emit_determinism_digest("p0", "test_graph_memory_bridge")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L4_state.enforcement.graph_memory_bridge import (
    EntityDefinition,
    GraphMemoryBridge,
    RelationDefinition,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_counts(db_path):
    """Return (entities, observations, relations) counts from a SQLite db."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    e = cur.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    o = cur.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    r = cur.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
    conn.close()
    return e, o, r


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def isolated_bridge(tmp_path, monkeypatch):
    """Fresh GraphMemoryBridge backed by a temp SQLite file.

    Uses monkeypatch so MEMORY_DB is restored after each test.
    Resets the singleton before and after to prevent state leakage.
    """
    db = tmp_path / "kg_test.sqlite"
    monkeypatch.setenv("MEMORY_DB", str(db))
    GraphMemoryBridge.reset_instance()
    bridge = GraphMemoryBridge.get_instance()
    yield bridge, db
    GraphMemoryBridge.reset_instance()


# ---------------------------------------------------------------------------
# Dataclass contracts (always run — no skip guard needed)
# ---------------------------------------------------------------------------

class TestEntityDefinitionContract:
    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(EntityDefinition)

    def test_field_names(self):
        names = {f.name for f in dataclasses.fields(EntityDefinition)}
        assert names >= {"name", "entity_type", "observations"}


class TestRelationDefinitionContract:
    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(RelationDefinition)

    def test_field_names(self):
        names = {f.name for f in dataclasses.fields(RelationDefinition)}
        assert names >= {"from_entity", "to_entity", "relation_type"}


# ---------------------------------------------------------------------------
# B1 — mcp11 unavailable in CLI: SQLite fallback must activate
# ---------------------------------------------------------------------------

class TestSQLiteFallbackInit:
    def test_is_available_true_without_mcp11(self, isolated_bridge):
        """B1: bridge must be available via SQLite even when mcp11 is absent."""
        bridge, _ = isolated_bridge
        assert bridge.is_available is True

    def test_sqlite_store_is_wired(self, isolated_bridge):
        """B1: _sqlite_store must be non-None — proves SQLite fallback activated."""
        bridge, _ = isolated_bridge
        assert bridge._sqlite_store is not None

    def test_mcp_module_is_none_in_cli(self, isolated_bridge):
        """B1: _mcp_module must be None (mcp11 is a Windsurf live-process module)."""
        bridge, _ = isolated_bridge
        assert bridge._mcp_module is None


# ---------------------------------------------------------------------------
# B2 — entity must persist to SQLite, not be discarded in an ephemeral dict
# ---------------------------------------------------------------------------

class TestEntityPersistence:
    def test_create_entity_writes_to_sqlite(self, isolated_bridge):
        """B2: entity count in SQLite must be 1 after a single create_agent_entity call."""
        bridge, db = isolated_bridge
        bridge.create_agent_entity("AgentAlpha", "Agent", ["obs_a"])
        entities, _, _ = _row_counts(db)
        assert entities == 1

    def test_multiple_entities_all_persisted(self, isolated_bridge):
        """B2: all entities across 5 separate calls must land in SQLite."""
        bridge, db = isolated_bridge
        for i in range(5):
            bridge.create_agent_entity(f"Agent_{i}", "Agent", [f"obs_{i}"])
        entities, _, _ = _row_counts(db)
        assert entities == 5

    def test_entity_survives_singleton_reset(self, tmp_path, monkeypatch):
        """B2: entity written by bridge_1 must be readable by fresh bridge_2 on same db.

        This is the definitive test that data is durable, not ephemeral.
        """
        db = tmp_path / "kg_persist.sqlite"
        monkeypatch.setenv("MEMORY_DB", str(db))

        GraphMemoryBridge.reset_instance()
        b1 = GraphMemoryBridge.get_instance()
        b1.create_agent_entity("DurableAgent", "Agent", ["durable_obs"])

        GraphMemoryBridge.reset_instance()
        b2 = GraphMemoryBridge.get_instance()
        results = b2.search_entities("DurableAgent")
        GraphMemoryBridge.reset_instance()

        assert len(results) > 0, "entity written by b1 must be readable by b2 — data must be durable"

    def test_observations_written_with_entity(self, isolated_bridge):
        """B2: observations passed to create_agent_entity must land in SQLite."""
        bridge, db = isolated_bridge
        bridge.create_agent_entity("ObsAgent", "Agent", ["obs_x", "obs_y"])
        _, obs_count, _ = _row_counts(db)
        assert obs_count == 2


# ---------------------------------------------------------------------------
# B3 — relations and observations must not silently drop (previously returned None)
# ---------------------------------------------------------------------------

class TestRelationPersistence:
    def test_create_relation_writes_to_sqlite(self, isolated_bridge):
        """B3: create_relation must persist — previously _call_mcp_create_relations returned None."""
        bridge, db = isolated_bridge
        bridge.create_agent_entity("Src", "Agent")
        bridge.create_agent_entity("Tgt", "Agent")
        ok = bridge.create_relation("Src", "Tgt", "DEPENDS_ON")
        assert ok is True
        _, _, rels = _row_counts(db)
        assert rels == 1

    def test_create_relation_correct_endpoints(self, isolated_bridge):
        """B3: relation endpoints must match what was requested."""
        bridge, db = isolated_bridge
        bridge.create_agent_entity("NodeA", "Agent")
        bridge.create_agent_entity("NodeB", "Agent")
        bridge.create_relation("NodeA", "NodeB", "INTERACTS_WITH")
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT from_entity, relation_type, to_entity FROM relations"
        ).fetchone()
        conn.close()
        assert row[0] == "NodeA"
        assert row[1] == "INTERACTS_WITH"
        assert row[2] == "NodeB"


class TestObservationPersistence:
    def test_add_observation_writes_to_sqlite(self, isolated_bridge):
        """B3: add_observation must persist — previously _call_mcp_add_observations returned None."""
        bridge, db = isolated_bridge
        bridge.create_agent_entity("Target", "Agent", ["initial"])
        bridge.add_observation("Target", "appended_obs")
        conn = sqlite3.connect(str(db))
        obs = [r[0] for r in conn.execute(
            "SELECT content FROM observations WHERE entity_name='Target'"
        ).fetchall()]
        conn.close()
        assert "appended_obs" in obs

    def test_duplicate_observation_not_duplicated(self, isolated_bridge):
        """add_observation must be idempotent — same obs written twice = 1 row for that content."""
        bridge, db = isolated_bridge
        bridge.create_agent_entity("Idem", "Agent")
        bridge.add_observation("Idem", "same_obs")
        bridge.add_observation("Idem", "same_obs")
        conn = sqlite3.connect(str(db))
        n = conn.execute(
            "SELECT COUNT(*) FROM observations WHERE entity_name='Idem' AND content='same_obs'"
        ).fetchone()[0]
        conn.close()
        assert n == 1


# ---------------------------------------------------------------------------
# B4 — search must return data, not an empty list when data was written
# ---------------------------------------------------------------------------

class TestSearchReturnsPersistedData:
    def test_search_entities_finds_written_entity(self, isolated_bridge):
        """B4 proxy: if search returns [] after write, persistence is broken."""
        bridge, _ = isolated_bridge
        bridge.create_agent_entity("UniqueSearchTarget_xyz", "Agent", ["marker"])
        results = bridge.search_entities("UniqueSearchTarget_xyz")
        assert len(results) > 0

    def test_search_returns_observations(self, isolated_bridge):
        """search must surface observation content, not just entity name."""
        bridge, _ = isolated_bridge
        bridge.create_agent_entity("SearchObs", "Agent", ["findable_token_abc"])
        results = bridge.search_entities("findable_token_abc")
        assert len(results) > 0
