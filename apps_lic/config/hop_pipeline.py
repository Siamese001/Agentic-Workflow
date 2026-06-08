"""apps_lic HOP pipeline topology.

Declares the 9-stage inner DAG that runs inside the L2 authorize_and_execute
step of ``l2_execute_apps_lic`` (product path via canonical_dispatch).

Per Author-Gate 2026-05-01 (`architecture_choice`, selected=
`shared_substrate_hop_pipeline`) this file is the SSOT for apps_lic stage
topology. Domain logic per stage lives in
``apps_lic/engines/<stage_name>_engine.py``; the walk is delegated to
``apps_shared.orchestration.HopPipelineExecutor``.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-hop-substrate-f7751b.md (Wave 2 Phase 2.1)

Historical note
---------------
The 9 stage names are preserved from the pre-2026-02-08 consolidation
(which reduced 190 -> 149 agents by collapsing HOP1..HOP9 classes into
one parameterized executor). The stage *bodies* were lost in that
refactor; the engines referenced below are fresh re-derivations
implementing the minimum I/O contract each stage's name implies, not
resurrections from git.
"""

from __future__ import annotations

from apps_shared.orchestration import HopRegistry, HopStageSpec

_STAGE_SPECS: list[HopStageSpec] = [
    HopStageSpec(
        stage_id=1,
        stage_name="profile_analysis",
        engine_module="apps_lic.engines.profile_analysis_engine",
        engine_class="ProfileAnalysisEngine",
        inputs=("campaign_request",),
        outputs=("profile_features",),
        required=True,
    ),
    HopStageSpec(
        stage_id=2,
        stage_name="research",
        engine_module="apps_lic.engines.research_engine",
        engine_class="ResearchEngine",
        # Bounded C0/manual/preloaded evidence only; no live research delegation.
        inputs=("profile_features", "retrieval_chunks"),
        outputs=("evidence_bundle",),
        required=True,
    ),
    HopStageSpec(
        stage_id=3,
        stage_name="sender_grounding",
        engine_module="apps_lic.engines.sender_grounding_engine",
        engine_class="SenderGroundingEngine",
        inputs=("campaign_request",),
        outputs=("sender_persona",),
        required=True,
    ),
    HopStageSpec(
        stage_id=4,
        stage_name="routing",
        engine_module="apps_lic.engines.routing_engine",
        engine_class="RoutingEngine",
        inputs=("profile_features", "evidence_bundle", "sender_persona"),
        outputs=("routing_decision", "generation_prompt"),
        required=True,
    ),
    HopStageSpec(
        stage_id=5,
        stage_name="generation",
        engine_module="apps_lic.engines.generation_engine",
        engine_class="GenerationEngine",
        inputs=("generation_prompt", "sender_persona"),
        outputs=("draft_message",),
        required=True,
    ),
    HopStageSpec(
        stage_id=6,
        stage_name="validation",
        engine_module="apps_lic.engines.validation_engine",
        engine_class="ValidationEngine",
        inputs=("draft_message", "evidence_bundle"),
        outputs=("validation_report",),
        required=True,
    ),
    HopStageSpec(
        stage_id=7,
        stage_name="gate_decision",
        engine_module="apps_lic.engines.gate_decision_engine",
        engine_class="GateDecisionEngine",
        inputs=("validation_report",),
        outputs=("passed", "gate_reason"),
        required=True,
        gate=True,
    ),
    HopStageSpec(
        stage_id=8,
        stage_name="qa_report",
        engine_module="apps_lic.engines.qa_report_engine",
        engine_class="QaReportEngine",
        inputs=("draft_message", "validation_report", "evidence_bundle"),
        outputs=("qa_report",),
        required=True,
    ),
    HopStageSpec(
        stage_id=9,
        stage_name="integration",
        engine_module="apps_lic.engines.integration_engine",
        engine_class="IntegrationEngine",
        inputs=(
            "campaign_request",
            "draft_message",
            "validation_report",
            "qa_report",
        ),
        outputs=("lic_run_record_fields",),
        required=True,
    ),
]


REGISTRY: HopRegistry = HopRegistry("apps_lic").register_all(_STAGE_SPECS)
"""Module-level SSOT. Import as:

    from apps_lic.config.hop_pipeline import REGISTRY
"""


__all__ = ["REGISTRY"]
