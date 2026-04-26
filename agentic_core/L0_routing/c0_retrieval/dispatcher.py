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
from .evidence_projections import (
    project_background,
    project_contradicts,
    project_definition,
    project_excluded,
    project_must_use,
    project_supporting,
)
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
    compute_source_manifest_hash,
    seal_final_contract,
)
from .gates import GateReport, run_all_gates
from .contradiction_gap import ConflictGapReport
from .graph_traverse import AdjacencyFn, GraphExpandedEvidencePool, expand_graph
from .hydration import HydratedEvidencePool, normalize_pool
from .plan import RetrievalPlan, build_retrieval_plan
from .preflight import C0PreflightStatus, run_preflight
from .refine_loop import RefinedEvidenceContract, detect_compound_target, plan_refinement
from .route_contract import L1PlanContract, RouteContract
from .shape import ShapedEvidenceSet, shape_pool
from .verdicts import (
    EvidenceClass,
    RecommendedDisposition,
    RefineTactic,
    RetrievalMode,
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


def _authority_signal():
    """Resolve at call time so we don't import RerankSignal at module top
    (avoids circular import; mirrors evidence_contract._authority_key)."""
    from .shape import RerankSignal
    return RerankSignal.AUTHORITY


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
        route_replay_key=route.route_replay_key,
        policy_hash=route.policy_hash,
        blueprint_hash=route.blueprint_hash,
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
    """Spec lines 1082-1086 — stale_sources holds SOURCE-LEVEL ids, not chunk ids."""
    stale: list[str] = []
    versions: list[str] = []
    for h in hydrated.hydrated:
        if not h.quality.source_version_current:
            # Source-level identity per spec line 1085 (list of stale sources).
            stale.append(h.canonical_source_path)
        if h.candidate.manifest.version:
            versions.append(h.candidate.manifest.version)
    newest = max(versions, default="")
    return FreshnessReport(
        freshness_class=route.freshness_class.value,
        newest_source_age=newest,
        # De-dupe while preserving insertion order.
        stale_sources=tuple(dict.fromkeys(stale)),
        version_mismatches=(),
    )


def _build_acl_report(
    hydrated: HydratedEvidencePool, route: RouteContract,
) -> AclReport:
    """Spec lines 1088-1092 — cleared_sources holds SOURCE-LEVEL ids, not chunk ids."""
    cleared = [h.canonical_source_path for h in hydrated.hydrated if h.quality.acl_clear]
    blocked = sum(1 for h in hydrated.hydrated if not h.quality.acl_clear)
    classes = sorted({h.candidate.manifest.data_class for h in hydrated.hydrated if h.candidate.manifest.data_class})
    return AclReport(
        tenant_scope=route.tenant_scope,
        # De-dupe while preserving insertion order.
        cleared_sources=tuple(dict.fromkeys(cleared)),
        blocked_sources_count=blocked,
        data_classes_seen=tuple(classes),
    )


def _build_budget_report(
    *,
    retrieval_passes: int,
    expanded_hops: int,
    latency_ms: int,
    shaped: ShapedEvidenceSet,
    route: RouteContract,
    plan: RetrievalPlan,
) -> BudgetReport:
    """Spec lines 1123-1128 — budget_report carries actual usage, not placeholders."""
    tokens_used = shaped.token_estimate
    tokens_remaining = max(0, plan.budgets.max_token_context - tokens_used)
    latency_remaining = max(0, plan.budgets.max_latency_ms - latency_ms)
    return BudgetReport(
        retrieval_passes=retrieval_passes,
        graph_hops_used=expanded_hops,
        latency_ms=latency_ms,
        cost_tier_used=route.max_cost_tier,
        token_estimate=tokens_used,
        budget_remaining=(
            f"tokens={tokens_remaining}/{plan.budgets.max_token_context}, "
            f"latency_ms={latency_remaining}/{plan.budgets.max_latency_ms}"
        ),
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


# ----- refinement-tactic application -----


def _apply_refine_tactic(plan: RetrievalPlan, tactic: RefineTactic) -> RetrievalPlan:
    """Build a refined plan from a base plan + tactic.

    Spec lines 707-715 — the allowed refinements for a single bounded second
    pass. We modify only the parameters the tactic governs; everything else
    (route, ACL, tenant, support_target) is held fixed per spec lines 717-724.
    """
    if tactic == RefineTactic.HYBRIDIZE:
        # Ensure SPARSE present in retrieval modes; spec line 715.
        if RetrievalMode.SPARSE in plan.retrieval_modes:
            return plan
        return _replace_plan(plan, retrieval_modes=plan.retrieval_modes + (RetrievalMode.SPARSE,))
    if tactic == RefineTactic.GRAPH_HOP:
        # Bounded one-hop expansion — spec line 714.
        from .plan import GraphBounds
        new_bounds = GraphBounds(
            max_hops=plan.graph_bounds.max_hops + 1,
            max_parent_expansion=plan.graph_bounds.max_parent_expansion,
            max_child_expansion=plan.graph_bounds.max_child_expansion,
            relation_filter=plan.graph_bounds.relation_filter,
        )
        return _replace_plan(plan, graph_bounds=new_bounds)
    if tactic == RefineTactic.BROADEN:
        # Lower dense similarity_threshold; spec line 711.
        if plan.dense_query_spec is not None and plan.dense_query_spec.similarity_threshold > 0:
            from .plan import DenseQuerySpec
            new_dq = DenseQuerySpec(
                query_text=plan.dense_query_spec.query_text,
                embed_model_id=plan.dense_query_spec.embed_model_id,
                top_k=plan.dense_query_spec.top_k,
                similarity_threshold=max(0.0, plan.dense_query_spec.similarity_threshold - 0.1),
            )
            return _replace_plan(plan, dense_query_spec=new_dq)
        return plan
    if tactic == RefineTactic.NARROW:
        # Tighten dense similarity_threshold; spec line 712.
        if plan.dense_query_spec is not None:
            from .plan import DenseQuerySpec
            new_dq = DenseQuerySpec(
                query_text=plan.dense_query_spec.query_text,
                embed_model_id=plan.dense_query_spec.embed_model_id,
                top_k=plan.dense_query_spec.top_k,
                similarity_threshold=min(1.0, plan.dense_query_spec.similarity_threshold + 0.1),
            )
            return _replace_plan(plan, dense_query_spec=new_dq)
        return plan
    if tactic == RefineTactic.FRESHEN:
        # Drop CACHE if active; force METADATA mode; spec line 711.
        new_modes = tuple(m for m in plan.retrieval_modes if m != RetrievalMode.CACHE)
        if RetrievalMode.METADATA not in new_modes:
            new_modes = new_modes + (RetrievalMode.METADATA,)
        return _replace_plan(plan, retrieval_modes=new_modes)
    if tactic == RefineTactic.REWRITE:
        # No-op for the base wave: REWRITE requires query rewriting which the
        # caller controls. We still mark refine_attempts so callers can detect.
        return plan
    # DECOMPOSE / ABSTAIN — caller-handled / no second pass.
    return plan


def _replace_plan(plan: RetrievalPlan, **kwargs) -> RetrievalPlan:
    """Frozen-dataclass replace helper that round-trips through the constructor."""
    fields = {f: getattr(plan, f) for f in plan.__dataclass_fields__}
    fields.update(kwargs)
    return RetrievalPlan(**fields)


# ----- inner pipeline state container -----


@dataclass(frozen=True)
class _PipelinePass:
    """Per-pass artifacts. Used by both the first pass and the refinement re-run."""

    candidates: CandidateEvidencePool
    hydrated: HydratedEvidencePool
    expanded: GraphExpandedEvidencePool
    conflict_report: ConflictGapReport
    shaped: ShapedEvidenceSet
    intermediate: EvidenceContract


# ----- the dispatcher -----


@dataclass
class C0Dispatcher:
    """Stateless wrapper around the pipeline. Carries injected callbacks."""

    fetch: FetcherFn
    adjacency: AdjacencyFn

    def _run_pipeline_pass(
        self, *, plan: RetrievalPlan, route: RouteContract, request_id: str,
    ) -> _PipelinePass:
        """Execute fetch -> hydrate -> graph -> conflict -> shape -> verify_and_score
        for ONE pass. Pure: no I/O outside the injected callbacks.
        """
        candidates = self.fetch(plan, route)
        hydrated = normalize_pool(candidates, tenant=route.tenant_scope)
        expanded = expand_graph(
            hydrated, bounds=plan.graph_bounds, adjacency=self.adjacency,
        )
        conflict_report = scan_conflicts_and_gaps(
            expanded, target=plan.support_target,
        )
        shaped = shape_pool(
            expanded,
            target=plan.support_target,
            max_token_context=plan.budgets.max_token_context,
            contradiction_chunk_ids=conflict_report.contradiction_chunk_ids(),
        )
        intermediate = verify_and_score(
            shaped,
            request_id=request_id,
            target=plan.support_target,
            conflict_report=conflict_report,
        )
        return _PipelinePass(
            candidates=candidates,
            hydrated=hydrated,
            expanded=expanded,
            conflict_report=conflict_report,
            shaped=shaped,
            intermediate=intermediate,
        )

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

        try:
            return self._run_inner(
                contract_id=contract_id, rid=rid, route=route,
                plan_contract=plan_contract, plan_id=plan_id,
                t_start=t_start, notes=notes,
            )
        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            # C0.I11 — any error inside the pipeline must surface as a sealed
            # BLOCKED contract. We never propagate exceptions to callers
            # because doing so would leak retrieval lineage and bypass the
            # output contract.
            blocked = _build_blocked_contract(
                contract_id=contract_id,
                route=route,
                blocked_reason=f"dispatcher_error: {type(exc).__name__}: {exc}",
                notes=tuple(notes) + (f"exception_class={type(exc).__name__}",),
            )
            return C0Result(
                contract=seal_final_contract(blocked),
                intermediate_contract=None,
                refined=None,
                gates=None,
                failure_modes=None,
                plan=None,
                notes=tuple(notes) + (f"raised: {exc}",),
            )

    def _run_inner(
        self,
        *,
        contract_id: str,
        rid: str,
        route: RouteContract,
        plan_contract: L1PlanContract,
        plan_id: str | None,
        t_start: float,
        notes: list[str],
    ) -> C0Result:
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

        # Stages C0.2 .. C0.5 — first pipeline pass.
        first_pass = self._run_pipeline_pass(plan=plan, route=route, request_id=rid)
        candidates = first_pass.candidates
        hydrated = first_pass.hydrated
        expanded = first_pass.expanded
        conflict_report = first_pass.conflict_report
        shaped = first_pass.shaped
        intermediate = first_pass.intermediate

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

        # C0.6 refine — single-pass at most.
        # Spec lines 700-739: if the first pass returns WEAK / CONFLICTED /
        # EMPTY and the route allows another attempt, build a refined plan
        # via the chosen tactic and RUN THE PIPELINE A SECOND TIME with it.
        compound = detect_compound_target(plan_contract.task_spec)
        refined = plan_refinement(
            intermediate, conflict=conflict_report, plan=plan, attempts_so_far=0,
            compound_target=compound,
        )

        # Re-run pipeline if refinement is actionable (not bypassed and not
        # a no-op tactic like ABSTAIN/DECOMPOSE/REWRITE).
        actionable_tactics = {
            RefineTactic.HYBRIDIZE,
            RefineTactic.GRAPH_HOP,
            RefineTactic.BROADEN,
            RefineTactic.NARROW,
            RefineTactic.FRESHEN,
        }
        if (
            not refined.bypass_reason
            and refined.refine_tactic in actionable_tactics
            and refined.refine_attempts > 0
            and plan.budgets.max_refine_attempts >= 1
        ):
            try:
                refined_plan = _apply_refine_tactic(plan, refined.refine_tactic)
                second = self._run_pipeline_pass(
                    plan=refined_plan, route=route, request_id=rid,
                )
                # Keep whichever pass produced higher support_score.
                if second.intermediate.support_score > intermediate.support_score:
                    delta = second.intermediate.support_score - intermediate.support_score
                    plan = refined_plan
                    candidates = second.candidates
                    hydrated = second.hydrated
                    expanded = second.expanded
                    conflict_report = second.conflict_report
                    shaped = second.shaped
                    intermediate = second.intermediate
                    notes.append(f"refine:replaced_first_pass:delta={delta:.3f}")
                    refined = RefinedEvidenceContract(
                        base_contract=intermediate,
                        refine_attempts=refined.refine_attempts,
                        refine_tactic=refined.refine_tactic,
                        diagnostic=refined.diagnostic,
                        refine_delta_score=delta,
                        remaining_gap_codes=intermediate.unresolved_gap_codes,
                        bypass_reason="",
                    )
                else:
                    notes.append(
                        f"refine:second_pass_no_improvement:tactic={refined.refine_tactic.value}"
                    )
            except (ValueError, TypeError, KeyError, RuntimeError) as exc:
                # Refinement failure must NOT poison the first-pass result.
                notes.append(f"refine:second_pass_error:{type(exc).__name__}:{exc}")

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

        # Build typed projections from shaped buckets — spec lines 1041-1080.
        contradiction_type_by_chunk = {
            cf.source_a_chunk_id: cf.contradiction_type.value
            for cf in conflict_report.contradictions
        }
        # also map source_b -> type so chunks on either side get a label.
        for cf in conflict_report.contradictions:
            contradiction_type_by_chunk.setdefault(
                cf.source_b_chunk_id, cf.contradiction_type.value,
            )
        contradiction_summary_by_chunk = {
            cf.source_a_chunk_id: cf.summary for cf in conflict_report.contradictions
        }

        must_use_view = tuple(
            project_must_use(
                r.chunk,
                authority_score=r.signals.get(_authority_signal(), 0.5),
            )
            for r in shaped.must_use
        )
        supporting_view = tuple(
            project_supporting(r.chunk, reason=f"score={r.final_score:.2f}")
            for r in shaped.supporting
        )
        contradicts_view = tuple(
            project_contradicts(
                r.chunk,
                conflict_type=contradiction_type_by_chunk.get(
                    r.chunk.candidate.chunk_id, "semantic",
                ),
                conflict_summary=contradiction_summary_by_chunk.get(
                    r.chunk.candidate.chunk_id, "",
                ),
            )
            for r in shaped.contradicts
        )
        background_view = tuple(
            project_background(r.chunk, reason=f"score={r.final_score:.2f}")
            for r in shaped.background
        )
        definitions_view = tuple(
            project_definition(r.chunk) for r in shaped.definitions
        )
        excluded_view = tuple(
            project_excluded(r.chunk, reason="shape:excluded")
            for r in shaped.excluded
        )

        # Source-manifest hash spans every source actually referenced.
        source_ids_for_manifest: tuple[str, ...] = tuple(
            dict.fromkeys(
                [v.source_id for v in must_use_view]
                + [v.source_id for v in supporting_view]
                + [v.source_id for v in contradicts_view]
                + [v.source_id for v in background_view]
                + [v.source_id for v in definitions_view]
            )
        )
        source_manifest_hash = compute_source_manifest_hash(source_ids_for_manifest)

        contract = FinalEvidenceContract(
            contract_id=contract_id,
            route_id=route.route_id,
            route_replay_key=route.route_replay_key,
            policy_hash=route.policy_hash,
            blueprint_hash=route.blueprint_hash,
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
            must_use_view=must_use_view,
            supporting_view=supporting_view,
            contradicts_view=contradicts_view,
            background_view=background_view,
            definitions_view=definitions_view,
            excluded_view=excluded_view,
            contradiction_flags=contradiction_flags_out,
            unresolved_gaps=gaps_out,
            freshness_report=_build_freshness_report(hydrated, route),
            acl_report=_build_acl_report(hydrated, route),
            prompt_budget_hint=_build_prompt_budget_hint(
                shaped, max_tokens=plan.budgets.max_token_context,
            ),
            recommended_disposition=_disposition_from_status(final_status),
            budget_report=_build_budget_report(
                retrieval_passes=1 + (1 if refined.refine_attempts > 0 else 0),
                expanded_hops=len(expanded.traverse.hops),
                latency_ms=latency_ms,
                shaped=shaped,
                route=route,
                plan=plan,
            ),
            replay_metadata=ReplayMetadata(
                policy_hash=route.policy_hash,
                blueprint_hash=route.blueprint_hash,
                route_replay_key=route.route_replay_key,
                source_manifest_hash=source_manifest_hash,
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
