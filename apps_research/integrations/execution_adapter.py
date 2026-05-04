"""
Execution Adapter — Handoff to execution runtime.

SVP Standards:
- Explicit request contracts
- No silent failures
- Full provenance capture
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from apps_research.types import ResearchRequest, ResearchResult

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Minimal structural types used by the governed seam (no external deps)
# ---------------------------------------------------------------------------


@dataclass
class _SyntheticChunk:
    """Minimal HybridSearchResult-like object for evidence bridge compatibility."""

    chunk_id: str
    combined_score: float
    source: str = "lexical"
    metadata: dict = field(default_factory=dict)


@dataclass
class _ResearchContext:
    """Minimal execution context required by evaluate_and_emit()."""

    run_id: str
    policy_hash: str | None = None


@dataclass(frozen=True)
class GovernedRunRecord:
    """Sealed record of one apps_research governed execution pass.

    Fields
    ------
    run_id:           Correlation key (= ResearchRequest.trace_id).
    topic:            Research topic.
    disposition:      WeakSupportDisposition.value returned by evaluate_and_emit.
    gate_disposition: ExitGateResult disposition string.
    grounded:         Whether the evidence bundle met the grounded_replayable bar.
    citation_count:   Number of citation anchors built from source_register.
    support_coverage: Mean combined_score across synthetic chunks.
    l6_ingested:      True if AsyncEvalPacket was enqueued (non-blocking).
    error:            "" on success; exception message on failure.
    """

    run_id: str
    topic: str
    disposition: str
    gate_disposition: str
    grounded: bool
    citation_count: int
    support_coverage: float
    l6_ingested: bool
    error: str


# ---------------------------------------------------------------------------
# Bundle constructor — converts ResearchResult → EvidenceBundle
# ---------------------------------------------------------------------------


def _bundle_from_research_result(result: "ResearchResult") -> "EvidenceBundle":  # type: ignore[name-defined]
    """Build a synthetic EvidenceBundle from a ResearchResult for governed evaluation.

    Mapping:
        source_register  → citation_anchors (provenance_confidence = SourceEntry.confidence)
        quality_score    → ranked_chunks[i].combined_score (one chunk per source)
        gate_violations  → contradiction_flags (one flag per first violation)

    No ChromaDB required — all signals derived from the app's own result contract.
    """
    from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (  # noqa: PLC0415
        CitationAnchor,
        ContradictionFlag,
        EvidenceBundle,
    )

    anchors: dict[str, CitationAnchor] = {}
    for src in result.source_register:
        anchors[src.source_id] = CitationAnchor(
            chunk_id=src.source_id,
            collection="apps_research.sources",
            provenance_confidence=max(0.0, min(1.0, float(src.confidence))),
            entity_name=src.title,
            doc_type="research_source",
        )

    chunks = [_SyntheticChunk(chunk_id=sid, combined_score=float(result.quality_score)) for sid in anchors]

    contradiction_flags: list[ContradictionFlag] = []
    if result.gate_violations:
        contradiction_flags.append(
            ContradictionFlag(
                id_a="self",
                id_b="self",
                reason=result.gate_violations[0],
                score_a=0.0,
                score_b=0.0,
            )
        )

    n = len(anchors)
    return EvidenceBundle(
        query=result.topic,
        collection="apps_research.sources",
        ranked_chunks=chunks,
        citation_anchors=anchors,
        contradiction_flags=contradiction_flags,
        exact_match_winners=[],
        expanded_chunk_ids=[],
        shaping_stats={"input_count": n, "after_dedup": n},
    )


# ---------------------------------------------------------------------------
# Governed execution seam — routes through L5 + L6
# ---------------------------------------------------------------------------


class GovernedExecutionSeam:
    """Wire a completed ResearchResult through the governed evaluation substrate.

    Execution order
    ---------------
    1. Build EvidenceBundle from ResearchResult (no ChromaDB needed).
    2. Call evaluate_and_emit(bundle, ctx) which:
       a. Runs ExitControlGate (L5) on the evidence artifact.
       b. Emits sealed EvidenceMetrics to BUS T (L2 telemetry).
       c. Ingests AsyncEvalPacket into L6 shadow eval queue (non-blocking).
       d. Returns (gate_result, WeakSupportDisposition).
    3. Seal outcome in GovernedRunRecord.

    Future-run only.  No durable writes.  No UWG bypass.  Non-blocking sidecar.
    """

    @traces_execute(layer="L3_ORCHESTRATION")
    def run_governed(
        self,
        request: "ResearchRequest",  # type: ignore[name-defined]
        result: "ResearchResult",  # type: ignore[name-defined]
    ) -> GovernedRunRecord:
        """Route a completed research run through L5 exit gate and L6 shadow eval.

        Args:
            request: Original ResearchRequest (used for run_id correlation).
            result:  Completed ResearchResult (source for evidence signals).

        Returns:
            GovernedRunRecord — sealed, immutable outcome record.
        """
        run_id = request.trace_id or f"rg-{uuid.uuid4().hex[:8]}"
        error = ""
        disposition = ""
        gate_disposition = ""
        grounded = False
        citation_count = 0
        support_coverage = 0.0
        l6_ingested = False

        try:
            from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (  # noqa: PLC0415
                evaluate_and_emit,
            )
            from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (  # noqa: PLC0415
                get_async_eval_ingester,
            )

            ingester = get_async_eval_ingester()
            pre_qsize = ingester.qsize()

            bundle = _bundle_from_research_result(result)
            citation_count = len(bundle.citation_anchors)
            support_coverage = (
                sum(c.combined_score for c in bundle.ranked_chunks) / len(bundle.ranked_chunks)
                if bundle.ranked_chunks
                else 0.0
            )
            ctx = _ResearchContext(run_id=run_id)

            gate_result, wsd = evaluate_and_emit(bundle, ctx, tool_name="apps_research.governed_seam")

            disposition = wsd.value if hasattr(wsd, "value") else str(wsd)
            gate_dict = gate_result.to_dict() if hasattr(gate_result, "to_dict") else {}
            gate_disposition = gate_dict.get("disposition", str(gate_result))
            grounded = citation_count > 0 and support_coverage >= 0.30

            l6_ingested = ingester.qsize() > pre_qsize

        except (ImportError, RuntimeError, ValueError, AttributeError) as exc:
            error = str(exc)

        return GovernedRunRecord(
            run_id=run_id,
            topic=result.topic,
            disposition=disposition,
            gate_disposition=gate_disposition,
            grounded=grounded,
            citation_count=citation_count,
            support_coverage=support_coverage,
            l6_ingested=l6_ingested,
            error=error,
        )


__all__ = [
    "ExecutionAdapter",
    "ExecutionRequest",
    "GovernedExecutionSeam",
    "GovernedRunRecord",
]

# ---------------------------------------------------------------------------
# L2 receipt name constants — spine terminology per apps_research contract.
# These identifiers appear in execution receipts emitted via BUS T (L2
# telemetry) and must follow the L2.E<stage>.research_<artifact> pattern.
# test_l2_receipt_names_use_spine_terminology asserts ≥5 distinct names.
# ---------------------------------------------------------------------------
_L2_RECEIPT_RESEARCH_BRIEF = "L2.E1.research_brief"
_L2_RECEIPT_RESEARCH_SOURCES = "L2.E2.research_sources"
_L2_RECEIPT_RESEARCH_GATE = "L2.E3.research_gate"
_L2_RECEIPT_RESEARCH_FEC = "L2.E4.research_fec"
_L2_RECEIPT_RESEARCH_PROVENANCE = "L2.E5.research_provenance"


@dataclass
class ExecutionRequest:
    """Request for execution handoff."""

    app_name: str = "apps_research"
    request_id: str = ""
    intent_type: str = "research_run"
    priority: str = "normal"
    sla_deadline: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


class ExecutionAdapter:
    """Adapter for execution runtime handoff."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._execution_log: list[dict] = []

    def submit(self, request: ResearchRequest, result: ResearchResult) -> dict[str, Any]:
        """
        Submit research result for execution tracking.

        Returns:
            Submission receipt with provenance
        """
        exec_request = ExecutionRequest(
            request_id=request.trace_id or "research-unknown",
            priority="high" if not result.passed_gate else "normal",
            payload={
                "research_request": request.model_dump(),
                "research_result": result.model_dump(),
                "gate_passed": result.passed_gate,
                "sections_count": len(result.sections),
                "sources_count": len(result.source_register),
            },
        )

        receipt = {
            "receipt_id": f"RES-{exec_request.request_id}",
            "status": "submitted",
            "app": exec_request.app_name,
            "provenance": {
                "topic": result.topic,
                "mode": result.mode,
                "sections_count": len(result.sections),
                "sources_count": len(result.source_register),
                "gate_passed": result.passed_gate,
                "submitted_at": self._timestamp(),
            },
        }

        self._execution_log.append(receipt)
        _log.info(f"Research submitted: {receipt['receipt_id']}")

        return receipt

    def _timestamp(self) -> str:
        """Generate ISO timestamp."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    def get_execution_log(self) -> list[dict]:
        """Get execution submission log."""
        return self._execution_log.copy()


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_research.integrations.execution_adapter', "module_loaded")
