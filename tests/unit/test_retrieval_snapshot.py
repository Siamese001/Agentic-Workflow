"""
Phase 6 — Wave 2 Tests: RetrievalBoundarySnapshot (deterministic, non-mutating).
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L4_state.types.retrieval_boundary_snapshot_types import (
    AnchorEntry,
    RetrievalBoundarySnapshot,
    build_request_hash,
    create_retrieval_boundary_snapshot,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_retrieval_snapshot", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_retrieval_snapshot", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_retrieval_snapshot", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_retrieval_snapshot", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_retrieval_snapshot", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_retrieval_snapshot", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_retrieval_snapshot", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_retrieval_snapshot", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_retrieval_snapshot", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_retrieval_snapshot", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_retrieval_snapshot", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_retrieval_snapshot", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_retrieval_snapshot", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_retrieval_snapshot", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_retrieval_snapshot", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_retrieval_snapshot", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_retrieval_snapshot", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_retrieval_snapshot", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_retrieval_snapshot", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_retrieval_snapshot", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_retrieval_snapshot", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_retrieval_snapshot", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_retrieval_snapshot", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_retrieval_snapshot", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_retrieval_snapshot", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_retrieval_snapshot", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_retrieval_snapshot", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_retrieval_snapshot", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_retrieval_snapshot")
# REMOVED: _emit_applies_guardrail("p0", "test_retrieval_snapshot", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_retrieval_snapshot", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_retrieval_snapshot", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_retrieval_snapshot", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_retrieval_snapshot", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_retrieval_snapshot", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_retrieval_snapshot", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_retrieval_snapshot", "write_through")
# REMOVED: _emit_writes_through("p1", "test_retrieval_snapshot", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_retrieval_snapshot", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_retrieval_snapshot", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_retrieval_snapshot", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_retrieval_snapshot", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_retrieval_snapshot", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_retrieval_snapshot", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_retrieval_snapshot", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_retrieval_snapshot", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_retrieval_snapshot", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_retrieval_snapshot", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_retrieval_snapshot", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_retrieval_snapshot", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_retrieval_snapshot", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_retrieval_snapshot", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_retrieval_snapshot")
# REMOVED: _emit_gated_by_confidence("p1", "test_retrieval_snapshot", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_retrieval_snapshot")
# REMOVED: emit_determinism_digest("p0", "test_retrieval_snapshot")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_retrieval_snapshot", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_retrieval_snapshot", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_retrieval_snapshot", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_retrieval_snapshot", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_retrieval_snapshot", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_retrieval_snapshot", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_retrieval_snapshot", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_retrieval_snapshot", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_retrieval_snapshot", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_retrieval_snapshot", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_retrieval_snapshot", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_retrieval_snapshot", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_retrieval_snapshot", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_retrieval_snapshot", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_retrieval_snapshot", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_retrieval_snapshot", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_retrieval_snapshot", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_retrieval_snapshot", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_retrieval_snapshot", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_retrieval_snapshot", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"
_CONFIG_HASHES = {
    "policy_hash": "aaa111",
    "routing_hash": "bbb222",
    "model_hash": "ccc333",
    "budget_hash": "ddd444",
}


def _make_anchors(*chunk_ids: str) -> list[AnchorEntry]:
    return [AnchorEntry(chunk_id=cid, version_hash=f"vh-{cid}") for cid in chunk_ids]


def _make_snapshot(**overrides) -> RetrievalBoundarySnapshot:
    defaults: dict = {
        "schema_version": 1,
        "mission_id": "mission-test",
        "request_hash": build_request_hash("query text", 5, AGENTIC_CORE_DIR),
        "active_config_hashes": dict(_CONFIG_HASHES),
        "anchors": _make_anchors("chunk-A", "chunk-B"),
        "created_at_utc": _TS,
    }
    defaults.update(overrides)
    return RetrievalBoundarySnapshot(**defaults)


class TestSnapshotHashStable:
    def test_snapshot_hash_stable(self):
        """Same inputs produce the same snapshot_hash on repeated construction."""
        s1 = _make_snapshot()
        s2 = _make_snapshot()
        assert s1.snapshot_hash == s2.snapshot_hash
        assert len(s1.snapshot_hash) == 64

    def test_hash_changes_with_mission_id(self):
        s1 = _make_snapshot(mission_id="mission-A")
        s2 = _make_snapshot(mission_id="mission-B")
        assert s1.snapshot_hash != s2.snapshot_hash

    def test_hash_changes_with_request_hash(self):
        s1 = _make_snapshot(request_hash=build_request_hash("query-1", 5, "dom"))
        s2 = _make_snapshot(request_hash=build_request_hash("query-2", 5, "dom"))
        assert s1.snapshot_hash != s2.snapshot_hash

    def test_hash_changes_with_config_hashes(self):
        s1 = _make_snapshot(active_config_hashes={"policy_hash": "aaa"})
        s2 = _make_snapshot(active_config_hashes={"policy_hash": "bbb"})
        assert s1.snapshot_hash != s2.snapshot_hash

    def test_hash_changes_with_anchors(self):
        s1 = _make_snapshot(anchors=_make_anchors("chunk-X"))
        s2 = _make_snapshot(anchors=_make_anchors("chunk-Y"))
        assert s1.snapshot_hash != s2.snapshot_hash

    def test_snapshot_hash_excluded_from_canonical_bytes(self):
        s = _make_snapshot()
        assert b"snapshot_hash" not in s.canonical_bytes()

    def test_canonical_bytes_deterministic(self):
        s1 = _make_snapshot()
        s2 = _make_snapshot()
        assert s1.canonical_bytes() == s2.canonical_bytes()


class TestSnapshotCanonicalOrdering:
    def test_snapshot_canonical_ordering(self):
        """
        Anchors in canonical_bytes must be sorted by (chunk_id, version_hash)
        regardless of the order passed to the constructor.
        """
        anchors_unsorted = _make_anchors("chunk-Z", "chunk-A", "chunk-M")
        anchors_sorted = _make_anchors("chunk-A", "chunk-M", "chunk-Z")
        s1 = _make_snapshot(anchors=anchors_unsorted)
        s2 = _make_snapshot(anchors=anchors_sorted)
        assert s1.snapshot_hash == s2.snapshot_hash

    def test_anchors_stored_sorted(self):
        s = _make_snapshot(anchors=_make_anchors("chunk-Z", "chunk-A", "chunk-M"))
        chunk_ids = [a.chunk_id for a in s.anchors]
        assert chunk_ids == sorted(chunk_ids)

    def test_config_hashes_sorted_in_canonical_bytes(self):
        """active_config_hashes keys must be sorted in canonical_bytes."""
        s = _make_snapshot(
            active_config_hashes={
                "z_hash": "zzz",
                "a_hash": "aaa",
                "m_hash": "mmm",
            }
        )
        raw = s.canonical_bytes().decode()
        a_pos = raw.index("a_hash")
        m_pos = raw.index("m_hash")
        z_pos = raw.index("z_hash")
        assert a_pos < m_pos < z_pos

    def test_empty_anchors_allowed(self):
        s = _make_snapshot(anchors=[])
        assert s.anchors == []
        assert len(s.snapshot_hash) == 64


class TestSnapshotContainsConfigHashesAndAnchorIds:
    def test_snapshot_contains_config_hashes_and_anchor_ids(self):
        """
        Snapshot must carry all active_config_hashes keys and all anchor chunk_ids.
        """
        s = _make_snapshot(
            active_config_hashes=_CONFIG_HASHES,
            anchors=_make_anchors("chunk-A", "chunk-B"),
        )
        assert "policy_hash" in s.active_config_hashes
        assert "routing_hash" in s.active_config_hashes
        assert "model_hash" in s.active_config_hashes
        assert "budget_hash" in s.active_config_hashes
        chunk_ids = {a.chunk_id for a in s.anchors}
        assert "chunk-A" in chunk_ids
        assert "chunk-B" in chunk_ids

    def test_snapshot_config_hashes_values_preserved(self):
        s = _make_snapshot(active_config_hashes=_CONFIG_HASHES)
        assert s.active_config_hashes["policy_hash"] == "aaa111"
        assert s.active_config_hashes["routing_hash"] == "bbb222"

    def test_snapshot_anchor_version_hash_preserved(self):
        s = _make_snapshot(anchors=_make_anchors("chunk-A"))
        assert s.anchors[0].version_hash == "vh-chunk-A"


class TestSnapshotValidation:
    def test_invalid_schema_version_raises(self):
        with pytest.raises(ValueError, match="schema_version"):
            _make_snapshot(schema_version=99)

    def test_empty_mission_id_raises(self):
        with pytest.raises(ValueError, match="mission_id"):
            _make_snapshot(mission_id="")

    def test_empty_request_hash_raises(self):
        with pytest.raises(ValueError, match="request_hash"):
            _make_snapshot(request_hash="")

    def test_non_dict_config_hashes_raises(self):
        with pytest.raises(TypeError, match="active_config_hashes"):
            _make_snapshot(active_config_hashes="not-a-dict")  # type: ignore[arg-type]

    def test_non_list_anchors_raises(self):
        with pytest.raises(TypeError, match="anchors"):
            _make_snapshot(anchors="not-a-list")  # type: ignore[arg-type]


class TestBuildRequestHash:
    def test_request_hash_stable(self):
        h1 = build_request_hash("query", 5, "dom")
        h2 = build_request_hash("query", 5, "dom")
        assert h1 == h2
        assert len(h1) == 64

    def test_request_hash_differs_by_query(self):
        h1 = build_request_hash("query-A", 5, "dom")
        h2 = build_request_hash("query-B", 5, "dom")
        assert h1 != h2

    def test_request_hash_differs_by_top_k(self):
        h1 = build_request_hash("query", 5, "dom")
        h2 = build_request_hash("query", 10, "dom")
        assert h1 != h2

    def test_request_hash_differs_by_domain(self):
        h1 = build_request_hash("query", 5, "dom-A")
        h2 = build_request_hash("query", 5, "dom-B")
        assert h1 != h2


class TestCreateSnapshotFactory:
    def test_factory_produces_valid_snapshot(self):
        s = create_retrieval_boundary_snapshot(
            mission_id="m1",
            query="test query",
            top_k=3,
            domain=AGENTIC_CORE_DIR,
            active_config_hashes=_CONFIG_HASHES,
            anchors=_make_anchors("chunk-X"),
            created_at_utc=_TS,
        )
        assert isinstance(s, RetrievalBoundarySnapshot)
        assert len(s.snapshot_hash) == 64

    def test_factory_request_hash_matches_build_request_hash(self):
        s = create_retrieval_boundary_snapshot(
            mission_id="m1",
            query="test query",
            top_k=3,
            domain=AGENTIC_CORE_DIR,
            active_config_hashes=_CONFIG_HASHES,
            anchors=[],
            created_at_utc=_TS,
        )
        expected = build_request_hash("test query", 3, AGENTIC_CORE_DIR)
        assert s.request_hash == expected

    def test_to_dict_contains_all_fields(self):
        s = _make_snapshot()
        d = s.to_dict()
        assert "schema_version" in d
        assert "mission_id" in d
        assert "request_hash" in d
        assert "active_config_hashes" in d
        assert "anchors" in d
        assert "created_at_utc" in d
        assert "snapshot_hash" in d
