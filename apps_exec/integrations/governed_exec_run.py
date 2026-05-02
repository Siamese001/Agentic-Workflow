"""
True end-to-end governed runner — apps_exec.

Lane trace (all substrates real; graceful degradation where store absent):

  ExecBriefRequest
    ↓ [query construction] audience + emphasis_areas → query string
    ↓ L1 query_planner.decompose_query(query)         [intent decomposition → sub-queries]
    ↓ L0 AgenticRouter.route(query)                   [route switching → exec_brief_assembly]
    ↓ C0 HybridSearchEngine.search()                  [grounded retrieval — degrades gracefully]
         EvidenceShaper.shape()                        [evidence shaping → EvidenceBundle]
    ↓ L2 authorize_and_execute()                      [chokepoint — guardrail + safety plane]
    ↓ evaluate_and_emit(bundle, ctx)                  [L5 exit gate + BUS T + L6 shadow eval]
      → ExitControlGate.evaluate()                    [L5]
      → emit_bundle_telemetry()                       [BUS T — EvidenceMetrics sealed]
      → ingest_eval_packet()                          [L6 — AsyncEvalPacket queued]
    ↓ GovernedExecE2ERunRecord (frozen)

No bypass.  No new packages.  No router redesign.  No collection rebuilds.
Common L1→L0→C0→L2→L5+L6 pipeline lives in GovernedAppRunner (apps_shared).
This module configures the runner for apps_exec and translates the shared
GovernedAppRunRecord into the app-specific GovernedExecE2ERunRecord.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import uuid
from dataclasses import dataclass
from typing import Any

from apps_exec.types.exec_types import ExecBriefRequest
from apps_shared.integrations.governed_app_runner import (
    GovernedAppRunRecord,
    GovernedAppRunner,
    build_app_record,
)


# ---------------------------------------------------------------------------
# Exec-specific run record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GovernedExecE2ERunRecord:
    """Sealed record of one governed executive-brief E2E run.

    Fields
    ------
    run_id:           Correlation key (= ExecBriefRequest.trace_id or UUID).
    audience:         Target audience persona (recruiter / cto / svp_eng / board / head_of_ai).
    emphasis_areas:   Emphasis areas from the original request.
    query:            Constructed query string fed through L1→L0→C0.
    l1_sub_queries:   Sub-queries produced by L1 query_planner.
    l1_fallback:      True when L1 gracefully fell back to the original query.
    l0_intent:        Intent label assigned by L0 router.
    l0_target:        Routing target chosen by L0 router.
    l0_confidence:    L0 routing confidence (0.0–1.0).
    l0_fallback:      True when L0 gracefully fell back.
    c0_raw_count:     Chunks from real retrieval (0 when store absent).
    c0_shaped_count:  Chunks after EvidenceShaper.shape() (incl. injected).
    c0_collection:    Collection queried.
    disposition:      WeakSupportDisposition.value.
    gate_disposition: ExitDisposition.value.
    grounded:         True when gate reports grounded_replayable=True.
    citation_count:   Citation anchors from the shaped bundle.
    support_coverage: Mean combined_score across ranked chunks.
    l6_ingested:      True when L6 ingest_eval_packet() was invoked.
    l2_executed:      True when authorize_and_execute() ran without error.
    error:            "" on success; exception message on failure.
    """

    run_id: str
    audience: str
    emphasis_areas: tuple[str, ...]
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
    # ── Per-phase errors (W1 hardening — default "" preserves back-compat) ──
    l1_error: str = ""
    l0_error: str = ""
    c0_error: str = ""
    l2_error: str = ""
    l5_error: str = ""
    l6_error: str = ""
    hitl_error: str = ""
    # ── Runtime HITL (W5) — threaded from GovernedAppRunRecord ───────────
    hitl_action: str = "none"
    hitl_class: str = ""
    hitl_ledger_id: str = ""
    hitl_enabled: bool = False
    # ── Inner-DAG HOP checkpoints (Wave 5 — plan apps-hop-substrate-four-apps-b4a2c9) ──
    hop_checkpoints: tuple[dict, ...] = ()
    hop_terminal_error: str = ""


# ---------------------------------------------------------------------------
# GovernedExecRun — subclass of GovernedAppRunner
# ---------------------------------------------------------------------------


class GovernedExecRun(GovernedAppRunner):
    """True E2E governed runner for apps_exec (executive brief generation).

    Configures the shared GovernedAppRunner for executive brief assembly and
    translates GovernedAppRunRecord → GovernedExecE2ERunRecord.

    Usage::

        runner = GovernedExecRun(collection="exec_docs")

        # Degraded path — real retrieval; degrades gracefully without store
        rec = runner.run_governed_e2e(request)

        # Happy-path demonstration — inject well-formed HybridSearchResult chunks
        rec = runner.run_governed_e2e(request, inject_chunks=[...])
    """

    APP_NAME = "apps_exec"
    CAPABILITY_TOKEN = "apps_exec.governed_e2e.v1"
    ROUTING_TARGET = "exec_brief_assembly"
    # W5 P5.3: opt-in to runtime HITL. Master env flag RUNTIME_HITL_ENABLED
    # must also be set for actual escalation to occur.
    HITL_ENABLED = True
    ROUTING_KEYWORDS = [
        "brief",
        "executive",
        "capabilities",
        "board",
        "technical",
        "governance",
        "architecture",
        "platform",
    ]

    def __init__(self, collection: str = "exec_docs") -> None:
        super().__init__(collection=collection)

    @traces_execute(layer="L3_ORCHESTRATION")
    def run_governed_e2e(
        self,
        request: ExecBriefRequest,
        *,
        inject_chunks: list[Any] | None = None,
    ) -> GovernedExecE2ERunRecord:
        """Run one governed end-to-end exec-brief pass.  Returns a frozen sealed record."""
        audience: str = (
            request.audience.value if hasattr(request.audience, "value") else str(request.audience)
        )
        emphasis_areas: list[str] = list(request.emphasis_areas or [])
        emphasis_str = " ".join(emphasis_areas) if emphasis_areas else "governance architecture"
        query = f"{audience} executive brief: {emphasis_str}"

        run_id = request.trace_id or str(uuid.uuid4())
        core: GovernedAppRunRecord = self.run_governed_core(
            query=query,
            run_id=run_id,
            inject_chunks=inject_chunks,
        )

        # ── Inner-DAG HOP pipeline (Wave 5 — plan apps-hop-substrate-four-apps-b4a2c9) ──
        hop_payload = self._run_hop_pipeline(
            request=request,
            run_id=run_id,
            trace_id=request.trace_id or "",
        )

        # W5: build_app_record handles all 22 substrate fields automatically.
        # Only app-specific fields (audience, emphasis_areas) are passed explicitly.
        return build_app_record(
            GovernedExecE2ERunRecord, core,
            audience=audience,
            emphasis_areas=tuple(emphasis_areas),
            hop_checkpoints=hop_payload["checkpoints"],
            hop_terminal_error=hop_payload["terminal_error"],
        )

    # ------------------------------------------------------------------
    # Inner-DAG driver (Wave 5 — plan apps-hop-substrate-four-apps-b4a2c9)
    # ------------------------------------------------------------------

    def _run_hop_pipeline(
        self,
        *,
        request: ExecBriefRequest,
        run_id: str,
        trace_id: str,
    ) -> dict[str, Any]:
        """Execute the 4-stage apps_exec HOP pipeline.

        Isolated helper so inner-DAG failures cannot take down substrate
        record assembly — mirror of apps_lic Wave 2.5 posture.
        """
        try:
            from apps_exec.reasoning.ExecHopOrchestrator import (  # noqa: PLC0415
                ExecHopOrchestrator,
            )

            orchestrator = ExecHopOrchestrator()
            record = orchestrator.run(
                context={"exec_request": request},
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
            return {
                "checkpoints": checkpoints,
                "terminal_error": record.terminal_error,
            }
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError, ImportError) as exc:
            # guardian: allow-broad-exception -- inner-DAG failures must not
            # destroy the substrate record; surface as terminal_error.
            return {
                "checkpoints": (),
                "terminal_error": f"hop_pipeline_error: {type(exc).__name__}: {exc}",
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

_emit_records_telemetry_event("p4", 'apps_exec.integrations.governed_exec_run', "module_loaded")
