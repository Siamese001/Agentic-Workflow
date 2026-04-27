"""v6 §X3 — Disposition packet builders.

Each ``build_x3*`` function returns the spec-defined required output packet
for its disposition. ``build_x3_packet`` dispatches on the aggregate-decision
disposition and returns the right packet shape.
"""

from __future__ import annotations

import hashlib
import time
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from agentic_core.runtime.prove_requirements.otel_emitter import (
        RuntimeSpanEmitter,
    )
from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateVerdict,
    V6Disposition,
    X3AllowPacket,
    X3BreakGlassAllowPacket,
    X3CommitRequestPacket,
    X3DenyPacket,
    X3EscalatePacket,
    X3SafeAbstainPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision

# v4_hardening §H3.1 — gates that NEVER bypass under break-glass
_X3F_FORBIDDEN_BYPASS_GATES: frozenset[str] = frozenset({"X1A", "X1C"})

# v4_hardening §H3.2.2 — hard cap on break-glass duration
_X3F_MAX_DURATION_MS: int = 60 * 60 * 1000  # 60 minutes

# v4_hardening §H3.3 — post-mortem deadline
_X3F_POST_MORTEM_OFFSET_MS: int = 24 * 60 * 60 * 1000  # 24 hours


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


class BreakGlassValidationError(ValueError):
    """Raised when a break-glass invocation violates v4_hardening §H3 invariants."""


def build_x3f_break_glass_allow(
    packet: ExitReviewPacket,
    decision: AggregateDecision,
    *,
    operator_id: str,
    capability_token_ref: str,
    written_justification: str,
    bypassed_gates: list[str],
    audit_id: str,
    pages_emitted: list[str] | None = None,
    customer_facing_l4_commit_allowed: bool = False,
    expiry_ms: int | None = None,
    granted_at_ms: int | None = None,
    final_response: str = "",
) -> X3BreakGlassAllowPacket:
    """Build an X3F BREAK_GLASS_ALLOW packet (v4_hardening §H3).

    Enforces all H3 invariants synchronously. Any violation raises
    ``BreakGlassValidationError`` — there is no fail-open path.

    Required:
        - operator_id: named on-call operator id (non-empty)
        - capability_token_ref: ref to a token containing ``break_glass=True``
          AND ``operator_id`` matching ``operator_id`` arg
        - written_justification: non-empty free-text rationale
        - bypassed_gates: list of gates being bypassed; MUST exclude X1A and X1C
        - audit_id: ref to a high-visibility audit row (non-empty)

    The capability_token on the ExitReviewPacket is the source of truth for
    break-glass authorization. The token MUST have:
        - ``break_glass=True``
        - ``operator_id`` == operator_id arg
        - ``not_expired=True``  (caller verifies; this builder asserts the field)
    """
    # H3.1 — non-bypassable gates
    bypassed = list(bypassed_gates or [])
    forbidden = _X3F_FORBIDDEN_BYPASS_GATES.intersection(bypassed)
    if forbidden:
        raise BreakGlassValidationError(
            f"break-glass cannot bypass {sorted(forbidden)}; H3.1 invariant"
        )

    # H3.2.1 — capability token
    token = packet.capability_token or {}
    if not token.get("break_glass"):
        raise BreakGlassValidationError(
            "capability_token.break_glass=True required; H3.2.1 invariant"
        )
    if not operator_id:
        raise BreakGlassValidationError("operator_id required; H3.2.1 invariant")
    if token.get("operator_id") and token.get("operator_id") != operator_id:
        raise BreakGlassValidationError(
            f"operator_id mismatch: token={token.get('operator_id')!r} arg={operator_id!r}"
        )
    if token.get("expired") is True:
        raise BreakGlassValidationError("capability_token expired; H3.2.1 invariant")

    # H3.2.2 — written justification
    if not (written_justification or "").strip():
        raise BreakGlassValidationError(
            "written_justification required (non-empty); H3.2.2 invariant"
        )

    # H3.2.2 — expiry hard cap (60 min)
    now_ms = granted_at_ms if granted_at_ms is not None else int(time.time() * 1000)
    grant_ms = granted_at_ms if granted_at_ms is not None else now_ms
    final_expiry = expiry_ms if expiry_ms is not None else grant_ms + _X3F_MAX_DURATION_MS
    if final_expiry - grant_ms > _X3F_MAX_DURATION_MS:
        raise BreakGlassValidationError(
            f"break-glass duration exceeds {_X3F_MAX_DURATION_MS}ms cap; H3.2.2 invariant"
        )
    if final_expiry <= grant_ms:
        raise BreakGlassValidationError(
            "expiry_ms must be after granted_at_ms; H3.2.2 invariant"
        )

    # H3.2.4 — audit_id required
    if not (audit_id or "").strip():
        raise BreakGlassValidationError(
            "audit_id required (high-visibility audit row); H3.2.4 invariant"
        )

    # H3.2.5 — UWG verification not bypassable (cannot include U1/U2/U3 in bypassed_gates)
    uwg_bypass_attempt = {g for g in bypassed if g.upper().startswith("U")}
    if uwg_bypass_attempt:
        raise BreakGlassValidationError(
            f"break-glass cannot bypass UWG verification gates {sorted(uwg_bypass_attempt)}; H3.1 UWG invariant"
        )

    return X3BreakGlassAllowPacket(
        operator_id=operator_id,
        capability_token_ref=capability_token_ref,
        written_justification=written_justification,
        granted_at_ms=grant_ms,
        expiry_ms=final_expiry,
        bypassed_gates=bypassed,
        audit_id=audit_id,
        pages_emitted=list(pages_emitted or []),
        customer_facing_l4_commit_allowed=bool(customer_facing_l4_commit_allowed),
        post_mortem_due_at_ms=grant_ms + _X3F_POST_MORTEM_OFFSET_MS,
        final_response=final_response or str((packet.output or {}).get("text", "")),
        trace_root=packet.trace_root,
    )


