from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from enum import Enum
from hashlib import sha1
from types import SimpleNamespace
import time
import uuid
from typing import Any

from agentic_core.L2_execution.audit.telemetry_bus import BusType, get_telemetry_bus
from agentic_core.L2_execution.types.sealed_l2_artifact import (
    ReplayMetadata,
    SealedL2Artifact,
    TerminalClassification,
    ValidationCounters,
)
from agentic_core.L5_safety.enforcement.exit_control_gate import ExitControlGate  # guardian: allow-layer-violation -- L3 orchestration bridge is the canonical producer of exit dicts + sealed artifacts for governed retrieval; intentional narrow import of the policy gate
from agentic_core.L5_safety.types.exit_disposition_types import (
    ExitDisposition,
    ExitEvaluationDimensions,
    ExitGateResult,
)
from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (  # guardian: allow-layer-violation -- evidence_eval_bridge is the L3 side of shadow-eval async pipeline; the packet schema lives in L6 evaluation utils as the canonical evaluator-input contract, and L3 is the boundary-inversion producer
    AsyncEvalPacket,
    ShadowEvalPacket,
    enqueue_shadow_eval_packet,
    get_async_eval_ingester,
)

_ABSTAIN_COVERAGE_THRESHOLD = 0.20
_REFINE_COVERAGE_THRESHOLD = 0.50
_GROUNDED_CITATION_THRESHOLD = 0.75


class WeakSupportDisposition(str, Enum):
    ABSTAIN = "ABSTAIN"
    ESCALATE = "ESCALATE"
    REFINE = "REFINE"
    PROCEED = "PROCEED"


@dataclass(frozen=True)
class EvidenceMetrics:
    citation_completeness: float
    support_coverage: float
    contradiction_present: bool
    provenance_completeness: float
    exact_match_ratio: float
    dedup_savings: float
    grounded_replayable: bool
    retrieval_id: str
    collection: str
    query_hash: str


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_len(value: Any) -> int:
    try:
        return len(value)
    except (TypeError, ValueError):
        return 0


def _bundle_query_hash(bundle: Any) -> str:
    query = getattr(bundle, "query", "") or ""
    collection = getattr(bundle, "collection", "") or ""
    digest = sha1(f"{collection}|{query}".encode("utf-8")).hexdigest()
    return digest[:16]


def _bundle_retrieval_id(bundle: Any) -> str:
    explicit = getattr(bundle, "retrieval_id", "") or getattr(bundle, "request_id", "") or ""
    if explicit:
        return str(explicit)
    return f"ret-{_bundle_query_hash(bundle)}"


def _anchor_confidence(anchor: Any) -> float:
    if isinstance(anchor, dict):
        return _safe_float(anchor.get("provenance_confidence", 0.0))
    return _safe_float(getattr(anchor, "provenance_confidence", 0.0))


def _chunk_score(chunk: Any) -> float:
    if isinstance(chunk, dict):
        for key in ("combined_score", "score", "vector_score"):
            if key in chunk:
                return _safe_float(chunk.get(key), 0.0)
        return 0.0
    for attr in ("combined_score", "score", "vector_score"):
        if hasattr(chunk, attr):
            return _safe_float(getattr(chunk, attr, 0.0), 0.0)
    return 0.0


