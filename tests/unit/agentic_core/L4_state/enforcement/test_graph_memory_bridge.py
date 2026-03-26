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

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_graph_memory_bridge")
# REMOVED: _emit_applies_guardrail("p0", "test_graph_memory_bridge", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_graph_memory_bridge", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_graph_memory_bridge", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_graph_memory_bridge")
# REMOVED: emit_determinism_digest("p0", "test_graph_memory_bridge")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_graph_memory_bridge", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_graph_memory_bridge", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_graph_memory_bridge", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_graph_memory_bridge", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_graph_memory_bridge", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_graph_memory_bridge", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_graph_memory_bridge", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_graph_memory_bridge", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_graph_memory_bridge", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_graph_memory_bridge", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_graph_memory_bridge", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_graph_memory_bridge", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_graph_memory_bridge", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_graph_memory_bridge", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_graph_memory_bridge", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_graph_memory_bridge", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_graph_memory_bridge", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_graph_memory_bridge", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_graph_memory_bridge", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_graph_memory_bridge", "exec_snapshot_link")

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L4_state.enforcement.graph_memory_bridge import (
    EntityDefinition,
    GraphMemoryBridge,
    RelationDefinition,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_graph_memory_bridge", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_graph_memory_bridge", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_graph_memory_bridge", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_graph_memory_bridge", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_graph_memory_bridge", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_graph_memory_bridge", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_graph_memory_bridge", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_graph_memory_bridge", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_graph_memory_bridge", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_graph_memory_bridge", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_graph_memory_bridge", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_graph_memory_bridge", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_graph_memory_bridge", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_graph_memory_bridge", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_graph_memory_bridge", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_graph_memory_bridge", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_graph_memory_bridge", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_graph_memory_bridge", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_graph_memory_bridge", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_graph_memory_bridge", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_graph_memory_bridge", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_graph_memory_bridge", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_graph_memory_bridge", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_graph_memory_bridge", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_graph_memory_bridge", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_graph_memory_bridge", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_graph_memory_bridge", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_graph_memory_bridge", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_graph_memory_bridge", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_graph_memory_bridge", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_graph_memory_bridge", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_graph_memory_bridge", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_graph_memory_bridge", "write_through")
# REMOVED: _emit_writes_through("p1", "test_graph_memory_bridge", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_graph_memory_bridge", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_graph_memory_bridge", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_graph_memory_bridge", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_graph_memory_bridge", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_graph_memory_bridge", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_graph_memory_bridge", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_graph_memory_bridge", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_graph_memory_bridge", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_graph_memory_bridge", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_graph_memory_bridge", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_graph_memory_bridge", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_graph_memory_bridge", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_graph_memory_bridge", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_graph_memory_bridge", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_graph_memory_bridge")
# REMOVED: _emit_gated_by_confidence("p1", "test_graph_memory_bridge", "confidence_gate")

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
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L4_state.enforcement.graph_memory_bridge import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                assert dataclasses.is_dataclass(EntityDefinition)

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
