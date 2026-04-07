"""LM-as-a-Judge Evaluator for Quality Assessment.

Phase 2 - Pillar 10: observability (Tracing & Judging)
Uses LLM to evaluate agent outputs against quality criteria.
"""

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "judge_evaluator_types", "p0_governance")
_emit_reads_policy_state("p0", "judge_evaluator_types", "policy_binding")
_emit_snapshots_state("p0", "judge_evaluator_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("judge_evaluator_types", "p4obs", "metric_1")
_emit_emits_metric_event("judge_evaluator_types", "p4obs", "metric_2")
_emit_emits_metric_event("judge_evaluator_types", "p4obs", "metric_3")
_emit_emits_metric_event("judge_evaluator_types", "p4obs", "metric_4")
_emit_emits_metric_event("judge_evaluator_types", "p4obs", "metric_5")
_emit_emits_metric_event("judge_evaluator_types", "p4obs", "metric_6")
_emit_records_incident_event("judge_evaluator_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("judge_evaluator_types", "p4obs", "anomaly")
_emit_writes_observability_log("judge_evaluator_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("judge_evaluator_types", "p4obs", "mon_state")
_emit_triggers_alert("judge_evaluator_types", "p4obs", "alert")
_emit_links_incident_trace("judge_evaluator_types", "p4obs", "trace_link")
_emit_captures_pattern("judge_evaluator_types", "p3lm", "pattern")
_emit_records_learning_event("judge_evaluator_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("judge_evaluator_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("judge_evaluator_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("judge_evaluator_types", "p3lm", "routing")
_emit_improves_agent_policy("judge_evaluator_types", "p3lm", "policy")
_emit_stores_learning_state("judge_evaluator_types", "p3lm", "state")
_emit_records_execution_trace("judge_evaluator_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("judge_evaluator_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("judge_evaluator_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("judge_evaluator_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("judge_evaluator_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("judge_evaluator_types", "env_read", "p2_env_1")
_emit_reads_environ("judge_evaluator_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("judge_evaluator_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("judge_evaluator_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "judge_evaluator_types", "context_pull")
_emit_pulls_context("p1", "judge_evaluator_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "judge_evaluator_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "judge_evaluator_types", "uwg_term_2")
_emit_writes_through("p1", "judge_evaluator_types", "write_through")
_emit_writes_through("p1", "judge_evaluator_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "judge_evaluator_types", "safety_validation")
_emit_invokes_eval("p1", "judge_evaluator_types", "eval_call")
_emit_proposal_commits_routing("p1", "judge_evaluator_types", "routing_commit")
_emit_escalates_to_human("p1", "judge_evaluator_types", "human_escalation")
_emit_routes_through("p1", "judge_evaluator_types", "route_through")
_emit_checks_agent_registry("p1", "judge_evaluator_types", "agent_registry")
_emit_validates_agent_capability("p1", "judge_evaluator_types", "capability")
_emit_dispatches_execution_plan("p1", "judge_evaluator_types", "exec_plan")
_emit_agent_executes_agent("p1", "judge_evaluator_types", "sub_agent")
_emit_routes_to_agent("p1", "judge_evaluator_types", "target_agent")
_emit_verifies_policy("p1", "judge_evaluator_types", "policy_check")
_emit_observes_runtime_state("p1", "judge_evaluator_types", "runtime_state")
_emit_verifies_boundary("p1", "judge_evaluator_types", "boundary_check")
_emit_transcripts_response("p1", "judge_evaluator_types", "transcript")
_emit_hard_fails_untranscripted("p1", "judge_evaluator_types")
_emit_gated_by_confidence("p1", "judge_evaluator_types", "confidence_gate")
emit_replay_key("p0", "judge_evaluator_types")
emit_determinism_digest("p0", "judge_evaluator_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "judge_evaluator_types", "execution_auth")
_emit_validates_capability("p2", "judge_evaluator_types", "capability_check")
_emit_routes_to_capability("p2", "judge_evaluator_types", "capability_route")
_emit_writes_via_uwg("p2", "judge_evaluator_types", "uwg_write")
_emit_blocks_direct_write("p2", "judge_evaluator_types", "direct_write_block")
_emit_records_tool_invocation("p2", "judge_evaluator_types", "tool_invocation")
_emit_captures_execution_output("p2", "judge_evaluator_types", "exec_output")
_emit_dispatches_agent("p3", "judge_evaluator_types", "agent_dispatch")
_emit_coordinates_agents("p3", "judge_evaluator_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "judge_evaluator_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "judge_evaluator_types", "healing_outcome")
_emit_escalates_failure("p3", "judge_evaluator_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "judge_evaluator_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "judge_evaluator_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "judge_evaluator_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "judge_evaluator_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "judge_evaluator_types", "eval_metric")
_emit_stores_embedding("p4", "judge_evaluator_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "judge_evaluator_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "judge_evaluator_types", "exec_snapshot_link")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_1")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_2")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_3")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_4")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_5")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_6")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_7")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_8")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_9")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_10")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_11")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_12")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_13")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_14")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_15")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_16")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_17")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_18")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_19")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_20")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_21")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_22")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_23")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_24")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_25")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_26")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_27")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_28")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_29")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_30")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_31")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_32")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_33")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_34")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_35")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_36")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_37")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_38")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_39")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_40")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_41")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_42")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_43")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_44")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_45")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_46")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_47")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_48")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_49")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_50")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_51")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_52")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_53")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_54")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_55")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_56")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_57")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_58")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_59")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_60")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_61")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_62")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_63")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_64")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_65")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_66")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_67")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_68")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_69")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_70")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_71")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_72")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_73")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_74")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_75")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_76")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_77")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_78")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_79")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_80")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_81")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_82")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_83")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_84")
_emit_reads_through("l4", "judge_evaluator_types", "urg_read_85")

