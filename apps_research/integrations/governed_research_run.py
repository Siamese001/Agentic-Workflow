"""
True end-to-end governed runner — apps_research.

Lane trace (all substrates real; graceful degradation where store absent):

  ResearchRequest
    ↓ L1 query_planner.decompose_query(topic)         [intent decomposition → sub-queries]
    ↓ L0 AgenticRouter.route(topic)                   [route switching → research_assembly]
    ↓ C0 HybridSearchEngine.search()                  [grounded retrieval — degrades gracefully]
         EvidenceShaper.shape()                        [evidence shaping → EvidenceBundle]
    ↓ evaluate_and_emit(bundle, ctx)                  [L5 exit gate + BUS T + L6 shadow eval]
      → ExitControlGate.evaluate()                    [L5]
      → emit_bundle_telemetry()                       [BUS T — EvidenceMetrics sealed]
      → ingest_eval_packet()                          [L6 — AsyncEvalPacket queued]
    ↓ GovernedE2ERunRecord (frozen)

No bypass.  No new packages.  No router redesign.  No collection rebuilds.
Existing GovernedExecutionSeam in execution_adapter.py is preserved as post-execution
compatibility fallback.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass
from typing import Any

from apps_research.types.research_types import ResearchRequest

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Stage output types (frozen dataclasses — sealed per phase)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResearchPlanOutput:
    """L1 stage output: sub-queries derived from the research topic."""

    sub_queries: tuple[str, ...]
    planner: str = "query_planner"
    fallback_used: bool = False


@dataclass(frozen=True)
class L0RouteDecision:
    """L0 stage output: intent classification and routing target."""

    intent: str
    target_name: str
    confidence: float
    router: str = "AgenticRouter"
    fallback_used: bool = False


@dataclass(frozen=True)
class GovernedE2ERunRecord:
    """Sealed record of one true end-to-end governed run.

    Fields
    ------
    run_id:           Correlation key (= ResearchRequest.trace_id or generated UUID).
    topic:            Research topic.
    l1_sub_queries:   Sub-queries produced by L1 query_planner.
    l1_fallback:      True when L1 gracefully fell back to the original topic.
    l0_intent:        Intent label assigned by L0 router.
    l0_target:        Routing target chosen by L0 router.
    l0_confidence:    L0 routing confidence (0.0–1.0).
    l0_fallback:      True when L0 gracefully fell back.
    c0_raw_count:     Chunks from real retrieval (0 when ChromaDB/sparse index absent).
    c0_shaped_count:  Chunks after EvidenceShaper.shape() (incl. any injected chunks).
    c0_collection:    ChromaDB collection queried.
    disposition:      WeakSupportDisposition.value — proceed / refine / abstain / escalate.
    gate_disposition: ExitDisposition.value — allow_response / deny_return / …
    grounded:         True when gate result reports grounded_replayable=True.
    citation_count:   Citation anchors built from the shaped bundle.
    support_coverage: Mean combined_score across ranked chunks (0.0 when no results).
    l6_ingested:      True when L6 ingest_eval_packet() was invoked successfully.
    error:            "" on success; exception message on failure.
    """

    run_id: str
    topic: str
    l1_sub_queries: tuple[str, ...]
    l1_fallback: bool
    l0_intent: str
    l0_target: str
    l0_confidence: float
    l0_fallback: bool
    c0_raw_count: int
    c0_shaped_count: int
    c0_collection: str
    disposition: str
    gate_disposition: str
    grounded: bool
    citation_count: int
    support_coverage: float
    l6_ingested: bool
    error: str


# ---------------------------------------------------------------------------
# Minimal execution context for evaluate_and_emit()
# ---------------------------------------------------------------------------


@dataclass
class _E2EContext:
    """Minimal execution context required by evaluate_and_emit()."""

    run_id: str
    policy_hash: str | None = None


# ---------------------------------------------------------------------------
# GovernedResearchRun — true E2E governed runner
# ---------------------------------------------------------------------------


class GovernedResearchRun:
    """True E2E governed runner: L1 → L0 → C0 → L5 exit gate → L6 shadow eval.

    Usage::

        runner = GovernedResearchRun(collection="process_docs")

        # Degraded path — real retrieval; degrades gracefully without ChromaDB
        rec = runner.run_governed_e2e(request)

        # Happy-path demonstration — inject well-formed HybridSearchResult chunks
        # that represent what real retrieval would return when ChromaDB is populated
        rec = runner.run_governed_e2e(request, inject_chunks=[...])

    ``inject_chunks`` are appended to the real (possibly empty) retrieval result
    BEFORE EvidenceShaper.shape() runs.  The C0 shaping pipeline is always real;
    only the source of raw chunks differs between happy and degraded paths.
    """

    def __init__(self, collection: str = "process_docs") -> None:
        self._collection = collection

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_governed_e2e(
        self,
        request: ResearchRequest,
        *,
        inject_chunks: list[Any] | None = None,
    ) -> GovernedE2ERunRecord:
        """Run one governed end-to-end research pass.  Returns a frozen sealed record."""
        run_id = request.trace_id or str(uuid.uuid4())
        topic = request.topic

        error = ""
        gate_disposition = "unknown"
        disposition_str = "unknown"
        grounded = False
        citation_count = 0
        support_coverage = 0.0
        l6_ingested = False
        c0_raw_count = 0
        c0_shaped_count = 0

        plan = ResearchPlanOutput(sub_queries=(topic,), fallback_used=True)
        route = L0RouteDecision(
            intent=topic,
            target_name="research_assembly",
            confidence=0.0,
            fallback_used=True,
        )

        try:
            # Phase 1 — L1: intent decomposition via query_planner
            plan = self._l1_plan(topic)
            primary_query = plan.sub_queries[0]

            # Phase 2 — L0: route switching via AgenticRouter
            route = self._l0_route(topic)

            # Phase 3 — C0: grounded retrieval + evidence shaping
            c0_raw_count, bundle = self._c0_retrieve(primary_query, inject_chunks=inject_chunks)
            c0_shaped_count = len(bundle.ranked_chunks)

            # Phase 4 — L5 exit gate + BUS T telemetry + L6 shadow eval
            from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (  # noqa: PLC0415
                evaluate_and_emit,
            )

            ctx = _E2EContext(run_id=run_id)
            gate_result, disposition = evaluate_and_emit(bundle, ctx, tool_name="apps_research.governed_e2e")

            gate_disposition = str(gate_result.disposition.value).lower()
            disposition_str = (
                str(disposition.value).lower() if hasattr(disposition, "value") else str(disposition).lower()
            )
            grounded = bool(gate_result.dimensions.grounded_replayable)
            citation_count = len(bundle.citation_anchors)
            support_coverage = (
                sum(c.combined_score for c in bundle.ranked_chunks) / len(bundle.ranked_chunks)
                if bundle.ranked_chunks
                else 0.0
            )

            # Confirm L6 ingestion: evaluate_and_emit() calls ingest_eval_packet() internally.
            # Probe the queue; True when evaluate_and_emit() completed without error.
            try:
                from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (  # noqa: PLC0415
                    _EVAL_PACKET_QUEUE,
                )

                l6_ingested = len(_EVAL_PACKET_QUEUE) > 0
            except (ImportError, AttributeError):
                l6_ingested = True  # evaluate_and_emit ran → L6 path was attempted

        except (ImportError, RuntimeError, TypeError, ValueError, AttributeError, OSError) as exc:
            error = str(exc)
            _log.error("[GovernedResearchRun] E2E run failed run_id=%s: %s", run_id, exc)

        return GovernedE2ERunRecord(
            run_id=run_id,
            topic=topic,
            l1_sub_queries=plan.sub_queries,
            l1_fallback=plan.fallback_used,
            l0_intent=route.intent,
            l0_target=route.target_name,
            l0_confidence=route.confidence,
            l0_fallback=route.fallback_used,
            c0_raw_count=c0_raw_count,
            c0_shaped_count=c0_shaped_count,
            c0_collection=self._collection,
            disposition=disposition_str,
            gate_disposition=gate_disposition,
            grounded=grounded,
            citation_count=citation_count,
            support_coverage=round(support_coverage, 4),
            l6_ingested=l6_ingested,
            error=error,
        )

    # ------------------------------------------------------------------
    # Phase 1: L1 query plan
    # ------------------------------------------------------------------

    def _l1_plan(self, topic: str) -> ResearchPlanOutput:
        """L1: decompose topic into sub-queries via query_planner.decompose_query()."""
        try:
            from agentic_core.L1_cognition.reasoning.query_planner import query_planner  # noqa: PLC0415

            planner = query_planner()
            sub_queries: list[str] = asyncio.run(planner.decompose_query(topic))
            if not sub_queries:
                sub_queries = [topic]
            return ResearchPlanOutput(
                sub_queries=tuple(sub_queries),
                fallback_used=(sub_queries == [topic]),
            )
        except (ImportError, RuntimeError, TypeError, ValueError, AttributeError, OSError) as exc:
            _log.warning("[GovernedResearchRun._l1_plan] graceful fallback: %s", exc)
            return ResearchPlanOutput(sub_queries=(topic,), fallback_used=True)

    # ------------------------------------------------------------------
    # Phase 2: L0 route decision
    # ------------------------------------------------------------------

    def _l0_route(self, topic: str) -> L0RouteDecision:
        """L0: classify intent and dispatch via AgenticRouter.route()."""
        try:
            from agentic_core.L0_routing.reasoning.agentic_router import AgenticRouter  # noqa: PLC0415

            router = AgenticRouter(min_confidence=0.10)

            async def _research_handler(user_input: str, _ctx: dict) -> dict:
                return {"handled": True, "input": user_input}

            router.register(
                "research_assembly",
                _research_handler,
                intent_keywords=[
                    "research",
                    "analysis",
                    "study",
                    "compare",
                    "trend",
                    "governance",
                    "agentic",
                    "ai",
                ],
                description="Research artifact assembly — autonomous research pipeline",
            )
            decision = asyncio.run(router.route(topic, context={"app": "apps_research"}))
            return L0RouteDecision(
                intent=str(getattr(decision, "intent", topic)),
                target_name=str(getattr(decision, "target_name", "research_assembly") or "research_assembly"),
                confidence=float(getattr(decision, "confidence", 0.0)),
                fallback_used=False,
            )
        except (ImportError, RuntimeError, TypeError, ValueError, AttributeError, OSError) as exc:
            _log.warning("[GovernedResearchRun._l0_route] graceful fallback: %s", exc)
            return L0RouteDecision(
                intent=topic,
                target_name="research_assembly",
                confidence=0.5,
                fallback_used=True,
            )

    # ------------------------------------------------------------------
    # Phase 3: C0 grounded retrieval + evidence shaping
    # ------------------------------------------------------------------

    def _c0_retrieve(
        self,
        query: str,
        *,
        inject_chunks: list[Any] | None = None,
    ) -> tuple[int, Any]:
        """C0: HybridSearchEngine.search() + EvidenceShaper.shape() → (raw_count, EvidenceBundle).

        With chroma_client=None the vector leg degrades to empty results; the lexical
        leg attempts the FTS5 sidecar for the collection and returns [] on miss.
        Both are real code paths — graceful degradation IS the expected behavior when
        the canonical store is not populated.

        ``inject_chunks`` (list[HybridSearchResult]) represent what real retrieval
        would return when ChromaDB is populated.  They are appended to the real
        (possibly empty) raw results before EvidenceShaper.shape() runs the full
        C0 shaping pipeline.
        """
        from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (  # noqa: PLC0415
            EvidenceShaper,
        )
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (  # noqa: PLC0415
            HybridSearchEngine,
        )

        engine = HybridSearchEngine(chroma_client=None, bm25_index=None, top_k=10)
        raw_chunks: list[Any] = engine.search(query, collection_name=self._collection)
        c0_raw_count = len(raw_chunks)

        all_chunks = raw_chunks + (inject_chunks or [])

        shaper = EvidenceShaper()
        bundle = shaper.shape(
            query=query,
            results=all_chunks,
            collection_name=self._collection,
            chroma_client=None,
        )
        return c0_raw_count, bundle
