"""Healing Outcome Learning Types - Deterministic aggregation for meta-learning.

Immutable, frozen dataclasses for deterministic healing outcome aggregation.
All types are frozen with slots for deterministic behavior.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class HealingOutcomeAggregateKey:
    """Deterministic key for healing outcome aggregation.

    Attributes
    ----------
    healer_name : str
        Canonical healer identifier.
    tier : str
        Healing tier (e.g., 'LOCAL_AGENT', 'REMOTE_AGENT', 'CLOUD_SERVICE').
    failure_type : str
        Stable failure category string.
    """
    healer_name: str
    tier: str
    failure_type: str

    def __post_init__(self) -> None:
        """Validate invariants."""
        if not self.healer_name:
            raise ValueError("healer_name must not be empty")
        if not self.tier:
            raise ValueError("tier must not be empty")
        if not self.failure_type:
            raise ValueError("failure_type must not be empty")


@dataclass(frozen=True, slots=True)
class HealingOutcomeAggregate:
    """Deterministic aggregate counters for a healing outcome key.

    Attributes
    ----------
    success_count : int
        Number of successful healing attempts.
    failure_count : int
        Number of failed healing attempts.
    total_count : int
        Total attempts (success_count + failure_count).
    """
    success_count: int
    failure_count: int
    total_count: int

    def __post_init__(self) -> None:
        """Validate invariants."""
        if self.success_count < 0:
            raise ValueError("success_count must be non-negative")
        if self.failure_count < 0:
            raise ValueError("failure_count must be non-negative")
        if self.total_count != self.success_count + self.failure_count:
            raise ValueError("total_count must equal success_count + failure_count")

    @property
    def success_rate(self) -> float:
        """Compute success rate with deterministic rounding."""
        if self.total_count == 0:
            return 0.0
        # Round to 4 decimal places using round-half-up
        raw_rate = self.success_count / self.total_count
        return round(raw_rate + 1e-10, 4)  # Small epsilon for round-half-up

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation for hashing."""
        # Sort keys for deterministic ordering
        data = {
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "total_count": self.total_count,
        }
        # Use separators for compact JSON
        json_str = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return json_str.encode('utf-8')

    def content_hash(self) -> str:
        """Generate SHA-256 hash of canonical bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class HealingOutcomeAggregateSnapshot:
    """Deterministic snapshot of healing outcome aggregates.

    Attributes
    ----------
    version_id : str
        Unique version identifier (SHA-256 hash of content).
    created_utc : int
        Snapshot creation timestamp (explicit, no wall-clock reads).
    aggregates : tuple[tuple[HealingOutcomeAggregateKey, HealingOutcomeAggregate], ...]
        Sorted tuple of (key, aggregate) pairs.
    """
    version_id: str
    created_utc: int
    aggregates: Tuple[Tuple[HealingOutcomeAggregateKey, HealingOutcomeAggregate], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate invariants."""
        if not self.version_id:
            raise ValueError("version_id must not be empty")
        if self.created_utc < 0:
            raise ValueError("created_utc must be non-negative")
        # Verify aggregates are sorted
        if self.aggregates:
            keys = [key for key, _ in self.aggregates]
            sorted_keys = sorted(keys, key=lambda k: (k.healer_name, k.tier, k.failure_type))
            if keys != sorted_keys:
                raise ValueError("aggregates must be sorted by (healer_name, tier, failure_type)")

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation for hashing."""
        # Convert aggregates to sorted list for deterministic serialization
        aggregates_data = []
        for key, aggregate in self.aggregates:
            key_data = {
                "healer_name": key.healer_name,
                "tier": key.tier,
                "failure_type": key.failure_type,
            }
            aggregate_data = {
                "success_count": aggregate.success_count,
                "failure_count": aggregate.failure_count,
                "total_count": aggregate.total_count,
            }
            aggregates_data.append({"key": key_data, "aggregate": aggregate_data})

        data = {
            "version_id": self.version_id,
            "created_utc": self.created_utc,
            "aggregates": aggregates_data,
        }

        # Use separators for compact JSON
        json_str = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return json_str.encode('utf-8')

    def content_hash(self) -> str:
        """Generate SHA-256 hash of canonical bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    def get_success_rate(self, key: HealingOutcomeAggregateKey) -> float:
        """Get success rate for a specific key."""
        for k, aggregate in self.aggregates:
            if (k.healer_name == key.healer_name and
                k.tier == key.tier and
                k.failure_type == key.failure_type):
                return aggregate.success_rate
        return 0.0


__all__ = [
    "HealingOutcomeAggregateKey",
    "HealingOutcomeAggregate",
    "HealingOutcomeAggregateSnapshot",
]
