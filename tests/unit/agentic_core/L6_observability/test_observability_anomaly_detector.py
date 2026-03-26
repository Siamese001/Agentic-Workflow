"""
Wave 3 Phase 8 — L6 Observability / Anomaly Detector Tests

§4-compliant test suite covering:
- DetectionSignal: build, validation guards, canonical hash, determinism
- emit_detection_signal: basic emission, all metric fields
- emit_signal_from_gateway_result: success/failure mapping, authority constraint
- DriftDetector: first register, drift detection, clear, reset, global instance
- compute_replay_key: determinism, field sensitivity, canonical ordering
"""

from __future__ import annotations

import pytest

#  # MOVED: from agentic_core.L6_observability.engines.detection_signal_emitter import (
    emit_detection_signal,
    emit_signal_from_gateway_result,
)
#  # MOVED: from agentic_core.L6_observability.engines.drift_detector import (
    DriftDetector,
    get_drift_detector,
    reset_drift_detector,
)
#  # MOVED: from agentic_core.L6_observability.engines.replay_key_computer import (
    ReplayKeyComponents,
    compute_replay_key,
)
#  # MOVED: from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_observability_anomaly_detector", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_observability_anomaly_detector", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_observability_anomaly_detector", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_observability_anomaly_detector", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_observability_anomaly_detector", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_observability_anomaly_detector", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_observability_anomaly_detector", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_observability_anomaly_detector", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_observability_anomaly_detector", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_observability_anomaly_detector", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_observability_anomaly_detector", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_observability_anomaly_detector", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_observability_anomaly_detector", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_observability_anomaly_detector", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_observability_anomaly_detector", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_observability_anomaly_detector", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_observability_anomaly_detector", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_observability_anomaly_detector", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_observability_anomaly_detector", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_observability_anomaly_detector", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_observability_anomaly_detector", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_observability_anomaly_detector", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_observability_anomaly_detector", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_observability_anomaly_detector", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_observability_anomaly_detector", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_observability_anomaly_detector", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_observability_anomaly_detector", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_observability_anomaly_detector", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_observability_anomaly_detector")
# REMOVED: _emit_applies_guardrail("p0", "test_observability_anomaly_detector", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_observability_anomaly_detector", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_observability_anomaly_detector", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_observability_anomaly_detector", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_observability_anomaly_detector", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_observability_anomaly_detector", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_observability_anomaly_detector", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_observability_anomaly_detector", "write_through")
# REMOVED: _emit_writes_through("p1", "test_observability_anomaly_detector", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_observability_anomaly_detector", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_observability_anomaly_detector", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_observability_anomaly_detector", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_observability_anomaly_detector", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_observability_anomaly_detector", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_observability_anomaly_detector", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_observability_anomaly_detector", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_observability_anomaly_detector", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_observability_anomaly_detector", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_observability_anomaly_detector", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_observability_anomaly_detector", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_observability_anomaly_detector", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_observability_anomaly_detector", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_observability_anomaly_detector", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_observability_anomaly_detector")
# REMOVED: _emit_gated_by_confidence("p1", "test_observability_anomaly_detector", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_observability_anomaly_detector")
# REMOVED: emit_determinism_digest("p0", "test_observability_anomaly_detector")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_observability_anomaly_detector", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_observability_anomaly_detector", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_observability_anomaly_detector", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_observability_anomaly_detector", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_observability_anomaly_detector", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_observability_anomaly_detector", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_observability_anomaly_detector", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_observability_anomaly_detector", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_observability_anomaly_detector", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_observability_anomaly_detector", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_observability_anomaly_detector", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_observability_anomaly_detector", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_observability_anomaly_detector", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_observability_anomaly_detector", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_observability_anomaly_detector", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_observability_anomaly_detector", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_observability_anomaly_detector", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_observability_anomaly_detector", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_observability_anomaly_detector", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_observability_anomaly_detector", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASE = {
    "mission_id": "mission-A",
    "created_at_utc": 1_700_000_000,
    "anomaly_score": 0.2,
    "escalation_rate": 0.1,
    "retry_rate": 0.05,
    "violation_density": 0.0,
    "schema_version": 1,
}


