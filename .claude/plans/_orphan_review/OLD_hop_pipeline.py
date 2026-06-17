"""apps_rg HOP pipeline topology.

Declares the 7-stage resume generation inner DAG corresponding to the
HOP1..HOP7 config schemas already present in ``agent_spec_config.py``:

    HOP1  ClerkExtraction     ΓÇö parse JD + master resume
    HOP2  DataEnrichment      ΓÇö normalize extracted data
    HOP3  ResumeGeneration    ΓÇö LLM synthesis of tailored resume
    HOP4  FactCheck           ΓÇö cross-reference against master resume
    HOP5  BulletDiversityGate ΓÇö thematic-spread gate (evaluator-style)
    HOP6  ContentOptimizer    ΓÇö keyword/action-verb refinement
    HOP7  GenerationDiagnostics ΓÇö final scorecard + QA report

This substrate adoption is **additive**: the existing 606-line
``RgResumeOrchestrator.run()`` remains the primary runtime path (with
Qwen gateway, repo signals, and heal cycle). The substrate path here
lets new callers walk the same 7 stages declaratively via
``HopPipelineExecutor`` ΓÇö useful for replay, composability, and
seal_step integration.

See ``apps_rg/engines/hop_pipeline_adapters.py`` for the BaseModelΓåödict
adapters that keep this declaration side-by-side with the Pydantic-typed
``BaseRGEngine`` line.

Plan: .claude/plans/apps-hop-substrate-f7751b.md (Wave 3)
"""

from __future__ import annotations

from apps_shared.orchestration import HopRegistry, HopStageSpec

_STAGE_SPECS: list[HopStageSpec] = [
    HopStageSpec(
        stage_id=1,
        stage_name="clerk_extraction",
        engine_module="apps_rg.engines.hop_pipeline_adapters",
        engine_class="HopClerkExtractionEngine",
        inputs=("job_description", "master_resume"),
        outputs=("hop1_extraction",),
        required=True,
    ),
    HopStageSpec(
        stage_id=2,
        stage_name="data_enrichment",
        engine_module="apps_rg.engines.hop_pipeline_adapters",
        engine_class="HopDataEnrichmentEngine",
        inputs=("hop1_extraction",),
        outputs=("hop2_enrichment",),
        required=True,
    ),
    HopStageSpec(
        stage_id=3,
        stage_name="resume_generation",
        engine_module="apps_rg.engines.hop_pipeline_adapters",
        engine_class="HopResumeGenerationEngine",
        inputs=("hop2_enrichment", "master_resume", "job_description"),
        outputs=("generated_resume",),
        required=True,
    ),
    HopStageSpec(
        stage_id=4,
        stage_name="fact_check",
        engine_module="apps_rg.engines.hop_pipeline_adapters",
        engine_class="HopFactCheckEngine",
        inputs=("generated_resume", "master_resume"),
        outputs=("fact_check_report",),
        required=True,
    ),
    HopStageSpec(
        stage_id=5,
        stage_name="bullet_diversity_gate",
        engine_module="apps_rg.engines.hop_pipeline_adapters",
        engine_class="HopBulletDiversityGateEngine",
        inputs=("generated_resume", "fact_check_report"),
        outputs=("passed", "gate_reason"),
        required=True,
        gate=True,
    ),
    HopStageSpec(
        stage_id=6,
        stage_name="content_optimizer",
        engine_module="apps_rg.engines.hop_pipeline_adapters",
        engine_class="HopContentOptimizerEngine",
        inputs=("generated_resume",),
        outputs=("optimized_resume",),
        required=True,
    ),
    HopStageSpec(
        stage_id=7,
        stage_name="generation_diagnostics",
        engine_module="apps_rg.engines.hop_pipeline_adapters",
        engine_class="HopGenerationDiagnosticsEngine",
        inputs=("optimized_resume", "fact_check_report"),
        outputs=("qa_report",),
        required=True,
    ),
]


REGISTRY: HopRegistry = HopRegistry("apps_rg").register_all(_STAGE_SPECS)


__all__ = ["REGISTRY"]
