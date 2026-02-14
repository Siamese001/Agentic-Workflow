"""Meta-Learning Proposal Contract — Wave 7.0.1 (Schema Lock Only).

Defines the MetaLearningProposalArtifact frozen dataclass and the
build_meta_learning_proposal() deterministic builder.

NO runtime behavior changes.  NO mutation logic.  NO automatic application.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Literal

from agentic_core.L0_routing.types.v15_p2_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)

# =============================================================================
# §B — Immutable Components (Hard Boundary)
# =============================================================================

IMMUTABLE_COMPONENTS: frozenset[str] = frozenset(
    {
        "guardian_contract",
        "capability_enforcement",
        "inventory_schema",
        "evidence_hashing",
        "territory_map",
    }
)

# =============================================================================
# §A — Frozen Sub-Structures
# =============================================================================


@dataclass(frozen=True)
class ObjectiveSignal:
    """Metric evidence for a proposed change."""

    metric_name: str
    baseline: float
    candidate: float
    delta: float

    def to_dict(self) -> dict[str, object]:
        """Deterministic serialization: keys sorted alphabetically."""
        return {
            "baseline": self.baseline,
            "candidate": self.candidate,
            "delta": self.delta,
            "metric_name": self.metric_name,
        }


@dataclass(frozen=True)
class ProposedChange:
    """Before/after change pair.  Stored as canonical JSON for immutability."""

    before_canonical: str
    after_canonical: str

    def to_dict(self) -> dict[str, object]:
        """Deterministic serialization: keys sorted alphabetically."""
        return {
            "after": json.loads(self.after_canonical),
            "before": json.loads(self.before_canonical),
        }

    @classmethod
    def from_dicts(cls, before: dict, after: dict) -> ProposedChange:
        """Build from plain dicts — canonicalizes on construction."""
        return cls(
            before_canonical=json.dumps(before, sort_keys=True, separators=(",", ":")),
            after_canonical=json.dumps(after, sort_keys=True, separators=(",", ":")),
        )


# =============================================================================
# §A — MetaLearningProposalArtifact
# =============================================================================


@dataclass(frozen=True)
class MetaLearningProposalArtifact:
    """Frozen, schema-locked meta-learning proposal.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - canonical serialization (sort_keys=True).
    - No executable code, no file paths, no dynamic imports.
    - No fields allowing schema or guardrail modification.
    - target_component ∈ IMMUTABLE_COMPONENTS → ValueError("IMMUTABLE_TARGET").
    """

    artifact_type: Literal["META_LEARNING_PROPOSAL"]
    semantic_clock: SemanticClockSnapshot
    trace_id: str
    proposer: str
    target_component: str
    proposed_change: ProposedChange
    objective_signal: ObjectiveSignal
    evidence_hash: str
    policy_config_hash: str | None

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "MetaLearningProposalArtifact")
        if self.target_component in IMMUTABLE_COMPONENTS:
            raise ValueError("IMMUTABLE_TARGET")
        if self.artifact_type != "META_LEARNING_PROPOSAL":
            raise ValueError(
                f"artifact_type must be 'META_LEARNING_PROPOSAL', got {self.artifact_type!r}",
            )

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "artifact_type": self.artifact_type,
            "evidence_hash": self.evidence_hash,
            "objective_signal": self.objective_signal.to_dict(),
            "policy_config_hash": self.policy_config_hash,
            "proposed_change": self.proposed_change.to_dict(),
            "proposer": self.proposer,
            "semantic_clock": self.semantic_clock.to_dict(),
            "target_component": self.target_component,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


# =============================================================================
# §A — Deterministic Builder
# =============================================================================


def _canonical_payload_json(payload: dict) -> str:
    """Canonical JSON of payload excluding trace_id."""
    filtered = {k: v for k, v in payload.items() if k != "trace_id"}
    return json.dumps(filtered, sort_keys=True, separators=(",", ":"))


def build_meta_learning_proposal(
    *,
    semantic_clock: SemanticClockSnapshot,
    proposer: str,
    target_component: str,
    before: dict,
    after: dict,
    metric_name: str,
    baseline: float,
    candidate: float,
    evidence_hash: str,
    policy_config_hash: str | None = None,
) -> MetaLearningProposalArtifact:
    """Build a MetaLearningProposalArtifact with deterministic trace_id.

    Parameters
    ----------
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    proposer : str
        Identifier of the proposing subsystem.
    target_component : str
        Target of the proposed change (must NOT be in IMMUTABLE_COMPONENTS).
    before, after : dict
        State before and after the proposed change.
    metric_name : str
        Name of the objective metric.
    baseline, candidate : float
        Metric values before and after the proposed change.
    evidence_hash : str
        SHA-256 of the supporting evidence bundle.
    policy_config_hash : str | None
        Optional hash of the governing policy config.

    Returns
    -------
    MetaLearningProposalArtifact
        Frozen, deterministic proposal artifact.
    """
    proposed_change = ProposedChange.from_dicts(before, after)
    delta = candidate - baseline
    objective_signal = ObjectiveSignal(
        metric_name=metric_name,
        baseline=baseline,
        candidate=candidate,
        delta=delta,
    )

    temp_payload = {
        "artifact_type": "META_LEARNING_PROPOSAL",
        "evidence_hash": evidence_hash,
        "objective_signal": objective_signal.to_dict(),
        "policy_config_hash": policy_config_hash,
        "proposed_change": proposed_change.to_dict(),
        "proposer": proposer,
        "semantic_clock": semantic_clock.to_dict(),
        "target_component": target_component,
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return MetaLearningProposalArtifact(
        artifact_type="META_LEARNING_PROPOSAL",
        semantic_clock=semantic_clock,
        trace_id=trace_id,
        proposer=proposer,
        target_component=target_component,
        proposed_change=proposed_change,
        objective_signal=objective_signal,
        evidence_hash=evidence_hash,
        policy_config_hash=policy_config_hash,
    )
