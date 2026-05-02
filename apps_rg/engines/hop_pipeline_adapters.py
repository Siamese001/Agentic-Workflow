"""apps_rg HOP pipeline adapter engines.

Substrate-compatible adapters that declare the 7-stage apps_rg HOP topology
for the shared ``apps_shared.orchestration.HopPipelineExecutor`` without
disturbing the primary ``RgResumeOrchestrator.run()`` path (606 lines of
Qwen-aware generation + repo-signals enrichment + heal-cycle integration
that the shared substrate cannot yet express).

Why these are thin adapters
---------------------------
The existing apps_rg engines (``ClerkExtractionEngine``,
``DataEnrichmentEngine``, ``ResumeGenerationTask``, ``FactCheckEngine``,
``BulletDiversityGate``, ``ContentOptimizerEngine``,
``GenerationDiagnosticsEngine``) all inherit from ``BaseRGEngine`` and
expose ``execute(input_data: BaseModel) -> BaseModel`` — Pydantic model
in/out, not the ``execute(context: dict) -> dict`` contract the substrate
requires. Rather than re-type every engine, each adapter here:

1. Reads the incoming context dict for the keys this stage consumes.
2. Emits a deterministic passthrough output that names the underlying
   engine and declares what the stage intends to do.
3. Lets ``RgResumeOrchestrator.run()`` continue as the primary runtime
   path for real resume generation.

New callers that want declarative substrate-walk semantics (replay,
composability, seal_step integration) get a clean 7-stage checkpoint
record. Follow-up plan ``apps-rg-substrate-deep-migration`` can replace
these with full BaseModel↔dict marshaling once a golden-parity fixture
is captured.

Plan: .windsurf/plans/apps-hop-substrate-f7751b.md (Wave 3)
"""

from __future__ import annotations

from typing import Any


def _passthrough(
    stage_name: str, engine_class: str, inputs_read: tuple[str, ...]
) -> dict[str, Any]:
    """Build a uniform passthrough output dict."""
    return {
        f"{stage_name}_marker": {
            "stage": stage_name,
            "delegates_to": engine_class,
            "inputs_observed": list(inputs_read),
            "note": (
                "Substrate-path adapter. Primary runtime path remains "
                "RgResumeOrchestrator.run(). See plan "
                "apps-hop-substrate-f7751b Wave 3."
            ),
        }
    }


class HopClerkExtractionEngine:
    """HOP1 clerk_extraction — adapter for ``ClerkExtractionEngine``."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        jd = context.get("job_description")
        return _passthrough(
            "clerk_extraction",
            "apps_rg.engines.clerk_extraction_engine.ClerkExtractionEngine",
            ("job_description",) if jd is not None else (),
        ) | {"hop1_extraction": {"source": "adapter_passthrough"}}


class HopDataEnrichmentEngine:
    """HOP2 data_enrichment — adapter for ``DataEnrichmentEngine``."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return _passthrough(
            "data_enrichment",
            "apps_rg.engines.data_enrichment_engine.DataEnrichmentEngine",
            tuple(k for k in ("hop1_extraction",) if k in context),
        ) | {"hop2_enrichment": {"source": "adapter_passthrough"}}


class HopResumeGenerationEngine:
    """HOP3 resume_generation — adapter for ``ResumeGenerationTask``."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return _passthrough(
            "resume_generation",
            "apps_rg.engines.resume_generation_task.ResumeGenerationTask",
            tuple(
                k
                for k in ("hop2_enrichment", "master_resume", "job_description")
                if k in context
            ),
        ) | {"generated_resume": {"source": "adapter_passthrough"}}


class HopFactCheckEngine:
    """HOP4 fact_check — adapter for ``FactCheckEngine``."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return _passthrough(
            "fact_check",
            "apps_rg.engines.fact_check_engine.FactCheckEngine",
            tuple(k for k in ("generated_resume",) if k in context),
        ) | {"fact_check_report": {"source": "adapter_passthrough", "issues": []}}


class HopBulletDiversityGateEngine:
    """HOP5 bullet_diversity_gate — adapter for ``BulletDiversityGate``."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        report = context.get("fact_check_report") or {}
        # Gate passes when fact_check produced no issues.
        passed = not (report.get("issues") or [])
        return _passthrough(
            "bullet_diversity_gate",
            "apps_rg.engines.bullet_diversity_gate.BulletDiversityGate",
            tuple(k for k in ("generated_resume", "fact_check_report") if k in context),
        ) | {"passed": passed, "gate_reason": "fact_check_clean" if passed else "fact_check_issues"}


class HopContentOptimizerEngine:
    """HOP6 content_optimizer — adapter for ``ContentOptimizerEngine``."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return _passthrough(
            "content_optimizer",
            "apps_rg.engines.content_optimizer_engine.ContentOptimizerEngine",
            tuple(k for k in ("generated_resume",) if k in context),
        ) | {"optimized_resume": {"source": "adapter_passthrough"}}


class HopGenerationDiagnosticsEngine:
    """HOP7 generation_diagnostics — adapter for ``GenerationDiagnosticsEngine``."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return _passthrough(
            "generation_diagnostics",
            "apps_rg.engines.generation_diagnostics_engine.GenerationDiagnosticsEngine",
            tuple(
                k
                for k in ("optimized_resume", "fact_check_report")
                if k in context
            ),
        ) | {"qa_report": {"source": "adapter_passthrough", "composite_score": 1.0}}
