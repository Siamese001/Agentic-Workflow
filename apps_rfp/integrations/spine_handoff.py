"""apps_rfp spine-handoff -- W12 R3_grounded_read direct surfacing.

Mirrors the apps_research W9, apps_exec W10, and apps_lic W11
patterns. Surfaces the canonical R3 contract chain (per
``docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md``) directly from
``agentic_core`` so the runtime-mode scanner
(``tools.analysis.apps_spine_coverage``) can verify the delegation
evidence statically. Today these contracts flow into apps_rfp
**transitively** through
``apps_shared.integrations.governed_app_runner.GovernedAppRunner``;
this module makes the surface **directly visible** without changing
runtime behavior.

This module is STATIC EVIDENCE only. It does NOT:
  - construct any of the R3 contracts at runtime;
  - rewrite or replace ``GovernedRfpRun.run_governed_e2e()``;
  - rewrite ``RfpOrchestrator.run`` or any internal orchestrator behavior;
  - add a ``CommitRequest`` (apps_rfp has no durable-write surface);
  - add a ``StateDiffCandidate``;
  - claim a proposal-store durable write;
  - claim portal-submission write (explicitly out of scope per
    ``apps_rfp/SVP_ENGINEERING_REVIEW.md`` and ``apps_rfp/SLO.md``);
  - bypass ``GovernedAppRunner``;
  - copy the apps_qna ``build_time_compiler + ValidatedRequest envelope`` pattern;
  - claim runtime certification.

HITL posture (informational): ``GovernedRfpRun`` does NOT declare
``HITL_ENABLED`` (defaults False per ``GovernedAppRunner``). apps_rfp
does not opt into runtime HITL escalation -- proposal review happens
out-of-band. This is a weaker HITL posture than apps_lic / apps_exec
(both True), but HITL is orthogonal to route shape: R3R4_managed_workflow
requires CommitRequest, not HITL. apps_rfp stays in R3_grounded_read.

The R3 contract chain (8 contracts):

    ValidatedRequest         intake -- L0 ingress
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
  - §29 closed-loop: the GovernedRfpRun pipeline keeps emitting
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
# Canonical paths (matched to apps_research W9 / apps_exec W10 / apps_lic W11).
#
# NOTE: CommitRequest is INTENTIONALLY NOT IMPORTED. apps_rfp is
# R3_grounded_read, not R3R4_managed_workflow. The pre-migration audit
# proved no durable-write surface exists; portal submission is explicitly
# out of scope per apps_rfp/SVP_ENGINEERING_REVIEW.md and apps_rfp/SLO.md.
# Importing CommitRequest here would be contract theater that contradicts
# the app's documented charter.
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
    from apps_rfp.integrations.governed_rfp_run import (
        GovernedRfpE2ERunRecord,
        GovernedRfpRun,
    )
    from apps_rfp.types.rfp_types import RfpRequest

_log = logging.getLogger(__name__)

_PROBLEM_STATEMENT_PREVIEW_CHARS: int = 120
"""Match the truncation length used in GovernedRfpE2ERunRecord.problem_statement."""


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
"""The 8 canonical R3 contract types apps_rfp delegates through.

