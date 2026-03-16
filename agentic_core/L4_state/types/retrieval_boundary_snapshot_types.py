"""
Phase 6 — RetrievalBoundarySnapshot: deterministic, non-mutating retrieval record.

Records retrieval inputs + anchor set + active config hashes at the boundary.
Does NOT write to the knowledge index (Pinecone/Redis).
snapshot_hash = sha256(canonical_bytes excluding snapshot_hash).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

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

emit_replay_key("p0", "retrieval_boundary_snapshot_types")
emit_determinism_digest("p0", "retrieval_boundary_snapshot_types")

_emit_dispatches_healing_run("p1", "retrieval_boundary_snapshot_types", "L4")
_emit_routes_through("p1", "retrieval_boundary_snapshot_types", "L4")
_emit_escalates_to_human("p1", "retrieval_boundary_snapshot_types", "L4")
_emit_reads_policy_state("p1", "retrieval_boundary_snapshot_types", "L4")

_SCHEMA_VERSION: int = 1


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class AnchorEntry:
    """
    Minimal anchor identifier included in the snapshot.
    Carries chunk_id and version_hash for deterministic ordering.
    """

    chunk_id: str
    version_hash: str

    def __post_init__(self) -> None:
        if not self.chunk_id:
            raise ValueError("AnchorEntry: chunk_id must be non-empty")
        if not self.version_hash:
            raise ValueError("AnchorEntry: version_hash must be non-empty")

    def to_dict(self) -> dict[str, str]:
        return {"chunk_id": self.chunk_id, "version_hash": self.version_hash}

    def sort_key(self) -> tuple[str, str]:
        return (self.chunk_id, self.version_hash)


@dataclass
class RetrievalBoundarySnapshot:
    """
    Non-mutating boundary record produced at the start of every retrieval.

    Fields
    ------
    schema_version      : int  — bumped on breaking schema changes
    mission_id          : str  — non-empty identifier for the mission/run
    request_hash        : str  — sha256 of the canonical retrieval request subset
    active_config_hashes: dict — {"policy_hash": ..., "routing_hash": ..., ...}
    anchors             : list — sorted AnchorEntry records (chunk_id, version_hash)
    created_at_utc      : str  — ISO-8601 UTC timestamp (stable, no uuid/elapsed)
    snapshot_hash       : str  — sha256(canonical_bytes()); auto-computed
    """

    schema_version: int
    mission_id: str
    request_hash: str
    active_config_hashes: dict[str, str]
    anchors: list[AnchorEntry]
    created_at_utc: str
    snapshot_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(
                f"RetrievalBoundarySnapshot: schema_version must be {_SCHEMA_VERSION}, got {self.schema_version!r}"
            )
        if not self.mission_id:
            raise ValueError("RetrievalBoundarySnapshot: mission_id must be non-empty")
        if not self.request_hash:
            raise ValueError("RetrievalBoundarySnapshot: request_hash must be non-empty")
        if not isinstance(self.active_config_hashes, dict):
            raise TypeError("RetrievalBoundarySnapshot: active_config_hashes must be a dict")
        if not isinstance(self.anchors, list):
            raise TypeError("RetrievalBoundarySnapshot: anchors must be a list")
        self.anchors = sorted(self.anchors, key=lambda a: a.sort_key())
        object.__setattr__(self, "snapshot_hash", _sha256(self.canonical_bytes()))

    def canonical_bytes(self) -> bytes:
        """
        Deterministic serialisation excluding snapshot_hash (self-referential).
        Keys sorted, anchors sorted by (chunk_id, version_hash).
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(
            str(_uuid.uuid4()), "RetrievalBoundarySnapshot.canonical_bytes", "state_snapshot"
        )
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "RetrievalBoundarySnapshot.canonical_bytes", "p0_governance"
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "RetrievalBoundarySnapshot.canonical_bytes"
        )

        doc: dict[str, Any] = {
            "active_config_hashes": {
                k: self.active_config_hashes[k] for k in sorted(self.active_config_hashes)
            },
            "anchors": [a.to_dict() for a in sorted(self.anchors, key=lambda a: a.sort_key())],
            "created_at_utc": self.created_at_utc,
            "mission_id": self.mission_id,
            "request_hash": self.request_hash,
            "schema_version": self.schema_version,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mission_id": self.mission_id,
            "request_hash": self.request_hash,
            "active_config_hashes": dict(self.active_config_hashes),
            "anchors": [a.to_dict() for a in self.anchors],
            "created_at_utc": self.created_at_utc,
            "snapshot_hash": self.snapshot_hash,
        }


def build_request_hash(query: str, top_k: int, domain: str) -> str:
    """
    Compute a deterministic sha256 hash of the canonical retrieval request subset.
    Excludes volatile fields (timestamps, trace IDs).
    """
    doc = {"domain": domain, "query": query, "top_k": top_k}
    raw = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
    return _sha256(raw)


def create_retrieval_boundary_snapshot(
    mission_id: str,
    query: str,
    top_k: int,
    domain: str,
    active_config_hashes: dict[str, str],
    anchors: list[AnchorEntry],
    created_at_utc: str,
) -> RetrievalBoundarySnapshot:
    """
    Factory: build a RetrievalBoundarySnapshot from retrieval parameters.

    Non-mutating — does not write to any persistent store.
    """
    request_hash = build_request_hash(query=query, top_k=top_k, domain=domain)
    return RetrievalBoundarySnapshot(
        schema_version=_SCHEMA_VERSION,
        mission_id=mission_id,
        request_hash=request_hash,
        active_config_hashes=active_config_hashes,
        anchors=anchors,
        created_at_utc=created_at_utc,
    )
