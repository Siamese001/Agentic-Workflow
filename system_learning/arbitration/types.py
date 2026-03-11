"""Arbitration types for deterministic multi-agent proposal selection."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass(frozen=True)
class ArbitrationCandidate:
    """A candidate proposal for arbitration."""

    id: str
    kind: str
    payload: dict[str, Any]
    score: float
    cost: float
    provenance: str
    created_at: int | None = None  # Optional but MUST NOT affect ordering

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for deterministic fingerprinting."""
        data = {
            "id": self.id,
            "kind": self.kind,
            "payload": self.payload,
            "score": self.score,
            "cost": self.cost,
            "provenance": self.provenance,
            # Note: created_at intentionally excluded to ensure it doesn't affect ordering
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")


@dataclass(frozen=True)
class ArbitrationPolicy:
    """Policy governing arbitration decisions."""

    weights: dict[str, float]
    caps: dict[str, Any]
    thresholds: dict[str, float]
    allowed_kinds: set[str]

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for deterministic fingerprinting."""
        data = {
            "weights": self.weights,
            "caps": self.caps,
            "thresholds": self.thresholds,
            "allowed_kinds": sorted(self.allowed_kinds),  # Sort for determinism
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")


@dataclass(frozen=True)
class ArbitrationDecision:
    """Result of arbitration process."""

    winner_ids: tuple[str, ...]
    merged_payload: dict[str, Any] | None
    rationale_codes: tuple[str, ...]
    deterministic_fingerprint: str

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for deterministic fingerprinting."""
        data = {
            "winner_ids": self.winner_ids,
            "merged_payload": self.merged_payload,
            "rationale_codes": self.rationale_codes,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
