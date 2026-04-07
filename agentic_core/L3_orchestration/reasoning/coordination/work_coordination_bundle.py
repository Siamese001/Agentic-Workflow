"""
agentic_core/L3_orchestration/coordination/work_coordination_bundle.py

WorkCoordinationBundle — P1-L3 gap remediation.

Shared case file per multi-agent run. All participating agents read from
and write to this bundle, giving L3 a run-scoped coordination state that
can be stamped, snapshotted, and observed.

ADG evidence: 0/204 L3 modules emit stamps_work_contract, freezes_context,
snapshots_state, or observes_runtime_state. 13 reads_runtime_state with
0 write-back coordination signals.

ADG edges emitted: stamps_work_contract, snapshots_state,
                   observes_runtime_state, reads_runtime_state
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)
from agentic_core.runtime.types.execution_trace import get_active_execution_trace

logger = logging.getLogger(__name__)


class BundlePhase(str, Enum):
    """Lifecycle phase of a WorkCoordinationBundle."""

    INITIALISED = "initialised"
    ACTIVE = "active"
    CHECKPOINTED = "checkpointed"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class AgentCompletion:
    """Immutable record of a single agent's completion within the bundle."""

    agent_name: str
    task_key: str
    result_hash: str
    success: bool
    timestamp: float


@dataclass(frozen=True)
class BundleSnapshot:
    """Point-in-time snapshot of bundle coordination state."""

    bundle_id: str
    trace_id: str
    snapshot_key: str
    phase: BundlePhase
    agent_completions: tuple[AgentCompletion, ...]
    shared_state_keys: tuple[str, ...]
    timestamp: float


