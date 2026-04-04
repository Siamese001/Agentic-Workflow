"""
V15 P3 Framework Contracts — Governance & Human Escalation Enforcement.

Runtime contracts enforcing P3 (Governance) invariants required by
the V15 Target State audit (Prompt v5.0 Enhanced).

Contract version: 1.0.0
"""

from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import datetime, timezone
from typing import Any

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
)
from agentic_core.L0_routing.types.governance_types import (
    ChangeAction,
    EvidencePack,
    ExceptionScope,
    HILOutcome,
    PolicyExceptionArtifact,
    PolicySnapshot,
    PolicyUpdateProposal,
    ProposedPolicyChange,
    RouteDecisionRef,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_log = logging.getLogger(__name__)


def _make_proposal_id(trace_id: str) -> str:
    """REQ-111: deterministic ID derived from trace_id; no uuid4."""
    return "PROP-" + hashlib.sha256(trace_id.encode()).hexdigest()[:16]


# =============================================================================
# §3.4 — build_evidence_pack
# =============================================================================


class EvidencePackError(Exception):
    """Raised when EvidencePack construction fails (fail-closed)."""


def build_evidence_pack(
    trace_id: str,
    action_trace: tuple[str, ...],
    policy_evals: tuple[str, ...],
    risk_score: float,
    budget_breach_data: dict[str, object],
    boundary_snapshot_hash: str,
) -> EvidencePack:
    """§3.4 — Build a structured EvidencePack for human escalation.

    Fail-closed: any invalid field raises EvidencePackError.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "build_evidence_pack", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "build_evidence_pack")
    try:
        pack = EvidencePack(
            trace_id=trace_id,
            action_trace=action_trace,
            policy_evals=policy_evals,
            risk_score=risk_score,
            budget_breach_data=budget_breach_data,
            boundary_snapshot_hash=boundary_snapshot_hash,
        )
    except (ValueError, TypeError) as exc:
        raise EvidencePackError(
            f"FAIL (P3): EvidencePack construction failed: {exc}",
        ) from exc
    return pack


def validate_evidence_pack(pack: Any) -> EvidencePack:
    """§3.4 — Validate that an object is a well-formed EvidencePack."""
    import uuid  # noqa: PLC0415

    _emit_verifies_policy(str(uuid.uuid4()), "Module.validate_evidence_pack", "L0_ROUTING")
    if not isinstance(pack, EvidencePack):
        raise EvidencePackError(
            f"FAIL (P3): Expected EvidencePack, got {type(pack).__name__}",
        )
    return pack


def build_hil_evidence_pack(
    trace_id: str,
    escalation_reason: str,
    route_decision_ref: RouteDecisionRef,
    policy_snapshot_data: PolicySnapshot,
    risk_score: float = 0.8,
    action_trace: tuple[str, ...] = (),
    policy_evals: tuple[str, ...] = (),
    guardian_results: tuple[str, ...] = (),
    ssot_hash: str = "",
    attachments: tuple[str, ...] = (),
    semantic_clock: SemanticClockSnapshot | None = None,
) -> EvidencePack:
    """§Wave2.2 — Build a full EvidencePack for HIL escalation.

    Fail-closed: any invalid field raises EvidencePackError.
    """
    try:
        pack = EvidencePack(
            trace_id=trace_id,
            action_trace=action_trace,
            policy_evals=policy_evals,
            risk_score=risk_score,
            budget_breach_data={},
            boundary_snapshot_hash=ssot_hash or "n/a",
            evidence_id=_make_proposal_id(trace_id),
            timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            escalation_reason=escalation_reason,
            route_decision_ref=route_decision_ref,
            guardian_results=guardian_results,
            policy_snapshot_data=policy_snapshot_data,
            ssot_hash=ssot_hash,
            attachments=attachments,
            semantic_clock=semantic_clock,
        )
    except (ValueError, TypeError) as exc:
        raise EvidencePackError(
            f"FAIL (P3/Wave2.2): HIL EvidencePack construction failed: {exc}",
        ) from exc
    return pack


# =============================================================================
# §3.7 — emit_policy_exception
# =============================================================================


class PolicyExceptionError(Exception):
    """Raised when PolicyExceptionArtifact construction or validation fails."""


def emit_policy_exception(
    trace_id: str,
    exception_scope: ExceptionScope,
    semantic_clock_tick: int,
    issuer_signature: str,
    nonce: str | None = None,
) -> PolicyExceptionArtifact:
    """§3.7 — Emit a PolicyExceptionArtifact for a policy challenge.

    Generates a cryptographic nonce if not provided.
    Fail-closed: any invalid field raises PolicyExceptionError.
    """
    if nonce is None:
        nonce = secrets.token_hex(16)

    try:
        artifact = PolicyExceptionArtifact(
            trace_id=trace_id,
            nonce=nonce,
            exception_scope=exception_scope,
            semantic_clock_tick=semantic_clock_tick,
            issuer_signature=issuer_signature,
        )
    except (ValueError, TypeError) as exc:
        raise PolicyExceptionError(
            f"FAIL (P3): PolicyExceptionArtifact construction failed: {exc}",
        ) from exc
    return artifact


def validate_policy_exception_tick(
    artifact: PolicyExceptionArtifact,
    current_tick: int,
) -> bool:
    """§3.7 — Validate that a policy exception is valid for the current tick.

    An exception is valid ONLY for the semantic clock tick it was issued at.
    Returns True if valid, raises PolicyExceptionError if expired.
    """
    if artifact.semantic_clock_tick != current_tick:
        raise PolicyExceptionError(
            f"FAIL (P3): PolicyException expired. "
            f"Issued at tick {artifact.semantic_clock_tick}, current tick {current_tick}.",
        )
    return True


# =============================================================================
# §3.5 — propose_policy_update
# =============================================================================


class PolicyUpdateError(Exception):
    """Raised when PolicyUpdateProposal construction or validation fails."""


def propose_policy_update(
    trace_id: str,
    override_id: str,
    proposed_policy_diff: str,
    originating_agent: str,
    semantic_clock_tick: int,
) -> PolicyUpdateProposal:
    """§3.5 — Emit a PolicyUpdateProposal for bidirectional feedback.

    Emitted when a human override occurs, proposing a policy change
    back to the Policy Update Mechanism.
    Fail-closed: any invalid field raises PolicyUpdateError.
    """
    try:
        proposal = PolicyUpdateProposal(
            trace_id=trace_id,
            override_id=override_id,
            proposed_policy_diff=proposed_policy_diff,
            originating_agent=originating_agent,
            semantic_clock_tick=semantic_clock_tick,
        )
    except (ValueError, TypeError) as exc:
        raise PolicyUpdateError(
            f"FAIL (P3): PolicyUpdateProposal construction failed: {exc}",
        ) from exc
    return proposal


def validate_proposal(proposal: Any) -> PolicyUpdateProposal:
    """§3.5 — Validate that an object is a well-formed PolicyUpdateProposal."""
    if not isinstance(proposal, PolicyUpdateProposal):
        raise PolicyUpdateError(
            f"FAIL (P3): Expected PolicyUpdateProposal, got {type(proposal).__name__}",
        )
    return proposal


# =============================================================================
# §Wave2.3 — build_hil_policy_proposal
# =============================================================================

# Deterministic mapping: HILOutcome → default ProposedPolicyChange entries
_HIL_OUTCOME_CHANGE_MAP: dict[HILOutcome, tuple[ProposedPolicyChange, ...]] = {
    HILOutcome.APPROVED: (
        ProposedPolicyChange(
            target="routing_policy",
            action=ChangeAction.ADJUST,
            scope="L3/orchestration",
            risk_note="Human approved action; consider lowering escalation threshold",
            current_value="human_escalation",
            proposed_value="standard_validation",
        ),
    ),
    HILOutcome.REJECTED: (
        ProposedPolicyChange(
            target="routing_policy",
            action=ChangeAction.ADD,
            scope="L5/governance",
            risk_note="Human rejected action; consider adding deny rule",
            current_value="",
            proposed_value="deny",
        ),
    ),
    HILOutcome.OVERRIDDEN: (
        ProposedPolicyChange(
            target="routing_policy",
            action=ChangeAction.ADJUST,
            scope="L5/governance",
            risk_note="Human overrode system decision; review policy calibration",
            current_value="system_decision",
            proposed_value="human_override",
        ),
    ),
    HILOutcome.NEEDS_MORE_INFO: (),
}


def build_hil_policy_proposal(
    trace_id: str,
    evidence_pack_id: str,
    hil_outcome: HILOutcome,
    reviewer_id: str,
    review_notes: str,
    request_id: str = "",
    file_scope: str = "",
    confidence: float = 0.7,
    semantic_clock: SemanticClockSnapshot | None = None,
) -> PolicyUpdateProposal:
    """§Wave2.3 — Build a PolicyUpdateProposal from HIL review outcome.

    Uses a deterministic mapping table from HILOutcome to ProposedPolicyChange
    entries. If no structured reason exists, proposed_changes is empty but
    rationale must explain why.

    Fail-closed: any invalid field raises PolicyUpdateError.
    """
    proposed_changes = _HIL_OUTCOME_CHANGE_MAP.get(hil_outcome, ())

    # Override scope from file context if available
    if file_scope and proposed_changes:
        proposed_changes = tuple(
            ProposedPolicyChange(
                target=pc.target,
                action=pc.action,
                scope=file_scope,
                risk_note=pc.risk_note,
                current_value=pc.current_value,
                proposed_value=pc.proposed_value,
            )
            for pc in proposed_changes
        )

    rationale = review_notes or f"HIL outcome: {hil_outcome.value}; no structured notes provided"

    try:
        proposal = PolicyUpdateProposal(
            trace_id=trace_id,
            override_id=request_id or _make_proposal_id(trace_id),
            proposed_policy_diff=f"{hil_outcome.value}: {rationale[:200]}",
            originating_agent=f"HIL/{reviewer_id}",
            semantic_clock_tick=0,
            proposal_id=_make_proposal_id(trace_id),
            timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            evidence_pack_id=evidence_pack_id,
            hil_outcome=hil_outcome,
            proposed_changes=proposed_changes,
            rationale=rationale,
            proposer="SYSTEM",
            confidence=confidence,
            semantic_clock=semantic_clock,
        )
    except (ValueError, TypeError) as exc:
        raise PolicyUpdateError(
            f"FAIL (P3/Wave2.3): HIL PolicyUpdateProposal construction failed: {exc}",
        ) from exc
    return proposal


__all__ = [
    "EvidencePackError",
    "PolicyExceptionError",
    "PolicyUpdateError",
    "build_evidence_pack",
    "build_hil_evidence_pack",
    "build_hil_policy_proposal",
    "emit_policy_exception",
    "propose_policy_update",
    "validate_evidence_pack",
    "validate_policy_exception_tick",
    "validate_proposal",
]
