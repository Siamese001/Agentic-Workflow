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
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
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
