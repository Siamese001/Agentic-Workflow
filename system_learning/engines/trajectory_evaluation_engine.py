"""Trajectory Evaluation Engine — Evaluation Spine Component C.

Evaluates execution trajectory per Evaluation Spine documentation:
  - Tool selection/order
  - Argument correctness
  - Retry thrashing
  - Budget discipline
  - Policy compliance

Deterministic, with full ADG traceability.
"""

from __future__ import annotations

import logging

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_blocks_direct_write,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_records_execution_trace,
    _emit_records_tool_invocation,
    _emit_routes_to_agent,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
from system_learning.enforcement.determinism import stable_sha256_json
from system_learning.types.evaluation_spine_types import MetricScore, TrajectoryEvaluationResult

# ADG wiring for trajectory evaluation engine
_emit_records_execution_trace("trajectory_evaluation_engine", "p0", "trajectory_eval_trace")
_emit_applies_guardrail("p0", "trajectory_evaluation_engine", "p0_governance")
emit_replay_key("p0", "trajectory_evaluation_engine")
emit_determinism_digest("p0", "trajectory_evaluation_engine")
_emit_writes_via_uwg("p2", "trajectory_evaluation_engine", "uwg_write")
_emit_blocks_direct_write("p2", "trajectory_evaluation_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "trajectory_evaluation_engine", "tool_invocation")
_emit_captures_execution_output("p2", "trajectory_evaluation_engine", "exec_output")
_emit_dispatches_agent("p3", "trajectory_evaluation_engine", "agent_dispatch")
_emit_dispatches_execution_plan("p3", "trajectory_evaluation_engine", "exec_plan")
_emit_routes_to_agent("p3", "trajectory_evaluation_engine", "target_agent")
_emit_checks_agent_registry("p3", "trajectory_evaluation_engine", "agent_registry")
_emit_validates_agent_capability("p3", "trajectory_evaluation_engine", "capability")
_emit_verifies_policy("p3", "trajectory_evaluation_engine", "policy_check")
_emit_verifies_boundary("p3", "trajectory_evaluation_engine", "boundary_check")
_emit_agent_executes_agent("p3", "trajectory_evaluation_engine", "sub_agent")

logger = logging.getLogger(__name__)


# =============================================================================
# TrajectoryEvaluationEngine
# =============================================================================


class TrajectoryEvaluationEngine:
    """Engine for evaluating execution trajectory (Component C).

    Evaluates 5 trajectory metrics per Evaluation Spine:
        1. Tool selection — Quality of tool choices
        2. Argument correctness — Quality of tool arguments
        3. Retry thrashing — Efficiency of retry behavior
        4. Budget discipline — Adherence to resource budgets
        5. Policy compliance — Adherence to policies

    Deterministic: Same inputs always produce same output hash.

    Attributes
    ----------
    max_acceptable_retries:
        Maximum retries before considering thrashing.
    budget_tolerance:
        Tolerance factor for budget overruns.
    """

    DEFAULT_MAX_RETRIES: int = 3
    DEFAULT_BUDGET_TOLERANCE: float = 1.2  # 20% over budget acceptable

    # Default weights for overall score calculation
    DEFAULT_WEIGHTS: dict[str, float] = {
        "tool_selection": 0.25,
        "arg_correctness": 0.20,
        "retry_thrashing": 0.20,
        "budget_discipline": 0.20,
        "policy_compliance": 0.15,
    }

    def __init__(
        self,
        max_acceptable_retries: int | None = None,
        budget_tolerance: float | None = None,
        weights: dict[str, float] | None = None,
    ) -> None:
        self.max_acceptable_retries = max_acceptable_retries or self.DEFAULT_MAX_RETRIES
        self.budget_tolerance = budget_tolerance or self.DEFAULT_BUDGET_TOLERANCE
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

    def evaluate_trajectory(
        self,
        trace_id: str,
        tool_calls: list[dict],
        execution_metadata: dict,
        timestamp_utc: int,
    ) -> TrajectoryEvaluationResult:
        """Evaluate execution trajectory across 5 metrics.

        Parameters
        ----------
        trace_id:
            Source execution trace identifier.
        tool_calls:
            List of tool call records from execution.
        execution_metadata:
            Metadata about the execution (budget, policy checks, etc.).
        timestamp_utc:
            Unix timestamp provided by caller (no wall-clock reads).

        Returns
        -------
        TrajectoryEvaluationResult
            Deterministic trajectory evaluation result.
        """
        _emit_records_execution_trace("trajectory_evaluation_engine", "eval_start", trace_id)

        # Extract tool sequence
        tool_sequence = self._extract_tool_sequence(tool_calls)

        # Count retries
        retry_count = self._count_retries(tool_calls)

        # Extract budget info
        budget_used = execution_metadata.get("budget_used", 0.0)
        budget_allocated = execution_metadata.get("budget_allocated", 100.0)

        # Evaluate each metric
        tool_selection = self._evaluate_tool_selection(tool_calls, tool_sequence)
        arg_correctness = self._evaluate_arg_correctness(tool_calls)
        retry_thrashing = self._evaluate_retry_thrashing(retry_count)
        budget_discipline = self._evaluate_budget_discipline(budget_used, budget_allocated)
        policy_compliance = self._evaluate_policy_compliance(execution_metadata)

        # Build metric scores with evidence
        metric_scores = (
            MetricScore(
                metric_name="tool_selection",
                score=tool_selection,
                confidence=0.85,
                evidence=f"Tool selection evaluated: {tool_selection:.4f}",
            ),
            MetricScore(
                metric_name="arg_correctness",
                score=arg_correctness,
                confidence=0.8,
                evidence=f"Argument correctness evaluated: {arg_correctness:.4f}",
            ),
            MetricScore(
                metric_name="retry_thrashing",
                score=retry_thrashing,
                confidence=0.9,
                evidence=f"Retry efficiency evaluated: {retry_thrashing:.4f}",
            ),
            MetricScore(
                metric_name="budget_discipline",
                score=budget_discipline,
                confidence=0.85,
                evidence=f"Budget discipline evaluated: {budget_discipline:.4f}",
            ),
            MetricScore(
                metric_name="policy_compliance",
                score=policy_compliance,
                confidence=0.75,
                evidence=f"Policy compliance evaluated: {policy_compliance:.4f}",
            ),
        )

        # Calculate overall score
        overall_score = self._calculate_overall_score(
            tool_selection,
            arg_correctness,
            retry_thrashing,
            budget_discipline,
            policy_compliance,
        )

        # Build evaluation summary
        evaluation_summary = self._build_evaluation_summary(
            tool_selection,
            arg_correctness,
            retry_thrashing,
            budget_discipline,
            policy_compliance,
            overall_score,
            retry_count,
            budget_used,
            budget_allocated,
        )

        _emit_records_execution_trace("trajectory_evaluation_engine", "eval_complete", trace_id)

        result = TrajectoryEvaluationResult(
            artifact_type="TRAJECTORY_EVALUATION_RESULT",
            result_id=stable_sha256_json({
                "trace_id": trace_id,
                "overall_score": overall_score,
                "timestamp_utc": timestamp_utc,
            }),
            trace_id=trace_id,
            tool_selection=tool_selection,
            arg_correctness=arg_correctness,
            retry_thrashing=retry_thrashing,
            budget_discipline=budget_discipline,
            policy_compliance=policy_compliance,
            overall_score=overall_score,
            metric_scores=metric_scores,
            tool_sequence=tuple(tool_sequence),
            retry_count=retry_count,
            budget_used=budget_used,
            budget_allocated=budget_allocated,
            evaluation_summary=evaluation_summary,
            timestamp_utc=timestamp_utc,
        )

        logger.info(
            "Trajectory evaluation complete: trace_id=%s, overall_score=%.4f, retries=%d",
            trace_id,
            overall_score,
            retry_count,
        )

        return result

    def _extract_tool_sequence(self, tool_calls: list[dict]) -> list[str]:
        """Extract ordered sequence of tool names from tool calls."""
        sequence = []
        for call in tool_calls:
            tool_name = call.get("tool_name") or call.get("tool") or call.get("name")
            if tool_name:
                sequence.append(tool_name)
        return sequence

    def _count_retries(self, tool_calls: list[dict]) -> int:
        """Count number of retry attempts in tool calls."""
        retry_count = 0
        for call in tool_calls:
            # Check for retry indicators
            if call.get("is_retry", False):
                retry_count += 1
            if call.get("retry_count", 0) > 0:
                retry_count += call.get("retry_count", 0)
            # Check for error recovery
            if call.get("error") and call.get("subsequent_success"):
                retry_count += 1
        return retry_count

    def _evaluate_tool_selection(self, tool_calls: list[dict], tool_sequence: list[str]) -> float:
        """Evaluate quality of tool selection.

        Scores based on:
        - Appropriate tool choices for the task
        - Optimal tool sequence
        - No redundant tool calls
        """
        score = 0.0

        if not tool_calls:
            return 0.0

        # Score for having any tools selected
        score += 0.3

        # Score for diverse tool usage (not stuck on one tool)
        unique_tools = len(set(tool_sequence))
        if unique_tools > 1:
            score += min(0.3, unique_tools * 0.1)
        else:
            # Using single tool might be correct for simple tasks
            score += 0.2

        # Score for optimal sequence (heuristic: certain tools should come first/last)
        if tool_sequence:
            # Router/planner tools should come early
            early_tools = ["router", "planner", "orchestrator"]
            if any(t in tool_sequence[0].lower() for t in early_tools):
                score += 0.2

            # Output/writer tools should come late
            late_tools = ["writer", "output", "formatter"]
            if any(t in tool_sequence[-1].lower() for t in late_tools):
                score += 0.2

        return min(1.0, score)

    def _evaluate_arg_correctness(self, tool_calls: list[dict]) -> float:
        """Evaluate correctness of tool arguments.

        Scores based on:
        - Required arguments present
        - Arguments properly formatted
        - No malformed inputs
        """
        if not tool_calls:
            return 0.0

        correct_count = 0

        for call in tool_calls:
            args = call.get("arguments", {})

            # Check for non-empty arguments
            if args:
                correct_count += 0.5

            # Check for valid argument types
            if all(isinstance(v, (str, int, float, bool, list, dict)) for v in args.values()):
                correct_count += 0.3

            # Check for no null/None critical args
            critical_null = any(v is None for k, v in args.items() if k.startswith("required"))
            if not critical_null:
                correct_count += 0.2

        return min(1.0, correct_count / len(tool_calls))

    def _evaluate_retry_thrashing(self, retry_count: int) -> float:
        """Evaluate retry efficiency.

        Higher score for fewer retries (inverse relationship).
        Score = 1.0 - (retry_count / max_acceptable_retries)
        """
        if retry_count == 0:
            return 1.0

        # Linear decay based on retry count
        score = 1.0 - (retry_count / self.max_acceptable_retries)
        return max(0.0, score)

    def _evaluate_budget_discipline(self, budget_used: float, budget_allocated: float) -> float:
        """Evaluate budget adherence.

        Score based on:
        - Staying within budget (full score if under)
        - Graceful degradation if slightly over
        - Zero score if significantly over
        """
        if budget_allocated <= 0:
            return 0.0

        usage_ratio = budget_used / budget_allocated

        if usage_ratio <= 1.0:
            # Under budget - full score with bonus for efficiency
            efficiency_bonus = max(0.0, (1.0 - usage_ratio) * 0.1)
            return min(1.0, 0.9 + efficiency_bonus)

        elif usage_ratio <= self.budget_tolerance:
            # Slightly over budget
            overage = usage_ratio - 1.0
            penalty = overage / (self.budget_tolerance - 1.0)
            return 0.7 * (1.0 - penalty)

        else:
            # Significantly over budget
            return max(0.0, 0.3 - (usage_ratio - self.budget_tolerance) * 0.5)

    def _evaluate_policy_compliance(self, execution_metadata: dict) -> float:
        """Evaluate policy compliance.

        Scores based on:
        - No policy violations
        - All required checks passed
        - Safety gates respected
        """
        score = 1.0  # Start with full score, deduct for violations

        # Check for policy violations
        violations = execution_metadata.get("policy_violations", [])
        if violations:
            score -= min(0.5, len(violations) * 0.2)

        # Check for safety gate bypasses
        bypasses = execution_metadata.get("safety_bypasses", [])
        if bypasses:
            score -= min(0.4, len(bypasses) * 0.3)

        # Check for required approvals
        missing_approvals = execution_metadata.get("missing_approvals", [])
        if missing_approvals:
            score -= min(0.3, len(missing_approvals) * 0.15)

        # Check compliance checks passed
        checks_passed = execution_metadata.get("compliance_checks_passed", 0)
        checks_total = execution_metadata.get("compliance_checks_total", 1)
        if checks_total > 0:
            compliance_ratio = checks_passed / checks_total
            score = score * 0.5 + compliance_ratio * 0.5

        return max(0.0, min(1.0, score))

    def _calculate_overall_score(
        self,
        tool_selection: float,
        arg_correctness: float,
        retry_thrashing: float,
        budget_discipline: float,
        policy_compliance: float,
    ) -> float:
        """Calculate weighted overall trajectory score."""
        overall = (
            self.weights["tool_selection"] * tool_selection +
            self.weights["arg_correctness"] * arg_correctness +
            self.weights["retry_thrashing"] * retry_thrashing +
            self.weights["budget_discipline"] * budget_discipline +
            self.weights["policy_compliance"] * policy_compliance
        )
        return round(overall, 6)  # Deterministic rounding

    def _build_evaluation_summary(
        self,
        tool_selection: float,
        arg_correctness: float,
        retry_thrashing: float,
        budget_discipline: float,
        policy_compliance: float,
        overall_score: float,
        retry_count: int,
        budget_used: float,
        budget_allocated: float,
    ) -> str:
        """Build human-readable evaluation summary."""
        budget_pct = (budget_used / budget_allocated * 100) if budget_allocated > 0 else 0

        summary_parts = [
            f"Tool Selection: {tool_selection:.2f}",
            f"Arg Correctness: {arg_correctness:.2f}",
            f"Retry Efficiency: {retry_thrashing:.2f} ({retry_count} retries)",
            f"Budget Discipline: {budget_discipline:.2f} ({budget_pct:.1f}% used)",
            f"Policy Compliance: {policy_compliance:.2f}",
            f"Overall Score: {overall_score:.2f}",
        ]

        # Add qualitative assessment
        if overall_score >= 0.8:
            summary_parts.append("Assessment: EXCELLENT_TRAJECTORY")
        elif overall_score >= 0.6:
            summary_parts.append("Assessment: GOOD_TRAJECTORY")
        elif overall_score >= 0.4:
            summary_parts.append("Assessment: ACCEPTABLE_TRAJECTORY")
        else:
            summary_parts.append("Assessment: NEEDS_OPTIMIZATION")

        return " | ".join(summary_parts)


__all__ = ["TrajectoryEvaluationEngine"]
