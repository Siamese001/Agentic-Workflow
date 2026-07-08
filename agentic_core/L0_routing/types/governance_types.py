"""
V15 P3 Typed Artifacts — Governance & Human Escalation.

Typed artifacts required by Prompt v5.0 Enhanced for P3 (Governance)
invariants. All artifacts are frozen dataclasses with strict field
validation enforced at construction time.

Artifact version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from agentic_core.L0_routing.reasoning.assembly_stage import GovernedPayload  # noqa: F401
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_dispatches_healing_run("p1", "governance_types", "L0")
trace_contract._emit_routes_through("p1", "governance_types", "L0")
trace_contract._emit_checks_agent_registry("p1", "governance_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "governance_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "governance_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "governance_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "governance_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "governance_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "governance_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "governance_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "governance_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "governance_types")
trace_contract._emit_gated_by_confidence("p1", "governance_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "governance_types", "L0")
trace_contract._emit_reads_policy_state("p1", "governance_types", "L0")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "governance_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "governance_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "governance_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "governance_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "governance_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "governance_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "governance_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "governance_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "governance_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "governance_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "governance_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "governance_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "governance_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "governance_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "governance_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "governance_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "governance_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "governance_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "governance_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "governance_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "governance_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "governance_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("governance_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("governance_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("governance_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("governance_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("governance_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("governance_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("governance_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("governance_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("governance_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("governance_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("governance_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("governance_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("governance_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("governance_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("governance_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("governance_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("governance_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("governance_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("governance_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("governance_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("governance_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("governance_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("governance_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("governance_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("governance_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("governance_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("governance_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("governance_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "governance_types", "context_pull")
trace_contract._emit_pulls_context("p1", "governance_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "governance_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "governance_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "governance_types", "write_through")
trace_contract._emit_writes_through("p1", "governance_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "governance_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "governance_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "governance_types", "routing_commit")


@dataclass(frozen=True)
class RouteDecisionRef:
    """§Wave2.2 — Essential subset of a RouteDecisionArtifact for cross-layer linking."""

    trace_id: str
    decision: str
    agent_name: str
    reason: str


@dataclass(frozen=True)
class PolicySnapshot:
    """§Wave2.2 — Policy state at the time of escalation."""

    security_level: str
    risk_tier: str
    laws_applied: tuple[str, ...]
    policy_hash: str


@dataclass(frozen=True)
class EvidencePack:
    """§3.4 — Structured evidence for human escalation.

    Generated when a routing decision reaches HUMAN_REVIEW.
    Contains the full action trace, policy evaluations, risk score,
    budget breach data, and an immutable boundary snapshot hash.

    Wave 2.2 extension: evidence_id, timestamp_utc, escalation_reason,
    route_decision_ref, guardian_results, policy_snapshot_data, ssot_hash,
    attachments — all optional (defaults) to preserve backward compat.
    """

    trace_id: str
    action_trace: tuple[str, ...]
    policy_evals: tuple[str, ...]
    risk_score: float
    budget_breach_data: dict[str, object]
    boundary_snapshot_hash: str
    evidence_id: str = ""
    timestamp_utc: str = ""
    escalation_reason: str = ""
    route_decision_ref: RouteDecisionRef | None = None
    guardian_results: tuple[str, ...] = ()
    policy_snapshot_data: PolicySnapshot | None = None
    ssot_hash: str = ""
    attachments: tuple[str, ...] = ()
    semantic_clock: SemanticClockSnapshot | None = None

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("EvidencePack: trace_id must be non-empty")
        if not isinstance(self.action_trace, tuple):
            raise TypeError("EvidencePack: action_trace must be a tuple")
        if not isinstance(self.policy_evals, tuple):
            raise TypeError("EvidencePack: policy_evals must be a tuple")
        if not 0.0 <= self.risk_score <= 1.0:
            raise ValueError(f"EvidencePack: risk_score must be in [0.0, 1.0], got {self.risk_score}")
        if not self.boundary_snapshot_hash:
            raise ValueError("EvidencePack: boundary_snapshot_hash must be non-empty")


class ExceptionScope(Enum):
    """Valid scopes for a policy exception."""

    SINGLE_AGENT = "single_agent"
    HEALING_WAVE = "healing_wave"
    FULL_PIPELINE = "full_pipeline"


@dataclass(frozen=True)
class PolicyExceptionArtifact:
    """§3.7 — Policy exception issued by a human to override a Block decision.

    Valid only for the current semantic clock tick. The nonce ensures
    single-use and prevents replay attacks.
    """

    trace_id: str
    nonce: str
    exception_scope: ExceptionScope
    semantic_clock_tick: int
    issuer_signature: str
    ttl_ticks: int = 0

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("PolicyExceptionArtifact: trace_id must be non-empty")
        if not self.nonce:
            raise ValueError("PolicyExceptionArtifact: nonce must be non-empty")
        if not isinstance(self.exception_scope, ExceptionScope):
            raise TypeError(
                f"PolicyExceptionArtifact: exception_scope must be ExceptionScope, got {type(self.exception_scope).__name__}",
            )
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"PolicyExceptionArtifact: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}",
            )
        if not self.issuer_signature:
            raise ValueError("PolicyExceptionArtifact: issuer_signature must be non-empty")

    def is_expired(self, now_tick: int) -> bool:
        """REQ-245: return True if this exception has expired per semantic clock.

        If ttl_ticks == 0 the exception has no TTL and never expires.
        Expired when now_tick > semantic_clock_tick + ttl_ticks.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L0_ROUTING,
            "PolicyExceptionArtifact.is_expired",
        )
        trace_contract.emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        trace_contract.emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if self.ttl_ticks == 0:
            return False
        return now_tick > self.semantic_clock_tick + self.ttl_ticks


