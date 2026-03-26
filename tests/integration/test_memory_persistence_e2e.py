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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_memory_persistence_e2e")
# REMOVED: _emit_applies_guardrail("p0", "test_memory_persistence_e2e", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_memory_persistence_e2e", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_memory_persistence_e2e", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_memory_persistence_e2e", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_memory_persistence_e2e", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_memory_persistence_e2e", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_memory_persistence_e2e", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_memory_persistence_e2e", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_memory_persistence_e2e", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_memory_persistence_e2e", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_memory_persistence_e2e", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_memory_persistence_e2e", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_memory_persistence_e2e", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_memory_persistence_e2e", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_memory_persistence_e2e", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_memory_persistence_e2e", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_memory_persistence_e2e", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_memory_persistence_e2e", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_memory_persistence_e2e", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_memory_persistence_e2e", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_memory_persistence_e2e", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_memory_persistence_e2e", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_memory_persistence_e2e", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_memory_persistence_e2e", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_memory_persistence_e2e", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_memory_persistence_e2e", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_memory_persistence_e2e", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_memory_persistence_e2e", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_memory_persistence_e2e", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_memory_persistence_e2e", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_memory_persistence_e2e", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_memory_persistence_e2e", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_memory_persistence_e2e", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_memory_persistence_e2e", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_memory_persistence_e2e", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_memory_persistence_e2e", "write_through")
# REMOVED: _emit_writes_through("p1", "test_memory_persistence_e2e", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_memory_persistence_e2e", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_memory_persistence_e2e", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_memory_persistence_e2e", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_memory_persistence_e2e", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_memory_persistence_e2e", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_memory_persistence_e2e", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_memory_persistence_e2e", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_memory_persistence_e2e", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_memory_persistence_e2e", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_memory_persistence_e2e", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_memory_persistence_e2e", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_memory_persistence_e2e", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_memory_persistence_e2e", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_memory_persistence_e2e", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_memory_persistence_e2e")
# REMOVED: _emit_gated_by_confidence("p1", "test_memory_persistence_e2e", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_memory_persistence_e2e")
# REMOVED: emit_determinism_digest("p0", "test_memory_persistence_e2e")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_memory_persistence_e2e", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_memory_persistence_e2e", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_memory_persistence_e2e", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_memory_persistence_e2e", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_memory_persistence_e2e", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_memory_persistence_e2e", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_memory_persistence_e2e", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_memory_persistence_e2e", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_memory_persistence_e2e", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_memory_persistence_e2e", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_memory_persistence_e2e", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_memory_persistence_e2e", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_memory_persistence_e2e", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_memory_persistence_e2e", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_memory_persistence_e2e", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_memory_persistence_e2e", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_memory_persistence_e2e", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_memory_persistence_e2e", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_memory_persistence_e2e", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_memory_persistence_e2e", "exec_snapshot_link")

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
    layers = [
        "L0_routing",
        "L1_cognition",
        "L2_execution",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
    ]
    modules = [f"agentic_core/{layers[i % len(layers)]}/module_{i}.py" for i in range(n_modules)]
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
#  # MOVED: from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

    db = tmp_path / "kg_e2e.sqlite"
    monkeypatch.setenv("MEMORY_DB", str(db))
    GraphMemoryBridge.reset_instance()

#  # MOVED: from agentic_core.adg.adapters.ADGMemoryAdapter import ADGMemoryAdapter

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
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
        from agentic_core.adg.adapters.ADGMemoryAdapter import ADGMemoryAdapter
        from agentic_core.adg.adapters.ADGMemoryAdapter import ADGMemoryAdapter
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
        """Full pipeline: ingest_snapshot must produce non-zero entity count in SQLite."""
        adapter, db = memory_env
        scan = _make_scan_result(n_modules=10, n_edges=5)

        adapter.ingest_snapshot(scan, ts="20991231T000000Z")

        entities, obs, rels = _counts(db)
        assert entities > 0, (
            f"Expected entities > 0 after ingest, got {entities}. Full pipeline is silently dropping data."
        )

    def test_snapshot_entity_written(self, memory_env):
        """ADGSnapshot entity must be the anchor node after ingest."""
        adapter, db = memory_env
        ts = "20991231T120000Z"
        adapter.ingest_snapshot(_make_scan_result(), ts=ts)

        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT name, entity_type FROM entities WHERE name LIKE 'ADGSnapshot%'").fetchone()
        conn.close()

        assert row is not None, f"ADGSnapshot_* entity missing after ingest(ts={ts!r})"
        assert row[1] == "ADGSnapshot"

    def test_layer_entities_written(self, memory_env):
        """At least one ADGLayer entity must exist — layers are the structural backbone."""
        adapter, db = memory_env
        adapter.ingest_snapshot(_make_scan_result(n_modules=20), ts="20991231T000000Z")

        conn = sqlite3.connect(str(db))
        n = conn.execute("SELECT COUNT(*) FROM entities WHERE entity_type='ADGLayer'").fetchone()[0]
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
#  # MOVED: from agentic_core.adg.adapters.ADGMemoryAdapter import ADGMemoryAdapter
#  # MOVED: from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

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
        n = conn.execute("SELECT COUNT(*) FROM entities WHERE entity_type='ADGViolation'").fetchone()[0]
        conn.close()

        assert n > 0, "ADGViolation entities not persisted — violation tracking is broken"
