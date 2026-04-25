"""v6 §X3 — Disposition packet builders.

Each ``build_x3*`` function returns the spec-defined required output packet
for its disposition. ``build_x3_packet`` dispatches on the aggregate-decision
disposition and returns the right packet shape.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateVerdict,
    V6Disposition,
    X3AllowPacket,
    X3CommitRequestPacket,
    X3DenyPacket,
    X3EscalatePacket,
    X3SafeAbstainPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision


def _commit_request_id(packet: ExitReviewPacket) -> str:
    """Deterministic commit_request_id derived from replay+run identity."""
    raw = f"{packet.replay_key}|{packet.run_id}|{packet.policy_hash}".encode("utf-8")
    return f"crq-{hashlib.sha256(raw).hexdigest()[:16]}"


def _user_safe_message(decision: AggregateDecision) -> str:
    if decision.disposition is V6Disposition.DENY:
        return "Your request could not be completed safely. It has been denied or rerouted to a safer path."
    return ""


def build_x3a_deny(
    packet: ExitReviewPacket,
    decision: AggregateDecision,
    *,
    sub_disposition: str = "DENY_STOP",
    safe_partial_artifact_id: str = "",
    replan_hint: str = "",
) -> X3DenyPacket:
    return X3DenyPacket(
        sub_disposition=sub_disposition,
        reason_codes=list(decision.reason_codes),
        failed_gate_ids=list(decision.failed_gate_ids),
        user_safe_message=_user_safe_message(decision),
        safe_partial_artifact_id=safe_partial_artifact_id,
        replan_hint=replan_hint,
        l6_failure_packet={
            "rationale": decision.rationale,
            "verdicts": [
                {"gate_id": v.gate_id, "result": v.result.value, "reasons": list(v.reason_codes)}
                for v in decision.triggering_verdicts
            ],
        },
        trace_root=packet.trace_root,
    )


def build_x3b_escalate(
    packet: ExitReviewPacket,
    decision: AggregateDecision,
    *,
    review_packet_id: str = "",
    h1_freeze_state: dict[str, Any] | None = None,
    review_packet_contents: dict[str, Any] | None = None,
) -> X3EscalatePacket:
    if not review_packet_id:
        raw = f"escalate|{packet.replay_key}|{packet.run_id}".encode("utf-8")
        review_packet_id = f"hitl-{hashlib.sha256(raw).hexdigest()[:16]}"
    return X3EscalatePacket(
        trigger_reasons=list(decision.reason_codes) or [decision.rationale],
        review_packet_id=review_packet_id,
        h1_freeze_state=dict(h1_freeze_state or {}),
        review_packet_contents=dict(review_packet_contents or {}),
        trace_root=packet.trace_root,
    )


def build_x3c_commit_request(
    packet: ExitReviewPacket,
    decision: AggregateDecision,
    *,
    grader_verdict_bundle: list[GateVerdict] | None = None,
) -> X3CommitRequestPacket:
    sd = packet.state_diff or {}
    return X3CommitRequestPacket(
        commit_request_id=_commit_request_id(packet),
        request_id=packet.request_id,
        run_id=packet.run_id,
        trace_root=packet.trace_root,
        route_contract=dict(packet.route_contract),
        policy_hash=packet.policy_hash,
        blueprint_hash=packet.blueprint_hash,
        replay_key=packet.replay_key,
        compliance_hash=packet.compliance_hash,
        hmac_sig=packet.hmac_sig,
        capability_token=dict(packet.capability_token),
        state_diff=dict(sd),
        write_intent_class=packet.write_intent_class,
        before_snapshot=dict(sd.get("before_snapshot", {}) or {}),
        after_proposed_snapshot=dict(sd.get("after_proposed_snapshot", {}) or {}),
        rollback_plan=dict(sd.get("rollback_plan", {}) or {}),
        blast_radius=str(sd.get("blast_radius", "")),
        evidence_citation_map=dict(packet.evidence_bundle),
        hitl_decision_receipt=dict(packet.hitl_packet),
        grader_verdict_bundle=list(grader_verdict_bundle or []),
        pass_k_consistency_receipt=dict((packet.grader_composition or {}).get("consistency", {})),
        replay_determinism_digest=packet.replay_key,
        trace_evidence_seal=str((packet.otel_spans or {}).get("evidence_seal", "")),
    )


def build_x3d_allow(
    packet: ExitReviewPacket,
    decision: AggregateDecision,
    *,
    final_response: str = "",
    commit_receipt_id: str = "",
) -> X3AllowPacket:
    out = packet.output or {}
    return X3AllowPacket(
        final_response=final_response or str(out.get("text", "")),
        schema_status="valid" if out.get("schema_valid", True) else "invalid",
        evidence_status=str((packet.final_evidence_contract or {}).get("c0_status", "")),
        commit_receipt_id=commit_receipt_id,
        trace_root=packet.trace_root,
        runtime_exhaust_manifest={
            "rationale": decision.rationale,
            "track_label": packet.track_label,
            "produced_at": int(time.time()),
        },
    )


def build_x3e_safe_abstain(
    packet: ExitReviewPacket,
    decision: AggregateDecision,
    *,
    abstain_reason: str = "",
    minimal_clarification_question: str = "",
    safe_alternative: str = "",
    failed_support_target: str = "",
) -> X3SafeAbstainPacket:
    reason = abstain_reason or "; ".join(decision.reason_codes) or decision.rationale
    return X3SafeAbstainPacket(
        abstain_reason=reason,
        minimal_clarification_question=minimal_clarification_question,
        safe_alternative=safe_alternative,
        failed_support_target=failed_support_target,
        trace_root=packet.trace_root,
    )


def build_x3_packet(
    packet: ExitReviewPacket,
    decision: AggregateDecision,
    *,
    grader_verdict_bundle: list[GateVerdict] | None = None,
    final_response: str = "",
):
    """Dispatch to the right X3* packet builder based on decision.disposition."""
    if decision.disposition is V6Disposition.DENY:
        return build_x3a_deny(packet, decision)
    if decision.disposition is V6Disposition.ESCALATE:
        return build_x3b_escalate(packet, decision)
    if decision.disposition is V6Disposition.COMMIT_REQUEST:
        return build_x3c_commit_request(packet, decision, grader_verdict_bundle=grader_verdict_bundle)
    if decision.disposition is V6Disposition.ALLOW:
        return build_x3d_allow(packet, decision, final_response=final_response)
    if decision.disposition is V6Disposition.SAFE_ABSTAIN:
        return build_x3e_safe_abstain(packet, decision)
    raise ValueError(f"unknown disposition: {decision.disposition!r}")


__all__ = [
    "build_x3a_deny",
    "build_x3b_escalate",
    "build_x3c_commit_request",
    "build_x3d_allow",
    "build_x3e_safe_abstain",
    "build_x3_packet",
]
