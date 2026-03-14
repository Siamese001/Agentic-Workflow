"""
Wave 6: RunStateAuthority — unified runtime state facade.

Single ledger facade for all runtime state reads and writes. Closes L4 P0
(Unified Runtime State Authority) by routing:

  - All ``reads_runtime_state`` through ``RunStateAuthority.read()``
  - All ``writes_through`` (Wave 1 UWG) committed via ``RunStateAuthority.commit()``
  - Versioned log of state changes per run ID

Starts as a pass-through facade with zero semantic change. Existing state stores
(Redis, runtime_state.json, semantic_cache) are delegated to via ``_backend``
adapters. Full migration replaces direct store access one L3 orchestrator at a time.

ADG edges emitted (structured log records):
  ``observes_runtime_state``  — every RunStateAuthority.read() call
  ``snapshots_state``         — every RunStateAuthority.snapshot()
  ``reads_runtime_state``     — aliased by read() for backward compatibility

Version vectors
---------------
Every ``commit()`` increments the version for that key. ``read()`` returns the
value along with the version at time of read, enabling conflict detection for
concurrent orchestration runs.

Usage — facade (zero behaviour change)::

    from agentic_core.L4_state.authority.run_state_authority import get_run_state_authority

    rsa = get_run_state_authority()
    value, version = rsa.read("my_key")
    rsa.commit("my_key", new_value, run_id="run-001")

Usage — scoped to a run (recommended for L3 orchestrators)::

    with rsa.run_scope("run-001") as scope:
        scope.commit("phase", "wave6")
        scope.snapshot("checkpoint_1")
        v, ver = scope.read("phase")
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Generator

logger = logging.getLogger(__name__)
_OBSERVE_LOGGER = logging.getLogger("adg.observes_runtime_state")
_SNAPSHOT_LOGGER = logging.getLogger("adg.snapshots_state")
_READS_LOGGER = logging.getLogger("adg.reads_runtime_state")


@dataclass
class StateVersion:
    """Versioned state value for conflict detection."""

    key: str
    value: Any
    version: int
    run_id: str
    content_hash: str

    @classmethod
    def build(cls, key: str, value: Any, version: int, run_id: str) -> StateVersion:
        payload = json.dumps({"key": key, "value": value, "version": version, "run_id": run_id},
                             sort_keys=True, default=str)
        return cls(
            key=key,
            value=value,
            version=version,
            run_id=run_id,
            content_hash=hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16],
        )


@dataclass
class StateSnapshot:
    """Point-in-time snapshot of all state managed by a RunStateAuthority."""

    run_id: str
    label: str
    version_vectors: dict[str, int]
    state: dict[str, Any]
    content_hash: str

    @classmethod
    def build(cls, run_id: str, label: str, state: dict[str, Any],
              version_vectors: dict[str, int]) -> StateSnapshot:
        payload = json.dumps(
            {"run_id": run_id, "label": label, "state": state, "versions": version_vectors},
            sort_keys=True, default=str,
        )
        return cls(
            run_id=run_id,
            label=label,
            version_vectors=dict(version_vectors),
            state=dict(state),
            content_hash=hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16],
        )


class RunStateAuthority:
    """Unified runtime state authority — single ledger facade for L4 state.

    Thread-safe. All reads and writes are versioned and logged.
    Snapshots are append-only; state is mutable per commit.
    """

    def __init__(self, run_id: str = "", backend: Any = None) -> None:
        """
        Args:
            run_id: The run this authority is scoped to (optional for process-level).
            backend: Optional existing state store to delegate reads to on cache miss.
        """
        self.run_id = run_id
        self._backend = backend
        self._state: dict[str, Any] = {}
        self._versions: dict[str, int] = {}
        self._ledger: list[StateVersion] = []
        self._snapshots: list[StateSnapshot] = []
        self._lock = threading.RLock()

    def read(self, key: str, default: Any = None) -> tuple[Any, int]:
        """Read a state value and its version.

        ADG edges: ``reads_runtime_state``, ``observes_runtime_state``.

        Returns:
            ``(value, version)`` — version is 0 if key has never been written.
        """
        with self._lock:
            if key in self._state:
                value = self._state[key]
                version = self._versions.get(key, 0)
            else:
                value = self._backend_read(key, default)
                version = 0

        _READS_LOGGER.debug(
            "reads_runtime_state key=%s version=%d run_id=%s",
            key, version, self.run_id,
        )
        _OBSERVE_LOGGER.debug(
            "observes_runtime_state key=%s version=%d run_id=%s",
            key, version, self.run_id,
        )
        return value, version

    def commit(self, key: str, value: Any, run_id: str = "") -> StateVersion:
        """Write a state value, incrementing its version.

        Returns the new ``StateVersion`` record.
        """
        effective_run_id = run_id or self.run_id
        with self._lock:
            new_version = self._versions.get(key, 0) + 1
            self._state[key] = value
            self._versions[key] = new_version
            sv = StateVersion.build(key=key, value=value, version=new_version, run_id=effective_run_id)
            self._ledger.append(sv)

        logger.debug(
            "RUN_STATE_AUTHORITY commit key=%s version=%d run_id=%s hash=%s",
            key, new_version, effective_run_id, sv.content_hash,
        )
        return sv

    def snapshot(self, label: str, run_id: str = "") -> StateSnapshot:
        """Capture a point-in-time snapshot of all managed state.

        ADG edge: ``snapshots_state``.
        """
        effective_run_id = run_id or self.run_id
        with self._lock:
            snap = StateSnapshot.build(
                run_id=effective_run_id,
                label=label,
                state=dict(self._state),
                version_vectors=dict(self._versions),
            )
            self._snapshots.append(snap)

        _SNAPSHOT_LOGGER.debug(
            "snapshots_state run_id=%s label=%s keys=%d hash=%s",
            effective_run_id, label, len(snap.state), snap.content_hash,
        )
        return snap

    def get_version(self, key: str) -> int:
        """Return the current version for ``key`` (0 if never written)."""
        with self._lock:
            return self._versions.get(key, 0)

    def detect_conflict(self, key: str, expected_version: int) -> bool:
        """Return True if current version differs from ``expected_version``."""
        return self.get_version(key) != expected_version

    def ledger(self) -> list[StateVersion]:
        """Return append-only copy of the commit ledger."""
        with self._lock:
            return list(self._ledger)

    def snapshots(self) -> list[StateSnapshot]:
        """Return append-only copy of all snapshots."""
        with self._lock:
            return list(self._snapshots)

    def get_stats(self) -> dict[str, Any]:
        """Return statistics for monitoring and CI gate verification."""
        with self._lock:
            return {
                "run_id": self.run_id,
                "managed_keys": sorted(self._state.keys()),
                "total_commits": len(self._ledger),
                "total_snapshots": len(self._snapshots),
                "version_vectors": dict(self._versions),
            }

    def _backend_read(self, key: str, default: Any) -> Any:
        """Delegate to backend store on cache miss."""
        if self._backend is not None and hasattr(self._backend, "get"):
            try:
                result = self._backend.get(key)
                if result is not None:
                    return result
            except Exception as exc:
                logger.debug("RUN_STATE_AUTHORITY backend_read failed key=%s: %s", key, exc)
        return default

    @contextmanager
    def run_scope(self, run_id: str) -> Generator[RunStateAuthority, None, None]:
        """Return a child RunStateAuthority scoped to a specific run_id.

        The child shares the parent's backend but has its own state ledger.
        On exit, snapshots are promoted back to the parent's snapshot list.
        """
        child = RunStateAuthority(run_id=run_id, backend=self._backend)
        try:
            yield child
        finally:
            with self._lock:
                self._snapshots.extend(child._snapshots)
            if child._snapshots:
                _SNAPSHOT_LOGGER.debug(
                    "snapshots_state run_scope_exit run_id=%s promoted_snapshots=%d",
                    run_id, len(child._snapshots),
                )


# ---------------------------------------------------------------------------
# Process-level singleton
# ---------------------------------------------------------------------------

_global_rsa: RunStateAuthority | None = None
_global_rsa_lock = threading.Lock()


def get_run_state_authority() -> RunStateAuthority:
    """Return the process-level RunStateAuthority singleton."""
    global _global_rsa
    if _global_rsa is None:
        with _global_rsa_lock:
            if _global_rsa is None:
                _global_rsa = RunStateAuthority(run_id="__process__")
    return _global_rsa


def reset_run_state_authority() -> None:
    """Reset the singleton (for testing)."""
    global _global_rsa
    _global_rsa = None


__all__ = [
    "RunStateAuthority",
    "StateVersion",
    "StateSnapshot",
    "get_run_state_authority",
    "reset_run_state_authority",
]
