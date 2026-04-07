"""
agentic_core/L4_state/authority/run_scoped_state_authority.py

RunScopedStateAuthority — P0-L4 gap remediation.

Single authoritative run-scoped state object governing all L4 reads,
writes, and memory. Replaces the fragmented 19-write-target pattern
(1,827 reads_from / 50 writes_to with no unification) identified by
ADG analysis. All L4 state access routes through this authority.

ADG edges emitted: stamps_work_contract, snapshots_state,
                   freezes_context, unfreezes_context
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.L4_state.utils.versioning.commit_versioned_state_transition import (
    ActorContext,
    MutationPayload,
    SnapshotPolicy,
    StateConflictError,
    StateContext,
    StateNamespaceError,
    StateVersionMissingError,
    commit_versioned_state_transition,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace,  # noqa: E402
    _emit_snapshots_state,
    _emit_writes_through,  # noqa: E402
)
from agentic_core.runtime.types.execution_trace import get_active_execution_trace

_emit_records_execution_trace("p0", "evidence", "run_scoped_state_authority")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace,
)

logger = logging.getLogger(__name__)
_WRITES_THROUGH_LOG = logging.getLogger("adg.writes_through")
_READS_LOG = logging.getLogger("adg.reads_runtime_state")


@dataclass(frozen=True)
class StateSnapshot:
    """Immutable point-in-time snapshot of the run-scoped state."""

    run_id: str
    trace_id: str
    snapshot_key: str
    keys: tuple[str, ...]
    value_hashes: dict[str, str]
    timestamp_monotonic: float
    frozen: bool

    @classmethod
    def capture(
        cls,
        run_id: str,
        trace_id: str,
        state: dict[str, Any],
        frozen: bool = False,
    ) -> StateSnapshot:
        ts = time.monotonic()
        value_hashes = {k: hashlib.sha256(repr(v).encode()).hexdigest()[:16] for k, v in state.items()}
        snap_payload = f"{run_id}:{trace_id}:{sorted(value_hashes.items())}:{ts:.6f}"
        snapshot_key = hashlib.sha256(snap_payload.encode()).hexdigest()[:24]
        return cls(
            run_id=run_id,
            trace_id=trace_id,
            snapshot_key=snapshot_key,
            keys=tuple(sorted(state.keys())),
            value_hashes=value_hashes,
            timestamp_monotonic=ts,
            frozen=frozen,
        )


@dataclass(frozen=True)
class WorkContract:
    """Immutable work contract stamped at run start."""

    run_id: str
    trace_id: str
    contract_hash: str
    task_description: str
    created_at: float

    @classmethod
    def stamp(cls, run_id: str, trace_id: str, task_description: str = "") -> WorkContract:
        ts = time.monotonic()
        payload = f"{run_id}:{trace_id}:{task_description}:{ts:.6f}"
        contract_hash = hashlib.sha256(payload.encode()).hexdigest()[:24]
        return cls(
            run_id=run_id,
            trace_id=trace_id,
            contract_hash=contract_hash,
            task_description=task_description,
            created_at=ts,
        )


class FrozenStateError(RuntimeError):
    """Raised when a write is attempted on a frozen state."""


class RunScopedStateAuthority:
    """Single authoritative state ledger for one execution run.

    All L4 state reads and writes must route through this authority.
    Provides freezing (critical section), snapshots, and a work contract
    anchoring the run identity.

    Usage::

        auth = RunScopedStateAuthority(run_id="run-abc")
        auth.stamp_work_contract("Summarise campaign brief")

        auth.write("context.prompt", prompt_text)
        value = auth.read("context.prompt")

        with auth.frozen_section():
            # no writes permitted inside
            result = read_only_operation()

        snap = auth.snapshot()
    """

    def __init__(self, run_id: str = "") -> None:
        self._run_id = run_id or f"run-{int(time.monotonic() * 1e6)}"
        self._state: dict[str, Any] = {}
        self._lock = threading.RLock()
        self._frozen = False
        self._work_contract: WorkContract | None = None
        self._snapshots: list[StateSnapshot] = []

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def is_frozen(self) -> bool:
        return self._frozen

    def _trace_id(self) -> str:
        active = get_active_execution_trace()
        return active.trace_id if active else "no-active-trace"

    def stamp_work_contract(self, task_description: str = "") -> WorkContract:
        """Stamp an immutable work contract anchoring this run's identity.

        Emits ``stamps_work_contract`` ADG edge.
        """
        with self._lock:
            if self._work_contract is not None:
                logger.warning("AUTHORITY work_contract already stamped for run=%s", self._run_id)
                return self._work_contract
            contract = WorkContract.stamp(self._run_id, self._trace_id(), task_description)
            self._work_contract = contract
            logger.info(
                "AUTHORITY stamps_work_contract run=%s contract_hash=%s",
                self._run_id,
                contract.contract_hash,
            )
            return contract

    def write(
        self,
        key: str,
        value: Any,
        *,
        actor_id: str = "",
        state_namespace: str = "",
        expected_previous_version: int = -1,
    ) -> None:
        """Write a value under ``key``.

        P2/L4: Routes through commit_versioned_state_transition() for mandatory
        versioning, conflict detection, and snapshot policy.
        Raises :class:`FrozenStateError` if the authority is currently frozen.
        Emits writes_through and state_transition_committed ADG edges.
        """
        _emit_writes_through(str(uuid.uuid4()), "RunScopedStateAuthority.write", "L4_STATE")
        with self._lock:
            if self._frozen:
                raise FrozenStateError(
                    f"RunScopedStateAuthority.write blocked: state is frozen (run={self._run_id}, key={key})",
                )
            old_value = self._state.get(key)

        # P2/L4: Mandatory versioned transition through commit_versioned_state_transition()
        namespace = state_namespace or f"run_scoped.{self._run_id}"
        try:
            state_ctx = StateContext.create(
                state_namespace=namespace,
                key=key,
                run_id=self._run_id,
                trace_id=self._trace_id(),
            )
            mutation = MutationPayload.create(
                key=key,
                old_value=old_value,
                new_value=value,
            )
            actor_ctx = ActorContext.create(
                actor_id=actor_id or "run_scoped_state_authority",
            )

            transition = commit_versioned_state_transition(
                state_context=state_ctx,
                mutation_payload=mutation,
                actor_context=actor_ctx,
                snapshot_policy=SnapshotPolicy.ON_STAGE_COMPLETION,
                stage_completion=True,  # Every write in scoped authority is a stage boundary
                expected_previous_version=expected_previous_version,
            )
        except (StateNamespaceError, StateVersionMissingError, StateConflictError) as exc:    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling    # guardian: Multiple exceptions (StateNamespaceError, StateVersionMissingError) need specific handling
            logger.error(
                "RUN_SCOPED_STATE_AUTHORITY commit_versioned_state_transition failed: %s (namespace=%s key=%s)",
                exc,
                namespace,
                key,
            )
            raise

        # Update internal state after successful transition
        with self._lock:
            self._state[key] = value
            logger.debug(
                "AUTHORITY write run=%s key=%s version=%d transition_id=%s",
                self._run_id,
                key,
                transition.new_version,
                transition.state_transition_id,
            )

        # P1/L4: emit writes_through ADG edge on every governed state write
        _WRITES_THROUGH_LOG.debug(
            "writes_through RUN_SCOPED_STATE_AUTHORITY key=%s run_id=%s version=%d transition_id=%s",
            key,
            self._run_id,
            transition.new_version,
            transition.state_transition_id,
        )

    def read(
        self,
        key: str,
        default: Any = None,
        *,
        state_namespace: str = "",
    ) -> Any:
        """Read a value by ``key`` (returns ``default`` if absent).

        P2/L4: Returns versioned state when state_namespace is provided.
        """
        if state_namespace:
            from agentic_core.L4_state.utils.versioning.commit_versioned_state_transition import (
                StateVersionMissingError,
                UnversionedStateError,
                read_versioned_state,
            )

            try:
                versioned = read_versioned_state(
                    state_namespace=state_namespace,
                    key=key,
                    run_id=self._run_id,
                    trace_id=self._trace_id(),
                    default=default,
                )
                _READS_LOG.debug(
                    "reads_runtime_state namespace=%s key=%s version=%d run_id=%s source_hash=%s",
                    state_namespace,
                    key,
                    versioned.state_version,
                    self._run_id,
                    versioned.source_hash,
                )
                return versioned.value
            except (StateVersionMissingError, UnversionedStateError) as exc:    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling    # guardian: Multiple exceptions (StateVersionMissingError, UnversionedStateError) need specific handling
                logger.warning(
                    "RUN_SCOPED_STATE_AUTHORITY versioned_read failed, falling back: %s (namespace=%s key=%s)",
                    exc,
                    state_namespace,
                    key,
                )
                # Fall through to legacy read

        # Legacy read path
        with self._lock:
            return self._state.get(key, default)

    def delete(self, key: str) -> None:
        """Remove ``key`` from state."""
        with self._lock:
            if self._frozen:
                raise FrozenStateError(
                    f"RunScopedStateAuthority.delete blocked: state is frozen (run={self._run_id}, key={key})",
                )
            self._state.pop(key, None)

    def keys(self) -> list[str]:
        with self._lock:
            return list(self._state.keys())

    def snapshot(self) -> StateSnapshot:
        """Capture an immutable snapshot of the current state.

        Emits ``snapshots_state`` ADG edge.
        """
        _emit_snapshots_state(str(uuid.uuid4()), "RunScopedStateAuthority.snapshot", "L4_STATE")
        with self._lock:
            snap = StateSnapshot.capture(
                self._run_id,
                self._trace_id(),
                self._state,
                frozen=self._frozen,
            )
            self._snapshots.append(snap)
            logger.debug(
                "AUTHORITY snapshots_state run=%s key=%s keys=%d",
                self._run_id,
                snap.snapshot_key,
                len(snap.keys),
            )
            return snap

    def freeze(self) -> None:
        """Freeze state — all writes blocked until ``unfreeze()``.

        Emits ``freezes_context`` ADG edge.
        """
        with self._lock:
            self._frozen = True
            logger.info("AUTHORITY freezes_context run=%s", self._run_id)

    def unfreeze(self) -> None:
        """Unfreeze state — writes permitted again.

        Emits ``unfreezes_context`` ADG edge.
        """
        with self._lock:
            self._frozen = False
            logger.info("AUTHORITY unfreezes_context run=%s", self._run_id)

    class frozen_section:
        """Context manager: freeze state for the duration of the block."""

        def __init__(self, authority: RunScopedStateAuthority) -> None:
            self._auth = authority

        def __enter__(self) -> RunScopedStateAuthority.frozen_section:
            self._auth.freeze()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
            self._auth.unfreeze()
            return False

    def frozen_critical_section(self) -> RunScopedStateAuthority.frozen_section:
        """Return a context manager that freezes state for a critical section."""
        return RunScopedStateAuthority.frozen_section(self)

    def work_contract(self) -> WorkContract | None:
        return self._work_contract

    def snapshot_history(self) -> list[StateSnapshot]:
        with self._lock:
            return list(self._snapshots)


_registry: dict[str, RunScopedStateAuthority] = {}
_registry_lock = threading.Lock()


def get_state_authority(run_id: str) -> RunScopedStateAuthority:
    """Get or create a :class:`RunScopedStateAuthority` for ``run_id``."""
    with _registry_lock:
        if run_id not in _registry:
            _registry[run_id] = RunScopedStateAuthority(run_id=run_id)
        return _registry[run_id]


def release_state_authority(run_id: str) -> None:
    """Release the authority for ``run_id`` (call at run end)."""
    with _registry_lock:
        _registry.pop(run_id, None)


def active_run_ids() -> list[str]:
    with _registry_lock:
        return list(_registry.keys())


__all__ = [
    "StateSnapshot",
    "WorkContract",
    "FrozenStateError",
    "RunScopedStateAuthority",
    "get_state_authority",
    "release_state_authority",
    "active_run_ids",
]
