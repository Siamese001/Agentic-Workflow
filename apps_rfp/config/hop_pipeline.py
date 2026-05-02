"""apps_rfp HOP pipeline topology.

Declares the 3-stage inner DAG for the proposal / RFP generator:
ingest RFP documents -> retrieve similar prior proposals ->
assemble proposal.

This substrate adoption is **additive**: the existing imperative
``BaseRfpEngine``-rooted runtime remains primary. The shared-substrate
entry point documented here lets future callers drive the same 3 stages
declaratively via ``HopPipelineExecutor``.

Plan: .windsurf/plans/apps-hop-substrate-four-apps-b4a2c9.md (Wave 2)
"""

from __future__ import annotations

from apps_shared.orchestration import HopRegistry, HopStageSpec

_STAGE_SPECS: list[HopStageSpec] = [
    HopStageSpec(
        stage_id=1,
        stage_name="rfp_ingestion",
        engine_module="apps_rfp.engines.hop_rfp_ingestion_engine",
        engine_class="HopRfpIngestionEngine",
        inputs=("rfp_request",),
        outputs=("ingested_rfp",),
        required=True,
    ),
    HopStageSpec(
        stage_id=2,
        stage_name="proposal_retrieval",
        engine_module="apps_rfp.engines.hop_proposal_retrieval_engine",
        engine_class="HopProposalRetrievalEngine",
        inputs=("rfp_request", "ingested_rfp"),
        outputs=("retrieved_proposals",),
        required=True,
    ),
    HopStageSpec(
        stage_id=3,
        stage_name="proposal_assembly",
        engine_module="apps_rfp.engines.hop_proposal_assembly_engine",
        engine_class="HopProposalAssemblyEngine",
        inputs=("rfp_request", "ingested_rfp", "retrieved_proposals"),
        outputs=("proposal",),
        required=True,
    ),
]


REGISTRY: HopRegistry = HopRegistry("apps_rfp").register_all(_STAGE_SPECS)


__all__ = ["REGISTRY"]
