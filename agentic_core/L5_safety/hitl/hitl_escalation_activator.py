"""
agentic_core/L5_safety/hitl/hitl_escalation_activator.py

HITLEscalationActivator — P3-L5 gap remediation.

Activates the HITL escalation path when policy enforcement, guardrail
checks, or tool safety gates produce ESCALATE / REENTER verdicts.
Closes the gap: 608 L5 modules, 0 hitl_escalation_activation edges,
2 HITL files but 0 escalation triggers from enforcement modules.

ADG edges emitted: hitl_escalation_activation, reenters_safety,
                   validated_by_safety_plane
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from agentic_core.L5_safety.hitl.decision_logger import (
    HITLDecision,
    get_decision_logger,
)
from agentic_core.runtime.execution_trace import get_active_execution_trace
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace

logger = logging.getLogger(__name__)


class EscalationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EscalationRequest:
    """Single HITL escalation request."""

    trace_id: str
    agent: str
    module: str
    trigger_reason: str
    priority: EscalationPriority
    proposed_action: str
    policy_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution: str = ""

    def resolve(self, decision: str) -> None:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "EscalationRequest.resolve")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:EscalationRequest.resolve".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.resolved = True
        self.resolution = decision


class HITLEscalationActivator:
    """Activates HITL escalation from enforcement verdicts.

    Usage::

        activator = HITLEscalationActivator()
        activator.register_handler(my_async_review_handler)

        # When PolicyEnforcementPoint returns ESCALATE:
        escalation = activator.escalate(
            agent="ToolSafetyGate",
            module="tool_safety_gate",
            trigger_reason="policy hash missing",
            proposed_action="invoke eval tool",
            priority=EscalationPriority.HIGH,
            policy_hash="",
        )
    """

    def __init__(self) -> None:
        self._pending: list[EscalationRequest] = []
        self._resolved: list[EscalationRequest] = []
        self._handlers: list[Callable[[EscalationRequest], str | None]] = []

    def register_handler(self, handler: Callable[[EscalationRequest], str | None]) -> None:
        """Register a review handler (sync). Handler returns decision string or None."""
        self._handlers.append(handler)

    def _trace_id(self) -> str:
        active = get_active_execution_trace()
        return active.trace_id if active else "no-active-trace"

    def escalate(
        self,
        agent: str,
        module: str,
        trigger_reason: str,
        proposed_action: str = "",
        priority: EscalationPriority = EscalationPriority.HIGH,
        policy_hash: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> EscalationRequest:
        """Activate HITL escalation for a given trigger.

        Emits ``hitl_escalation_activation`` + ``reenters_safety`` ADG edges.
        Logs via HITLDecisionLogger.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "HITLEscalationActivator.escalate")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:HITLEscalationActivator.escalate".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        req = EscalationRequest(
            trace_id=self._trace_id(),
            agent=agent,
            module=module,
            trigger_reason=trigger_reason,
            priority=priority,
            proposed_action=proposed_action,
            policy_hash=policy_hash,
            metadata=metadata or {},
        )
        self._pending.append(req)
        logger.warning(
            "HITL hitl_escalation_activation reenters_safety "
            "agent=%s module=%s priority=%s reason=%s trace=%s",
            agent,
            module,
            priority.value,
            trigger_reason,
            req.trace_id,
        )

        decision_logger = get_decision_logger()
        decision: HITLDecision = decision_logger.log(
            agent=agent,
            file=module,
            violation=trigger_reason,
            proposed=proposed_action,
            decision="pending",
            metadata={"priority": priority.value, **req.metadata},
        )

        # Dispatch to handlers synchronously
        for handler in self._handlers:
            try:
                result = handler(req)
                if result:
                    req.resolve(result)
                    self._pending.remove(req)
                    self._resolved.append(req)
                    logger.info(
                        "HITL validated_by_safety_plane agent=%s decision=%s",
                        agent,
                        result,
                    )
                    break
            # guardian: allow-silent-swallow
            except Exception as exc:
                logger.error("HITL handler error agent=%s: %s", agent, exc)

        return req

    def pending(self) -> list[EscalationRequest]:
        return list(self._pending)

    def resolved(self) -> list[EscalationRequest]:
        return list(self._resolved)

    def pending_count(self) -> int:
        return len(self._pending)


_global_activator: HITLEscalationActivator | None = None


def get_hitl_escalation_activator() -> HITLEscalationActivator:
    global _global_activator
    if _global_activator is None:
        _global_activator = HITLEscalationActivator()
    return _global_activator


def reset_hitl_escalation_activator() -> None:
    global _global_activator
    _global_activator = None


__all__ = [
    "EscalationPriority",
    "EscalationRequest",
    "HITLEscalationActivator",
    "get_hitl_escalation_activator",
    "reset_hitl_escalation_activator",
]
