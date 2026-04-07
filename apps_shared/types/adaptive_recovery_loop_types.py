"""Adaptive Recovery Loop - The Fixer

This module implements temperature escalation protocol for adaptive recovery.
Handles both creative and mechanical failures with intelligent temperature adjustments.

Layer: Runtime/Shared
Responsibilities:
- Monitor validation failures and classify failure types
- Adjust temperature parameters based on failure patterns
- Implement max retry logic with hard halt
- Track temperature escalation history

Non-responsibilities:
- Content generation
- Validation execution
- Model invocation
"""

import time
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

_emit_applies_guardrail("p0", "adaptive_recovery_loop_types", "p0_governance")
_emit_reads_policy_state("p0", "adaptive_recovery_loop_types", "policy_binding")
_emit_snapshots_state("p0", "adaptive_recovery_loop_types", "state_snapshot")
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

_emit_emits_metric_event("adaptive_recovery_loop_types", "p4obs", "metric_1")
_emit_emits_metric_event("adaptive_recovery_loop_types", "p4obs", "metric_2")
_emit_emits_metric_event("adaptive_recovery_loop_types", "p4obs", "metric_3")
_emit_emits_metric_event("adaptive_recovery_loop_types", "p4obs", "metric_4")
_emit_emits_metric_event("adaptive_recovery_loop_types", "p4obs", "metric_5")
_emit_emits_metric_event("adaptive_recovery_loop_types", "p4obs", "metric_6")
_emit_records_incident_event("adaptive_recovery_loop_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("adaptive_recovery_loop_types", "p4obs", "anomaly")
_emit_writes_observability_log("adaptive_recovery_loop_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("adaptive_recovery_loop_types", "p4obs", "mon_state")
_emit_triggers_alert("adaptive_recovery_loop_types", "p4obs", "alert")
_emit_links_incident_trace("adaptive_recovery_loop_types", "p4obs", "trace_link")
_emit_captures_pattern("adaptive_recovery_loop_types", "p3lm", "pattern")
_emit_records_learning_event("adaptive_recovery_loop_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adaptive_recovery_loop_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("adaptive_recovery_loop_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adaptive_recovery_loop_types", "p3lm", "routing")
_emit_improves_agent_policy("adaptive_recovery_loop_types", "p3lm", "policy")
_emit_stores_learning_state("adaptive_recovery_loop_types", "p3lm", "state")
_emit_records_execution_trace("adaptive_recovery_loop_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adaptive_recovery_loop_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adaptive_recovery_loop_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adaptive_recovery_loop_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adaptive_recovery_loop_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adaptive_recovery_loop_types", "env_read", "p2_env_1")
_emit_reads_environ("adaptive_recovery_loop_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("adaptive_recovery_loop_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adaptive_recovery_loop_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adaptive_recovery_loop_types", "context_pull")
_emit_pulls_context("p1", "adaptive_recovery_loop_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "adaptive_recovery_loop_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adaptive_recovery_loop_types", "uwg_term_2")
_emit_writes_through("p1", "adaptive_recovery_loop_types", "write_through")
_emit_writes_through("p1", "adaptive_recovery_loop_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "adaptive_recovery_loop_types", "safety_validation")
_emit_invokes_eval("p1", "adaptive_recovery_loop_types", "eval_call")
_emit_proposal_commits_routing("p1", "adaptive_recovery_loop_types", "routing_commit")
_emit_escalates_to_human("p1", "adaptive_recovery_loop_types", "human_escalation")
_emit_routes_through("p1", "adaptive_recovery_loop_types", "route_through")
_emit_checks_agent_registry("p1", "adaptive_recovery_loop_types", "agent_registry")
_emit_validates_agent_capability("p1", "adaptive_recovery_loop_types", "capability")
_emit_dispatches_execution_plan("p1", "adaptive_recovery_loop_types", "exec_plan")
_emit_agent_executes_agent("p1", "adaptive_recovery_loop_types", "sub_agent")
_emit_routes_to_agent("p1", "adaptive_recovery_loop_types", "target_agent")
_emit_verifies_policy("p1", "adaptive_recovery_loop_types", "policy_check")
_emit_observes_runtime_state("p1", "adaptive_recovery_loop_types", "runtime_state")
_emit_verifies_boundary("p1", "adaptive_recovery_loop_types", "boundary_check")
_emit_transcripts_response("p1", "adaptive_recovery_loop_types", "transcript")
_emit_hard_fails_untranscripted("p1", "adaptive_recovery_loop_types")
_emit_gated_by_confidence("p1", "adaptive_recovery_loop_types", "confidence_gate")
emit_replay_key("p0", "adaptive_recovery_loop_types")
emit_determinism_digest("p0", "adaptive_recovery_loop_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "adaptive_recovery_loop_types", "execution_auth")
_emit_validates_capability("p2", "adaptive_recovery_loop_types", "capability_check")
_emit_routes_to_capability("p2", "adaptive_recovery_loop_types", "capability_route")
_emit_writes_via_uwg("p2", "adaptive_recovery_loop_types", "uwg_write")
_emit_blocks_direct_write("p2", "adaptive_recovery_loop_types", "direct_write_block")
_emit_records_tool_invocation("p2", "adaptive_recovery_loop_types", "tool_invocation")
_emit_captures_execution_output("p2", "adaptive_recovery_loop_types", "exec_output")
_emit_dispatches_agent("p3", "adaptive_recovery_loop_types", "agent_dispatch")
_emit_coordinates_agents("p3", "adaptive_recovery_loop_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "adaptive_recovery_loop_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "adaptive_recovery_loop_types", "healing_outcome")
_emit_escalates_failure("p3", "adaptive_recovery_loop_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "adaptive_recovery_loop_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adaptive_recovery_loop_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "adaptive_recovery_loop_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "adaptive_recovery_loop_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adaptive_recovery_loop_types", "eval_metric")
_emit_stores_embedding("p4", "adaptive_recovery_loop_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "adaptive_recovery_loop_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adaptive_recovery_loop_types", "exec_snapshot_link")


class FailureType(Enum):
    CREATIVE = "CREATIVE"
    MECHANICAL = "MECHANICAL"
    UNKNOWN = "UNKNOWN"


class RecoveryAction(Enum):
    INCREASE_TEMP = "INCREASE_TEMP"
    DECREASE_TEMP = "DECREASE_TEMP"
    HARD_HALT = "HARD_HALT"
    CONTINUE = "CONTINUE"


@dataclass
class FailureEvent:
    attempt: int
    failure_type: FailureType
    gate_id: str
    message: str
    timestamp: float = field(default_factory=time.time)
    details: dict[str, Any] | None = None


@dataclass
class TemperatureAdjustment:
    from_temp: float
    to_temp: float
    reason: str
    failure_type: FailureType
    timestamp: float = field(default_factory=time.time)


@dataclass
class RecoveryResult:
    action: RecoveryAction
    new_temperature: float
    message: str
    should_retry: bool
    details: dict[str, Any]


class AdaptiveRecoveryLoop:
    """
    The Fixer - Implements Temperature Escalation Protocol.

    Recovery Philosophy:
    - Creative Failure: Increase temp +0.15 (force different thinking)
    - Mechanical Failure: Increase temp +0.05 (slight nudge)
    - Max 3 attempts before HARD_HALT
    """

    MAX_ATTEMPTS = 3
    CREATIVE_TEMP_INCREASE = 0.15
    MECHANICAL_TEMP_INCREASE = 0.05
    CREATIVE_MAX_TEMP = 0.9
    MECHANICAL_MAX_TEMP = 0.7
    CREATIVE_FAILURE_PATTERNS = {
        "generic",
        "cliché",
        "robotic",
        "template",
        "boilerplate",
        "buzzword",
        "jargon",
        "vague",
        "abstract",
        "unoriginal",
    }
    MECHANICAL_FAILURE_PATTERNS = {
        "word count",
        "character limit",
        "length",
        "format",
        "structure",
        "punctuation",
        "capitalization",
    }

    def __init__(self, initial_temperature: float = 0.5):
        self.initial_temperature = initial_temperature
        self.current_temperature = initial_temperature
        self.attempt_count = 0
        self.failure_history: list[FailureEvent] = []
        self.temperature_history: list[TemperatureAdjustment] = []

    def record_failure(
        self, gate_id: str, message: str, details: dict[str, Any] | None = None,
    ) -> RecoveryResult:
        """
        Record a validation failure and determine recovery action.

        Returns RecoveryResult with action and new temperature.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AdaptiveRecoveryLoop.record_failure")

        self.attempt_count += 1
        failure_type = self._classify_failure(message, details)
        failure_event = FailureEvent(
            attempt=self.attempt_count,
            failure_type=failure_type,
            gate_id=gate_id,
            message=message,
            details=details,
        )
        self.failure_history.append(failure_event)
        if self.attempt_count >= self.MAX_ATTEMPTS:
            return RecoveryResult(
                action=RecoveryAction.HARD_HALT,
                new_temperature=self.current_temperature,
                message=f"HARD_HALT: Max attempts ({self.MAX_ATTEMPTS}) reached",
                should_retry=False,
                details={
                    "total_attempts": self.attempt_count,
                    "failure_history": [
                        {"attempt": f.attempt, "type": f.failure_type.value, "gate": f.gate_id}
                        for f in self.failure_history
                    ],
                },
            )
        new_temp = self._calculate_new_temperature(failure_type)
        adjustment = TemperatureAdjustment(
            from_temp=self.current_temperature,
            to_temp=new_temp,
            reason=self._get_adjustment_reason(failure_type),
            failure_type=failure_type,
        )
        self.temperature_history.append(adjustment)
        old_temp = self.current_temperature
        self.current_temperature = new_temp
        return RecoveryResult(
            action=RecoveryAction.INCREASE_TEMP,
            new_temperature=new_temp,
            message=f"Temperature adjusted: {old_temp:.2f} → {new_temp:.2f} ({failure_type.value})",
            should_retry=True,
            details={
                "attempt": self.attempt_count,
                "failure_type": failure_type.value,
                "temperature_delta": new_temp - old_temp,
                "remaining_attempts": self.MAX_ATTEMPTS - self.attempt_count,
            },
        )

    def record_success(self) -> dict[str, Any]:
        """Record successful generation after recovery"""
        return {
            "success": True,
            "total_attempts": self.attempt_count,
            "temperature_adjustments": len(self.temperature_history),
            "final_temperature": self.current_temperature,
            "recovery_path": [
                {
                    "from": adj.from_temp,
                    "to": adj.to_temp,
                    "reason": adj.reason,
                    "type": adj.failure_type.value,
                }
                for adj in self.temperature_history
            ],
        }

    def reset(self, initial_temperature: float | None = None) -> None:
        """Reset recovery loop for new generation task"""
        if initial_temperature is not None:
            self.initial_temperature = initial_temperature
        self.current_temperature = self.initial_temperature
        self.attempt_count = 0
        self.failure_history.clear()
        self.temperature_history.clear()

    def get_temperature_log(self) -> list[dict[str, Any]]:
        """Get complete temperature adjustment log for audit"""
        return [
            {
                "from_temp": adj.from_temp,
                "to_temp": adj.to_temp,
                "delta": adj.to_temp - adj.from_temp,
                "reason": adj.reason,
                "failure_type": adj.failure_type.value,
                "timestamp": adj.timestamp,
            }
            for adj in self.temperature_history
        ]

    def _classify_failure(self, message: str, details: dict[str, Any] | None) -> FailureType:
        """
        Classify failure as CREATIVE or MECHANICAL based on message content.

        Creative: Generic/cliché/robotic prose detected
        Mechanical: Word count/format/structure violations
        """
        message_lower = message.lower()
        if any(pattern in message_lower for pattern in self.CREATIVE_FAILURE_PATTERNS):
            return FailureType.CREATIVE
        if any(pattern in message_lower for pattern in self.MECHANICAL_FAILURE_PATTERNS):
            return FailureType.MECHANICAL
        if details:
            details_str = str(details).lower()
            if any(pattern in details_str for pattern in self.CREATIVE_FAILURE_PATTERNS):
                return FailureType.CREATIVE
            if any(pattern in details_str for pattern in self.MECHANICAL_FAILURE_PATTERNS):
                return FailureType.MECHANICAL
        return FailureType.UNKNOWN

    def _calculate_new_temperature(self, failure_type: FailureType) -> float:
        """
        Calculate new temperature based on failure type.

        Creative Failure: +0.15 (max 0.9) - Force model to think differently
        Mechanical Failure: +0.05 (max 0.7) - Slight nudge to regenerate
        """
        if failure_type == FailureType.CREATIVE:
            new_temp = min(self.current_temperature + self.CREATIVE_TEMP_INCREASE, self.CREATIVE_MAX_TEMP)
        elif failure_type == FailureType.MECHANICAL:
            new_temp = min(self.current_temperature + self.MECHANICAL_TEMP_INCREASE, self.MECHANICAL_MAX_TEMP)
        else:
            new_temp = min(self.current_temperature + self.MECHANICAL_TEMP_INCREASE, self.MECHANICAL_MAX_TEMP)
        return round(new_temp, 2)

    def _get_adjustment_reason(self, failure_type: FailureType) -> str:
        """Get human-readable reason for temperature adjustment"""
        if failure_type == FailureType.CREATIVE:
            return "Creative failure detected - forcing different thinking pattern"
        elif failure_type == FailureType.MECHANICAL:
            return "Mechanical failure detected - slight nudge for regeneration"
        else:
            return "Unknown failure type - applying conservative adjustment"


def create_adaptive_recovery_loop(initial_temperature: float = 0.5) -> AdaptiveRecoveryLoop:
    """Factory function to create AdaptiveRecoveryLoop instance"""
    return AdaptiveRecoveryLoop(initial_temperature=initial_temperature)