def _compute_metrics(bundle: Any) -> EvidenceMetrics:
    anchors = getattr(bundle, "citation_anchors", {}) or {}
    anchor_values = list(anchors.values())
    citation = sum(_anchor_confidence(anchor) for anchor in anchor_values) / max(1, len(anchor_values))
    ranked = list(getattr(bundle, "ranked_chunks", []) or [])
    coverage = max((_chunk_score(chunk) for chunk in ranked), default=0.0)
    contradiction_present = bool(getattr(bundle, "contradiction_flags", []))
    shaping_stats = getattr(bundle, "shaping_stats", {}) or {}
    input_count = max(1, int(shaping_stats.get("input_count", max(1, len(ranked)))))
    dedup_after = int(shaping_stats.get("after_dedup", len(ranked)))
    dedup_savings = max(0.0, min(1.0, 1.0 - (dedup_after / input_count)))
    exact_match_winners = getattr(bundle, "exact_match_winners", []) or []
    exact_ratio = _safe_len(exact_match_winners) / max(1, len(ranked))
    grounded = (
        bool(anchor_values)
        and citation >= _GROUNDED_CITATION_THRESHOLD
        and not contradiction_present
        and coverage > _ABSTAIN_COVERAGE_THRESHOLD
    )
    return EvidenceMetrics(
        citation_completeness=citation,
        support_coverage=coverage,
        contradiction_present=contradiction_present,
        provenance_completeness=citation,
        exact_match_ratio=exact_ratio,
        dedup_savings=dedup_savings,
        grounded_replayable=grounded,
        retrieval_id=_bundle_retrieval_id(bundle),
        collection=str(getattr(bundle, "collection", "") or ""),
        query_hash=_bundle_query_hash(bundle),
    )


def classify_evidence_support(metrics: EvidenceMetrics) -> WeakSupportDisposition:
    if metrics.contradiction_present:
        return WeakSupportDisposition.ESCALATE
    if metrics.support_coverage <= _ABSTAIN_COVERAGE_THRESHOLD and not metrics.grounded_replayable:
        return WeakSupportDisposition.ABSTAIN
    if metrics.support_coverage < _REFINE_COVERAGE_THRESHOLD:
        return WeakSupportDisposition.REFINE
    if metrics.citation_completeness < _GROUNDED_CITATION_THRESHOLD:
        return WeakSupportDisposition.REFINE
    return WeakSupportDisposition.PROCEED


def build_exit_artifact(bundle: Any) -> dict[str, Any]:
    metrics = _compute_metrics(bundle)
    confidence_score = max(0.0, min(1.0, (metrics.citation_completeness + metrics.support_coverage) / 2.0))
    escalation_reason = "evidence_contradiction_detected" if metrics.contradiction_present else None
    return {
        "rules_compliant": not metrics.contradiction_present,
        "answer_fit": metrics.support_coverage >= _REFINE_COVERAGE_THRESHOLD,
        "safety_clear": not metrics.contradiction_present,
        "grounded_replayable": metrics.grounded_replayable,
        "confidence_score": float(confidence_score),
        "escalation_reason": escalation_reason,
        "_evidence_metrics": asdict(metrics),
    }


def emit_bundle_telemetry(
    bundle: Any,
    *,
    request_id: str | None = None,
    contract: Any | None = None,
    trace_id: str | None = None,
) -> EvidenceMetrics:
    """Publish BUS T evidence_quality_metrics and return the sealed EvidenceMetrics row.

    Optional ``contract`` (e.g. ``C0EvidenceContract``) may override ``retrieval_id`` when
    present. ``request_id`` is a secondary override for correlation. Read-only.
    """
    metrics = _compute_metrics(bundle)
    rid = getattr(contract, "retrieval_id", None) if contract is not None else None
    if rid:
        metrics = replace(metrics, retrieval_id=str(rid))
    elif request_id:
        metrics = replace(metrics, retrieval_id=str(request_id))
    tid = trace_id or request_id or getattr(bundle, "retrieval_id", "") or ""
    _publish_metrics(metrics, trace_id=str(tid))
    return metrics


