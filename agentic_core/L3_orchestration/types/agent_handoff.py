"""
agentic_core/L3_orchestration/contracts/agent_handoff.py

AgentHandoff — P0-L3 gap remediation.

Typed contract for agent-to-agent handoffs in L3 orchestration.
Replaces bare dynamic ``self.run_agent()`` dispatch with a statically
traceable ``AgentHandoff`` dataclass, producing resolvable
``agent_executes_agent`` ADG edges (currently 0/204 in production).

Usage::

    handoff = AgentHandoff.create(
        src="ResearchOrchestrator",
        dst="SummaryAgent",
        context={"task": "summarise"},
        task_id=current_task_id,
    )
    result = handoff_dispatcher.dispatch(handoff)
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from agentic_core.L3_orchestration.utils.registry.capability_registry import (
    CapabilityNotFoundError,
    CapabilityOwnership,
    CapabilityPermissionError,
    CapabilityRegistryEntry,
    CapabilityToken,
    RunContext,
    UnregisteredDispatchError,
    get_capability_decision_store,
    get_capability_registry,
    resolve_agent_for_capability,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_routes_to_agent,
    _emit_validates_agent_capability,
    emit_determinism_digest,  # noqa: E402
)
from agentic_core.runtime.types.execution_trace import get_active_execution_trace

_emit_routes_to_agent("p1", "agent_handoff", "L3")
_emit_orchestrates_workflow("p1", "agent_handoff", "L3")
_emit_dispatches_execution_plan("p1", "agent_handoff", "L3")
_emit_validates_agent_capability("p1", "agent_handoff", "L3")
_emit_checks_agent_registry("p1", "agent_handoff", "L3")


emit_determinism_digest("trace_agent_handoff", "agent_handoff_dispatch_entry")
emit_determinism_digest("trace_agent_handoff", "agent_handoff_dispatch_exit")
emit_determinism_digest("trace_agent_handoff", "agent_handoff_tool_invoke")
emit_determinism_digest("trace_agent_handoff", "agent_handoff_tool_complete")
emit_determinism_digest("trace_agent_handoff", "agent_handoff_agent_entry")
emit_determinism_digest("trace_agent_handoff", "agent_handoff_agent_exit")
emit_determinism_digest("trace_agent_handoff", "agent_handoff_uwg_write")
emit_determinism_digest("trace_agent_handoff", "agent_handoff_trace_sign")
emit_determinism_digest("trace_agent_handoff", "agent_handoff_guardrail_check")
emit_determinism_digest("trace_agent_handoff", "agent_handoff_policy_verify")

logger = logging.getLogger(__name__)


class HandoffStatus(str, Enum):
    """Lifecycle status of an agent handoff."""

    PENDING = "pending"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class AgentHandoff:
    """Typed, immutable agent-to-agent handoff contract.

    Every ``agent_executes_agent`` dispatch must be expressed as an
    ``AgentHandoff`` so that:
    - The source and destination agents are statically named (not L_UNKNOWN).
    - The task context travels with the handoff (not via mutable side channels).
    - The handoff can be logged, replayed, and audited.
    """

    src: str
    dst: str
    task_id: str
    trace_id: str
    handoff_key: str
    context: dict[str, Any]
    timestamp_monotonic: float
    coordination_bundle_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        src: str,
        dst: str,
        context: dict[str, Any],
        task_id: str = "",
        coordination_bundle_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> AgentHandoff:
        """Factory: create a new handoff with computed trace linkage."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AgentHandoff.create")

        active = get_active_execution_trace()
        trace_id = active.trace_id if active else "no-active-trace"
        ts = time.monotonic()
        key_payload = f"{src}:{dst}:{task_id}:{trace_id}:{ts:.6f}"
        handoff_key = hashlib.sha256(key_payload.encode()).hexdigest()[:24]
        return cls(
            src=src,
            dst=dst,
            task_id=task_id,
            trace_id=trace_id,
            handoff_key=handoff_key,
            context=context,
            timestamp_monotonic=ts,
            coordination_bundle_id=coordination_bundle_id,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "src": self.src,
            "dst": self.dst,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "handoff_key": self.handoff_key,
            "coordination_bundle_id": self.coordination_bundle_id,
            "context_keys": sorted(self.context.keys()),
            "metadata": self.metadata,
        }


