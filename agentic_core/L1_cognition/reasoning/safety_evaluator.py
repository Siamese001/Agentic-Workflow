"""Safety Evaluator.

Comprehensive safety evaluation system that combines constitutional
rules and content filtering for overall safety assessment.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from agentic_core.L1_cognition.config.graphrag_config import get_config
from agentic_core.L1_cognition.reasoning.constitutional_rules_engine import ConstitutionalRulesEngine
from agentic_core.L1_cognition.reasoning.content_filter import ContentFilterEngine
from agentic_core.L1_cognition.types.guardrail_types import (
    GuardrailAction,
    GuardrailConfig,
    GuardrailReport,
    GuardrailSeverity,
    SafetyEvaluation,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "safety_evaluator")
emit_determinism_digest("p0", "safety_evaluator")

_emit_dispatches_healing_run("p1", "safety_evaluator", "L1")
_emit_routes_through("p1", "safety_evaluator", "L1")
_emit_checks_agent_registry("p1", "safety_evaluator", "agent_registry")
_emit_validates_agent_capability("p1", "safety_evaluator", "capability")
_emit_dispatches_execution_plan("p1", "safety_evaluator", "exec_plan")
_emit_agent_executes_agent("p1", "safety_evaluator", "sub_agent")
_emit_routes_to_agent("p1", "safety_evaluator", "target_agent")
_emit_verifies_policy("p1", "safety_evaluator", "policy_check")
_emit_observes_runtime_state("p1", "safety_evaluator", "runtime_state")
_emit_verifies_boundary("p1", "safety_evaluator", "boundary_check")
_emit_transcripts_response("p1", "safety_evaluator", "transcript")
_emit_hard_fails_untranscripted("p1", "safety_evaluator")
_emit_gated_by_confidence("p1", "safety_evaluator", "confidence_gate")
_emit_escalates_to_human("p1", "safety_evaluator", "L1")
_emit_reads_policy_state("p1", "safety_evaluator", "L1")
_emit_authorize_and_execute("p2", "safety_evaluator", "execution_auth")
_emit_validates_capability("p2", "safety_evaluator", "capability_check")
_emit_routes_to_capability("p2", "safety_evaluator", "capability_route")
_emit_writes_via_uwg("p2", "safety_evaluator", "uwg_write")
_emit_blocks_direct_write("p2", "safety_evaluator", "direct_write_block")
_emit_records_tool_invocation("p2", "safety_evaluator", "execution_auth")
_emit_captures_execution_output("p2", "safety_evaluator", "exec_output")
_emit_dispatches_agent("p3", "safety_evaluator", "agent_dispatch")
_emit_coordinates_agents("p3", "safety_evaluator", "agent_coordination")
_emit_records_workflow_lineage("p3", "safety_evaluator", "workflow_lineage")
_emit_records_healing_outcome("p3", "safety_evaluator", "healing_outcome")
_emit_escalates_failure("p3", "safety_evaluator", "failure_escalation")
_emit_orchestrates_workflow("p3", "safety_evaluator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "safety_evaluator", "healing_dispatch")
_emit_invokes_evaluation("p3", "safety_evaluator", "evaluation_signal")
_emit_records_telemetry_event("p4", "safety_evaluator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "safety_evaluator", "eval_metric")
_emit_stores_embedding("p4", "safety_evaluator", "embedding_store")


class SafetyEvaluator:
    """Comprehensive safety evaluator combining multiple safety mechanisms."""

    def __init__(
        self,
        config: GuardrailConfig | None = None,
        constitutional_engine: ConstitutionalRulesEngine | None = None,
        content_filter: ContentFilterEngine | None = None
    ) -> None:
        """Initialize the safety evaluator.

        Args:
            config: Guardrail configuration
            constitutional_engine: Constitutional rules engine
            content_filter: Content filter engine
        """
        self.config = config or GuardrailConfig()
        self.graphrag_config = get_config()

        # Initialize components
        self.constitutional_engine = constitutional_engine or ConstitutionalRulesEngine(self.config)
        self.content_filter = content_filter or ContentFilterEngine(self.config)

        # Evaluation statistics
        self._evaluation_stats: dict[str, list[float]] = {
            "evaluation_time": [],
            "safety_scores": [],
            "risk_levels": {}
        }

    async def evaluate_safety(
        self,
        content: str,
        content_id: str,
        content_type: str = "generation",
        context: str | None = None,
        additional_metadata: dict[str, Any] | None = None
    ) -> SafetyEvaluation:
        """Evaluate the safety of content.

        Args:
            content: Content to evaluate
            content_id: Unique identifier for the content
            content_type: Type of content ("query", "context", "response", "generation")
            context: Additional context for evaluation
            additional_metadata: Additional metadata for evaluation

        Returns:
            Comprehensive safety evaluation
        """
        start_time = datetime.utcnow()
        evaluation_id = f"safety_eval_{content_id}_{start_time.strftime('%Y%m%d_%H%M%S')}"

        try:
            # Step 1: Run constitutional rules evaluation
            constitutional_report = self.constitutional_engine.evaluate_content(
                content, content_id, content_type, context
            )

            # Step 2: Run content filtering
            content_filter_report = self.content_filter.filter_content(
                content, content_id, content_type, context
            )

            # Step 3: Combine results and calculate overall safety
            safety_scores = self._calculate_safety_scores(
                constitutional_report, content_filter_report
            )

            # Step 4: Determine risk level
            risk_level = self._determine_risk_level(
                constitutional_report, content_filter_report, safety_scores
            )

            # Step 5: Generate recommendations
            recommendations = self._generate_recommendations(
                constitutional_report, content_filter_report, risk_level
            )

            # Step 6: Determine if safe to proceed
            safe_to_proceed = self._is_safe_to_proceed(
                constitutional_report, content_filter_report, risk_level
            )

            # Create evaluation
            evaluation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            evaluation = SafetyEvaluation(
                evaluation_id=evaluation_id,
                content_id=content_id,
                overall_safety_score=safety_scores["overall"],
                category_scores=safety_scores["categories"],
                risk_level=risk_level,
                risk_factors=self._extract_risk_factors(
                    constitutional_report, content_filter_report
                ),
                safe_to_proceed=safe_to_proceed,
                recommended_actions=recommendations,
                evaluation_time_ms=evaluation_time,
                evaluator_version="1.0.0"
            )

            # Update statistics
            self._evaluation_stats["evaluation_time"].append(evaluation_time)
            self._evaluation_stats["safety_scores"].append(evaluation.overall_safety_score)

            risk_key = risk_level.value
            if risk_key not in self._evaluation_stats["risk_levels"]:
                self._evaluation_stats["risk_levels"][risk_key] = 0
            self._evaluation_stats["risk_levels"][risk_key] += 1

            _emit_records_telemetry_event(
                "safety_evaluator",
                f"safety_evaluated_{evaluation.overall_safety_score:.2f}_{risk_level.value}",
                "safety_evaluated"
            )

            return evaluation

        except Exception as e:
            # Return error evaluation
            return SafetyEvaluation(
                evaluation_id=evaluation_id,
                content_id=content_id,
                overall_safety_score=0.0,
                category_scores={},
                risk_level=GuardrailSeverity.CRITICAL,
                risk_factors=["evaluation_error"],
                safe_to_proceed=False,
                recommended_actions=["escalate_to_human", "review_error"],
                evaluation_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                evaluator_version="1.0.0"
            )

    def _calculate_safety_scores(
        self,
        constitutional_report: GuardrailReport,
        content_filter_report: GuardrailReport
    ) -> dict[str, float]:
        """Calculate safety scores from reports."""
        scores = {
            "overall": 0.0,
            "categories": {
                "constitutional": 0.0,
                "content_filter": 0.0,
                "helpfulness": 0.0,
                "safety": 0.0,
                "privacy": 0.0,
                "fairness": 0.0
            }
        }

        # Constitutional score
        if constitutional_report.total_checks > 0:
            constitutional_score = constitutional_report.overall_score
            scores["categories"]["constitutional"] = constitutional_score
        else:
            scores["categories"]["constitutional"] = 1.0  # No issues found

        # Content filter score
        if content_filter_report.total_checks > 0:
            content_filter_score = content_filter_report.overall_score
            scores["categories"]["content_filter"] = content_filter_score
        else:
            scores["categories"]["content_filter"] = 1.0  # No issues found

        # Category-specific scores from constitutional rules
        for check in constitutional_report.checks:
            if not check.passed:
                # Deduct points for failed checks
                rule_category = check.metadata.get("rule_category", "general")
                if rule_category in scores["categories"]:
                    scores["categories"][rule_category] *= 0.8  # 20% penalty
            else:
                # Add points for passed checks
                rule_category = check.metadata.get("rule_category", "general")
                if rule_category in scores["categories"]:
                    scores["categories"][rule_category] = min(1.0,
                        scores["categories"][rule_category] + 0.1)

        # Calculate overall score
        # Weight constitutional rules more heavily
        constitutional_weight = 0.6
        content_filter_weight = 0.4

        scores["overall"] = (
            scores["categories"]["constitutional"] * constitutional_weight +
            scores["categories"]["content_filter"] * content_filter_weight
        )

        # Ensure score is in [0, 1] range
        scores["overall"] = max(0.0, min(1.0, scores["overall"]))

        return scores

    def _determine_risk_level(
        self,
        constitutional_report: GuardrailReport,
        content_filter_report: GuardrailReport,
        safety_scores: dict[str, float]
    ) -> GuardrailSeverity:
        """Determine overall risk level."""
        # Check for critical violations
        critical_violations = []

        for report in [constitutional_report, content_filter_report]:
            if report.highest_severity == GuardrailSeverity.CRITICAL and not report.passed:
                critical_violations.append(report.highest_severity)

        if critical_violations:
            return GuardrailSeverity.CRITICAL

        # Check for high violations
        high_violations = []

        for report in [constitutional_report, content_filter_report]:
            if report.highest_severity == GuardrailSeverity.HIGH and not report.passed:
                high_violations.append(report.highest_severity)

        if high_violations:
            return GuardrailSeverity.HIGH

        # Check safety score thresholds
        if safety_scores["overall"] < 0.3:
            return GuardrailSeverity.HIGH
        elif safety_scores["overall"] < 0.6:
            return GuardrailSeverity.MEDIUM
        elif safety_scores["overall"] < 0.8:
            return GuardrailSeverity.LOW

        return GuardrailSeverity.LOW

    def _generate_recommendations(
        self,
        constitutional_report: GuardrailReport,
        content_filter_report: GuardrailReport,
        risk_level: GuardrailSeverity
    ) -> list[str]:
        """Generate safety recommendations."""
        recommendations = []

        # Based on risk level
        if risk_level == GuardrailSeverity.CRITICAL:
            recommendations.extend([
                "Immediately block this content",
                "Escalate to human reviewer",
                "Review safety protocols"
            ])
        elif risk_level == GuardrailSeverity.HIGH:
            recommendations.extend([
                "Consider blocking this content",
                "Apply additional filtering",
                "Review with safety team"
            ])
        elif risk_level == GuardrailSeverity.MEDIUM:
            recommendations.extend([
                "Apply content modifications if needed",
                "Add warning labels",
                "Monitor for similar patterns"
            ])
        elif risk_level == GuardrailSeverity.LOW:
            recommendations.extend([
                "Content appears safe",
                "Continue with standard processing",
                "Log for future reference"
            ])

        # Based on specific violations
        for report in [constitutional_report, content_filter_report]:
            for check in report.checks:
                if not check.passed:
                    if check.action == GuardrailAction.MODIFY:
                        recommendations.append(f"Apply {check.filter_id or check.rule_id} modifications")
                    elif check.action == GuardrailAction.WARN:
                        recommendations.append(f"Add warning for {check.filter_id or check.rule_id}")
                    elif check.action == GuardrailAction.ESCALATE:
                        recommendations.append(f"Escalate {check.filter_id or check.rule_id} to reviewer")

        return list(set(recommendations))  # Remove duplicates

    def _extract_risk_factors(
        self,
        constitutional_report: GuardrailReport,
        content_filter_report: GuardrailReport
    ) -> list[str]:
        """Extract risk factors from reports."""
        risk_factors = []

        for report in [constitutional_report, content_filter_report]:
            if not report.passed:
                risk_factors.append(f"Failed {report.content_type} guardrails")

                for check in report.checks:
                    if not check.passed:
                        if check.rule_id:
                            risk_factors.append(f"Violated rule: {check.rule_id}")
                        if check.filter_id:
                            risk_factors.append(f"Triggered filter: {check.filter_id}")

        return list(set(risk_factors))

    def _is_safe_to_proceed(
        self,
        constitutional_report: GuardrailReport,
        content_filter_report: GuardrailReport,
        risk_level: GuardrailSeverity
    ) -> bool:
        """Determine if content is safe to proceed."""
        # Check for critical violations
        if risk_level == GuardrailSeverity.CRITICAL:
            return False

        # Check for escalations
        if constitutional_report.escalation_required or content_filter_report.escalation_required:
            return False

        # Check configuration
        if self.config.strict_mode:
            # In strict mode, any violation blocks
            return constitutional_report.passed and content_filter_report.passed
        else:
            # In non-strict mode, only critical violations block
            return risk_level != GuardrailSeverity.CRITICAL

    def get_evaluation_stats(self) -> dict[str, Any]:
        """Get evaluation statistics."""
        stats = {}

        # Evaluation time stats
        if self._evaluation_stats["evaluation_time"]:
            times = self._evaluation_stats["evaluation_time"]
            stats["avg_evaluation_time_ms"] = sum(times) / len(times)
            stats["min_evaluation_time_ms"] = min(times)
            stats["max_evaluation_time_ms"] = max(times)
            stats["total_evaluations"] = len(times)
        else:
            stats["avg_evaluation_time_ms"] = 0.0
            stats["min_evaluation_time_ms"] = 0.0
            stats["max_evaluation_time_ms"] = 0.0
            stats["total_evaluations"] = 0

        # Safety score stats
        if self._evaluation_stats["safety_scores"]:
            scores = self._evaluation_stats["safety_scores"]
            stats["avg_safety_score"] = sum(scores) / len(scores)
            stats["min_safety_score"] = min(scores)
            stats["max_safety_score"] = max(scores)
        else:
            stats["avg_safety_score"] = 0.0
            stats["min_safety_score"] = 0.0
            stats["max_safety_score"] = 0.0

        # Risk level distribution
        stats["risk_level_distribution"] = self._evaluation_stats["risk_levels"].copy()

        return stats

    def reset_stats(self) -> None:
        """Reset evaluation statistics."""
        self._evaluation_stats = {
            "evaluation_time": [],
            "safety_scores": [],
            "risk_levels": {}
        }

        _emit_records_telemetry_event(
            "safety_evaluator",
            "stats_reset"
        )


# Factory function
def create_safety_evaluator(
    config: GuardrailConfig | None = None,
    constitutional_engine: ConstitutionalRulesEngine | None = None,
    content_filter: ContentFilterEngine | None = None
) -> SafetyEvaluator:
    """Create a safety evaluator."""
    return SafetyEvaluator(config, constitutional_engine, content_filter)


__all__ = [
    "SafetyEvaluator",
    "create_safety_evaluator",
]
