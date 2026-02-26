"""Apply Attempt Artifact — Wave 7.0.14 (Schema Lock).

Frozen, schema-locked artifact recording the outcome of an explicit
meta-learning apply attempt (DRY_RUN or APPLY).

NO automatic application.  Explicit invoke only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.interfaces.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from system_learning.enforcement.determinism import (
    deterministic_json,
    stable_sha256_json,
)
from system_learning.types.meta_learning_types import (
    _canonical_payload_json,
)


@dataclass(frozen=True)
class MetaLearningApplyAttemptArtifact:
    """Frozen, schema-locked apply attempt record.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - outcome is APPLIED or REJECTED (fail-closed).
    - reject_reason is None when APPLIED, a stable code when REJECTED.
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["META_LEARNING_APPLY_ATTEMPT"]
    change_package_trace_id: str
    rollout_trace_id: str
    policy_config_hash: str | None
    target_component: str
    apply_mode: Literal["DRY_RUN", "APPLY"]
    outcome: Literal["APPLIED", "REJECTED"]
    reject_reason: str | None
    details: dict[str, str]
    semantic_clock: SemanticClockSnapshot
    trace_id: str

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "MetaLearningApplyAttemptArtifact")
        if self.artifact_type != "META_LEARNING_APPLY_ATTEMPT":
            raise ValueError(
                f"artifact_type must be 'META_LEARNING_APPLY_ATTEMPT', got {self.artifact_type!r}",
            )

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "apply_mode": self.apply_mode,
            "artifact_type": self.artifact_type,
            "change_package_trace_id": self.change_package_trace_id,
            "details": dict(sorted(self.details.items())),
            "outcome": self.outcome,
            "policy_config_hash": self.policy_config_hash,
            "reject_reason": self.reject_reason,
            "rollout_trace_id": self.rollout_trace_id,
            "semantic_clock": self.semantic_clock.to_dict(),
            "target_component": self.target_component,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return deterministic_json(self.to_dict())


def build_apply_attempt(
    *,
    change_package_trace_id: str,
    rollout_trace_id: str,
    policy_config_hash: str | None,
    target_component: str,
    apply_mode: Literal["DRY_RUN", "APPLY"],
    outcome: Literal["APPLIED", "REJECTED"],
    reject_reason: str | None,
    details: dict[str, str],
    semantic_clock: SemanticClockSnapshot,
) -> MetaLearningApplyAttemptArtifact:
    """Build a MetaLearningApplyAttemptArtifact with deterministic trace_id."""
    validate_semantic_clock(semantic_clock, "build_apply_attempt")

    sorted_details = dict(sorted(details.items()))

    temp_payload: dict[str, Any] = {
        "apply_mode": apply_mode,
        "artifact_type": "META_LEARNING_APPLY_ATTEMPT",
        "change_package_trace_id": change_package_trace_id,
        "details": sorted_details,
        "outcome": outcome,
        "policy_config_hash": policy_config_hash,
        "reject_reason": reject_reason,
        "rollout_trace_id": rollout_trace_id,
        "semantic_clock": semantic_clock.to_dict(),
        "target_component": target_component,
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = stable_sha256_json(json.loads(canonical))

    return MetaLearningApplyAttemptArtifact(
        artifact_type="META_LEARNING_APPLY_ATTEMPT",
        change_package_trace_id=change_package_trace_id,
        rollout_trace_id=rollout_trace_id,
        policy_config_hash=policy_config_hash,
        target_component=target_component,
        apply_mode=apply_mode,
        outcome=outcome,
        reject_reason=reject_reason,
        details=sorted_details,
        semantic_clock=semantic_clock,
        trace_id=trace_id,
    )
