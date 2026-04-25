"""DECISION RAIL — explicit terminal authority (spec lines 590–650).

Composes upstream G0/G1/G2a outcomes (and optionally a v4 runtime-lane
report) into a final ``DecisionVerdict`` with reason codes.

Precedence (most-restrictive wins):
    REJECT > ESCALATE > REMEDIATE > CERTIFY

Hard invariants (enforced by ``GovernanceResult.__post_init__``):
- ``REMEDIATE`` is forbidden when ``HARD_CONSTRAINT_BREACH`` is in reason codes.
- ``CERTIFY`` requires both capability_token + sandbox_envelope.
- ``REJECT`` with ``HARD_CONSTRAINT_BREACH`` requires ``hard_stop=True``.
"""

from __future__ import annotations

from typing import Any, Mapping

from agentic_core.L5_safety.v5.contracts import (
    CapabilityTokenV5,
    GovernanceResult,
    GovernanceReviewRequest,
    OriginTrustManifest,
    ReplayEnvelope,
    SandboxEnvelope,
    StandardsFingerprint,
    TriageReport,
)
from agentic_core.L5_safety.v5.g0_entry import EntryValidationFailure
from agentic_core.L5_safety.v5.types import (
    BoundaryClassification,
    DecisionVerdict,
    NextLane,
    ReasonCode,
    ReviewDepth,
    RiskTierBandV5,
    TriageFlag,
)


# Reason codes that force REJECT regardless of remediation possibility.
_HARD_REJECT_CODES = frozenset(
    {
        ReasonCode.HARD_CONSTRAINT_BREACH,
        ReasonCode.CROSS_TENANT_RISK,
        ReasonCode.INJECTION_DETECTED,
    }
)


def _entry_failures_to_codes(
    failures: tuple[EntryValidationFailure, ...],
) -> tuple[ReasonCode, ...]:
    return tuple(f.code for f in failures)


