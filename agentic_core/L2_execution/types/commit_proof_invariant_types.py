"""CommitProofInvariant — determinism proof standard for phase digests.

Spec: Determinism & Replayability, Guarantee #18.
A CommitProofInvariant captures a determinism digest at a known point in time.
It can be re-evaluated to verify the digest is stable (same inputs → same hash)
or verify it has changed (negative control: tampered inputs → different hash).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable


class DeterminismProofFailure(RuntimeError):
    """Raised when a CommitProofInvariant verification fails."""


@dataclass(frozen=True)
class CommitProofInvariant:
    """Captures a determinism digest and verifies it is reproducible.

    Spec: Determinism & Replayability, Guarantee #18.

    Fields:
        phase_id: Stable identifier for the phase this proof covers.
        digest: The expected 64-hex SHA-256 digest.
        inputs_summary: Human-readable summary of what contributed to the digest.
    """

    phase_id: str
    digest: str
    inputs_summary: str

    def __post_init__(self) -> None:
        if not self.phase_id or not self.phase_id.strip():
            raise DeterminismProofFailure("CommitProofInvariant.phase_id must be non-empty")
        if len(self.digest) != 64 or not all(c in "0123456789abcdef" for c in self.digest):
            raise DeterminismProofFailure(
                f"CommitProofInvariant.digest must be a 64-char lowercase hex string, got '{self.digest[:16]}...' (len={len(self.digest)})"
            )

    def verify_stable(self, recompute_fn: Callable[[], str]) -> None:
        """Assert that recompute_fn() returns the same digest as self.digest.

        Raises DeterminismProofFailure if the digest has changed (non-determinism detected).
        """
        actual = recompute_fn()
        if actual != self.digest:
            raise DeterminismProofFailure(
                f"[Phase {self.phase_id}] Determinism proof FAILED: expected={self.digest[:16]}..., actual={actual[:16]}... Inputs changed without updating the committed proof."
            )

    def verify_unstable(self, recompute_fn: Callable[[], str]) -> None:
        """Assert that recompute_fn() returns a DIFFERENT digest than self.digest.

        Negative control: verifies that tampered inputs produce a different hash.
        Raises DeterminismProofFailure if the digest is unchanged (tamper not detected).
        """
        actual = recompute_fn()
        if actual == self.digest:
            raise DeterminismProofFailure(
                f"[Phase {self.phase_id}] Negative control FAILED: tampered inputs produced the same digest={self.digest[:16]}... The determinism function is insensitive to this mutation."
            )


def make_proof(phase_id: str, inputs_summary: str, recompute_fn: Callable[[], str]) -> CommitProofInvariant:
    """Compute a fresh CommitProofInvariant by calling recompute_fn().

    Use this at seal time to capture the current digest.
    """
    digest = recompute_fn()
    return CommitProofInvariant(phase_id=phase_id, digest=digest, inputs_summary=inputs_summary)


def canonical_digest(obj: Any) -> str:
    """Compute SHA-256 of canonical JSON (sorted keys, no spaces, ASCII-safe)."""
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


__all__ = ["CommitProofInvariant", "DeterminismProofFailure", "make_proof", "canonical_digest"]
