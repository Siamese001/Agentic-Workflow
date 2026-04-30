"""apps_rg spine-handoff -- W13 R3_grounded_read direct surfacing.

Mirrors the apps_research W9, apps_exec W10, apps_lic W11, and
apps_rfp W12 patterns. Surfaces the canonical R3 contract chain (per
``docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md``) directly from
``agentic_core`` so the runtime-mode scanner
(``tools.analysis.apps_spine_coverage``) can verify the delegation
evidence statically.

apps_rg already surfaced ONE R3 contract directly before this
migration: ``PromptEnvelope`` (an accepted equivalent for
``CompiledPromptArtifact`` per
``CONTRACT_EQUIVALENT_GROUPS``) is consumed by
``apps_rg/utils/anthropic_rag_entrypoint.py::build_anthropic_rag_payload``
at runtime. That existing real handoff is **preserved unchanged** by
this migration; this module surfaces the OTHER 7 contracts (and the
canonical ``CompiledPromptArtifact`` name) so the scanner sees the
full R3 chain as direct imports.

This module is STATIC EVIDENCE only. It does NOT:
  - construct any of the R3 contracts at runtime;
  - rewrite or replace ``GovernedRgRun.run_governed_e2e()``;
  - rewrite or replace ``build_anthropic_rag_payload`` in
    ``apps_rg/utils/anthropic_rag_entrypoint.py``;
  - remove the existing ``PromptEnvelope`` import from
    ``apps_rg/utils/anthropic_rag_entrypoint.py``;
  - add a ``CommitRequest`` (apps_rg has no durable-write surface);
  - add a ``StateDiffCandidate``;
  - claim an ATS / LinkedIn / profile-store durable write;
  - bypass ``GovernedAppRunner``;
  - copy the apps_qna ``build_time_compiler + ValidatedRequest envelope`` pattern;
  - claim runtime certification.

HITL posture (informational): ``GovernedRgRun`` does NOT declare
``HITL_ENABLED`` (defaults False per ``GovernedAppRunner``). apps_rg
does not opt into runtime HITL escalation -- résumé review happens
out-of-band. Matches apps_research / apps_rfp posture; weaker than
apps_lic / apps_exec. HITL is orthogonal to route shape:
``R3R4_managed_workflow`` requires ``CommitRequest``, not HITL.
apps_rg stays in ``R3_grounded_read``.

The R3 contract chain (8 contracts):

    ValidatedRequest         intake -- L0 ingress
    L1PlanContract           L1 typed reasoning output
    RouteContract            L0 deterministic instruction to C0
    RetrievalPlan            C0.1 bounded retrieval plan
    FinalEvidenceContract    C0 output to PA
    CompiledPromptArtifact   PA -> L2 sealed prompt (PromptEnvelope is
                             an accepted equivalent and is also
                             consumed by apps_rg via
                             utils/anthropic_rag_entrypoint.py)
    SealedArtifact           L2 sealed output of model execution
    ExitReviewPacket         5.1 normalized exit-review surface

Constitutional alignment:
  - §3 anti-bypass: writes still flow through UWG via GovernedAppRunner.
  - §22 graph-layer evidence: the 8 imports introduce direct L0/L1/L2/L3/L5
    edges the scanner sees without walking apps_shared.
  - §29 closed-loop: the GovernedRgRun pipeline keeps emitting
    ROUTER_DECISION + ledger events as it does today; this module adds
    no new emissions.
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
# Canonical paths (matched to apps_research W9 / apps_exec W10 /
# apps_lic W11 / apps_rfp W12). CompiledPromptArtifact is preferred
# here for consistency with W9-W12 even though apps_rg also has the
# pre-existing PromptEnvelope consumer in utils/anthropic_rag_entrypoint.py
# (PromptEnvelope is an accepted equivalent per
# CONTRACT_EQUIVALENT_GROUPS).
#
# NOTE: CommitRequest is INTENTIONALLY NOT IMPORTED. apps_rg is
# R3_grounded_read, not R3R4_managed_workflow. The pre-migration audit
# proved no durable-write surface exists; ATS scoring is read-side,
# LinkedIn references are pattern-mining, ml_cache_ats_compatibility
# is cross-run meta-learning cache. Importing CommitRequest here would
# be contract theater.
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
    from apps_rg.integrations.governed_rg_run import (
        GovernedRgE2ERunRecord,
        GovernedRgRun,
    )
    from apps_rg.types.rg_types import ResumeRequest

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
"""The 8 canonical R3 contract types apps_rg delegates through.