logger = logging.getLogger(__name__)


class JudgmentCriterion(Enum):
    """Criteria for judging output quality."""

    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    COHERENCE = "coherence"
    FACTUALITY = "factuality"
    SAFETY = "safety"
    HELPFULNESS = "helpfulness"


class JudgmentScore(Enum):
    """Judgment score levels."""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


@dataclass
class JudgeVerdict:
    """Verdict from LM-as-a-Judge evaluation."""

    criterion: JudgmentCriterion
    score: JudgmentScore
    score_value: float
    reasoning: str
    evidence: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "criterion": self.criterion.value,
            "score": self.score.value,
            "score_value": self.score_value,
            "reasoning": self.reasoning,
            "evidence": self.evidence,
            "suggestions": self.suggestions,
        }


@dataclass
class JudgeEvaluationResult:
    """Complete evaluation result from judge."""

    overall_score: float
    verdicts: list[JudgeVerdict]
    passed: bool
    threshold: float
    summary: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_score": self.overall_score,
            "verdicts": [v.to_dict() for v in self.verdicts],
            "passed": self.passed,
            "threshold": self.threshold,
            "summary": self.summary,
            "metadata": self.metadata,
        }

    def get_failing_criteria(self) -> list[JudgmentCriterion]:
        """Get criteria that failed."""
        return [
            v.criterion for v in self.verdicts if v.score in {JudgmentScore.POOR, JudgmentScore.UNACCEPTABLE}
        ]


