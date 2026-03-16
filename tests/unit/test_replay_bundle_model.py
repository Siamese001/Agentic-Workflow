"""
Phase 9 — Wave 1 Tests: ReplayBundle model + deterministic validation.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.types.replay_bundle_types import (
    ReplayBundle,
    build_replay_bundle,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
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
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_replay_bundle_model", "p4obs", "metric_1")
_emit_emits_metric_event("test_replay_bundle_model", "p4obs", "metric_2")
_emit_emits_metric_event("test_replay_bundle_model", "p4obs", "metric_3")
_emit_emits_metric_event("test_replay_bundle_model", "p4obs", "metric_4")
_emit_emits_metric_event("test_replay_bundle_model", "p4obs", "metric_5")
_emit_emits_metric_event("test_replay_bundle_model", "p4obs", "metric_6")
_emit_records_incident_event("test_replay_bundle_model", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_replay_bundle_model", "p4obs", "anomaly")
_emit_writes_observability_log("test_replay_bundle_model", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_replay_bundle_model", "p4obs", "mon_state")
_emit_triggers_alert("test_replay_bundle_model", "p4obs", "alert")
_emit_links_incident_trace("test_replay_bundle_model", "p4obs", "trace_link")
_emit_captures_pattern("test_replay_bundle_model", "p3lm", "pattern")
_emit_records_learning_event("test_replay_bundle_model", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_replay_bundle_model", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_replay_bundle_model", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_replay_bundle_model", "p3lm", "routing")
_emit_improves_agent_policy("test_replay_bundle_model", "p3lm", "policy")
_emit_stores_learning_state("test_replay_bundle_model", "p3lm", "state")
_emit_records_execution_trace("test_replay_bundle_model", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_replay_bundle_model", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_replay_bundle_model", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_replay_bundle_model", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_replay_bundle_model", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_replay_bundle_model", "env_read", "p2_env_1")
_emit_reads_environ("test_replay_bundle_model", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_replay_bundle_model", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_replay_bundle_model", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_replay_bundle_model")
_emit_applies_guardrail("p0", "test_replay_bundle_model", "p0_governance")
_emit_reads_policy_state("p0", "test_replay_bundle_model", "policy_binding")
_emit_snapshots_state("p0", "test_replay_bundle_model", "state_snapshot")
_emit_pulls_context("p1", "test_replay_bundle_model", "context_pull")
_emit_pulls_context("p1", "test_replay_bundle_model", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_replay_bundle_model", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_replay_bundle_model", "uwg_term_secondary")
_emit_writes_through("p1", "test_replay_bundle_model", "write_through")
_emit_writes_through("p1", "test_replay_bundle_model", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_replay_bundle_model", "safety_validation")
_emit_invokes_eval("p1", "test_replay_bundle_model", "eval_call")
_emit_proposal_commits_routing("p1", "test_replay_bundle_model", "routing_commit")
emit_replay_key("p0", "test_replay_bundle_model")
emit_determinism_digest("p0", "test_replay_bundle_model")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_replay_bundle_model", "execution_auth")
_emit_validates_capability("p2", "test_replay_bundle_model", "capability_check")
_emit_routes_to_capability("p2", "test_replay_bundle_model", "capability_route")
_emit_writes_via_uwg("p2", "test_replay_bundle_model", "uwg_write")
_emit_blocks_direct_write("p2", "test_replay_bundle_model", "direct_write_block")
_emit_records_tool_invocation("p2", "test_replay_bundle_model", "tool_invocation")
_emit_captures_execution_output("p2", "test_replay_bundle_model", "exec_output")
_emit_dispatches_agent("p3", "test_replay_bundle_model", "agent_dispatch")
_emit_coordinates_agents("p3", "test_replay_bundle_model", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_replay_bundle_model", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_replay_bundle_model", "healing_outcome")
_emit_escalates_failure("p3", "test_replay_bundle_model", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_replay_bundle_model", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_replay_bundle_model", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_replay_bundle_model", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_replay_bundle_model", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_replay_bundle_model", "eval_metric")
_emit_stores_embedding("p4", "test_replay_bundle_model", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_replay_bundle_model", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_replay_bundle_model", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

_MH = "m" * 64
_CONFIG = {"policy_hash": "ph1", "routing_hash": "rh1", "model_hash": "mh1", "budget_hash": "bh1"}


def _make_bundle(**overrides) -> ReplayBundle:
    defaults: dict = {
        "schema_version": 1,
        "mission_id": "mission-test",
        "execution_start_tick": 5,
        "execution_end_tick": 10,
        "manifest_hash": _MH,
        "active_config_hashes": dict(_CONFIG),
        "retrieval_used": False,
        "citation_hash": "",
        "prior_detection_signal_hash": "",
        "prior_violation_event_hashes": [],
        "tool_intent_hashes": [],
        "tool_result_hashes": [],
    }
    defaults.update(overrides)
    return ReplayBundle(**defaults)


class TestReplayBundleHashStable:
    def test_replay_bundle_hash_stable(self):
        """Same inputs produce the same replay_hash on repeated construction."""
        b1 = _make_bundle()
        b2 = _make_bundle()
        assert b1.replay_hash == b2.replay_hash
        assert len(b1.replay_hash) == 64

    def test_hash_changes_with_mission_id(self):
        b1 = _make_bundle(mission_id="mission-A")
        b2 = _make_bundle(mission_id="mission-B")
        assert b1.replay_hash != b2.replay_hash

    def test_hash_changes_with_manifest_hash(self):
        b1 = _make_bundle(manifest_hash="a" * 64)
        b2 = _make_bundle(manifest_hash="b" * 64)
        assert b1.replay_hash != b2.replay_hash

    def test_hash_changes_with_config_hashes(self):
        b1 = _make_bundle(active_config_hashes={"policy_hash": "aaa"})
        b2 = _make_bundle(active_config_hashes={"policy_hash": "bbb"})
        assert b1.replay_hash != b2.replay_hash

    def test_hash_changes_with_ticks(self):
        b1 = _make_bundle(execution_start_tick=5, execution_end_tick=10)
        b2 = _make_bundle(execution_start_tick=6, execution_end_tick=10)
        assert b1.replay_hash != b2.replay_hash

    def test_hash_changes_with_violation_hashes(self):
        b1 = _make_bundle(prior_violation_event_hashes=["vh-A"])
        b2 = _make_bundle(prior_violation_event_hashes=["vh-B"])
        assert b1.replay_hash != b2.replay_hash

    def test_replay_hash_excluded_from_canonical_bytes(self):
        b = _make_bundle()
        assert b"replay_hash" not in b.canonical_bytes()

    def test_canonical_bytes_deterministic(self):
        b1 = _make_bundle()
        b2 = _make_bundle()
        assert b1.canonical_bytes() == b2.canonical_bytes()

    def test_hash_with_retrieval_used_and_citation(self):
        b = _make_bundle(retrieval_used=True, citation_hash="c" * 64)
        assert len(b.replay_hash) == 64

    def test_hash_changes_with_citation_hash(self):
        b1 = _make_bundle(retrieval_used=True, citation_hash="c" * 64)
        b2 = _make_bundle(retrieval_used=True, citation_hash="d" * 64)
        assert b1.replay_hash != b2.replay_hash


class TestReplayBundleSortingDeterministic:
    def test_replay_bundle_sorting_deterministic(self):
        """
        Lists passed in any order produce the same replay_hash after sorting.
        """
        b1 = _make_bundle(
            prior_violation_event_hashes=["vh-Z", "vh-A", "vh-M"],
            tool_intent_hashes=["ih-Z", "ih-A"],
            tool_result_hashes=["rh-Z", "rh-A"],
        )
        b2 = _make_bundle(
            prior_violation_event_hashes=["vh-A", "vh-M", "vh-Z"],
            tool_intent_hashes=["ih-A", "ih-Z"],
            tool_result_hashes=["rh-A", "rh-Z"],
        )
        assert b1.replay_hash == b2.replay_hash

    def test_violation_hashes_stored_sorted(self):
        b = _make_bundle(prior_violation_event_hashes=["vh-Z", "vh-A", "vh-M"])
        assert b.prior_violation_event_hashes == sorted(b.prior_violation_event_hashes)

    def test_intent_hashes_stored_sorted(self):
        b = _make_bundle(tool_intent_hashes=["ih-Z", "ih-A"])
        assert b.tool_intent_hashes == sorted(b.tool_intent_hashes)

    def test_result_hashes_stored_sorted(self):
        b = _make_bundle(tool_result_hashes=["rh-Z", "rh-A"])
        assert b.tool_result_hashes == sorted(b.tool_result_hashes)

    def test_config_hashes_keys_sorted_in_canonical_bytes(self):
        b = _make_bundle(active_config_hashes={"z_hash": "zzz", "a_hash": "aaa", "m_hash": "mmm"})
        raw = b.canonical_bytes().decode()
        a_pos = raw.index("a_hash")
        m_pos = raw.index("m_hash")
        z_pos = raw.index("z_hash")
        assert a_pos < m_pos < z_pos

    def test_empty_lists_allowed(self):
        b = _make_bundle(
            prior_violation_event_hashes=[],
            tool_intent_hashes=[],
            tool_result_hashes=[],
        )
        assert b.prior_violation_event_hashes == []
        assert b.tool_intent_hashes == []
        assert b.tool_result_hashes == []
        assert len(b.replay_hash) == 64


class TestReplayBundleRequiresCitationHashWhenRetrievalUsed:
    def test_replay_bundle_requires_citation_hash_when_retrieval_used(self):
        """retrieval_used=True with empty citation_hash must raise ValueError."""
        with pytest.raises(ValueError, match="citation_hash"):
            _make_bundle(retrieval_used=True, citation_hash="")

    def test_retrieval_used_false_no_citation_hash_ok(self):
        b = _make_bundle(retrieval_used=False, citation_hash="")
        assert b.citation_hash == ""

    def test_retrieval_used_true_with_citation_hash_ok(self):
        b = _make_bundle(retrieval_used=True, citation_hash="c" * 64)
        assert b.citation_hash == "c" * 64

    def test_invalid_schema_version_raises(self):
        with pytest.raises(ValueError, match="schema_version"):
            _make_bundle(schema_version=99)

    def test_empty_mission_id_raises(self):
        with pytest.raises(ValueError, match="mission_id"):
            _make_bundle(mission_id="")

    def test_empty_manifest_hash_raises(self):
        with pytest.raises(ValueError, match="manifest_hash"):
            _make_bundle(manifest_hash="")

    def test_negative_start_tick_raises(self):
        with pytest.raises(ValueError, match="execution_start_tick"):
            _make_bundle(execution_start_tick=-1, execution_end_tick=0)

    def test_end_tick_before_start_tick_raises(self):
        with pytest.raises(ValueError, match="execution_end_tick"):
            _make_bundle(execution_start_tick=10, execution_end_tick=5)

    def test_non_dict_config_hashes_raises(self):
        with pytest.raises(TypeError, match="active_config_hashes"):
            _make_bundle(active_config_hashes="not-a-dict")  # type: ignore[arg-type]

    def test_non_list_violation_hashes_raises(self):
        with pytest.raises(TypeError, match="prior_violation_event_hashes"):
            _make_bundle(prior_violation_event_hashes="not-a-list")  # type: ignore[arg-type]


class TestBuildReplayBundleFactory:
    def test_factory_produces_valid_bundle(self):
        b = build_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
        )
        assert isinstance(b, ReplayBundle)
        assert len(b.replay_hash) == 64

    def test_factory_defaults_no_retrieval(self):
        b = build_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
        )
        assert b.retrieval_used is False
        assert b.citation_hash == ""

    def test_to_dict_contains_all_fields(self):
        b = _make_bundle()
        d = b.to_dict()
        for key in (
            "schema_version",
            "mission_id",
            "execution_start_tick",
            "execution_end_tick",
            "manifest_hash",
            "active_config_hashes",
            "retrieval_used",
            "citation_hash",
            "prior_detection_signal_hash",
            "prior_violation_event_hashes",
            "tool_intent_hashes",
            "tool_result_hashes",
            "replay_hash",
        ):
            assert key in d
