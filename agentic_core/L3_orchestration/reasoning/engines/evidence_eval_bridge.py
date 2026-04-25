from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from hashlib import sha1
from types import SimpleNamespace
import time
import uuid
from typing import Any

from agentic_core.L2_execution.audit.telemetry_bus import BusType, get_telemetry_bus
from agentic_core.L2_execution.types.sealed_l2_artifact import SealedL2Artifact, TerminalClassification
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


def _default_gate_result(disposition: WeakSupportDisposition) -> Any:
    mapping = {
        WeakSupportDisposition.ABSTAIN: "DENY_RETURN",
        WeakSupportDisposition.ESCALATE: "ESCALATE_TO_HITL",
        WeakSupportDisposition.REFINE: "DENY_RETURN",
        WeakSupportDisposition.PROCEED: "ALLOW_RETURN",
    }
    return SimpleNamespace(disposition=SimpleNamespace(value=mapping[disposition]), reason=disposition.value)


def _run_sealed_exit_gate(bundle: Any, ctx: Any, disposition: WeakSupportDisposition | None = None) -> Any:
    resolved_disposition = disposition or classify_evidence_support(_compute_metrics(bundle))
    return _default_gate_result(resolved_disposition)


def _coerce_trace_fields(ctx: Any) -> tuple[str, str]:
    trace_id = getattr(ctx, "trace_id", "") or getattr(ctx, "run_id", "") or str(uuid.uuid4())
    run_id = getattr(ctx, "run_id", "") or trace_id
    return str(trace_id), str(run_id)


def _build_sealed_l2_artifact(bundle: Any, ctx: Any, gate_result: Any | None = None) -> SealedL2Artifact:
    gate_result = gate_result or _run_sealed_exit_gate(bundle, ctx)
    trace_id, run_id = _coerce_trace_fields(ctx)
    disposition_value = getattr(getattr(gate_result, "disposition", None), "value", "")
    terminal = TerminalClassification.SUCCESS
    if disposition_value == "DENY_RETURN":
        terminal = TerminalClassification.FAILURE
    elif disposition_value == "ESCALATE_TO_HITL":
        terminal = TerminalClassification.NEEDS_HELP
    escalation_reason = None
    if bool(getattr(bundle, "contradiction_flags", [])):
        escalation_reason = "evidence_contradictions_present"
    # NOTE: run_scope is a ClassVar on SealedL2Artifact (always "CURRENT_RUN"),
    # so it MUST NOT be passed to __init__. artifact_id is required.
    return SealedL2Artifact(
        artifact_id=f"seal-{uuid.uuid4()}",
        trace_id=trace_id,
        exec_trace={"trace_id": trace_id, "run_id": run_id},
        terminal_classification=terminal,
        escalation_reason=escalation_reason,
        has_commit_payload=(disposition_value == "COMMIT_TO_UWG"),
    )


def _publish_metrics(metrics: EvidenceMetrics, trace_id: str = "") -> None:
    # TelemetryBus.publish takes individual args (it builds the BusMessage
    # internally, including timestamp + trace_id). Calling BusMessage(...) here
    # directly would skip required positional fields.
    get_telemetry_bus().publish(
        bus_type=BusType.TELEMETRY,
        signal_type="evidence_quality_metrics",
        payload=asdict(metrics),
        trace_id=trace_id,
    )


def _enqueue_eval_packets(
    ctx: Any,
    metrics: EvidenceMetrics,
    gate_result: Any,
    disposition: WeakSupportDisposition,
    artifact: SealedL2Artifact,
    tool_name: str,
) -> None:
    sealed_at = time.time()
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
        exit_disposition=getattr(gate_result.disposition, "value", ""),
        exit_trace_id=artifact.trace_id,
        exit_reason=getattr(gate_result, "reason", ""),
        weak_support_disposition=disposition.value,
        sealed_at=sealed_at,
    )
    get_async_eval_ingester().ingest(async_packet)
    enqueue_shadow_eval_packet(
        ShadowEvalPacket(
            packet_id=f"sep-{uuid.uuid4()}",
            run_id=async_packet.run_id,
            sealed_at=sealed_at,
        )
    )


def evaluate_and_emit(
    bundle: Any, ctx: Any, tool_name: str = "default_lane"
) -> tuple[Any, WeakSupportDisposition]:
    metrics = _compute_metrics(bundle)
    disposition = classify_evidence_support(metrics)
    gate_result = _default_gate_result(disposition)
    gate_failed = False
    try:
        gate_result = _run_sealed_exit_gate(bundle, ctx, disposition)
    except (AttributeError, RuntimeError, TypeError, ValueError):
        gate_result = _default_gate_result(disposition)
        gate_failed = True

    _trace_id_for_publish, _ = _coerce_trace_fields(ctx)
    _publish_metrics(metrics, trace_id=_trace_id_for_publish)
    artifact = _build_sealed_l2_artifact(bundle, ctx, gate_result=gate_result)
    if gate_failed:
        return gate_result, disposition
    try:
        _enqueue_eval_packets(ctx, metrics, gate_result, disposition, artifact, tool_name)
    except (
        AttributeError,
        RuntimeError,
        TypeError,
        ValueError,
    ):  # guardian: allow-silent-swallow -- eval packet enqueue: non-fatal, gate_result already returned
        pass
    return gate_result, disposition