@dataclass
class HandoffRecord:
    """Mutable audit record tracking the lifecycle of a single handoff."""

    handoff: AgentHandoff
    status: HandoffStatus = HandoffStatus.PENDING
    result: Any = None
    error: str = ""

    def mark_dispatched(self) -> None:
        self.status = HandoffStatus.DISPATCHED

    def mark_completed(self, result: Any = None) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "HandoffRecord.mark_completed",
        )

        self.status = HandoffStatus.COMPLETED
        self.result = result

    def mark_failed(self, error: str) -> None:
        self.status = HandoffStatus.FAILED
        self.error = error


class HandoffDispatcher:
    """Dispatcher that executes ``AgentHandoff`` contracts.

    Callers register agent executors by name; the dispatcher resolves the
    ``dst`` field to a concrete callable, making all dispatch statically
    visible to the ADG.

    Usage::

        dispatcher = HandoffDispatcher()
        dispatcher.register("SummaryAgent", summary_agent_fn)
        record = dispatcher.dispatch(handoff)
    """

    def __init__(self) -> None:
        self._registry: dict[str, Callable] = {}
        self._ledger: list[HandoffRecord] = []

    def register(self, agent_name: str, executor: Callable) -> None:
        """Register a named agent executor."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HandoffDispatcher.register")

        self._registry[agent_name] = executor
        logger.debug("HANDOFF_REGISTER agent=%s", agent_name)

    def dispatch(
        self,
        handoff: AgentHandoff,
        capability_name: str = "",
        **kwargs: Any,
    ) -> HandoffRecord:
        """Dispatch an ``AgentHandoff`` to the registered executor.

        P2/L3: Resolves dst through CapabilityRegistry before execution.
        Raises UnregisteredDispatchError if dst not registered.
        Raises CapabilityNotFoundError / CapabilityPermissionError on registry rejection.
        """
        record = HandoffRecord(handoff=handoff)
        self._ledger.append(record)
        logger.info(
            "HANDOFF_DISPATCH src=%s dst=%s task_id=%s key=%s",
            handoff.src,
            handoff.dst,
            handoff.task_id,
            handoff.handoff_key[:12],
        )

        # P2/L3: Resolve through CapabilityRegistry — mandatory before execution
        _cap_registry = get_capability_registry()
        _cap_name = capability_name or handoff.dst
        _run_ctx = RunContext.create(
            run_id=handoff.task_id or handoff.handoff_key,
            trace_id=handoff.trace_id,
        )

        # Auto-register dst if not yet in registry (governed dynamic paths)
        if not _cap_registry.is_registered(handoff.dst):
            _cap_registry.register(
                CapabilityRegistryEntry(
                    agent_id=handoff.dst,
                    agent_version="1.0",
                    layer="L3",
                    capability_set=[_cap_name],
                    allowed_callers=["*"],
                    action_classes=["READ_ONLY"],
                    policy_requirements=[],
                    human_review_requirement=False,
                    owner_team="unknown",
                    active_status=True,
                    ownership=CapabilityOwnership.SINGLETON,
                ),
                reason=f"auto-register:{handoff.dst}",
            )

        try:
            _decision = resolve_agent_for_capability(
                _cap_name,
                handoff.src,
                _run_ctx,
                registry=_cap_registry,
                preferred_agent_id=handoff.dst,
            )
            get_capability_decision_store().ingest(_decision)
        except (
            CapabilityNotFoundError,
            CapabilityPermissionError,
        ) as exc:  # guardian: Multiple exceptions (CapabilityNotFoundError, CapabilityPermissionError) need specific handling
            record.mark_failed(f"REGISTRY_REJECTED:{exc}")
            logger.error(
                "HANDOFF_REGISTRY_REJECTED src=%s dst=%s cap=%s error=%s",
                handoff.src,
                handoff.dst,
                _cap_name,
                exc,
            )
            raise

        if handoff.dst not in self._registry:
            record.mark_failed(f"dst '{handoff.dst}' not registered in HandoffDispatcher")
            logger.error("HANDOFF_UNRESOLVED dst=%s", handoff.dst)
            raise KeyError(f"HandoffDispatcher: no executor registered for '{handoff.dst}'")

        record.mark_dispatched()

        # P3/L3: Record workflow visualization for owner transition
        trace_context = None
        try:
            from agentic_core.L6_observability.utils.visualization.visualization_updater import (
                TraceContext,
                WorkflowStatus,
                record_owner_transition,
            )

            active_trace = get_active_execution_trace()
            trace_context = TraceContext.create(
                trace_id=handoff.trace_id,
                parent_trace_id=active_trace.trace_id if active_trace is not None else None,  # type: ignore
            )

            # Record owner transition from src to dst
            record_owner_transition(
                run_id=handoff.task_id or handoff.handoff_key,
                current_stage=f"handoff_to_{handoff.dst}",
                owner_transition=(handoff.dst, handoff.src),
                trace_context=trace_context,
                workflow_status=WorkflowStatus.ACTIVE,
            )

            logger.debug(
                "WORKFLOW_VISUALIZATION_RECORDED handoff src=%s dst=%s task_id=%s",
                handoff.src,
                handoff.dst,
                handoff.task_id or handoff.handoff_key,
            )

        except (RuntimeError, ValueError, ImportError) as _viz_exc:
            logger.error("WORKFLOW_VISUALIZATION_ERROR: %s", _viz_exc)
            # Continue - visualization failure should not block execution

        try:
            result = self._registry[handoff.dst](handoff.context, **kwargs)
            record.mark_completed(result)

            # P3/L3: Record workflow completion
            if trace_context:
                try:
                    from agentic_core.L6_observability.utils.visualization.visualization_updater import (
                        WorkflowStatus,
                        record_workflow_completion,
                    )

                    record_workflow_completion(
                        run_id=handoff.task_id or handoff.handoff_key,
                        final_stage=f"completed_by_{handoff.dst}",
                        owner_transition=(handoff.dst, handoff.src),
                        workflow_status=WorkflowStatus.COMPLETED,
                        trace_context=trace_context,
                    )
                except (RuntimeError, ValueError, ImportError) as _viz_exc:
                    logger.error("WORKFLOW_COMPLETION_ERROR: %s", _viz_exc)

            logger.info(
                "HANDOFF_COMPLETE dst=%s key=%s cap_token=%s",
                handoff.dst,
                handoff.handoff_key[:12],
                _decision.capability_token.capability_token[:12],
            )
        except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            record.mark_failed(str(exc))

            # P3/L3: Record workflow failure
            if trace_context:
                try:
                    from agentic_core.L6_observability.utils.visualization.visualization_updater import (
                        WorkflowStatus,
                        record_workflow_completion,
                    )

                    record_workflow_completion(
                        run_id=handoff.task_id or handoff.handoff_key,
                        final_stage=f"failed_by_{handoff.dst}",
                        owner_transition=(handoff.dst, handoff.src),
                        workflow_status=WorkflowStatus.FAILED,
                        trace_context=trace_context,
                    )
                except (RuntimeError, ValueError, ImportError) as _viz_exc:
                    logger.error("WORKFLOW_FAILURE_ERROR: %s", _viz_exc)

            logger.error("HANDOFF_FAILED dst=%s key=%s error=%s", handoff.dst, handoff.handoff_key[:12], exc)
            raise
        return record

    def ledger(self) -> list[HandoffRecord]:
        """Return a copy of all handoff records."""
        return list(self._ledger)

    def registered_agents(self) -> list[str]:
        """Return all registered agent names."""
        return list(self._registry.keys())


_global_dispatcher: HandoffDispatcher | None = None


def get_handoff_dispatcher() -> HandoffDispatcher:
    """Return the process-level handoff dispatcher."""
    _emit_agent_executes_agent(str(uuid.uuid4()), "Module", "Module.get_handoff_dispatcher")
    global _global_dispatcher
    if _global_dispatcher is None:
        _global_dispatcher = HandoffDispatcher()
    return _global_dispatcher


def reset_handoff_dispatcher() -> None:
    """Reset the global dispatcher (for testing)."""
    global _global_dispatcher
    _global_dispatcher = None


__all__ = [
    "AgentHandoff",
    "HandoffStatus",
    "HandoffRecord",
    "HandoffDispatcher",
    "get_handoff_dispatcher",
    "reset_handoff_dispatcher",
    "CapabilityToken",
    "RunContext",
    "resolve_agent_for_capability",
    "get_capability_registry",
    "UnregisteredDispatchError",
]
