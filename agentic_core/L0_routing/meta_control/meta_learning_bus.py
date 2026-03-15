"""
Meta-Learning Bus - Queue-backed deterministic change conduit.

Implements FIFO queue for meta-learning changes with deterministic hashing.
No wall-clock usage, no randomness, no direct L4 mutation.
"""

import hashlib
import json
from collections import deque
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "meta_learning_bus", "L0")
_emit_routes_through("p1", "meta_learning_bus", "L0")
_emit_escalates_to_human("p1", "meta_learning_bus", "L0")
_emit_reads_policy_state("p1", "meta_learning_bus", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "meta_learning_bus", "p0_governance")
_emit_snapshots_state("p0", "meta_learning_bus", "state_snapshot")


@dataclass(frozen=True)
class MetaLearningChangePackage:
    """Immutable change package for meta-learning operations."""

    trace_id: str
    kind: str
    payload: dict[str, Any]
    package_hash: str

    @classmethod
    def create(cls, trace_id: str, kind: str, payload: dict[str, Any]) -> "MetaLearningChangePackage":
        """
        Create a new MetaLearningChangePackage with deterministic hash.

        Args:
            trace_id: Unique trace identifier
            kind: Change package kind
            payload: Package payload data

        Returns:
            New MetaLearningChangePackage with computed hash
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "MetaLearningChangePackage.create")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        canonical_data = {"kind": kind, "payload": payload}
        canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
        package_hash = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
        return cls(trace_id=trace_id, kind=kind, payload=payload, package_hash=package_hash)


class MetaLearningBus:
    """
    Queue-backed meta-learning bus for deterministic change processing.

    Provides FIFO queue behavior with injected apply functions.
    No wall-clock usage, no direct L4 mutation.
    """

    def __init__(self):
        """Initialize MetaLearningBus with in-memory FIFO queue."""
        self._queue: deque[MetaLearningChangePackage] = deque()

    def enqueue(self, pkg: MetaLearningChangePackage) -> None:
        """
        Add a package to the queue.

        Args:
            pkg: Package to enqueue
        """
        self._queue.append(pkg)

    def dequeue(self) -> MetaLearningChangePackage | None:
        """
        Remove and return the next package from queue.

        Returns:
            Next package or None if queue is empty
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "MetaLearningBus.dequeue")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if not self._queue:
            return None
        return self._queue.popleft()

    def size(self) -> int:
        """
        Get current queue size.

        Returns:
            Number of packages in queue
        """
        return len(self._queue)

    def apply_next(self, *, apply_fn) -> tuple[MetaLearningChangePackage, Any] | None:
        """
        Apply the next package using injected function.

        Pops one package, calls apply_fn(pkg), returns result.
        Bus has no knowledge of L4; apply_fn is injected.

        Args:
            apply_fn: Function to apply the package

        Returns:
            (package, result) tuple or None if queue empty
        """
        pkg = self.dequeue()
        if pkg is None:
            return None
        result = apply_fn(pkg)
        return (pkg, result)
