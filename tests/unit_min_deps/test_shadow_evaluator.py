"""Unit tests for system_learning.validators.shadow_evaluator."""

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "test_shadow_evaluator", "execution_auth")
_emit_validates_capability("p2", "test_shadow_evaluator", "capability_check")
_emit_routes_to_capability("p2", "test_shadow_evaluator", "capability_route")
_emit_writes_via_uwg("p2", "test_shadow_evaluator", "uwg_write")
_emit_blocks_direct_write("p2", "test_shadow_evaluator", "direct_write_block")
_emit_records_tool_invocation("p2", "test_shadow_evaluator", "tool_invocation")
_emit_captures_execution_output("p2", "test_shadow_evaluator", "exec_output")
_emit_dispatches_agent("p3", "test_shadow_evaluator", "agent_dispatch")
_emit_coordinates_agents("p3", "test_shadow_evaluator", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_shadow_evaluator", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_shadow_evaluator", "healing_outcome")
_emit_escalates_failure("p3", "test_shadow_evaluator", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_shadow_evaluator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_shadow_evaluator", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_shadow_evaluator", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_shadow_evaluator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_shadow_evaluator", "eval_metric")
_emit_stores_embedding("p4", "test_shadow_evaluator", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_shadow_evaluator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_shadow_evaluator", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
from system_learning.validators.shadow_evaluator import (
    ShadowMetrics,
    ShadowRegression,
    ShadowThresholds,
    evaluate_shadow,
)

_emit_emits_metric_event("test_shadow_evaluator", "p4obs", "metric_1")
_emit_emits_metric_event("test_shadow_evaluator", "p4obs", "metric_2")
_emit_emits_metric_event("test_shadow_evaluator", "p4obs", "metric_3")
_emit_emits_metric_event("test_shadow_evaluator", "p4obs", "metric_4")
_emit_emits_metric_event("test_shadow_evaluator", "p4obs", "metric_5")
_emit_emits_metric_event("test_shadow_evaluator", "p4obs", "metric_6")
_emit_records_incident_event("test_shadow_evaluator", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_shadow_evaluator", "p4obs", "anomaly")
_emit_writes_observability_log("test_shadow_evaluator", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_shadow_evaluator", "p4obs", "mon_state")
_emit_triggers_alert("test_shadow_evaluator", "p4obs", "alert")
_emit_links_incident_trace("test_shadow_evaluator", "p4obs", "trace_link")
_emit_captures_pattern("test_shadow_evaluator", "p3lm", "pattern")
_emit_records_learning_event("test_shadow_evaluator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_shadow_evaluator", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_shadow_evaluator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_shadow_evaluator", "p3lm", "routing")
_emit_improves_agent_policy("test_shadow_evaluator", "p3lm", "policy")
_emit_stores_learning_state("test_shadow_evaluator", "p3lm", "state")
_emit_records_execution_trace("test_shadow_evaluator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_shadow_evaluator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_shadow_evaluator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_shadow_evaluator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_shadow_evaluator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_shadow_evaluator", "env_read", "p2_env_1")
_emit_reads_environ("test_shadow_evaluator", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_shadow_evaluator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_shadow_evaluator", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_shadow_evaluator")
_emit_applies_guardrail("p0", "test_shadow_evaluator", "p0_governance")
_emit_reads_policy_state("p0", "test_shadow_evaluator", "policy_binding")
_emit_snapshots_state("p0", "test_shadow_evaluator", "state_snapshot")
_emit_pulls_context("p1", "test_shadow_evaluator", "context_pull")
_emit_pulls_context("p1", "test_shadow_evaluator", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_shadow_evaluator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_shadow_evaluator", "uwg_term_secondary")
_emit_writes_through("p1", "test_shadow_evaluator", "write_through")
_emit_writes_through("p1", "test_shadow_evaluator", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_shadow_evaluator", "safety_validation")
_emit_invokes_eval("p1", "test_shadow_evaluator", "eval_call")
_emit_proposal_commits_routing("p1", "test_shadow_evaluator", "routing_commit")
_emit_escalates_to_human("p1", "test_shadow_evaluator", "human_escalation")
_emit_routes_through("p1", "test_shadow_evaluator", "route_through")
_emit_checks_agent_registry("p1", "test_shadow_evaluator", "agent_registry")
_emit_validates_agent_capability("p1", "test_shadow_evaluator", "capability")
_emit_dispatches_execution_plan("p1", "test_shadow_evaluator", "exec_plan")
_emit_agent_executes_agent("p1", "test_shadow_evaluator", "sub_agent")
_emit_routes_to_agent("p1", "test_shadow_evaluator", "target_agent")
_emit_verifies_policy("p1", "test_shadow_evaluator", "policy_check")
_emit_observes_runtime_state("p1", "test_shadow_evaluator", "runtime_state")
_emit_verifies_boundary("p1", "test_shadow_evaluator", "boundary_check")
_emit_transcripts_response("p1", "test_shadow_evaluator", "transcript")
_emit_hard_fails_untranscripted("p1", "test_shadow_evaluator")
_emit_gated_by_confidence("p1", "test_shadow_evaluator", "confidence_gate")
emit_replay_key("p0", "test_shadow_evaluator")
emit_determinism_digest("p0", "test_shadow_evaluator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestShadowEvaluator:
    def test_pass_within_thresholds(self):
        """Shadow metrics within thresholds pass validation."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=105.0,  # 5% regression
            error_rate=0.015,  # 0.005 absolute increase
            safety_violation_count=0,
            cpu_pct=52.0,  # 4% regression
            mem_mb=1020.0,  # 2% regression
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.01,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        # Should not raise
        evaluate_shadow(prod, shadow, thresholds)

    def test_fail_latency_regression(self):
        """Latency regression beyond threshold raises."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=120.0,  # 20% regression
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        with pytest.raises(ShadowRegression, match="P95_LATENCY_REGRESSION"):
            evaluate_shadow(prod, shadow, thresholds)

    def test_fail_error_rate_regression(self):
        """Error rate regression beyond threshold raises."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.08,  # 0.07 absolute increase
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        with pytest.raises(ShadowRegression, match="ERROR_RATE_REGRESSION"):
            evaluate_shadow(prod, shadow, thresholds)

    def test_fail_safety_violation_increase(self):
        """Any safety violation increase raises when forbidden."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=1,  # Increase from 0 to 1
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        with pytest.raises(ShadowRegression, match="SAFETY_VIOLATION_INCREASE"):
            evaluate_shadow(prod, shadow, thresholds)

    def test_fail_cpu_regression(self):
        """CPU regression beyond threshold raises."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=70.0,  # 40% regression
            mem_mb=1000.0,
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        with pytest.raises(ShadowRegression, match="CPU_REGRESSION"):
            evaluate_shadow(prod, shadow, thresholds)

    def test_fail_mem_regression(self):
        """Memory regression beyond threshold raises."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1500.0,  # 50% regression
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        with pytest.raises(ShadowRegression, match="MEM_REGRESSION"):
            evaluate_shadow(prod, shadow, thresholds)

    def test_multiple_violations_reported(self):
        """Multiple violations are all reported in error message."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=120.0,  # Latency violation
            error_rate=0.08,  # Error rate violation
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        with pytest.raises(ShadowRegression) as exc_info:
            evaluate_shadow(prod, shadow, thresholds)

        error_msg = str(exc_info.value)
        assert "P95_LATENCY_REGRESSION" in error_msg
        assert "ERROR_RATE_REGRESSION" in error_msg


class TestDeterminism:
    def test_evaluate_shadow_deterministic(self):
        """evaluate_shadow produces consistent results."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=105.0,
            error_rate=0.015,
            safety_violation_count=0,
            cpu_pct=52.0,
            mem_mb=1020.0,
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.01,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        # Should not raise on multiple calls
        evaluate_shadow(prod, shadow, thresholds)
        evaluate_shadow(prod, shadow, thresholds)
        evaluate_shadow(prod, shadow, thresholds)
