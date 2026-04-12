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

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from apps_rfp.types.rfp_types import RfpRequest
from apps_shared.integrations.governed_app_runner import GovernedAppRunRecord, GovernedAppRunner


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

        return GovernedRfpE2ERunRecord(
            # substrate
            run_id=core.run_id,
            app_name=core.app_name,
            query=core.query,
            l1_sub_queries=core.l1_sub_queries,
            l1_fallback=core.l1_fallback,
            l0_intent=core.l0_intent,
            l0_target=core.l0_target,
            l0_confidence=core.l0_confidence,
            l0_fallback=core.l0_fallback,
            c0_raw_count=core.c0_raw_count,
            c0_shaped_count=core.c0_shaped_count,
            c0_collection=core.c0_collection,
            disposition=core.disposition,
            gate_disposition=core.gate_disposition,
            grounded=core.grounded,
            citation_count=core.citation_count,
            support_coverage=core.support_coverage,
            l6_ingested=core.l6_ingested,
            l2_executed=core.l2_executed,
            error=core.error,
            # RFP-specific
            industry=request.industry,
            architecture_posture=request.architecture_posture,
            problem_statement=request.problem_statement[:120],
        )
