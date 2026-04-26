"""v6 §X3B — HITL flow: H1 FREEZE -> H2 PACKET -> H3 REVIEW -> H4 DECISION
plus L5 RE-CLEARANCE GATE.

Spec invariant: human input is untrusted DATA until L5 re-clears it. No human
change bypasses L5. The re-clearance step re-runs the relevant X1 gates on
the modified packet.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateVerdict,
    V6Disposition,
)
from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import GATE_EVALUATORS

# Spec §X3B H1 — fields that MUST be in the freeze state.
H1_FREEZE_FIELDS: tuple[str, ...] = (
    "auth_state",
    "write_auth",
    "capability_token_status",
    "pending_diffs",
    "provider_egress",
    "external_action",
    "additional_retrieval",
    "durable_write",
)


class HITLVerdict(str, Enum):
    """Spec §X3B H4 — bounded human verdicts."""

    APPROVE = "APPROVE"
    MODIFY_DIFF = "MODIFY_DIFF"
    REJECT = "REJECT"
    RETURN_TO_L1 = "RETURN_TO_L1"
    REQUEST_MORE_EVIDENCE = "REQUEST_MORE_EVIDENCE"
    REQUEST_REPLAY = "REQUEST_REPLAY"
    REQUEST_SCHEMA_REPAIR = "REQUEST_SCHEMA_REPAIR"


@dataclass(slots=True)
class HITLDecision:
    """Spec §X3B H4 — verdict + auxiliary data."""

    verdict: HITLVerdict
    modified_packet: ExitReviewPacket | None = None
    rationale: str = ""
    reviewer_id: str = ""
    decision_at_ms: int = 0


@dataclass(slots=True)
class HITLPacket:
    """Spec §X3B H2 — bounded review packet contents.

    Constructed via ``materialize_review_packet``. The ``contents`` dict
    omits sensitive fields beyond minimal need-to-know per spec.
    """

    review_packet_id: str
    contents: dict[str, Any] = field(default_factory=dict)
    h1_freeze_state: dict[str, Any] = field(default_factory=dict)


def _h1_freeze(packet: ExitReviewPacket) -> dict[str, Any]:
    """H1 FREEZE — produce the freeze state dict."""
    return {
        "auth_state": "FROZEN",
        "write_auth": "NONE",
        "capability_token_status": "SUSPENDED",
        "pending_diffs": "LOCKED",
        "provider_egress": "PAUSED",
        "external_action": "PAUSED",
        "additional_retrieval": "BLOCKED_UNLESS_REQUEST_MORE_EVIDENCE",
        "durable_write": "BLOCKED",
        "frozen_run_id": packet.run_id,
        "frozen_replay_key": packet.replay_key,
    }


def materialize_review_packet(
    packet: ExitReviewPacket,
    verdicts: list[GateVerdict],
    *,
    review_packet_id: str,
) -> HITLPacket:
    """Spec §X3B H2 — materialize bounded review packet for human review.

    Includes only the fields the spec enumerates. Sensitive raw payload data
    is intentionally excluded; reviewers see summaries + identity refs.
    """
    contents = {
        "request_summary": {
            "request_id": packet.request_id,
            "run_id": packet.run_id,
            "trace_root": packet.trace_root,
        },
        "route_contract": dict(packet.route_contract),
        "policy_hash": packet.policy_hash,
        "blueprint_hash": packet.blueprint_hash,
        "source_type": packet.source_type.value,
        "proposed_diff": dict(packet.state_diff),
        "write_intent_class": packet.write_intent_class,
        "blast_radius": (packet.state_diff or {}).get("blast_radius", ""),
        "rollback_plan": (packet.state_diff or {}).get("rollback_plan", {}),
        "grader_composition": dict(packet.grader_composition),
        "per_dimension_scores": [
            {
                "gate_id": v.gate_id,
                "result": v.result.value,
                "score": v.score,
                "threshold": v.threshold,
                "reasons": list(v.reason_codes),
                "abstain_flag": v.abstain_flag,
            }
            for v in verdicts
        ],
        "trajectory_snapshot": dict(packet.trajectory_snapshot),
        "citation_support_map": dict(packet.evidence_bundle),
        "replay_key": packet.replay_key,
        "deterministic_receipts": (packet.exec_trace or {}).get("replay_receipts", {}),
        "pass_k_evidence": (packet.grader_composition or {}).get("consistency", {}),
        "trace_coverage_map": dict(packet.otel_spans or {}),
        "anomaly_flags": list(packet.anomaly_flags),
    }
    return HITLPacket(
        review_packet_id=review_packet_id,
        contents=contents,
        h1_freeze_state=_h1_freeze(packet),
    )


# ---- L5 re-clearance gate ----


# Mapping from HITLVerdict to the X1 gates that MUST be re-run before
# proceeding. Spec §X3B "L5 RE-CLEARANCE GATE".
_RECLEAR_GATES: dict[HITLVerdict, tuple[str, ...]] = {
    HITLVerdict.APPROVE: ("X1A", "X1C", "X1F"),
    HITLVerdict.MODIFY_DIFF: ("X1A", "X1B", "X1C", "X1D", "X1E", "X1F", "X1G", "X1J"),
    HITLVerdict.REJECT: (),  # No re-clearance — straight to X3A
    HITLVerdict.RETURN_TO_L1: (),
    HITLVerdict.REQUEST_MORE_EVIDENCE: ("X1D",),
    HITLVerdict.REQUEST_REPLAY: ("X1H", "X1I"),
    HITLVerdict.REQUEST_SCHEMA_REPAIR: ("X1B", "X1C", "X1H"),
}


@dataclass(slots=True)
class L5ReclearanceResult:
    """Outcome of L5 re-clearance after a HITL decision."""

    next_disposition: V6Disposition
    re_run_verdicts: list[GateVerdict] = field(default_factory=list)
    reroute_target: str = ""  # e.g. "L1" for RETURN_TO_L1
    notes: str = ""


def run_l5_reclearance(
    decision: HITLDecision,
    packet: ExitReviewPacket,
) -> L5ReclearanceResult:
    """Spec §X3B L5 RE-CLEARANCE GATE — apply post-HITL routing.

    Returns the next-disposition handoff. Caller is responsible for invoking
    ``aggregate_decision()`` again on the re-run verdicts before producing
    the final X3 packet.
    """
    if decision.verdict is HITLVerdict.REJECT:
        return L5ReclearanceResult(
            next_disposition=V6Disposition.DENY,
            notes="HITL rejected; route to X3A DENY_STOP.",
        )
    if decision.verdict is HITLVerdict.RETURN_TO_L1:
        return L5ReclearanceResult(
            next_disposition=V6Disposition.DENY,
            reroute_target="L1",
            notes="HITL chose RETURN_TO_L1; route to X3A REROUTE_TO_L1.",
        )

    # MODIFY_DIFF / APPROVE / REQUEST_* — re-run relevant X1 gates on the
    # (possibly modified) packet. APPROVE without modification still re-runs
    # the policy + sandbox + adversarial trio per spec.
    target_packet = decision.modified_packet or packet
    gates_to_run = _RECLEAR_GATES.get(decision.verdict, ())
    re_run = [GATE_EVALUATORS[g](target_packet) for g in gates_to_run]
    # Caller routes via aggregate_decision on the re-run verdicts; we only
    # surface them. Default placeholder disposition is ESCALATE (still in
    # review) — caller MUST run the matrix to finalize.
    return L5ReclearanceResult(
        next_disposition=V6Disposition.ESCALATE,
        re_run_verdicts=re_run,
        notes=f"L5 re-cleared after {decision.verdict.value}; caller must run X2 matrix.",
    )


# ---- §5.6 spec-named contract receipts ----------------------------------
#
# These dataclasses match the receipt shapes spelled out in
# 05.6_Exit_HITL_Freeze_Review_and_Reclearance_detailed.md.
# They wrap the existing ``HITLPacket`` / ``HITLDecision`` / ``L5ReclearanceResult``
# without breaking back-compat: the original types remain the runtime shapes;
# these names are the canonical 5.6 ledger-grade receipts.


@dataclass(slots=True)
class FreezeReceipt:
    """Spec §5.6 H1 — FreezeReceipt."""

    freeze_id: str
    exit_review_packet_id: str
    request_id: str
    run_id: str
    trace_root: str
    reason_codes: list[str] = field(default_factory=list)
    frozen_artifact_refs: list[str] = field(default_factory=list)
    pending_state_diff_refs: list[str] = field(default_factory=list)
    suspended_capability_refs: list[str] = field(default_factory=list)
    policy_hash: str = ""
    blueprint_hash: str = ""
    replay_key: str = ""
    freeze_digest: str = ""


@dataclass(slots=True)
class HumanReviewPacket:
    """Spec §5.6 H2 — HumanReviewPacket (canonical receipt shape).

    Distinct from runtime ``HITLPacket``: this carries the final receipt for
    L5 / audit, with sensitive_data_manifest separated, allowed/prohibited
    actions enumerated, and ``packet_hash`` deterministically derived.
    """

    review_packet_id: str
    freeze_id: str
    escalation_reason_codes: list[str] = field(default_factory=list)
    human_decision_options: list[str] = field(default_factory=list)
    minimal_context_refs: list[str] = field(default_factory=list)
    evidence_map_refs: list[str] = field(default_factory=list)
    proposed_diff_refs: list[str] = field(default_factory=list)
    policy_threshold_refs: list[str] = field(default_factory=list)
    replay_refs: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
    sensitive_data_manifest: dict[str, Any] = field(default_factory=dict)
    allowed_actions: list[str] = field(default_factory=list)
    prohibited_actions: list[str] = field(default_factory=list)
    packet_hash: str = ""


@dataclass(slots=True)
class HumanDecisionReceipt:
    """Spec §5.6 H4 — HumanDecisionReceipt."""

    human_decision_id: str
    review_packet_id: str
    reviewer_id_ref: str
    decision: str  # APPROVE | MODIFY_DIFF | REJECT | RETURN_TO_L1 | REQUEST_*
    rationale_ref: str = ""
    modification_diff_ref: str = ""
    requested_reentry_target: str = ""
    timestamp: int = 0
    data_not_authority_assertion: bool = True
    digest: str = ""


@dataclass(slots=True)
class L5ReclearanceRequest:
    """Spec §5.6 L5 RECLEARANCE REQUEST — required for any human-touched outcome."""

    reclearance_request_id: str
    human_decision_receipt_ref: str
    original_exit_review_packet_ref: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    modified_packet_ref: str = ""
    modified_diff_ref: str = ""
    authority_label_manifest: dict[str, Any] = field(default_factory=dict)
    origin_trust_manifest: dict[str, Any] = field(default_factory=dict)
    scope_delta_report: dict[str, Any] = field(default_factory=dict)
    required_rechecks: list[str] = field(default_factory=list)
    digest: str = ""


# ---- spec-named builders --------------------------------------------------


def _digest(*parts: str) -> str:
    raw = "|".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def build_freeze_receipt(
    packet: ExitReviewPacket,
    *,
    reason_codes: list[str],
    frozen_artifact_refs: list[str] | None = None,
    pending_state_diff_refs: list[str] | None = None,
    suspended_capability_refs: list[str] | None = None,
) -> FreezeReceipt:
    """Spec §5.6 H1 — produce a ``FreezeReceipt`` for a packet entering review."""
    freeze_id = f"frz-{_digest(packet.replay_key, packet.run_id, 'freeze')}"
    digest = _digest(freeze_id, packet.policy_hash, packet.blueprint_hash, packet.replay_key)
    return FreezeReceipt(
        freeze_id=freeze_id,
        exit_review_packet_id=f"erp-{_digest(packet.replay_key, packet.run_id)}",
        request_id=packet.request_id,
        run_id=packet.run_id,
        trace_root=packet.trace_root,
        reason_codes=list(reason_codes),
        frozen_artifact_refs=list(frozen_artifact_refs or []),
        pending_state_diff_refs=list(pending_state_diff_refs or []),
        suspended_capability_refs=list(suspended_capability_refs or []),
        policy_hash=packet.policy_hash,
        blueprint_hash=packet.blueprint_hash,
        replay_key=packet.replay_key,
        freeze_digest=digest,
    )


def build_human_review_packet(
    packet: ExitReviewPacket,
    freeze: FreezeReceipt,
    *,
    review_packet_id: str,
    escalation_reason_codes: list[str],
    minimal_context_refs: list[str] | None = None,
    evidence_map_refs: list[str] | None = None,
    proposed_diff_refs: list[str] | None = None,
    sensitive_data_manifest: dict[str, Any] | None = None,
) -> HumanReviewPacket:
    """Spec §5.6 H2 — produce a bounded ``HumanReviewPacket`` for L5/audit.

    Decision options are fixed by the spec — the H4 verdict enum.
    """
    options = [v.value for v in HITLVerdict]
    prohibited = [
        "L4_DIRECT_WRITE",
        "POLICY_OVERRIDE",
        "SCOPE_WIDENING",
        "SECRET_LEAK",
        "AUTHORITY_CLAIM_ON_RETRIEVED_TEXT",
        "BYPASS_L5",
        "FORCE_UNSUPPORTED_FACT",
    ]
    digest = _digest(
        freeze.freeze_id,
        review_packet_id,
        ",".join(escalation_reason_codes),
        packet.replay_key,
    )
    return HumanReviewPacket(
        review_packet_id=review_packet_id,
        freeze_id=freeze.freeze_id,
        escalation_reason_codes=list(escalation_reason_codes),
        human_decision_options=options,
        minimal_context_refs=list(minimal_context_refs or []),
        evidence_map_refs=list(evidence_map_refs or []),
        proposed_diff_refs=list(proposed_diff_refs or []),
        policy_threshold_refs=[packet.policy_hash, packet.blueprint_hash],
        replay_refs=[packet.replay_key] if packet.replay_key else [],
        trace_refs=[packet.trace_root] if packet.trace_root else [],
        sensitive_data_manifest=dict(sensitive_data_manifest or {}),
        allowed_actions=options,
        prohibited_actions=prohibited,
        packet_hash=digest,
    )


def build_human_decision_receipt(
    review_packet_id: str,
    decision: HITLDecision,
    *,
    reviewer_id_ref: str = "",
) -> HumanDecisionReceipt:
    """Spec §5.6 H4 — convert a runtime ``HITLDecision`` to a ledger-grade receipt."""
    ts = decision.decision_at_ms or int(time.time() * 1000)
    digest_id = _digest(
        review_packet_id, decision.verdict.value, str(ts), decision.reviewer_id or reviewer_id_ref
    )
    return HumanDecisionReceipt(
        human_decision_id=f"hd-{digest_id}",
        review_packet_id=review_packet_id,
        reviewer_id_ref=reviewer_id_ref or decision.reviewer_id,
        decision=decision.verdict.value,
        rationale_ref=decision.rationale,
        modification_diff_ref=("modified" if decision.modified_packet else ""),
        requested_reentry_target=("L1" if decision.verdict is HITLVerdict.RETURN_TO_L1 else ""),
        timestamp=ts,
        data_not_authority_assertion=True,
        digest=digest_id,
    )


def build_l5_reclearance_request(
    packet: ExitReviewPacket,
    decision_receipt: HumanDecisionReceipt,
    *,
    required_rechecks: list[str] | None = None,
) -> L5ReclearanceRequest:
    """Spec §5.6 L5 RECLEARANCE REQUEST — produced before any modified-packet outcome."""
    rec_id = _digest(
        decision_receipt.human_decision_id,
        packet.replay_key,
        packet.policy_hash,
    )
    digest = _digest(
        rec_id,
        decision_receipt.decision,
        ",".join(required_rechecks or []),
    )
    return L5ReclearanceRequest(
        reclearance_request_id=f"recl-{rec_id}",
        human_decision_receipt_ref=decision_receipt.human_decision_id,
        original_exit_review_packet_ref=f"erp-{_digest(packet.replay_key, packet.run_id)}",
        policy_hash=packet.policy_hash,
        blueprint_hash=packet.blueprint_hash,
        replay_key=packet.replay_key,
        modified_packet_ref=decision_receipt.modification_diff_ref,
        modified_diff_ref=decision_receipt.modification_diff_ref,
        authority_label_manifest={
            "human_review_data": "data_not_authority",
            "retrieved_text": "data_not_authority",
            "policy_evidence_ref": packet.policy_hash,
        },
        origin_trust_manifest={
            "reviewer_id_ref": decision_receipt.reviewer_id_ref,
            "data_not_authority_assertion": True,
        },
        scope_delta_report={
            "decision": decision_receipt.decision,
            "modified": bool(decision_receipt.modification_diff_ref),
        },
        required_rechecks=list(required_rechecks or []),
        digest=digest,
    )


__all__ = [
    "FreezeReceipt",
    "H1_FREEZE_FIELDS",
    "HITLDecision",
    "HITLPacket",
    "HITLVerdict",
    "HumanDecisionReceipt",
    "HumanReviewPacket",
    "L5ReclearanceRequest",
    "L5ReclearanceResult",
    "build_freeze_receipt",
    "build_human_decision_receipt",
    "build_human_review_packet",
    "build_l5_reclearance_request",
    "materialize_review_packet",
    "run_l5_reclearance",
]
