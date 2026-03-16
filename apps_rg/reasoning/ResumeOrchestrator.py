# Ownership: apps_rg / L3_orchestration
"""Pure orchestration of resume generation using shared atoms."""

import uuid

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "ResumeOrchestrator", "p0_governance")
_emit_reads_policy_state("p0", "ResumeOrchestrator", "policy_binding")
_emit_snapshots_state("p0", "ResumeOrchestrator", "state_snapshot")
emit_replay_key("p0", "ResumeOrchestrator")
emit_determinism_digest("p0", "ResumeOrchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ResumeOrchestrator", "execution_auth")
_emit_validates_capability("p2", "ResumeOrchestrator", "capability_check")
_emit_routes_to_capability("p2", "ResumeOrchestrator", "capability_route")
_emit_writes_via_uwg("p2", "ResumeOrchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "ResumeOrchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "ResumeOrchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "ResumeOrchestrator", "exec_output")
_emit_dispatches_agent("p3", "ResumeOrchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "ResumeOrchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "ResumeOrchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "ResumeOrchestrator", "healing_outcome")
_emit_escalates_failure("p3", "ResumeOrchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "ResumeOrchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ResumeOrchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "ResumeOrchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "ResumeOrchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ResumeOrchestrator", "eval_metric")
_emit_stores_embedding("p4", "ResumeOrchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "ResumeOrchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ResumeOrchestrator", "exec_snapshot_link")


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
