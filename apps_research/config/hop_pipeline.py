"""apps_research HOP pipeline topology.

Declares the 3-stage inner DAG for the autonomous research pipeline:
retrieve prior research artifacts -> generate company brief ->
assemble final research artifact.

This substrate adoption is **additive**: the existing imperative runtime
(``BaseResearchEngine`` subclasses driven by
``apps_research/integrations/execution_adapter.py``) remains the primary
path. The shared-substrate entry point documented here lets future
callers drive the same 3 stages declaratively via the standard
``HopPipelineExecutor`` surface — useful for replay, composability, and
per-stage checkpointing.

Plan: .windsurf/plans/apps-hop-substrate-four-apps-b4a2c9.md (Wave 1)
"""

from __future__ import annotations

from apps_shared.orchestration import HopRegistry, HopStageSpec

_STAGE_SPECS: list[HopStageSpec] = [
    HopStageSpec(
        stage_id=1,
        stage_name="research_retrieval",
        engine_module="apps_research.engines.hop_research_retrieval_engine",
        engine_class="HopResearchRetrievalEngine",
        inputs=("research_request",),
        outputs=("retrieved_research",),
        required=True,
    ),
    HopStageSpec(
        stage_id=2,
        stage_name="company_brief",
        engine_module="apps_research.engines.hop_company_brief_engine",
        engine_class="HopCompanyBriefEngine",
        inputs=("research_request", "retrieved_research"),
        outputs=("company_brief",),
        required=True,
    ),
    HopStageSpec(
        stage_id=3,
        stage_name="research_assembly",
        engine_module="apps_research.engines.hop_research_assembly_engine",
        engine_class="HopResearchAssemblyEngine",
        inputs=("research_request", "retrieved_research", "company_brief"),
        outputs=("research_artifact",),
        required=True,
    ),
]


REGISTRY: HopRegistry = HopRegistry("apps_research").register_all(_STAGE_SPECS)


__all__ = ["REGISTRY"]
