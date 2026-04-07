"""
agentic_core/L4_state/authority/memory_authority.py

MemoryAuthority — P1/L4 unified memory write governance facade.

All mutable memory operations MUST pass through MemoryAuthority.
Direct writes to mutable memory stores are prohibited.

Write-through discipline:
    MemoryAuthority -> RunStateAuthority/UWG -> durable store

Namespaces:
    runtime_state, semantic_memory, orchestration_memory,
    reasoning_context_memory, cache_backed_mutation, long_term_memory

MemoryWriteRecord (8 required fields per spec §3):
    memory_write_id, run_id, memory_namespace, previous_version,
    new_version, mutation_hash, trace_id, policy_hash

ADG edges emitted:
    writes_through        — every governed mutable write
    reads_runtime_state   — every governed read
    snapshots_state       — every snapshot call
    observes_runtime_state — every observe call
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L2_execution.utils.providers import get_clock
from agentic_core.L4_state.enforcement.authority.run_state_authority import (
    RunStateAuthority,
    get_run_state_authority,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

logger = logging.getLogger(__name__)
_WRITES_THROUGH_LOG = logging.getLogger("adg.writes_through")
_READS_LOG = logging.getLogger("adg.reads_runtime_state")
_SNAPSHOT_LOG = logging.getLogger("adg.snapshots_state")
_OBSERVE_LOG = logging.getLogger("adg.observes_runtime_state")


# ---------------------------------------------------------------------------
# Namespace definitions
# ---------------------------------------------------------------------------


class MemoryNamespace(str, Enum):
    """All recognized memory namespaces for MemoryAuthority."""

    RUNTIME_STATE = "runtime_state"
    SEMANTIC_MEMORY = "semantic_memory"
    ORCHESTRATION_MEMORY = "orchestration_memory"
    REASONING_CONTEXT_MEMORY = "reasoning_context_memory"
    CACHE_BACKED_MUTATION = "cache_backed_mutation"
    LONG_TERM_MEMORY = "long_term_memory"


@dataclass(frozen=True)
class NamespacePolicy:
    """Version, retention, and mutation policy for a memory namespace."""

    namespace: MemoryNamespace
    version_policy: str  # "increment" | "pinned" | "monotonic"
    retention_policy: str  # "run_scoped" | "session" | "persistent"
    mutation_policy: str  # "governed" | "append_only" | "immutable"
    requires_durable_ledger: bool = True
    allows_cache: bool = True


_NAMESPACE_POLICIES: dict[MemoryNamespace, NamespacePolicy] = {
    MemoryNamespace.RUNTIME_STATE: NamespacePolicy(
        namespace=MemoryNamespace.RUNTIME_STATE,
        version_policy="increment",
        retention_policy="run_scoped",
        mutation_policy="governed",
        requires_durable_ledger=True,
        allows_cache=True,
    ),
    MemoryNamespace.SEMANTIC_MEMORY: NamespacePolicy(
        namespace=MemoryNamespace.SEMANTIC_MEMORY,
        version_policy="increment",
        retention_policy="session",
        mutation_policy="governed",
        requires_durable_ledger=True,
        allows_cache=True,
    ),
    MemoryNamespace.ORCHESTRATION_MEMORY: NamespacePolicy(
        namespace=MemoryNamespace.ORCHESTRATION_MEMORY,
        version_policy="increment",
        retention_policy="run_scoped",
        mutation_policy="governed",
        requires_durable_ledger=True,
        allows_cache=False,
    ),
    MemoryNamespace.REASONING_CONTEXT_MEMORY: NamespacePolicy(
        namespace=MemoryNamespace.REASONING_CONTEXT_MEMORY,
        version_policy="monotonic",
        retention_policy="session",
        mutation_policy="append_only",
        requires_durable_ledger=True,
        allows_cache=True,
    ),
    MemoryNamespace.CACHE_BACKED_MUTATION: NamespacePolicy(
        namespace=MemoryNamespace.CACHE_BACKED_MUTATION,
        version_policy="increment",
        retention_policy="session",
        mutation_policy="governed",
        requires_durable_ledger=True,  # must bind to ledger before cache write
        allows_cache=True,
    ),
    MemoryNamespace.LONG_TERM_MEMORY: NamespacePolicy(
        namespace=MemoryNamespace.LONG_TERM_MEMORY,
        version_policy="increment",
        retention_policy="persistent",
        mutation_policy="governed",
        requires_durable_ledger=True,
        allows_cache=False,
    ),
}


def get_namespace_policy(ns: MemoryNamespace) -> NamespacePolicy:
    return _NAMESPACE_POLICIES[ns]


# ---------------------------------------------------------------------------
# MemoryWriteRecord — 8 required spec fields
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MemoryWriteRecord:
    """Immutable record of one governed memory write (P1/L4 spec §3)."""

    memory_write_id: str
    run_id: str
    memory_namespace: str
    previous_version: int
    new_version: int
    mutation_hash: str
    trace_id: str
    policy_hash: str

    key: str = ""
    actor_id: str = ""
    created_tick: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        run_id: str,
        namespace: MemoryNamespace,
        key: str,
        value: Any,
        previous_version: int,
        new_version: int,
        trace_id: str = "",
        policy_hash: str = "",
        actor_id: str = "",
    ) -> MemoryWriteRecord:
        write_id = str(uuid.uuid4())[:16]
        payload = json.dumps(
            {
                "run_id": run_id,
                "namespace": namespace.value,
                "key": key,
                "value": value,
                "v_from": previous_version,
                "v_to": new_version,
            },
            sort_keys=True,
            default=str,
        )
        mutation_hash = hashlib.sha256(payload.encode()).hexdigest()[:16]
        return cls(
            memory_write_id=write_id,
            run_id=run_id,
            memory_namespace=namespace.value,
            previous_version=previous_version,
            new_version=new_version,
            mutation_hash=mutation_hash,
            trace_id=trace_id,
            policy_hash=policy_hash,
            key=key,
            actor_id=actor_id,
        )


# ---------------------------------------------------------------------------
# MemoryReadResult — version binding per spec §6
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MemoryReadResult:
    """Result of a governed memory read (P1/L4 spec §6)."""

    key: str
    value: Any
    memory_version: int
    namespace: str
    source_hash: str


# ---------------------------------------------------------------------------
# Direct-write bypass error
# ---------------------------------------------------------------------------


class DirectMemoryWriteError(PermissionError):
    """Raised when a direct mutable write bypasses MemoryAuthority."""


class UnclassifiedNamespaceError(ValueError):
    """Raised when a write lacks a valid namespace classification."""


# ---------------------------------------------------------------------------
# MemoryAuthority facade
# ---------------------------------------------------------------------------


class MemoryAuthority:
    """Unified memory write governance facade — P1/L4 spec.

    All mutable memory writes flow through write().
    Read-through cache is allowed; write-through side channels are prohibited.

    Write chain:
        MemoryAuthority.write() -> RunStateAuthority.commit() -> durable store
    """

    def __init__(
        self,
        run_id: str = "",
        run_state_authority: RunStateAuthority | None = None,
        policy_hash: str = "default",
    ) -> None:
        self.run_id = run_id
        self._rsa = run_state_authority or get_run_state_authority()
        self.policy_hash = policy_hash
        self._write_records: list[MemoryWriteRecord] = []
        self._version_map: dict[str, int] = {}
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Mandatory entrypoints per spec §2
    # ------------------------------------------------------------------

    def read(
        self,
        key: str,
        namespace: MemoryNamespace = MemoryNamespace.RUNTIME_STATE,
        default: Any = None,
    ) -> MemoryReadResult:
        """Governed memory read — returns value + version + namespace + source_hash.

        ADG edge: reads_runtime_state, observes_runtime_state.
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"MemoryAuthority.read:{namespace.value}:{key}",
        )
        value, version = self._rsa.read(key, default)
        source_hash = hashlib.sha256(repr(value).encode()).hexdigest()[:16]
        _READS_LOG.debug(
            "reads_runtime_state MEMORY_AUTHORITY key=%s ns=%s version=%d run_id=%s",
            key,
            namespace.value,
            version,
            self.run_id,
        )
        _OBSERVE_LOG.debug(
            "observes_runtime_state MEMORY_AUTHORITY read key=%s ns=%s version=%d run_id=%s",
            key,
            namespace.value,
            version,
            self.run_id,
        )
        return MemoryReadResult(
            key=key,
            value=value,
            memory_version=version,
            namespace=namespace.value,
            source_hash=source_hash,
        )

    def write(
        self,
        key: str,
        value: Any,
        namespace: MemoryNamespace,
        run_id: str = "",
        actor_id: str = "",
        trace_id: str = "",
        policy_hash: str = "",
    ) -> MemoryWriteRecord:
        """Mandatory governed write entrypoint.

        All mutable memory writes MUST call this method.
        Produces MemoryWriteRecord with 8 required fields.
        Emits writes_through ADG edge.

        Write chain: MemoryAuthority -> RunStateAuthority.commit() -> durable store.

        Raises:
            UnclassifiedNamespaceError: if namespace is invalid.
        """
        if not isinstance(namespace, MemoryNamespace):
            raise UnclassifiedNamespaceError(
                f"MemoryAuthority.write: namespace must be a MemoryNamespace enum value, "
                f"got {type(namespace).__name__!r} for key={key!r}",
            )

        effective_run_id = run_id or self.run_id
        effective_policy = policy_hash or self.policy_hash

        with self._lock:
            prev_version = self._version_map.get(key, 0)
            new_version = prev_version + 1
            self._version_map[key] = new_version

        # Resolve trace_id from active trace if not provided
        if not trace_id:
            try:
                from agentic_core.runtime.types.execution_trace import (
                    get_active_execution_trace,  # noqa: PLC0415
                )

                _at = get_active_execution_trace()
                trace_id = _at.trace_id if _at else ""
            except (ValueError, TypeError, RuntimeError) as e:
                trace_id = ""

        write_record = MemoryWriteRecord.create(
            run_id=effective_run_id,
            namespace=namespace,
            key=key,
            value=value,
            previous_version=prev_version,
            new_version=new_version,
            trace_id=trace_id,
            policy_hash=effective_policy,
            actor_id=actor_id,
        )

        with self._lock:
            self._write_records.append(write_record)

        self._rsa.snapshot_state(f"memory_write:{namespace.value}:{key}", run_id=effective_run_id)

        # Write-through: delegate to RunStateAuthority (durable ledger)
        self._rsa.commit(
            key=f"{namespace.value}:{key}",
            value=value,
            run_id=effective_run_id,
            actor_id=actor_id or "memory_authority",
            policy_hash=effective_policy,
            trace_id=trace_id,
        )

        # Emit writes_through ADG edge
        _WRITES_THROUGH_LOG.debug(
            "writes_through MEMORY_AUTHORITY key=%s ns=%s v_from=%d v_to=%d "
            "run_id=%s write_id=%s mutation_hash=%s",
            key,
            namespace.value,
            prev_version,
            new_version,
            effective_run_id,
            write_record.memory_write_id,
            write_record.mutation_hash,
        )
        logger.debug(
            "MEMORY_AUTHORITY write key=%s ns=%s version=%d run_id=%s",
            key,
            namespace.value,
            new_version,
            effective_run_id,
        )
        return write_record

    def observe(
        self,
        context: str,
        namespace: MemoryNamespace = MemoryNamespace.RUNTIME_STATE,
        stage: str = "",
        actor_id: str = "",
    ) -> None:
        """Emit observes_runtime_state signal for the given context.

        ADG edge: observes_runtime_state.
        """
        self._rsa.observe(context, stage=stage, actor_id=actor_id)
        _OBSERVE_LOG.debug(
            "observes_runtime_state MEMORY_AUTHORITY context=%s ns=%s stage=%s run_id=%s",
            context,
            namespace.value,
            stage,
            self.run_id,
        )

    def version(
        self,
        key: str,
        namespace: MemoryNamespace = MemoryNamespace.RUNTIME_STATE,
    ) -> int:
        """Return the current MemoryAuthority-local version for key.

        Does NOT emit ADG edges (read-only metadata query).
        """
        with self._lock:
            return self._version_map.get(key, 0)

    def snapshot(
        self,
        label: str,
        run_id: str = "",
    ) -> dict[str, Any]:
        """Capture a snapshot of current memory state.

        ADG edge: snapshots_state.
        """
        _emit_snapshots_state(str(uuid.uuid4()), "MemoryAuthority.snapshot", "L4_STATE")
        effective_run_id = run_id or self.run_id
        snap = self._rsa.snapshot(label, run_id=effective_run_id)
        _SNAPSHOT_LOG.debug(
            "snapshots_state MEMORY_AUTHORITY label=%s run_id=%s keys=%d hash=%s",
            label,
            effective_run_id,
            len(snap.state),
            snap.content_hash,
        )
        return {
            "run_id": snap.run_id,
            "label": snap.label,
            "version_vectors": snap.version_vectors,
            "content_hash": snap.content_hash,
            "memory_authority_versions": dict(self._version_map),
        }

    # ------------------------------------------------------------------
    # Audit / read-only views
    # ------------------------------------------------------------------

    def write_records(self) -> list[MemoryWriteRecord]:
        with self._lock:
            return list(self._write_records)

    def namespace_policy(self, ns: MemoryNamespace) -> NamespacePolicy:
        return get_namespace_policy(ns)

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            ns_counts: dict[str, int] = {}
            for r in self._write_records:
                ns_counts[r.memory_namespace] = ns_counts.get(r.memory_namespace, 0) + 1
            return {
                "run_id": self.run_id,
                "total_writes": len(self._write_records),
                "writes_by_namespace": ns_counts,
                "tracked_keys": len(self._version_map),
            }


# ---------------------------------------------------------------------------
# Process-level singleton
# ---------------------------------------------------------------------------

_global_ma: MemoryAuthority | None = None
_global_ma_lock = threading.Lock()


def get_memory_authority(run_id: str = "", policy_hash: str = "default") -> MemoryAuthority:
    """Return the process-level MemoryAuthority singleton."""
    global _global_ma
    if _global_ma is None:
        with _global_ma_lock:
            if _global_ma is None:
                _global_ma = MemoryAuthority(
                    run_id=run_id or "__process__",
                    policy_hash=policy_hash,
                )
    return _global_ma


def reset_memory_authority() -> None:
    """Reset the singleton (for testing)."""
    global _global_ma
    _global_ma = None


__all__ = [
    "MemoryAuthority",
    "MemoryWriteRecord",
    "MemoryReadResult",
    "MemoryNamespace",
    "NamespacePolicy",
    "get_memory_authority",
    "reset_memory_authority",
    "get_namespace_policy",
    "DirectMemoryWriteError",
    "UnclassifiedNamespaceError",
]
