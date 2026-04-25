"""Top-level v5 governance façade — ``certify_packet``.

Composes G0 → G1 → G2a → optional v4 runtime-lane → Decision Rail →
replay sealing → audit log into a single ``GovernanceResult``.

This is the single function v5-aware callers invoke per inbound packet.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Iterable, Mapping

from agentic_core.L5_safety.v5.contracts import (
    CapabilityTokenV5,
    GovernanceResult,
    HITLDispositionPacket,
    RuntimeRegressionReport,
    SandboxEnvelope,
    StandardsFingerprint,
)
from agentic_core.L5_safety.v5.decision_rail import emit_verdict
from agentic_core.L5_safety.v5.g0_entry import (
    EntryValidationResult,
    validate_entry_packet,
)
from agentic_core.L5_safety.v5.g1_triage import triage_request
from agentic_core.L5_safety.v5.g2a_origin_trust import classify_origins
from agentic_core.L5_safety.v5.replay_audit import (
    build_audit_log_event,
    seal_replay_envelope,
)
from agentic_core.L5_safety.v5.types import (
    DecisionVerdict,
    GovernanceMode,
    ReasonCode,
    RiskTierBandV5,
    StandardsTag,
)


def _utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).isoformat()


def _empty_govresult_for_failed_entry(
    *,
    raw: Mapping[str, Any],
    entry: EntryValidationResult,
    standards: StandardsFingerprint,
    actor: str,
    span_id: str,
    route_id: str,
    timestamp_iso: str,
) -> GovernanceResult:
    """Build a minimal REJECT GovernanceResult for a failed-entry packet.

    The packet failed G0 validation; we still need to emit an auditable,
    sealed result so the caller has a forensic record.
    """
    # Synthesize a minimal request out of whatever was parseable.
    from agentic_core.L5_safety.v5.contracts import (
        GovernanceReviewRequest,
        OriginTrustManifest,
        TriageReport,
    )
    from agentic_core.L5_safety.v5.types import (
        BoundaryClassification,
        NextLane,
        PacketKind,
        ReviewDepth,
        SideEffectClass,
        TriageFlag,
    )

    # If the dict had a recognizable packet_kind/side_effect_class, use it;
    # otherwise fall back to safe defaults.
    try:
        packet_kind = PacketKind(raw.get("packet_kind", PacketKind.REQUEST_ENVELOPE.value))
    except ValueError:
        packet_kind = PacketKind.REQUEST_ENVELOPE
    try:
        side_effect_class = SideEffectClass(raw.get("side_effect_class", SideEffectClass.NONE.value))
    except ValueError:
        side_effect_class = SideEffectClass.NONE

    request = GovernanceReviewRequest(
        request_id=str(raw.get("request_id", "unknown")),
        trace_id=str(raw.get("trace_id", "unknown")),
        run_id=str(raw.get("run_id", "unknown")),
        tenant_id=str(raw.get("tenant_id", "unknown")),
        caller_id=str(raw.get("caller_id", "unknown")),
        packet_kind=packet_kind,
        side_effect_class=side_effect_class,
    )
    triage = TriageReport(
        governance_mode=GovernanceMode.RUNTIME_CHECK,
        risk_tier_band=RiskTierBandV5.HIGH,
        review_depth=ReviewDepth.LOCKDOWN,
        triage_flags=(TriageFlag.HARD_CONSTRAINT_CANDIDATE,),
        next_lane=NextLane.DECISION_RAIL_REJECT,
    )
    origin = OriginTrustManifest(
        labeled_fields={},
        boundary_classification=BoundaryClassification.REJECTED,
    )
    replay = seal_replay_envelope(
        request=request,
        decision_verdict=DecisionVerdict.REJECT,
        standards_fingerprint=standards,
        span_id=span_id,
        route_id=route_id,
    )
    audit = build_audit_log_event(
        request=request,
        decision=DecisionVerdict.REJECT,
        reason_codes=tuple(f.code.value for f in entry.failures),
        compliance_hash=replay.compliance_hash,
        actor=actor,
        timestamp_iso=timestamp_iso,
    )
    return emit_verdict(
        review_request=request,
        triage=triage,
        origin_trust=origin,
        entry_failures=entry.failures,
        additional_reason_codes=(ReasonCode.MISSING_AUTHORITY,),
        runtime_final_action="reject",
        capability_token=None,
        sandbox_envelope=None,
        replay_envelope=replay,
        audit_log_event=audit,
        governance_reports={
            "triage_report": triage.to_dict(),
            "origin_boundary_report": origin.to_dict(),
            "g0_entry_report": {
                "accepted": False,
                "failures": [f.to_dict() for f in entry.failures],
            },
        },
        standards_fingerprint=standards,
    )


def certify_packet(
    *,
    raw_packet: Mapping[str, Any],
    standards: StandardsFingerprint | None = None,
    risk_tier_hint: RiskTierBandV5 = RiskTierBandV5.LOW,
    incident_suspected: bool = False,
    static_only: bool = False,
    declared_authority: tuple[str, ...] | None = None,
    declared_read_only: bool = False,
    text_samples: Iterable[str] = (),
    field_payloads: Mapping[str, str] | None = None,
    runtime_final_action: str | None = None,
    capability_token: CapabilityTokenV5 | None = None,
    sandbox_envelope: SandboxEnvelope | None = None,
    hitl_disposition: HITLDispositionPacket | None = None,
    runtime_regression: RuntimeRegressionReport | None = None,
    actor: str = "L5.governance_plane",
    span_id: str = "root",
    route_id: str = "",
    timestamp_iso: str | None = None,
    additional_reason_codes: tuple[ReasonCode, ...] = (),
    declared_mode: GovernanceMode | None = None,
    # Optional v4 / CI bridge outputs. Each is a JSON-serializable dict
    # produced by ``agentic_core.L5_safety.v5.bridges.bridge_*``. When
    # supplied, each one populates the matching named report and may
    # surface a reason code. None means "delegated module did not run".
    static_report: Mapping[str, Any] | None = None,
    runtime_guardrail_report: Mapping[str, Any] | None = None,
    handoff_report: Mapping[str, Any] | None = None,
    policy_validation_report: Mapping[str, Any] | None = None,
    egress_report: Mapping[str, Any] | None = None,
    registry_match_report: Mapping[str, Any] | None = None,
) -> GovernanceResult:
    """Compose the v5 governance pipeline.

    Inputs map directly to spec sections:
    - ``raw_packet`` → G0 entry contract
    - ``risk_tier_hint`` / ``incident_suspected`` / ``static_only`` → G1
    - ``text_samples`` / ``field_payloads`` → G1 injection scan + G2a
    - ``runtime_final_action`` → optional v4 runtime-lane composition
    - ``capability_token`` / ``sandbox_envelope`` → R7 outputs the caller
      already produced (only consumed when verdict is CERTIFY)
    """
    standards = standards or StandardsFingerprint(
        tags=(StandardsTag.NIST_AI_RMF, StandardsTag.ISO_42001),
    )
    timestamp_iso = timestamp_iso or _utc_now_iso()

    # G0 -----------------------------------------------------------
    entry = validate_entry_packet(raw_packet, declared_read_only=declared_read_only)
    if not entry.accepted or entry.request is None:
        return _empty_govresult_for_failed_entry(
            raw=raw_packet,
            entry=entry,
            standards=standards,
            actor=actor,
            span_id=span_id,
            route_id=route_id,
            timestamp_iso=timestamp_iso,
        )

    request = entry.request

    # G1 -----------------------------------------------------------
    triage = triage_request(
        request,
        risk_tier_hint=risk_tier_hint,
        incident_suspected=incident_suspected,
        static_only=static_only,
        text_samples=text_samples,
        declared_authority=declared_authority,
        declared_mode=declared_mode,
    )

    # G2a ----------------------------------------------------------
    origin = classify_origins(
        raw_labels=request.origin_trust_manifest_raw,
        field_payloads=field_payloads,
    )

    # Replay sealing (R12) ----------------------------------------
    # Provisional verdict so we can hash it; the rail may downgrade and we
    # re-seal once. This double-seal is cheap (deterministic JSON sha256).
    provisional = DecisionVerdict.CERTIFY  # placeholder
    replay = seal_replay_envelope(
        request=request,
        decision_verdict=provisional,
        standards_fingerprint=standards,
        span_id=span_id,
        route_id=route_id,
        capability_token_hash=capability_token.allowed_args_hash if capability_token else "",
        sandbox_envelope_hash="",
        prompt_artifact_hash="",
        evidence_contract_hash="",
        output_schema_hash="",
        tool_invocation_hashes=(),
        model_invocation_hashes=(),
        state_diff_hash="",
        human_disposition_hash="",
    )

    # Decision rail -----------------------------------------------
    audit = build_audit_log_event(
        request=request,
        decision=DecisionVerdict.CERTIFY,  # placeholder, rail may overwrite
        reason_codes=(),
        compliance_hash=replay.compliance_hash,
        actor=actor,
        timestamp_iso=timestamp_iso,
    )

    # Spec lines 731–745: GovernanceResult.governance_reports must surface
    # every named sub-report. v5 populates the four reports it produces
    # natively; the rest are placeholders kept in shape so downstream
    # consumers can pattern-match on a stable wire schema.
    full_reports = {
        "triage_report": triage.to_dict(),
        "origin_boundary_report": origin.to_dict(),
        "g0_entry_report": {"accepted": True, "failures": []},
        "authority_context_report": {
            "policy_hash": request.policy_hash,
            "blueprint_hash": request.blueprint_hash,
            "registry_digest_set": list(request.registry_digest_set),
            "principal_chain_id": request.principal_chain_id,
        },
        # Lanes that v4 / external modules own. Bridge outputs (when
        # supplied) populate the spec-named report; otherwise empty dict
        # preserves the wire shape.
        "static_report": dict(static_report) if static_report else {},
        "runtime_guardrail_report": (
            dict(runtime_guardrail_report) if runtime_guardrail_report else {}
        ),
        "route_alignment_report": {},
        "handoff_report": dict(handoff_report) if handoff_report else {},
        "context_boundary_report": {},
        "policy_validation_report": (
            dict(policy_validation_report) if policy_validation_report else {}
        ),
        "token_sandbox_report": {
            "capability_token": capability_token.to_dict() if capability_token else None,
            "sandbox_envelope": sandbox_envelope.to_dict() if sandbox_envelope else None,
            "registry_match": dict(registry_match_report) if registry_match_report else {},
        },
        "egress_report": dict(egress_report) if egress_report else {},
        "HITL_report": hitl_disposition.to_dict() if hitl_disposition else {},
        "runtime_regression_report": runtime_regression.to_dict() if runtime_regression else {},
        "audit_seal_report": {"compliance_hash": replay.compliance_hash},
    }

    # Bridge fail-results surface as reason codes on the rail. Codes are
    # drawn from the spec-line-663-681 reason-code set; bridges are
    # mapped onto the closest semantic match.
    bridge_reason_codes: list[ReasonCode] = []
    if static_report and static_report.get("passed") is False:
        # S1 blueprint violation → POLICY_VIOLATION (spec line 663
        # subsumes structural-rule failures under policy-class).
        bridge_reason_codes.append(ReasonCode.POLICY_VIOLATION)
    if runtime_guardrail_report and runtime_guardrail_report.get("decision") == "reject":
        # R1/R2 guardrail reject → INJECTION_DETECTED (spec line 668)
        bridge_reason_codes.append(ReasonCode.INJECTION_DETECTED)
    if handoff_report and handoff_report.get("approved") is False:
        # R4 handoff failure → CONTEXT_BLEED / CROSS_TENANT_RISK
        bridge_reason_codes.append(ReasonCode.CONTEXT_BLEED)
    if policy_validation_report and policy_validation_report.get("passed") is False:
        bridge_reason_codes.append(ReasonCode.POLICY_VIOLATION)
    if registry_match_report and registry_match_report.get("matched") is False:
        bridge_reason_codes.append(ReasonCode.REGISTRY_MISMATCH)
    if egress_report and egress_report.get("decision") == "reject":
        # R9 connector/network egress violation → CONNECTOR_SCOPE_MISMATCH
        bridge_reason_codes.append(ReasonCode.CONNECTOR_SCOPE_MISMATCH)
    additional_reason_codes = additional_reason_codes + tuple(bridge_reason_codes)

    # Spec R11 — drift detection fold-in: if the regression report failed,
    # surface DRIFT_DETECTED so the rail can ESCALATE/REJECT appropriately.
    drift_reason_codes: tuple[ReasonCode, ...] = ()
    if runtime_regression is not None and not runtime_regression.passed:
        drift_reason_codes = (ReasonCode.DRIFT_DETECTED,)
    additional_reason_codes = additional_reason_codes + drift_reason_codes

    # Spec R10 — if the HITL packet exists and the human REJECTED, force
    # the rail toward REJECT.
    if hitl_disposition is not None and hitl_disposition.decision == "REJECT":
        runtime_final_action = "reject"

    result = emit_verdict(
        review_request=request,
        triage=triage,
        origin_trust=origin,
        entry_failures=entry.failures,
        additional_reason_codes=additional_reason_codes,
        runtime_final_action=runtime_final_action,
        capability_token=capability_token,
        sandbox_envelope=sandbox_envelope,
        replay_envelope=replay,
        audit_log_event=audit,
        governance_reports=full_reports,
        standards_fingerprint=standards,
    )

    # Re-seal replay with the final verdict so compliance_hash binds it.
    import hashlib as _hashlib
    import json as _json

    human_hash = ""
    if hitl_disposition is not None:
        human_hash = _hashlib.sha256(
            _json.dumps(hitl_disposition.to_dict(), sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()
    final_replay = seal_replay_envelope(
        request=request,
        decision_verdict=result.decision,
        standards_fingerprint=standards,
        span_id=span_id,
        route_id=route_id,
        capability_token_hash=capability_token.allowed_args_hash if capability_token else "",
        human_disposition_hash=human_hash,
    )
    final_audit = build_audit_log_event(
        request=request,
        decision=result.decision,
        reason_codes=tuple(c.value for c in result.reason_codes),
        compliance_hash=final_replay.compliance_hash,
        actor=actor,
        timestamp_iso=timestamp_iso,
    )

    # GovernanceResult is frozen; rebuild with re-sealed envelope + audit.
    from dataclasses import replace as _replace

    return _replace(
        result,
        replay_envelope=final_replay,
        compliance_hash=final_replay.compliance_hash,
        audit_log_event=final_audit,
    )


__all__ = ["certify_packet"]
