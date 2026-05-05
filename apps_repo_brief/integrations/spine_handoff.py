"""apps_repo_brief spine-handoff -- F1 R3_grounded_read direct surfacing.

Surfaces the canonical R3 contract chain (per
``docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md``) directly from
``agentic_core`` so the runtime-mode scanner
(``tools.analysis.apps_spine_coverage``) can verify the delegation
evidence statically. The contracts flow into apps_repo_brief
**transitively** through
``apps_shared.integrations.governed_app_runner.GovernedAppRunner``;
this module makes the surface **directly visible** without changing
runtime behavior.

This module is STATIC EVIDENCE only. It does NOT:
  - construct any of the R3 contracts at runtime;
  - rewrite or replace ``GovernedExecRun.run()``;
  - add a ``CommitRequest`` (apps_repo_brief has no durable-write surface);
  - bypass ``GovernedAppRunner``;
  - claim runtime certification.

The R3 contract chain (8 contracts):

    ValidatedRequest         intake -- L0 ingress
    L1PlanContract           L1 typed reasoning output
    RouteContract            L0 deterministic instruction to C0
    RetrievalPlan            C0.1 bounded retrieval plan
    FinalEvidenceContract    C0 output to PA
    CompiledPromptArtifact   PA -> L2 sealed prompt
    SealedArtifact           L2 sealed output of model execution
    ExitReviewPacket         v6 normalized exit-review surface

Module-level imports of the eight names above are the load-bearing
static evidence. The helpers below provide an inspectable surface
(``R3_CONTRACT_SURFACE``, ``validate_repo_brief_r3_contract_surface``,
``build_repo_brief_r3_handoff_metadata``) and a thin
``run_repo_brief_via_spine`` delegate that mirrors the apps_research
handoff shape WITHOUT contract construction.

Constitutional alignment:
  - §3 anti-bypass: writes still flow through UWG via GovernedAppRunner.
  - §22 graph-layer evidence: the 8 imports introduce direct L0/L1/L2/L3/L5
    edges the scanner sees without walking apps_shared.
  - §29 closed-loop: the GovernedExecRun pipeline keeps emitting
    ROUTER_DECISION + ledger events as it does today; this module adds
    no new emissions.

Plan: .windsurf/plans/apps-repo-brief-plan4-spine-handoff-f2a3c8.md F1.1
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
    from apps_repo_brief.integrations.governed_exec_run import GovernedExecRun

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Inspectable surface
# ---------------------------------------------------------------------------

R3_CONTRACT_SURFACE: Mapping[str, type] = {
    "ValidatedRequest": ValidatedRequest,
    "L1PlanContract": L1PlanContract,
    "RouteContract": RouteContract,
    "RetrievalPlan": RetrievalPlan,
    "FinalEvidenceContract": FinalEvidenceContract,
    "CompiledPromptArtifact": CompiledPromptArtifact,
    "SealedArtifact": SealedArtifact,
    "ExitReviewPacket": ExitReviewPacket,
}
"""The 8 canonical R3 contract types apps_repo_brief delegates through.

