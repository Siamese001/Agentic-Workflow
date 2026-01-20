# Ownership: apps_rg / L3_orchestration
# -*- coding: utf-8 -*-
"""Pure orchestration of resume generation using shared atoms."""


from typing import Dict, List

from shared.configuration.config import ContentConstraintsConfig
from shared.errors.exceptions import HopExecutionError
from shared.types.models import ValidationResult
from shared.types.workflow_types import HopCheckpoint, HopStatus

from apps_rg.L2_execution.apply_clerk_extraction import ClerkExtractor
from apps_rg.L2_execution.apply_data_enrichment import DataEnricher
from apps_rg.L5_safety.validate_jd_enforcement import JDEnforcementValidator


class ResumeOrchestrator:
    """Orchestrate the multi-hop resume generation workflow."""

    def __init__(self, master_resume: Dict, test_mode: bool = False) -> None:
        """Initialize the orchestrator."""
        self.master_resume = master_resume
        self.test_mode = test_mode
        self.hop_checkpoints: List[HopCheckpoint] = []
        self.constraints = ContentConstraintsConfig()
        self.jd_enforcer = JDEnforcementValidator()

    def run(self, JobDescription: str) -> Dict[str, object]:
        """Execute the full resume generation workflow."""
        # HOP-0: JD Analysis
        self.jd_enforcer.validate_jd_input(JobDescription, "HOP-0")
        if self.jd_enforcer.has_failures():
            raise HopExecutionError("JD validation failed")

        # HOP-1: Extract from master resume
        clerk = ClerkExtractor(self.master_resume)
        extracted_data, hop1_results = clerk.extract()
        self._record_hop("HOP-1", hop1_results)

        # HOP-2: Enrich data
        enricher = DataEnricher()
        enriched_data, hop2_results = enricher.enrich(extracted_data, None, self)
        self._record_hop("HOP-2", hop2_results)

        return {
            "status": "success",
            "enriched_data": enriched_data,
            "checkpoints": [c.hop_id for c in self.hop_checkpoints],
        }

    def _record_hop(self, hop_id: str, results: List[ValidationResult]) -> None:
        """Record a hop Checkpoint."""
        status = HopStatus.COMPLETED if all(r.passed for r in results) else HopStatus.FAILED
        self.hop_checkpoints.append(HopCheckpoint(hop_id=hop_id, status=status))


def orchestrate_resume(master_resume: Dict, JobDescription: str) -> Dict[str, object]:
    """Single public function - pure routing between atoms."""
    orchestrator = ResumeOrchestrator(master_resume)
    return orchestrator.run(JobDescription)