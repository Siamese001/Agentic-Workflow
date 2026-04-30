"""
True end-to-end governed runner — apps_research.

Lane trace (all substrates real; graceful degradation where store absent):

  ResearchRequest
    ↓ L1 query_planner.decompose_query(topic)         [intent decomposition → sub-queries]
    ↓ L0 AgenticRouter.route(topic)                   [route switching → research_assembly]
    ↓ C0 HybridSearchEngine.search()                  [grounded retrieval — degrades gracefully]
         EvidenceShaper.shape()                        [evidence shaping → EvidenceBundle]
    ↓ L2 authorize_and_execute()                      [chokepoint — guardrail + safety plane]
    ↓ evaluate_and_emit(bundle, ctx)                  [L5 exit gate + BUS T + L6 shadow eval]
      → ExitControlGate.evaluate()                    [L5]
      → emit_bundle_telemetry()                       [BUS T — EvidenceMetrics sealed]
      → ingest_eval_packet()                          [L6 — AsyncEvalPacket queued]
    ↓ GovernedE2ERunRecord (frozen)

No bypass.  No new packages.  No router redesign.  No collection rebuilds.
Common L1→L0→C0→L2→L5+L6 pipeline lives in GovernedAppRunner (apps_shared).
This module configures the runner for apps_research and translates the shared
GovernedAppRunRecord into the app-specific GovernedE2ERunRecord.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from apps_research.types.research_types import ResearchRequest
from apps_shared.integrations.governed_app_runner import (
    GovernedAppRunRecord,
    GovernedAppRunner,
    build_app_record,
)


# ---------------------------------------------------------------------------
# App-specific stage output types (kept for backward compatibility)
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
    error:            "" on success; aggregated phase-error message on failure.
    l2_executed:      True when authorize_and_execute() ran without error.

    Per-phase error fields (W1 hardening — ADG G1)
    ----------------------------------------------
    l1_error / l0_error / c0_error / l2_error / l5_error / l6_error / hitl_error:
        Empty on success; exception message on failure. Surfacing per-phase
        identity replaces the prior whole-pipeline broad catch in the substrate.
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
    l2_executed: bool = False
    # ── Per-phase errors (W1 hardening — default "" preserves back-compat) ──
    l1_error: str = ""
    l0_error: str = ""
    c0_error: str = ""
    l2_error: str = ""
    l5_error: str = ""
    l6_error: str = ""
    hitl_error: str = ""


# ---------------------------------------------------------------------------
# GovernedResearchRun — subclass of GovernedAppRunner
# ---------------------------------------------------------------------------


class GovernedResearchRun(GovernedAppRunner):
    """True E2E governed runner for apps_research.

    Configures the shared GovernedAppRunner for research artifact assembly
    and translates GovernedAppRunRecord → GovernedE2ERunRecord.

    Usage::

        runner = GovernedResearchRun(collection="process_docs")

        # Degraded path — real retrieval; degrades gracefully without ChromaDB
        rec = runner.run_governed_e2e(request)

        # Happy-path demonstration — inject well-formed HybridSearchResult chunks
        rec = runner.run_governed_e2e(request, inject_chunks=[...])

    ``inject_chunks`` are appended to the real (possibly empty) retrieval result
    BEFORE EvidenceShaper.shape() runs.  The C0 shaping pipeline is always real;
    only the source of raw chunks differs between happy and degraded paths.
    """

    APP_NAME = "apps_research"
    CAPABILITY_TOKEN = "apps_research.governed_e2e.v1"
    ROUTING_TARGET = "research_assembly"
    ROUTING_KEYWORDS = [
        "research",
        "analysis",
        "study",
        "compare",
        "trend",
        "governance",
        "agentic",
        "ai",
    ]

    def __init__(self, collection: str = "process_docs") -> None:
        super().__init__(collection=collection)

    def run_governed_e2e(
        self,
        request: ResearchRequest,
        *,
        inject_chunks: list[Any] | None = None,
    ) -> GovernedE2ERunRecord:
        """Run one governed end-to-end research pass.  Returns a frozen sealed record."""
        run_id = request.trace_id or str(uuid.uuid4())
        core: GovernedAppRunRecord = self.run_governed_core(
            query=request.topic,
            run_id=run_id,
            inject_chunks=inject_chunks,
        )
        # W5: build_app_record handles all substrate fields automatically.
        # apps_research renames `query` -> `topic`; everything else is name-matched.
        return build_app_record(
            GovernedE2ERunRecord, core,
            aliases={"topic": "query"},
        )


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_research.integrations.governed_research_run', "module_loaded")
