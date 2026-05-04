"""W7 P-HITL1 — apps_rg HITL schema dataclasses.

Defines all data contracts for the RuntimeAuthorGate decision loop:

  RuntimeAuthorGateDecisionRequest  — trigger payload emitted by 00C / L2
  BoundedOption                     — one valid choice shown to the human
  HumanReviewDecision               — the human's response (hash-bound)
  HITLReviewPacket                  — carrier into Exit X3B
  L5ReClearanceReceipt              — L5 receipt after re-clearance

None of these types execute code, call input(), or write state.  They are
pure data containers.

Plan: apps-rg-canonical-wireup-c8a4f2 W7 P-HITL1.
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Trigger kind vocabulary
# ---------------------------------------------------------------------------

TRIGGER_KINDS: tuple[str, ...] = (
    "MISSING_BRIEF",
    "STALE_BRIEF",
    "UNSUPPORTED_CLAIM",
    "LOW_CONFIDENCE",
    "RELEASE_APPROVAL",
    "CACHE_PROMOTION",
)


# ---------------------------------------------------------------------------
# Core request / option types
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class BoundedOption:
    """One valid choice surfaced to the human operator."""

    option_id: str
    label: str
    consequence: str
    is_recommended: bool = False


@dataclass(slots=True)
class RuntimeAuthorGateDecisionRequest:
    """Trigger payload emitted by 00C or an L2 DAG step.

    The emitter (00C / L2) builds this and hands it to RuntimeAuthorGate.
    The gate is the only caller of cli_hitl_adapter.prompt().
    """

    request_id: str
    trigger_kind: str
    run_id: str
    input_manifest_hash: str
    recommendations: list[str]
    confidence_score: float
    evidence_refs: list[str]
    bounded_options: list[BoundedOption]
    replay_key: str

    def __post_init__(self) -> None:
        if self.trigger_kind not in TRIGGER_KINDS:
            raise ValueError(
                f"trigger_kind {self.trigger_kind!r} not in {TRIGGER_KINDS}"
            )
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("confidence_score must be in [0.0, 1.0]")
        if not self.bounded_options:
            raise ValueError("bounded_options must be non-empty")


# ---------------------------------------------------------------------------
# Human decision (hash-bound)
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class HumanReviewDecision:
    """Hash-bound human decision.  The decision_hash ties this decision to its
    exact request + chosen option + input manifest — verifiable offline.

    Schema invariant:
        decision_hash == sha256(decision_id + chosen_option_id + input_manifest_hash)
    """

    decision_id: str
    request_id: str
    chosen_option_id: str
    decision_timestamp: str
    input_manifest_hash: str
    decision_hash: str
    replay_key: str
    operator_id: str = "amit"

    @staticmethod
    def compute_hash(
        decision_id: str,
        chosen_option_id: str,
        input_manifest_hash: str,
    ) -> str:
        payload = decision_id + chosen_option_id + input_manifest_hash
        return hashlib.sha256(payload.encode()).hexdigest()

    def verify_hash(self) -> bool:
        expected = self.compute_hash(
            self.decision_id,
            self.chosen_option_id,
            self.input_manifest_hash,
        )
        return self.decision_hash == expected


# ---------------------------------------------------------------------------
# Exit X3B carrier
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class HITLReviewPacket:
    """Carrier of the human decision into Exit V6 X3B.

    Mapping to ExitX3BPacket fields (per plan §W7 schema):
        freeze_reason         → ExitX3BPacket.freeze_code
        input_manifest_hash   → ExitX3BPacket.context_binding_hash
        decision              → ExitX3BPacket.human_review_payload
        l5_receipt            → ExitX3BPacket.re_clearance_receipt

    This is the ONLY channel through which the human decision enters Exit.
    """

    review_id: str
    run_id: str
    freeze_reason: str
    input_manifest_hash: str
    decision: HumanReviewDecision
    l5_receipt: L5ReClearanceReceipt | None = None
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# L5 re-clearance receipt
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class L5ReClearanceReceipt:
    """L5 receipt issued after re-clearance with human_review data.

    gate_verdict.source == GraderType.HUMAN_CALIBRATED (not sovereign).
    L5 policy is still in effect — the human decision is treated as data,
    not as a bypass of L5.
    """

    receipt_id: str
    decision_id: str
    cleared_at: str
    policy_hash: str
    binding_hash: str
    gate_verdict_dict: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def compute_binding_hash(decision_id: str, policy_hash: str) -> str:
        payload = decision_id + policy_hash
        return hashlib.sha256(payload.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def make_decision_request(
    trigger_kind: str,
    run_id: str,
    input_manifest_hash: str,
    recommendations: list[str],
    confidence_score: float,
    evidence_refs: list[str],
    bounded_options: list[BoundedOption],
    replay_key: str,
) -> RuntimeAuthorGateDecisionRequest:
    return RuntimeAuthorGateDecisionRequest(
        request_id=str(uuid.uuid4()),
        trigger_kind=trigger_kind,
        run_id=run_id,
        input_manifest_hash=input_manifest_hash,
        recommendations=recommendations,
        confidence_score=confidence_score,
        evidence_refs=evidence_refs,
        bounded_options=bounded_options,
        replay_key=replay_key,
    )
