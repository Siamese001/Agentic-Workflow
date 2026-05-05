"""C0 Thin Adapter — shapes request, calls canonical C0, returns unchanged.

W2.1: Enhanced adapter with proper error handling, fail-closed semantics,
and canonical C0 integration contract.

D1.1: Wired to canonical run_c0 from agentic_core.L0_routing.c0_retrieval.
Uses a no-op stub fetcher/adjacency — apps_qna has no vector store yet
(D3 lands real retrieval). Bridges the canonical FinalEvidenceContract to
the apps_qna-shaped FinalEvidenceContract.

The adapter MUST:
- Shape an app-specific C0 request from interview parameters
- Call the canonical C0 retrieval endpoint
- Return the canonical FinalEvidenceContract unchanged
- Handle C0 errors fail-closed (→ SAFE_ABSTAIN)
- Never transform evidence or invent facts

Plan: .windsurf/plans/apps-qna-spine-deferred-e9c5b3.md D1.1
"""

from __future__ import annotations

import logging
from typing import Any

from apps_qna.types.evidence_contracts import FinalEvidenceContract

_LOGGER = logging.getLogger(__name__)


class C0UnavailableError(Exception):
    """Raised when canonical C0 is unavailable — fail-closed."""


def call_c0(
    *,
    interview_slug: str,
    route_id: str,
    query_text: str = "",
) -> dict[str, Any]:
    """Call canonical C0 and return FinalEvidenceContract unchanged.

    Args:
        interview_slug: The interview slug for evidence scoping.
        route_id: The selected route id.
        query_text: Optional retrieval query text.

    Returns:
        A FinalEvidenceContract-shaped dict.

    Raises:
        C0UnavailableError: If canonical C0 is unreachable (fail-closed).
    """
    try:
        fec = _call_canonical_c0(
            interview_slug=interview_slug,
            route_id=route_id,
            query_text=query_text,
        )
    except Exception as exc:
        _LOGGER.error("C0 unavailable for slug=%s: %s", interview_slug, exc)
        raise C0UnavailableError(
            f"Canonical C0 unavailable for interview '{interview_slug}'. "
            "Fail-closed: no evidence can be invented."
        ) from exc

    return fec.to_dict()


def _call_canonical_c0(
    *,
    interview_slug: str,
    route_id: str,
    query_text: str = "",
) -> FinalEvidenceContract:
    """Call the canonical C0 retrieval endpoint via run_c0.

    D1.1: Wired to agentic_core.L0_routing.c0_retrieval.run_c0.
    Uses no-op stub fetcher + adjacency because apps_qna has no vector
    store yet. The canonical pipeline runs preflight → plan → gates;
    the empty fetch pool causes it to emit a WEAK/EMPTY contract which
    we bridge to the apps_qna FinalEvidenceContract shape.
    """
    from agentic_core.L0_routing.c0_retrieval import (
        run_c0,
        RouteContract,
        L1PlanContract,
        FreshnessClass,
        SupportTarget,
    )
    from agentic_core.L0_routing.c0_retrieval.candidate_pool import (
        CandidateEvidencePool,
    )
    from agentic_core.L0_routing.c0_retrieval.verdicts import SupportStatus

    def _stub_fetch(plan: Any, route: Any) -> CandidateEvidencePool:
        return CandidateEvidencePool(plan_id=plan.plan_id, candidates=())

    def _stub_adjacency(node_id: str, relations: Any) -> tuple:
        return ()

    route = RouteContract(
        route_id=route_id,
        grounding_required=True,
        execution_form="SINGLE_STEP",
        freshness_class=FreshnessClass.CURRENT,
        support_target=SupportTarget.SOURCE_SUMMARY,
        tenant_scope=interview_slug or "apps_qna",
        data_class="internal",
    )
    plan_contract = L1PlanContract(
        task_spec=f"interview_prep:{interview_slug}",
        query_spec=query_text or interview_slug,
        grounding_required=True,
        user_task_text=query_text,
    )

    result = run_c0(
        route=route,
        plan_contract=plan_contract,
        fetch=_stub_fetch,
        adjacency=_stub_adjacency,
    )

    canonical = result.contract
    grounded = canonical.status not in (SupportStatus.BLOCKED, SupportStatus.EMPTY)
    sufficiency = "grounded" if grounded else "template_only"

    retrieval_sources: tuple[str, ...] = ()
    source_register: tuple[str, ...] = ()
    contradiction_flags: tuple[str, ...] = ()

    if canonical.must_use_view:
        retrieval_sources = tuple(
            v.source_id for v in canonical.must_use_view
        )
        source_register = retrieval_sources
    if canonical.contradiction_flags:
        contradiction_flags = tuple(
            str(f) for f in canonical.contradiction_flags
        )

    freshness = "current"
    if canonical.freshness_report and canonical.freshness_report.stale_sources:
        freshness = "stale"

    return FinalEvidenceContract(
        schema_version="1.0",
        producer="agentic_core.C0",
        grounded=grounded,
        retrieval_sources=retrieval_sources,
        route_id=route_id,
        evidence_sufficiency=sufficiency,
        interview_slug=interview_slug,
        query_text=query_text,
        source_register=source_register,
        freshness_assessment=freshness,
        claim_confidence=float(canonical.support_score),
        contradiction_flags=contradiction_flags,
    )


__all__ = ["C0UnavailableError", "call_c0"]
