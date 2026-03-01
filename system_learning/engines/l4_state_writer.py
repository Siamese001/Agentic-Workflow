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

    def write_l4c_retrieval_profile(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Write L4C retrieval profile to L4 state.

        Args:
            payload_bytes: Serialized retrieval profile.
            component_name: Name of the component (typically 'meta-learning').
            created_utc: Timestamp for the write (injected, no wall clock).

        Returns:
            Version ID of the written state.
        """
        ...

    def write_l4c_shadow_drift(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        """Write L4C shadow drift summary to L4 state (informational only).

        Args:
            payload_bytes: Serialized shadow drift summary.
            component_name: Name of the component (typically 'meta-learning').
            created_utc: Timestamp for the write (injected, no wall clock).

        Returns:
            Version ID of the written state.
        """
        ...

    def write_l4c_policy_recommendation(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Write L4C policy recommendation to L4 state (advisory only).

        Args:
            payload_bytes: Serialized policy recommendation.
            component_name: Name of the component (typically 'meta-learning').
            created_utc: Timestamp for the write (injected, no wall clock).

        Returns:
            Version ID of the written state.
        """
        ...

    def write_l4c_retrieval_profile_proposal(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Write L4C retrieval profile proposal to L4 state (requires approval).

        Args:
            payload_bytes: Serialized retrieval profile proposal.
            component_name: Name of the component (typically 'meta-learning').
            created_utc: Timestamp for the write (injected, no wall clock).

        Returns:
            Version ID of the written state.
        """
        ...

    def write_l4c_retrieval_profile_proposal_approval(
        self, *, proposal_digest: str, approved: bool, approved_at_utc: int, component_name: str
    ) -> str:
        """Write L4C retrieval profile proposal approval to L4 state (append-only).

        Args:
            proposal_digest: Digest of the proposal being approved/rejected.
            approved: True for approval, False for rejection.
            approved_at_utc: Timestamp when approval was granted.
            component_name: Name of the component (typically 'meta-learning').

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

    def write_l4c_retrieval_profile(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Write L4C retrieval profile to L4 state."""
        # Create a change package for the retrieval profile
        package = SimpleChangePackage(
            component=f"l4c_retrieval_profile_{component_name}",
            payload_bytes=payload_bytes,
            metadata={
                "type": "retrieval_profile",
                "component_name": component_name,
                "created_utc": created_utc,
            },
        )

        # Write to version store (content-hash keyed, write-once)
        version_id = self._version_store.commit_change_package(
            package=package,
            parent_version_id=None,
            change_spec_hash="retrieval_profile",
            committed_at_utc=created_utc,
        )
        return version_id

    def write_l4c_shadow_drift(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        """Write L4C shadow drift summary to L4 state (informational only)."""
        # Create a change package for the shadow drift summary
        package = SimpleChangePackage(
            component=f"l4c_shadow_drift_{component_name}",
            payload_bytes=payload_bytes,
            metadata={
                "type": "shadow_drift",
                "component_name": component_name,
                "created_utc": created_utc,
            },
        )

        # Write to version store (content-hash keyed, write-once)
        version_id = self._version_store.commit_change_package(
            package=package,
            parent_version_id=None,
            change_spec_hash="shadow_drift",
            committed_at_utc=created_utc,
        )
        return version_id

    def write_l4c_policy_recommendation(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Write L4C policy recommendation to L4 state (advisory only)."""
        # Create a change package for the policy recommendation
        package = SimpleChangePackage(
            component=f"l4c_policy_recommendation_{component_name}",
            payload_bytes=payload_bytes,
            metadata={
                "type": "policy_recommendation",
                "component_name": component_name,
                "created_utc": created_utc,
            },
        )

        # Write to version store (content-hash keyed, write-once)
        version_id = self._version_store.commit_change_package(
            package=package,
            parent_version_id=None,
            change_spec_hash="policy_recommendation",
            committed_at_utc=created_utc,
        )
        return version_id

    def write_l4c_retrieval_profile_proposal(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Write L4C retrieval profile proposal to L4 state (requires approval)."""
        # Create a change package for the retrieval profile proposal
        package = SimpleChangePackage(
            component=f"l4c_retrieval_profile_proposal_{component_name}",
            payload_bytes=payload_bytes,
            metadata={
                "type": "retrieval_profile_proposal",
                "component_name": component_name,
                "created_utc": created_utc,
            },
        )

        # Write to version store (content-hash keyed, write-once)
        version_id = self._version_store.commit_change_package(
            package=package,
            parent_version_id=None,
            change_spec_hash="retrieval_profile_proposal",
            committed_at_utc=created_utc,
        )
        return version_id

    def write_l4c_retrieval_profile_proposal_approval(
        self, *, proposal_digest: str, approved: bool, approved_at_utc: int, component_name: str
    ) -> str:
        """Write L4C retrieval profile proposal approval to L4 state (append-only)."""
        # Create approval record as JSON
        import json

        approval_data = {
            "proposal_digest": proposal_digest,
            "approved": approved,
            "approved_at_utc": approved_at_utc,
            "component_name": component_name,
        }
        payload_bytes = json.dumps(approval_data, sort_keys=True, separators=(",", ":")).encode("utf-8")

        # Create a change package for the approval record
        package = SimpleChangePackage(
            component=f"l4c_retrieval_profile_proposal_approval_{component_name}",
            payload_bytes=payload_bytes,
            metadata={
                "type": "retrieval_profile_proposal_approval",
                "proposal_digest": proposal_digest,
                "approved": approved,
                "approved_at_utc": approved_at_utc,
                "component_name": component_name,
            },
        )

        # Write to version store (append-only, no parent for approvals)
        version_id = self._version_store.commit_change_package(
            package=package,
            parent_version_id=None,
            change_spec_hash=f"proposal_approval_{proposal_digest[:8]}",
            committed_at_utc=approved_at_utc,
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

    def write_l4c_retrieval_profile(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """No-op write that returns a placeholder version ID."""
        return f"noop_l4c_{created_utc}"

    def write_l4c_shadow_drift(self, *, payload_bytes: bytes, component_name: str, created_utc: int) -> str:
        """No-op write that returns a placeholder version ID."""
        return f"noop_shadow_drift_{created_utc}"

    def write_l4c_policy_recommendation(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """No-op write that returns a placeholder version ID."""
        return f"noop_policy_recommendation_{created_utc}"

    def write_l4c_retrieval_profile_proposal(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """No-op write that returns a placeholder version ID."""
        return f"noop_retrieval_profile_proposal_{created_utc}"

    def write_l4c_retrieval_profile_proposal_approval(
        self, *, proposal_digest: str, approved: bool, approved_at_utc: int, component_name: str
    ) -> str:
        """No-op write that returns a placeholder version ID."""
        return f"noop_proposal_approval_{approved_at_utc}"


__all__ = [
    "L4StateWriter",
    "DefaultL4StateWriter",
    "NoOpL4StateWriter",
]
