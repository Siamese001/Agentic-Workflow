"""Healing outcome scoring types for offline evaluation.

Phase 3: Types for deterministic scoring of healing outcome proposals.
All types are frozen/immutable with ASCII-only reasons.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def _validate_weight(value: float, name: str) -> None:
    """Validate weight is finite and non-negative."""
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number, got {type(value).__name__}")
    if not (value >= 0):
        raise ValueError(f"{name} must be >= 0, got {value}")
    if value != value:  # NaN check
        raise ValueError(f"{name} must not be NaN")
    if value in (float("inf"), float("-inf")):
        raise ValueError(f"{name} must be finite, got {value}")


def _validate_ascii_only(value: str, name: str) -> None:
    """Validate string is ASCII-only."""
    try:
        value.encode("ascii")
    except UnicodeEncodeError:
        raise ValueError(f"{name} must be ASCII-only, contains non-ASCII characters")


def _stable_round(score: float) -> float:
    """Deterministic rounding: round-half-up to 4 decimal places."""
    # Multiply by 10000, add 0.5, take floor, then divide by 10000
    # This implements round-half-up consistently
    return int(score * 10000 + 0.5) / 10000


@dataclass(frozen=True, slots=True)
class ScoringWeights:
    """Weights for deterministic scoring of healing outcome proposals.

    All weights must be finite and >= 0.
    """

    success_rate_weight: float
    stability_penalty_weight: float
    sample_size_weight: float
    risk_tier_penalty_weight: float

    def __post_init__(self) -> None:
        """Validate all weights."""
        _validate_weight(self.success_rate_weight, "success_rate_weight")
        _validate_weight(self.stability_penalty_weight, "stability_penalty_weight")
        _validate_weight(self.sample_size_weight, "sample_size_weight")
        _validate_weight(self.risk_tier_penalty_weight, "risk_tier_penalty_weight")


@dataclass(frozen=True, slots=True)
class ScoredRecommendation:
    """A scored recommendation from the offline evaluator.

    Reasons must be ASCII-only strings.
    """

    proposer_id: str
    target_surface: str
    recommended_actions: tuple[str, ...]
    score: float  # Deterministically rounded to 4 decimal places
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate fields."""
        if not isinstance(self.proposer_id, str):
            raise ValueError("proposer_id must be a string")
        if not isinstance(self.target_surface, str):
            raise ValueError("target_surface must be a string")
        if not isinstance(self.recommended_actions, tuple):
            raise ValueError("recommended_actions must be a tuple")
        if not isinstance(self.reasons, tuple):
            raise ValueError("reasons must be a tuple")

        # Validate score is finite
        _validate_weight(self.score, "score")

        # Validate ASCII-only reasons
        for i, reason in enumerate(self.reasons):
            _validate_ascii_only(reason, f"reasons[{i}]")


@dataclass(frozen=True, slots=True)
class ScoringReport:
    """Report from offline evaluation of healing outcome proposals.

    Recommendations are sorted deterministically by (-score, proposer_id, target_surface).
    Rejected reasons are ordered deterministically.
    """

    created_utc: int
    intake_record: HealingOutcomeIntakeRecord
    weights: ScoringWeights
    schema_version: int = 1
    source: str = "offline-evaluator"
    recommendations: tuple[ScoredRecommendation, ...] = field(default_factory=tuple)
    rejected_reasons: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate fields."""
        if self.schema_version < 1:
            raise ValueError("schema_version must be >= 1")
        if not isinstance(self.created_utc, int):
            raise ValueError("created_utc must be an integer")
        if not isinstance(self.source, str):
            raise ValueError("source must be a string")
        if not isinstance(self.recommendations, tuple):
            raise ValueError("recommendations must be a tuple")
        if not isinstance(self.rejected_reasons, tuple):
            raise ValueError("rejected_reasons must be a tuple")

        # Validate ASCII-only rejected reasons
        for i, reason in enumerate(self.rejected_reasons):
            _validate_ascii_only(reason, f"rejected_reasons[{i}]")

        # Verify recommendations are sorted deterministically
        if list(self.recommendations) != sorted(
            self.recommendations, key=lambda r: (-r.score, r.proposer_id, r.target_surface)
        ):
            raise ValueError("recommendations must be sorted by (-score, proposer_id, target_surface)")

    def canonical_bytes(self) -> bytes:
        """Get canonical byte representation for hashing.

        Returns:
            Stable byte representation using sorted JSON keys and stable rounding
        """
        # Convert to dict with stable serialization
        data = asdict(self)

        # Ensure stable JSON serialization
        canonical_json = json.dumps(data, sort_keys=True, separators=(",", ":"))

        # Return UTF-8 encoded bytes
        return canonical_json.encode("utf-8")

    def content_hash(self) -> str:
        """Get SHA-256 hash of canonical content.

        Returns:
            Hexadecimal SHA-256 hash
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


__all__ = [
    "ScoringWeights",
    "ScoredRecommendation",
    "ScoringReport",
    "_stable_round",
]
