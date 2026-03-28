"""Runtime ADG store — persists and queries RuntimeADGSnapshots via L4.

Uses FileBackedVersionStore (content-addressable) as the persistence backend.
Integrates with L4 sovereign territory for runtime ADG storage.
No new storage subsystem. InMemoryRuntimeADGStore is provided for tests.

Idempotency: committing the same snapshot twice returns the same version_id.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    L4_APPROVED_FOLDERS,
    get_validated_project_root,
)
from system_learning.runtime_adg.snapshot import (
    RuntimeADGEdge,
    RuntimeADGNode,
    RuntimeADGSnapshot,
    create_runtime_adg_snapshot,
)
from system_learning.stores.version_store import FileBackedVersionStore, InMemoryVersionStore

emit_determinism_digest("runtime_adg_store", "runtime_adg_store_digest")
record_execution_trace("runtime_adg_store", "runtime_adg_store_trace")


class InMemoryRuntimeADGStore:
    """In-memory runtime ADG store for tests and single-process use."""

    def __init__(self) -> None:
        self._store = InMemoryVersionStore()
        self._index: dict[str, str] = {}

    def persist(self, snapshot: RuntimeADGSnapshot) -> str:
        """Persist a snapshot and return its version_id. Idempotent."""
        version_id = self._store.commit_change_package(snapshot)
        self._index[snapshot.trace_id] = version_id
        self._index[snapshot.snapshot_id] = version_id
        return version_id

    def get_by_version(self, version_id: str) -> bytes | None:
        return self._store.get(version_id)

    def get_version_id_for_trace(self, trace_id: str) -> str | None:
        return self._index.get(trace_id)

    def list_snapshots(self) -> list[str]:
        return self._store.list_versions()


class FileBackedRuntimeADGStore:
    """File-backed runtime ADG store using content-addressable L4 storage.

    Integrates with sovereign L4 territory for runtime ADG persistence.
    Directory layout (mirrors FileBackedVersionStore)::

        <L4_STATE_MEMORY>/runtime_adg/
            <content_hash[:2]>/<content_hash>.json   # snapshot entry
            _index.json                               # version_id -> hash
            _trace_index.json                         # trace_id -> version_id

    Parameters
    ----------
    base_dir:
        Root directory for snapshot persistence. If None, uses L4-approved territory.
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        # Use L4 sovereign territory if no base_dir specified
        if base_dir is None:
            project_root = get_validated_project_root()
            base_dir = project_root / "agentic_core" / "L4_state" / "memory" / "runtime_adg"    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging

        self._base_dir = Path(base_dir)
        self._validate_l4_compliance()

        self._version_store = FileBackedVersionStore(self._base_dir)
        self._trace_index_path = self._base_dir / "_trace_index.json"
        self._trace_index: dict[str, str] = self._load_trace_index()

    def _validate_l4_compliance(self) -> None:
        """Validate storage location is within L4 sovereign territory."""
        try:
            # Convert to relative path for L4 validation
            abs_base = self._base_dir.resolve()
            project_root = get_validated_project_root()

            if not abs_base.is_relative_to(project_root):
                raise ValueError(f"Runtime ADG store must be within project root: {self._base_dir}")

            rel_path = abs_base.relative_to(project_root)
            rel_path_str = str(rel_path).replace("\\", "/")

            # Check if this path is in L4 approved folders
            l4_approved = False
            for approved in L4_APPROVED_FOLDERS:
                if rel_path_str.startswith(approved):
                    l4_approved = True
                    break

            if not l4_approved:
                raise ValueError(
                    f"Runtime ADG store path not in L4 approved territory: {rel_path_str}. "
                    f"Approved L4 folders include: {sorted(L4_APPROVED_FOLDERS)[:3]}..."
                )

        except Exception as e:
            raise ValueError(f"L4 compliance validation failed for {self._base_dir}: {e}")

    def _load_trace_index(self) -> dict[str, str]:
        if self._trace_index_path.exists():
            try:
                return json.loads(self._trace_index_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_trace_index(self) -> None:
        self._trace_index_path.write_text(
            json.dumps(self._trace_index, indent=2, sort_keys=True), encoding="utf-8"
        )

    def persist(self, snapshot: RuntimeADGSnapshot) -> str:
        """Persist snapshot idempotently. Returns version_id."""
        version_id = self._version_store.commit_change_package(snapshot)
        if snapshot.trace_id not in self._trace_index:
            self._trace_index[snapshot.trace_id] = version_id
            self._trace_index[snapshot.snapshot_id] = version_id
            self._save_trace_index()
        return version_id

    def get_by_version(self, version_id: str) -> bytes | None:
        return self._version_store.get(version_id)

    def get_version_id_for_trace(self, trace_id: str) -> str | None:
        return self._trace_index.get(trace_id)

    def load_snapshot(self, version_id: str) -> RuntimeADGSnapshot | None:
        """Deserialise a stored snapshot by version_id. Returns None if not found."""
        payload = self._version_store.get(version_id)
        if payload is None:
            return None
        try:
            return _deserialise_snapshot(payload)
        except (KeyError, ValueError, TypeError):
            return None

    def list_snapshots(self) -> list[str]:
        return self._version_store.list_versions()


def _deserialise_snapshot(payload: bytes) -> RuntimeADGSnapshot:
    """Reconstruct a RuntimeADGSnapshot from its canonical bytes payload."""
    meta = json.loads(payload.decode("utf-8"))
    data: dict[str, Any] = meta.get("data", meta)
    nodes = tuple(
        RuntimeADGNode(
            node_id=str(n["node_id"]),
            name=str(n["name"]),
            kind=str(n["kind"]),
            layer=str(n["layer"]),
            component=str(n["component"]),
            started_at_utc=int(n["started_at_utc"]),
            duration_ms=float(n["duration_ms"]),
            status=str(n["status"]),
            attributes_json=str(n["attributes_json"]),
        )
        for n in data.get("nodes", [])
    )
    edges = tuple(
        RuntimeADGEdge(
            src_id=str(e["src_id"]),
            dst_id=str(e["dst_id"]),
            relation=str(e["relation"]),
        )
        for e in data.get("edges", [])
    )
    return create_runtime_adg_snapshot(
        trace_id=str(data["trace_id"]),
        mission=str(data["mission"]),
        started_at_utc=int(data["started_at_utc"]),
        ended_at_utc=int(data["ended_at_utc"]),
        nodes=nodes,
        edges=edges,
    )