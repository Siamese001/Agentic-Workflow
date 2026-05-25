"""Optimization types for the ADG-driven meta-learning bus.

Covers the proposal → validation → commit → reward pipeline:

  OptimizationProposal      — controlled change proposal from RCA cluster
  ValidationResult          — output of the four-gate validation pipeline
  OptimizationCommit        — versioned commit of a validated proposal
  GovernanceRewardSignal    — per-trace reward model signal
  GovernanceRewardScore     — aggregated reward score for a proposal

Design invariants
-----------------
1. All types are frozen dataclasses — no mutation after construction.
2. No wall-clock reads; ``timestamp_utc`` always caller-supplied.
3. stable_hash() = SHA-256(deterministic_json(to_dict())) for every type.
4. Proposals MUST NOT mutate system state directly; they are proposal-only
   containers.  Actual application is gated by ``ValidationResult.validation_pass``
   and downstream ``OptimizationCommit`` creation.
5. The ADG relation ``proposal_commits_optimization`` is created only when
   ``OptimizationCommit`` is produced from a passing ``ValidationResult``.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

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

_emit_authorize_and_execute("p2", "optimization_types", "execution_auth")
_emit_validates_capability("p2", "optimization_types", "capability_check")
_emit_routes_to_capability("p2", "optimization_types", "capability_route")
_emit_writes_via_uwg("p2", "optimization_types", "uwg_write")
_emit_blocks_direct_write("p2", "optimization_types", "direct_write_block")
_emit_records_tool_invocation("p2", "optimization_types", "tool_invocation")
_emit_captures_execution_output("p2", "optimization_types", "exec_output")
_emit_dispatches_agent("p3", "optimization_types", "agent_dispatch")
_emit_coordinates_agents("p3", "optimization_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "optimization_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "optimization_types", "healing_outcome")
_emit_escalates_failure("p3", "optimization_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "optimization_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "optimization_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "optimization_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "optimization_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "optimization_types", "eval_metric")
_emit_stores_embedding("p4", "optimization_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "optimization_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "optimization_types", "exec_snapshot_link")
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
from agentic_core.L6_system_learning.enforcement.determinism import deterministic_json
from tqdm import tqdm

_emit_emits_metric_event("optimization_types", "p4obs", "metric_1")
_emit_emits_metric_event("optimization_types", "p4obs", "metric_2")
_emit_emits_metric_event("optimization_types", "p4obs", "metric_3")
_emit_emits_metric_event("optimization_types", "p4obs", "metric_4")
_emit_emits_metric_event("optimization_types", "p4obs", "metric_5")
_emit_emits_metric_event("optimization_types", "p4obs", "metric_6")
_emit_records_incident_event("optimization_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("optimization_types", "p4obs", "anomaly")
_emit_writes_observability_log("optimization_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("optimization_types", "p4obs", "mon_state")
_emit_triggers_alert("optimization_types", "p4obs", "alert")
_emit_links_incident_trace("optimization_types", "p4obs", "trace_link")
_emit_captures_pattern("optimization_types", "p3lm", "pattern")
_emit_records_learning_event("optimization_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("optimization_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("optimization_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("optimization_types", "p3lm", "routing")
_emit_improves_agent_policy("optimization_types", "p3lm", "policy")
_emit_stores_learning_state("optimization_types", "p3lm", "state")
_emit_records_execution_trace("optimization_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("optimization_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("optimization_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("optimization_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("optimization_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("optimization_types", "env_read", "p2_env_1")
_emit_reads_environ("optimization_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("optimization_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("optimization_types", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "optimization_types")
_emit_applies_guardrail("p0", "optimization_types", "p0_governance")
_emit_snapshots_state("p0", "optimization_types", "state_snapshot")
_emit_pulls_context("p1", "optimization_types", "context_pull")
_emit_pulls_context("p1", "optimization_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "optimization_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "optimization_types", "uwg_term_secondary")
_emit_writes_through("p1", "optimization_types", "write_through")
_emit_writes_through("p1", "optimization_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "optimization_types", "safety_validation")
_emit_invokes_eval("p1", "optimization_types", "eval_call")
_emit_proposal_commits_routing("p1", "optimization_types", "routing_commit")
_emit_escalates_to_human("p1", "optimization_types", "human_escalation")
_emit_routes_through("p1", "optimization_types", "route_through")
_emit_checks_agent_registry("p1", "optimization_types", "agent_registry")
_emit_validates_agent_capability("p1", "optimization_types", "capability")
_emit_dispatches_execution_plan("p1", "optimization_types", "exec_plan")
_emit_agent_executes_agent("p1", "optimization_types", "sub_agent")
_emit_routes_to_agent("p1", "optimization_types", "target_agent")
_emit_verifies_policy("p1", "optimization_types", "policy_check")
_emit_observes_runtime_state("p1", "optimization_types", "runtime_state")
_emit_verifies_boundary("p1", "optimization_types", "boundary_check")
_emit_transcripts_response("p1", "optimization_types", "transcript")
_emit_hard_fails_untranscripted("p1", "optimization_types")
_emit_gated_by_confidence("p1", "optimization_types", "confidence_gate")
emit_replay_key("p0", "optimization_types")
emit_determinism_digest("p0", "optimization_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Change type literals
# ---------------------------------------------------------------------------

_VALID_CHANGE_TYPES: frozenset[str] = frozenset(
    {
        "ROUTING_RULE_ADJUSTMENT",
        "CONFIDENCE_THRESHOLD_UPDATE",
        "RETRIEVAL_RANKING_ADJUSTMENT",
        "EMBEDDING_CORPUS_EXPANSION",
        "GUARDRAIL_REFINEMENT",
        "HEALER_ROUTING_IMPROVEMENT",
        "PROMPT_TUNING",
        "DPO_DATASET_GENERATION",
    },
)

_VALID_RISK_CLASSES: frozenset[str] = frozenset(
    {"LOW", "MEDIUM", "HIGH", "CRITICAL"},
)

_VALID_VALIDATION_GATES: frozenset[str] = frozenset(
    {
        "REPLAY_VALIDATION",
        "POLICY_VALIDATION",
        "GUARDRAIL_VALIDATION",
        "DETERMINISM_VERIFICATION",
        "REGRESSION_TESTING",
    },
)


# ---------------------------------------------------------------------------
# OptimizationProposal
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OptimizationProposal:
    """Controlled optimization proposal generated from an RCA cluster.

    Proposals are strictly informational — they MUST NOT mutate routing,
    safety, config, or any system state directly.  Downstream validation
    and the OptimizationCommit stage gate actual application.

    Attributes
    ----------
    proposal_id : str
        Content-addressed ID = stable_hash().
    cluster_id : str
        ID of the RCACluster that generated this proposal.
    proposed_change_type : str
        Type of change being proposed (see ``_VALID_CHANGE_TYPES``).
    affected_component : str
        ADG entity name of the target component.
    expected_outcome : str
        Human-readable description of the expected improvement.
    risk_class : str
        Risk level of this change (``"LOW"``, ``"MEDIUM"``, ``"HIGH"``,
        ``"CRITICAL"``).
    change_spec : tuple[tuple[str, str], ...]
        Deterministic key-value pairs describing the proposed change
        (sorted for stability, values are strings for serializability).
    evidence_bundle_hashes : tuple[str, ...]
        stable_hash() values of the RCACluster and feature records that
        support this proposal.
    reward_score : float | None
        Governance reward score (set by GovernanceRewardModel; None
        until scored).
    policy_hash : str | None
        Policy config hash active when this proposal was generated.
    timestamp_utc : int
        Caller-supplied Unix timestamp.
    """

    proposal_id: str
    cluster_id: str
    proposed_change_type: str
    affected_component: str
    expected_outcome: str
    risk_class: str
    change_spec: tuple[tuple[str, str], ...]
    evidence_bundle_hashes: tuple[str, ...]
    reward_score: float | None
    policy_hash: str | None
    timestamp_utc: int

    def __post_init__(self) -> None:
        if not self.cluster_id:
            raise ValueError("cluster_id must not be empty")
        if self.proposed_change_type not in _VALID_CHANGE_TYPES:
            raise ValueError(
                f"proposed_change_type must be one of "
                f"{sorted(_VALID_CHANGE_TYPES)}, got {self.proposed_change_type!r}",
            )
        if self.risk_class not in _VALID_RISK_CLASSES:
            raise ValueError(
                f"risk_class must be one of {sorted(_VALID_RISK_CLASSES)}, got {self.risk_class!r}",
            )
        if self.reward_score is not None and not 0.0 <= self.reward_score <= 1.0:
            raise ValueError(
                f"reward_score must be in [0.0, 1.0] or None, got {self.reward_score}",
            )

    def _canonical_dict(self) -> dict:
        return {
            "affected_component": self.affected_component,
            "change_spec": sorted(self.change_spec),
            "cluster_id": self.cluster_id,
            "evidence_bundle_hashes": sorted(self.evidence_bundle_hashes),
            "expected_outcome": self.expected_outcome,
            "policy_hash": self.policy_hash,
            "proposal_id": self.proposal_id,
            "proposed_change_type": self.proposed_change_type,
            "reward_score": (round(self.reward_score, 6) if self.reward_score is not None else None),
            "risk_class": self.risk_class,
            "timestamp_utc": self.timestamp_utc,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(
            deterministic_json(self._canonical_dict()).encode("utf-8"),
        ).hexdigest()

    def to_dict(self) -> dict:
        return self._canonical_dict()

    def to_json(self) -> str:
        return deterministic_json(self._canonical_dict())


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ValidationResult:
    """Output of the four-gate validation pipeline for a proposal.

    Only proposals with ``validation_pass=True`` proceed to commit.

    Attributes
    ----------
    result_id : str
        Content-addressed ID = stable_hash().
    proposal_id : str
        ID of the validated OptimizationProposal.
    validation_pass : bool
        True iff all required gates passed.
    replay_safe : bool
        Whether the proposal passed replay validation.
    policy_safe : bool
        Whether the proposal passed policy validation.
    guardrail_safe : bool
        Whether the proposal passed guardrail validation.
    determinism_verified : bool
        Whether determinism verification passed.
    regression_risk : str
        Regression risk assessment (``"NONE"``, ``"LOW"``, ``"MEDIUM"``,
        ``"HIGH"``).
    gate_results : tuple[tuple[str, bool], ...]
        Sorted tuple of (gate_name, passed) for each validation gate.
    denial_reasons : tuple[str, ...]
        Gate names that failed (empty if validation_pass=True).
    policy_hash : str | None
        Policy config hash active during validation.
    timestamp_utc : int
        Caller-supplied Unix timestamp.
    """

    result_id: str
    proposal_id: str
    validation_pass: bool
    replay_safe: bool
    policy_safe: bool
    guardrail_safe: bool
    determinism_verified: bool
    regression_risk: str
    gate_results: tuple[tuple[str, bool], ...]
    denial_reasons: tuple[str, ...]
    policy_hash: str | None
    timestamp_utc: int

    _VALID_REGRESSION_RISKS: frozenset[str] = field(
        default=frozenset({"NONE", "LOW", "MEDIUM", "HIGH"}),
        init=False,
        compare=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        if not self.proposal_id:
            raise ValueError("proposal_id must not be empty")
        if self.regression_risk not in self._VALID_REGRESSION_RISKS:
            raise ValueError(
                f"regression_risk must be one of "
                f"{sorted(self._VALID_REGRESSION_RISKS)}, "
                f"got {self.regression_risk!r}",
            )
        # Consistency check: validation_pass must match gate results
        if self.validation_pass and self.denial_reasons:
            raise ValueError(
                "validation_pass=True but denial_reasons is non-empty",
            )
        if not self.validation_pass and not self.denial_reasons:
            raise ValueError(
                "validation_pass=False but denial_reasons is empty",
            )

    def _canonical_dict(self) -> dict:
        return {
            "denial_reasons": sorted(self.denial_reasons),
            "determinism_verified": self.determinism_verified,
            "gate_results": sorted(self.gate_results),
            "guardrail_safe": self.guardrail_safe,
            "policy_hash": self.policy_hash,
            "policy_safe": self.policy_safe,
            "proposal_id": self.proposal_id,
            "regression_risk": self.regression_risk,
            "replay_safe": self.replay_safe,
            "result_id": self.result_id,
            "timestamp_utc": self.timestamp_utc,
            "validation_pass": self.validation_pass,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(
            deterministic_json(self._canonical_dict()).encode("utf-8"),
        ).hexdigest()

    def to_dict(self) -> dict:
        return self._canonical_dict()

    def to_json(self) -> str:
        return deterministic_json(self._canonical_dict())


# ---------------------------------------------------------------------------
# OptimizationCommit
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OptimizationCommit:
    """Versioned commit produced from a validated optimization proposal.

    Creates ADG relation: ``proposal_commits_optimization``.

    Attributes
    ----------
    commit_id : str
        Content-addressed ID = stable_hash().
    proposal_id : str
        ID of the originating OptimizationProposal.
    validation_result_id : str
        ID of the passing ValidationResult that authorized this commit.
    affected_rules : tuple[str, ...]
        Rule identifiers changed by this commit (sorted).
    affected_routes : tuple[str, ...]
        Route paths affected (sorted).
    affected_retrieval_policy : tuple[str, ...]
        Retrieval policy identifiers affected (sorted).
    affected_components : tuple[str, ...]
        ADG entity names of all affected components (sorted).
    policy_hash : str | None
        Policy config hash active at commit time.
    change_type : str
        Change type from the originating proposal.
    risk_class : str
        Risk class from the originating proposal.
    adg_relation : str
        Always ``"proposal_commits_optimization"`` — the ADG relation
        type created by this commit.
    timestamp_utc : int
        Caller-supplied Unix timestamp.
    """

    commit_id: str
    proposal_id: str
    validation_result_id: str
    affected_rules: tuple[str, ...]
    affected_routes: tuple[str, ...]
    affected_retrieval_policy: tuple[str, ...]
    affected_components: tuple[str, ...]
    policy_hash: str | None
    change_type: str
    risk_class: str
    adg_relation: str
    timestamp_utc: int

    def __post_init__(self) -> None:
        if not self.proposal_id:
            raise ValueError("proposal_id must not be empty")
        if not self.validation_result_id:
            raise ValueError("validation_result_id must not be empty")
        if self.adg_relation != "proposal_commits_optimization":
            raise ValueError(
                f"adg_relation must be 'proposal_commits_optimization', got {self.adg_relation!r}",
            )
        if self.change_type not in _VALID_CHANGE_TYPES:
            raise ValueError(
                f"change_type must be one of {sorted(_VALID_CHANGE_TYPES)}, got {self.change_type!r}",
            )
        if self.risk_class not in _VALID_RISK_CLASSES:
            raise ValueError(
                f"risk_class must be one of {sorted(_VALID_RISK_CLASSES)}, got {self.risk_class!r}",
            )

    def _canonical_dict(self) -> dict:
        return {
            "adg_relation": self.adg_relation,
            "affected_components": sorted(self.affected_components),
            "affected_retrieval_policy": sorted(self.affected_retrieval_policy),
            "affected_routes": sorted(self.affected_routes),
            "affected_rules": sorted(self.affected_rules),
            "change_type": self.change_type,
            "commit_id": self.commit_id,
            "policy_hash": self.policy_hash,
            "proposal_id": self.proposal_id,
            "risk_class": self.risk_class,
            "timestamp_utc": self.timestamp_utc,
            "validation_result_id": self.validation_result_id,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(
            deterministic_json(self._canonical_dict()).encode("utf-8"),
        ).hexdigest()

    def to_dict(self) -> dict:
        return self._canonical_dict()

    def to_json(self) -> str:
        return deterministic_json(self._canonical_dict())


# ---------------------------------------------------------------------------
# GovernanceRewardSignal — per-trace reward model input
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GovernanceRewardSignal:
    """Per-trace reward signal for the governance reward model.

    Attributes
    ----------
    signal_id : str
        Content-addressed ID.
    trace_id : str
        Originating trace.
    groundedness_score : float
        Retrieval groundedness score (0.0–1.0).
    policy_compliance : float
        Fraction of policy checks that passed (0.0–1.0).
    replay_stability : float
        Replay stability score (0.0–1.0); 1.0 = fully deterministic.
    guardrail_cleanliness : float
        Fraction of guardrail checks that passed without false positives
        (0.0–1.0).
    mutation_correctness : float
        Source mutation correctness score (0.0–1.0); 1.0 = no
        unauthorized mutations.
    human_approval : bool | None
        Human approval decision if HITL was invoked; None otherwise.
    timestamp_utc : int
        Caller-supplied Unix timestamp.
    """

    signal_id: str
    trace_id: str
    groundedness_score: float
    policy_compliance: float
    replay_stability: float
    guardrail_cleanliness: float
    mutation_correctness: float
    human_approval: bool | None
    timestamp_utc: int

    def __post_init__(self) -> None:
        for attr in tqdm(
            (
                "groundedness_score",
                "policy_compliance",
                "replay_stability",
                "guardrail_cleanliness",
                "mutation_correctness",
            ),
            desc="Processing",
            unit="item",
        ):
            val = getattr(self, attr)
            if not 0.0 <= val <= 1.0:
                raise ValueError(
                    f"{attr} must be in [0.0, 1.0], got {val}",
                )

    def _canonical_dict(self) -> dict:
        return {
            "groundedness_score": round(self.groundedness_score, 6),
            "guardrail_cleanliness": round(self.guardrail_cleanliness, 6),
            "human_approval": self.human_approval,
            "mutation_correctness": round(self.mutation_correctness, 6),
            "policy_compliance": round(self.policy_compliance, 6),
            "replay_stability": round(self.replay_stability, 6),
            "signal_id": self.signal_id,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(
            deterministic_json(self._canonical_dict()).encode("utf-8"),
        ).hexdigest()

    def to_dict(self) -> dict:
        return self._canonical_dict()

    def to_json(self) -> str:
        return deterministic_json(self._canonical_dict())


# ---------------------------------------------------------------------------
# GovernanceRewardScore — aggregated reward for a proposal
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GovernanceRewardScore:
    """Aggregated governance reward score for an optimization proposal.

    Produced by the GovernanceRewardModel from one or more
    GovernanceRewardSignal objects.

    Attributes
    ----------
    score_id : str
        Content-addressed ID.
    proposal_id : str
        The proposal being scored.
    aggregate_score : float
        Weighted aggregate reward (0.0–1.0).  Higher is better.
    groundedness_contrib : float
        Groundedness contribution to aggregate score.
    policy_compliance_contrib : float
        Policy compliance contribution.
    replay_stability_contrib : float
        Replay stability contribution.
    guardrail_cleanliness_contrib : float
        Guardrail cleanliness contribution.
    mutation_correctness_contrib : float
        Mutation correctness contribution.
    human_approval_rate : float
        Fraction of HITL-escalated traces that received approval (0.0–1.0).
        Set to 1.0 when no HITL traces were present.
    invariant_preserved : bool
        True iff the proposal preserves all governance invariants
        (aggregate_score >= invariant_floor AND no CRITICAL violations).
    signal_count : int
        Number of GovernanceRewardSignal objects aggregated.
    timestamp_utc : int
        Caller-supplied Unix timestamp.
    """

    score_id: str
    proposal_id: str
    aggregate_score: float
    groundedness_contrib: float
    policy_compliance_contrib: float
    replay_stability_contrib: float
    guardrail_cleanliness_contrib: float
    mutation_correctness_contrib: float
    human_approval_rate: float
    invariant_preserved: bool
    signal_count: int
    timestamp_utc: int

    def __post_init__(self) -> None:
        for attr in tqdm(
            (
                "aggregate_score",
                "groundedness_contrib",
                "policy_compliance_contrib",
                "replay_stability_contrib",
                "guardrail_cleanliness_contrib",
                "mutation_correctness_contrib",
                "human_approval_rate",
            ),
            desc="Processing",
            unit="item",
        ):
            val = getattr(self, attr)
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{attr} must be in [0.0, 1.0], got {val}")
        if self.signal_count < 0:
            raise ValueError("signal_count must be >= 0")

    def _canonical_dict(self) -> dict:
        return {
            "aggregate_score": round(self.aggregate_score, 6),
            "groundedness_contrib": round(self.groundedness_contrib, 6),
            "guardrail_cleanliness_contrib": round(
                self.guardrail_cleanliness_contrib,
                6,
            ),
            "human_approval_rate": round(self.human_approval_rate, 6),
            "invariant_preserved": self.invariant_preserved,
            "mutation_correctness_contrib": round(
                self.mutation_correctness_contrib,
                6,
            ),
            "policy_compliance_contrib": round(self.policy_compliance_contrib, 6),
            "proposal_id": self.proposal_id,
            "replay_stability_contrib": round(self.replay_stability_contrib, 6),
            "score_id": self.score_id,
            "signal_count": self.signal_count,
            "timestamp_utc": self.timestamp_utc,
        }

    def stable_hash(self) -> str:
        return hashlib.sha256(
            deterministic_json(self._canonical_dict()).encode("utf-8"),
        ).hexdigest()

    def to_dict(self) -> dict:
        return self._canonical_dict()

    def to_json(self) -> str:
        return deterministic_json(self._canonical_dict())


__all__ = [
    "GovernanceRewardScore",
    "GovernanceRewardSignal",
    "OptimizationCommit",
    "OptimizationProposal",
    "ValidationResult",
]
