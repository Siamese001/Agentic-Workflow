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
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from agentic_core.runtime.execution_trace import get_active_execution_trace

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
        self._registry[agent_name] = executor
        logger.debug("HANDOFF_REGISTER agent=%s", agent_name)

    def dispatch(self, handoff: AgentHandoff, **kwargs: Any) -> HandoffRecord:
        """Dispatch an ``AgentHandoff`` to the registered executor.

        Logs the handoff, resolves ``dst`` to a concrete callable, and
        records the outcome.  Raises ``KeyError`` if ``dst`` is not registered.
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
        if handoff.dst not in self._registry:
            record.mark_failed(f"dst '{handoff.dst}' not registered in HandoffDispatcher")
            logger.error("HANDOFF_UNRESOLVED dst=%s", handoff.dst)
            raise KeyError(f"HandoffDispatcher: no executor registered for '{handoff.dst}'")
        record.mark_dispatched()
        try:
            result = self._registry[handoff.dst](handoff.context, **kwargs)
            record.mark_completed(result)
            logger.info("HANDOFF_COMPLETE dst=%s key=%s", handoff.dst, handoff.handoff_key[:12])
        except Exception as exc:
            record.mark_failed(str(exc))
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
]