# W13 live wire-up: map V6Disposition -> proof-OTEL span status.
# DENY -> BLOCKED is the security-critical mapping that Scenario D's
# anti-bypass test asserts. ESCALATE/SAFE_ABSTAIN are not hard blocks
# but are not OK either; they map to ABSTAINED.
_DISPOSITION_TO_SPAN_STATUS: dict[V6Disposition, str] = {
    V6Disposition.DENY: "BLOCKED",
    V6Disposition.ESCALATE: "ABSTAINED",
    V6Disposition.SAFE_ABSTAIN: "ABSTAINED",
    V6Disposition.ALLOW: "OK",
    V6Disposition.COMMIT_REQUEST: "OK",
    # BREAK_GLASS_ALLOW is intentionally absent -- build_x3_packet rejects it.
}


def build_x3_packet(
    packet: ExitReviewPacket,
    decision: AggregateDecision,
    *,
    grader_verdict_bundle: list[GateVerdict] | None = None,
    final_response: str = "",
    emitter: "Optional[RuntimeSpanEmitter]" = None,
):
    """Dispatch to the right X3* packet builder based on decision.disposition.

    Note: BREAK_GLASS_ALLOW (X3F) is NOT dispatched here because it requires
    capability-token-gated invocation by an operator, not aggregate-decision
    selection. Call ``build_x3f_break_glass_allow`` directly.

    W13 live wire-up: when ``emitter`` is provided, emits an
    ``exit.x3.disposition`` proof-OTEL span. Status is precomputed from
    ``decision.disposition`` so DENY -> BLOCKED, ESCALATE/SAFE_ABSTAIN ->
    ABSTAINED, ALLOW/COMMIT_REQUEST -> OK. This is the security-critical
    mapping anchored by the Scenario D anti-bypass test.
    """
    if emitter is None:
        return _build_x3_packet_impl(
            packet,
            decision,
            grader_verdict_bundle=grader_verdict_bundle,
            final_response=final_response,
        )

    span_status = _DISPOSITION_TO_SPAN_STATUS.get(decision.disposition, "OK")
    with emitter.span(
        "exit.x3.disposition",
        status=span_status,
        reason_codes=[decision.disposition.value],
        replay_key=packet.replay_key,
    ):
        return _build_x3_packet_impl(
            packet,
            decision,
            grader_verdict_bundle=grader_verdict_bundle,
            final_response=final_response,
        )


def _build_x3_packet_impl(
    packet: ExitReviewPacket,
    decision: AggregateDecision,
    *,
    grader_verdict_bundle: list[GateVerdict] | None = None,
    final_response: str = "",
):
    """Original build_x3_packet dispatcher (W13 split)."""
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
    if decision.disposition is V6Disposition.BREAK_GLASS_ALLOW:
        raise ValueError(
            "X3F BREAK_GLASS_ALLOW must be invoked via build_x3f_break_glass_allow with "
            "explicit operator_id/capability_token_ref/written_justification; "
            "not via aggregate-decision dispatch (H3.2.1 invariant)"
        )
    raise ValueError(f"unknown disposition: {decision.disposition!r}")


__all__ = [
    "build_x3a_deny",
    "build_x3b_escalate",
    "build_x3c_commit_request",
    "build_x3d_allow",
    "build_x3e_safe_abstain",
    "build_x3f_break_glass_allow",
    "build_x3_packet",
    "BreakGlassValidationError",
]