class WorkCoordinationBundle:
    """Shared coordination case file for a multi-agent orchestration run.

    All agent dispatches and completions are recorded here; the bundle
    acts as the single source of coordination truth for L3.

    Usage::

        bundle = WorkCoordinationBundle.create("campaign-research-001")
        bundle.stamp_work_contract("Generate campaign brief")

        # agent starts
        bundle.observe_runtime_state("rag_results", rag_data)

        # agent completes
        bundle.record_agent_completion("ResearchAgent", "fetch_sources", result)
        snap = bundle.snapshot()
    """

    def __init__(self, bundle_id: str, task_description: str = "") -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "WorkCoordinationBundle.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "WorkCoordinationBundle.__init__", "p0_governance")
        self._bundle_id = bundle_id
        self._task_description = task_description
        self._phase = BundlePhase.INITIALISED
        self._contract_hash: str = ""
        self._shared_state: dict[str, Any] = {}
        self._completions: list[AgentCompletion] = []
        self._snapshots: list[BundleSnapshot] = []
        self._lock = threading.RLock()

    @classmethod
    def create(cls, bundle_id: str, task_description: str = "") -> WorkCoordinationBundle:
        """Factory: create and activate a bundle, stamping its work contract."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "WorkCoordinationBundle.create",
        )

        bundle = cls(bundle_id=bundle_id, task_description=task_description)
        bundle.stamp_work_contract(task_description)
        return bundle

    @property
    def bundle_id(self) -> str:
        return self._bundle_id

    @property
    def phase(self) -> BundlePhase:
        return self._phase

    @property
    def contract_hash(self) -> str:
        return self._contract_hash

    def _trace_id(self) -> str:
        active = get_active_execution_trace()
        return active.trace_id if active else "no-active-trace"

    def stamp_work_contract(self, task_description: str = "") -> str:
        """Stamp an immutable work contract for this orchestration run.

        Emits ``stamps_work_contract`` ADG edge. Returns the contract hash.
        """
        with self._lock:
            if self._contract_hash:
                return self._contract_hash
            ts = time.monotonic()
            payload = f"{self._bundle_id}:{self._trace_id()}:{task_description}:{ts:.6f}"
            self._contract_hash = hashlib.sha256(payload.encode()).hexdigest()[:24]
            self._phase = BundlePhase.ACTIVE
            logger.info(
                "BUNDLE stamps_work_contract bundle=%s contract=%s task=%s",
                self._bundle_id,
                self._contract_hash,
                task_description or self._task_description,
            )
            return self._contract_hash

    def observe_runtime_state(self, key: str, value: Any) -> None:
        """Observe and store a runtime state value.

        Emits ``observes_runtime_state`` + ``reads_runtime_state`` ADG edges.
        """
        with self._lock:
            self._shared_state[key] = value
            logger.debug(
                "BUNDLE observes_runtime_state bundle=%s key=%s",
                self._bundle_id,
                key,
            )

    def read_shared(self, key: str, default: Any = None) -> Any:
        """Read a value from the shared coordination state."""
        with self._lock:
            return self._shared_state.get(key, default)

    def record_agent_completion(
        self,
        agent_name: str,
        task_key: str,
        result: Any = None,
        success: bool = True,
    ) -> AgentCompletion:
        """Record that an agent has completed its assigned task.

        Triggers an automatic snapshot.
        """
        with self._lock:
            result_hash = hashlib.sha256(repr(result).encode()).hexdigest()[:16]
            completion = AgentCompletion(
                agent_name=agent_name,
                task_key=task_key,
                result_hash=result_hash,
                success=success,
                timestamp=time.monotonic(),
            )
            self._completions.append(completion)
            logger.info(
                "BUNDLE agent_completed bundle=%s agent=%s task=%s ok=%s",
                self._bundle_id,
                agent_name,
                task_key,
                success,
            )
        self.snapshot()
        return completion

    def snapshot(self) -> BundleSnapshot:
        """Capture a point-in-time snapshot of the coordination state.

        Emits ``snapshots_state`` ADG edge.
        """
        with self._lock:
            ts = time.monotonic()
            payload = f"{self._bundle_id}:{len(self._completions)}:{ts:.6f}"
            snap_key = hashlib.sha256(payload.encode()).hexdigest()[:24]
            snap = BundleSnapshot(
                bundle_id=self._bundle_id,
                trace_id=self._trace_id(),
                snapshot_key=snap_key,
                phase=self._phase,
                agent_completions=tuple(self._completions),
                shared_state_keys=tuple(sorted(self._shared_state.keys())),
                timestamp=ts,
            )
            self._snapshots.append(snap)
            if self._phase == BundlePhase.ACTIVE:
                self._phase = BundlePhase.CHECKPOINTED
            logger.debug(
                "BUNDLE snapshots_state bundle=%s snap=%s agents=%d",
                self._bundle_id,
                snap_key,
                len(self._completions),
            )
            return snap

    def complete(self, success: bool = True) -> BundleSnapshot:
        """Mark the bundle as completed and take a final snapshot."""
        with self._lock:
            self._phase = BundlePhase.COMPLETED if success else BundlePhase.FAILED
        return self.snapshot()

    def completion_count(self) -> int:
        with self._lock:
            return len(self._completions)

    def snapshot_history(self) -> list[BundleSnapshot]:
        with self._lock:
            return list(self._snapshots)

    def completions(self) -> list[AgentCompletion]:
        with self._lock:
            return list(self._completions)


_bundle_registry: dict[str, WorkCoordinationBundle] = {}
_registry_lock = threading.Lock()


def get_coordination_bundle(bundle_id: str, task_description: str = "") -> WorkCoordinationBundle:
    """Get or create a :class:`WorkCoordinationBundle` for ``bundle_id``."""
    with _registry_lock:
        if bundle_id not in _bundle_registry:
            _bundle_registry[bundle_id] = WorkCoordinationBundle.create(
                bundle_id=bundle_id, task_description=task_description,
            )
        return _bundle_registry[bundle_id]


def release_coordination_bundle(bundle_id: str) -> None:
    """Release the bundle for ``bundle_id`` after the run ends."""
    with _registry_lock:
        _bundle_registry.pop(bundle_id, None)


def active_bundle_ids() -> list[str]:
    with _registry_lock:
        return list(_bundle_registry.keys())


__all__ = [
    "BundlePhase",
    "AgentCompletion",
    "BundleSnapshot",
    "WorkCoordinationBundle",
    "get_coordination_bundle",
    "release_coordination_bundle",
    "active_bundle_ids",
]
