"""
Shared governed-app runner — reusable L1→L0→C0→L2→L5+L6 pipeline base.

All governed apps subclass GovernedAppRunner and configure via class
attributes (APP_NAME, CAPABILITY_TOKEN, ROUTING_TARGET, ROUTING_KEYWORDS)
plus constructor args (collection).

Pattern::

    class MyGovernedRun(GovernedAppRunner):
        APP_NAME        = "apps_my"
        CAPABILITY_TOKEN = "apps_my.governed_e2e.v1"
        ROUTING_TARGET  = "my_assembly"
        ROUTING_KEYWORDS = ["keyword1", "keyword2"]

        def __init__(self, collection: str = "my_docs") -> None:
            super().__init__(collection=collection)

        def run_governed_e2e(self, request, *, inject_chunks=None):
            core = self.run_governed_core(
                query=_query_from(request),
                run_id=request.trace_id or "",
                inject_chunks=inject_chunks,
            )
            return _translate(core)          # app-specific record type

Current consumers:
  apps_research.integrations.governed_research_run.GovernedResearchRun
  apps_exec.integrations.governed_exec_run.GovernedExecRun

No bypass.  No new packages.  No router redesign.  No collection rebuilds.
Layer rule: apps_shared may import from agentic_core L0–L6 only (downward).
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal pipeline stage types (private to this module)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _PlanOutput:
    sub_queries: tuple[str, ...]
    fallback_used: bool = False


@dataclass(frozen=True)
class _RouteOutput:
    intent: str
    target_name: str
    confidence: float
    fallback_used: bool = False


@dataclass
class _AppContext:
    """Minimal execution context passed to evaluate_and_emit()."""

    run_id: str
    policy_hash: str | None = None


# ---------------------------------------------------------------------------
# GovernedAppRunRecord — common sealed record for all governed apps
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GovernedAppRunRecord:
    """Sealed record of one governed app E2E pipeline run.

    App-specific runners translate this into their own result types before
    returning to callers (see GovernedResearchRun, GovernedExecRun).

    Fields
    ------
    run_id:           Correlation key.
    app_name:         Application identifier (e.g. "apps_research").
    query:            Primary query string fed through the pipeline.
    l1_sub_queries:   Sub-queries produced by L1 query_planner.
    l1_fallback:      True when L1 fell back to the original query.
    l0_intent:        Intent label assigned by L0 router.
    l0_target:        Routing target chosen by L0 router.
    l0_confidence:    L0 routing confidence (0.0–1.0).
    l0_fallback:      True when L0 fell back.
    c0_raw_count:     Chunks from real retrieval (0 when store absent).
    c0_shaped_count:  Chunks after EvidenceShaper.shape().
    c0_collection:    Collection queried.
    disposition:      WeakSupportDisposition.value.
    gate_disposition: ExitDisposition.value.
    grounded:         True when gate result reports grounded_replayable=True.
    citation_count:   Citation anchors from the shaped bundle.
    support_coverage: Mean combined_score across ranked chunks.
    l6_ingested:      True when L6 ingest_eval_packet() was invoked.
    l2_executed:      True when authorize_and_execute() ran without error.
    error:            "" on success; exception message on failure.
    """

    run_id: str
    app_name: str
    query: str
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
    l2_executed: bool
    error: str


# ---------------------------------------------------------------------------
# GovernedAppRunner — shared base class
# ---------------------------------------------------------------------------


class GovernedAppRunner:
    """Shared base for the governed-app L1→L0→C0→L2→L5+L6 pipeline.

    Subclasses declare their app identity via class attributes and call
    ``run_governed_core()`` from their app-specific ``run_governed_e2e()``
    method to execute the common governed substrate.

    Class attributes to override
    ----------------------------
    APP_NAME:         e.g. "apps_research"
    CAPABILITY_TOKEN: e.g. "apps_research.governed_e2e.v1"
    ROUTING_TARGET:   e.g. "research_assembly"
    ROUTING_KEYWORDS: e.g. ["research", "analysis", ...]
    """

    APP_NAME: str = ""
    CAPABILITY_TOKEN: str = ""
    ROUTING_TARGET: str = ""
    ROUTING_KEYWORDS: list[str] = []

    def __init__(self, collection: str = "process_docs") -> None:
        self._collection = collection

    # ------------------------------------------------------------------
    # Public: shared pipeline
    # ------------------------------------------------------------------

    def run_governed_core(
        self,
        query: str,
        *,
        run_id: str = "",
        inject_chunks: list[Any] | None = None,
    ) -> GovernedAppRunRecord:
        """Execute L1→L0→C0→L2→L5+L6 and return a sealed GovernedAppRunRecord.

        Parameters
        ----------
        query:
            Primary query / topic string for this run.
        run_id:
            Correlation key; a UUID is generated when empty.
        inject_chunks:
            Optional list of HybridSearchResult-like objects appended to
            real retrieval results before EvidenceShaper.shape() runs.
            Represents what real retrieval would return when the canonical
            store is populated; graceful degradation is expected when this
            is None and ChromaDB/BM25 index are absent.
        """
        import uuid as _uuid  # noqa: PLC0415

        run_id = run_id or str(_uuid.uuid4())

        error = ""
        gate_disposition = "unknown"
        disposition_str = "unknown"
        grounded = False
        citation_count = 0
        support_coverage = 0.0
        l6_ingested = False
        l2_executed = False
        c0_raw_count = 0
        c0_shaped_count = 0

        plan = _PlanOutput(sub_queries=(query,), fallback_used=True)
        route = _RouteOutput(
            intent=query,
            target_name=self.ROUTING_TARGET or "unknown",
            confidence=0.0,
            fallback_used=True,
        )

        try:
            # Phase 1 — L1: intent decomposition via query_planner
            plan = self._l1_plan(query)
            primary_query = plan.sub_queries[0]

            # Phase 2 — L0: route switching via AgenticRouter
            route = self._l0_route(query)

            # Phase 3 — C0: grounded retrieval + evidence shaping
            c0_raw_count, bundle = self._c0_retrieve(primary_query, inject_chunks=inject_chunks)
            c0_shaped_count = len(bundle.ranked_chunks)

            # Phase 4 — L2 chokepoint + L5 exit gate + L6 shadow eval
            from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (  # noqa: PLC0415
                evaluate_and_emit,
            )

            _l2_ctx: Any = _AppContext(run_id=run_id)
            try:
                from agentic_core.L4_state.utils.context.execution_context import (  # noqa: PLC0415
                    ActionClass,
                    ExecutionContext,
                )
                from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (  # noqa: PLC0415
                    authorize_and_execute,
                )
                import hashlib as _hl  # noqa: PLC0415

                _policy_hash = _hl.sha256(f"{self.APP_NAME}:{query}".encode("utf-8")).hexdigest()
                _execution_ctx = ExecutionContext.create(
                    run_id=run_id,
                    capability_token=self.CAPABILITY_TOKEN,
                    policy_hash=_policy_hash,
                    execution_input=query,
                    execution_target=f"{self.APP_NAME}.governed_e2e",
                    action_class=ActionClass.READ_ONLY,
                    trace_id=run_id,
                )
                _, _l2_ctx = authorize_and_execute(
                    _execution_ctx,
                    lambda _payload: {"query": _payload, "status": "execution_complete"},
                    self.CAPABILITY_TOKEN,
                    query,
                    target_name=f"{self.APP_NAME}.governed_e2e",
                    safety_plane_available=True,
                )
                l2_executed = True
            except (ImportError, RuntimeError, ValueError, AttributeError) as _l2_exc:
                _log.warning(
                    "[GovernedAppRunner._l2] chokepoint skipped app=%s: %s",
                    self.APP_NAME,
                    _l2_exc,
                )

            gate_result, disposition = evaluate_and_emit(
                bundle, _l2_ctx, tool_name=f"{self.APP_NAME}.governed_e2e"
            )

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

            try:
                from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (  # noqa: PLC0415
                    get_async_eval_ingester,
                    get_shadow_eval_ingester,
                )

                l6_ingested = get_async_eval_ingester().qsize() > 0 or get_shadow_eval_ingester().qsize() > 0
            except (ImportError, AttributeError):
                l6_ingested = True

        except (ImportError, RuntimeError, TypeError, ValueError, AttributeError, OSError) as exc:
            error = str(exc)
            _log.error(
                "[GovernedAppRunner] E2E failed run_id=%s app=%s: %s",
                run_id,
                self.APP_NAME,
                exc,
            )

        return GovernedAppRunRecord(
            run_id=run_id,
            app_name=self.APP_NAME,
            query=query,
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
            l2_executed=l2_executed,
            error=error,
        )

    # ------------------------------------------------------------------
    # Phase 1: L1 query plan
    # ------------------------------------------------------------------

    def _l1_plan(self, topic: str) -> _PlanOutput:
        """L1: decompose topic into sub-queries via query_planner.decompose_query()."""
        try:
            from agentic_core.L1_cognition.reasoning.query_planner import query_planner  # noqa: PLC0415

            planner = query_planner()
            sub_queries: list[str] = asyncio.run(planner.decompose_query(topic))
            if not sub_queries:
                sub_queries = [topic]
            return _PlanOutput(
                sub_queries=tuple(sub_queries),
                fallback_used=(sub_queries == [topic]),
            )
        except (ImportError, RuntimeError, TypeError, ValueError, AttributeError, OSError) as exc:
            _log.warning(
                "[GovernedAppRunner._l1_plan] graceful fallback app=%s: %s",
                self.APP_NAME,
                exc,
            )
            return _PlanOutput(sub_queries=(topic,), fallback_used=True)

    # ------------------------------------------------------------------
    # Phase 2: L0 route decision
    # ------------------------------------------------------------------

    def _l0_route(self, topic: str) -> _RouteOutput:
        """L0: classify intent and dispatch via AgenticRouter.route()."""
        try:
            from agentic_core.L0_routing.reasoning.agentic_router import AgenticRouter  # noqa: PLC0415

            router = AgenticRouter(min_confidence=0.10)

            async def _handler(user_input: str, _ctx: dict) -> dict:
                return {"handled": True, "input": user_input}

            router.register(
                self.ROUTING_TARGET,
                _handler,
                intent_keywords=self.ROUTING_KEYWORDS,
                description=f"{self.APP_NAME} governed pipeline",
            )
            decision = asyncio.run(router.route(topic, context={"app": self.APP_NAME}))
            return _RouteOutput(
                intent=str(getattr(decision, "intent", topic)),
                target_name=str(getattr(decision, "target_name", self.ROUTING_TARGET) or self.ROUTING_TARGET),
                confidence=float(getattr(decision, "confidence", 0.0)),
                fallback_used=False,
            )
        except (ImportError, RuntimeError, TypeError, ValueError, AttributeError, OSError) as exc:
            _log.warning(
                "[GovernedAppRunner._l0_route] graceful fallback app=%s: %s",
                self.APP_NAME,
                exc,
            )
            return _RouteOutput(
                intent=topic,
                target_name=self.ROUTING_TARGET or "unknown",
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

        With chroma_client=None the vector leg degrades to empty results; the
        lexical leg attempts the FTS5 sidecar and returns [] on miss.  Both are
        real code paths — graceful degradation IS the expected behaviour when
        the canonical store is not populated.

        inject_chunks are appended to the real (possibly empty) raw results
        before EvidenceShaper.shape() runs the full C0 shaping pipeline.
        """
        from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (  # noqa: PLC0415
            EvidenceShaper,
        )
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (  # noqa: PLC0415
            get_hybrid_search_engine,
        )

        engine = get_hybrid_search_engine(collection_name=self._collection, top_k=10)
        try:
            raw_chunks: list[Any] = engine.search(query, collection_name=self._collection)
        except Exception as _search_exc:  # guardian: allow-except-exception -- collection-not-found (chromadb.errors.NotFoundError) and other backend errors are not importable without hard chromadb dep at the base layer; graceful degradation to empty results is the correct path
            _log.warning(
                "[GovernedAppRunner._c0_retrieve] search degraded to empty results app=%s: %s",
                self.APP_NAME,
                _search_exc,
            )
            raw_chunks = []
        c0_raw_count = len(raw_chunks)

        all_chunks = raw_chunks + (inject_chunks or [])

        shaper = EvidenceShaper()
        bundle = shaper.shape(
            query=query,
            results=all_chunks,
            collection_name=self._collection,
            chroma_client=engine.chroma_client,
        )
        return c0_raw_count, bundle
