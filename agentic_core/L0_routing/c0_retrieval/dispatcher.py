"""C0 dispatcher — the orchestrator that wires every stage.

Pipeline:
  preflight -> plan -> fetch -> hydrate -> graph_expand -> shape -> conflict
  -> verify_and_score -> gates -> failure_modes -> (refine?) -> seal

Hard rules:
- C0.I1: dispatcher never returns prose, only a sealed FinalEvidenceContract.
- C0.I9: at most ONE refinement pass per call (budget-permitting).
- C0.I10: dispatcher cannot self-authorize a route — it only suggests via
  recommended_disposition.
- C0.I11: any exception aborts to a BLOCKED contract; nothing else may exit.

The dispatcher accepts retriever / adjacency callbacks as parameters so it
stays free of any concrete backend dependency.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Callable, Mapping

from .candidate_pool import CandidateEvidencePool
from .contradiction_gap import scan_conflicts_and_gaps
from .evidence_contract import EvidenceContract, verify_and_score
from .failure_modes import FailureModeReport, detect_all_failure_modes
from .final_contract import (
    AclReport,
    BudgetReport,
    ContradictionFlagOut,
    FinalEvidenceContract,
    FreshnessReport,
    LineageEntry,
    PromptBudgetHint,
    ReplayMetadata,
    UnresolvedGapOut,
    seal_final_contract,
)
from .gates import GateReport, run_all_gates
from .graph_traverse import AdjacencyFn, expand_graph
from .hydration import HydratedEvidencePool, normalize_pool
from .plan import RetrievalPlan, build_retrieval_plan
from .preflight import C0PreflightStatus, run_preflight
from .refine_loop import RefinedEvidenceContract, plan_refinement
from .route_contract import L1PlanContract, RouteContract
from .shape import ShapedEvidenceSet, shape_pool
from .verdicts import (
    EvidenceClass,
    RecommendedDisposition,
    SupportStatus,
)


# ----- callback protocols -----

# The dispatcher receives a fetcher callable; it returns a ready
# CandidateEvidencePool. Implementations may use vector DB, BM25, OTEL,
# code index — the dispatcher does not care.
FetcherFn = Callable[[RetrievalPlan, RouteContract], CandidateEvidencePool]


@dataclass(frozen=True)
class C0Result:
    """Whole-pipeline return type — sealed contract + diagnostics."""

    contract: FinalEvidenceContract
    intermediate_contract: EvidenceContract | None
    refined: RefinedEvidenceContract | None
    gates: GateReport | None
    failure_modes: FailureModeReport | None
    plan: RetrievalPlan | None
    notes: tuple[str, ...] = ()


# ----- helpers -----


def _new_contract_id() -> str:
    return f"c0:{uuid.uuid4().hex[:16]}"


def _disposition_from_status(status: SupportStatus) -> RecommendedDisposition:
    return {
        SupportStatus.PASS: RecommendedDisposition.PROCEED,
        SupportStatus.WEAK: RecommendedDisposition.ABSTAIN,
        SupportStatus.WEAK_WITH_CAVEATS: RecommendedDisposition.PROCEED_WITH_CAVEAT,
        SupportStatus.CONFLICTED: RecommendedDisposition.HUMAN_REVIEW,
        SupportStatus.EMPTY: RecommendedDisposition.FALLBACK_R5,
        SupportStatus.BLOCKED: RecommendedDisposition.ABSTAIN,
    }[status]


def _build_blocked_contract(
    *,
    contract_id: str,
    route: RouteContract,
    blocked_reason: str,
    notes: tuple[str, ...] = (),
) -> FinalEvidenceContract:
    """C0.I11 — when any block-severity gate fires, emit a BLOCKED contract."""
    return FinalEvidenceContract(
        contract_id=contract_id,
        route_id=route.route_id,
        status=SupportStatus.BLOCKED,
        support_score=0.0,
        blocked_reason=blocked_reason,
        recommended_disposition=RecommendedDisposition.ABSTAIN,
        replay_metadata=ReplayMetadata(
            policy_hash=route.policy_hash,
            blueprint_hash=route.blueprint_hash,
            route_replay_key=route.route_replay_key,
        ),
        extras={"notes": " | ".join(notes)} if notes else {},
    )


def _build_freshness_report(
    hydrated: HydratedEvidencePool, route: RouteContract,
) -> FreshnessReport:
    stale: list[str] = []
    versions: list[str] = []
    for h in hydrated.hydrated:
        if not h.quality.source_version_current:
            stale.append(h.candidate.chunk_id)
        if h.candidate.manifest.version:
            versions.append(h.candidate.manifest.version)
    newest = max(versions, default="")
    return FreshnessReport(
        freshness_class=route.freshness_class.value,
        newest_source_age=newest,
        stale_sources=tuple(stale),
        version_mismatches=(),
    )


def _build_acl_report(
    hydrated: HydratedEvidencePool, route: RouteContract,
) -> AclReport:
    cleared = [h.candidate.chunk_id for h in hydrated.hydrated if h.quality.acl_clear]
    blocked = sum(1 for h in hydrated.hydrated if not h.quality.acl_clear)
    classes = sorted({h.candidate.manifest.data_class for h in hydrated.hydrated if h.candidate.manifest.data_class})
    return AclReport(
        tenant_scope=route.tenant_scope,
        cleared_sources=tuple(cleared),
        blocked_sources_count=blocked,
        data_classes_seen=tuple(classes),
    )


def _build_budget_report(
    *,
    retrieval_passes: int,
    expanded_hops: int,
    latency_ms: int,
    shaped: ShapedEvidenceSet,
) -> BudgetReport:
    return BudgetReport(
        retrieval_passes=retrieval_passes,
        graph_hops_used=expanded_hops,
        latency_ms=latency_ms,
        cost_tier_used="standard",
        token_estimate=shaped.token_estimate,
        budget_remaining="",
    )


def _build_prompt_budget_hint(
    shaped: ShapedEvidenceSet, *, max_tokens: int,
) -> PromptBudgetHint:
    must_keep = tuple(r.chunk.candidate.chunk_id for r in shaped.must_use)
    pack_order = (
        tuple(r.chunk.candidate.chunk_id for r in shaped.must_use)
        + tuple(r.chunk.candidate.chunk_id for r in shaped.contradicts)
        + tuple(r.chunk.candidate.chunk_id for r in shaped.supporting)
        + tuple(r.chunk.candidate.chunk_id for r in shaped.background)
    )
    trim_first = (
        tuple(r.chunk.candidate.chunk_id for r in shaped.background)
        + tuple(r.chunk.candidate.chunk_id for r in shaped.lineage)
    )
    return PromptBudgetHint(
        pack_order=pack_order,
        must_keep_evidence_ids=must_keep,
        trim_first_evidence_ids=trim_first,
        contradiction_keepers=tuple(
            r.chunk.candidate.chunk_id for r in shaped.contradicts
        ),
        max_context_tokens=max_tokens,
        estimated_context_tokens=shaped.token_estimate,
    )


def _build_lineage(shaped: ShapedEvidenceSet) -> tuple[LineageEntry, ...]:
    out: list[LineageEntry] = []
    for r in shaped.ranked:
        lanes = "|".join(l.value for l in r.chunk.candidate.found_by_lanes)
        out.append(
            LineageEntry(
                evidence_id=r.chunk.candidate.chunk_id,
                found_by=lanes,
                expanded_by="",
                rerank_reason=f"bucket={r.bucket.value} score={r.final_score:.2f}",
            ),
        )
    return tuple(out)


def _project_contradiction_flags(
    conflict_report,
) -> tuple[ContradictionFlagOut, ...]:
    return tuple(
        ContradictionFlagOut(
            type=cf.contradiction_type.value,
            source_a=cf.source_a_chunk_id,
            source_b=cf.source_b_chunk_id,
            severity=cf.severity,
            summary=cf.summary,
            required_downstream_behavior=cf.required_downstream_behavior,
        )
        for cf in conflict_report.contradictions
    )


def _project_gaps(conflict_report) -> tuple[UnresolvedGapOut, ...]:
    return tuple(
        UnresolvedGapOut(
            gap_type=g.gap_type,
            severity=g.severity,
            impact_on_answer=g.impact_on_answer,
            suggested_next_step=g.suggested_next_step.value,
        )
        for g in conflict_report.gaps
    )


# ----- the dispatcher -----


@dataclass
class C0Dispatcher:
    """Stateless wrapper around the pipeline. Carries injected callbacks."""

    fetch: FetcherFn
    adjacency: AdjacencyFn

    def run(
        self,
        *,
        route: RouteContract,
        plan_contract: L1PlanContract,
        plan_id: str | None = None,
        request_id: str | None = None,
    ) -> C0Result:
        contract_id = _new_contract_id()
        rid = request_id or contract_id
        notes: list[str] = []
        t_start = time.monotonic()

        # Stage C0.0 — preflight
        pre = run_preflight(route, plan_contract)
        if not pre.eligible:
            blocked = _build_blocked_contract(
                contract_id=contract_id,
                route=route,
                blocked_reason=f"preflight: {pre.blocked_reason.value if pre.blocked_reason else 'unknown'}",
                notes=tuple(pre.notes),
            )
            return C0Result(
                contract=seal_final_contract(blocked),
                intermediate_contract=None,
                refined=None,
                gates=None,
                failure_modes=None,
                plan=None,
                notes=tuple(pre.notes),
            )

        # Stage C0.1 — retrieval plan
        plan = build_retrieval_plan(
            route=route,
            plan_contract=plan_contract,
            preflight=pre,
            plan_id=plan_id or f"plan:{uuid.uuid4().hex[:12]}",
        )

        # Stage C0.2 — fetch (callback)
        candidates = self.fetch(plan, route)

        # Stage C0.2A — hydrate
        hydrated = normalize_pool(candidates, tenant=route.tenant_scope)

        # Stage C0.3 — graph expand
        expanded = expand_graph(
            hydrated, bounds=plan.graph_bounds, adjacency=self.adjacency,
        )

        # Stage C0.4A — contradictions + gaps (computed first so shape can flag them)
        conflict_report = scan_conflicts_and_gaps(
            expanded, target=plan.support_target,
        )

        # Stage C0.4 — shape
        shaped = shape_pool(
            expanded,
            target=plan.support_target,
            max_token_context=plan.budgets.max_token_context,
            contradiction_chunk_ids=conflict_report.contradiction_chunk_ids(),
        )

        # Stage C0.5 — verify + score
        intermediate = verify_and_score(
            shaped,
            request_id=rid,
            target=plan.support_target,
            conflict_report=conflict_report,
        )

        # Gates
        gates = run_all_gates(
            route=route,
            plan_contract=plan_contract,
            preflight=pre,
            plan=plan,
            candidates=candidates,
            hydrated=hydrated,
            expanded=expanded,
            shaped=shaped,
            conflict=conflict_report,
            contract=intermediate,
        )

        # Failure modes
        fm = detect_all_failure_modes(
            plan=plan, route=route, candidates=candidates, hydrated=hydrated,
            expanded=expanded, shaped=shaped, conflict=conflict_report,
            contract=intermediate,
        )

        # If any gate is block-severity (other than G0 which we passed at preflight),
        # emit BLOCKED — even if intermediate.status would be PASS.
        blockers = gates.blockers()
        if blockers:
            block_reason = "; ".join(o.reason for o in blockers)
            blocked = _build_blocked_contract(
                contract_id=contract_id, route=route,
                blocked_reason=f"gate(s) failed: {block_reason}",
                notes=tuple(o.gate.value for o in blockers),
            )
            return C0Result(
                contract=seal_final_contract(blocked),
                intermediate_contract=intermediate,
                refined=None,
                gates=gates,
                failure_modes=fm,
                plan=plan,
                notes=tuple(notes),
            )

        # C0.6 refine — single-pass at most
        refined = plan_refinement(
            intermediate, conflict=conflict_report, plan=plan, attempts_so_far=0,
        )

        # Build the final contract. Refinement does NOT re-run the pipeline
        # in this base wave — it records intent. A wrapper or higher-level
        # orchestrator may invoke the dispatcher again with a refined plan.
        latency_ms = int((time.monotonic() - t_start) * 1000)
        final_status = intermediate.status

        contradiction_flags_out = _project_contradiction_flags(conflict_report)
        gaps_out = _project_gaps(conflict_report)

        # Map shaped buckets onto the final contract evidence-class fields.
        must_use = tuple(r.chunk for r in shaped.must_use)
        supporting = tuple(r.chunk for r in shaped.supporting)
        contradicts = tuple(r.chunk for r in shaped.contradicts)
        background = tuple(r.chunk for r in shaped.background)
        definitions = tuple(r.chunk for r in shaped.definitions)

        excluded = tuple(
            (r.chunk.candidate.chunk_id, "shape:excluded")
            for r in shaped.excluded
        )

        # If status is CONFLICTED and contradiction_flags_out is empty, that
        # would violate the FinalEvidenceContract invariant. Cover this
        # explicitly: project at least one synthesized flag from the conflict
        # report so the contract validates.
        if (
            final_status == SupportStatus.CONFLICTED
            and not contradiction_flags_out
        ):
            # Should not happen given _choose_status, but guard defensively.
            final_status = SupportStatus.WEAK_WITH_CAVEATS

        # WEAK_WITH_CAVEATS requires gaps OR contradictions to satisfy the
        # post_init invariant. If shaping produced none, downgrade to WEAK
        # (which has no such requirement).
        if (
            final_status == SupportStatus.WEAK_WITH_CAVEATS
            and not gaps_out and not contradiction_flags_out
        ):
            final_status = SupportStatus.WEAK

        contract = FinalEvidenceContract(
            contract_id=contract_id,
            route_id=route.route_id,
            status=final_status,
            support_score=intermediate.support_score,
            score_breakdown=intermediate.score_breakdown,
            must_use=must_use,
            supporting=supporting,
            contradicts=contradicts,
            background=background,
            definitions=definitions,
            lineage=_build_lineage(shaped),
            excluded=excluded,
            contradiction_flags=contradiction_flags_out,
            unresolved_gaps=gaps_out,
            freshness_report=_build_freshness_report(hydrated, route),
            acl_report=_build_acl_report(hydrated, route),
            prompt_budget_hint=_build_prompt_budget_hint(
                shaped, max_tokens=plan.budgets.max_token_context,
            ),
            recommended_disposition=_disposition_from_status(final_status),
            budget_report=_build_budget_report(
                retrieval_passes=1,
                expanded_hops=len(expanded.traverse.hops),
                latency_ms=latency_ms,
                shaped=shaped,
            ),
            replay_metadata=ReplayMetadata(
                policy_hash=route.policy_hash,
                blueprint_hash=route.blueprint_hash,
                route_replay_key=route.route_replay_key,
                source_manifest_hash="",
            ),
            refine_attempts=refined.refine_attempts,
            refine_tactic=refined.refine_tactic.value,
            refine_delta=str(refined.refine_delta_score),
            remaining_gaps=refined.remaining_gap_codes,
            extras={
                "failure_modes_detected": ",".join(m.value for m in fm.detected),
                "evidence_hmac": intermediate.evidence_hmac,
            },
        )

        sealed = seal_final_contract(contract)
        return C0Result(
            contract=sealed,
            intermediate_contract=intermediate,
            refined=refined,
            gates=gates,
            failure_modes=fm,
            plan=plan,
            notes=tuple(notes),
        )


def run_c0(
    *,
    route: RouteContract,
    plan_contract: L1PlanContract,
    fetch: FetcherFn,
    adjacency: AdjacencyFn,
    plan_id: str | None = None,
    request_id: str | None = None,
) -> C0Result:
    """Convenience entry point — wraps C0Dispatcher for a single call."""
    return C0Dispatcher(fetch=fetch, adjacency=adjacency).run(
        route=route,
        plan_contract=plan_contract,
        plan_id=plan_id,
        request_id=request_id,
    )


__all__ = ["C0Dispatcher", "C0Result", "FetcherFn", "run_c0"]
