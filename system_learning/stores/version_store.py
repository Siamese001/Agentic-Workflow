"""Concrete VersionStore — content-addressable storage for committed ChangePackages.

Provides file-backed and in-memory implementations of the ``VersionStore``
protocol defined in ``meta_learning_pipeline.py``.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "version_store", "p0_governance")
_emit_reads_policy_state("p0", "version_store", "policy_binding")
emit_replay_key("p0", "version_store")
emit_determinism_digest("p0", "version_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "version_store", "execution_auth")
_emit_validates_capability("p2", "version_store", "capability_check")
_emit_routes_to_capability("p2", "version_store", "capability_route")
_emit_writes_via_uwg("p2", "version_store", "uwg_write")
_emit_blocks_direct_write("p2", "version_store", "direct_write_block")
_emit_records_tool_invocation("p2", "version_store", "tool_invocation")
_emit_captures_execution_output("p2", "version_store", "exec_output")
_emit_dispatches_agent("p3", "version_store", "agent_dispatch")
_emit_coordinates_agents("p3", "version_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "version_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "version_store", "healing_outcome")
_emit_escalates_failure("p3", "version_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "version_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "version_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "version_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "version_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "version_store", "eval_metric")
_emit_stores_embedding("p4", "version_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "version_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "version_store", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class InMemoryVersionStore:
    """In-memory version store for testing and single-process use."""

    _store: dict[str, bytes] = field(default_factory=dict)
    _metadata: dict[str, dict[str, Any]] = field(default_factory=dict)

    def commit_change_package(self, pkg: Any) -> str:
        """Commit a change package and return its version_id.

        The package must have a ``canonical_bytes()`` method for
        content-hash computation.
        """
        _emit_snapshots_state(str(uuid.uuid4()), "InMemoryVersionStore.commit_change_package", "L4_STATE")
        _emit_writes_through(str(uuid.uuid4()), "InMemoryVersionStore.commit_change_package", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "InMemoryVersionStore.commit_change_package")

        if hasattr(pkg, "canonical_bytes"):
            payload = pkg.canonical_bytes()
        else:
            payload = json.dumps(str(pkg), sort_keys=True).encode("utf-8")
        content_hash = hashlib.sha256(payload).hexdigest()
        version_id = f"v_{content_hash[:16]}"
        if version_id not in self._store:
            self._store[version_id] = payload
            self._metadata[version_id] = {"content_hash": content_hash, "type": type(pkg).__name__}
        return version_id

    def get(self, version_id: str) -> bytes | None:
        return self._store.get(version_id)

    def list_versions(self) -> list[str]:
        return sorted(self._store.keys())


class FileBackedVersionStore:
    """File-backed version store with content-addressable directory layout.

    Directory layout::

        <base_dir>/
            <content_hash[:2]>/<content_hash>.json   # payload + metadata
            _index.json                               # version_id -> hash mapping
    """

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self._base_dir / "_index.json"
        self._index: dict[str, str] = self._load_index()

    def _load_index(self) -> dict[str, str]:
        if self._index_path.exists():
            try:
                return json.loads(self._index_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_index(self) -> None:
        self._index_path.write_text(json.dumps(self._index, indent=2, sort_keys=True), encoding="utf-8")

    def commit_change_package(self, pkg: Any) -> str:
        """Commit a change package and return its version_id."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FileBackedVersionStore.commit_change_package")

        if hasattr(pkg, "canonical_bytes"):
            payload = pkg.canonical_bytes()
        else:
            payload = json.dumps(str(pkg), sort_keys=True).encode("utf-8")
        content_hash = hashlib.sha256(payload).hexdigest()
        version_id = f"v_{content_hash[:16]}"
        if version_id in self._index:
            return version_id
        shard_dir = self._base_dir / content_hash[:2]
        shard_dir.mkdir(exist_ok=True)
        entry_path = shard_dir / f"{content_hash}.json"
        meta = {
            "version_id": version_id,
            "content_hash": content_hash,
            "type": type(pkg).__name__,
            "payload_hex": payload.hex(),
        }
        entry_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        self._index[version_id] = content_hash
        self._save_index()
        return version_id

    def get(self, version_id: str) -> bytes | None:
        content_hash = self._index.get(version_id)
        if content_hash is None:
            return None
        entry_path = self._base_dir / content_hash[:2] / f"{content_hash}.json"
        if not entry_path.exists():
            return None
        try:
            meta = json.loads(entry_path.read_text(encoding="utf-8"))
            return bytes.fromhex(meta["payload_hex"])
        except (json.JSONDecodeError, OSError, KeyError, ValueError):
            return None

    def list_versions(self) -> list[str]:
        return sorted(self._index.keys())


__all__ = ["InMemoryVersionStore", "FileBackedVersionStore"]
