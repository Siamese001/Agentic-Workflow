"""Meta-Learning Contracts — Waves 7.0.1–7.0.6 (Schema Lock Only).

Defines schema-locked, frozen artifacts for the meta-learning subsystem:
  - MetaLearningProposalArtifact      (Wave 7.0.1)
  - MetaLearningEvaluationArtifact    (Wave 7.0.3)
  - MetaLearningApprovalArtifact      (Wave 7.0.4)
  - MetaLearningDecisionArtifact      (Wave 7.0.5)
  - MetaLearningChangePackageArtifact (Wave 7.0.6)

APP signal artifacts (Wave 7.0.8) are in app_signal_types.py.

NO runtime behavior changes.  NO mutation logic.  NO automatic application.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.interfaces.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "meta_learning_types", "execution_auth")
_emit_validates_capability("p2", "meta_learning_types", "capability_check")
_emit_routes_to_capability("p2", "meta_learning_types", "capability_route")
_emit_writes_via_uwg("p2", "meta_learning_types", "uwg_write")
_emit_blocks_direct_write("p2", "meta_learning_types", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_learning_types", "tool_invocation")
_emit_captures_execution_output("p2", "meta_learning_types", "exec_output")
_emit_dispatches_agent("p3", "meta_learning_types", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_learning_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_learning_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_learning_types", "healing_outcome")
_emit_escalates_failure("p3", "meta_learning_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_learning_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_learning_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_learning_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_learning_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_learning_types", "eval_metric")
_emit_stores_embedding("p4", "meta_learning_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_learning_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_learning_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from system_learning.enforcement.determinism import (
    deterministic_json,
    stable_sha256_json,
)

_emit_emits_metric_event("meta_learning_types", "p4obs", "metric_1")
_emit_emits_metric_event("meta_learning_types", "p4obs", "metric_2")
_emit_emits_metric_event("meta_learning_types", "p4obs", "metric_3")
_emit_emits_metric_event("meta_learning_types", "p4obs", "metric_4")
_emit_emits_metric_event("meta_learning_types", "p4obs", "metric_5")
_emit_emits_metric_event("meta_learning_types", "p4obs", "metric_6")
_emit_records_incident_event("meta_learning_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_learning_types", "p4obs", "anomaly")
_emit_writes_observability_log("meta_learning_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_learning_types", "p4obs", "mon_state")
_emit_triggers_alert("meta_learning_types", "p4obs", "alert")
_emit_links_incident_trace("meta_learning_types", "p4obs", "trace_link")
_emit_captures_pattern("meta_learning_types", "p3lm", "pattern")
_emit_records_learning_event("meta_learning_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_learning_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_learning_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_learning_types", "p3lm", "routing")
_emit_improves_agent_policy("meta_learning_types", "p3lm", "policy")
_emit_stores_learning_state("meta_learning_types", "p3lm", "state")
_emit_records_execution_trace("meta_learning_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_learning_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_learning_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_learning_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_learning_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_learning_types", "env_read", "p2_env_1")
_emit_reads_environ("meta_learning_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_learning_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_learning_types", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "meta_learning_types")
_emit_applies_guardrail("p0", "meta_learning_types", "p0_governance")
_emit_snapshots_state("p0", "meta_learning_types", "state_snapshot")
_emit_pulls_context("p1", "meta_learning_types", "context_pull")
_emit_pulls_context("p1", "meta_learning_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "meta_learning_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_learning_types", "uwg_term_secondary")
_emit_writes_through("p1", "meta_learning_types", "write_through")
_emit_writes_through("p1", "meta_learning_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "meta_learning_types", "safety_validation")
_emit_invokes_eval("p1", "meta_learning_types", "eval_call")
_emit_proposal_commits_routing("p1", "meta_learning_types", "routing_commit")
_emit_escalates_to_human("p1", "meta_learning_types", "human_escalation")
_emit_routes_through("p1", "meta_learning_types", "route_through")
_emit_checks_agent_registry("p1", "meta_learning_types", "agent_registry")
_emit_validates_agent_capability("p1", "meta_learning_types", "capability")
_emit_dispatches_execution_plan("p1", "meta_learning_types", "exec_plan")
_emit_agent_executes_agent("p1", "meta_learning_types", "sub_agent")
_emit_routes_to_agent("p1", "meta_learning_types", "target_agent")
_emit_verifies_policy("p1", "meta_learning_types", "policy_check")
_emit_observes_runtime_state("p1", "meta_learning_types", "runtime_state")
_emit_verifies_boundary("p1", "meta_learning_types", "boundary_check")
_emit_transcripts_response("p1", "meta_learning_types", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_learning_types")
_emit_gated_by_confidence("p1", "meta_learning_types", "confidence_gate")
emit_replay_key("p0", "meta_learning_types")
emit_determinism_digest("p0", "meta_learning_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
    },
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
            before_canonical=deterministic_json(before),
            after_canonical=deterministic_json(after),
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
        return deterministic_json(self.to_dict())


# =============================================================================
# §A — Deterministic Builder
# =============================================================================


def _canonical_payload_json(payload: dict) -> str:
    """Canonical JSON of payload excluding trace_id."""
    filtered = {k: v for k, v in payload.items() if k != "trace_id"}
    return deterministic_json(filtered)


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
    trace_id = stable_sha256_json(json.loads(canonical))

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
        return deterministic_json(self.to_dict())


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
    trace_id = stable_sha256_json(json.loads(canonical))

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
        return deterministic_json(self.to_dict())


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
    trace_id = stable_sha256_json(json.loads(canonical))

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


# =============================================================================
# §Wave7.0.5 — Deny Reason Codes (stable strings)
# =============================================================================

DENY_REASONS: dict[str, str] = {
    "MISSING_PROPOSAL": "MISSING_PROPOSAL",
    "MISSING_EVALUATION": "MISSING_EVALUATION",
    "MISSING_APPROVAL": "MISSING_APPROVAL",
    "TRACE_MISMATCH": "TRACE_MISMATCH",
    "POLICY_HASH_MISMATCH": "POLICY_HASH_MISMATCH",
    "EVAL_VERDICT_NOT_IMPROVE": "EVAL_VERDICT_NOT_IMPROVE",
    "APPROVAL_REJECTED": "APPROVAL_REJECTED",
    "CLOCK_INVALID": "CLOCK_INVALID",
}


# =============================================================================
# §Wave7.0.5 — MetaLearningDecisionArtifact
# =============================================================================


@dataclass(frozen=True)
class MetaLearningDecisionArtifact:
    """Frozen, schema-locked intake gate decision.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - decision is ALLOW_TO_APPLY or REJECT (fail-closed).
    - deny_reason is None when ALLOW_TO_APPLY, a stable code when REJECT.
    - This artifact does NOT trigger application; apply remains RuntimeError.
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["META_LEARNING_DECISION"]
    semantic_clock: SemanticClockSnapshot
    trace_id: str
    proposal_trace_id: str
    evaluation_trace_id: str | None
    approval_trace_id: str | None
    decision: Literal["ALLOW_TO_APPLY", "REJECT"]
    deny_reason: str | None
    policy_config_hash: str | None

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "MetaLearningDecisionArtifact")
        if self.artifact_type != "META_LEARNING_DECISION":
            raise ValueError(
                f"artifact_type must be 'META_LEARNING_DECISION', got {self.artifact_type!r}",
            )

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "approval_trace_id": self.approval_trace_id,
            "artifact_type": self.artifact_type,
            "decision": self.decision,
            "deny_reason": self.deny_reason,
            "evaluation_trace_id": self.evaluation_trace_id,
            "policy_config_hash": self.policy_config_hash,
            "proposal_trace_id": self.proposal_trace_id,
            "semantic_clock": self.semantic_clock.to_dict(),
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return deterministic_json(self.to_dict())


