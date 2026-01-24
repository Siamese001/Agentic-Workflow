"""
Resume Orchestrator Engine - L3 Manager handling HOP transitions
Refactored from orchestrate_resume.py + RgResumeOrchestratorAgent.py
Following Batch 1 specifications

HARDENING: Now acts as the State Controller. It initializes the Buffer with
'mission_input' and triggers the HOPs sequentially. It does NOT pass data
between HOPs directly - all data flows through the Immutable Buffer.
"""

from __future__ import annotations
from typing import Any
from dataclasses import dataclass, field
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine
from apps_rg.engines.hops.hop1_clerk_engine import ClerkExtractionEngine
from apps_rg.engines.hops.hop2_enrichment_engine import DataEnrichmentEngine

Logger = logging.getLogger(__name__)


@dataclass
class HopCheckpoint:
    hop_id: str
    status: str
    metrics: dict[str, Any] = field(default_factory=dict)


class ResumeOrchestratorEngine(BaseRGEngine):
    """
    L3 Orchestrator.
    Manages the Sovereign Data Flow via Immutable Buffer.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="ORCHESTRATOR_L3")
        self.hop_checkpoints: list[HopCheckpoint] = []

    async def execute(self, job_description: str) -> dict[str, Any]:
        """
        Orchestrate the full cycle.
        """
        self._mcp_audit("workflow_start")

        # 1. INITIALIZE BUFFER (The "Genesis" State)
        # We assume the context was pre-loaded with master_resume in the factory
        mission_input = {
            "job_description": job_description,
            "master_resume": getattr(self.ctx, "master_resume", {}),
        }

        try:
            self.ctx.buffer.write("mission_input", mission_input, source_agent=self.name)
        except PermissionError:
            Logger.warning("mission_input already exists in buffer (Retry cycle?)")

        try:
            # 2. EXECUTE HOP-1 (Clerk)
            # Notice: No arguments passed. Clerk reads from Buffer.
            clerk = ClerkExtractionEngine(self.ctx)
            await clerk.run()
            self.hop_checkpoints.append(HopCheckpoint("HOP-1", "COMPLETED"))

            # 3. EXECUTE HOP-2 (Enrichment)
            # Notice: No arguments. Enricher reads 'hop1_extraction' from Buffer.
            enricher = DataEnrichmentEngine(self.ctx)
            await enricher.run()
            self.hop_checkpoints.append(HopCheckpoint("HOP-2", "COMPLETED"))

            # 4. FINAL STATE
            final_state = self.ctx.buffer.read("hop2_enrichment")
            return {
                "status": "success",
                "checkpoints": [c.hop_id for c in self.hop_checkpoints],
                "final_output_summary": f"Processed {len(final_state.get('experience_sections', []))} sections",
            }

        except Exception as e:
            Logger.critical(f"Orchestration Failed: {e}")
            self.record_fail(f"Workflow Aborted: {e}", signal="SYSTEM_CRITICAL")
            raise
