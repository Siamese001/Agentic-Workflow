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
import time
import uuid
from typing import Any, Union

from agentic_core.L2_execution.types.sealed_l2_artifact import (
    SealedL2Artifact,
    TerminalClassification,
)
from agentic_core.L5_safety.types.exit_disposition_types import (
    CurrentRunEvaluationResult,
    ExitDisposition,
    ExitEvaluationDimensions,
    ExitGateResult,
    IntegrityChecks,
    QualityChecks,
    RubricScores,
)
from agentic_core.L5_safety.types.exit_outcome_types import (
    AllowResponsePayload,
    CommitToUWGRequest,
    DenyReturnPayload,
    EscalateToHITLPacket,
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
_GROUNDED_THRESHOLD = 0.60
_RULES_COMPLIANCE_THRESHOLD = 0.50
_REPLAY_COMPLETENESS_THRESHOLD = 0.80


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

    # ------------------------------------------------------------------
    # Sealed-artifact evaluation path (evaluate_sealed + shape_outcome)
    # ------------------------------------------------------------------

    def evaluate_sealed(self, artifact: SealedL2Artifact) -> CurrentRunEvaluationResult:
        """Run X1A–X1D evaluation on a typed SealedL2Artifact.

        Primary entry point for post-L2 current-run evaluation.
        Never raises — evaluation errors produce DENY_RETURN (fail closed).
        Shadow-eval packetization MUST NOT be called from this method.
        """
        eval_id = str(uuid.uuid4())
        trace_id = artifact.trace_id or str(uuid.uuid4())

        _emit_snapshots_state(trace_id, "ExitControlGate.evaluate_sealed", "exit_state")
        _emit_applies_guardrail(trace_id, "ExitControlGate.evaluate_sealed", "X1A_X1D_exit")
        _emit_records_execution_trace(trace_id, "L5_POLICY", "ExitControlGate.evaluate_sealed")

        try:
            rubric = self._eval_rubrics(artifact)
            quality = self._eval_quality(artifact)
            integrity = self._eval_integrity(artifact)
            confidence_score = self._compute_confidence_from_checks(rubric, quality, integrity)
            disposition, reason = self._decide_from_evaluation(
                rubric, quality, integrity, confidence_score, artifact
            )
        except (AttributeError, TypeError, ValueError) as exc:
            logger.error("[ExitControlGate.evaluate_sealed] Evaluation failed: %s", exc)
            rubric = RubricScores()
            quality = QualityChecks()
            integrity = IntegrityChecks()
            confidence_score = 0.0
            disposition = ExitDisposition.DENY_RETURN
            reason = f"Artifact evaluation failed — fail closed: {exc}"

        _emit_transcripts_response(trace_id, "ExitControlGate", disposition.value)
        logger.info(
            "[ExitControlGate.evaluate_sealed] eval_id=%s trace_id=%s disposition=%s",
            eval_id,
            trace_id,
            disposition.value,
        )

        # Shadow eval_spine observer — gated by EVAL_SPINE_SHADOW=1. Never
        # raises, never mutates decision. See Author-Gate 2026-04-23
        # (confidence=0.86, principle=observer-first-enforcer-later) and
        # docs/archive/windsurf/legacy-tree/plans/exit-eval-spine-shadow-wiring-a9c124.md.
        try:
            from agentic_core.L5_safety.eval_spine.shadow_observer import (
                emit_shadow_exit_decision,
            )

            emit_shadow_exit_decision(
                artifact,
                policy_snapshot=self._policy_hash or "shadow-unknown",
            )
        except ImportError:  # guardian: allow-silent-swallow -- shadow is opt-in; missing subpackage must not break the live exit path (pass-through to enforcement or legacy disposition)
            pass

        # Active §5 enforcement — gated by EVAL_SPINE_ENFORCE=1. Upgrade-only
        # semantics: eval_spine can make disposition stricter, never looser.
        # See plan docs/archive/windsurf/legacy-tree/plans/exit-eval-spine-deferred-closeout-d5e8b3.md §Q4.
        try:
            from agentic_core.L5_safety.eval_spine.enforcement_bridge import (
                is_enforce_enabled,
                merge_disposition,
            )

            if is_enforce_enabled():
                from agentic_core.L5_safety.eval_spine.budget_envelope import (
                    BudgetEnvelope,
                )
                from agentic_core.L5_safety.eval_spine.exit_eval import (
                    ExitEvalPolicy,
                    SealedArtifact,
                    evaluate_exit,
                )
                from agentic_core.L5_safety.eval_spine.shadow_observer import (
                    sealed_l2_to_eval_spine,
                )

                sealed = sealed_l2_to_eval_spine(artifact)
                env = BudgetEnvelope(origin="enforce_default")
                pol = ExitEvalPolicy(policy_snapshot=self._policy_hash or "enforce-unknown")
                result = evaluate_exit(sealed, env, pol)
                upgraded, upgrade_reason = merge_disposition(disposition, result.exit_decision)
                if upgrade_reason is not None:
                    logger.warning(
                        "[ExitControlGate.evaluate_sealed] eval_spine upgraded disposition %s -> %s: %s",
                        disposition.value,
                        upgraded.value,
                        upgrade_reason,
                    )
                    disposition = upgraded
                    reason = f"{reason} | {upgrade_reason}"
        except ImportError:  # guardian: allow-silent-swallow -- enforcement is opt-in; missing subpackage must not break the live exit path (falls through to legacy disposition)
            pass
        except (
            AttributeError,
            TypeError,
            ValueError,
        ) as enforce_exc:  # guardian: allow-log-and-swallow -- enforcement merge bugs must never fail the live exit path; logs warning and falls back to legacy disposition
            logger.warning(
                "[ExitControlGate.evaluate_sealed] eval_spine enforce failed: %s",
                enforce_exc,
            )

        return CurrentRunEvaluationResult(
            eval_id=eval_id,
            artifact_id=artifact.artifact_id,
            trace_id=trace_id,
            rubric_scores=rubric,
            quality_checks=quality,
            integrity_checks=integrity,
            confidence_score=confidence_score,
            disposition=disposition,
            disposition_reason=reason,
            policy_hash=self._policy_hash,
            compliance_hash=self._compliance_hash,
            evaluated_at=time.monotonic(),
        )

    def shape_outcome(
        self,
        result: CurrentRunEvaluationResult,
        artifact: SealedL2Artifact,
    ) -> Union[
        AllowResponsePayload,
        DenyReturnPayload,
        EscalateToHITLPacket,
        CommitToUWGRequest,
    ]:
        """Map a CurrentRunEvaluationResult to its minimal live outcome payload.

        Dispatches to one of four path-specific outcome stubs.  No silent
        fallback — raises ValueError for any unhandled ExitDisposition value
        (guarded by the enum; unreachable in practice).
        Shadow-eval code MUST NOT be called from this method.
        """
        if result.disposition is ExitDisposition.ALLOW_RESPONSE:
            return AllowResponsePayload(
                eval_id=result.eval_id,
                trace_id=result.trace_id,
                artifact_id=result.artifact_id,
                confidence_score=result.confidence_score,
                policy_hash=result.policy_hash,
                compliance_hash=result.compliance_hash,
            )

        if result.disposition is ExitDisposition.DENY_RETURN:
            return DenyReturnPayload(
                eval_id=result.eval_id,
                trace_id=result.trace_id,
                artifact_id=result.artifact_id,
                reason=result.disposition_reason,
                policy_hash=result.policy_hash,
            )

        if result.disposition is ExitDisposition.ESCALATE_TO_HITL:
            return EscalateToHITLPacket(
                eval_id=result.eval_id,
                trace_id=result.trace_id,
                artifact_id=result.artifact_id,
                reason=result.disposition_reason,
                confidence_score=result.confidence_score,
                bounded_context={
                    "artifact_id": result.artifact_id,
                    "rubric_scores": {
                        "rules_compliance_score": result.rubric_scores.rules_compliance_score,
                        "schema_completion_score": result.rubric_scores.schema_completion_score,
                    },
                    "integrity_checks": {
                        "safety_clear": result.integrity_checks.safety_clear,
                        "policy_pass": result.integrity_checks.policy_pass,
                        "replay_env_complete": result.integrity_checks.replay_env_complete,
                    },
                    "terminal_classification": artifact.terminal_classification.value,
                },
                policy_hash=result.policy_hash,
            )

        if result.disposition is ExitDisposition.COMMIT_TO_UWG:
            return CommitToUWGRequest(
                eval_id=result.eval_id,
                trace_id=result.trace_id,
                artifact_id=result.artifact_id,
                state_diff=dict(artifact.state_diff),
                replay_key=artifact.replay_metadata.replay_key,
                policy_hash=result.policy_hash,
                compliance_hash=result.compliance_hash,
            )

        raise ValueError(  # pragma: no cover — ExitDisposition is exhaustive
            f"Unhandled ExitDisposition: {result.disposition!r}"
        )

    # ------------------------------------------------------------------
    # Private helpers for evaluate_sealed
    # ------------------------------------------------------------------

    def _eval_rubrics(self, artifact: SealedL2Artifact) -> RubricScores:
        """Derive X1A rubric scores from validation counters and terminal state."""
        v = artifact.validation_counters
        total_policy = v.policy_checks_passed + v.policy_checks_failed
        rules_score = (v.policy_checks_passed / total_policy) if total_policy > 0 else 0.0
        total_schema = v.schema_checks_passed + v.schema_checks_failed
        schema_score = (v.schema_checks_passed / total_schema) if total_schema > 0 else 0.0
        format_fit = 1.0 if artifact.terminal_classification is TerminalClassification.SUCCESS else 0.0
        return RubricScores(
            rules_compliance_score=rules_score,
            policy_adherence_score=rules_score,
            format_fit_score=format_fit,
            schema_completion_score=schema_score,
        )

    def _eval_quality(self, artifact: SealedL2Artifact) -> QualityChecks:
        """Derive X1B + X1D quality checks from evidence bundle and terminal state."""
        eb = artifact.evidence_bundle
        return QualityChecks(
            answer_fit=(artifact.terminal_classification is TerminalClassification.SUCCESS),
            groundedness_score=float(eb.get("groundedness_score", 0.0)),
            support_coverage=float(eb.get("support_coverage", 0.0)),
            relevance_score=float(eb.get("relevance_score", 0.0)),
            abstain_correct=bool(eb.get("abstain_correct", True)),
            escalation_correct=bool(eb.get("escalation_correct", True)),
        )

    def _eval_integrity(self, artifact: SealedL2Artifact) -> IntegrityChecks:
        """Derive X1C integrity checks from validation counters and replay metadata."""
        v = artifact.validation_counters
        rm = artifact.replay_metadata
        eb = artifact.evidence_bundle
        return IntegrityChecks(
            safety_clear=bool(eb.get("safety_clear", False)),
            policy_pass=v.policy_checks_failed == 0,
            mutation_authorized=v.mutation_auth_checks_failed == 0,
            env_integrity=rm.isolation_verified,
            replay_env_complete=(rm.replay_completeness >= _REPLAY_COMPLETENESS_THRESHOLD),
        )

    def _compute_confidence_from_checks(
        self,
        rubric: RubricScores,
        quality: QualityChecks,
        integrity: IntegrityChecks,
    ) -> float:
        """Weighted confidence score from evaluation sub-results.

        Weights: rules 0.25, schema 0.10, groundedness 0.25, support 0.15,
                 relevance 0.15, safety binary 0.10.  Total = 1.00.
        """
        safety_weight = 1.0 if integrity.safety_clear else 0.0
        raw = (
            rubric.rules_compliance_score * 0.25
            + rubric.schema_completion_score * 0.10
            + quality.groundedness_score * 0.25
            + quality.support_coverage * 0.15
            + quality.relevance_score * 0.15
            + safety_weight * 0.10
        )
        return min(1.0, max(0.0, raw))

    def _decide_from_evaluation(
        self,
        rubric: RubricScores,
        quality: QualityChecks,
        integrity: IntegrityChecks,
        confidence_score: float,
        artifact: SealedL2Artifact,
    ) -> tuple[ExitDisposition, str]:
        """Priority-ordered disposition tree for typed evaluation results.

        Decision order (mirrors _decide priority contract):
        1. DENY  — X1C safety_clear=False (hard fail; no override)
        2. DENY  — unauthorized commit payload (has_commit_payload + not mutation_authorized)
        3. DENY  — X1A rules / policy check failed
        4. ESCALATE — explicit escalation_reason
        5. ESCALATE — confidence below threshold
        6. DENY  — X1B answer_fit=False
        7. DENY  — X1D grounded_replayable=False
        8. COMMIT — all pass + authorized commit payload
        9. ALLOW  — all pass, no commit payload

        No branch produces None.  No silent fallback.
        """
        if not integrity.safety_clear:
            return (
                ExitDisposition.DENY_RETURN,
                "X1C failed: safety_clear=False (secrets, PII, unsafe content, or injection residue detected)",
            )

        if artifact.has_commit_payload and not integrity.mutation_authorized:
            return (
                ExitDisposition.DENY_RETURN,
                "X1A failed: mutation_authorized=False (commit payload present but write not authorized)",
            )

        rules_compliant = (
            integrity.policy_pass and rubric.rules_compliance_score >= _RULES_COMPLIANCE_THRESHOLD
        )
        if not rules_compliant:
            return (
                ExitDisposition.DENY_RETURN,
                "X1A failed: rules_compliant=False (policy-rule violation detected)",
            )

        if artifact.escalation_reason:
            return (
                ExitDisposition.ESCALATE_TO_HITL,
                f"Explicit escalation_reason: {artifact.escalation_reason}",
            )

        if confidence_score < self._confidence_threshold:
            return (
                ExitDisposition.ESCALATE_TO_HITL,
                f"Confidence {confidence_score:.3f} below threshold {self._confidence_threshold:.3f}",
            )

        if not quality.answer_fit:
            return (
                ExitDisposition.DENY_RETURN,
                "X1B failed: answer_fit=False (output does not answer the question asked)",
            )

        grounded_replayable = (
            integrity.replay_env_complete and quality.groundedness_score >= _GROUNDED_THRESHOLD
        )
        if not grounded_replayable:
            return (
                ExitDisposition.DENY_RETURN,
                "X1D failed: grounded_replayable=False (output not grounded or not reproducible)",
            )

        if artifact.has_commit_payload:
            return (
                ExitDisposition.COMMIT_TO_UWG,
                "All four dimensions pass; has_commit_payload=True → route to UWG",
            )

        return (
            ExitDisposition.ALLOW_RESPONSE,
            "All four dimensions pass (X1A rules_compliant, X1B answer_fit, X1C safety_clear, X1D grounded_replayable)",
        )