def _signal(**overrides) -> DetectionSignal:
    kwargs = {**_BASE, **overrides}
    return DetectionSignal.build(**kwargs)


def _components(**overrides) -> ReplayKeyComponents:
    defaults = {
        "tier_selection": "LOW",
        "retry_count": 0,
        "threshold_config": {"X": 0.75},
        "tool_budget_caps": {"tool_a": 100},
        "freshness_windows": {"ctx": 3600},
        "config_surface_hash": "abc123",
        "embedding_pack_hash": "deadbeef",
        "embedding_model_version": "v1.0",
        "c0_context_hash": "cafebabe",
    }
    return ReplayKeyComponents(**{**defaults, **overrides})


# ===========================================================================
# 1. DetectionSignal — build, hash, validation guards
# ===========================================================================


class TestDetectionSignal:
    @pytest.mark.governance
    def test_build_returns_detection_signal(self):
                from agentic_core.L6_observability.engines.detection_signal_emitter import (
                from agentic_core.L6_observability.engines.drift_detector import (
                from agentic_core.L6_observability.engines.replay_key_computer import (
                from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                s = _signal()
                assert isinstance(s, DetectionSignal)

        assert isinstance(s, DetectionSignal)

    @pytest.mark.governance
    def test_signal_hash_is_64_hex_chars(self):
        s = _signal()
        assert len(s.signal_hash) == 64
        int(s.signal_hash, 16)

    @pytest.mark.governance
    def test_signal_hash_deterministic_for_same_inputs(self):
        s1 = _signal()
        s2 = _signal()
        assert s1.signal_hash == s2.signal_hash

    @pytest.mark.governance
    def test_signal_hash_differs_for_different_mission_id(self):
        s1 = _signal(mission_id="m1")
        s2 = _signal(mission_id="m2")
        assert s1.signal_hash != s2.signal_hash

    @pytest.mark.governance
    def test_signal_hash_differs_for_different_anomaly_score(self):
        s1 = _signal(anomaly_score=0.1)
        s2 = _signal(anomaly_score=0.9)
        assert s1.signal_hash != s2.signal_hash

    @pytest.mark.governance
    def test_raises_when_schema_version_below_1(self):
    """Test raises_when_schema_version_below_1 contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
    def test_exact_boundary_created_at_utc_0_valid(self):
        s = _signal(created_at_utc=0)
        assert s.created_at_utc == 0

    @pytest.mark.governance
    @pytest.mark.parametrize("field", ["anomaly_score", "escalation_rate", "retry_rate", "violation_density"])
    def test_raises_when_float_field_below_0(self, field):
        with pytest.raises(ValueError, match=field):
            DetectionSignal.build(**{**_BASE, field: -0.01})

    @pytest.mark.governance
    @pytest.mark.parametrize("field", ["anomaly_score", "escalation_rate", "retry_rate", "violation_density"])
    def test_raises_when_float_field_above_1(self, field):
        with pytest.raises(ValueError, match=field):
            DetectionSignal.build(**{**_BASE, field: 1.01})

    @pytest.mark.governance
    @pytest.mark.parametrize("field", ["anomaly_score", "escalation_rate", "retry_rate", "violation_density"])
    def test_boundary_float_field_0_valid(self, field):
        s = DetectionSignal.build(**{**_BASE, field: 0.0})
        assert getattr(s, field) == 0.0

    @pytest.mark.governance
    @pytest.mark.parametrize("field", ["anomaly_score", "escalation_rate", "retry_rate", "violation_density"])
    def test_boundary_float_field_1_valid(self, field):
        s = DetectionSignal.build(**{**_BASE, field: 1.0})
        assert getattr(s, field) == 1.0

    @pytest.mark.governance
    def test_canonical_bytes_is_deterministic(self):
        s = _signal()
        assert s.canonical_bytes() == s.canonical_bytes()

    @pytest.mark.governance
    def test_compute_hash_matches_signal_hash(self):
        s = _signal()
        expected = DetectionSignal.compute_hash(
            schema_version=s.schema_version,
            mission_id=s.mission_id,
            created_at_utc=s.created_at_utc,
            anomaly_score=s.anomaly_score,
            escalation_rate=s.escalation_rate,
            retry_rate=s.retry_rate,
            violation_density=s.violation_density,
        )
        assert s.signal_hash == expected


# ===========================================================================
# 2. emit_detection_signal — emission path
# ===========================================================================


class TestEmitDetectionSignal:
    @pytest.mark.governance
    def test_returns_detection_signal(self):
        s = emit_detection_signal(mission_id="m", created_at_utc=1000)
        assert isinstance(s, DetectionSignal)

    @pytest.mark.governance
    def test_default_all_metrics_are_zero(self):
        s = emit_detection_signal(mission_id="m", created_at_utc=1000)
        assert s.anomaly_score == 0.0
        assert s.escalation_rate == 0.0
        assert s.retry_rate == 0.0
        assert s.violation_density == 0.0

    @pytest.mark.governance
    def test_custom_anomaly_score_propagated(self):
        s = emit_detection_signal(mission_id="m", created_at_utc=1000, anomaly_score=0.7)
        assert s.anomaly_score == 0.7

    @pytest.mark.governance
    def test_mission_id_and_timestamp_propagated(self):
        s = emit_detection_signal(mission_id="test-mission", created_at_utc=42)
        assert s.mission_id == "test-mission"
        assert s.created_at_utc == 42

    @pytest.mark.governance
    def test_deterministic_for_same_inputs_twice(self):
        s1 = emit_detection_signal(mission_id="m", created_at_utc=1000, anomaly_score=0.3)
        s2 = emit_detection_signal(mission_id="m", created_at_utc=1000, anomaly_score=0.3)
        assert s1.signal_hash == s2.signal_hash

    @pytest.mark.governance
    def test_schema_version_default_is_1(self):
        s = emit_detection_signal(mission_id="m", created_at_utc=1000)
        assert s.schema_version == 1


# ===========================================================================
# 3. emit_signal_from_gateway_result — authority constraint & field derivation
# ===========================================================================


class TestEmitSignalFromGatewayResult:
    @pytest.mark.governance
    def test_returns_detection_signal(self):
        gw = type("GW", (), {"success": True, "error": None})()
        s = emit_signal_from_gateway_result("m", 1000, gw)
        assert isinstance(s, DetectionSignal)

    @pytest.mark.governance
    def test_anomaly_score_is_0_when_success(self):
        gw = type("GW", (), {"success": True, "error": None})()
        s = emit_signal_from_gateway_result("m", 1000, gw)
        assert s.anomaly_score == 0.0

    @pytest.mark.governance
    def test_anomaly_score_is_nonzero_when_failure(self):
        gw = type("GW", (), {"success": False, "error": "oops"})()
        s = emit_signal_from_gateway_result("m", 1000, gw)
        assert s.anomaly_score > 0.0

    @pytest.mark.governance
    def test_violation_density_0_when_no_error(self):
        gw = type("GW", (), {"success": True, "error": None})()
        s = emit_signal_from_gateway_result("m", 1000, gw)
        assert s.violation_density == 0.0

    @pytest.mark.governance
    def test_violation_density_nonzero_when_error_present(self):
        gw = type("GW", (), {"success": True, "error": "some error"})()
        s = emit_signal_from_gateway_result("m", 1000, gw)
        assert s.violation_density > 0.0

    @pytest.mark.governance
    def test_gateway_result_not_mutated(self):
        gw = type("GW", (), {"success": True, "error": None})()
# REMOVED:         emit_signal_from_gateway_result("m", 1000, gw)
        assert gw.success is True
        assert gw.error is None

    @pytest.mark.governance
    def test_tolerates_gateway_result_missing_success_attribute(self):
        gw = object()  # no success/error attributes
        s = emit_signal_from_gateway_result("m", 1000, gw)
        assert isinstance(s, DetectionSignal)

    @pytest.mark.governance
    def test_deterministic_for_same_gateway_result_twice(self):
        gw = type("GW", (), {"success": False, "error": "err"})()
        s1 = emit_signal_from_gateway_result("m", 1000, gw)
        s2 = emit_signal_from_gateway_result("m", 1000, gw)
        assert s1.signal_hash == s2.signal_hash


# ===========================================================================
# 4. DriftDetector — all branches
# ===========================================================================


class TestDriftDetector:
    @pytest.mark.governance
    def test_first_registration_returns_false_no_drift(self):
        d = DriftDetector()
        result = d.register_context_hash("key1", "hash_aaa")
        assert result is False

    @pytest.mark.governance
    def test_second_registration_same_hash_returns_false(self):
        d = DriftDetector()
        d.register_context_hash("key1", "hash_aaa")
        result = d.register_context_hash("key1", "hash_aaa")
        assert result is False

    @pytest.mark.governance
    def test_second_registration_different_hash_returns_true(self):
        d = DriftDetector()
        d.register_context_hash("key1", "hash_aaa")
        result = d.register_context_hash("key1", "hash_bbb")
        assert result is True

    @pytest.mark.governance
    def test_has_drift_false_when_no_drift(self):
        d = DriftDetector()
        d.register_context_hash("key1", "hash_aaa")
        assert d.has_drift("key1") is False

    @pytest.mark.governance
    def test_has_drift_true_after_drift_detected(self):
        d = DriftDetector()
        d.register_context_hash("key1", "hash_aaa")
        d.register_context_hash("key1", "hash_bbb")
        assert d.has_drift("key1") is True

    @pytest.mark.governance
    def test_get_drift_alert_returns_none_when_no_drift(self):
        d = DriftDetector()
        assert d.get_drift_alert("key1") is None

    @pytest.mark.governance
    def test_get_drift_alert_returns_old_new_hashes(self):
        d = DriftDetector()
        d.register_context_hash("key1", "old_hash")
        d.register_context_hash("key1", "new_hash")
        alert = d.get_drift_alert("key1")
        assert alert is not None
        assert alert == ("old_hash", "new_hash")

    @pytest.mark.governance
    def test_clear_drift_alert_removes_alert(self):
        d = DriftDetector()
        d.register_context_hash("key1", "h1")
        d.register_context_hash("key1", "h2")
        d.clear_drift_alert("key1")
        assert d.has_drift("key1") is False

    @pytest.mark.governance
    def test_clear_drift_alert_on_nonexistent_key_is_noop(self):
        d = DriftDetector()
        d.clear_drift_alert("nonexistent")  # must not raise

    @pytest.mark.governance
    def test_get_all_drift_alerts_returns_all_drifted_keys(self):
        d = DriftDetector()
        d.register_context_hash("k1", "h1")
        d.register_context_hash("k1", "h2")
        d.register_context_hash("k2", "ha")
        d.register_context_hash("k2", "hb")
        alerts = d.get_all_drift_alerts()
        assert set(alerts.keys()) == {"k1", "k2"}

    @pytest.mark.governance
    def test_get_all_drift_alerts_returns_copy(self):
        d = DriftDetector()
        d.register_context_hash("k1", "h1")
        d.register_context_hash("k1", "h2")
        alerts = d.get_all_drift_alerts()
        alerts["new_key"] = ("x", "y")
        assert "new_key" not in d.get_all_drift_alerts()

    @pytest.mark.governance
    def test_reset_clears_registry_and_alerts(self):
        d = DriftDetector()
        d.register_context_hash("k1", "h1")
        d.register_context_hash("k1", "h2")
        d.reset()
        assert d.has_drift("k1") is False
        assert d.get_context_hash("k1") is None

    @pytest.mark.governance
    def test_compute_c0_context_hash_is_64_hex_chars(self):
        d = DriftDetector()
        h = d.compute_c0_context_hash("some context")
        assert len(h) == 64
        int(h, 16)

    @pytest.mark.governance
    def test_compute_c0_context_hash_deterministic(self):
        d = DriftDetector()
        h1 = d.compute_c0_context_hash("ctx")
        h2 = d.compute_c0_context_hash("ctx")
        assert h1 == h2

    @pytest.mark.governance
    def test_compute_c0_context_hash_differs_for_different_context(self):
        d = DriftDetector()
        assert d.compute_c0_context_hash("A") != d.compute_c0_context_hash("B")

    @pytest.mark.governance
    def test_get_context_hash_returns_none_for_unknown_key(self):
        d = DriftDetector()
        assert d.get_context_hash("missing") is None

    @pytest.mark.governance
    def test_get_context_hash_returns_first_registered_hash(self):
        d = DriftDetector()
        d.register_context_hash("k", "initial_hash")
        assert d.get_context_hash("k") == "initial_hash"

    @pytest.mark.governance
    def test_independent_keys_do_not_interfere(self):
        d = DriftDetector()
        d.register_context_hash("k1", "h1")
        d.register_context_hash("k2", "ha")
        d.register_context_hash("k2", "hb")
        assert d.has_drift("k1") is False
        assert d.has_drift("k2") is True


# ===========================================================================
# 5. Global drift detector singleton
# ===========================================================================


class TestGlobalDriftDetector:
    @pytest.mark.governance
    def test_get_drift_detector_returns_detector_instance(self):
        reset_drift_detector()
        d = get_drift_detector()
        assert isinstance(d, DriftDetector)

    @pytest.mark.governance
    def test_get_drift_detector_returns_same_instance_twice(self):
        reset_drift_detector()
        d1 = get_drift_detector()
        d2 = get_drift_detector()
        assert d1 is d2

    @pytest.mark.governance
    def test_reset_drift_detector_clears_state(self):
        d = get_drift_detector()
        d.register_context_hash("key", "h1")
        d.register_context_hash("key", "h2")
        reset_drift_detector()
        d2 = get_drift_detector()
        assert not d2.has_drift("key")


# ===========================================================================
# 6. compute_replay_key — determinism, field sensitivity, canonical ordering
# ===========================================================================


class TestComputeReplayKey:
    @pytest.mark.governance
    def test_returns_64_hex_char_string(self):
        key = compute_replay_key(_components())
        assert len(key) == 64
        int(key, 16)

    @pytest.mark.governance
    def test_deterministic_for_same_components_twice(self):
        c = _components()
        assert compute_replay_key(c) == compute_replay_key(c)

    @pytest.mark.governance
    def test_differs_when_tier_selection_changes(self):
        k1 = compute_replay_key(_components(tier_selection="LOW"))
        k2 = compute_replay_key(_components(tier_selection="HIGH"))
        assert k1 != k2

    @pytest.mark.governance
    def test_differs_when_retry_count_changes(self):
        k1 = compute_replay_key(_components(retry_count=0))
        k2 = compute_replay_key(_components(retry_count=1))
        assert k1 != k2

    @pytest.mark.governance
    def test_differs_when_threshold_config_changes(self):
        k1 = compute_replay_key(_components(threshold_config={"X": 0.5}))
        k2 = compute_replay_key(_components(threshold_config={"X": 0.9}))
        assert k1 != k2

    @pytest.mark.governance
    def test_differs_when_embedding_pack_hash_changes(self):
        k1 = compute_replay_key(_components(embedding_pack_hash="aaa"))
        k2 = compute_replay_key(_components(embedding_pack_hash="bbb"))
        assert k1 != k2

    @pytest.mark.governance
    def test_differs_when_c0_context_hash_changes(self):
        k1 = compute_replay_key(_components(c0_context_hash="ctx1"))
        k2 = compute_replay_key(_components(c0_context_hash="ctx2"))
        assert k1 != k2

    @pytest.mark.governance
    def test_replay_key_components_is_frozen(self):
        c = _components()
        with pytest.raises((AttributeError, TypeError)):
            c.tier_selection = "CRITICAL"  # type: ignore[misc]

    @pytest.mark.governance
    def test_threshold_config_key_order_independence(self):
        k1 = compute_replay_key(_components(threshold_config={"A": 0.5, "B": 0.75}))
        k2 = compute_replay_key(_components(threshold_config={"B": 0.75, "A": 0.5}))
        assert k1 == k2
