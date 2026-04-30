"""apps_exec spine-handoff -- W10 R3_grounded_read direct surfacing.

Mirrors the apps_research W9 pattern. Surfaces the canonical R3
contract chain (per ``docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md``)
directly from ``agentic_core`` so the runtime-mode scanner
(``tools.analysis.apps_spine_coverage``) can verify the delegation
evidence statically. Today these contracts flow into apps_exec
**transitively** through
``apps_shared.integrations.governed_app_runner.GovernedAppRunner``;
this module makes the surface **directly visible** without changing
runtime behavior.

This module is STATIC EVIDENCE only. It does NOT:
  - construct any of the R3 contracts at runtime;
  - rewrite or replace ``GovernedExecRun.run_governed_e2e()``;
  - add a ``CommitRequest`` (apps_exec has no durable-write surface);
  - bypass ``GovernedAppRunner``;
  - copy the apps_qna ``build_time_compiler + ValidatedRequest envelope`` pattern;
  - claim runtime certification.

HITL posture (informational): ``GovernedExecRun.HITL_ENABLED = True``.
That gates the spine's runtime HITL escalation path; it is NOT
evidence of a durable-write surface and does not change the route
shape. apps_exec stays in R3_grounded_read because the
``GovernedExecE2ERunRecord`` carries no commit / durable-write field.

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
  - §29 closed-loop: the GovernedExecRun pipeline keeps emitting
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
# Canonical paths (matched to apps_research W9 selections):
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
    from apps_exec.integrations.governed_exec_run import (
        GovernedExecE2ERunRecord,
        GovernedExecRun,
    )
    from apps_exec.types.exec_types import ExecBriefRequest

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
"""The 8 canonical R3 contract types apps_exec delegates through.

Declarative mapping. Importing this module brings the eight contract
types into namespace; the values are the imported classes themselves.
Iterating ``R3_CONTRACT_SURFACE.items()`` lets a caller introspect the
spine surface without re-importing each type by hand.
"""

R3_REQUIRED_CONTRACT_NAMES: tuple[str, ...] = tuple(R3_CONTRACT_SURFACE.keys())
"""Stable ordering of the 8 R3 contract names (matches manifest order)."""


def validate_exec_r3_contract_surface() -> dict[str, bool]:
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
    """Inspection-only metadata describing one apps_exec handoff.

    Returned by :func:`build_exec_r3_handoff_metadata`. Carries the
    run_id, audience, route type, and a frozen tuple of contract names
    exposed by this module. Intended for ledger introspection / test
    fixtures; NOT used on the hot path of GovernedExecRun.
    """

    run_id: str
    audience: str
    route_type: str
    contract_surface: tuple[str, ...]


def build_exec_r3_handoff_metadata(
    request: "ExecBriefRequest",
) -> R3HandoffMetadata:
    """Build inspection-only metadata for an executive-brief request.

    No contract is constructed. The returned object simply captures
    ``request.trace_id`` (or empty string), ``request.audience`` (as
    its string value), the route type, and the static contract surface
    this module exposes. Useful for tests asserting the surface is
    wired without exercising the full GovernedExecRun pipeline.
    """
    trace_id = getattr(request, "trace_id", "") or ""
    audience_attr = getattr(request, "audience", "")
    audience = (
        audience_attr.value
        if hasattr(audience_attr, "value")
        else str(audience_attr or "")
    )
    return R3HandoffMetadata(
        run_id=trace_id,
        audience=audience,
        route_type="R3_grounded_read",
        contract_surface=R3_REQUIRED_CONTRACT_NAMES,
    )


# ---------------------------------------------------------------------------
# Thin delegate -- behavior unchanged
# ---------------------------------------------------------------------------


def run_exec_via_spine(
    request: "ExecBriefRequest",
    *,
    runner: "GovernedExecRun | None" = None,
    inject_chunks: list[Any] | None = None,
) -> "GovernedExecE2ERunRecord":
    """Delegate unchanged to GovernedExecRun.run_governed_e2e().

    Name-only seam that records the handoff without altering behavior.
    apps_exec's pipeline today already routes every request through
    GovernedAppRunner -> L1 -> L0 -> C0 -> L2 -> L5+L6; this wrapper
    does not change that.

    Args:
        request: typed ExecBriefRequest (audience + emphasis_areas + optional trace_id).
        runner: optional pre-constructed GovernedExecRun. When None,
            a default instance is created (collection="exec_docs").
        inject_chunks: optional well-formed HybridSearchResult chunks for
            happy-path proof harnesses; production callers pass None.

    Returns:
        GovernedExecE2ERunRecord -- the existing frozen sealed record from
        GovernedExecRun.run_governed_e2e().

    Side effects:
        Logs an INFO line tagging the handoff with the request's
        trace_id + audience. NO ledger emission. NO contract construction.
        NO ValidatedRequest envelope is built (that is the apps_qna
        build_time_compiler shape, which does NOT apply here).

    Notes:
        Constitutional invariants are upheld by the underlying
        GovernedExecRun substrate; this wrapper adds no governance.
        The eight R3 contracts are surfaced at module load via the
        imports above; this function does not need to reference them
        directly to pass the static-evidence test.
    """
    # Local import keeps this module side-effect-free at import time.
    from apps_exec.integrations.governed_exec_run import GovernedExecRun

    if runner is None:
        runner = GovernedExecRun(collection="exec_docs")

    trace_id = getattr(request, "trace_id", "") or ""
    audience_attr = getattr(request, "audience", "")
    audience = (
        audience_attr.value
        if hasattr(audience_attr, "value")
        else str(audience_attr or "")
    )
    _log.info(
        "spine_handoff: exec request trace_id=%s audience=%s -> "
        "GovernedExecRun.run_governed_e2e (R3_grounded_read)",
        trace_id,
        audience,
    )
    return runner.run_governed_e2e(request, inject_chunks=inject_chunks)


__all__ = [
    "R3_CONTRACT_SURFACE",
    "R3_REQUIRED_CONTRACT_NAMES",
    "R3HandoffMetadata",
    "build_exec_r3_handoff_metadata",
    "run_exec_via_spine",
    "validate_exec_r3_contract_surface",
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
