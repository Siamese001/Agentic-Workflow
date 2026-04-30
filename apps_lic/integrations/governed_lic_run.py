"""
GovernedLicRun — apps_lic on the shared GovernedAppRunner substrate.

apps_lic on the formal governed-app standard. Migration complete; status = GOVERNED.
Reuses the full L1 → L0 → C0 → L2 → L5 + L6 pipeline from the shared base;
only the query-construction one-liner and the record mapper are LIC-specific.

Contract:
  registry entry : apps_shared.integrations.app_registry.APP_REGISTRY["apps_lic"]
  capability token: apps_lic.governed_e2e.v1
  routing target  : lic_campaign_assembly
  collection      : lic_docs  (degrades gracefully when absent)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from apps_lic.types.lic_types import CampaignRequest
from apps_shared.integrations.governed_app_runner import (
    GovernedAppRunRecord,
    GovernedAppRunner,
    build_app_record,
)


# ---------------------------------------------------------------------------
# Frozen result record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GovernedLicE2ERunRecord:
    """Sealed record of one apps_lic governed execution pass.

    Mirrors GovernedRfpE2ERunRecord — all substrate fields are inherited from
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
    # ── LIC-specific context ─────────────────────────────────────────────
    campaign_id: str
    target_audience: str
    compliance_level: str
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


# ---------------------------------------------------------------------------
# GovernedLicRun
# ---------------------------------------------------------------------------


class GovernedLicRun(GovernedAppRunner):
    """Governed runner for apps_lic — Lead Intelligence & Campaign.

    Shared substrate: L1 query decomposition → L0 intent routing →
    C0 hybrid retrieval + evidence shaping → L2 execution chokepoint →
    L5 safety exit gate → L6 observability + eval packet ingestion.

    App-specific:
      - _build_query(): constructs retrieval query from CampaignRequest fields
      - run_governed_e2e(): maps GovernedAppRunRecord → GovernedLicE2ERunRecord
    """

    APP_NAME = "apps_lic"
    CAPABILITY_TOKEN = "apps_lic.governed_e2e.v1"
    ROUTING_TARGET = "lic_campaign_assembly"
    # W5 P5.1: opt-in to runtime HITL. Master env flag RUNTIME_HITL_ENABLED
    # must also be set for actual escalation; default YAML policy applies.
    HITL_ENABLED = True
    ROUTING_KEYWORDS = [
        "campaign",
        "outreach",
        "lead",
        "intelligence",
        "draft",
        "message",
        "email",
        "compliance",
    ]

    # ------------------------------------------------------------------
    # Query construction
    # ------------------------------------------------------------------

    def _build_query(self, request: CampaignRequest) -> str:
        """Construct C0 retrieval query from CampaignRequest.

        Uses target_audience + campaign name so the query is semantically
        grounded in the outreach campaign domain without being unbounded.
        """
        return f"lic campaign: {request.config.target_audience} {request.config.name}"

    # ------------------------------------------------------------------
    # Governed E2E entry point
    # ------------------------------------------------------------------

    def run_governed_e2e(
        self,
        request: CampaignRequest,
        *,
        inject_chunks: list[Any] | None = None,
    ) -> GovernedLicE2ERunRecord:
        """Run the full governed pipeline for a campaign outreach request.

        Parameters
        ----------
        request:
            Validated CampaignRequest from the apps_lic domain layer.
        inject_chunks:
            Optional well-formed HybridSearchResult chunks injected before
            C0 shaping.  Used by the proof harness for happy-path validation.
            Production callers pass None; real retrieval from ``lic_docs`` is
            attempted first and degrades gracefully when absent.

        Returns
        -------
        GovernedLicE2ERunRecord
            Frozen record capturing full substrate + LIC-domain context.
        """
        run_id = f"lic-{request.trace_id or request.campaign_id or uuid4().hex[:12]}"
        query = self._build_query(request)

        core: GovernedAppRunRecord = self.run_governed_core(
            query,
            run_id=run_id,
            inject_chunks=inject_chunks,
        )

        # W5: build_app_record handles all substrate fields automatically.
        # Only LIC-specific fields are passed explicitly.
        return build_app_record(
            GovernedLicE2ERunRecord, core,
            campaign_id=request.campaign_id,
            target_audience=request.config.target_audience,
            compliance_level=request.config.compliance_level,
        )