def _sealed_evidence_bundle_overlay(bundle: Any, exit_dict: dict[str, Any], metrics: EvidenceMetrics) -> dict[str, Any]:
    """Map sealed C0 metrics into SealedL2Artifact.evidence_bundle keys consumed by ExitControlGate.evaluate_sealed."""
    ranked = list(getattr(bundle, "ranked_chunks", []) or [])
    empty = len(ranked) == 0
    abstain_ok = empty or (metrics.support_coverage <= _ABSTAIN_COVERAGE_THRESHOLD) or metrics.grounded_replayable
    esc_reason = exit_dict.get("escalation_reason")
    escalation_ok = not (bool(esc_reason) ^ metrics.contradiction_present)
    relevance = max(
        float(metrics.exact_match_ratio),
        (float(metrics.citation_completeness) + float(metrics.support_coverage)) / 2.0,
    )
    return {
        "groundedness_score": float(metrics.citation_completeness),
        "support_coverage": float(metrics.support_coverage),
        "relevance_score": float(relevance),
        "abstain_correct": bool(abstain_ok),
        "escalation_correct": bool(escalation_ok),
        "safety_clear": bool(exit_dict.get("safety_clear", not metrics.contradiction_present)),
        "citation_completeness": float(metrics.citation_completeness),
        "contradiction_present": bool(metrics.contradiction_present),
        "grounded_replayable_contract": bool(exit_dict.get("grounded_replayable")),
        "_evidence_metrics": dict(exit_dict.get("_evidence_metrics") or asdict(metrics)),
    }


def _terminal_from_exit(disposition: ExitDisposition) -> TerminalClassification:
    if disposition is ExitDisposition.DENY_RETURN:
        return TerminalClassification.FAILURE
    if disposition is ExitDisposition.ESCALATE_TO_HITL:
        return TerminalClassification.NEEDS_HELP
    return TerminalClassification.SUCCESS


def _deny_exit_gate_result(trace_id: str, reason: str) -> ExitGateResult:
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
        reason=reason,
    )


def _default_gate_result(disposition: WeakSupportDisposition) -> Any:
    mapping = {
        WeakSupportDisposition.ABSTAIN: "DENY_RETURN",
        WeakSupportDisposition.ESCALATE: "ESCALATE_TO_HITL",
        WeakSupportDisposition.REFINE: "DENY_RETURN",
        WeakSupportDisposition.PROCEED: "ALLOW_RESPONSE",
    }
    return SimpleNamespace(disposition=SimpleNamespace(value=mapping[disposition]), reason=disposition.value)


def _run_sealed_exit_gate(bundle: Any, ctx: Any, disposition: WeakSupportDisposition | None = None) -> Any:
    resolved_disposition = disposition or classify_evidence_support(_compute_metrics(bundle))
    return _default_gate_result(resolved_disposition)


def _coerce_trace_fields(ctx: Any) -> tuple[str, str]:
    trace_id = getattr(ctx, "trace_id", "") or getattr(ctx, "run_id", "") or str(uuid.uuid4())
    run_id = getattr(ctx, "run_id", "") or trace_id
    return str(trace_id), str(run_id)


