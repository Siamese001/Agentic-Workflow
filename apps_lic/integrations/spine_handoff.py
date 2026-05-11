"""apps_lic spine-handoff -- canonical contract surface and thin run delegate.

Mirrors the apps_research W9 and apps_exec W10 patterns. Surfaces the
canonical contract chain (per
``docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md``) directly from
``agentic_core`` so the runtime-mode scanner
(``tools.analysis.apps_spine_coverage``) can verify the delegation
evidence statically. Today these contracts flow into apps_lic
**transitively** through
``apps_shared.integrations.governed_app_runner.GovernedAppRunner``;
this module makes the surface **directly visible** without changing
runtime behavior.

This module is STATIC EVIDENCE only. It does NOT:
  - construct any of the contracts at runtime;
  - rewrite or replace ``GovernedLicRun.run_governed_e2e()``;
  - rewrite ``EnterpriseLicOrchestrator.execute_workflow``;
  - add a ``CommitRequest`` (apps_lic has no durable-write surface);
  - add a ``StateDiffCandidate``;
  - claim a compliance-log durable write;
  - bypass ``GovernedAppRunner``;
  - copy the apps_qna ``build_time_compiler + ValidatedRequest envelope`` pattern;
  - claim runtime certification.

HITL posture (informational): ``GovernedLicRun.HITL_ENABLED = True``.
That gates the spine's runtime HITL escalation path for
compliance-sensitive review of message drafts; it is NOT evidence of
a durable-write surface and does not change the route shape. The
pre-migration audit found ZERO matches in apps_lic/ for
``CommitRequest``, ``commit_request``, ``StateDiffCandidate``,
``proposed_state_diff``, ``MutationIntent``, ``durable_write``,
``write_gateway``, ``compliance_log``, or ``send_queue``.

Final L0 routing model (plan apps-lic-u0-runtime-package-complete-f8e2a1):

  R4_MANAGED_DRAFT               -- fresh context; L3 HOP draft workflow
  R3R4_MANAGED_RESEARCH_THEN_DRAFT -- stale/missing context; apps_research
                                    support then HOP draft workflow
  R5_FALLBACK                    -- no valid context; fail-closed / abstain

The canonical contract chain (8 contracts):

    ValidatedRequest         intake -- U0 ingress (carries runtime_customization_package)
    L1PlanContract           L1 typed reasoning output
    RouteContract            L0 deterministic instruction to C0
    RetrievalPlan            C0.1 bounded retrieval plan
    FinalEvidenceContract    C0 output to PA
    CompiledPromptArtifact   PA -> L2 sealed prompt (PromptEnvelope is
                             an accepted equivalent per
                             CONTRACT_EQUIVALENT_GROUPS)
    SealedArtifact           L2 sealed output of model execution
    ExitReviewPacket         5.1 normalized exit-review surface

Constitutional alignment:
  - §3 anti-bypass: writes still flow through UWG via GovernedAppRunner.
  - §22 graph-layer evidence: the 8 imports introduce direct L0/L1/L2/L3/L5
    edges the scanner sees without walking apps_shared.
  - §29 closed-loop: the GovernedLicRun pipeline keeps emitting
    ROUTER_DECISION + ledger events as it does today; this module adds
    no new emissions.

W5 wiring (plan apps-lic-u0-runtime-package-complete-f8e2a1, P5.2/P5.4):
  - Stale legacy route name removed; final L0 routing model applied (R4/R3R4/R5).
  - ``ValidatedRequest.app_payload`` carries the full
    ``runtime_customization_package``; this module preserves it through the
    ``run_lic_via_spine`` delegate without extraction or mutation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

# ---------------------------------------------------------------------------
# R3 contract chain -- direct imports from agentic_core.
# These imports are the load-bearing static evidence the scanner
# (tools.analysis.apps_spine_coverage) consumes. Do NOT remove or
# replace with local re-imports / aliases.
#
# Canonical paths (matched to apps_research W9 and apps_exec W10).
#
# NOTE: CommitRequest is INTENTIONALLY NOT IMPORTED. apps_lic has no
# durable-write surface (pre-migration audit proved zero matches for
# commit/write primitives). Importing CommitRequest would be contract theater.
# ---------------------------------------------------------------------------
from agentic_core.L0_routing.intake.validated_request import ValidatedRequest
from agentic_core.L1_cognition.types.plan_contract_types import L1PlanContract
from agentic_core.L0_routing.c0_retrieval.route_contract import RouteContract
from agentic_core.L0_routing.c0_retrieval.plan import RetrievalPlan
from agentic_core.L0_routing.c0_retrieval.final_contract import (
    FinalEvidenceContract,
)
from agentic_core.L2_execution.reasoning.compiled_artifact import (
    CompiledPromptArtifact,
)
from agentic_core.L5_safety.eval_spine.exit_eval import SealedArtifact
from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket

if TYPE_CHECKING:  # pragma: no cover -- type-only imports
    from apps_lic.integrations.governed_lic_run import (
        GovernedLicE2ERunRecord,
        GovernedLicRun,
    )
    from apps_lic.types.lic_types import CampaignRequest

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Inspectable surface
# ---------------------------------------------------------------------------

CONTRACT_SURFACE: Mapping[str, type] = {
    "ValidatedRequest": ValidatedRequest,
    "L1PlanContract": L1PlanContract,
    "RouteContract": RouteContract,
    "RetrievalPlan": RetrievalPlan,
    "FinalEvidenceContract": FinalEvidenceContract,
    "CompiledPromptArtifact": CompiledPromptArtifact,
    "SealedArtifact": SealedArtifact,
    "ExitReviewPacket": ExitReviewPacket,
}
"""The 8 canonical contract types apps_lic delegates through.

