"""Rollout & Rollback Contracts — Wave 7.0.12 (Schema Lock Only).

Defines schema-locked, frozen artifacts for safe rollout planning:
  - MetaLearningRolloutPlanArtifact  (versioned rollout config)
  - MetaLearningRollbackArtifact     (rollback record)

NO runtime behavior changes.  NO mutation logic.  NO automatic application.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from system_learning.enforcement.determinism import (
    deterministic_json,
    stable_sha256_json,
)
from system_learning.types.meta_learning_types import (
    MetaLearningChangePackageArtifact,
    _canonical_payload_json,
)

# =============================================================================
# §Wave7.0.12 — MetaLearningRolloutPlanArtifact
# =============================================================================

ROLLOUT_STRATEGIES = frozenset({"CANARY", "ALL_AT_ONCE"})
ROLLBACK_REASONS = frozenset(
    {
        "INVARIANT_VIOLATION",
        "METRIC_REGRESSION",
        "TIMEOUT",
        "MANUAL",
    }
)


@dataclass(frozen=True)
class MetaLearningRolloutPlanArtifact:
    """Frozen, schema-locked rollout plan.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - rollout_strategy must be CANARY or ALL_AT_ONCE.
    - canary_percent required iff CANARY (1-50 range); forbidden for ALL_AT_ONCE.
    - invariants must be non-empty list.
    - max_duration_minutes must be >= 1.
    - rollback_on_invariant_fail defaults True; always stored.
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["META_LEARNING_ROLLOUT_PLAN"]
    change_package_trace_id: str
    rollout_strategy: str
    canary_percent: int | None
    max_duration_minutes: int
    invariants: tuple[str, ...]
    rollback_on_invariant_fail: bool
    semantic_clock: SemanticClockSnapshot
    policy_config_hash: str | None
    trace_id: str

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "MetaLearningRolloutPlanArtifact")
        if self.artifact_type != "META_LEARNING_ROLLOUT_PLAN":
            raise ValueError(
                f"artifact_type must be 'META_LEARNING_ROLLOUT_PLAN', got {self.artifact_type!r}",
            )
        if self.rollout_strategy not in ROLLOUT_STRATEGIES:
            raise ValueError(f"INVALID_ROLLOUT_STRATEGY: {self.rollout_strategy!r}")
        if self.rollout_strategy == "CANARY":
            if self.canary_percent is None:
                raise ValueError("CANARY_PERCENT_REQUIRED_FOR_CANARY")
            if not (1 <= self.canary_percent <= 50):
                raise ValueError(
                    f"CANARY_PERCENT_OUT_OF_RANGE: {self.canary_percent} not in [1,50]",
                )
        elif self.canary_percent is not None:
            raise ValueError("CANARY_PERCENT_FORBIDDEN_FOR_ALL_AT_ONCE")
        if not self.invariants:
            raise ValueError("INVARIANTS_EMPTY")
        if self.max_duration_minutes < 1:
            raise ValueError("MAX_DURATION_MINUTES_LESS_THAN_ONE")

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "artifact_type": self.artifact_type,
            "canary_percent": self.canary_percent,
            "change_package_trace_id": self.change_package_trace_id,
            "invariants": list(self.invariants),
            "max_duration_minutes": self.max_duration_minutes,
            "policy_config_hash": self.policy_config_hash,
            "rollback_on_invariant_fail": self.rollback_on_invariant_fail,
            "rollout_strategy": self.rollout_strategy,
            "semantic_clock": self.semantic_clock.to_dict(),
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return deterministic_json(self.to_dict())


