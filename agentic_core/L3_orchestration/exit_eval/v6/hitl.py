"""v6 §X3B — HITL flow: H1 FREEZE -> H2 PACKET -> H3 REVIEW -> H4 DECISION
plus L5 RE-CLEARANCE GATE.

Spec invariant: human input is untrusted DATA until L5 re-clears it. No human
change bypasses L5. The re-clearance step re-runs the relevant X1 gates on
the modified packet.
"""

from __future__ import annotations

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


__all__ = [
    "H1_FREEZE_FIELDS",
    "HITLDecision",
    "HITLPacket",
    "HITLVerdict",
    "L5ReclearanceResult",
    "materialize_review_packet",
    "run_l5_reclearance",
]