Declarative mapping. Importing this module brings the eight contract
types into namespace; the values are the imported classes themselves.
``CommitRequest`` is intentionally absent -- apps_lic has no
durable-write surface.
"""

# Legacy alias only.  Does NOT represent an active R3 route.
# The stale legacy route name was removed in W5 (plan
# apps-lic-u0-runtime-package-complete-f8e2a1, P5.4).
# New callers must use CONTRACT_SURFACE.
LEGACY_CONTRACT_SURFACE_ALIAS: Mapping[str, type] = CONTRACT_SURFACE
R3_CONTRACT_SURFACE: Mapping[str, type] = CONTRACT_SURFACE  # kept for import compatibility only

R3_REQUIRED_CONTRACT_NAMES: tuple[str, ...] = tuple(CONTRACT_SURFACE.keys())
"""Stable ordering of the 8 contract names (matches manifest order)."""


def validate_lic_r3_contract_surface() -> dict[str, bool]:
    """Return per-contract availability map.

    Every entry is True when this module imports cleanly (the imports
    above are at module level, so a failed import would prevent this
    function from being callable in the first place). The function
    exists as a programmatic affirmation surface for tests and ledger
    inspection -- it does NOT instantiate any contract.
    """
    return {
        name: cls is not None for name, cls in CONTRACT_SURFACE.items()
    }


@dataclass(frozen=True)
class R3HandoffMetadata:
    """Inspection-only metadata describing one apps_lic handoff.

    Returned by :func:`build_lic_r3_handoff_metadata`. Carries the
    run_id, campaign_id, target_audience, compliance_level, route
    type, and a frozen tuple of contract names exposed by this
    module. Intended for ledger introspection / test fixtures; NOT
    used on the hot path of GovernedLicRun.

    HITL posture is documented at module level (HITL_ENABLED=True);
    the metadata does not redundantly carry that flag because it is
    a property of the runner, not of an individual handoff.
    """

    run_id: str
    campaign_id: str
    target_audience: str
    compliance_level: str
    route_type: str
    contract_surface: tuple[str, ...]


def build_lic_r3_handoff_metadata(
    request: "CampaignRequest",
) -> R3HandoffMetadata:
    """Build inspection-only metadata for an LIC outreach-campaign request.

    No contract is constructed. The returned object simply captures
    ``request.trace_id`` (or empty string), the campaign_id,
    target_audience, compliance_level, the route type, and the static
    contract surface this module exposes. Useful for tests asserting
    the surface is wired without exercising the full GovernedLicRun
    pipeline.
    """
    trace_id = getattr(request, "trace_id", "") or ""
    campaign_id = getattr(request, "campaign_id", "") or ""
    config = getattr(request, "config", None)
    target_audience = getattr(config, "target_audience", "") or "" if config else ""
    compliance_level = getattr(config, "compliance_level", "") or "" if config else ""
    return R3HandoffMetadata(
        run_id=trace_id,
        campaign_id=str(campaign_id),
        target_audience=str(target_audience),
        compliance_level=str(compliance_level),
        route_type="R4_MANAGED_DRAFT",
        contract_surface=R3_REQUIRED_CONTRACT_NAMES,
    )


# ---------------------------------------------------------------------------
# Thin delegate -- behavior unchanged
# ---------------------------------------------------------------------------


def run_lic_via_spine(
    request: "CampaignRequest",
    *,
    runner: "GovernedLicRun | None" = None,
    inject_chunks: list[Any] | None = None,
) -> "GovernedLicE2ERunRecord":
    """Delegate unchanged to GovernedLicRun.run_governed_e2e().

    Name-only seam that records the handoff without altering behavior.
    apps_lic's pipeline today already routes every request through
    GovernedAppRunner -> L1 -> L0 -> C0 -> L2 -> L5+L6; this wrapper
    does not change that.

    Args:
        request: typed CampaignRequest (campaign_id + config + optional trace_id).
        runner: optional pre-constructed GovernedLicRun. When None,
            a default instance is created (collection="lic_docs").
        inject_chunks: optional well-formed HybridSearchResult chunks for
            happy-path proof harnesses; production callers pass None.

    Returns:
        GovernedLicE2ERunRecord -- the existing frozen sealed record from
        GovernedLicRun.run_governed_e2e().

    Side effects:
        Logs an INFO line tagging the handoff with the request's
        trace_id + campaign_id. NO ledger emission. NO contract
        construction. NO ValidatedRequest envelope is built (that is
        the apps_qna build_time_compiler shape, which does NOT apply
        here). NO CommitRequest is built (apps_lic has no durable-write
        surface).

    Notes:
        Constitutional invariants are upheld by the underlying
        GovernedLicRun substrate; this wrapper adds no governance.
        The eight R3 contracts are surfaced at module load via the
        imports above; this function does not need to reference them
        directly to pass the static-evidence test.
    """
    # Local import keeps this module side-effect-free at import time.
    from apps_lic.integrations.governed_lic_run import GovernedLicRun

    if runner is None:
        runner = GovernedLicRun(collection="lic_docs")

    trace_id = getattr(request, "trace_id", "") or ""
    campaign_id = getattr(request, "campaign_id", "") or ""
    _log.info(
        "spine_handoff: lic request trace_id=%s campaign_id=%s -> "
        "GovernedLicRun.run_governed_e2e",
        trace_id,
        campaign_id,
    )
    return runner.run_governed_e2e(request, inject_chunks=inject_chunks)


__all__ = [
    "CONTRACT_SURFACE",
    "R3_CONTRACT_SURFACE",  # backward-compatible alias
    "R3_REQUIRED_CONTRACT_NAMES",
    "R3HandoffMetadata",
    "build_lic_r3_handoff_metadata",
    "run_lic_via_spine",
    "validate_lic_r3_contract_surface",
    # Re-exports of the 8 contract types.
    "CompiledPromptArtifact",
    "ExitReviewPacket",
    "FinalEvidenceContract",
    "L1PlanContract",
    "RetrievalPlan",
    "RouteContract",
    "SealedArtifact",
    "ValidatedRequest",
]