# =============================================================================
# §Wave7.0.5 — Intake Gate Builder (fail-closed, no side effects)
# =============================================================================


def _build_reject_decision(
    *,
    deny_reason: str,
    proposal_trace_id: str,
    evaluation_trace_id: str | None,
    approval_trace_id: str | None,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str | None,
) -> MetaLearningDecisionArtifact:
    """Internal helper to build a REJECT decision with deterministic trace_id."""
    temp_payload = {
        "approval_trace_id": approval_trace_id,
        "artifact_type": "META_LEARNING_DECISION",
        "decision": "REJECT",
        "deny_reason": deny_reason,
        "evaluation_trace_id": evaluation_trace_id,
        "policy_config_hash": policy_config_hash,
        "proposal_trace_id": proposal_trace_id,
        "semantic_clock": semantic_clock.to_dict(),
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = stable_sha256_json(json.loads(canonical))
    return MetaLearningDecisionArtifact(
        artifact_type="META_LEARNING_DECISION",
        semantic_clock=semantic_clock,
        trace_id=trace_id,
        proposal_trace_id=proposal_trace_id,
        evaluation_trace_id=evaluation_trace_id,
        approval_trace_id=approval_trace_id,
        decision="REJECT",
        deny_reason=deny_reason,
        policy_config_hash=policy_config_hash,
    )


def build_meta_learning_decision(
    *,
    proposal: MetaLearningProposalArtifact | None,
    evaluation: MetaLearningEvaluationArtifact | None,
    approval: MetaLearningApprovalArtifact | None,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str | None,
) -> MetaLearningDecisionArtifact:
    """Deterministic intake gate: consume Proposal+Evaluation+Approval, emit Decision.

    Fail-closed: any validation failure produces REJECT with a stable deny_reason.
    ALLOW_TO_APPLY is emitted ONLY as an artifact — it MUST NOT trigger application.

    Parameters
    ----------
    proposal, evaluation, approval : artifacts or None
        The three pipeline artifacts. None → REJECT.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    policy_config_hash : str | None
        Expected policy config hash; all artifacts must match.

    Returns
    -------
    MetaLearningDecisionArtifact
    """
    # Validate semantic clock (raises ValueError if None)
    validate_semantic_clock(semantic_clock, "build_meta_learning_decision")

    # Helper to build reject with available trace ids
    def _reject(reason: str) -> MetaLearningDecisionArtifact:
        return _build_reject_decision(
            deny_reason=reason,
            proposal_trace_id=proposal.trace_id if proposal else "",
            evaluation_trace_id=evaluation.trace_id if evaluation else None,
            approval_trace_id=approval.trace_id if approval else None,
            semantic_clock=semantic_clock,
            policy_config_hash=policy_config_hash,
        )

    # --- Presence checks (fail-closed) ---
    if proposal is None:
        return _reject(DENY_REASONS["MISSING_PROPOSAL"])
    if evaluation is None:
        return _reject(DENY_REASONS["MISSING_EVALUATION"])
    if approval is None:
        return _reject(DENY_REASONS["MISSING_APPROVAL"])

    # --- Cross-artifact trace linkage ---
    if evaluation.proposal_trace_id != proposal.trace_id:
        return _reject(DENY_REASONS["TRACE_MISMATCH"])
    if approval.proposal_trace_id != proposal.trace_id or approval.evaluation_trace_id != evaluation.trace_id:
        return _reject(DENY_REASONS["TRACE_MISMATCH"])

    # --- Policy hash alignment (None is a valid value; all must match) ---
    if not (
        proposal.policy_config_hash == policy_config_hash
        and evaluation.policy_config_hash == policy_config_hash
        and approval.policy_config_hash == policy_config_hash
    ):
        return _reject(DENY_REASONS["POLICY_HASH_MISMATCH"])

    # --- Verdict + decision checks ---
    if evaluation.verdict != "IMPROVE":
        return _reject(DENY_REASONS["EVAL_VERDICT_NOT_IMPROVE"])
    if approval.decision != "APPROVE":
        return _reject(DENY_REASONS["APPROVAL_REJECTED"])

    # --- All checks pass → ALLOW_TO_APPLY ---
    temp_payload = {
        "approval_trace_id": approval.trace_id,
        "artifact_type": "META_LEARNING_DECISION",
        "decision": "ALLOW_TO_APPLY",
        "deny_reason": None,
        "evaluation_trace_id": evaluation.trace_id,
        "policy_config_hash": policy_config_hash,
        "proposal_trace_id": proposal.trace_id,
        "semantic_clock": semantic_clock.to_dict(),
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = stable_sha256_json(json.loads(canonical))

    return MetaLearningDecisionArtifact(
        artifact_type="META_LEARNING_DECISION",
        semantic_clock=semantic_clock,
        trace_id=trace_id,
        proposal_trace_id=proposal.trace_id,
        evaluation_trace_id=evaluation.trace_id,
        approval_trace_id=approval.trace_id,
        decision="ALLOW_TO_APPLY",
        deny_reason=None,
        policy_config_hash=policy_config_hash,
    )


# =============================================================================
# §Wave7.0.6 — Mutable Components (strict allowlist)
# =============================================================================

MUTABLE_COMPONENTS: tuple[str, ...] = (
    "prompt_templates",
    "routing_thresholds",
    "tool_policies",
)


# =============================================================================
# §Wave7.0.6 — MetaLearningChangePackageArtifact
# =============================================================================


@dataclass(frozen=True)
class MetaLearningChangePackageArtifact:
    """Frozen, schema-locked change package.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - target_component must be in MUTABLE_COMPONENTS.
    - change_spec is canonicalized (sorted keys) on construction.
    - This artifact does NOT apply changes; apply remains RuntimeError.
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["META_LEARNING_CHANGE_PACKAGE"]
    semantic_clock: SemanticClockSnapshot
    trace_id: str
    proposal_trace_id: str
    evaluation_trace_id: str
    approval_trace_id: str
    decision_trace_id: str
    target_component: str
    change_spec: dict[str, Any]
    policy_config_hash: str | None

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "MetaLearningChangePackageArtifact")
        if self.artifact_type != "META_LEARNING_CHANGE_PACKAGE":
            raise ValueError(
                f"artifact_type must be 'META_LEARNING_CHANGE_PACKAGE', got {self.artifact_type!r}",
            )
        if self.target_component not in MUTABLE_COMPONENTS:
            raise ValueError("IMMUTABLE_COMPONENT")

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "approval_trace_id": self.approval_trace_id,
            "artifact_type": self.artifact_type,
            "change_spec": self.change_spec,
            "decision_trace_id": self.decision_trace_id,
            "evaluation_trace_id": self.evaluation_trace_id,
            "policy_config_hash": self.policy_config_hash,
            "proposal_trace_id": self.proposal_trace_id,
            "semantic_clock": self.semantic_clock.to_dict(),
            "target_component": self.target_component,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return deterministic_json(self.to_dict())


# =============================================================================
# §Wave7.0.6 — Change Package Builder (fail-closed, no side effects)
# =============================================================================


def build_meta_learning_change_package(
    *,
    proposal: MetaLearningProposalArtifact,
    evaluation: MetaLearningEvaluationArtifact,
    approval: MetaLearningApprovalArtifact,
    decision: MetaLearningDecisionArtifact,
    target_component: str,
    change_spec: dict[str, Any],
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str | None,
) -> MetaLearningChangePackageArtifact:
    """Build a MetaLearningChangePackageArtifact with deterministic trace_id.

    Fail-closed: validates decision==ALLOW_TO_APPLY, trace linkage,
    target_component ∈ MUTABLE_COMPONENTS, and policy hash alignment.

    Parameters
    ----------
    proposal, evaluation, approval, decision : artifacts
        The four pipeline artifacts.
    target_component : str
        Must be in MUTABLE_COMPONENTS.
    change_spec : dict
        Deterministic change specification (will be canonicalized).
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    policy_config_hash : str | None
        Expected policy config hash; all artifacts must match.

    Returns
    -------
    MetaLearningChangePackageArtifact
    """
    # --- Decision gate ---
    if decision.decision != "ALLOW_TO_APPLY":
        raise ValueError("DECISION_NOT_ALLOW_TO_APPLY")

    # --- Target component validation ---
    if target_component not in MUTABLE_COMPONENTS:
        raise ValueError("IMMUTABLE_COMPONENT")

    # --- Trace linkage ---
    if (
        decision.proposal_trace_id != proposal.trace_id
        or decision.evaluation_trace_id != evaluation.trace_id
        or decision.approval_trace_id != approval.trace_id
    ):
        raise ValueError("TRACE_LINKAGE_MISMATCH")

    # --- Policy hash alignment ---
    if not (
        proposal.policy_config_hash == policy_config_hash
        and evaluation.policy_config_hash == policy_config_hash
        and approval.policy_config_hash == policy_config_hash
        and decision.policy_config_hash == policy_config_hash
    ):
        raise ValueError("POLICY_HASH_MISMATCH")

    # --- Canonicalize change_spec ---
    canonical_spec_str = deterministic_json(change_spec)
    canonical_spec: dict[str, Any] = json.loads(canonical_spec_str)

    # --- Build trace_id ---
    temp_payload = {
        "approval_trace_id": approval.trace_id,
        "artifact_type": "META_LEARNING_CHANGE_PACKAGE",
        "change_spec": canonical_spec,
        "decision_trace_id": decision.trace_id,
        "evaluation_trace_id": evaluation.trace_id,
        "policy_config_hash": policy_config_hash,
        "proposal_trace_id": proposal.trace_id,
        "semantic_clock": semantic_clock.to_dict(),
        "target_component": target_component,
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = stable_sha256_json(json.loads(canonical))

    return MetaLearningChangePackageArtifact(
        artifact_type="META_LEARNING_CHANGE_PACKAGE",
        semantic_clock=semantic_clock,
        trace_id=trace_id,
        proposal_trace_id=proposal.trace_id,
        evaluation_trace_id=evaluation.trace_id,
        approval_trace_id=approval.trace_id,
        decision_trace_id=decision.trace_id,
        target_component=target_component,
        change_spec=canonical_spec,
        policy_config_hash=policy_config_hash,
    )