Declarative mapping. Importing this module brings the eight contract
types into namespace; the values are the imported classes themselves.
``CommitRequest`` is intentionally absent -- apps_rfp is
R3_grounded_read, not R3R4_managed_workflow.
"""

R3_REQUIRED_CONTRACT_NAMES: tuple[str, ...] = tuple(R3_CONTRACT_SURFACE.keys())
"""Stable ordering of the 8 R3 contract names (matches manifest order)."""


def validate_rfp_r3_contract_surface() -> dict[str, bool]:
    """Return per-contract availability map.

    Every entry is True when this module imports cleanly (the imports
    above are at module level, so a failed import would prevent this
    function from being callable in the first place). The function
    exists as a programmatic affirmation surface for tests and ledger
    inspection -- it does NOT instantiate any contract.
    """
    return {
        name: cls is not None for name, cls in R3_CONTRACT_SURFACE.items()
    }


@dataclass(frozen=True)
class R3HandoffMetadata:
    """Inspection-only metadata describing one apps_rfp handoff.

    Returned by :func:`build_rfp_r3_handoff_metadata`. Carries the
    run_id, industry, architecture_posture, problem_statement
    preview, route type, and a frozen tuple of contract names exposed
    by this module. Intended for ledger introspection / test
    fixtures; NOT used on the hot path of GovernedRfpRun.

    HITL posture is documented at module level (HITL is False/absent
    on GovernedRfpRun); the metadata does not redundantly carry that
    flag because it is a property of the runner, not of an
    individual handoff.
    """

    run_id: str
    industry: str
    architecture_posture: str
    problem_statement_preview: str
    route_type: str
    contract_surface: tuple[str, ...]


def build_rfp_r3_handoff_metadata(
    request: "RfpRequest",
) -> R3HandoffMetadata:
    """Build inspection-only metadata for an RFP proposal request.

    No contract is constructed. The returned object simply captures
    ``request.trace_id`` (or empty string), industry,
    architecture_posture, a 120-character preview of
    problem_statement (matching the runtime record's truncation),
    the route type, and the static contract surface this module
    exposes. Useful for tests asserting the surface is wired without
    exercising the full GovernedRfpRun pipeline.
    """
    trace_id = getattr(request, "trace_id", "") or ""
    industry = getattr(request, "industry", "") or ""
    architecture_posture = getattr(request, "architecture_posture", "") or ""
    problem_statement = getattr(request, "problem_statement", "") or ""
    return R3HandoffMetadata(
        run_id=trace_id,
        industry=str(industry),
        architecture_posture=str(architecture_posture),
        problem_statement_preview=str(problem_statement)[
            :_PROBLEM_STATEMENT_PREVIEW_CHARS
        ],
        route_type="R3_grounded_read",
        contract_surface=R3_REQUIRED_CONTRACT_NAMES,
    )


# ---------------------------------------------------------------------------
# Thin delegate -- behavior unchanged
# ---------------------------------------------------------------------------


def run_rfp_via_spine(
    request: "RfpRequest",
    *,
    runner: "GovernedRfpRun | None" = None,
    inject_chunks: list[Any] | None = None,
) -> "GovernedRfpE2ERunRecord":
    """Delegate unchanged to GovernedRfpRun.run_governed_e2e().

    Name-only seam that records the handoff without altering behavior.
    apps_rfp's pipeline today already routes every request through
    GovernedAppRunner -> L1 -> L0 -> C0 -> L2 -> L5+L6; this wrapper
    does not change that.

    Args:
        request: typed RfpRequest (problem_statement + industry +
            architecture_posture + delivery_timeline_weeks + optional
            trace_id + dry_run).
        runner: optional pre-constructed GovernedRfpRun. When None,
            a default instance is created (collection="rfp_docs").
        inject_chunks: optional well-formed HybridSearchResult chunks for
            happy-path proof harnesses; production callers pass None.

    Returns:
        GovernedRfpE2ERunRecord -- the existing frozen sealed record from
        GovernedRfpRun.run_governed_e2e().

    Side effects:
        Logs an INFO line tagging the handoff with the request's
        trace_id + industry. NO ledger emission. NO contract
        construction. NO ValidatedRequest envelope is built (that is
        the apps_qna build_time_compiler shape, which does NOT apply
        here). NO CommitRequest is built (apps_rfp has no
        durable-write surface). NO portal call is made (explicitly
        out of scope per the SVP review).

    Notes:
        Constitutional invariants are upheld by the underlying
        GovernedRfpRun substrate; this wrapper adds no governance.
        The eight R3 contracts are surfaced at module load via the
        imports above; this function does not need to reference them
        directly to pass the static-evidence test.
    """
    # Local import keeps this module side-effect-free at import time.
    from apps_rfp.integrations.governed_rfp_run import GovernedRfpRun

    if runner is None:
        runner = GovernedRfpRun(collection="rfp_docs")

    trace_id = getattr(request, "trace_id", "") or ""
    industry = getattr(request, "industry", "") or ""
    _log.info(
        "spine_handoff: rfp request trace_id=%s industry=%s -> "
        "GovernedRfpRun.run_governed_e2e (R3_grounded_read)",
        trace_id,
        industry,
    )
    return runner.run_governed_e2e(request, inject_chunks=inject_chunks)


__all__ = [
    "R3_CONTRACT_SURFACE",
    "R3_REQUIRED_CONTRACT_NAMES",
    "R3HandoffMetadata",
    "build_rfp_r3_handoff_metadata",
    "run_rfp_via_spine",
    "validate_rfp_r3_contract_surface",
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
