"""
GovernedRfpRun — apps_rfp on the shared GovernedAppRunner substrate.

apps_rfp on the formal governed-app standard. Migration complete; status = GOVERNED.
Reuses the full L1 → L0 → C0 → L2 → L5 + L6 pipeline from the shared base;
only the query-construction one-liner and the record mapper are RFP-specific.

Contract:
  registry entry : apps_shared.integrations.app_registry.APP_REGISTRY["apps_rfp"]
  capability token: apps_rfp.governed_e2e.v1
  routing target  : rfp_proposal_assembly
  collection      : rfp_docs  (degrades gracefully when absent)
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from apps_rfp.types.rfp_types import RfpRequest
from apps_shared.integrations.governed_app_runner import (
    GovernedAppRunRecord,
    GovernedAppRunner,
    build_app_record,
)


# ---------------------------------------------------------------------------
# Frozen result record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GovernedRfpE2ERunRecord:
    """Sealed record of one apps_rfp governed execution pass.

    Mirrors GovernedExecE2ERunRecord — all substrate fields are inherited from
    GovernedAppRunRecord and surfaced here for a stable, inspectable API.
    """

    # ── substrate fields (mirrored from GovernedAppRunRecord) ────────────
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
    # ── RFP-specific context ─────────────────────────────────────────────
    industry: str
    architecture_posture: str
    problem_statement: str  # first 120 chars — sealed summary
    # ── Per-phase errors (W1 hardening — default "" preserves back-compat) ──
    l1_error: str = ""
    l0_error: str = ""
    c0_error: str = ""
    l2_error: str = ""
    l5_error: str = ""
    l6_error: str = ""
    hitl_error: str = ""
    # ── Inner-DAG HOP checkpoints (Wave 5 — plan apps-hop-substrate-four-apps-b4a2c9) ──
    hop_checkpoints: tuple[dict, ...] = ()
    hop_terminal_error: str = ""


# ---------------------------------------------------------------------------
# GovernedRfpRun
# ---------------------------------------------------------------------------


class GovernedRfpRun(GovernedAppRunner):
    """Governed runner for apps_rfp — AI Proposal / RFP Generator.

    Shared substrate: L1 query decomposition → L0 intent routing →
    C0 hybrid retrieval + evidence shaping → L2 execution chokepoint →
    L5 safety exit gate → L6 observability + eval packet ingestion.

    App-specific:
      - _build_query(): constructs retrieval query from RfpRequest fields
      - run_governed_e2e(): maps GovernedAppRunRecord → GovernedRfpE2ERunRecord
    """

    APP_NAME = "apps_rfp"
    CAPABILITY_TOKEN = "apps_rfp.governed_e2e.v1"
    ROUTING_TARGET = "rfp_proposal_assembly"
    ROUTING_KEYWORDS = [
        "rfp",
        "proposal",
        "procurement",
        "solution",
        "bid",
        "tender",
        "architecture",
        "implementation",
    ]

    # ------------------------------------------------------------------
    # Query construction
    # ------------------------------------------------------------------

    def _build_query(self, request: RfpRequest) -> str:
        """Construct C0 retrieval query from RfpRequest.

        Uses industry + truncated problem_statement so the query is
        semantically grounded in the RFP domain without being unbounded.
        """
        return f"RFP proposal: {request.industry} {request.problem_statement[:100]}"

    # ------------------------------------------------------------------
    # Governed E2E entry point
    # ------------------------------------------------------------------

    @traces_execute(layer="L3_ORCHESTRATION")
    def run_governed_e2e(
        self,
        request: RfpRequest,
        *,
        inject_chunks: list[Any] | None = None,
    ) -> GovernedRfpE2ERunRecord:
        """Run the full governed pipeline for an RFP proposal request.

        Parameters
        ----------
        request:
            Validated RfpRequest from the apps_rfp domain layer.
        inject_chunks:
            Optional well-formed HybridSearchResult chunks injected before
            C0 shaping.  Used by the proof harness for happy-path validation.
            Production callers pass None; real retrieval from ``rfp_docs`` is
            attempted first and degrades gracefully when absent.

        Returns
        -------
        GovernedRfpE2ERunRecord
            Frozen record capturing full substrate + RFP-domain context.
        """
        run_id = f"rfp-{request.trace_id or uuid4().hex[:12]}"
        query = self._build_query(request)

        core: GovernedAppRunRecord = self.run_governed_core(
            query,
            run_id=run_id,
            inject_chunks=inject_chunks,
        )

        # ── Inner-DAG HOP pipeline (Wave 5 — plan apps-hop-substrate-four-apps-b4a2c9) ──
        hop_payload = self._run_hop_pipeline(
            request=request,
            run_id=run_id,
            trace_id=request.trace_id or "",
        )

        # W5: build_app_record handles all substrate fields automatically.
        # Only RFP-specific fields are passed explicitly.
        return build_app_record(
            GovernedRfpE2ERunRecord, core,
            industry=request.industry,
            architecture_posture=request.architecture_posture,
            problem_statement=request.problem_statement[:120],
            hop_checkpoints=hop_payload["checkpoints"],
            hop_terminal_error=hop_payload["terminal_error"],
        )

    # ------------------------------------------------------------------
    # Inner-DAG driver (Wave 5 — plan apps-hop-substrate-four-apps-b4a2c9)
    # ------------------------------------------------------------------

    def _run_hop_pipeline(
        self,
        *,
        request: RfpRequest,
        run_id: str,
        trace_id: str,
    ) -> dict[str, Any]:
        """Execute the 3-stage apps_rfp HOP pipeline.

        Isolated helper so inner-DAG failures cannot take down substrate
        record assembly — mirror of apps_lic Wave 2.5 posture.
        """
        try:
            from apps_rfp.reasoning.RfpHopOrchestrator import (  # noqa: PLC0415
                RfpHopOrchestrator,
            )

            orchestrator = RfpHopOrchestrator()
            record = orchestrator.run(
                context={"rfp_request": request},
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

_emit_records_telemetry_event("p4", 'apps_rfp.integrations.governed_rfp_run', "module_loaded")