def build_meta_learning_rollout_plan(
    change_pkg: MetaLearningChangePackageArtifact,
    *,
    strategy: str,
    canary_percent: int | None = None,
    invariants: list[str],
    max_duration_minutes: int,
    rollback_on_invariant_fail: bool = True,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str | None = None,
) -> MetaLearningRolloutPlanArtifact:
    """Build a MetaLearningRolloutPlanArtifact with deterministic trace_id.

    Parameters
    ----------
    change_pkg : MetaLearningChangePackageArtifact
        The change package this rollout plan covers.
    strategy : str
        CANARY or ALL_AT_ONCE.
    canary_percent : int | None
        Required for CANARY (1-50), forbidden for ALL_AT_ONCE.
    invariants : list[str]
        Non-empty list of invariant checks to enforce during rollout.
    max_duration_minutes : int
        Maximum rollout duration (>= 1).
    rollback_on_invariant_fail : bool
        Whether to auto-rollback on invariant failure (default True).
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    policy_config_hash : str | None
        Optional hash of the governing policy config.

    Returns
    -------
    MetaLearningRolloutPlanArtifact
    """
    validate_semantic_clock(semantic_clock, "build_meta_learning_rollout_plan")
    if strategy not in ROLLOUT_STRATEGIES:
        raise ValueError(f"INVALID_ROLLOUT_STRATEGY: {strategy!r}")
    if not invariants:
        raise ValueError("INVARIANTS_EMPTY")

    inv_tuple = tuple(sorted(invariants))

    temp_payload = {
        "artifact_type": "META_LEARNING_ROLLOUT_PLAN",
        "canary_percent": canary_percent,
        "change_package_trace_id": change_pkg.trace_id,
        "invariants": list(inv_tuple),
        "max_duration_minutes": max_duration_minutes,
        "policy_config_hash": policy_config_hash,
        "rollback_on_invariant_fail": rollback_on_invariant_fail,
        "rollout_strategy": strategy,
        "semantic_clock": semantic_clock.to_dict(),
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = stable_sha256_json(json.loads(canonical))

    return MetaLearningRolloutPlanArtifact(
        artifact_type="META_LEARNING_ROLLOUT_PLAN",
        change_package_trace_id=change_pkg.trace_id,
        rollout_strategy=strategy,
        canary_percent=canary_percent,
        max_duration_minutes=max_duration_minutes,
        invariants=inv_tuple,
        rollback_on_invariant_fail=rollback_on_invariant_fail,
        semantic_clock=semantic_clock,
        policy_config_hash=policy_config_hash,
        trace_id=trace_id,
    )


# =============================================================================
# §Wave7.0.12 — MetaLearningRollbackArtifact
# =============================================================================


@dataclass(frozen=True)
class MetaLearningRollbackArtifact:
    """Frozen, schema-locked rollback record.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - rollback_reason must be a valid ROLLBACK_REASONS value.
    - rollout_trace_id links back to the rollout plan.
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["META_LEARNING_ROLLBACK"]
    rollout_trace_id: str
    rollback_reason: str
    semantic_clock: SemanticClockSnapshot
    policy_config_hash: str | None
    trace_id: str

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "MetaLearningRollbackArtifact")
        if self.artifact_type != "META_LEARNING_ROLLBACK":
            raise ValueError(
                f"artifact_type must be 'META_LEARNING_ROLLBACK', got {self.artifact_type!r}",
            )
        if self.rollback_reason not in ROLLBACK_REASONS:
            raise ValueError(f"INVALID_ROLLBACK_REASON: {self.rollback_reason!r}")

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "artifact_type": self.artifact_type,
            "policy_config_hash": self.policy_config_hash,
            "rollback_reason": self.rollback_reason,
            "rollout_trace_id": self.rollout_trace_id,
            "semantic_clock": self.semantic_clock.to_dict(),
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return deterministic_json(self.to_dict())


def build_meta_learning_rollback(
    rollout: MetaLearningRolloutPlanArtifact,
    *,
    rollback_reason: str,
    semantic_clock: SemanticClockSnapshot,
) -> MetaLearningRollbackArtifact:
    """Build a MetaLearningRollbackArtifact with deterministic trace_id.

    Parameters
    ----------
    rollout : MetaLearningRolloutPlanArtifact
        The rollout plan being rolled back.
    rollback_reason : str
        Must be one of ROLLBACK_REASONS.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.

    Returns
    -------
    MetaLearningRollbackArtifact
    """
    validate_semantic_clock(semantic_clock, "build_meta_learning_rollback")
    if rollback_reason not in ROLLBACK_REASONS:
        raise ValueError(f"INVALID_ROLLBACK_REASON: {rollback_reason!r}")

    temp_payload = {
        "artifact_type": "META_LEARNING_ROLLBACK",
        "policy_config_hash": rollout.policy_config_hash,
        "rollback_reason": rollback_reason,
        "rollout_trace_id": rollout.trace_id,
        "semantic_clock": semantic_clock.to_dict(),
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = stable_sha256_json(json.loads(canonical))

    return MetaLearningRollbackArtifact(
        artifact_type="META_LEARNING_ROLLBACK",
        rollout_trace_id=rollout.trace_id,
        rollback_reason=rollback_reason,
        semantic_clock=semantic_clock,
        policy_config_hash=rollout.policy_config_hash,
        trace_id=trace_id,
    )
