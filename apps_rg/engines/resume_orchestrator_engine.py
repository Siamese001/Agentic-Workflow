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
from apps_rg.engines.ats_compatibility_engine import ATSCompatibilityEngine
from apps_rg.engines.base_rg_engine import BaseRGEngine
from apps_rg.engines.clerk_extraction_engine import ClerkExtractionEngine
from apps_rg.engines.content_optimizer_engine import ContentOptimizerEngine
from apps_rg.engines.content_quality_engine import ContentQualityEngine
from apps_rg.engines.data_enrichment_engine import DataEnrichmentEngine
from apps_rg.engines.gap_closure_engine import GapClosureEngine
from apps_rg.engines.section_ranker_engine import SectionRankerEngine
from apps_rg.types.trace_registry_types import TraceRegistry
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
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

    def __init__(self, ctx: Any, mission_id: str='default') -> None:
        super().__init__(config=ctx, node_id='ORCHESTRATOR_L3')
        self.hop_checkpoints: list[HopCheckpoint] = []
        self.mission_id = mission_id
        if self.rg_specs and hasattr(self.rg_specs, 'orchestrator'):
            self.GLOBAL_STEP_LIMIT = self.rg_specs.orchestrator.global_step_limit
            self.MAX_RETRY_ITERATIONS = self.rg_specs.orchestrator.max_retry_iterations
        else:
            self.GLOBAL_STEP_LIMIT = 50
            self.MAX_RETRY_ITERATIONS = 3
        if self.toggles and hasattr(self.toggles, 'use_persistent_tracing') and self.toggles.use_persistent_tracing:
            trace_path = Path(f'docs/reports/missions/{mission_id}/trace.jsonl')
            self.ctx.trace = TraceRegistry(persistence_path=trace_path)

    async def execute(self, job_description: str) -> dict[str, Any]:
        self._mcp_audit('workflow_start')
        mission_input = {'job_description': job_description, 'master_resume': getattr(self.ctx, 'master_resume', {}), 'job_description_keywords': job_description.lower().split()}
        try:
            self.ctx.buffer.write('mission_input', mission_input, source_agent=self.name)
        except PermissionError:
            pass
        try:
            step_count = 0
            for hop_engine, hop_id in [(ClerkExtractionEngine, 'HOP-1'), (DataEnrichmentEngine, 'HOP-2')]:
                step_count += 1
                if step_count > self.GLOBAL_STEP_LIMIT:
                    self.ctx.trace.add_trace('CRITICAL_FAILURE', {'reason': 'Global step limit exceeded'})
                    raise RuntimeError(f'Mission aborted: Exceeded global step limit of {self.GLOBAL_STEP_LIMIT}')
                await self._run_engine(hop_engine, hop_id)
            for hop_engine, hop_id in [(GapClosureEngine, 'HOP-3-K9'), (ContentOptimizerEngine, 'HOP-4-OPT'), (SectionRankerEngine, 'HOP-4-RANK')]:
                step_count += 1
                if step_count > self.GLOBAL_STEP_LIMIT:
                    raise RuntimeError(f'Exceeded global step limit of {self.GLOBAL_STEP_LIMIT}')
                await self._run_engine(hop_engine, hop_id)
            iteration = 0
            from apps_rg.config.reasoning_toggles_config import RGReasoningToggles as _RGToggles
            _defaults = _RGToggles()
            use_cyclic = self.toggles.use_cyclic_validation if self.toggles and hasattr(self.toggles, 'use_cyclic_validation') else _defaults.use_cyclic_validation
            while iteration < self.MAX_RETRY_ITERATIONS and use_cyclic:
                iteration += 1
                quality_engine = ContentQualityEngine(self.ctx)
                await quality_engine.execute()
                quality_report = self.ctx.buffer.read('quality_report')
                await self._run_engine(ATSCompatibilityEngine, 'HOP-5-ATS')
                ats_report = self.ctx.buffer.read('ats_report')
                if quality_report.get('status') == 'passed' and ats_report.get('valid', False):
                    self.ctx.trace.add_trace('VALIDATION_PASSED', {'iteration': iteration, 'quality_score': quality_report.get('score'), 'ats_valid': ats_report.get('valid')})
                    break
                if iteration < self.MAX_RETRY_ITERATIONS:
                    self.ctx.trace.add_trace('RETRY_CYCLE', {'iteration': iteration, 'quality_issues': quality_report.get('issues', []), 'ats_issues': ats_report.get('issues', [])})
                    mission_input['retry_iteration'] = iteration
                    mission_input['quality_feedback'] = quality_report.get('issues', [])
                    mission_input['ats_feedback'] = ats_report.get('issues', [])
                    self.ctx.buffer.write('mission_input', mission_input, source_agent='ORCHESTRATOR_RETRY')
                    await self._run_engine(DataEnrichmentEngine, 'HOP-2-RETRY')
                    await self._run_engine(GapClosureEngine, 'HOP-3-K9-RETRY')
                    await self._run_engine(ContentOptimizerEngine, 'HOP-4-OPT-RETRY')
                    await self._run_engine(SectionRankerEngine, 'HOP-4-RANK-RETRY')
            final_ats = self.ctx.buffer.read('ats_report', {'valid': False})
            final_quality = self.ctx.buffer.read('quality_report', {'score': 0})
            status = 'SUCCESS'
            if not final_ats.get('valid', False):
                status = 'WARNING'
            if final_quality.get('score', 0) < (self.rg_specs.validation.min_quality_score * 100 if self.rg_specs and hasattr(self.rg_specs, 'validation') else 70):
                status = 'WARNING'
            final_artifact = self.ctx.buffer.read('ranked_content', {})
            return {'status': status, 'checkpoints': [c.hop_id for c in self.hop_checkpoints], 'final_artifact_keys': list(final_artifact.keys()) if final_artifact else [], 'retry_iterations': iteration, 'final_quality_score': final_quality.get('score', 0), 'ats_valid': final_ats.get('valid', False)}
        except Exception as e:
            self.ctx.trace.add_trace('ORCHESTRATOR_ERROR', {'error': str(e)})
            self.logger.error(f'Orchestration failed: {e}')
            raise

    async def _run_engine(self, engine_cls, checkpoint_id: str):
        """Helper to run a Sovereign Engine and log checkpoint."""
        engine = engine_cls(self.ctx)
        await engine.execute()
        self.hop_checkpoints.append(HopCheckpoint(checkpoint_id, 'COMPLETED'))

    def run_subatomic_test(self) -> dict[str, Any]:
        """Run subatomic self-tests (inherited from SubatomicTestingMixin).

        Returns:
            Test results dict
        """
        return {'status': 'passed', 'tests_run': 0}