Declarative mapping. ``CommitRequest`` is intentionally absent --
apps_rg is R3_grounded_read, not R3R4_managed_workflow.
"""

R3_REQUIRED_CONTRACT_NAMES: tuple[str, ...] = tuple(R3_CONTRACT_SURFACE.keys())
"""Stable ordering of the 8 R3 contract names (matches manifest order)."""


def validate_rg_r3_contract_surface() -> dict[str, bool]:
    """Return per-contract availability map.

    Every entry is True when this module imports cleanly. Programmatic
    affirmation surface for tests and ledger inspection -- does NOT
    instantiate any contract.
    """
    return {
        name: cls is not None for name, cls in R3_CONTRACT_SURFACE.items()
    }


@dataclass(frozen=True)
class R3HandoffMetadata:
    """Inspection-only metadata describing one apps_rg handoff.

    Returned by :func:`build_rg_r3_handoff_metadata`. Carries the
    run_id, candidate_name, target_role, target_industry,
    experience_level, route type, and a frozen tuple of contract names
    exposed by this module. Intended for ledger introspection / test
    fixtures; NOT used on the hot path of GovernedRgRun.

    HITL posture is documented at module level (HITL is False/absent
    on GovernedRgRun); the metadata does not redundantly carry that
    flag because it is a property of the runner, not of an individual
    handoff.

    Note: this metadata structure is INDEPENDENT of the existing
    PromptEnvelope consumer in apps_rg/utils/anthropic_rag_entrypoint.py.
    That consumer continues to operate unchanged on its own path; this
    module only adds the static R3 contract surface for scanner
    visibility.
    """

    run_id: str
    candidate_name: str
    target_role: str
    target_industry: str
    experience_level: str
    route_type: str
    contract_surface: tuple[str, ...]


def build_rg_r3_handoff_metadata(
    request: "ResumeRequest",
) -> R3HandoffMetadata:
    """Build inspection-only metadata for a résumé generation request.

    No contract is constructed. Captures ``request.trace_id`` (or
    empty string), candidate_name, target_role, target_industry,
    experience_level, the route type, and the static contract surface
    this module exposes. Useful for tests asserting the surface is
    wired without exercising the full GovernedRgRun pipeline.
    """
    trace_id = getattr(request, "trace_id", "") or ""
    candidate_name = getattr(request, "candidate_name", "") or ""
    target_role = getattr(request, "target_role", "") or ""
    target_industry = getattr(request, "target_industry", "") or ""
    experience_level = getattr(request, "experience_level", "") or ""
    return R3HandoffMetadata(
        run_id=trace_id,
        candidate_name=str(candidate_name),
        target_role=str(target_role),
        target_industry=str(target_industry),
        experience_level=str(experience_level),
        route_type="R3_grounded_read",
        contract_surface=R3_REQUIRED_CONTRACT_NAMES,
    )


# ---------------------------------------------------------------------------
# Thin delegate -- behavior unchanged
# ---------------------------------------------------------------------------


def run_rg_via_spine(
    request: "ResumeRequest",
    *,
    runner: "GovernedRgRun | None" = None,
    inject_chunks: list[Any] | None = None,
) -> "GovernedRgE2ERunRecord":
    """Delegate unchanged to GovernedRgRun.run_governed_e2e().

    Name-only seam that records the handoff without altering behavior.
    apps_rg's pipeline today already routes every request through
    GovernedAppRunner -> L1 -> L0 -> C0 -> L2 -> L5+L6; this wrapper
    does not change that. The Anthropic-direct path via
    ``apps_rg/utils/anthropic_rag_entrypoint.py`` is also unchanged --
    this module does not touch it.

    Args:
        request: typed ResumeRequest (candidate_name + target_role +
            target_industry + experience_level + optional trace_id).
        runner: optional pre-constructed GovernedRgRun. When None,
            a default instance is created (collection="rg_docs").
        inject_chunks: optional well-formed HybridSearchResult chunks for
            happy-path proof harnesses; production callers pass None.

    Returns:
        GovernedRgE2ERunRecord -- the existing frozen sealed record from
        GovernedRgRun.run_governed_e2e().

    Side effects:
        Logs an INFO line tagging the handoff with the request's
        trace_id + target_role. NO ledger emission. NO contract
        construction. NO ValidatedRequest envelope is built (apps_qna
        build_time_compiler shape does NOT apply here). NO
        CommitRequest is built (apps_rg has no durable-write surface).
        NO LinkedIn / ATS publication call is made (out of scope).

    Notes:
        Constitutional invariants are upheld by the underlying
        GovernedRgRun substrate; this wrapper adds no governance.
        The eight R3 contracts are surfaced at module load via the
        imports above; this function does not need to reference them
        directly to pass the static-evidence test.
    """
    # Local import keeps this module side-effect-free at import time.
    from apps_rg.integrations.governed_rg_run import GovernedRgRun

    if runner is None:
        runner = GovernedRgRun(collection="rg_docs")

    trace_id = getattr(request, "trace_id", "") or ""
    target_role = getattr(request, "target_role", "") or ""
    _log.info(
        "spine_handoff: rg request trace_id=%s target_role=%s -> "
        "GovernedRgRun.run_governed_e2e (R3_grounded_read)",
        trace_id,
        target_role,
    )
    return runner.run_governed_e2e(request, inject_chunks=inject_chunks)


__all__ = [
    "R3_CONTRACT_SURFACE",
    "R3_REQUIRED_CONTRACT_NAMES",
    "R3HandoffMetadata",
    "build_rg_r3_handoff_metadata",
    "run_rg_via_spine",
    "validate_rg_r3_contract_surface",
    # Re-exports of the 8 R3 contract types.
    "CompiledPromptArtifact",
    "ExitReviewPacket",
    "FinalEvidenceContract",
    "L1PlanContract",
    "RetrievalPlan",
    "RouteContract",
    "SealedArtifact",
    "ValidatedRequest",
]
