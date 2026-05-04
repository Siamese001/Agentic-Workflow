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

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import dataclasses
import uuid
from dataclasses import dataclass, field
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
    # ── Inner pipeline checkpoints (Wave 5 — plan apps-hop-substrate-four-apps-b4a2c9) ──
    # Populated by ResearchHopOrchestrator after the outer substrate run.
    # Shape: tuple of dicts with keys stage_id/stage_name/status/duration_ms/error.
    # Default empty tuple preserves back-compat for callers that existed
    # before the inner pipeline was wired in (apps-hop-substrate-four-apps-b4a2c9).
    hop_checkpoints: tuple[dict, ...] = ()
    hop_terminal_error: str = ""
    # ── FEC v1.1 fields (apps-research-spine-deferred-followup-9c3e1a P1.1) ──
    # Populated from the inner hop pipeline when company_brief engine attaches
    # _depth_profile and _c0_bundle to the brief output.
    research_depth_profile: str = ""
    fec_run_context: dict = dataclasses.field(default_factory=dict)
    # ── L4 durable write path (apps-research-deferred-scope-b7e3d2 W3 / DS-3) ──
    # commit_receipt_ref from DurableWriteGateway.commit() after the run.
    # "PENDING" when the commit was never attempted (degraded path).
    # "BLOCKED" when UWG rejected the commit.
    # "COMMIT_FAILED" when the commit raised unexpectedly.
    l4_brief_committed: str = "PENDING"


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

    @traces_execute(layer="L3_ORCHESTRATION")
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

        # ── Inner pipeline checkpoints (Wave 5 — plan apps-hop-substrate-four-apps-b4a2c9) ──
        # Run the 3-stage apps_research inner pipeline after the substrate returns.
        # Isolated helper so inner pipeline failures cannot take down substrate
        # record assembly — mirror of apps_lic Wave 2.5 posture.
        hop_payload = self._run_hop_pipeline(
            request=request,
            run_id=run_id,
            trace_id=request.trace_id or "",
        )

        # W5: build_app_record handles all substrate fields automatically.
        # apps_research renames `query` -> `topic`; everything else is name-matched.
        fec_ctx = hop_payload.get("fec_context", {})
        record = build_app_record(
            GovernedE2ERunRecord, core,
            aliases={"topic": "query"},
            hop_checkpoints=hop_payload["checkpoints"],
            hop_terminal_error=hop_payload["terminal_error"],
            research_depth_profile=fec_ctx.get("research_depth_profile"),
            fec_run_context=fec_ctx,
        )

        # ── L4 durable write path (DS-3) — fail-soft ──────────────────────────
        # Commit a provenance record through UWG.  Import is lazy so that the
        # substrate path is never broken by import-time failures in the writer.
        try:
            from apps_research.integrations.research_brief_uwg_writer import (  # noqa: PLC0415
                commit_brief_record,
            )

            brief = commit_brief_record(record)
            # Return a new frozen record with the commit receipt attached.
            import dataclasses as _dc  # noqa: PLC0415
            record = _dc.replace(record, l4_brief_committed=brief.commit_receipt_ref)
        except (ImportError, AttributeError, TypeError, ValueError, RuntimeError):  # guardian: allow-log-and-swallow -- L4 UWG write is best-effort provenance; research pipeline must never break
            import logging as _logging  # noqa: PLC0415
            _logging.getLogger(__name__).warning(
                "GovernedResearchRun: L4 brief commit failed for run_id=%s",
                record.run_id,
                exc_info=True,
            )

        return record

    # ------------------------------------------------------------------
    # Inner pipeline driver (Wave 5 — plan apps-hop-substrate-four-apps-b4a2c9)
    # ------------------------------------------------------------------

    def _run_hop_pipeline(
        self,
        *,
        request: ResearchRequest,
        run_id: str,
        trace_id: str,
    ) -> dict[str, Any]:
        """Execute the 3-stage apps_research inner pipeline (R3_SIMPLE_GROUNDED_READ).

        Isolated helper so failure modes cannot take down the substrate
        record assembly — any exception inside the inner pipeline is
        captured and surfaced via ``hop_terminal_error`` instead of
        propagating.
        """
        try:
            # Lazy import keeps the substrate-only import surface unchanged
            # for existing consumers that don't exercise the inner pipeline.
            from apps_research.reasoning.ResearchHopOrchestrator import (  # noqa: PLC0415
                ResearchHopOrchestrator,
            )

            orchestrator = ResearchHopOrchestrator()
            record = orchestrator.run(
                context={"research_request": request},
                run_id=run_id,
                trace_id=trace_id,
            )
            checkpoints = tuple(
                {
                    "stage_id": cp.stage_id,
                    "stage_name": cp.stage_name,
                    "status": cp.status.value,
                    "duration_ms": cp.duration_ms,
                    "error": cp.error,
                }
                for cp in record.checkpoints
            )
            # Extract FEC v1.1 context from hop pipeline result
            fec_context: dict[str, Any] = {}
            try:
                final_ctx = getattr(record, "final_context", None) or {}
                brief = (final_ctx.get("company_brief") or {})
                if isinstance(brief, dict):
                    depth_profile = brief.get("_depth_profile")
                    c0_bundle = brief.get("_c0_bundle")
                    jd_context = brief.get("_jd_context")
                    if depth_profile:
                        fec_context["research_depth_profile"] = depth_profile
                    if c0_bundle:
                        fec_context["c0_bundle"] = c0_bundle
                    if jd_context:
                        fec_context["jd_context"] = jd_context
            except (AttributeError, TypeError, KeyError):
                pass
            return {
                "checkpoints": checkpoints,
                "terminal_error": record.terminal_error,
                "fec_context": fec_context,
            }
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError, ImportError) as exc:
            # guardian: allow-broad-exception -- inner-DAG failures must not
            # destroy the substrate record; surface as terminal_error and
            # continue to record assembly.
            return {
                "checkpoints": (),
                "terminal_error": f"hop_pipeline_error: {type(exc).__name__}: {exc}",
                "fec_context": {},
            }


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
