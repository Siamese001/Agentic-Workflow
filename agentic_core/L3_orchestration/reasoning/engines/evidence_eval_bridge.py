"""Evidence evaluation bridge — read-only, sealed evidence-quality metrics.

Converts EvidenceShaper::EvidenceBundle into:
  1. EvidenceMetrics  — frozen dataclass of quality signals
  2. ExitControlGate-compatible artifact dict  (X1D grounded_replayable)
  3. L6 telemetry via lifecycle trace contract (_emit_captures_evaluation_metric)

No durable writes.  No UWG bypass.  Retrieval remains read-only.

Public API:
    build_exit_artifact(bundle, ...) -> dict[str, Any]
    emit_bundle_telemetry(bundle, request_id, contract=None) -> EvidenceMetrics
    run_live_exit_gate(artifact, policy_hash, ...) -> ExitGateResult
    publish_to_bus_t(metrics, trace_id, request_id) -> bool
    authorize_and_execute_with_evidence(bundle, ctx, ...) -> tuple[output, ctx, ExitGateResult]
    WeakSupportDisposition: PROCEED | REFINE | ABSTAIN | ESCALATE
    classify_evidence_support(metrics) -> WeakSupportDisposition
    evaluate_and_emit(bundle, execution_context, tool_name) -> tuple[ExitGateResult, WeakSupportDisposition]
"""

from __future__ import annotations

import enum
import hashlib
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import EvidenceBundle
    from agentic_core.L3_orchestration.types.c0_evidence_contract_types import C0EvidenceContract

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_evaluation_metric,
    _emit_invokes_evaluation,
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "evidence_eval_bridge")
emit_determinism_digest("p0", "evidence_eval_bridge")

# Mirror the C0 abstain threshold without importing private names
_ABSTAIN_COVERAGE_THRESHOLD: float = 0.30
# Coverage threshold below which execution should refine (marginal quality band)
_REFINE_COVERAGE_THRESHOLD: float = 0.60
# Minimum citation completeness required for X1D grounded_replayable=True
_GROUNDED_CITATION_THRESHOLD: float = 0.50


# ---------------------------------------------------------------------------
# EvidenceMetrics — sealed output contract
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceMetrics:
    """Sealed evidence-quality metrics — exit evaluation and L6 telemetry.

    Frozen to prevent downstream mutation.  Use as_dict() for serialisation.
    """

    citation_completeness: float  # fraction of top-5 with provenance_confidence >= 0.8
    support_coverage: float  # mean combined_score across ranked_chunks
    contradiction_present: bool  # any contradiction_flags in the bundle
    provenance_completeness: float  # mean provenance_confidence across all citation anchors
    exact_match_ratio: float  # fraction of top-k chunks that won via sparse/exact leg
    dedup_savings: float  # fraction of near-duplicates removed by shaping
    grounded_replayable: bool  # coverage >= threshold AND citation completeness adequate
    retrieval_id: str = ""
    collection: str = ""
    query_hash: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "citation_completeness": self.citation_completeness,
            "support_coverage": self.support_coverage,
            "contradiction_present": self.contradiction_present,
            "provenance_completeness": self.provenance_completeness,
            "exact_match_ratio": self.exact_match_ratio,
            "dedup_savings": self.dedup_savings,
            "grounded_replayable": self.grounded_replayable,
            "retrieval_id": self.retrieval_id,
            "collection": self.collection,
            "query_hash": self.query_hash,
        }


# ---------------------------------------------------------------------------
# Internal metric computation
# ---------------------------------------------------------------------------


