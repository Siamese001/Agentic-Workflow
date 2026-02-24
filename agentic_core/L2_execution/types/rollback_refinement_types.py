"""
Rollback refinement types for L2 execution learning.
Deterministic, frozen dataclasses with canonical serialization.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from agentic_core.L2_execution.types.resource_prediction_types import FailureSignature


@dataclass(frozen=True)
class RollbackStrategyId:
    """Identifier for a rollback strategy."""

    name: str

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        data = {"name": self.name}
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class RollbackOutcomeStats:
    """Statistics for rollback strategy outcomes."""

    success: int
    fail: int

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        data = {
            "success": self.success,
            "fail": self.fail,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class RollbackRefinementRequest:
    """Request to refine rollback strategy selection."""

    failure_signature: FailureSignature
    candidates: tuple[RollbackStrategyId, ...]
    history_bytes: bytes | None

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        data = {
            "failure_signature": self.failure_signature.canonical_bytes().decode("ascii"),
            "candidates": tuple(sorted(c.name for c in self.candidates)),
            "history_bytes": self.history_bytes.decode("ascii") if self.history_bytes else None,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class RollbackRefinementDecision:
    """Decision on rollback strategy with deterministic ranking."""

    chosen: RollbackStrategyId
    ranked: tuple[RollbackStrategyId, ...]  # Deterministic order
    reasons: tuple[str, ...]  # Deterministic reasoning

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        data = {
            "chosen": self.chosen.name,
            "ranked": tuple(s.name for s in self.ranked),
            "reasons": tuple(sorted(self.reasons)),  # Sort for determinism
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
