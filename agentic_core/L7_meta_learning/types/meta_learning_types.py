"""Meta-Learning Contracts — Waves 7.0.1 / 7.0.3 / 7.0.4 (Schema Lock Only).

Defines schema-locked, frozen artifacts for the meta-learning subsystem:
  - MetaLearningProposalArtifact   (Wave 7.0.1)
  - MetaLearningEvaluationArtifact (Wave 7.0.3)
  - MetaLearningApprovalArtifact   (Wave 7.0.4)

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


# =============================================================================
# §Wave7.0.3 — Evaluation Thresholds (deterministic, no smoothing)
# =============================================================================

EVAL_THRESHOLDS: dict[str, float] = {
    "IMPROVE_MIN_DELTA": 0.0,
    "NO_CHANGE_EPS": 0.0,
}


def _derive_verdict(delta: float) -> Literal["IMPROVE", "REGRESS", "NO_CHANGE"]:
    """Deterministic verdict from delta using EVAL_THRESHOLDS."""
    if delta > EVAL_THRESHOLDS["IMPROVE_MIN_DELTA"]:
        return "IMPROVE"
    if abs(delta) <= EVAL_THRESHOLDS["NO_CHANGE_EPS"]:
        return "NO_CHANGE"
    return "REGRESS"


# =============================================================================
# §Wave7.0.3 — MetaLearningEvaluationArtifact
# =============================================================================


@dataclass(frozen=True)
class MetaLearningEvaluationArtifact:
    """Frozen, schema-locked offline evaluation result.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - delta MUST equal candidate - baseline (computed deterministically).
    - verdict derived deterministically via _derive_verdict().
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["META_LEARNING_EVALUATION"]
    semantic_clock: SemanticClockSnapshot
    trace_id: str
    proposal_trace_id: str
    evaluator: str
    dataset_id: str
    metrics: ObjectiveSignal
    verdict: Literal["IMPROVE", "REGRESS", "NO_CHANGE"]
    evidence_hash: str
    policy_config_hash: str | None

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "MetaLearningEvaluationArtifact")
        if self.artifact_type != "META_LEARNING_EVALUATION":
            raise ValueError(
                f"artifact_type must be 'META_LEARNING_EVALUATION', got {self.artifact_type!r}",
            )

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "artifact_type": self.artifact_type,
            "dataset_id": self.dataset_id,
            "evaluator": self.evaluator,
            "evidence_hash": self.evidence_hash,
            "metrics": self.metrics.to_dict(),
            "policy_config_hash": self.policy_config_hash,
            "proposal_trace_id": self.proposal_trace_id,
            "semantic_clock": self.semantic_clock.to_dict(),
            "trace_id": self.trace_id,
            "verdict": self.verdict,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def build_meta_learning_evaluation(
    *,
    proposal: MetaLearningProposalArtifact,
    evaluator: str,
    dataset_id: str,
    baseline: float,
    candidate: float,
    evidence_hash: str,
    policy_config_hash: str | None = None,
) -> MetaLearningEvaluationArtifact:
    """Build a MetaLearningEvaluationArtifact with deterministic trace_id.

    Parameters
    ----------
    proposal : MetaLearningProposalArtifact
        The proposal being evaluated.
    evaluator : str
        Identifier of the evaluating subsystem.
    dataset_id : str
        Identifier of the evaluation dataset.
    baseline, candidate : float
        Metric values before and after the proposed change.
    evidence_hash : str
        SHA-256 of the evaluation evidence bundle.
    policy_config_hash : str | None
        Optional hash of the governing policy config.

    Returns
    -------
    MetaLearningEvaluationArtifact
        Frozen, deterministic evaluation artifact.
    """
    delta = candidate - baseline
    verdict = _derive_verdict(delta)
    metrics = ObjectiveSignal(
        metric_name=proposal.objective_signal.metric_name,
        baseline=baseline,
        candidate=candidate,
        delta=delta,
    )

    temp_payload = {
        "artifact_type": "META_LEARNING_EVALUATION",
        "dataset_id": dataset_id,
        "evaluator": evaluator,
        "evidence_hash": evidence_hash,
        "metrics": metrics.to_dict(),
        "policy_config_hash": policy_config_hash,
        "proposal_trace_id": proposal.trace_id,
        "semantic_clock": proposal.semantic_clock.to_dict(),
        "verdict": verdict,
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return MetaLearningEvaluationArtifact(
        artifact_type="META_LEARNING_EVALUATION",
        semantic_clock=proposal.semantic_clock,
        trace_id=trace_id,
        proposal_trace_id=proposal.trace_id,
        evaluator=evaluator,
        dataset_id=dataset_id,
        metrics=metrics,
        verdict=verdict,
        evidence_hash=evidence_hash,
        policy_config_hash=policy_config_hash,
    )


# =============================================================================
# §Wave7.0.4 — MetaLearningApprovalArtifact
# =============================================================================


@dataclass(frozen=True)
class MetaLearningApprovalArtifact:
    """Frozen, schema-locked approval decision.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - decision is explicit (no inference).
    - No "apply" fields, no file paths, no code payloads.
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["META_LEARNING_APPROVAL"]
    semantic_clock: SemanticClockSnapshot
    trace_id: str
    proposal_trace_id: str
    evaluation_trace_id: str
    approver: str
    decision: Literal["APPROVE", "REJECT"]
    rationale: str
    policy_config_hash: str | None

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "MetaLearningApprovalArtifact")
        if self.artifact_type != "META_LEARNING_APPROVAL":
            raise ValueError(
                f"artifact_type must be 'META_LEARNING_APPROVAL', got {self.artifact_type!r}",
            )

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "approver": self.approver,
            "artifact_type": self.artifact_type,
            "decision": self.decision,
            "evaluation_trace_id": self.evaluation_trace_id,
            "policy_config_hash": self.policy_config_hash,
            "proposal_trace_id": self.proposal_trace_id,
            "rationale": self.rationale,
            "semantic_clock": self.semantic_clock.to_dict(),
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def build_meta_learning_approval(
    *,
    evaluation: MetaLearningEvaluationArtifact,
    approver: str,
    decision: Literal["APPROVE", "REJECT"],
    rationale: str,
    policy_config_hash: str | None = None,
) -> MetaLearningApprovalArtifact:
    """Build a MetaLearningApprovalArtifact with deterministic trace_id.

    Parameters
    ----------
    evaluation : MetaLearningEvaluationArtifact
        The evaluation being approved or rejected.
    approver : str
        Identifier of the approving entity.
    decision : "APPROVE" | "REJECT"
        Explicit decision (no inference).
    rationale : str
        Human-readable justification.
    policy_config_hash : str | None
        Optional hash of the governing policy config.

    Returns
    -------
    MetaLearningApprovalArtifact
        Frozen, deterministic approval artifact.
    """
    temp_payload = {
        "approver": approver,
        "artifact_type": "META_LEARNING_APPROVAL",
        "decision": decision,
        "evaluation_trace_id": evaluation.trace_id,
        "policy_config_hash": policy_config_hash,
        "proposal_trace_id": evaluation.proposal_trace_id,
        "rationale": rationale,
        "semantic_clock": evaluation.semantic_clock.to_dict(),
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return MetaLearningApprovalArtifact(
        artifact_type="META_LEARNING_APPROVAL",
        semantic_clock=evaluation.semantic_clock,
        trace_id=trace_id,
        proposal_trace_id=evaluation.proposal_trace_id,
        evaluation_trace_id=evaluation.trace_id,
        approver=approver,
        decision=decision,
        rationale=rationale,
        policy_config_hash=policy_config_hash,
    )


# =============================================================================
# §Wave7.0.4 — Apply Prohibited Guard
# =============================================================================


def apply_meta_learning_proposal(*args, **kwargs) -> None:  # noqa: ARG001
    """Deliberate guardrail: proposals cannot be applied by any L7 code path in v5.4."""
    raise RuntimeError("META_LEARNING_APPLY_PROHIBITED")
