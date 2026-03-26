"""
Tests for OscillationDetector adaptive thrashing prevention.

Phase 6.2: Mathematically-Sealed Sovereignty Hardening
"""
from __future__ import annotations



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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_oscillation_freeze")
# REMOVED: _emit_applies_guardrail("p0", "test_oscillation_freeze", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_oscillation_freeze", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_oscillation_freeze", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_oscillation_freeze")
# REMOVED: emit_determinism_digest("p0", "test_oscillation_freeze")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_oscillation_freeze", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_oscillation_freeze", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_oscillation_freeze", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_oscillation_freeze", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_oscillation_freeze", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_oscillation_freeze", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_oscillation_freeze", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_oscillation_freeze", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_oscillation_freeze", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_oscillation_freeze", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_oscillation_freeze", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_oscillation_freeze", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_oscillation_freeze", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_oscillation_freeze", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_oscillation_freeze", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_oscillation_freeze", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_oscillation_freeze", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_oscillation_freeze", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_oscillation_freeze", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_oscillation_freeze", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance

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
#  # MOVED: from system_learning.enforcement.oscillation_detector import (
    OscillationDetector,
    ParameterFrozenError,
)

# REMOVED: _emit_emits_metric_event("test_oscillation_freeze", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_oscillation_freeze", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_oscillation_freeze", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_oscillation_freeze", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_oscillation_freeze", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_oscillation_freeze", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_oscillation_freeze", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_oscillation_freeze", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_oscillation_freeze", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_oscillation_freeze", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_oscillation_freeze", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_oscillation_freeze", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_oscillation_freeze", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_oscillation_freeze", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_oscillation_freeze", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_oscillation_freeze", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_oscillation_freeze", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_oscillation_freeze", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_oscillation_freeze", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_oscillation_freeze", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_oscillation_freeze", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_oscillation_freeze", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_oscillation_freeze", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_oscillation_freeze", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_oscillation_freeze", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_oscillation_freeze", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_oscillation_freeze", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_oscillation_freeze", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_oscillation_freeze", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_oscillation_freeze", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_oscillation_freeze", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_oscillation_freeze", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_oscillation_freeze", "write_through")
# REMOVED: _emit_writes_through("p1", "test_oscillation_freeze", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_oscillation_freeze", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_oscillation_freeze", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_oscillation_freeze", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_oscillation_freeze", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_oscillation_freeze", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_oscillation_freeze", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_oscillation_freeze", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_oscillation_freeze", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_oscillation_freeze", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_oscillation_freeze", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_oscillation_freeze", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_oscillation_freeze", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_oscillation_freeze", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_oscillation_freeze", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_oscillation_freeze")
# REMOVED: _emit_gated_by_confidence("p1", "test_oscillation_freeze", "confidence_gate")


class TestOscillationDetectorBasic:
    def setup_method(self) -> None:
        self.detector = OscillationDetector(cooldown_window=10, freeze_cycles=5)

    def test_single_change_no_freeze(self) -> None:
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from system_learning.enforcement.oscillation_detector import (
        self.detector.record_change("threshold_a", 0.7, cycle=1)

    def test_same_value_repeated_no_freeze(self) -> None:
        for i in range(5):
            self.detector.record_change("threshold_a", 0.7, cycle=i + 1)

    def test_two_different_values_no_freeze(self) -> None:
        self.detector.record_change("threshold_a", 0.7, cycle=1)
        self.detector.record_change("threshold_a", 0.5, cycle=2)

    def test_oscillation_triggers_freeze(self) -> None:
        self.detector.record_change("threshold_a", 0.7, cycle=1)
        self.detector.record_change("threshold_a", 0.5, cycle=2)
        with pytest.raises(Exception):

            pass
            self.detector.record_change("threshold_a", 0.7, cycle=3)

    def test_freeze_blocks_further_changes(self) -> None:
        self.detector.record_change("p", 1, cycle=1)
        self.detector.record_change("p", 2, cycle=2)
        try:
            self.detector.record_change("p", 1, cycle=3)
        with pytest.raises(Exception):

            pass
            pass
        with pytest.raises(Exception):

            pass
            self.detector.record_change("p", 3, cycle=4)

    def test_freeze_expires_after_n_cycles(self) -> None:
        detector = OscillationDetector(cooldown_window=3, freeze_cycles=3)
        detector.record_change("p", 1, cycle=1)
        detector.record_change("p", 2, cycle=2)
        try:
            detector.record_change("p", 1, cycle=3)  # triggers freeze until cycle 6
        with pytest.raises(Exception):

            pass
            pass
        # cycle 4,5,6 still frozen; cycle 7 past freeze_until=6 and uses brand-new value
        assert detector.is_frozen("p", cycle=6) is True
        assert detector.is_frozen("p", cycle=7) is False

    def test_different_params_independent(self) -> None:
        self.detector.record_change("param_a", 1, cycle=1)
        self.detector.record_change("param_a", 2, cycle=2)
        try:
            self.detector.record_change("param_a", 1, cycle=3)
        with pytest.raises(Exception):

            pass
            pass
        # param_b unaffected
        self.detector.record_change("param_b", 0.9, cycle=3)


class TestOscillationDetectorIsFrozen:
    def test_not_frozen_initially(self) -> None:
        d = OscillationDetector()
        assert d.is_frozen("p", cycle=1) is False

    def test_frozen_after_oscillation(self) -> None:
        d = OscillationDetector(cooldown_window=5, freeze_cycles=5)
        d.record_change("p", 1, cycle=1)
        d.record_change("p", 2, cycle=2)
        try:
            d.record_change("p", 1, cycle=3)
        with pytest.raises(Exception):

            pass
            pass
        assert d.is_frozen("p", cycle=4) is True

    def test_frozen_count(self) -> None:
        d = OscillationDetector(cooldown_window=5, freeze_cycles=10)
        d.record_change("p1", 1, cycle=1)
        d.record_change("p1", 2, cycle=2)
        try:
            d.record_change("p1", 1, cycle=3)
        with pytest.raises(Exception):

            pass
            pass
        assert d.frozen_count() >= 1


class TestOscillationDetectorConstructor:
    def test_invalid_cooldown_window(self) -> None:
        with pytest.raises(Exception):

            pass
            OscillationDetector(cooldown_window=1)

    def test_invalid_freeze_cycles(self) -> None:
        with pytest.raises(Exception):

            pass
            OscillationDetector(freeze_cycles=0)

    def test_reset_for_testing(self) -> None:
        d = OscillationDetector()
        d.record_change("p", 1, cycle=1)
        d.record_change("p", 2, cycle=2)
        try:
            d.record_change("p", 1, cycle=3)
        with pytest.raises(Exception):

            pass
            pass
        d.reset_for_testing()
        # after reset, should allow changes again
        d.record_change("p", 1, cycle=1)