def emit_verdict(
    *,
    review_request: GovernanceReviewRequest,
    triage: TriageReport,
    origin_trust: OriginTrustManifest,
    entry_failures: tuple[EntryValidationFailure, ...] = (),
    additional_reason_codes: tuple[ReasonCode, ...] = (),
    runtime_final_action: str | None = None,  # v4 final_action: allow|step_up|remediate|reject
    capability_token: CapabilityTokenV5 | None = None,
    sandbox_envelope: SandboxEnvelope | None = None,
    replay_envelope: ReplayEnvelope,
    audit_log_event: Mapping[str, Any],
    governance_reports: Mapping[str, Mapping[str, Any]] | None = None,
    standards_fingerprint: StandardsFingerprint,
) -> GovernanceResult:
    """Compute final decision-rail verdict.

    The function is intentionally side-effect free; the caller persists
    the audit log event and the replay envelope.
    """
    reasons: list[ReasonCode] = list(_entry_failures_to_codes(entry_failures))
    reasons.extend(additional_reason_codes)

    # --- Origin / triage flag → reason code mapping --------------
    if origin_trust.boundary_classification == BoundaryClassification.REJECTED:
        reasons.append(ReasonCode.INJECTION_DETECTED)
    elif origin_trust.boundary_classification == BoundaryClassification.QUARANTINED:
        # Quarantine alone is not a reject; surface as evidence_weak so the
        # rail can still ESCALATE when combined with HIGH/CRITICAL band.
        reasons.append(ReasonCode.EVIDENCE_WEAK)

    if TriageFlag.IDENTITY_GAP in triage.triage_flags:
        reasons.append(ReasonCode.MISSING_AUTHORITY)
    if TriageFlag.REGISTRY_GAP in triage.triage_flags:
        reasons.append(ReasonCode.REGISTRY_MISMATCH)
    if TriageFlag.SCOPE_MISMATCH in triage.triage_flags:
        reasons.append(ReasonCode.ROUTE_MISMATCH)
    if TriageFlag.SIDE_EFFECT_MISMATCH in triage.triage_flags:
        reasons.append(ReasonCode.POLICY_VIOLATION)
    if TriageFlag.HARD_CONSTRAINT_CANDIDATE in triage.triage_flags:
        reasons.append(ReasonCode.HARD_CONSTRAINT_BREACH)
    if TriageFlag.INJECTION_SUSPECTED in triage.triage_flags:
        reasons.append(ReasonCode.INJECTION_DETECTED)

    # --- v4 runtime composition (optional) -----------------------
    if runtime_final_action == "reject":
        reasons.append(ReasonCode.POLICY_VIOLATION)
    elif runtime_final_action == "step_up":
        reasons.append(ReasonCode.HITL_REQUIRED)
    elif runtime_final_action == "remediate":
        # Remediate is only acceptable if no hard reject code present.
        pass

    reason_codes_tuple = tuple(dict.fromkeys(reasons))  # de-dup, preserve order

    # --- Verdict computation -------------------------------------
    has_hard_code = any(c in _HARD_REJECT_CODES for c in reason_codes_tuple)
    next_lane_force_reject = triage.next_lane == NextLane.DECISION_RAIL_REJECT
    runtime_rejected = runtime_final_action == "reject"

    if has_hard_code or next_lane_force_reject or runtime_rejected:
        decision = DecisionVerdict.REJECT
    elif (
        ReasonCode.HITL_REQUIRED in reason_codes_tuple
        or ReasonCode.DRIFT_DETECTED in reason_codes_tuple
        or triage.review_depth == ReviewDepth.LOCKDOWN
        or triage.risk_tier_band == RiskTierBandV5.CRITICAL
    ):
        decision = DecisionVerdict.ESCALATE
    elif reason_codes_tuple and runtime_final_action == "remediate":
        decision = DecisionVerdict.REMEDIATE
    elif (
        ReasonCode.EVIDENCE_WEAK in reason_codes_tuple
        and not has_hard_code
        and runtime_final_action != "reject"
    ):
        # Weak evidence alone → REMEDIATE (sanitize / refresh retrieval).
        decision = DecisionVerdict.REMEDIATE
    else:
        decision = DecisionVerdict.CERTIFY

    # CERTIFY requires token + sandbox; if missing, downgrade to ESCALATE.
    if decision == DecisionVerdict.CERTIFY and (capability_token is None or sandbox_envelope is None):
        decision = DecisionVerdict.ESCALATE
        reason_codes_tuple = (*reason_codes_tuple, ReasonCode.SANDBOX_INSUFFICIENT)

    # Hard-stop and re-clearance flags ----------------------------
    hard_stop = decision == DecisionVerdict.REJECT and (
        ReasonCode.HARD_CONSTRAINT_BREACH in reason_codes_tuple
        or ReasonCode.CROSS_TENANT_RISK in reason_codes_tuple
    )
    revalidate_required = decision == DecisionVerdict.REMEDIATE
    re_clearance_required = decision == DecisionVerdict.ESCALATE

    # Downstream disposition (spec lines 747–756) -----------------
    disposition: list[str] = []
    if decision == DecisionVerdict.CERTIFY:
        disposition.append("allow_l2_execution")
        if review_request.side_effect_class.value == "MODEL_CALL":
            disposition.append("allow_model_call")
        if review_request.side_effect_class.value == "TOOL_CALL":
            disposition.append("allow_tool_call")
        if review_request.side_effect_class.value == "NETWORK":
            disposition.append("allow_connector_call")
        if review_request.side_effect_class.value in {
            "WRITE_PROPOSAL",
            "EXTERNAL_COMMIT",
            "MEMORY",
        }:
            disposition.append("require_UWG_commit_review")
    elif decision == DecisionVerdict.REMEDIATE:
        disposition.append("reroute")
    elif decision == DecisionVerdict.ESCALATE:
        disposition.append("require_HITL")
    elif decision == DecisionVerdict.REJECT:
        if hard_stop:
            disposition.append("incident_lockdown")
        else:
            disposition.append("deny")

    return GovernanceResult(
        decision=decision,
        reason_codes=reason_codes_tuple,
        compliance_hash=replay_envelope.compliance_hash,
        standards_fingerprint=standards_fingerprint,
        review_request=review_request,
        triage=triage,
        origin_trust=origin_trust,
        capability_token=capability_token if decision == DecisionVerdict.CERTIFY else None,
        sandbox_envelope=sandbox_envelope if decision == DecisionVerdict.CERTIFY else None,
        replay_envelope=replay_envelope,
        audit_log_event=dict(audit_log_event),
        governance_reports={k: dict(v) for k, v in (governance_reports or {}).items()},
        downstream_disposition=tuple(disposition),
        hard_stop=hard_stop,
        revalidate_required=revalidate_required,
        re_clearance_required=re_clearance_required,
    )


__all__ = ["emit_verdict"]