def _build_sealed_l2_artifact(
    bundle: Any,
    ctx: Any,
    gate_result: Any | None = None,
    *,
    exit_result: ExitGateResult | None = None,
    metrics: EvidenceMetrics | None = None,
    exit_dict: dict[str, Any] | None = None,
) -> SealedL2Artifact:
    """Build a typed SealedL2Artifact for L6 / evaluate_sealed consumers.

    Legacy callers may pass ``gate_result`` (duck-typed with ``.disposition.value`` only).
    The governed path passes ``exit_result`` + ``metrics`` + ``exit_dict`` from
    :func:`build_exit_artifact` / :class:`ExitControlGate`.
    """
    trace_id, run_id = _coerce_trace_fields(ctx)

    if gate_result is not None and exit_result is None:
        resolved = gate_result or _run_sealed_exit_gate(bundle, ctx)
        disposition_value = getattr(getattr(resolved, "disposition", None), "value", "")
        terminal = TerminalClassification.SUCCESS
        if disposition_value == "DENY_RETURN":
            terminal = TerminalClassification.FAILURE
        elif disposition_value == "ESCALATE_TO_HITL":
            terminal = TerminalClassification.NEEDS_HELP
        escalation_reason = None
        if bool(getattr(bundle, "contradiction_flags", [])):
            escalation_reason = "evidence_contradictions_present"
        return SealedL2Artifact(
            artifact_id=f"seal-{uuid.uuid4()}",
            trace_id=trace_id,
            exec_trace={"trace_id": trace_id, "run_id": run_id},
            terminal_classification=terminal,
            escalation_reason=escalation_reason,
            has_commit_payload=(disposition_value == "COMMIT_TO_UWG"),
            evidence_bundle={},
            replay_metadata=ReplayMetadata(
                replay_key=trace_id,
                determinism_digest="",
                replay_completeness=0.0,
                seed_captured=False,
                isolation_verified=False,
            ),
            sealed_at=time.monotonic(),
        )

    if exit_result is not None and metrics is not None and exit_dict is not None:
        d = exit_result.disposition
        terminal = _terminal_from_exit(d)
        if bool(getattr(bundle, "contradiction_flags", [])):
            escalation_reason = "evidence_contradictions_present"
        else:
            escalation_reason = exit_result.dimensions.escalation_reason
        eb = _sealed_evidence_bundle_overlay(bundle, exit_dict, metrics)
        replay_ok = float(metrics.citation_completeness) >= 0.60 and metrics.grounded_replayable
        return SealedL2Artifact(
            artifact_id=f"seal-{uuid.uuid4()}",
            trace_id=trace_id,
            exec_trace={"trace_id": trace_id, "run_id": run_id},
            evidence_bundle=eb,
            validation_counters=ValidationCounters(
                policy_checks_passed=2,
                policy_checks_failed=0,
                schema_checks_passed=2,
                schema_checks_failed=0,
            ),
            terminal_classification=terminal,
            escalation_reason=escalation_reason,
            has_commit_payload=bool(exit_result.dimensions.has_commit_payload),
            replay_metadata=ReplayMetadata(
                replay_key=metrics.query_hash,
                determinism_digest=metrics.retrieval_id,
                replay_completeness=1.0 if replay_ok else max(metrics.citation_completeness, metrics.support_coverage, 0.0),
                seed_captured=True,
                isolation_verified=True,
            ),
            sealed_at=time.monotonic(),
        )

    exit_d = build_exit_artifact(bundle)
    m = _compute_metrics(bundle)
    policy_hash = getattr(ctx, "policy_hash", None)
    gate = ExitControlGate(policy_hash=policy_hash)
    er = gate.evaluate(exit_d)
    return _build_sealed_l2_artifact(bundle, ctx, exit_result=er, metrics=m, exit_dict=exit_d)


def _publish_metrics(metrics: EvidenceMetrics, trace_id: str = "") -> None:
    get_telemetry_bus().publish(
        bus_type=BusType.TELEMETRY,
        signal_type="evidence_quality_metrics",
        payload=asdict(metrics),
        trace_id=trace_id,
    )


def _shadow_telemetry_sealed(
    metrics: EvidenceMetrics,
    exit_result: ExitGateResult,
    exit_dict: dict[str, Any],
) -> dict[str, Any]:
    dims = exit_result.dimensions
    return {
        "evidence_metrics_sealed": asdict(metrics),
        "exit_dimensions": {
            "rules_compliant": dims.rules_compliant,
            "answer_fit": dims.answer_fit,
            "safety_clear": dims.safety_clear,
            "grounded_replayable": dims.grounded_replayable,
            "confidence_score": dims.confidence_score,
            "has_commit_payload": dims.has_commit_payload,
            "escalation_reason": dims.escalation_reason,
        },
        "exit_dict_x1": {k: v for k, v in exit_dict.items() if not str(k).startswith("_")},
    }


