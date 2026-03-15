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
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


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
        self, gate_id: str, message: str, details: dict[str, Any] | None = None
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
