"""L4 State Writer - Write-once, versioned, idempotent state persistence.

Phase 7: Persists L2 healing outcome aggregates and L6 drift/detection signals
into L4 structured state with content-hash keyed writes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from system_learning.engines.l4_version_store import L4VersionStore


@dataclass(frozen=True, slots=True)
class SimpleChangePackage:
    """Simple ChangePackage implementation for L4 state writing."""

    component: str
    payload_bytes: bytes
    metadata: dict[str, object]

    def canonical_bytes(self) -> bytes:
        """Return deterministic canonical byte representation."""
        import json

        data = {
            "component": self.component,
            "payload_bytes": self.payload_bytes.hex(),
            "metadata": self.metadata,
        }
        json_str = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return json_str.encode("utf-8")


class L4StateWriter(Protocol):
    """Protocol for L4 state writer with write-once semantics.

    All writes are content-hash keyed and idempotent.
    Returns version IDs for tracking and activation.
    """

    def write_l4a_detection_signal(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Write L4A detection signal to L4 state.

        Args:
            payload_bytes: Serialized detection signal payload.
            component_name: Name of the component emitting the signal.
            created_utc: Timestamp for the write (injected, no wall clock).

        Returns:
            Version ID of the written state.
        """
        ...

    def write_l4b_healing_snapshot(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Write L4B healing outcome snapshot to L4 state.

        Args:
            payload_bytes: Serialized healing outcome snapshot.
            component_name: Name of the component (typically 'meta-learning').
            created_utc: Timestamp for the write (injected, no wall clock).

        Returns:
            Version ID of the written state.
        """
        ...


class DefaultL4StateWriter:
    """Default implementation of L4 state writer using version store.

    Provides write-once, content-hash keyed persistence with version tracking.
    """

    def __init__(self, version_store: L4VersionStore) -> None:
        """Initialize with version store backend.

        Args:
            version_store: Version store for content-addressable storage.
        """
        self._version_store = version_store

    def write_l4a_detection_signal(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Write L4A detection signal to L4 state."""
        # Create a change package for the detection signal
        package = SimpleChangePackage(
            component=f"l4a_detection_signal_{component_name}",
            payload_bytes=payload_bytes,
            metadata={
                "type": "detection_signal",
                "component_name": component_name,
                "created_utc": created_utc,
            },
        )

        # Write to version store (content-hash keyed, write-once)
        version_id = self._version_store.commit_change_package(
            package=package,
            parent_version_id=None,
            change_spec_hash="detection_signal",
            committed_at_utc=created_utc,
        )
        return version_id

    def write_l4b_healing_snapshot(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Write L4B healing outcome snapshot to L4 state."""
        # Create a change package for the healing snapshot
        package = SimpleChangePackage(
            component=f"l4b_healing_snapshot_{component_name}",
            payload_bytes=payload_bytes,
            metadata={
                "type": "healing_snapshot",
                "component_name": component_name,
                "created_utc": created_utc,
            },
        )

        # Write to version store (content-hash keyed, write-once)
        version_id = self._version_store.commit_change_package(
            package=package,
            parent_version_id=None,
            change_spec_hash="healing_snapshot",
            committed_at_utc=created_utc,
        )
        return version_id


# No-op implementation for safe default
class NoOpL4StateWriter:
    """No-op implementation that does nothing.

    Used as safe default when L4 state writing is not configured.
    """

    def write_l4a_detection_signal(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """No-op write that returns a placeholder version ID."""
        return f"noop_l4a_{created_utc}"

    def write_l4b_healing_snapshot(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """No-op write that returns a placeholder version ID."""
        return f"noop_l4b_{created_utc}"


__all__ = [
    "L4StateWriter",
    "DefaultL4StateWriter",
    "NoOpL4StateWriter",
]
