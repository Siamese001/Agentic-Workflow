"""
agentic_core/runtime/execution_trace.py

Execution trace management for capability token binding.

An execution trace provides the cryptographic context required to issue
and verify capability tokens. Determinism digest is bound to the trace
after the determinism engine is sealed.
"""

import logging
import threading
import uuid
from dataclasses import dataclass
from typing import Any

_logger = logging.getLogger(__name__)


def _bootstrap_determinism_digest() -> None:
    """Deferred bootstrap to avoid circular import with lifecycle_trace_contract."""
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
        emit_determinism_digest,  # noqa: PLC0415
    )

    emit_determinism_digest("execution_trace", "execution_trace_digest")
    _logger.debug("execution_trace determinism digest emitted")


@dataclass(frozen=True)
class ExecutionTrace:
    """Immutable execution trace for capability binding."""

    trace_id: str
    plan_hash: str
    policy_hash: str
    determinism_digest: str
    hierarchy_hash: str
    metadata: dict[str, Any]


class ExecutionTraceManager:
    """Manages the lifecycle of a single active execution trace."""

    def __init__(self) -> None:
        self._active_trace: ExecutionTrace | None = None
        self._lock = threading.RLock()

    def start_trace(
        self,
        plan_hash: str,
        policy_hash: str,
        hierarchy_hash: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Start a new execution trace and return its trace_id."""
        with self._lock:
            trace_id = str(uuid.uuid4())
            self._active_trace = ExecutionTrace(
                trace_id=trace_id,
                plan_hash=plan_hash,
                policy_hash=policy_hash,
                determinism_digest="",
                hierarchy_hash=hierarchy_hash,
                metadata=metadata or {},
            )
            return trace_id

    def bind_determinism_digest(self, determinism_digest: str) -> None:
        """Bind the sealed determinism digest to the active trace."""
        with self._lock:
            if self._active_trace is None:
                raise RuntimeError("No active execution trace to bind digest to")
            self._active_trace = ExecutionTrace(
                trace_id=self._active_trace.trace_id,
                plan_hash=self._active_trace.plan_hash,
                policy_hash=self._active_trace.policy_hash,
                determinism_digest=determinism_digest,
                hierarchy_hash=self._active_trace.hierarchy_hash,
                metadata=self._active_trace.metadata,
            )

    def get_active_trace(self) -> ExecutionTrace | None:
        """Return the current active trace (None if not started)."""
        return self._active_trace

    def end_trace(self) -> None:
        """Clear the active execution trace."""
        with self._lock:
            self._active_trace = None


_execution_trace_manager = ExecutionTraceManager()


def get_execution_trace_manager() -> ExecutionTraceManager:
    """Return the global execution trace manager."""
    return _execution_trace_manager


def start_execution_trace(
    plan_hash: str,
    policy_hash: str,
    hierarchy_hash: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Start a new execution trace and return its trace_id."""
    return _execution_trace_manager.start_trace(plan_hash, policy_hash, hierarchy_hash, metadata)


def bind_determinism_to_trace(determinism_digest: str) -> None:
    """Bind the sealed determinism digest to the active trace."""
    _execution_trace_manager.bind_determinism_digest(determinism_digest)


def get_active_execution_trace() -> ExecutionTrace | None:
    """Return the current active execution trace."""
    return _execution_trace_manager.get_active_trace()
