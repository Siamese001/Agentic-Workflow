"""apps_exec HOP pipeline topology.

Declares the 4-stage inner DAG for the executive brief generator:
ingest source documents -> retrieve similar prior briefs ->
extract capability evidence -> assemble brief.

This substrate adoption is **additive**: the existing imperative
``BaseExecEngine``-rooted runtime remains primary. The shared-substrate
entry point documented here lets future callers drive the same 4 stages
declaratively via ``HopPipelineExecutor``.

Plan: .windsurf/plans/apps-hop-substrate-four-apps-b4a2c9.md (Wave 3)
"""

from __future__ import annotations

from apps_shared.orchestration import HopRegistry, HopStageSpec

_STAGE_SPECS: list[HopStageSpec] = [
    HopStageSpec(
        stage_id=1,
        stage_name="ingestion",
        engine_module="apps_exec.engines.hop_ingestion_engine",
        engine_class="HopIngestionEngine",
        inputs=("exec_request",),
        outputs=("ingested_documents",),
        required=True,
    ),
    HopStageSpec(
        stage_id=2,
        stage_name="brief_retrieval",
        engine_module="apps_exec.engines.hop_brief_retrieval_engine",
        engine_class="HopBriefRetrievalEngine",
        inputs=("exec_request", "ingested_documents"),
        outputs=("retrieved_briefs",),
        required=True,
    ),
    HopStageSpec(
        stage_id=3,
        stage_name="capability_extraction",
        engine_module="apps_exec.engines.hop_capability_extraction_engine",
        engine_class="HopCapabilityExtractionEngine",
        inputs=("ingested_documents",),
        outputs=("extracted_capabilities",),
        required=True,
    ),
    HopStageSpec(
        stage_id=4,
        stage_name="brief_assembly",
        engine_module="apps_exec.engines.hop_brief_assembly_engine",
        engine_class="HopBriefAssemblyEngine",
        inputs=(
            "exec_request",
            "ingested_documents",
            "retrieved_briefs",
            "extracted_capabilities",
        ),
        outputs=("exec_brief",),
        required=True,
    ),
]


REGISTRY: HopRegistry = HopRegistry("apps_exec").register_all(_STAGE_SPECS)


__all__ = ["REGISTRY"]
