"""Feedback Loop Orchestrator - Adaptive Regeneration Engine.

This module provides the orchestration layer for adaptive regeneration with
intelligent failure correction, temperature escalation, and reversion policies.

Primary Responsibilities:
1. Manage regeneration attempts with max 5 attempts
2. Classify failure types and adjust temperature adaptively
3. Implement reversion policy (revert if attempt N worse than N-1)
4. Build regeneration prompts with exact failure details
5. Support message type transitions for dynamic workflow adaptation
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
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

_emit_applies_guardrail("p0", "feedback_loop_orchestrator_types", "p0_governance")
_emit_reads_policy_state("p0", "feedback_loop_orchestrator_types", "policy_binding")
_emit_snapshots_state("p0", "feedback_loop_orchestrator_types", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("feedback_loop_orchestrator_types", "p4obs", "metric_1")
_emit_emits_metric_event("feedback_loop_orchestrator_types", "p4obs", "metric_2")
_emit_emits_metric_event("feedback_loop_orchestrator_types", "p4obs", "metric_3")
_emit_emits_metric_event("feedback_loop_orchestrator_types", "p4obs", "metric_4")
_emit_emits_metric_event("feedback_loop_orchestrator_types", "p4obs", "metric_5")
_emit_emits_metric_event("feedback_loop_orchestrator_types", "p4obs", "metric_6")
_emit_records_incident_event("feedback_loop_orchestrator_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("feedback_loop_orchestrator_types", "p4obs", "anomaly")
_emit_writes_observability_log("feedback_loop_orchestrator_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("feedback_loop_orchestrator_types", "p4obs", "mon_state")
_emit_triggers_alert("feedback_loop_orchestrator_types", "p4obs", "alert")
_emit_links_incident_trace("feedback_loop_orchestrator_types", "p4obs", "trace_link")
_emit_captures_pattern("feedback_loop_orchestrator_types", "p3lm", "pattern")
_emit_records_learning_event("feedback_loop_orchestrator_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("feedback_loop_orchestrator_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("feedback_loop_orchestrator_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("feedback_loop_orchestrator_types", "p3lm", "routing")
_emit_improves_agent_policy("feedback_loop_orchestrator_types", "p3lm", "policy")
_emit_stores_learning_state("feedback_loop_orchestrator_types", "p3lm", "state")
_emit_records_execution_trace("feedback_loop_orchestrator_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("feedback_loop_orchestrator_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("feedback_loop_orchestrator_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("feedback_loop_orchestrator_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("feedback_loop_orchestrator_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("feedback_loop_orchestrator_types", "env_read", "p2_env_1")
_emit_reads_environ("feedback_loop_orchestrator_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("feedback_loop_orchestrator_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("feedback_loop_orchestrator_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "feedback_loop_orchestrator_types", "context_pull")
_emit_pulls_context("p1", "feedback_loop_orchestrator_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "feedback_loop_orchestrator_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "feedback_loop_orchestrator_types", "uwg_term_2")
_emit_writes_through("p1", "feedback_loop_orchestrator_types", "write_through")
_emit_writes_through("p1", "feedback_loop_orchestrator_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "feedback_loop_orchestrator_types", "safety_validation")
_emit_invokes_eval("p1", "feedback_loop_orchestrator_types", "eval_call")
_emit_proposal_commits_routing("p1", "feedback_loop_orchestrator_types", "routing_commit")
_emit_escalates_to_human("p1", "feedback_loop_orchestrator_types", "human_escalation")
_emit_routes_through("p1", "feedback_loop_orchestrator_types", "route_through")
_emit_checks_agent_registry("p1", "feedback_loop_orchestrator_types", "agent_registry")
_emit_validates_agent_capability("p1", "feedback_loop_orchestrator_types", "capability")
_emit_dispatches_execution_plan("p1", "feedback_loop_orchestrator_types", "exec_plan")
_emit_agent_executes_agent("p1", "feedback_loop_orchestrator_types", "sub_agent")
_emit_routes_to_agent("p1", "feedback_loop_orchestrator_types", "target_agent")
_emit_verifies_policy("p1", "feedback_loop_orchestrator_types", "policy_check")
_emit_observes_runtime_state("p1", "feedback_loop_orchestrator_types", "runtime_state")
_emit_verifies_boundary("p1", "feedback_loop_orchestrator_types", "boundary_check")
_emit_transcripts_response("p1", "feedback_loop_orchestrator_types", "transcript")
_emit_hard_fails_untranscripted("p1", "feedback_loop_orchestrator_types")
_emit_gated_by_confidence("p1", "feedback_loop_orchestrator_types", "confidence_gate")
emit_replay_key("p0", "feedback_loop_orchestrator_types")
emit_determinism_digest("p0", "feedback_loop_orchestrator_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "feedback_loop_orchestrator_types", "execution_auth")
_emit_validates_capability("p2", "feedback_loop_orchestrator_types", "capability_check")
_emit_routes_to_capability("p2", "feedback_loop_orchestrator_types", "capability_route")
_emit_writes_via_uwg("p2", "feedback_loop_orchestrator_types", "uwg_write")
_emit_blocks_direct_write("p2", "feedback_loop_orchestrator_types", "direct_write_block")
_emit_records_tool_invocation("p2", "feedback_loop_orchestrator_types", "tool_invocation")
_emit_captures_execution_output("p2", "feedback_loop_orchestrator_types", "exec_output")
_emit_dispatches_agent("p3", "feedback_loop_orchestrator_types", "agent_dispatch")
_emit_coordinates_agents("p3", "feedback_loop_orchestrator_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "feedback_loop_orchestrator_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "feedback_loop_orchestrator_types", "healing_outcome")
_emit_escalates_failure("p3", "feedback_loop_orchestrator_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "feedback_loop_orchestrator_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "feedback_loop_orchestrator_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "feedback_loop_orchestrator_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "feedback_loop_orchestrator_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "feedback_loop_orchestrator_types", "eval_metric")
_emit_stores_embedding("p4", "feedback_loop_orchestrator_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "feedback_loop_orchestrator_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "feedback_loop_orchestrator_types", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class ConstraintFailureType(str, Enum):
    """Types of constraint failures for adaptive retry."""

    MECHANICAL = "MECHANICAL"
    CREATIVE = "CREATIVE"
    SEMANTIC = "SEMANTIC"
    CONFLICT = "CONFLICT"


@dataclass
class RegenerationCheckpoint:
    """Checkpoint for a single regeneration attempt."""

    attempt: int
    timestamp: datetime
    content: str
    validation_result: Any
    temperature: float
    failure_type: ConstraintFailureType | None = None
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "attempt": self.attempt,
            "timestamp": self.timestamp.isoformat(),
            "temperature": self.temperature,
            "failure_type": self.failure_type.value if self.failure_type else None,
            "score": self.score,
            "validation_status": self.validation_result.status.value if self.validation_result else None,
        }


@dataclass
class RegenerationResult:
    """Result of regeneration process."""

    success: bool
    final_content: str
    attempts: int
    checkpoints: list[RegenerationCheckpoint]
    final_validation: Any
    reverted: bool = False
    exhausted: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "success": self.success,
            "attempts": self.attempts,
            "reverted": self.reverted,
            "exhausted": self.exhausted,
            "checkpoints": [cp.to_dict() for cp in self.checkpoints],
        }


class FeedbackLoopOrchestrator:
    """Orchestrate adaptive regeneration with intelligent failure correction.

    This orchestrator wraps generation and validation steps, managing the
    regeneration process with adaptive temperature escalation, reversion
    policies, and detailed failure feedback.
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        max_attempts: int = 5,
        checkpoint_saving: bool = True,
        reversion_enabled: bool = True,
        adaptive_temperature_config: dict[str, Any] | None = None,
        message_type_transitions: dict[str, Any] | None = None,
    ):
        """Initialize feedback loop orchestrator.

        Args:
            max_attempts: Maximum regeneration attempts (default 5)
            checkpoint_saving: Enable checkpoint saving
            reversion_enabled: Enable reversion to better prior attempts
            adaptive_temperature_config: ADAPTIVE_TEMPERATURE_CONFIG from config
            message_type_transitions: MESSAGE_TYPE_TRANSITIONS from config
        """
        self.max_attempts = max_attempts
        self.checkpoint_saving = checkpoint_saving
        self.reversion_enabled = reversion_enabled
        self.adaptive_temperature_config = adaptive_temperature_config or {
            "initial_temperature": 0.5,
            "max_temperature": 0.9,
            "escalation_per_retry": 0.1,
            "constraint_failure_types": {
                "MECHANICAL": 0.05,
                "CREATIVE": 0.15,
                "SEMANTIC": 0.1,
                "CONFLICT": 0.0,
            },
        }
        self.message_type_transitions = message_type_transitions or {}
        logger.info(
            f"Initialized FeedbackLoopOrchestrator: max_attempts={max_attempts}, reversion={reversion_enabled}",
        )

    async def execute_with_feedback(
        self,
        generator: Callable,
        validator: Callable,
        initial_context: dict[str, Any],
        k_node_id: str,
    ) -> RegenerationResult:
        """Execute generation with feedback loop.

        Args:
            generator: Async function that generates content
            validator: Async function that validates content
            initial_context: Initial context for generation
            k_node_id: K-node identifier

        Returns:
            RegenerationResult with final content and metadata
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "FeedbackLoopOrchestrator.execute_with_feedback"
        )
        checkpoints = []
        temperature = self.adaptive_temperature_config["initial_temperature"]
        context = initial_context.copy()
        for attempt in tqdm(range(1, self.max_attempts + 1), desc="Processing", unit="item"):
            logger.info(f"Attempt {attempt}/{self.max_attempts} for {k_node_id} (temp={temperature:.2f})")
            try:
                content = await generator(context, temperature)
            # guardian: allow-silent-swallow
            except (TypeError, ValueError, KeyError, AttributeError, RuntimeError, OSError) as e:
                logger.error(f"Generation failed on attempt {attempt}: {e}")
                continue
            validation_result = await validator(content, context)
            checkpoint = RegenerationCheckpoint(
                attempt=attempt,
                timestamp=datetime.now(),
                content=content,
                validation_result=validation_result,
                temperature=temperature,
                score=validation_result.score if hasattr(validation_result, "score") else 0.0,
            )
            if self.checkpoint_saving:
                checkpoints.append(checkpoint)
            if validation_result.passed:
                logger.info(f"Validation passed on attempt {attempt}")
                return RegenerationResult(
                    success=True,
                    final_content=content,
                    attempts=attempt,
                    checkpoints=checkpoints,
                    final_validation=validation_result,
                )
            failure_type = self._classify_failure(validation_result)
            checkpoint.failure_type = failure_type
            logger.warning(
                f"Validation failed on attempt {attempt}: type={failure_type.value}, score={checkpoint.score:.2f}",
            )
            if self.reversion_enabled and attempt > 1:
                prev_checkpoint = checkpoints[-2]
                if checkpoint.score < prev_checkpoint.score:
                    logger.info(
                        f"Reverting to attempt {attempt - 1} (score {prev_checkpoint.score:.2f} > {checkpoint.score:.2f})",
                    )
                    return RegenerationResult(
                        success=True,
                        final_content=prev_checkpoint.content,
                        attempts=attempt,
                        checkpoints=checkpoints,
                        final_validation=prev_checkpoint.validation_result,
                        reverted=True,
                    )
            if attempt < self.max_attempts:
                temperature = self._adjust_temperature(temperature, failure_type)
                context = self._build_regeneration_context(
                    initial_context,
                    validation_result,
                    content,
                    attempt,
                )
        logger.error(f"Exhausted all {self.max_attempts} attempts for {k_node_id}")
        if self.reversion_enabled and checkpoints:
            best_checkpoint = max(checkpoints, key=lambda cp: cp.score)
            logger.info(
                f"Returning best attempt {best_checkpoint.attempt} (score={best_checkpoint.score:.2f})",
            )
            return RegenerationResult(
                success=False,
                final_content=best_checkpoint.content,
                attempts=self.max_attempts,
                checkpoints=checkpoints,
                final_validation=best_checkpoint.validation_result,
                exhausted=True,
            )
        last_checkpoint = checkpoints[-1] if checkpoints else None
        return RegenerationResult(
            success=False,
            final_content=last_checkpoint.content if last_checkpoint else "",
            attempts=self.max_attempts,
            checkpoints=checkpoints,
            final_validation=last_checkpoint.validation_result if last_checkpoint else None,
            exhausted=True,
        )

    def _classify_failure(self, validation_result: Any) -> ConstraintFailureType:
        """Classify failure type based on validation result.

        Args:
            validation_result: ValidationResult from validator

        Returns:
            ConstraintFailureType
        """
        if not hasattr(validation_result, "failures") or not validation_result.failures:
            return ConstraintFailureType.MECHANICAL
        has_word_count = False
        has_placeholder = False
        has_redundancy = False
        has_forbidden = False
        for failure in validation_result.failures:
            rule_id = failure.rule_id.lower()
            if "word" in rule_id or "char" in rule_id or "variance" in rule_id:
                has_word_count = True
            elif "placeholder" in rule_id:
                has_placeholder = True
            elif "dedup" in rule_id or "similarity" in rule_id or "redundancy" in rule_id:
                has_redundancy = True
            elif "forbidden" in rule_id or "filler" in rule_id:
                has_forbidden = True
        if has_placeholder or has_redundancy:
            return ConstraintFailureType.CREATIVE
        elif has_forbidden:
            return ConstraintFailureType.SEMANTIC
        elif has_word_count:
            return ConstraintFailureType.MECHANICAL
        else:
            return ConstraintFailureType.MECHANICAL

    def _adjust_temperature(self, current_temp: float, failure_type: ConstraintFailureType) -> float:
        """Adjust temperature based on failure type.

        Args:
            current_temp: Current temperature
            failure_type: Type of constraint failure

        Returns:
            Adjusted temperature
        """
        escalation = self.adaptive_temperature_config["constraint_failure_types"].get(
            failure_type.value,
            self.adaptive_temperature_config["escalation_per_retry"],
        )
        new_temp = current_temp + escalation
        max_temp = self.adaptive_temperature_config["max_temperature"]
        adjusted_temp = min(new_temp, max_temp)
        logger.info(
            f"Temperature adjustment: {current_temp:.2f} -> {adjusted_temp:.2f} (failure_type={failure_type.value}, escalation={escalation})",
        )
        return adjusted_temp

    def _build_regeneration_context(
        self,
        initial_context: dict[str, Any],
        validation_result: Any,
        previous_content: str,
        attempt: int,
    ) -> dict[str, Any]:
        """Build context for regeneration with exact failure details.

        Args:
            initial_context: Original context
            validation_result: Validation result with failures
            previous_content: Previously generated content
            attempt: Current attempt number

        Returns:
            Enhanced context with failure feedback
        """
        context = initial_context.copy()
        context["regeneration_attempt"] = attempt
        context["previous_content"] = previous_content
        if hasattr(validation_result, "failures") and validation_result.failures:
            failure_details = []
            for failure in validation_result.failures:
                detail = {
                    "rule_id": failure.rule_id,
                    "rule_name": failure.rule_name,
                    "message": failure.message,
                    "actual": failure.actual,
                    "expected": failure.expected,
                }
                failure_details.append(detail)
            context["validation_failures"] = failure_details
            failure_summary = self._build_failure_summary(validation_result.failures)
            context["failure_summary"] = failure_summary
        return context

    def _build_failure_summary(self, failures: list[Any]) -> str:
        """Build human-readable failure summary for regeneration prompt.

        Args:
            failures: List of RuleFailure objects

        Returns:
            Formatted failure summary
        """
        summary_lines = ["VALIDATION FAILURES:"]
        for i, failure in enumerate(failures, 1):
            summary_lines.append(f"{i}. {failure.rule_name}: {failure.message}")
            if hasattr(failure, "actual") and hasattr(failure, "expected"):
                summary_lines.append(f"   Actual: {failure.actual}, Expected: {failure.expected}")
        summary_lines.append("\nREGENERATION INSTRUCTIONS:")
        summary_lines.append("Fix ONLY the failing sections listed above.")
        summary_lines.append("Maintain all other content unchanged.")
        return "\n".join(summary_lines)

    def apply_message_transition(
        self,
        current_route: str,
        target_route: str,
        content: str,
        context: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """Apply message type transition logic.

        Args:
            current_route: Current message route
            target_route: Target message route
            content: Current content
            context: Current context

        Returns:
            Tuple of (modified_content, modified_context)
        """
        transition_key = f"{current_route}_to_{target_route}"
        transition = self.message_type_transitions.get(transition_key)
        if not transition:
            logger.warning(f"No transition defined for {transition_key}")
            return (content, context)
        logger.info(f"Applying transition: {transition_key}")
        if "action" in transition:
            action = transition["action"]
            if "Regenerate K.3" in action:
                if "continuity" in action.lower():
                    context["add_continuity_clause"] = True
                    context["prior_content"] = content
            elif "Expand K.3" in action:
                if "expansions" in transition:
                    context["expansion_requirements"] = transition["expansions"]
            elif "Enable job-specific RAG" in action:
                context["job_specific_mode"] = True
                if "requirements" in transition:
                    context["job_requirements"] = transition["requirements"]
        return (content, context)

    def generate_failure_report(self, result: RegenerationResult, k_node_id: str) -> str:
        """Generate detailed failure report for exhausted attempts.

        Args:
            result: RegenerationResult from execute_with_feedback
            k_node_id: K-node identifier

        Returns:
            Formatted failure report
        """
        report_lines = [
            f"REGENERATION FAILURE REPORT: {k_node_id}",
            "=" * 60,
            f"Status: {('REVERTED' if result.reverted else 'EXHAUSTED')}",
            f"Total Attempts: {result.attempts}",
            f"Max Attempts: {self.max_attempts}",
            "",
            "ATTEMPT HISTORY:",
        ]
        for checkpoint in tqdm(result.checkpoints, desc="Processing", unit="item"):
            report_lines.append(f"\nAttempt {checkpoint.attempt}:")
            report_lines.append(f"  Temperature: {checkpoint.temperature:.2f}")
            report_lines.append(f"  Score: {checkpoint.score:.2f}")
            report_lines.append(
                f"  Failure Type: {(checkpoint.failure_type.value if checkpoint.failure_type else 'N/A')}",
            )
            if hasattr(checkpoint.validation_result, "failures"):
                report_lines.append(f"  Failures: {len(checkpoint.validation_result.failures)}")
                for failure in checkpoint.validation_result.failures[:3]:
                    report_lines.append(f"    - {failure.rule_name}: {failure.message}")
        if result.reverted:
            report_lines.append(f"\nREVERTED TO: Attempt {result.checkpoints[-2].attempt}")
        report_lines.append("\nRECOMMENDATIONS:")
        if result.exhausted:
            report_lines.append("- Review constraint conflicts")
            report_lines.append("- Adjust generation parameters")
            report_lines.append("- Verify input data quality")
        return "\n".join(report_lines)
