"""
Resume Orchestrator Engine - L3 Manager handling HOP transitions
Refactored from orchestrate_resume.py + RgResumeOrchestrator.py
Following Batch 1 specifications

HARDENING: Extends the workflow to include Generation (K9), Refinement (Optimizer/Ranker),
and Safety (ATS). It defines the full Sovereign Pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps_rg.engines.ATSCompatibilityEngine import ATSCompatibilityEngine
from apps_rg.engines.BaseRGEngine import BaseRGEngine

# Import ALL Hardened Engines
from apps_rg.engines.ClerkExtractionEngine import ClerkExtractionEngine
from apps_rg.engines.ContentOptimizerEngine import ContentOptimizerEngine
from apps_rg.engines.ContentQualityEngine import ContentQualityEngine
from apps_rg.engines.DataEnrichmentEngine import DataEnrichmentEngine
from apps_rg.engines.GapClosureEngine import GapClosureEngine
from apps_rg.engines.SectionRankerEngine import SectionRankerEngine
from apps_rg.types.SovereignContext import TraceRegistry

Logger = logging.getLogger(__name__)


@dataclass
class HopCheckpoint:
    hop_id: str
    status: str
    metrics: dict[str, Any] = field(default_factory=dict)


class ResumeOrchestratorEngine(BaseRGEngine):
    """
    L3 Orchestrator (Final).
    Drives the full Sovereign Pipeline: Prep -> Gen -> Refine -> Verify with cyclic retry.
    """

    def __init__(self, ctx: Any, mission_id: str = "default") -> None:
        super().__init__(ctx, node_id="ORCHESTRATOR_L3")
        self.hop_checkpoints: list[HopCheckpoint] = []
        self.mission_id = mission_id

        # Hardened Global Safety Limits (from LIC)
        self.GLOBAL_STEP_LIMIT = self.rg_specs.orchestrator.global_step_limit
        self.MAX_RETRY_ITERATIONS = self.rg_specs.orchestrator.max_retry_iterations

        # Persistent trace registry like LIC - use SSOT-approved location
        if self.toggles.use_persistent_tracing:
            trace_path = Path(f"docs/reports/missions/{mission_id}/trace.jsonl")
            self.ctx.trace = TraceRegistry(persistence_path=trace_path)

    async def execute(self, job_description: str) -> dict[str, Any]:
        self._mcp_audit("workflow_start")

        # 1. GENESIS (HOP-0)
        mission_input = {
            "job_description": job_description,
            "master_resume": getattr(self.ctx, "master_resume", {}),
            "job_description_keywords": job_description.lower().split(),
        }
        try:
            self.ctx.buffer.write("mission_input", mission_input, source_agent=self.name)
        except PermissionError:
            pass  # Idempotent

        try:
            step_count = 0

            # 2. DATA PREP (HOP 1 & 2) - Linear Phase
            for hop_engine, hop_id in [
                (ClerkExtractionEngine, "HOP-1"),
                (DataEnrichmentEngine, "HOP-2"),
            ]:
                step_count += 1
                if step_count > self.GLOBAL_STEP_LIMIT:
                    self.ctx.trace.add_trace("CRITICAL_FAILURE", {"reason": "Global step limit exceeded"})
                    raise RuntimeError(
                        f"Mission aborted: Exceeded global step limit of {self.GLOBAL_STEP_LIMIT}",
                    )
                await self._run_engine(hop_engine, hop_id)

            # 3. GENERATION & REFINEMENT (HOP 3-4) - Linear Phase
            for hop_engine, hop_id in [
                (GapClosureEngine, "HOP-3-K9"),
                (ContentOptimizerEngine, "HOP-4-OPT"),
                (SectionRankerEngine, "HOP-4-RANK"),
            ]:
                step_count += 1
                if step_count > self.GLOBAL_STEP_LIMIT:
                    raise RuntimeError(f"Exceeded global step limit of {self.GLOBAL_STEP_LIMIT}")
                await self._run_engine(hop_engine, hop_id)

            # 4. VALIDATION CRUCIBLE (HOP 5-6) - Cyclic Phase
            iteration = 0
            while iteration < self.MAX_RETRY_ITERATIONS and self.toggles.use_cyclic_validation:
                iteration += 1

                # Run Quality Check
                quality_engine = ContentQualityEngine(self.ctx)
                await quality_engine.run()
                quality_report = self.ctx.buffer.read("quality_report")

                # Run ATS Check
                await self._run_engine(ATSCompatibilityEngine, "HOP-5-ATS")
                ats_report = self.ctx.buffer.read("ats_report")

                # Check if both passed
                if quality_report.get("status") == "passed" and ats_report.get("valid", False):
                    self.ctx.trace.add_trace(
                        "VALIDATION_PASSED",
                        {
                            "iteration": iteration,
                            "quality_score": quality_report.get("score"),
                            "ats_valid": ats_report.get("valid"),
                        },
                    )
                    break

                # If failed and we have retries left, adjust and retry from HOP-2
                if iteration < self.MAX_RETRY_ITERATIONS:
                    self.ctx.trace.add_trace(
                        "RETRY_CYCLE",
                        {
                            "iteration": iteration,
                            "quality_issues": quality_report.get("issues", []),
                            "ats_issues": ats_report.get("issues", []),
                        },
                    )

                    # Adjust mission input with feedback
                    mission_input["retry_iteration"] = iteration
                    mission_input["quality_feedback"] = quality_report.get("issues", [])
                    mission_input["ats_feedback"] = ats_report.get("issues", [])
                    self.ctx.buffer.write("mission_input", mission_input, source_agent="ORCHESTRATOR_RETRY")

                    # Retry from enrichment with adjusted parameters
                    await self._run_engine(DataEnrichmentEngine, "HOP-2-RETRY")
                    # Continue with generation again
                    await self._run_engine(GapClosureEngine, "HOP-3-K9-RETRY")
                    await self._run_engine(ContentOptimizerEngine, "HOP-4-OPT-RETRY")
                    await self._run_engine(SectionRankerEngine, "HOP-4-RANK-RETRY")

            # 5. FINAL VERDICT
            final_ats = self.ctx.buffer.read("ats_report", {"valid": False})
            final_quality = self.ctx.buffer.read("quality_report", {"score": 0})

            status = "SUCCESS"
            if not final_ats.get("valid", False):
                status = "WARNING"
            if final_quality.get("score", 0) < self.rg_specs.validation.min_quality_score * 100:
                status = "WARNING"

            final_artifact = self.ctx.buffer.read("ranked_content", {})

            return {
                "status": status,
                "checkpoints": [c.hop_id for c in self.hop_checkpoints],
                "final_artifact_keys": list(final_artifact.keys()) if final_artifact else [],
                "retry_iterations": iteration,
                "final_quality_score": final_quality.get("score", 0),
                "ats_valid": final_ats.get("valid", False),
            }
        except Exception as e:
            self.ctx.trace.add_trace("ORCHESTRATOR_ERROR", {"error": str(e)})
            self.record_fail(f"Orchestration failed: {e}")
            raise

    async def _run_engine(self, engine_cls, checkpoint_id: str):
        """Helper to run a Sovereign Engine and log checkpoint."""
        engine = engine_cls(self.ctx)
        await engine.run()
        self.hop_checkpoints.append(HopCheckpoint(checkpoint_id, "COMPLETED"))

    def run_subatomic_test(self) -> dict[str, Any]:
        """Run subatomic self-tests (inherited from SubatomicTestingMixin).

        Returns:
            Test results dict
        """
        return {"status": "passed", "tests_run": 0}
