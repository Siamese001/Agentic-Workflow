"""Exit-Control HITL Sequence — H1 through H5 (HITL-004).

Implements the bounded, re-clearance-mandatory HITL path for exit-control
escalations from ExitControlGate.ESCALATE_TO_HITL dispositions.

This module is SEPARATE from hitl_gate.py (which handles healing TTY prompts).
The two HITL contexts have fundamentally different semantics:
- Exit-control HITL (this module): state freeze + authority lock + re-clearance loop
- Healing HITL (hitl_gate.py): interactive TTY prompts for destructive file operations

H1  Freeze          — authority_state=FROZEN; write_auth=NONE
H2  Materialize     — produce bounded packet from sealed data only; no live state reference
H3  Human review    — human receives bounded packet; state remains frozen
H4  Validate input  — human response treated as UNTRUSTED DATA; re-enters L5 validator
H5  Re-clearance    — L5 re-clearance gate is the ONLY path to ALLOW or COMMIT

Constraints (HITL-004):
- No SOVEREIGN_AUTO_APPROVE bypass.
- No ARCHIVE_BATCH_ACCEPT bypass.
- No TTY interaction — this gate always materializes a packet; no interactive prompt.
- Human input to re-clear is UNTRUSTED DATA routed through L5 policy validator.
- MODIFY_DIFF without re-clear → BLOCKED.
- APPROVE bypassing L5 re-clearance → BLOCKED.

Layer authority: L5 (cross-cutting policy plane)
Write authority: NONE — no durable commit from this module; all commits route to UWG
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_chooses_exit_disposition,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_materializes_hitl_packet,
    _emit_reads_policy_state,
    _emit_reclears_human_decision,
    _emit_records_execution_trace,
    _emit_seals_result,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_transcripts_response,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "exit_control_hitl")
emit_determinism_digest("p0", "exit_control_hitl")
_emit_reads_policy_state("p1", "exit_control_hitl", "L5")
_emit_verifies_policy("p1", "exit_control_hitl", "policy_check")
_emit_verifies_boundary("p1", "exit_control_hitl", "boundary_check")
_emit_validated_by_safety_plane("p1", "exit_control_hitl", "safety_validation")
_emit_hard_fails_untranscripted("p1", "exit_control_hitl")
_emit_gated_by_confidence("p1", "exit_control_hitl", "confidence_gate")
_emit_escalates_to_human("p1", "exit_control_hitl", "human_escalation")

logger = logging.getLogger(__name__)


class AuthorityState(str, Enum):
    """Authority state for the exit-control HITL sequence."""

    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"


class WriteAuthority(str, Enum):
    """Write authority state during HITL sequence."""

    NORMAL = "NORMAL"
    NONE = "NONE"


class HumanDecision(str, Enum):
    """Valid decisions a human reviewer may submit."""

    APPROVE = "APPROVE"
    DENY = "DENY"
    MODIFY_DIFF = "MODIFY_DIFF"


class ReClearOutcome(str, Enum):
    """Result of the H5 re-clearance gate."""

    CLEARED_ALLOW = "CLEARED_ALLOW"
    CLEARED_COMMIT = "CLEARED_COMMIT"
    BLOCKED = "BLOCKED"


@dataclass
class BoundedPacket:
    """Materialised packet for human review (H2).

    Contains only sealed/frozen data — no live state references, no mutable
    handles.  Human reviewer receives exactly this and nothing more.
    """

    packet_id: str
    trace_id: str
    escalation_reason: str
    sealed_artifact_summary: dict
    authority_state: AuthorityState
    write_authority: WriteAuthority
    materialized_at_trace: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "trace_id": self.trace_id,
            "escalation_reason": self.escalation_reason,
            "sealed_artifact_summary": self.sealed_artifact_summary,
            "authority_state": self.authority_state.value,
            "write_authority": self.write_authority.value,
            "materialized_at_trace": self.materialized_at_trace,
        }


@dataclass
class HumanReviewInput:
    """Untrusted human reviewer input (H3/H4).

    Treated as external untrusted DATA by the H4 validator.
    Contains the decision, optional diff, and the reviewer's identity.
    """

    packet_id: str
    decision: HumanDecision
    reviewer_id: str
    justification: str
    proposed_diff: Optional[dict] = None


@dataclass
class ReClearResult:
    """Output of the H5 re-clearance gate."""

    outcome: ReClearOutcome
    packet_id: str
    trace_id: str
    reviewer_id: str
    reason: str
    re_cleared_artifact: Optional[dict] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "packet_id": self.packet_id,
            "trace_id": self.trace_id,
            "reviewer_id": self.reviewer_id,
            "reason": self.reason,
            "re_cleared_artifact": self.re_cleared_artifact,
        }


class ExitControlHITL:
    """Exit-control HITL sequence: H1 freeze → H2 materialise → H3 review → H4 validate → H5 re-clear.

    Usage::

        hitl = ExitControlHITL()

        # H1 + H2: freeze and materialise
        packet = hitl.freeze_and_materialize(gate_result, sealed_artifact)

        # H3: transmit packet to human reviewer (out of band)
        # ...

        # H4 + H5: receive human input, validate as untrusted data, re-clear
        result = hitl.validate_and_reclear(human_input, packet)
        # result.outcome ∈ {CLEARED_ALLOW, CLEARED_COMMIT, BLOCKED}

    Constraints:
    - MODIFY_DIFF is BLOCKED (no direct diff application; routes back to L2)
    - APPROVE without valid packet_id match is BLOCKED
    - Human input is always re-validated by L5 policy before clearance
    - authority_state=FROZEN is a typed invariant during H1–H5
    """

    def __init__(self, policy_validator: Any | None = None) -> None:
        """
        Args:
            policy_validator: Optional callable(artifact, reviewer_id) → bool.
                              If None, re-clearance requires APPROVE decision + non-empty justification.
        """
        self._policy_validator = policy_validator
        self._active_packets: dict[str, BoundedPacket] = {}

    def freeze_and_materialize(
        self,
        gate_result: Any,
        sealed_artifact: dict[str, Any],
    ) -> BoundedPacket:
        """H1 + H2: freeze authority state and materialise a bounded packet.

        Args:
            gate_result:     ExitGateResult with ESCALATE_TO_HITL disposition.
            sealed_artifact: The sealed L2 artifact under review (read-only snapshot).

        Returns:
            BoundedPacket — the packet to transmit to human reviewer.
        """
        d = gate_result.to_dict()
        trace_id = d["trace_id"]
        packet_id = str(uuid.uuid4())
        mat_trace = hashlib.sha256(f"{packet_id}:{trace_id}".encode()).hexdigest()[:16]

        _emit_snapshots_state(trace_id, "ExitControlHITL.freeze_and_materialize", "h1_freeze")
        _emit_seals_result(trace_id, "ExitControlHITL", "freeze_and_materialize")
        _emit_materializes_hitl_packet(trace_id, "ExitControlHITL", "h2_packet")
        _emit_applies_guardrail(
            trace_id, "ExitControlHITL.freeze_and_materialize", "h1_h2_freeze_materialize"
        )
        _emit_records_execution_trace(trace_id, "L5_POLICY", "ExitControlHITL.freeze_and_materialize")
        _seg = hashlib.sha256(f"{trace_id}:freeze".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(trace_id, _seg, _seg, 0)

        artifact_summary = {k: v for k, v in sealed_artifact.items() if k != "raw_content"}

        packet = BoundedPacket(
            packet_id=packet_id,
            trace_id=trace_id,
            escalation_reason=d.get("reason", ""),
            sealed_artifact_summary=artifact_summary,
            authority_state=AuthorityState.FROZEN,
            write_authority=WriteAuthority.NONE,
            materialized_at_trace=mat_trace,
        )
        self._active_packets[packet_id] = packet

        logger.info(
            "[ExitControlHITL] H1+H2 packet_id=%s trace_id=%s authority=FROZEN",
            packet_id,
            trace_id,
        )
        return packet

    def validate_and_reclear(
        self,
        human_input: HumanReviewInput,
        packet: BoundedPacket,
    ) -> ReClearResult:
        """H4 + H5: validate human input as untrusted DATA; run re-clearance gate.

        Args:
            human_input: Reviewer decision, justification, optional diff.
            packet:      The BoundedPacket previously issued in H2.

        Returns:
            ReClearResult with outcome CLEARED_ALLOW, CLEARED_COMMIT, or BLOCKED.
        """
        trace_id = packet.trace_id

        _emit_snapshots_state(trace_id, "ExitControlHITL.validate_and_reclear", "h4_validate")
        _emit_applies_guardrail(trace_id, "ExitControlHITL.validate_and_reclear", "h4_h5_validate_reclear")
        _emit_records_execution_trace(trace_id, "L5_POLICY", "ExitControlHITL.validate_and_reclear")

        if human_input.packet_id != packet.packet_id:
            return ReClearResult(
                outcome=ReClearOutcome.BLOCKED,
                packet_id=human_input.packet_id,
                trace_id=trace_id,
                reviewer_id=human_input.reviewer_id,
                reason=f"packet_id mismatch: submitted {human_input.packet_id!r} != issued {packet.packet_id!r}",
            )

        if packet.authority_state != AuthorityState.FROZEN:
            return ReClearResult(
                outcome=ReClearOutcome.BLOCKED,
                packet_id=packet.packet_id,
                trace_id=trace_id,
                reviewer_id=human_input.reviewer_id,
                reason="authority_state is not FROZEN — H5 re-clearance requires frozen state invariant",
            )

        if human_input.decision == HumanDecision.MODIFY_DIFF:
            self._active_packets.pop(packet.packet_id, None)
            return ReClearResult(
                outcome=ReClearOutcome.BLOCKED,
                packet_id=packet.packet_id,
                trace_id=trace_id,
                reviewer_id=human_input.reviewer_id,
                reason="MODIFY_DIFF is blocked — direct diff application bypasses L5 re-clearance. "
                "Route proposed changes back to L2 for re-execution.",
            )

        if human_input.decision == HumanDecision.DENY:
            self._active_packets.pop(packet.packet_id, None)
            return ReClearResult(
                outcome=ReClearOutcome.BLOCKED,
                packet_id=packet.packet_id,
                trace_id=trace_id,
                reviewer_id=human_input.reviewer_id,
                reason=f"Human reviewer denied clearance: {human_input.justification}",
            )

        if not human_input.reviewer_id or not human_input.reviewer_id.strip():
            return ReClearResult(
                outcome=ReClearOutcome.BLOCKED,
                packet_id=packet.packet_id,
                trace_id=trace_id,
                reviewer_id=human_input.reviewer_id,
                reason="H4 validation failed: reviewer_id is missing or empty",
            )

        if not human_input.justification or not human_input.justification.strip():
            return ReClearResult(
                outcome=ReClearOutcome.BLOCKED,
                packet_id=packet.packet_id,
                trace_id=trace_id,
                reviewer_id=human_input.reviewer_id,
                reason="H4 validation failed: justification is missing or empty — human input is untrusted data; justification is mandatory",
            )

        policy_passed = self._run_h5_policy(
            human_input=human_input,
            packet=packet,
        )
        if not policy_passed:
            return ReClearResult(
                outcome=ReClearOutcome.BLOCKED,
                packet_id=packet.packet_id,
                trace_id=trace_id,
                reviewer_id=human_input.reviewer_id,
                reason="H5 L5 policy re-clearance gate rejected the human-reviewed artifact",
            )

        del self._active_packets[packet.packet_id]

        has_commit = packet.sealed_artifact_summary.get("has_commit_payload", False)
        outcome = ReClearOutcome.CLEARED_COMMIT if has_commit else ReClearOutcome.CLEARED_ALLOW

        _emit_chooses_exit_disposition(trace_id, "ExitControlHITL", outcome.value)
        _emit_reclears_human_decision(trace_id, "ExitControlHITL", human_input.reviewer_id)
        _emit_transcripts_response(trace_id, "ExitControlHITL", outcome.value)
        logger.info(
            "[ExitControlHITL] H5 re-clearance passed: packet_id=%s outcome=%s reviewer=%s",
            packet.packet_id,
            outcome.value,
            human_input.reviewer_id,
        )

        return ReClearResult(
            outcome=outcome,
            packet_id=packet.packet_id,
            trace_id=trace_id,
            reviewer_id=human_input.reviewer_id,
            reason=f"H5 re-clearance passed. Reviewer: {human_input.reviewer_id}. Justification: {human_input.justification}",
            re_cleared_artifact=dict(packet.sealed_artifact_summary),
        )

    def _run_h5_policy(
        self,
        human_input: HumanReviewInput,
        packet: BoundedPacket,
    ) -> bool:
        """H5 re-clearance — run L5 policy validator on the human-reviewed artifact.

        If no external validator is injected, default re-clearance passes when:
        - decision is APPROVE
        - reviewer_id and justification are non-empty (already checked in validate_and_reclear)
        """
        if self._policy_validator is not None:
            return bool(
                self._policy_validator(
                    dict(packet.sealed_artifact_summary),
                    human_input.reviewer_id,
                )
            )
        return human_input.decision == HumanDecision.APPROVE
