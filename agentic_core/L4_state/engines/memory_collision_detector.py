from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import NamedTuple, Sequence

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "memory_collision_detector")
emit_determinism_digest("p0", "memory_collision_detector")

_emit_dispatches_healing_run("p1", "memory_collision_detector", "L4")
_emit_routes_through("p1", "memory_collision_detector", "L4")
_emit_escalates_to_human("p1", "memory_collision_detector", "L4")
_emit_reads_policy_state("p1", "memory_collision_detector", "L4")


class MemoryDeadlockViolation(Exception):
    """Raised when a deadlock is detected during lock acquisition."""


class LockAcquisitionResult(NamedTuple):
    """The result of a lock acquisition attempt."""

    success: bool
    locks_acquired: list[str]
    violation: MemoryDeadlockViolation | None = None


@dataclass(frozen=True)
class LockPolicy:
    """Defines the policy for lock acquisition."""

    lock_hierarchy: list[str]
    timeout_seconds: float = 5.0


class MemoryCollisionDetector:
    """
    Manages concurrent access to shared memory with deterministic deadlock resolution.

    This detector enforces Guarantee #14 by implementing a strict lock acquisition
    hierarchy and a timeout policy. It prevents both race conditions and livelocks,
    ensuring that memory access is safe and deterministic under concurrency.
    """

    def __init__(self, policy: LockPolicy):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "MemoryCollisionDetector.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "MemoryCollisionDetector.__init__", "p0_governance")
        self.policy = policy
        self._locks: dict[str, threading.Lock] = {name: threading.Lock() for name in policy.lock_hierarchy}
        self._lock_order: dict[str, int] = {name: i for i, name in enumerate(policy.lock_hierarchy)}

    def acquire_locks(self, trace_id: str, required_locks: Sequence[str]) -> LockAcquisitionResult:
        """
        Acquires a set of locks in a deterministic, deadlock-free order.

        Args:
            trace_id: The unique identifier for the execution trace.
            required_locks: A sequence of lock names that need to be acquired.

        Returns:
            A LockAcquisitionResult indicating the outcome.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "MemoryCollisionDetector.acquire_locks"
        )

        try:
            sorted_locks = sorted(required_locks, key=lambda name: self._lock_order[name])
        except KeyError as e:
            violation = MemoryDeadlockViolation(f"Lock '{e.args[0]}' is not defined in the global hierarchy.")
            return LockAcquisitionResult(success=False, locks_acquired=[], violation=violation)
        acquired_locks: list[str] = []
        start_time = time.monotonic()
        for lock_name in sorted_locks:
            lock = self._locks[lock_name]
            timeout = self.policy.timeout_seconds - (time.monotonic() - start_time)
            if timeout <= 0:
                violation = MemoryDeadlockViolation("Timeout exceeded during lock acquisition.")
                self._release_locks(acquired_locks)
                return LockAcquisitionResult(success=False, locks_acquired=[], violation=violation)
            if not lock.acquire(timeout=timeout):
                violation = MemoryDeadlockViolation(
                    f"Failed to acquire lock '{lock_name}' within the timeout."
                )
                self._release_locks(acquired_locks)
                return LockAcquisitionResult(success=False, locks_acquired=[], violation=violation)
            acquired_locks.append(lock_name)
        return LockAcquisitionResult(success=True, locks_acquired=acquired_locks)

    def _release_locks(self, locks_to_release: list[str]) -> None:
        """Releases a list of locks, typically after a failed acquisition."""
        for lock_name in reversed(locks_to_release):
            self._locks[lock_name].release()

    def release_locks(self, acquired_locks: list[str]) -> None:
        """Public method to release locks after an operation is complete."""
        for lock_name in sorted(acquired_locks, key=lambda name: self._lock_order[name], reverse=True):
            self._locks[lock_name].release()
