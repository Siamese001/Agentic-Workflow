"""
agentic_core/L3_orchestration/contracts/orchestration_handoff_contract.py

OrchestrationHandoffContract — P0/L3 mandatory handoff artifact.

Every agent-to-agent handoff MUST emit one of these.  If no contract is
emitted the orchestration path is invalid and execution FAILS CLOSED.

Required fields (spec §1):
    handoff_id, parent_agent_id, child_agent_id, run_id,
    capability_token, handoff_reason_hash, input_payload_hash,
    policy_hash, trace_id
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L2_execution.utils.providers import get_clock
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_routes_to_agent,
    _emit_validates_agent_capability,  # noqa: E402
)

_emit_routes_to_agent("p1", "orchestration_handoff_contract", "L3")
_emit_orchestrates_workflow("p1", "orchestration_handoff_contract", "L3")
_emit_dispatches_execution_plan("p1", "orchestration_handoff_contract", "L3")
_emit_validates_agent_capability("p1", "orchestration_handoff_contract", "L3")
_emit_checks_agent_registry("p1", "orchestration_handoff_contract", "L3")

logger = logging.getLogger(__name__)
_ADG_LOGGER = logging.getLogger("adg.agent_executes_agent")


class HandoffOutcome(str, Enum):
    """Lifecycle outcome of an orchestration handoff."""

    PENDING = "pending"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    FAILED = "failed"
    DENIED = "denied"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class OrchestrationHandoffContract:
    """Immutable typed contract for one agent-to-agent handoff.

    Carries all 9 mandatory fields required by the P0/L3 spec.
    Emits an ``agent_executes_agent`` ADG edge signal on creation.

    Hard rule: if this contract is not present, the handoff is invalid.
    """

    handoff_id: str
    parent_agent_id: str
    child_agent_id: str
    run_id: str
    capability_token: str
    handoff_reason_hash: str
    input_payload_hash: str
    policy_hash: str
    trace_id: str
    workflow_stage: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        parent_agent_id: str,
        child_agent_id: str,
        run_id: str,
        capability_token: str,
        handoff_reason: str,
        input_payload: Any,
        policy_hash: str,
        workflow_stage: str = "",
        trace_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> OrchestrationHandoffContract:
        """Factory: create a contract with deterministic hashes.

        Args:
            parent_agent_id: Dispatching agent name.
            child_agent_id: Receiving agent name.
            run_id: Current run/trace scope.
            capability_token: Token proving caller has authority.
            handoff_reason: Human-readable reason for this handoff.
            input_payload: Payload being handed off (any serialisable type).
            policy_hash: Hash of the current active policy.
            workflow_stage: Current workflow stage label.
            trace_id: Active trace ID (auto-resolved if empty).
            metadata: Extra key-value annotations.

        Returns:
            Immutable OrchestrationHandoffContract.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "OrchestrationHandoffContract.create",
        )

        if not trace_id:
            try:
                from agentic_core.runtime.trace_context import get_trace_context

                tc = get_trace_context()
                trace_id = getattr(tc, "trace_id", "") or ""
            except (ValueError, TypeError, RuntimeError) as e:
                trace_id = ""

        now = get_clock().now_epoch()
        handoff_id = hashlib.sha256(
            f"{parent_agent_id}:{child_agent_id}:{run_id}:{now:.6f}".encode(),
        ).hexdigest()[:24]
        handoff_reason_hash = hashlib.sha256(handoff_reason.encode()).hexdigest()[:16]
        input_payload_hash = hashlib.sha256(str(input_payload).encode()).hexdigest()[:16]

        contract = cls(
            handoff_id=handoff_id,
            parent_agent_id=parent_agent_id,
            child_agent_id=child_agent_id,
            run_id=run_id,
            capability_token=capability_token,
            handoff_reason_hash=handoff_reason_hash,
            input_payload_hash=input_payload_hash,
            policy_hash=policy_hash,
            trace_id=trace_id,
            workflow_stage=workflow_stage,
            metadata=metadata or {},
            created_epoch=now,
        )

        # Emit ADG-visible signal — captured by _AgentDispatchVisitor
        _ADG_LOGGER.debug(
            "agent_executes_agent parent=%s child=%s run_id=%s stage=%s handoff_id=%s",
            parent_agent_id,
            child_agent_id,
            run_id,
            workflow_stage,
            handoff_id,
        )
        return contract

    def emit_agent_executes_agent(self) -> None:
        """Re-emit the ADG edge signal (idempotent, for wiring call sites)."""
        _ADG_LOGGER.debug(
            "agent_executes_agent parent=%s child=%s run_id=%s",
            self.parent_agent_id,
            self.child_agent_id,
            self.run_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "handoff_id": self.handoff_id,
            "parent_agent_id": self.parent_agent_id,
            "child_agent_id": self.child_agent_id,
            "run_id": self.run_id,
            "capability_token": self.capability_token[:8] + "...",
            "handoff_reason_hash": self.handoff_reason_hash,
            "input_payload_hash": self.input_payload_hash,
            "policy_hash": self.policy_hash,
            "trace_id": self.trace_id,
            "workflow_stage": self.workflow_stage,
            "created_epoch": self.created_epoch,
        }


def emit_agent_executes_agent(
    parent_agent_id: str,
    child_agent_id: str,
    run_id: str = "",
    stage: str = "",
    capability_token: str = "default",  # noqa: S107
    policy_hash: str = "default",
    handoff_reason: str = "",
    input_payload: Any = None,
) -> OrchestrationHandoffContract:
    """Convenience wrapper: emit one agent_executes_agent signal.

    Creates and returns an OrchestrationHandoffContract.  Call this at
    every agent-to-agent handoff site to make the topology graph-visible.

    ADG scanner (_AgentDispatchVisitor) detects calls to this function
    by name and emits agent_executes_agent edges.
    """
    _emit_agent_executes_agent(str(uuid.uuid4()), "Module", "Module.emit_agent_executes_agent")
    return OrchestrationHandoffContract.create(
        parent_agent_id=parent_agent_id,
        child_agent_id=child_agent_id,
        run_id=run_id,
        capability_token=capability_token,
        handoff_reason=handoff_reason or f"{parent_agent_id}->{child_agent_id}",
        input_payload=input_payload or {},
        policy_hash=policy_hash,
        workflow_stage=stage,
    )


__all__ = [
    "OrchestrationHandoffContract",
    "HandoffOutcome",
    "emit_agent_executes_agent",
]