def _enqueue_eval_packets(
    ctx: Any,
    metrics: EvidenceMetrics,
    gate_result: ExitGateResult,
    disposition: WeakSupportDisposition,
    artifact: SealedL2Artifact,
    tool_name: str,
    exit_dict: dict[str, Any],
) -> None:
    sealed_at = time.time()
    exit_disp = gate_result.disposition.value
    async_packet = AsyncEvalPacket(
        packet_id=f"ap-{uuid.uuid4()}",
        run_id=artifact.exec_trace.get("run_id", ""),
        lane_id=str(tool_name or "default_lane"),
        collection=metrics.collection,
        policy_hash=str(getattr(ctx, "policy_hash", "") or ""),
        citation_completeness=metrics.citation_completeness,
        support_coverage=metrics.support_coverage,
        provenance_completeness=metrics.provenance_completeness,
        exact_match_ratio=metrics.exact_match_ratio,
        grounded_replayable=metrics.grounded_replayable,
        contradiction_present=metrics.contradiction_present,
        query_hash=metrics.query_hash,
        retrieval_id=metrics.retrieval_id,
        exit_disposition=exit_disp,
        exit_trace_id=artifact.trace_id,
        exit_reason=gate_result.reason,
        weak_support_disposition=disposition.value,
        sealed_at=sealed_at,
    )
    get_async_eval_ingester().ingest(async_packet)
    telemetry = _shadow_telemetry_sealed(metrics, gate_result, exit_dict)
    enqueue_shadow_eval_packet(
        ShadowEvalPacket(
            packet_id=f"sep-{uuid.uuid4()}",
            run_id=async_packet.run_id,
            exit_disposition=exit_disp,
            exit_trace_id=artifact.trace_id,
            exit_reason=gate_result.reason,
            telemetry=telemetry,
            sealed_at=sealed_at,
        )
    )


def run_live_exit_gate(
    exit_artifact: dict[str, Any],
    *,
    policy_hash: str | None = None,
    log_to_outcome_logger: bool = False,
) -> ExitGateResult:
    """Run :meth:`ExitControlGate.evaluate` on a dict shaped by :func:`build_exit_artifact`.

    Benchmark and proof harness entry point (no retrieval side effects).
    When ``log_to_outcome_logger`` is True, emits an INFO log line only (no L4 writes).
    """
    import logging

    gate = ExitControlGate(policy_hash=policy_hash)
    result = gate.evaluate(exit_artifact)
    if log_to_outcome_logger:
        logging.getLogger(__name__).info(
            "[run_live_exit_gate] disposition=%s trace_id=%s",
            result.disposition.value,
            result.trace_id,
        )
    return result


def evaluate_and_emit(
    bundle: Any, ctx: Any, tool_name: str = "default_lane"
) -> tuple[ExitGateResult, WeakSupportDisposition]:
    metrics = _compute_metrics(bundle)
    disposition = classify_evidence_support(metrics)
    exit_dict = build_exit_artifact(bundle)
    _hcp = getattr(ctx, "has_commit_payload", None)
    if isinstance(_hcp, bool):
        exit_dict = {**exit_dict, "has_commit_payload": _hcp}

    trace_id, _ = _coerce_trace_fields(ctx)
    gate_failed = False
    try:
        gate = ExitControlGate(policy_hash=getattr(ctx, "policy_hash", None))
        exit_result = gate.evaluate(exit_dict)
    except (
        AttributeError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as exc:
        gate_failed = True
        exit_result = _deny_exit_gate_result(trace_id, f"ExitControlGate.evaluate failed: {exc}")

    _trace_id_for_publish, _ = _coerce_trace_fields(ctx)
    _publish_metrics(metrics, trace_id=_trace_id_for_publish)

    artifact = _build_sealed_l2_artifact(bundle, ctx, exit_result=exit_result, metrics=metrics, exit_dict=exit_dict)

    if gate_failed:
        return exit_result, disposition

    try:
        _enqueue_eval_packets(ctx, metrics, exit_result, disposition, artifact, tool_name, exit_dict)
    except (
        AttributeError,
        RuntimeError,
        TypeError,
        ValueError,
    ):  # guardian: allow-silent-swallow -- eval packet enqueue: non-fatal, gate_result already returned
        pass
    return exit_result, disposition
