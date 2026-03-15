# Ownership: apps_rg / L3_orchestration
"""Pure orchestration of resume generation using shared atoms."""

import uuid

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class ResumeOrchestrator:
    """Orchestrate the multi-hop resume generation workflow."""

    def __init__(self, master_resume: dict, test_mode: bool = False) -> None:
        """Initialize the orchestrator."""
        self.master_resume = master_resume
        self.test_mode = test_mode
        self.hop_checkpoints: list[HopCheckpoint] = []
        self.constraints = ContentConstraintsConfig()
        self.jd_enforcer = JDEnforcementValidator()

    def run(self, JobDescription: str) -> dict[str, object]:
        """Execute the full resume generation workflow."""
        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ResumeOrchestrator.run")
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

    def _record_hop(self, hop_id: str, results: list[ValidationResult]) -> None:
        """Record a hop Checkpoint."""
        status = HopStatus.COMPLETED if all(r.passed for r in results) else HopStatus.FAILED
        self.hop_checkpoints.append(HopCheckpoint(hop_id=hop_id, status=status))


def orchestrate_resume(master_resume: dict, JobDescription: str) -> dict[str, object]:
    """Single public function - pure routing between atoms."""
    orchestrator = ResumeOrchestrator(master_resume)
    return orchestrator.run(JobDescription)
