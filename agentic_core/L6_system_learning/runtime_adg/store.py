"""Runtime ADG store — persists and queries RuntimeADGSnapshots via L4.

Uses FileBackedVersionStore (content-addressable) as the persistence backend.
Integrates with L4 sovereign territory for runtime ADG storage.
No new storage subsystem. InMemoryRuntimeADGStore is provided for tests.

Idempotency: committing the same snapshot twice returns the same version_id.
"""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import L4_APPROVED_FOLDERS, get_validated_project_root
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from .snapshot import (
    RuntimeADGEdge,
    RuntimeADGNode,
    RuntimeADGSnapshot,
    create_runtime_adg_snapshot,
)
from agentic_core.L6_system_learning.stores.version_store import (
    FileBackedVersionStore,
    InMemoryVersionStore,
)
from tqdm import tqdm

emit_determinism_digest("runtime_adg_store", "runtime_adg_store_digest")
record_execution_trace("runtime_adg_store", "runtime_adg_store_trace")

logger = logging.getLogger(__name__)


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
            base_dir = (
                project_root / "agentic_core" / "L4_state" / "memory" / "runtime_adg"
            )  # review: Add error context logging

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
                    f"Approved L4 folders include: {sorted(L4_APPROVED_FOLDERS)[:3]}...",
                )

        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            raise ValueError(f"L4 compliance validation failed for {self._base_dir}: {exc}") from exc

    def _load_trace_index(self) -> dict[str, str]:
        if self._trace_index_path.exists():
            try:
                raw_any = json.loads(self._trace_index_path.read_text(encoding="utf-8"))
                if not isinstance(raw_any, dict):
                    return {}
                raw: dict[str, str] = {str(k): str(v) for k, v in raw_any.items()}
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning(
                    "Failed to load runtime ADG trace index %s: %s",
                    self._trace_index_path,
                    exc,
                )
                return {}
            # Drop stale empty-string keys/values (residue of the pre-Tier-1
            # first-write-wins bug that locked out 88/89 snapshots).
            cleaned = {k: v for k, v in raw.items() if k and v}
            if len(cleaned) != len(raw):
                logger.warning(
                    "runtime_adg_trace_index_cleaned removed=%d remaining=%d",
                    len(raw) - len(cleaned),
                    len(cleaned),
                )
            return cleaned
        return {}

    def _save_trace_index(self) -> None:
        self._trace_index_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self._trace_index_path.parent,
            prefix=self._trace_index_path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(self._trace_index, handle, indent=2, sort_keys=True)
            tmp_name = handle.name
        Path(tmp_name).replace(self._trace_index_path)

    def persist(
        self,
        snapshot: RuntimeADGSnapshot,
        allow_unbound: bool = False,
        allow_empty_payload: bool = False,
    ) -> str:
        """Persist snapshot idempotently. Returns version_id.

        Tier 1 guardrail (per `.windsurf/plans/runtime-adg-tier1-trace-binding-c9b84d.md`):

          1. Empty `trace_id` is REJECTED by default. Use `allow_unbound=True`
             ONLY in back-fill/migration tooling that knows what it's doing.
             Previously, an empty trace_id caused first-write-wins lockout
             that silently skipped the trace-index for 88 of 89 snapshots.
          2. Empty payload (0 nodes AND 0 edges) is REJECTED unconditionally
             unless `allow_empty_payload=True`. Writing skeletal snapshots
             pollutes the L4 archive and makes coverage audits lie.
          3. Trace-index update is now UNCONDITIONAL. The previous
             `if trace_id not in index` check caused the lockout bug. Last
             write wins per trace_id; idempotent per snapshot_id because the
             version_id is deterministic from content.
        """
        if not snapshot.trace_id and not allow_unbound:
            raise ValueError(
                "Runtime ADG snapshot has empty trace_id; refusing to persist. "
                "Pass allow_unbound=True only from migration/back-fill tooling."
            )
        if not snapshot.nodes and not snapshot.edges and not allow_empty_payload:
            raise ValueError(
                "Runtime ADG snapshot has empty payload (0 nodes, 0 edges); "
                "refusing to persist skeletal snapshot."
            )

        version_id = self._version_store.commit_change_package(snapshot)

        # Unconditional index update. Only skip genuinely-empty keys to avoid
        # reintroducing the stale-""-key pathology this guardrail was built to kill.
        dirty = False
        if snapshot.trace_id:
            if self._trace_index.get(snapshot.trace_id) != version_id:
                self._trace_index[snapshot.trace_id] = version_id
                dirty = True
        if snapshot.snapshot_id:
            if self._trace_index.get(snapshot.snapshot_id) != version_id:
                self._trace_index[snapshot.snapshot_id] = version_id
                dirty = True
        if dirty:
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
        except (
            KeyError,
            ValueError,
            TypeError,
        ):  # guardian: allow-return-none-swallow -- deserialization: non-fatal, caller skips None
            return None

    def list_snapshots(self) -> list[str]:
        return self._version_store.list_versions()


def _deserialise_snapshot(payload: bytes) -> RuntimeADGSnapshot:
    """Reconstruct a RuntimeADGSnapshot from its canonical bytes payload.

    The canonical format uses RS (\x1f) as record separator and GS (\x1e) as group separator:
    header: trace_id\x1fmission\x1fstarted_at\x1fended_at
    nodes: node_id\x1ename\x1ekind\x1elayer\x1ecomponent\x1ets\x1eduration\x1estatus\x1eattrs_json
    edges: src_id\x1edst_id\x1erelation
    """
    try:
        # Split into header and body
        parts = payload.split(b"\x1f")
        if len(parts) < 4:
            raise ValueError("Invalid canonical format: insufficient header fields")

        trace_id = parts[0].decode("utf-8")
        mission = parts[1].decode("utf-8")
        started_at_utc = int(parts[2].decode("utf-8"))
        ended_at_utc = int(parts[3].decode("utf-8"))

        # Remaining parts are nodes and edges
        remaining = parts[4:]

        nodes: list[RuntimeADGNode] = []
        edges: list[RuntimeADGEdge] = []

        for part in tqdm(remaining, desc="Processing", unit="item"):
            if not part:
                continue
            fields = part.split(b"\x1e")

            if len(fields) == 9:
                # This is a node: 9 fields
                nodes.append(
                    RuntimeADGNode(
                        node_id=fields[0].decode("utf-8"),
                        name=fields[1].decode("utf-8"),
                        kind=fields[2].decode("utf-8"),
                        layer=fields[3].decode("utf-8"),
                        component=fields[4].decode("utf-8"),
                        started_at_utc=int(fields[5].decode("utf-8")),
                        duration_ms=float(fields[6].decode("utf-8")),
                        status=fields[7].decode("utf-8"),
                        attributes_json=fields[8].decode("utf-8"),
                    )
                )
            elif len(fields) == 3:
                # This is an edge: 3 fields
                edges.append(
                    RuntimeADGEdge(
                        src_id=fields[0].decode("utf-8"),
                        dst_id=fields[1].decode("utf-8"),
                        relation=fields[2].decode("utf-8"),
                    )
                )
            # Skip unknown field counts

        return create_runtime_adg_snapshot(
            trace_id=trace_id,
            mission=mission,
            started_at_utc=started_at_utc,
            ended_at_utc=ended_at_utc,
            nodes=tuple(nodes),
            edges=tuple(edges),
        )
    except (ValueError, IndexError, UnicodeDecodeError) as e:
        raise ValueError(f"Failed to deserialise snapshot: {e}")
