"""Exit Control Gate — X1A through X1D four-dimensional evaluation (HITL-001).

This module is the single mandatory post-execution gate that every sealed L2
artifact MUST pass before any response is sent, any commit is dispatched to
UWG, or any HITL escalation is triggered.

Evaluation dimensions (docs/reference/05_Live_Runtime_Exit_Control.md):
    X1A  rules_compliant      — no policy-rule violation
    X1B  answer_fit           — output answers the question asked
    X1C  safety_clear         — no secrets, PII, unsafe content, injection residue
    X1D  grounded_replayable  — grounded in evidence; deterministically reproducible

Explicit dispositions (ExitDisposition enum, HITL-003 — L5_safety/types):
    ALLOW_RESPONSE    — all four dimensions pass, no commit payload
    DENY_RETURN       — any safety or policy dimension fails
    ESCALATE_TO_HITL  — confidence below threshold or explicit escalation_reason
    COMMIT_TO_UWG     — all dimensions pass AND has_commit_payload=True

Layer authority: L5 (cross-cutting policy plane)
Write authority: NONE — this gate is evaluation-only; commits are routed OUT to UWG
No silent fallback. No catch-all. Every code path produces an explicit ExitDisposition.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from typing import Any

from agentic_core.L5_safety.types.exit_disposition_types import (
    ExitDisposition,
    ExitEvaluationDimensions,
    ExitGateResult,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_eval,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_transcripts_response,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "exit_control_gate")
emit_determinism_digest("p0", "exit_control_gate")
_emit_reads_policy_state("p1", "exit_control_gate", "L5")
_emit_verifies_policy("p1", "exit_control_gate", "policy_check")
_emit_verifies_boundary("p1", "exit_control_gate", "boundary_check")
_emit_validated_by_safety_plane("p1", "exit_control_gate", "safety_validation")
_emit_hard_fails_untranscripted("p1", "exit_control_gate")
_emit_gated_by_confidence("p1", "exit_control_gate", "confidence_gate")
_emit_invokes_eval("p1", "exit_control_gate", "exit_eval")

logger = logging.getLogger(__name__)

_CONFIDENCE_ESCALATION_THRESHOLD = 0.70


class ExitControlGate:
    """Four-dimensional exit gate — evaluate sealed L2 artifacts before response/commit.

    Usage::

        gate = ExitControlGate(policy_hash="sha256:...", confidence_threshold=0.70)
        result = gate.evaluate(artifact)   # ExitGateResult — never raises on evaluation
        # inspect result.disposition → route accordingly

    The gate NEVER silently swallows.  Every path produces one of the four
    explicit ExitDisposition values.  Callers MUST inspect the disposition
    and route to the correct downstream (response path, UWG, HITL, deny).

    Layer authority: L5 — evaluation only; no durable writes.
    """

    def __init__(
        self,
        policy_hash: str | None = None,
        compliance_hash: str | None = None,
        confidence_threshold: float = _CONFIDENCE_ESCALATION_THRESHOLD,
    ) -> None:
        self._policy_hash = policy_hash
        self._compliance_hash = compliance_hash
        self._confidence_threshold = confidence_threshold

    def evaluate(self, artifact: dict[str, Any]) -> ExitGateResult:
        """Run X1A–X1D evaluation on a sealed execution artifact.

        Args:
            artifact: Sealed execution artifact from L2.  Expected keys:
                - rules_compliant (bool)
                - answer_fit (bool)
                - safety_clear (bool)
                - grounded_replayable (bool)
                - confidence_score (float 0.0–1.0)
                - has_commit_payload (bool, optional)
                - escalation_reason (str | None, optional)

        Returns:
            ExitGateResult with an explicit non-null ExitDisposition.
            Never returns None. Never raises (evaluation errors → DENY_RETURN).
        """
        trace_id = str(uuid.uuid4())

        _emit_snapshots_state(trace_id, "ExitControlGate.evaluate", "exit_state")
        _emit_applies_guardrail(trace_id, "ExitControlGate.evaluate", "X1A_X1D_exit")
        _emit_records_execution_trace(trace_id, "L5_POLICY", "ExitControlGate.evaluate")
        _seg_hash = hashlib.sha256(f"{trace_id}:ExitControlGate".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(trace_id, _seg_hash, _seg_hash, 0)

        try:
            dims = self._extract_dimensions(artifact)
        except (KeyError, TypeError, ValueError) as exc:
            logger.error("[ExitControlGate] Dimension extraction failed: %s", exc)
            return ExitGateResult(
                disposition=ExitDisposition.DENY_RETURN,
                trace_id=trace_id,
                dimensions=ExitEvaluationDimensions(
                    rules_compliant=False,
                    answer_fit=False,
                    safety_clear=False,
                    grounded_replayable=False,
                    confidence_score=0.0,
                ),
                reason=f"Artifact malformed — dimension extraction failed: {exc}",
                policy_hash=self._policy_hash,
                compliance_hash=self._compliance_hash,
            )

        disposition, reason = self._decide(dims)

        _emit_transcripts_response(trace_id, "ExitControlGate", disposition.value)
        logger.info(
            "[ExitControlGate] trace_id=%s disposition=%s reason=%s",
            trace_id,
            disposition.value,
            reason,
        )

        return ExitGateResult(
            disposition=disposition,
            trace_id=trace_id,
            dimensions=dims,
            reason=reason,
            policy_hash=self._policy_hash,
            compliance_hash=self._compliance_hash,
        )

    def _extract_dimensions(self, artifact: dict[str, Any]) -> ExitEvaluationDimensions:
        """Extract and type-validate the four evaluation dimensions from the artifact."""
        return ExitEvaluationDimensions(
            rules_compliant=bool(artifact["rules_compliant"]),
            answer_fit=bool(artifact["answer_fit"]),
            safety_clear=bool(artifact["safety_clear"]),
            grounded_replayable=bool(artifact["grounded_replayable"]),
            confidence_score=float(artifact["confidence_score"]),
            has_commit_payload=bool(artifact.get("has_commit_payload", False)),
            escalation_reason=artifact.get("escalation_reason"),
        )

    def _decide(self, dims: ExitEvaluationDimensions) -> tuple[ExitDisposition, str]:
        """Derive the explicit ExitDisposition from the four dimensions.

        Decision tree (evaluated in priority order):
        1. DENY  — X1C safety_clear is False (hard fail — no override)
        2. DENY  — X1A rules_compliant is False
        3. ESCALATE — explicit escalation_reason present
        4. ESCALATE — confidence_score below threshold
        5. COMMIT   — all four pass AND has_commit_payload=True
        6. ALLOW    — all four pass, no commit payload

        No branch produces None. No catch-all silent path.
        """
        if not dims.safety_clear:
            return (
                ExitDisposition.DENY_RETURN,
                "X1C failed: safety_clear=False (secrets, PII, unsafe content, or injection residue detected)",
            )

        if not dims.rules_compliant:
            return (
                ExitDisposition.DENY_RETURN,
                "X1A failed: rules_compliant=False (policy-rule violation detected)",
            )

        if dims.escalation_reason:
            return (
                ExitDisposition.ESCALATE_TO_HITL,
                f"Explicit escalation_reason: {dims.escalation_reason}",
            )

        if dims.confidence_score < self._confidence_threshold:
            return (
                ExitDisposition.ESCALATE_TO_HITL,
                f"Confidence {dims.confidence_score:.3f} below threshold {self._confidence_threshold:.3f}",
            )

        if not dims.answer_fit:
            return (
                ExitDisposition.DENY_RETURN,
                "X1B failed: answer_fit=False (output does not answer the question asked)",
            )

        if not dims.grounded_replayable:
            return (
                ExitDisposition.DENY_RETURN,
                "X1D failed: grounded_replayable=False (output is not grounded or not reproducible)",
            )

        if dims.has_commit_payload:
            return (
                ExitDisposition.COMMIT_TO_UWG,
                "All four dimensions pass; has_commit_payload=True → route to UWG",
            )

        return (
            ExitDisposition.ALLOW_RESPONSE,
            "All four dimensions pass (X1A rules_compliant, X1B answer_fit, X1C safety_clear, X1D grounded_replayable)",
        )
