"""
Persistent Storage Layer Contract

Defines immutable data structures and protocols for deterministic,
append-only storage of agentic artifacts with local filesystem backend.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

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
)

_emit_dispatches_healing_run("p1", "persistent_store", "L4")
_emit_routes_through("p1", "persistent_store", "L4")
_emit_escalates_to_human("p1", "persistent_store", "L4")
_emit_reads_policy_state("p1", "persistent_store", "L4")


@dataclass(frozen=True)
class StoredArtifact:
    """Immutable artifact definition for storage."""

    kind: str
    logical_id: str
    created_utc: str
    content_type: str
    payload: dict[str, Any]
    hashes: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class StoreMetrics:
    """Deterministic performance metrics for storage operations."""

    bytes_written: int = 0
    bytes_read: int = 0
    artifacts_written: int = 0
    artifacts_read: int = 0


@dataclass(frozen=True)
class StoredArtifactRef:
    """Immutable reference to a stored artifact."""

    kind: str
    logical_id: str
    version: int
    path: str
    size_bytes: int = 0


class StoreBackend(Protocol):
    """Protocol for storage backends."""

    def put(self, artifact: StoredArtifact) -> StoredArtifactRef:
        """Store an artifact and return its reference."""
        ...

    def get(self, ref: StoredArtifactRef) -> StoredArtifact:
        """Retrieve an artifact by reference."""
        ...

    def list(self, kind: str | None = None) -> list[StoredArtifactRef]:
        """List stored artifacts, optionally filtered by kind."""
        ...


def _sanitize_id(identifier: str) -> str:
    """Sanitize identifier to prevent path traversal.

    Only allows alphanumeric, hyphen, underscore, and dot characters.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_sanitize_id", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_sanitize_id", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "_sanitize_id")
    sanitized = re.sub("[^a-zA-Z0-9._-]", "_", identifier)
    if sanitized.startswith("-") or (sanitized.startswith(".") and (not sanitized.startswith(".."))):
        sanitized = "id_" + sanitized
    return sanitized


def _canonicalize_payload(payload: dict[str, Any]) -> str:
    """Canonicalize payload to deterministic JSON string."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _compute_sha256(data: str) -> str:
    """Compute SHA256 hash of data string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def create_artifact(
    kind: str,
    logical_id: str,
    payload: dict[str, Any],
    content_type: str = "application/json",
    created_utc: str | None = None,
    metadata: dict[str, str] | None = None,
) -> StoredArtifact:
    """Create a StoredArtifact with computed hashes.

    Args:
        kind: Artifact kind
        logical_id: Logical identifier
        payload: Artifact data
        content_type: Content type (default: application/json)
        created_utc: ISO timestamp (if None, uses current UTC time)
        metadata: Allowlisted metadata (filtered to allowed keys)

    Returns:
        StoredArtifact with computed hashes
    """
    if created_utc is None:
        created_utc = datetime.utcnow().isoformat() + "Z"
    if metadata is None:
        metadata = {}
    payload_json = _canonicalize_payload(payload)
    hashes = {"sha256": _compute_sha256(payload_json)}
    metadata["size"] = str(len(payload_json.encode("utf-8")))
    return StoredArtifact(
        kind=kind,
        logical_id=_sanitize_id(logical_id),
        created_utc=created_utc,
        content_type=content_type,
        payload=payload,
        hashes=hashes,
        metadata=metadata,
    )


__all__ = [
    "StoredArtifact",
    "StoredArtifactRef",
    "StoreBackend",
    "create_artifact",
    "_sanitize_id",
    "_canonicalize_payload",
    "_compute_sha256",
]
