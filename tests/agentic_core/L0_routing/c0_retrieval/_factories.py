"""Test factories for C0 — keep test files terse and consistent."""

from __future__ import annotations

from agentic_core.L0_routing.c0_retrieval import (
    CandidateChunk,
    CandidateEvidencePool,
    FreshnessClass,
    HydrationManifest,
    L1PlanContract,
    RetrievalScores,
    RouteContract,
    SourceClass,
    SupportTarget,
)
from agentic_core.L0_routing.c0_retrieval.verdicts import RetrievalLane


def make_route(
    *,
    route_id: str = "R3_GROUNDED",
    grounding_required: bool = True,
    support_target: SupportTarget = SupportTarget.SOURCE_SUMMARY,
    freshness_class: FreshnessClass = FreshnessClass.STATIC,
    tenant_scope: str = "tenantA",
    region: str = "us",
    data_class: str = "internal",
    allowed_data_classes: tuple[str, ...] = ("public", "internal"),
    max_hops: int = 1,
    max_refine_attempts: int = 1,
    max_token_context: int = 4000,
    token_budget: int = 4000,
    allowed_sources: tuple[SourceClass, ...] = (),
    disallowed_sources: tuple[SourceClass, ...] = (),
    fallback_policy: str = "caveat",
    policy_hash: str = "ph1",
    blueprint_hash: str = "bp1",
    route_replay_key: str = "rrk1",
) -> RouteContract:
    return RouteContract(
        route_id=route_id,
        grounding_required=grounding_required,
        execution_form="SINGLE_STEP",
        freshness_class=freshness_class,
        support_target=support_target,
        tenant_scope=tenant_scope,
        region=region,
        data_class=data_class,
        allowed_data_classes=allowed_data_classes,
        max_hops=max_hops,
        max_refine_attempts=max_refine_attempts,
        max_token_context=max_token_context,
        token_budget=token_budget,
        allowed_sources=allowed_sources,
        disallowed_sources=disallowed_sources,
        fallback_policy=fallback_policy,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        route_replay_key=route_replay_key,
    )


def make_plan_contract(
    *,
    task_spec: str = "answer the question",
    query_spec: str = "C0 retrieval scope",
    user_task_text: str = "What is C0?",
    grounding_required: bool = True,
) -> L1PlanContract:
    return L1PlanContract(
        task_spec=task_spec,
        query_spec=query_spec,
        user_task_text=user_task_text,
        grounding_required=grounding_required,
    )


def make_chunk(
    *,
    chunk_id: str = "c1",
    source_class: SourceClass = SourceClass.DOCS,
    text: str = "C0 retrieves evidence; it does not answer.",
    file_path: str = "docs/c0.md",
    line_range: tuple[int, int] = (1, 5),
    version: str = "v1.0",
    tenant: str = "tenantA",
    region: str = "us",
    data_class: str = "internal",
    found_by_lanes: tuple[RetrievalLane, ...] = (RetrievalLane.SPARSE, RetrievalLane.DENSE),
    raw_score: float = 0.85,
    normalized_score: float = 0.85,
    parent_chunk_id: str = "",
    section: str = "C0 ROLE",
) -> CandidateChunk:
    manifest = HydrationManifest(
        source_id=file_path,
        file_path=file_path,
        line_range=line_range,
        version=version,
        tenant=tenant,
        region=region,
        data_class=data_class,
        retrieval_lane=found_by_lanes[0] if found_by_lanes else RetrievalLane.DENSE,
        parent_chunk_id=parent_chunk_id,
        section=section,
    )
    return CandidateChunk(
        chunk_id=chunk_id,
        source_class=source_class,
        text=text,
        manifest=manifest,
        scores=RetrievalScores(
            raw_score=raw_score, normalized_score=normalized_score, rank=1,
        ),
        found_by_lanes=found_by_lanes,
    )


def make_pool(
    chunks: tuple[CandidateChunk, ...] = (),
    *,
    plan_id: str = "plan-test",
    lanes_used: tuple[RetrievalLane, ...] = (RetrievalLane.SPARSE, RetrievalLane.DENSE),
) -> CandidateEvidencePool:
    return CandidateEvidencePool(
        plan_id=plan_id,
        candidates=chunks,
        lanes_used=lanes_used,
    )