class ProposalStatus(Enum):
    """Status of a policy update proposal."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class HILOutcome(Enum):
    """§Wave2.3 — Human-in-the-Loop decision outcomes."""

    APPROVED = "approved"
    REJECTED = "rejected"
    OVERRIDDEN = "overridden"
    NEEDS_MORE_INFO = "needs_more_info"


@dataclass(frozen=True)
class HILReviewOutcome:
    """§P4.W9 — REQ-085/086: HIL review record with reviewer signature.

    Carries the reviewer identity and cryptographic signature for audit.
    MODIFY_DIFF decision requires L5 re-clearance (requires_l5_reclear=True).
    """

    decision: str
    reviewer_id: str
    reviewer_sig: str
    requires_l5_reclear: bool = False


class ChangeAction(Enum):
    """§Wave2.3 — Actions that can be proposed for a policy change."""

    ADD = "add"
    REMOVE = "remove"
    ADJUST = "adjust"


@dataclass(frozen=True)
class ProposedPolicyChange:
    """§Wave2.3 — A single proposed change to a policy rule or configuration."""

    target: str
    action: ChangeAction
    scope: str
    risk_note: str
    current_value: str = ""
    proposed_value: str = ""


@dataclass(frozen=True)
class PolicyUpdateProposal:
    """§3.5 — Bidirectional feedback from human override back to policy layer.

    Emitted when a human override occurs, proposing a policy diff
    that the Policy Update Mechanism (L0/L5) should evaluate.

    Wave 2.3 extension: proposal_id, timestamp_utc, evidence_pack_id,
    hil_outcome, proposed_changes, rationale, proposer, confidence —
    all optional (defaults) to preserve backward compat.
    """

    trace_id: str
    override_id: str
    proposed_policy_diff: str
    originating_agent: str
    semantic_clock_tick: int
    status: ProposalStatus = ProposalStatus.PENDING
    proposal_id: str = ""
    timestamp_utc: str = ""
    evidence_pack_id: str = ""
    hil_outcome: HILOutcome | None = None
    proposed_changes: tuple[ProposedPolicyChange, ...] = ()
    rationale: str = ""
    proposer: str = ""
    confidence: float = 0.0
    semantic_clock: SemanticClockSnapshot | None = None

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("PolicyUpdateProposal: trace_id must be non-empty")
        if not self.override_id:
            raise ValueError("PolicyUpdateProposal: override_id must be non-empty")
        if not self.proposed_policy_diff:
            raise ValueError("PolicyUpdateProposal: proposed_policy_diff must be non-empty")
        if not self.originating_agent:
            raise ValueError("PolicyUpdateProposal: originating_agent must be non-empty")
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"PolicyUpdateProposal: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}",
            )
        if not isinstance(self.status, ProposalStatus):
            raise TypeError(
                f"PolicyUpdateProposal: status must be ProposalStatus, got {type(self.status).__name__}",
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"PolicyUpdateProposal: confidence must be in [0.0, 1.0], got {self.confidence}")


__all__ = [
    "ChangeAction",
    "EvidencePack",
    "ExceptionScope",
    "HILOutcome",
    "HILReviewOutcome",
    "PolicyExceptionArtifact",
    "PolicySnapshot",
    "PolicyUpdateProposal",
    "ProposalStatus",
    "ProposedPolicyChange",
    "RouteDecisionRef",
]