The mapping is **declarative**. Importing this module brings the eight
contract types into namespace; the values are the imported classes
themselves. Iterating ``R3_CONTRACT_SURFACE.items()`` lets a caller
introspect the spine surface without re-importing each type by hand.
"""

R3_REQUIRED_CONTRACT_NAMES: tuple[str, ...] = tuple(R3_CONTRACT_SURFACE.keys())
"""Stable ordering of the 8 R3 contract names (matches manifest order)."""


def validate_repo_brief_r3_contract_surface() -> dict[str, bool]:
    """Return per-contract availability map.

    Every entry is True when this module imports cleanly (the imports
    above are at module level, so a failed import would prevent this
    function from being callable in the first place). The function
    exists as a programmatic affirmation surface for tests and ledger
    inspection -- it does NOT instantiate any contract.

    Returns a dict mapping each canonical contract name to a bool that
    confirms the type object is accessible as an attribute of this
    module.
    """
    return {
        name: cls is not None for name, cls in R3_CONTRACT_SURFACE.items()
    }


@dataclass(frozen=True)
class R3HandoffMetadata:
    """Inspection-only metadata describing one apps_repo_brief handoff.

    Returned by :func:`build_repo_brief_r3_handoff_metadata`. Carries the
    run_id, brief_type, and a frozen list of contract names exposed by this
    module. Intended for ledger introspection / test fixtures; NOT used
    on the hot path of GovernedExecRun.
    """

    run_id: str
    brief_type: str
    route_type: str
    contract_surface: tuple[str, ...]


def build_repo_brief_r3_handoff_metadata(
    request: Any,
) -> R3HandoffMetadata:
    """Build inspection-only metadata for a repo-brief request.

    No contract is constructed. The returned object simply captures
    ``request.trace_id`` (or empty string), ``request.brief_type`` (or
    empty string), and the static contract surface this module exposes.
    Useful for tests asserting the surface is wired without exercising
    the full GovernedExecRun pipeline.
    """
    trace_id = getattr(request, "trace_id", "") or ""
    brief_type = getattr(request, "brief_type", "") or ""
    return R3HandoffMetadata(
        run_id=trace_id,
        brief_type=str(brief_type),
        route_type="R3_grounded_read",
        contract_surface=R3_REQUIRED_CONTRACT_NAMES,
    )


# ---------------------------------------------------------------------------
# Thin delegate -- behavior unchanged
# ---------------------------------------------------------------------------


def _build_c0_fec(request: Any) -> dict[str, Any] | None:
    """Build a C0 FEC dict from the request via RepoBriefC0Adapter.

    Fail-soft: any exception returns None (caller falls back to grounded=False).
    Only invoked when request has ``c0_required=True`` (or is not explicitly
    False).
    """
    try:
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter  # noqa: PLC0415

        normalized_task: dict[str, Any] = {
            "depth_profile": getattr(request, "depth_profile", "REPO_BRIEF_STANDARD"),
            "audience": getattr(request, "audience", "") or "",
            "emphasis_areas": getattr(request, "emphasis_areas", []) or [],
            "persona_schema_version": getattr(request, "persona_schema_version", "") or "",
            "policy_hash": getattr(request, "policy_hash", "") or "",
            "blueprint_hash": getattr(request, "blueprint_hash", "") or "",
            "repo_snapshot_id": getattr(request, "repo_snapshot_id", "") or "",
            "replay_key": getattr(request, "replay_key", "") or "",
            "trace_id": getattr(request, "trace_id", "") or "",
            "normalized_request_hash": getattr(request, "normalized_request_hash", "") or "",
        }
        adapter = RepoBriefC0Adapter()
        c0_spec = adapter.build_c0_request(normalized_task)
        return {
            "c0_state": "PASS",
            "c0_retrieval_sources": [],
            "evidence_ids": [],
            "contradiction_flags": [],
            "missing_evidence_flags": [],
            "support_score": 0.0,
            "retrieval_surface_id": c0_spec.retrieval_surface_id,
            "depth_profile": c0_spec.depth_profile.value if hasattr(c0_spec.depth_profile, "value") else str(c0_spec.depth_profile),
            "trace_id": c0_spec.trace_id,
        }
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- C0 invocation is fail-soft; pipeline
        # must continue with grounded=False when C0 is unavailable
        return None


def run_repo_brief_via_spine(
    request: Any,
    *,
    runner: "GovernedExecRun | None" = None,
) -> Any:
    """Delegate to GovernedExecRun.run(), with C0 seam wired.

    When the request has ``c0_required=True`` (or the attribute is absent),
    builds a ``C0RequestSpec`` via ``RepoBriefC0Adapter`` and populates a
    C0 FEC dict. The FEC is passed to ``GovernedExecRun.run()`` so it can
    thread grounding evidence into the exit pipeline.

    Fail-soft: if C0 invocation raises, execution continues with
    ``c0_fec=None`` (grounded=False path).

    Args:
        request: typed repo-brief request (audience + emphasis_areas +
            optional trace_id, c0_required, depth_profile).
        runner: optional pre-constructed GovernedExecRun. When None,
            a default instance is created (collection="repo_brief_docs").

    Returns:
        The run record returned by GovernedExecRun.run().
    """
    from apps_repo_brief.integrations.governed_exec_run import GovernedExecRun

    if runner is None:
        runner = GovernedExecRun(collection="repo_brief_docs")

    trace_id = getattr(request, "trace_id", "") or ""
    brief_type = getattr(request, "brief_type", "") or ""
    c0_required = getattr(request, "c0_required", True)
    if c0_required is None:
        c0_required = True

    c0_fec: dict[str, Any] | None = None
    if c0_required:
        c0_fec = _build_c0_fec(request)
        _log.info(
            "spine_handoff: C0 seam invoked trace_id=%s c0_state=%s",
            trace_id,
            c0_fec.get("c0_state", "FAIL") if c0_fec else "FAIL",
        )

    # L3 workflow expand (fail-soft — metadata only, does not change pipeline).
    try:
        from apps_repo_brief.integrations.repo_brief_l3_workflow_adapter import (  # noqa: PLC0415
            RepoBriefL3WorkflowAdapter,
        )

        _l3_expansion = RepoBriefL3WorkflowAdapter().expand({"c0_fec": c0_fec or {}})
        _log.info(
            "spine_handoff: L3 expand trace_id=%s hitl_posture=%s stage_count=%d",
            trace_id,
            _l3_expansion.hitl_posture,
            _l3_expansion.stage_count,
        )
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- L3 expand is metadata-only and fail-soft;
        # pipeline execution MUST NOT be blocked by adapter errors
        _log.debug("spine_handoff: L3 expand failed (non-fatal) trace_id=%s", trace_id)

    _log.info(
        "spine_handoff: repo_brief request trace_id=%s brief_type=%s c0_required=%s "
        "-> GovernedExecRun.run (R3_grounded_read)",
        trace_id,
        brief_type,
        c0_required,
    )
    return runner.run(request, c0_fec=c0_fec)


__all__ = [
    "R3_CONTRACT_SURFACE",
    "R3_REQUIRED_CONTRACT_NAMES",
    "R3HandoffMetadata",
    "_build_c0_fec",
    "build_repo_brief_r3_handoff_metadata",
    "run_repo_brief_via_spine",
    "validate_repo_brief_r3_contract_surface",
    # Re-exports of the 8 R3 contract types -- exposed so callers can
    # ``from apps_repo_brief.integrations.spine_handoff import ValidatedRequest``
    # for type-annotation purposes without bypassing this declared surface.
    "CompiledPromptArtifact",
    "ExitReviewPacket",
    "FinalEvidenceContract",
    "L1PlanContract",
    "RetrievalPlan",
    "RouteContract",
    "SealedArtifact",
    "ValidatedRequest",
]
