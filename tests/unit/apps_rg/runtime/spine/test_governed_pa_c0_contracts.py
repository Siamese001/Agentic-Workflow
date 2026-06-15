from __future__ import annotations

import pytest

from apps_rg.runtime.spine.governed_pa_c0_contracts import (
    CandidateChunk,
    ChunkBoundaryRisk,
    FinalEvidenceContract,
    FreshnessClass,
    HydratedChunk,
    HydrationManifest,
    L1PlanContract,
    QualityFlags,
    RetrievalLane,
    RouteContract,
    SourceClass,
    SupportStatus,
    SupportTarget,
)


def _hydrated_chunk() -> HydratedChunk:
    manifest = HydrationManifest(
        source_id="fact_001",
        file_path="resume.json",
        section="experience",
        line_range=(10, 12),
    )
    candidate = CandidateChunk(
        chunk_id="chunk_001",
        source_class=SourceClass.DOCS,
        text="Delivered platform modernization.",
        manifest=manifest,
        found_by_lanes=(RetrievalLane.GRAPH_SEED,),
    )
    quality = QualityFlags(
        span_resolves=True,
        source_version_current=True,
        acl_clear=True,
        parent_context_available=True,
        citation_anchor_stable=True,
        chunk_boundary_risk=ChunkBoundaryRisk.LOW,
    )
    return HydratedChunk(
        candidate=candidate,
        canonical_source_path="resume.json",
        section_hierarchy=("experience",),
        chunk_version="v1",
        citation_anchor_candidates=("fact_001",),
        quality=quality,
    )


def test_governed_pa_c0_contracts_accept_valid_shapes() -> None:
    chunk = _hydrated_chunk()
    fec = FinalEvidenceContract(
        contract_id="fec_001",
        route_id="route_001",
        status=SupportStatus.PASS,
        support_score=0.95,
        must_use=(chunk,),
    )
    route = RouteContract(
        route_id="route_001",
        grounding_required=True,
        execution_form="SINGLE_STEP",
        freshness_class=FreshnessClass.CURRENT,
        support_target=SupportTarget.CLAIM_CHECK,
        tenant_scope="tenant",
    )
    plan = L1PlanContract(task_spec="write headline", query_spec="facts for headline")

    assert fec.must_use[0].candidate.chunk_id == "chunk_001"
    assert route.execution_form == "SINGLE_STEP"
    assert plan.grounding_required is True


def test_governed_pa_c0_contracts_fail_closed_on_invalid_shapes() -> None:
    with pytest.raises(ValueError, match="source_id required"):
        HydrationManifest(source_id="")
    with pytest.raises(ValueError, match="invalid line_range"):
        HydrationManifest(source_id="fact", line_range=(3, 2))
    with pytest.raises(ValueError, match="chunk_id required"):
        CandidateChunk(
            chunk_id="",
            source_class=SourceClass.DOCS,
            text="x",
            manifest=HydrationManifest(source_id="fact"),
            found_by_lanes=(RetrievalLane.DENSE,),
        )
    with pytest.raises(ValueError, match="text must not be empty"):
        CandidateChunk(
            chunk_id="chunk",
            source_class=SourceClass.DOCS,
            text="",
            manifest=HydrationManifest(source_id="fact"),
            found_by_lanes=(RetrievalLane.DENSE,),
        )
    with pytest.raises(ValueError, match="missing lane provenance"):
        CandidateChunk(
            chunk_id="chunk",
            source_class=SourceClass.DOCS,
            text="x",
            manifest=HydrationManifest(source_id="fact"),
        )
    with pytest.raises(ValueError, match="canonical_source_path required"):
        HydratedChunk(
            candidate=_hydrated_chunk().candidate,
            canonical_source_path="",
            section_hierarchy=(),
            chunk_version="v1",
            citation_anchor_candidates=(),
            quality=_hydrated_chunk().quality,
        )


def test_route_and_evidence_contract_validation() -> None:
    with pytest.raises(ValueError, match="support_score=1.5"):
        FinalEvidenceContract(contract_id="fec", route_id="route", support_score=1.5)
    with pytest.raises(TypeError, match="status must be SupportStatus"):
        FinalEvidenceContract(contract_id="fec", route_id="route", status="PASS")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="invalid execution_form"):
        RouteContract(
            route_id="route",
            grounding_required=True,
            execution_form="single_step",
            freshness_class=FreshnessClass.CURRENT,
            support_target=SupportTarget.CLAIM_CHECK,
            tenant_scope="tenant",
        )
    with pytest.raises(TypeError, match="task_spec must be str"):
        L1PlanContract(task_spec={"bad": "shape"}, query_spec="query")  # type: ignore[arg-type]
