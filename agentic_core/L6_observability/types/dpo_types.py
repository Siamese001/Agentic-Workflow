"""DPO (Direct Preference Optimization) types for deterministic HITL feedback processing.

Frozen dataclasses with canonical serialization for human-in-the-loop feedback.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass(frozen=True, slots=True)
class DPOExampleId:
    """Unique identifier for a DPO example derived from control and candidate hashes.

    Attributes:
        control_hash: SHA-256 hash of control output (hex string, 64 chars).
        candidate_hash: SHA-256 hash of candidate output (hex string, 64 chars).
    """

    control_hash: str
    candidate_hash: str

    def canonical_bytes(self) -> bytes:
        """Return canonical ASCII-only bytes representation for hashing.

        Returns:
            Bytes with deterministic ordering and formatting.
        """
        return json.dumps(
            {
                "control_hash": self.control_hash,
                "candidate_hash": self.candidate_hash,
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")

    def content_hash(self) -> str:
        """Return SHA-256 hash of canonical bytes.

        Returns:
            Hex string (64 characters).
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class DPOPair:
    """A single DPO preference pair with human decision.

    Attributes:
        example_id: Unique identifier for this example.
        control_output_hash: SHA-256 hash of control output.
        candidate_output_hash: SHA-256 hash of candidate output.
        human_decision: Human decision ("APPROVE" or "REJECT").
        reasons: Tuple of short deterministic reason codes.
    """

    example_id: DPOExampleId
    control_output_hash: str
    candidate_output_hash: str
    human_decision: str
    reasons: tuple[str, ...]

    def canonical_bytes(self) -> bytes:
        """Return canonical ASCII-only bytes representation for hashing.

        Returns:
            Bytes with deterministic ordering and formatting.
        """
        return json.dumps(
            {
                "example_id": {
                    "control_hash": self.example_id.control_hash,
                    "candidate_hash": self.example_id.candidate_hash,
                },
                "control_output_hash": self.control_output_hash,
                "candidate_output_hash": self.candidate_output_hash,
                "human_decision": self.human_decision,
                "reasons": list(self.reasons),
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")

    def content_hash(self) -> str:
        """Return SHA-256 hash of canonical bytes.

        Returns:
            Hex string (64 characters).
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class DPOBatch:
    """A batch of DPO pairs for processing.

    Attributes:
        pairs: Tuple of DPO pairs sorted by (control_hash, candidate_hash).
    """

    pairs: tuple[DPOPair, ...]

    def canonical_bytes(self) -> bytes:
        """Return canonical ASCII-only bytes representation for hashing.

        Returns:
            Bytes with deterministic ordering and formatting.
        """
        pairs_data = []
        for pair in self.pairs:
            pairs_data.append(
                {
                    "example_id": {
                        "control_hash": pair.example_id.control_hash,
                        "candidate_hash": pair.example_id.candidate_hash,
                    },
                    "control_output_hash": pair.control_output_hash,
                    "candidate_output_hash": pair.candidate_output_hash,
                    "human_decision": pair.human_decision,
                    "reasons": list(pair.reasons),
                }
            )

        return json.dumps(
            {
                "pairs": pairs_data,
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")

    def content_hash(self) -> str:
        """Return SHA-256 hash of canonical bytes.

        Returns:
            Hex string (64 characters).
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
