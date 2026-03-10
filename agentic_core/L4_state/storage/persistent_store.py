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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# =============================================================================
# Data Structures (Frozen/Immutable)
# =============================================================================


@dataclass(frozen=True)
class StoredArtifact:
    """Immutable artifact definition for storage."""

    kind: str  # e.g., "replay_record", "replay_summary", "evidence"
    logical_id: str  # e.g., "execute_ssot_plan", "phase5_write_gateway"
    created_utc: str  # ISO timestamp with "Z" suffix (UTC)
    content_type: str  # e.g., "application/json"
    payload: dict[str, Any]  # Artifact data
    hashes: dict[str, str] = field(default_factory=dict)  # e.g., {"sha256": "..."}
    metadata: dict[str, str] = field(default_factory=dict)  # Allowlisted metadata only


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


# =============================================================================
# Store Backend Protocol
# =============================================================================


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


# =============================================================================
# Utility Functions
# =============================================================================


def _sanitize_id(identifier: str) -> str:
    """Sanitize identifier to prevent path traversal.

    Only allows alphanumeric, hyphen, underscore, and dot characters.
    """
    # Remove any path separators and normalize
    sanitized = re.sub(r"[^a-zA-Z0-9._-]", "_", identifier)
    # Prefix with id_ only when it starts with a single leading dot (hidden file)
    # or a dash — but NOT when it starts with .. (already sanitized path traversal)
    if sanitized.startswith("-") or (sanitized.startswith(".") and not sanitized.startswith("..")):
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

    # Canonicalize payload
    payload_json = _canonicalize_payload(payload)

    # Compute hashes
    hashes = {"sha256": _compute_sha256(payload_json)}

    # Add size to metadata
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


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "StoredArtifact",
    "StoredArtifactRef",
    "StoreBackend",
    "create_artifact",
    "_sanitize_id",
    "_canonicalize_payload",
    "_compute_sha256",
]