def _compute_metrics(
    bundle: "EvidenceBundle",
    retrieval_id: str = "",
    query_hash: str = "",
) -> EvidenceMetrics:
    """Derive sealed evidence metrics from a shaped bundle (pure function)."""
    chunks = bundle.ranked_chunks
    anchors = bundle.citation_anchors

    # Citation completeness over top-5
    top5_ids = [c.chunk_id for c in chunks[:5]]
    complete_count = sum(
        1 for cid in top5_ids if cid in anchors and anchors[cid].provenance_confidence >= 0.8
    )
    citation_completeness = complete_count / max(len(top5_ids), 1)

    # Support coverage — mean combined_score
    support_coverage = sum(c.combined_score for c in chunks) / len(chunks) if chunks else 0.0

    # Provenance completeness — mean across all anchors
    prov_vals = [a.provenance_confidence for a in anchors.values()]
    provenance_completeness = sum(prov_vals) / len(prov_vals) if prov_vals else 0.0

    # Exact-match ratio — chunks that won via sparse/exact leg
    exact_ids = set(bundle.exact_match_winners)
    exact_match_ratio = sum(1 for c in chunks if c.chunk_id in exact_ids) / len(chunks) if chunks else 0.0

    # Dedup savings from shaping_stats
    before = bundle.shaping_stats.get("input_count", 0)
    after = bundle.shaping_stats.get("after_dedup", 0)
    dedup_savings = (before - after) / before if before > 0 else 0.0

    # X1D grounded_replayable: coverage must meet abstain threshold AND
    # at least half of top-5 results must have complete citation anchors
    grounded_replayable = (
        support_coverage >= _ABSTAIN_COVERAGE_THRESHOLD
        and citation_completeness >= _GROUNDED_CITATION_THRESHOLD
    )

    return EvidenceMetrics(
        citation_completeness=round(citation_completeness, 4),
        support_coverage=round(support_coverage, 4),
        contradiction_present=bool(bundle.contradiction_flags),
        provenance_completeness=round(provenance_completeness, 4),
        exact_match_ratio=round(exact_match_ratio, 4),
        dedup_savings=round(dedup_savings, 4),
        grounded_replayable=grounded_replayable,
        retrieval_id=retrieval_id,
        collection=bundle.collection,
        query_hash=query_hash,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_exit_artifact(
    bundle: "EvidenceBundle",
    rules_compliant: bool = True,
    answer_fit: bool = True,
    safety_clear: bool = True,
    has_commit_payload: bool = False,
    confidence_override: float | None = None,
) -> dict[str, Any]:
    """Build an artifact dict compatible with ExitControlGate.evaluate().

    X1D ``grounded_replayable`` is derived from the bundle quality metrics.
    ``confidence_score`` defaults to the mean combined_score of ranked_chunks.

    The extra key ``_evidence_metrics`` is ignored by ExitControlGate but is
    available to any caller that needs the full metrics alongside the gate result.

    Args:
        bundle:             EvidenceShaper::EvidenceBundle from shape_search().
        rules_compliant:    X1A — policy rules pass (caller asserts this).
        answer_fit:         X1B — output answers the question (caller asserts).
        safety_clear:       X1C — no safety violations (caller asserts).
        has_commit_payload: True only when routing an artifact to UWG.
        confidence_override: Override confidence_score if caller has finer signal.

    Returns:
        Artifact dict for ExitControlGate.evaluate().
    """
    metrics = _compute_metrics(bundle)
    confidence = confidence_override if confidence_override is not None else metrics.support_coverage

    escalation_reason: str | None = None
    if bundle.contradiction_flags:
        escalation_reason = f"evidence_contradictions_detected:{len(bundle.contradiction_flags)}"

    return {
        "rules_compliant": rules_compliant,
        "answer_fit": answer_fit,
        "safety_clear": safety_clear,
        "grounded_replayable": metrics.grounded_replayable,
        "confidence_score": float(confidence),
        "has_commit_payload": has_commit_payload,
        "escalation_reason": escalation_reason,
        "_evidence_metrics": metrics.as_dict(),  # pass-through; ignored by gate
    }


def publish_to_bus_t(
    metrics: EvidenceMetrics,
    trace_id: str,
    request_id: str,
) -> bool:
    """Publish sealed evidence metrics to BUS T for future-run L6 shadow grading.

    BUS T is the 10C-REQ-134 async telemetry channel for future-run grading
    and RCA.  No durable writes, no live behavior mutation.

    Args:
        metrics:    EvidenceMetrics from emit_bundle_telemetry().
        trace_id:   Active execution trace ID for correlation.
        request_id: Upstream request ID.

    Returns:
        True if published; False if BUS T was full (dropped — non-fatal).
    """
    try:
        from agentic_core.L2_execution.audit.telemetry_bus import BusType, get_telemetry_bus  # noqa: PLC0415

        return get_telemetry_bus().publish(
            bus_type=BusType.TELEMETRY,
            signal_type="evidence_quality_metrics",
            payload={"request_id": request_id, **metrics.as_dict()},
            trace_id=trace_id,
        )
    except (ImportError, RuntimeError, ValueError):
        return False


def emit_bundle_telemetry(
    bundle: "EvidenceBundle",
    request_id: str,
    contract: "C0EvidenceContract | None" = None,
) -> EvidenceMetrics:
    """Emit sealed evidence metrics as L6 telemetry and return EvidenceMetrics.

    Read-only — no durable writes, no UWG bypass.
    Emits three metric events via lifecycle trace contract for L6 observability.

    Args:
        bundle:     EvidenceShaper::EvidenceBundle from shape_search().
        request_id: Upstream request identifier (for correlation).
        contract:   Optional C0EvidenceContract to anchor retrieval_id.

    Returns:
        EvidenceMetrics — frozen dataclass with all quality signals.
    """
    trace_id = str(uuid.uuid4())
    query_hash = hashlib.sha256(bundle.query.encode()).hexdigest()[:16]
    retrieval_id = contract.retrieval_id if contract is not None else request_id

    _emit_invokes_evaluation(trace_id, "evidence_eval_bridge", "evidence_quality_eval")

    metrics = _compute_metrics(bundle, retrieval_id=retrieval_id, query_hash=query_hash)

    _emit_captures_evaluation_metric(
        trace_id,
        "evidence_eval_bridge",
        "citation_completeness",
    )
    _emit_captures_evaluation_metric(
        trace_id,
        "evidence_eval_bridge",
        "support_coverage",
    )
    _emit_captures_evaluation_metric(
        trace_id,
        "evidence_eval_bridge",
        "provenance_completeness",
    )

    publish_to_bus_t(metrics, trace_id=trace_id, request_id=request_id)

    return metrics


# ---------------------------------------------------------------------------
# Weak-support governance — explicit disposition for all upgraded lanes
# ---------------------------------------------------------------------------


class WeakSupportDisposition(enum.Enum):
    """Explicit pre-execution grounding disposition for evidence-governed lanes.

    Produced by classify_evidence_support() and returned by evaluate_and_emit().
    All upgraded execution lanes receive this before _invoke_authorize_and_execute().

    PROCEED   — evidence meets quality bar; grounded execution may continue.
    REFINE    — coverage or citation quality is marginal; caller may retry retrieval.
    ABSTAIN   — coverage below threshold or bundle not grounded; must not proceed
                silently as if grounded.
    ESCALATE  — contradiction detected; human or safety-plane review needed.
    """

    PROCEED = "proceed"
    REFINE = "refine"
    ABSTAIN = "abstain"
    ESCALATE = "escalate"


def classify_evidence_support(metrics: EvidenceMetrics) -> WeakSupportDisposition:
    """Derive an explicit weak-support disposition from sealed evidence metrics.

    Rules (evaluated top-to-bottom, first match wins):
        1. ESCALATE  — contradiction_present is True
        2. ABSTAIN   — not grounded_replayable OR coverage < 0.30
        3. REFINE    — coverage < 0.60 OR citation_completeness < 0.50
        4. PROCEED   — all quality bars met

    Returns:
        WeakSupportDisposition — explicit, non-null, never silently downgraded.
    """
    if metrics.contradiction_present:
        return WeakSupportDisposition.ESCALATE
    if not metrics.grounded_replayable or metrics.support_coverage < _ABSTAIN_COVERAGE_THRESHOLD:
        return WeakSupportDisposition.ABSTAIN
    if (
        metrics.support_coverage < _REFINE_COVERAGE_THRESHOLD
        or metrics.citation_completeness < _GROUNDED_CITATION_THRESHOLD
    ):
        return WeakSupportDisposition.REFINE
    return WeakSupportDisposition.PROCEED


def evaluate_and_emit(
    bundle: "EvidenceBundle",
    execution_context: Any,
    tool_name: str = "",
) -> "tuple[Any, WeakSupportDisposition]":
    """Common cross-lane adapter: exit gate + BUS T + explicit weak-support disposition.

    Single shared function used by all evidence-upgraded execution lanes
    (ExecutionGateway, ToolIntentExecutor, ActionNode).  Replaces per-lane
    duplication of build_exit_artifact + run_live_exit_gate + emit_bundle_telemetry.

    Non-blocking sidecar: disposition is returned for caller awareness but does
    NOT interrupt execution.  No durable writes.  No UWG bypass.

    Args:
        bundle:            EvidenceBundle from shape_search().
        execution_context: L2 ExecutionContext (used for policy_hash and run_id).
        tool_name:         Tool name for observability (optional).

    Returns:
        (gate_result, disposition) —
            gate_result:  ExitGateResult from run_live_exit_gate().
            disposition:  WeakSupportDisposition — explicit grounding quality verdict.
    """
    artifact = build_exit_artifact(bundle)
    gate_result = run_live_exit_gate(
        artifact,
        policy_hash=getattr(execution_context, "policy_hash", None),
        log_to_outcome_logger=True,
    )
    metrics = emit_bundle_telemetry(
        bundle,
        request_id=getattr(execution_context, "run_id", ""),
    )
    disposition = classify_evidence_support(metrics)

    # L6 shadow eval ingestion seam — future-run only, non-blocking.
    # All three artifacts (gate_result, metrics, disposition) are captured here
    # simultaneously: the real BUS T + exit + sealed-artifact join point.
    try:
        from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (  # noqa: PLC0415
            ingest_eval_packet,
        )

        ingest_eval_packet(
            run_id=getattr(execution_context, "run_id", ""),
            lane_id=tool_name,
            gate_result=gate_result,
            metrics=metrics,
            weak_support_disposition=disposition,
        )
    except (ImportError, RuntimeError, ValueError):
        pass  # guardian: allow-silent-swallow -- L6 ingestion must not block live execution

    return gate_result, disposition


# ---------------------------------------------------------------------------
# Live exit gate — real runtime integration (Phase 2)
# ---------------------------------------------------------------------------


def run_live_exit_gate(
    artifact: dict[str, Any],
    policy_hash: str | None = None,
    log_to_outcome_logger: bool = True,
) -> Any:
    """Run ExitControlGate on an evidence-derived artifact (not benchmark-only).

    This is the real current-run exit gate call wired to live evidence metrics.
    The artifact MUST have been produced by build_exit_artifact() so all four
    X1A–X1D keys are present.

    Logs the ExitGateResult to OutcomeLogger for downstream L6 consumers
    (outcome_logger → evaluate_and_attach → EvaluationRecord).

    Args:
        artifact:              Dict from build_exit_artifact().
        policy_hash:           Policy hash from the execution context.
        log_to_outcome_logger: When True, log ExitGateResult to OutcomeLogger.

    Returns:
        ExitGateResult — typed, explicit, non-null disposition.
    """
    from agentic_core.L5_safety.enforcement.exit_control_gate import ExitControlGate  # noqa: PLC0415

    gate = ExitControlGate(policy_hash=policy_hash)
    gate_result = gate.evaluate(artifact)

    if log_to_outcome_logger:
        try:
            from agentic_core.L6_observability.enforcement.outcome_logger import OutcomeLogger  # noqa: PLC0415

            OutcomeLogger().append_gate_result(gate_result)
        except (RuntimeError, ValueError, TypeError):
            pass  # guardian: allow-silent-swallow -- OutcomeLogger failure must not block gate result

    return gate_result


# ---------------------------------------------------------------------------
# Evidence-aware execution wrapper — real control-plane seam (Phase 2 + 3)
# ---------------------------------------------------------------------------


def authorize_and_execute_with_evidence(
    bundle: "EvidenceBundle",
    execution_context: Any,
    target_callable: Any,
    capability_token: str,
    payload: Any,
    *,
    target_name: str = "",
    human_approved: bool = False,
    safety_plane_available: bool = True,
    uwg_callable: Any | None = None,
    rules_compliant: bool = True,
    answer_fit: bool = True,
    safety_clear: bool = True,
    request_id: str = "",
) -> tuple[Any, Any, Any]:
    """Evidence-aware wrapper around authorize_and_execute().

    Phase 2 — live exit: builds an evidence-derived artifact from the bundle
      and evaluates it via ExitControlGate after the chokepoint completes.
    Phase 3 — L6 telemetry: emit_bundle_telemetry() publishes sealed metrics
      to BUS T (10C-REQ-134) for future-run shadow grading and RCA.

    The execution chokepoint (L2) is unchanged.  Evidence evaluation is a
    post-execution sidecar: it cannot block the execution result, but the
    gate decision is always logged to OutcomeLogger.

    Returns:
        (output, bound_ctx, gate_result) — all three populated on success.
        Exceptions from the chokepoint propagate unchanged.
    """
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (  # noqa: PLC0415
        authorize_and_execute,
    )

    artifact = build_exit_artifact(
        bundle,
        rules_compliant=rules_compliant,
        answer_fit=answer_fit,
        safety_clear=safety_clear,
    )

    output, bound_ctx = authorize_and_execute(
        execution_context,
        target_callable,
        capability_token,
        payload,
        target_name=target_name,
        human_approved=human_approved,
        safety_plane_available=safety_plane_available,
        uwg_callable=uwg_callable,
    )

    gate_result = run_live_exit_gate(
        artifact,
        policy_hash=getattr(bound_ctx, "policy_hash", None),
        log_to_outcome_logger=True,
    )

    emit_bundle_telemetry(
        bundle,
        request_id=request_id or getattr(bound_ctx, "execution_request_id", ""),
    )

    return output, bound_ctx, gate_result
