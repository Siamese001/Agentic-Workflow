"""CommitProofInvariant -- binds committed version_ids to real implementation content.

GAP-010: The target-state requires that every commit proof binds to a true
implementation commit.  Churn commits (no-op content, placeholder bytes) must
not count as valid proof.

Rules enforced:
  - version_id must be a 64-char lowercase hex string (SHA-256).
  - implementation_hash must be a non-empty hex string.
  - version_id must equal SHA-256(canonical_bytes) of the committed package.
  - implementation_hash must NOT match the sentinel churn hash.
  - commit_timestamp_utc must be > 0.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

_HEX_RE = re.compile("^[0-9a-f]+$")
_EMPTY_CONTENT_HASH = hashlib.sha256(b"").hexdigest()
_PLACEHOLDER_HASH = hashlib.sha256(b"placeholder").hexdigest()
_CHURN_HASHES: frozenset[str] = frozenset({_EMPTY_CONTENT_HASH, _PLACEHOLDER_HASH})


class CommitProofViolation(Exception):
    """Raised when a commit proof invariant is violated."""


@dataclass(frozen=True)
class CommitProofInvariant:
    """Immutable proof record binding version_id to implementation content.

    Attributes
    ----------
    version_id : str
        SHA-256 hex digest of the committed ChangePackage.canonical_bytes().
    implementation_hash : str
        SHA-256 hex digest of the actual implementation bytes being committed
        (e.g. canonical_bytes() of the ChangePackage).  Must not be a churn hash.
    commit_timestamp_utc : int
        UTC timestamp at which the commit was made.  Must be > 0.
    """

    version_id: str
    implementation_hash: str
    commit_timestamp_utc: int

    def verify(self) -> None:
        """Verify all invariant conditions.  Raises CommitProofViolation on any failure."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CommitProofInvariant.verify")

        if not isinstance(self.version_id, str) or len(self.version_id) != 64:
            raise CommitProofViolation(
                f"COMMIT_PROOF_VIOLATION: version_id must be 64-char hex, got {self.version_id!r}"
            )
        if not _HEX_RE.match(self.version_id):
            raise CommitProofViolation(
                f"COMMIT_PROOF_VIOLATION: version_id is not lowercase hex: {self.version_id!r}"
            )
        if not isinstance(self.implementation_hash, str) or not self.implementation_hash:
            raise CommitProofViolation(
                "COMMIT_PROOF_VIOLATION: implementation_hash must be a non-empty hex string"
            )
        if not _HEX_RE.match(self.implementation_hash):
            raise CommitProofViolation(
                f"COMMIT_PROOF_VIOLATION: implementation_hash is not hex: {self.implementation_hash!r}"
            )
        if self.implementation_hash in _CHURN_HASHES:
            raise CommitProofViolation(
                f"COMMIT_PROOF_VIOLATION: implementation_hash {self.implementation_hash!r} matches a known churn/placeholder hash -- commit is not bound to real content"
            )
        if not isinstance(self.commit_timestamp_utc, int) or self.commit_timestamp_utc <= 0:
            raise CommitProofViolation(
                f"COMMIT_PROOF_VIOLATION: commit_timestamp_utc must be > 0, got {self.commit_timestamp_utc!r}"
            )

    @classmethod
    def from_package(
        cls, version_id: str, package: object, commit_timestamp_utc: int
    ) -> CommitProofInvariant:
        """Create and immediately verify a proof for a committed package.

        Parameters
        ----------
        version_id : str
            The version_id returned by VersionStore.commit_change_package().
        package : object
            The committed package (must implement canonical_bytes() -> bytes).
        commit_timestamp_utc : int
            UTC timestamp of the commit.

        Returns
        -------
        CommitProofInvariant
            Verified proof instance.

        Raises
        ------
        CommitProofViolation
            If any invariant is violated, including version_id mismatch.
        """
        if not hasattr(package, "canonical_bytes"):
            raise CommitProofViolation("COMMIT_PROOF_VIOLATION: package does not implement canonical_bytes()")
        pkg_bytes: bytes = package.canonical_bytes()
        impl_hash = hashlib.sha256(pkg_bytes).hexdigest()
        if version_id != impl_hash:
            raise CommitProofViolation(
                f"COMMIT_PROOF_VIOLATION: version_id {version_id!r} does not match SHA-256(canonical_bytes()) = {impl_hash!r} -- proof not bound to implementation"
            )
        proof = cls(
            version_id=version_id, implementation_hash=impl_hash, commit_timestamp_utc=commit_timestamp_utc
        )
        proof.verify()
        return proof


def verify_commit_proof(version_id: str, package: object, commit_timestamp_utc: int) -> CommitProofInvariant:
    """Convenience function: create and verify a CommitProofInvariant.

    Raises CommitProofViolation if any invariant fails.
    """
    return CommitProofInvariant.from_package(
        version_id=version_id, package=package, commit_timestamp_utc=commit_timestamp_utc
    )


__all__ = ["CommitProofInvariant", "CommitProofViolation", "verify_commit_proof"]