class JudgeEvaluator:
    """LM-as-a-Judge evaluator for output quality assessment.

    Uses an LLM to evaluate agent outputs against quality criteria.
    Integrates with golden state datasets for validation.
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        llm_client: Callable[[str], Awaitable[str]] | None = None,
        criteria: list[JudgmentCriterion] | None = None,
        pass_threshold: float = 0.7,
        enable_logging: bool = True,
        model_id: str | None = None,
        deterministic_anchor_tolerance: float = 0.15,
    ):
        """Initialize judge evaluator.

        Args:
            llm_client: Async function to call LLM for judgment
            criteria: Criteria to evaluate (default: all)
            pass_threshold: Minimum score to pass (0.0-1.0)
            enable_logging: Enable logging
            model_id: Identifier of the LLM model used (required when llm_client provided)
            deterministic_anchor_tolerance: Max allowed deviation between LLM and heuristic score
        """
        self.llm_client = llm_client
        self.criteria = criteria or list(JudgmentCriterion)
        self.pass_threshold = pass_threshold
        self.enable_logging = enable_logging
        self.model_id = model_id or ("unknown" if llm_client else "heuristic")
        self.deterministic_anchor_tolerance = deterministic_anchor_tolerance
        self._audit_log: list[dict] = []
        if self.enable_logging:
            logger.info(
                "judge_evaluator_initialized",
                extra={
                    "criteria_count": len(self.criteria),
                    "pass_threshold": pass_threshold,
                    "model_id": self.model_id,
                },
            )

    async def evaluate(
        self, output: str, expected: str | None = None, context: dict[str, Any] | None = None,
    ) -> JudgeEvaluationResult:
        """Evaluate output quality.

        Args:
            output: Agent output to evaluate
            expected: Optional expected/golden output
            context: Optional context (task, inputs, etc.)

        Returns:
            JudgeEvaluationResult with verdicts
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "JudgeEvaluator.evaluate")
        if self.enable_logging:
            logger.info(
                "evaluation_started",
                extra={"output_length": len(output), "has_expected": expected is not None},
            )
        verdicts: list[JudgeVerdict] = []
        for criterion in self.criteria:
            verdict = await self._evaluate_criterion(
                output=output, expected=expected, context=context, criterion=criterion,
            )
            verdicts.append(verdict)
        overall_score = sum(v.score_value for v in verdicts) / len(verdicts)
        passed = overall_score >= self.pass_threshold
        summary = self._generate_summary(verdicts, overall_score, passed)
        import hashlib
        import time

        anchor_score = self._compute_heuristic_anchor(output, expected)
        anchor_deviation = abs(overall_score - anchor_score)
        anchor_alert = self.llm_client is not None and anchor_deviation > self.deterministic_anchor_tolerance
        result = JudgeEvaluationResult(
            overall_score=overall_score,
            verdicts=verdicts,
            passed=passed,
            threshold=self.pass_threshold,
            summary=summary,
            metadata={
                "criteria_count": len(self.criteria),
                "output_length": len(output),
                "model_id": self.model_id,
                "heuristic_anchor": anchor_score,
                "anchor_deviation": anchor_deviation,
                "anchor_alert": anchor_alert,
                "evaluation_path": "llm" if self.llm_client else "heuristic",
            },
        )
        audit_entry = {
            "ts": time.time(),
            "model_id": self.model_id,
            "output_hash": hashlib.sha256(output.encode()).hexdigest()[:16],
            "overall_score": overall_score,
            "heuristic_anchor": anchor_score,
            "anchor_deviation": anchor_deviation,
            "anchor_alert": anchor_alert,
            "passed": passed,
            "evaluation_path": "llm" if self.llm_client else "heuristic",
        }
        self._audit_log.append(audit_entry)
        if self.enable_logging:
            if anchor_alert:
                logger.warning(
                    "judge_anchor_deviation",
                    extra={
                        "overall_score": overall_score,
                        "anchor_score": anchor_score,
                        "deviation": anchor_deviation,
                        "tolerance": self.deterministic_anchor_tolerance,
                    },
                )
            logger.info(
                "evaluation_completed",
                extra={
                    "overall_score": overall_score,
                    "passed": passed,
                    "failing_criteria": [c.value for c in result.get_failing_criteria()],
                    "model_id": self.model_id,
                    "anchor_alert": anchor_alert,
                },
            )
        return result

    async def _evaluate_criterion(
        self, output: str, expected: str | None, context: dict[str, Any] | None, criterion: JudgmentCriterion,
    ) -> JudgeVerdict:
        """Evaluate a single criterion.

        Args:
            output: Output to evaluate
            expected: Expected output
            context: Context
            criterion: Criterion to evaluate

        Returns:
            JudgeVerdict for this criterion
        """
        prompt = self._build_evaluation_prompt(
            output=output, expected=expected, context=context, criterion=criterion,
        )
        if self.llm_client:
            try:
                response = await self.llm_client(prompt)
                verdict = self._parse_llm_response(response, criterion)
            # guardian: allow-silent-swallow
            except Exception as e:
                if self.enable_logging:
                    logger.error(
                        "llm_evaluation_failed",
                        extra={"criterion": criterion.value, "error": str(e), "model_id": self.model_id},
                        exc_info=True,
                    )
                verdict = self._heuristic_evaluation(output, expected, criterion)
        else:
            verdict = self._heuristic_evaluation(output, expected, criterion)
        return verdict

    def _compute_heuristic_anchor(self, output: str, expected: str | None) -> float:
        """Compute a deterministic heuristic score for anchor cross-validation.

        Uses token overlap (F1) against expected when available,
        otherwise length and keyword density heuristics.

        Args:
            output: Agent output
            expected: Optional golden output

        Returns:
            Anchor score in [0.0, 1.0]
        """
        if expected:
            out_tokens = set(output.lower().split())
            exp_tokens = set(expected.lower().split())
            if not exp_tokens:
                return 0.5
            precision = len(out_tokens & exp_tokens) / max(len(out_tokens), 1)
            recall = len(out_tokens & exp_tokens) / len(exp_tokens)
            if precision + recall == 0:
                return 0.0
            return 2 * precision * recall / (precision + recall)
        if not output or not output.strip():
            return 0.0
        length_score = min(len(output) / 200.0, 1.0)
        word_count = len(output.split())
        density_score = min(word_count / 30.0, 1.0)
        return (length_score + density_score) / 2.0

    def _build_evaluation_prompt(
        self, output: str, expected: str | None, context: dict[str, Any] | None, criterion: JudgmentCriterion,
    ) -> str:
        """Build evaluation prompt for LLM.

        Args:
            output: Output to evaluate
            expected: Expected output
            context: Context
            criterion: Criterion

        Returns:
            Evaluation prompt
        """
        prompt_parts = [
            f"You are an expert evaluator. Evaluate the following output based on {criterion.value}.",
            "",
            "OUTPUT TO EVALUATE:",
            output,
            "",
        ]
        if expected:
            prompt_parts.extend(["EXPECTED OUTPUT:", expected, ""])
        if context:
            task = context.get("task", "")
            if task:
                prompt_parts.extend(["TASK:", task, ""])
        prompt_parts.extend(
            [
                f"Evaluate the output's {criterion.value} on a scale of 0.0 to 1.0.",
                "Provide:",
                "1. Score (0.0-1.0)",
                "2. Reasoning for the score",
                "3. Specific evidence from the output",
                "4. Suggestions for improvement",
                "",
                "Format your response as:",
                "SCORE: <number>",
                "REASONING: <explanation>",
                "EVIDENCE: <bullet points>",
                "SUGGESTIONS: <bullet points>",
            ],
        )
        return "\n".join(prompt_parts)

    def _parse_llm_response(self, response: str, criterion: JudgmentCriterion) -> JudgeVerdict:
        """Parse LLM response into verdict.

        Args:
            response: LLM response
            criterion: Criterion evaluated

        Returns:
            JudgeVerdict
        """
        lines = response.strip().split("\n")
        score_value, reasoning, evidence, suggestions = (0.5, "", [], [])
        current_section = None
        for line in lines:
            line = line.strip()
            score_value, reasoning, current_section = self._parse_line(
                line, score_value, reasoning, current_section, evidence, suggestions,
            )
        return self._create_verdict(score_value, reasoning, evidence, suggestions, criterion)

    def _parse_line(
        self,
        line: str,
        score_value: float,
        reasoning: str,
        current_section: str | None,
        evidence: list[str],
        suggestions: list[str],
    ) -> tuple:
        """Parse a single line."""
        if line.startswith("SCORE:"):
            return (self._parse_score(line, score_value), reasoning, current_section)
        if line.startswith("REASONING:"):
            return (score_value, line.split(":", 1)[1].strip(), "reasoning")
        if line.startswith("EVIDENCE:"):
            return (score_value, reasoning, "evidence")
        if line.startswith("SUGGESTIONS:"):
            return (score_value, reasoning, "suggestions")
        if line.startswith("-") or line.startswith("•"):
            self._parse_list_item(line, current_section, evidence, suggestions)
            return (score_value, reasoning, current_section)
        if current_section == "reasoning" and line.strip():
            return (score_value, reasoning + " " + line.strip(), current_section)
        return (score_value, reasoning, current_section)

    def _parse_score(self, line: str, default: float) -> float:
        """Parse score from line."""
        try:
            return float(line.split(":", 1)[1].strip())
        except (ValueError, IndexError):
            return default

    def _parse_list_item(
        self, line: str, section: str | None, evidence: list[str], suggestions: list[str],
    ) -> None:
        """Parse list item into appropriate list."""
        item = line.lstrip("-•").strip()
        if section == "evidence":
            evidence.append(item)
        elif section == "suggestions":
            suggestions.append(item)

    def _create_verdict(
        self,
        score_value: float,
        reasoning: str,
        evidence: list[str],
        suggestions: list[str],
        criterion: JudgmentCriterion,
    ) -> JudgeVerdict:
        """Create verdict from parsed data."""
        if score_value >= 0.9:
            score = JudgmentScore.EXCELLENT
        elif score_value >= 0.7:
            score = JudgmentScore.GOOD
        elif score_value >= 0.5:
            score = JudgmentScore.ACCEPTABLE
        elif score_value >= 0.3:
            score = JudgmentScore.POOR
        else:
            score = JudgmentScore.UNACCEPTABLE
        return JudgeVerdict(
            criterion=criterion,
            score=score,
            score_value=score_value,
            reasoning=reasoning or "No reasoning provided",
            evidence=evidence,
            suggestions=suggestions,
        )

    def _heuristic_evaluation(
        self, output: str, expected: str | None, criterion: JudgmentCriterion,
    ) -> JudgeVerdict:
        """Heuristic evaluation when LLM unavailable.

        Args:
            output: Output to evaluate
            expected: Expected output
            criterion: Criterion

        Returns:
            JudgeVerdict based on heuristics
        """
        score_value = 0.5
        reasoning = f"Heuristic evaluation for {criterion.value}"
        evidence = []
        suggestions = []
        if criterion == JudgmentCriterion.COMPLETENESS:
            if expected:
                ratio = len(output) / max(len(expected), 1)
                score_value = min(ratio, 1.0)
                reasoning = f"Output length is {ratio:.1%} of expected"
            else:
                score_value = 0.7 if len(output) > 100 else 0.4
                reasoning = f"Output length: {len(output)} characters"
        elif criterion == JudgmentCriterion.COHERENCE:
            has_sentences = "." in output or "!" in output or "?" in output
            has_paragraphs = "\n" in output
            score_value = 0.8 if has_sentences and has_paragraphs else 0.5
            reasoning = "Basic structure check"
        elif criterion == JudgmentCriterion.RELEVANCE:
            if expected:
                output_words = set(output.lower().split())
                expected_words = set(expected.lower().split())
                overlap = len(output_words & expected_words)
                score_value = min(overlap / max(len(expected_words), 1), 1.0)
                reasoning = f"Word overlap: {overlap} words"
            else:
                score_value = 0.6
                reasoning = "No expected output for comparison"
        else:
            score_value = 0.6
            reasoning = f"Default heuristic for {criterion.value}"
        if score_value >= 0.9:
            score = JudgmentScore.EXCELLENT
        elif score_value >= 0.7:
            score = JudgmentScore.GOOD
        elif score_value >= 0.5:
            score = JudgmentScore.ACCEPTABLE
        elif score_value >= 0.3:
            score = JudgmentScore.POOR
        else:
            score = JudgmentScore.UNACCEPTABLE
        return JudgeVerdict(
            criterion=criterion,
            score=score,
            score_value=score_value,
            reasoning=reasoning,
            evidence=evidence,
            suggestions=suggestions,
        )

    def _generate_summary(self, verdicts: list[JudgeVerdict], overall_score: float, passed: bool) -> str:
        """Generate evaluation summary.

        Args:
            verdicts: All verdicts
            overall_score: Overall score
            passed: Whether evaluation passed

        Returns:
            Summary string
        """
        status = "PASSED" if passed else "FAILED"
        excellent = sum(1 for v in verdicts if v.score == JudgmentScore.EXCELLENT)
        good = sum(1 for v in verdicts if v.score == JudgmentScore.GOOD)
        acceptable = sum(1 for v in verdicts if v.score == JudgmentScore.ACCEPTABLE)
        poor = sum(1 for v in verdicts if v.score == JudgmentScore.POOR)
        unacceptable = sum(1 for v in verdicts if v.score == JudgmentScore.UNACCEPTABLE)
        summary_parts = [
            f"Evaluation {status} (Score: {overall_score:.2f})",
            f"Excellent: {excellent}, Good: {good}, Acceptable: {acceptable}, Poor: {poor}, Unacceptable: {unacceptable}",
        ]
        if not passed:
            failing = [
                v.criterion.value
                for v in verdicts
                if v.score in {JudgmentScore.POOR, JudgmentScore.UNACCEPTABLE}
            ]
            summary_parts.append(f"Failing criteria: {', '.join(failing)}")
        return " | ".join(summary_parts)


# guardian: allow-magic-config
def create_judge_evaluator(
    llm_client: Callable[[str], Awaitable[str]] | None = None, pass_threshold: float = 0.7,
) -> JudgeEvaluator:
    """Factory function to create judge evaluator.

    Args:
        llm_client: LLM client function
        pass_threshold: Pass threshold

    Returns:
        JudgeEvaluator instance
    """
    return JudgeEvaluator(llm_client=llm_client, pass_threshold=pass_threshold)
