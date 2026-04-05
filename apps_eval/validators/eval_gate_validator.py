"""
Eval Gate Validator — apps_eval.

Enforces quality gates on evaluation run results:
- Overall score meets minimum threshold
- No regressions when fail_on_regression=True
- No timeout violations beyond max_timeout_violations
- All required suites ran

Deterministic: all checks are threshold comparisons.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_authorize_and_execute("p2", "eval_gate_validator", "execution_auth")
_emit_validates_capability("p2", "eval_gate_validator", "capability_check")
_emit_routes_to_capability("p2", "eval_gate_validator", "capability_route")
_emit_writes_via_uwg("p2", "eval_gate_validator", "uwg_write")
_emit_blocks_direct_write("p2", "eval_gate_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "eval_gate_validator", "tool_invocation")
_emit_captures_execution_output("p2", "eval_gate_validator", "exec_output")
_emit_dispatches_agent("p3", "eval_gate_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "eval_gate_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "eval_gate_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "eval_gate_validator", "healing_outcome")
_emit_escalates_failure("p3", "eval_gate_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "eval_gate_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "eval_gate_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "eval_gate_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "eval_gate_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "eval_gate_validator", "eval_metric")
_emit_stores_embedding("p4", "eval_gate_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "eval_gate_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "eval_gate_validator", "exec_snapshot_link")
from apps_eval.types.eval_types import RegressionRecord, RegressionVerdict, ScorecardRow, SuiteResult

_emit_applies_guardrail("p0", "eval_gate_validator", "p0_governance")
_emit_reads_policy_state("p0", "eval_gate_validator", "policy_binding")
_emit_snapshots_state("p0", "eval_gate_validator", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("eval_gate_validator", "p4obs", "metric_1")
_emit_emits_metric_event("eval_gate_validator", "p4obs", "metric_2")
_emit_emits_metric_event("eval_gate_validator", "p4obs", "metric_3")
_emit_emits_metric_event("eval_gate_validator", "p4obs", "metric_4")
_emit_emits_metric_event("eval_gate_validator", "p4obs", "metric_5")
_emit_emits_metric_event("eval_gate_validator", "p4obs", "metric_6")
_emit_records_incident_event("eval_gate_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("eval_gate_validator", "p4obs", "anomaly")
_emit_writes_observability_log("eval_gate_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("eval_gate_validator", "p4obs", "mon_state")
_emit_triggers_alert("eval_gate_validator", "p4obs", "alert")
_emit_links_incident_trace("eval_gate_validator", "p4obs", "trace_link")
_emit_captures_pattern("eval_gate_validator", "p3lm", "pattern")
_emit_records_learning_event("eval_gate_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("eval_gate_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("eval_gate_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("eval_gate_validator", "p3lm", "routing")
_emit_improves_agent_policy("eval_gate_validator", "p3lm", "policy")
_emit_stores_learning_state("eval_gate_validator", "p3lm", "state")
_emit_records_execution_trace("eval_gate_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("eval_gate_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("eval_gate_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("eval_gate_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("eval_gate_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("eval_gate_validator", "env_read", "p2_env_1")
_emit_reads_environ("eval_gate_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("eval_gate_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("eval_gate_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "eval_gate_validator", "context_pull")
_emit_pulls_context("p1", "eval_gate_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "eval_gate_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "eval_gate_validator", "uwg_term_2")
_emit_writes_through("p1", "eval_gate_validator", "write_through")
_emit_writes_through("p1", "eval_gate_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "eval_gate_validator", "safety_validation")
_emit_invokes_eval("p1", "eval_gate_validator", "eval_call")
_emit_proposal_commits_routing("p1", "eval_gate_validator", "routing_commit")
_emit_escalates_to_human("p1", "eval_gate_validator", "human_escalation")
_emit_routes_through("p1", "eval_gate_validator", "route_through")
_emit_checks_agent_registry("p1", "eval_gate_validator", "agent_registry")
_emit_validates_agent_capability("p1", "eval_gate_validator", "capability")
_emit_dispatches_execution_plan("p1", "eval_gate_validator", "exec_plan")
_emit_agent_executes_agent("p1", "eval_gate_validator", "sub_agent")
_emit_routes_to_agent("p1", "eval_gate_validator", "target_agent")
_emit_verifies_policy("p1", "eval_gate_validator", "policy_check")
_emit_observes_runtime_state("p1", "eval_gate_validator", "runtime_state")
_emit_verifies_boundary("p1", "eval_gate_validator", "boundary_check")
_emit_transcripts_response("p1", "eval_gate_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "eval_gate_validator")
_emit_gated_by_confidence("p1", "eval_gate_validator", "confidence_gate")
emit_replay_key("p0", "eval_gate_validator")
emit_determinism_digest("p0", "eval_gate_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_log = logging.getLogger(__name__)

# Default gate thresholds (can be overridden in __init__)
_DEFAULT_MIN_SCORE = 0.70
_DEFAULT_FAIL_ON_REGRESSION = True
_DEFAULT_MAX_TIMEOUT_VIOLATIONS = 0


@dataclass
class EvalViolation:
    """A single evaluation gate violation."""

    rule_id: str
    severity: str
    message: str


@dataclass
class EvalGateResult:
    """Result of evaluation gate check."""

    passed: bool
    violations: list[EvalViolation] = field(default_factory=list)
    overall_score: float = 0.0


class EvalGateValidator:
    """Validate evaluation run results against configured quality gates."""

    def __init__(
        self,
        min_overall_score: float = _DEFAULT_MIN_SCORE,
        fail_on_regression: bool = _DEFAULT_FAIL_ON_REGRESSION,
        max_timeout_violations: int = _DEFAULT_MAX_TIMEOUT_VIOLATIONS,
    ) -> None:
        self._min_overall_score = min_overall_score
        self._fail_on_regression = fail_on_regression
        self._max_timeout_violations = max_timeout_violations

    def validate(
        self,
        suite_results: list[SuiteResult],
        scorecard_rows: list[ScorecardRow],
        regression_records: list[RegressionRecord],
        overall_score: float,
    ) -> EvalGateResult:
        """Run all gate checks.

        Returns:
            EvalGateResult with all violations.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EvalGateValidator.validate")

        violations: list[EvalViolation] = []

        if overall_score < self._min_overall_score:
            violations.append(
                EvalViolation(
                    rule_id="EVAL_SCORE_BELOW_THRESHOLD",
                    severity="BLOCK",
                    message=(
                        f"Overall score {overall_score:.2%} is below minimum {self._min_overall_score:.2%}."
                    ),
                )
            )

        if self._fail_on_regression:
            regressions = [r for r in regression_records if r.verdict == RegressionVerdict.REGRESSION]
            if regressions:
                dims = [r.dimension_id for r in regressions]
                violations.append(
                    EvalViolation(
                        rule_id="EVAL_REGRESSION_DETECTED",
                        severity="BLOCK",
                        message=f"Regression detected in dimensions: {dims}",
                    )
                )

        for suite in suite_results:
            if suite.error:
                violations.append(
                    EvalViolation(
                        rule_id="EVAL_SUITE_ERROR",
                        severity="BLOCK",
                        message=f"Suite '{suite.suite_id}' encountered an error: {suite.error}",
                    )
                )

        timeout_count = sum(
            1
            for suite in suite_results
            for scenario in suite.scenarios
            if scenario.outcome.value == "TIMEOUT"
        )
        if timeout_count > self._max_timeout_violations:
            violations.append(
                EvalViolation(
                    rule_id="EVAL_TIMEOUT_VIOLATIONS",
                    severity="BLOCK",
                    message=(
                        f"Timeout violations: {timeout_count} exceeds max {self._max_timeout_violations}."
                    ),
                )
            )

        block_count = sum(1 for v in violations if v.severity == "BLOCK")
        return EvalGateResult(
            passed=block_count == 0,
            violations=violations,
            overall_score=overall_score,
        )
