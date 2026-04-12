"""C1.5: Seal Determinism Digest - Stable proof for audit.

10C-REQ-121: Produce exactly one stable proof W<n>-DETERMINISM-DIGEST invariant
same input+envelope+clock+reads produces same digest
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any

from .replay_envelope import ReplayEnvelope
from .replay_guard import InvocationRecord


@dataclass(frozen=True)
class DeterminismDigest:
    """Determinism digest - proof of deterministic execution.

    10C-REQ-121: W<n>-DETERMINISM-DIGEST invariant same input+envelope+clock+reads
    produces same digest.
    """

    digest_hash: str
    envelope_hash: str
    input_hash: str
    clock_hash: str
    reads_hash: str
    invocation_count: int
    timestamp: float
    invariant: str = "same input+envelope+clock+reads -> same digest"

    def verify_invariant(self) -> bool:
        """Verify the determinism invariant holds."""
        # Recompute digest from components
        raw = f"{self.envelope_hash}:{self.input_hash}:{self.clock_hash}:{self.reads_hash}"
        expected = hashlib.sha256(raw.encode()).hexdigest()
        return self.digest_hash == expected


class DigestSealer:
    """Seals determinism digests for execution proof."""

    def __init__(self) -> None:
        self._digests: dict[str, DeterminismDigest] = {}
        self._counter: int = 0

    def seal(
        self,
        envelope: ReplayEnvelope,
        inputs: dict[str, Any],
        clock_value: float,
        state_reads: list[str],
        invocations: list[InvocationRecord],
    ) -> DeterminismDigest:
        """Seal a determinism digest.

        10C-REQ-121: Produce exactly one stable proof.
        """
        self._counter += 1

        # Hash each component.
        # envelope.ml_model_hashes is included in envelope.envelope_hash() so
        # runs with different model artifacts produce distinct digest_hash values,
        # satisfying the C1 "one snapshot only" invariant for ML artifact identity.
        envelope_hash = envelope.envelope_hash()
        input_hash = self._hash_inputs(inputs)
        clock_hash = hashlib.sha256(str(clock_value).encode()).hexdigest()
        reads_hash = self._hash_reads(state_reads)

        # Combined digest
        raw = f"{envelope_hash}:{input_hash}:{clock_hash}:{reads_hash}"
        digest_hash = hashlib.sha256(raw.encode()).hexdigest()

        digest = DeterminismDigest(
            digest_hash=digest_hash,
            envelope_hash=envelope_hash,
            input_hash=input_hash,
            clock_hash=clock_hash,
            reads_hash=reads_hash,
            invocation_count=len(invocations),
            timestamp=time.time(),
        )

        self._digests[digest_hash] = digest
        return digest

    def _hash_inputs(self, inputs: dict[str, Any]) -> str:
        """Hash input parameters."""
        raw = json.dumps(inputs, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _hash_reads(self, reads: list[str]) -> str:
        """Hash state reads."""
        raw = json.dumps(sorted(reads))
        return hashlib.sha256(raw.encode()).hexdigest()

    def get_digest(self, digest_hash: str) -> DeterminismDigest | None:
        """Retrieve a sealed digest."""
        return self._digests.get(digest_hash)

    def verify_digest(self, digest_hash: str) -> bool:
        """Verify a digest's integrity."""
        digest = self._digests.get(digest_hash)
        if not digest:
            return False
        return digest.verify_invariant()

    def get_digest_count(self) -> int:
        """Get total number of sealed digests."""
        return len(self._digests)
