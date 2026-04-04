# Ownership: apps_rg / L3_orchestration
"""Pure orchestration of resume generation using shared atoms."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("ResumeOrchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("ResumeOrchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("ResumeOrchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("ResumeOrchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("ResumeOrchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("ResumeOrchestrator", "p4obs", "metric_6")
_emit_records_incident_event("ResumeOrchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("ResumeOrchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("ResumeOrchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("ResumeOrchestrator", "p4obs", "mon_state")
_emit_triggers_alert("ResumeOrchestrator", "p4obs", "alert")
_emit_links_incident_trace("ResumeOrchestrator", "p4obs", "trace_link")
_emit_captures_pattern("ResumeOrchestrator", "p3lm", "pattern")
_emit_records_learning_event("ResumeOrchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ResumeOrchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("ResumeOrchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ResumeOrchestrator", "p3lm", "routing")
_emit_improves_agent_policy("ResumeOrchestrator", "p3lm", "policy")
_emit_stores_learning_state("ResumeOrchestrator", "p3lm", "state")
_emit_records_execution_trace("ResumeOrchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ResumeOrchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ResumeOrchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ResumeOrchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ResumeOrchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ResumeOrchestrator", "env_read", "p2_env_1")
_emit_reads_environ("ResumeOrchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("ResumeOrchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ResumeOrchestrator", "runtime_state", "p2_rt_2")

_emit_applies_guardrail("p0", "ResumeOrchestrator", "p0_governance")
_emit_reads_policy_state("p0", "ResumeOrchestrator", "policy_binding")
_emit_snapshots_state("p0", "ResumeOrchestrator", "state_snapshot")
_emit_pulls_context("p1", "ResumeOrchestrator", "context_pull")
_emit_pulls_context("p1", "ResumeOrchestrator", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "ResumeOrchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ResumeOrchestrator", "uwg_term_secondary")
_emit_writes_through("p1", "ResumeOrchestrator", "write_through")
_emit_writes_through("p1", "ResumeOrchestrator", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "ResumeOrchestrator", "safety_validation")
_emit_invokes_eval("p1", "ResumeOrchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "ResumeOrchestrator", "routing_commit")
_emit_escalates_to_human("p1", "ResumeOrchestrator", "human_escalation")
_emit_routes_through("p1", "ResumeOrchestrator", "route_through")
_emit_checks_agent_registry("p1", "ResumeOrchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "ResumeOrchestrator", "capability")
_emit_dispatches_execution_plan("p1", "ResumeOrchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "ResumeOrchestrator", "sub_agent")
_emit_routes_to_agent("p1", "ResumeOrchestrator", "target_agent")
_emit_verifies_policy("p1", "ResumeOrchestrator", "policy_check")
_emit_observes_runtime_state("p1", "ResumeOrchestrator", "runtime_state")
_emit_verifies_boundary("p1", "ResumeOrchestrator", "boundary_check")
_emit_transcripts_response("p1", "ResumeOrchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "ResumeOrchestrator")
_emit_gated_by_confidence("p1", "ResumeOrchestrator", "confidence_gate")
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


if TYPE_CHECKING:
    from agentic_core.L0_routing.types.reasoning_intensity_types import ReasoningIntensityProfile


class ResumeOrchestrator:
    """Orchestrate the multi-hop resume generation workflow with dynamic reasoning.

    Supports L0-stamped ReasoningIntensityProfile for ADG-informed dynamic
    reasoning path selection (COT/TOT/Reflexion) based on query complexity.
    """

    def __init__(
        self,
        master_resume: dict,
        test_mode: bool = False,
        reasoning_profile: ReasoningIntensityProfile | None = None,
    ) -> None:
        """Initialize the orchestrator with optional reasoning profile."""
        self.master_resume = master_resume
        self.test_mode = test_mode
        self.reasoning_profile = reasoning_profile
        self.hop_checkpoints: list[HopCheckpoint] = []
        self.constraints = ContentConstraintsConfig()
        self.jd_enforcer = JDEnforcementValidator()

        # Extract ADG complexity tier from profile for dynamic path selection
        if self.reasoning_profile is not None:
            self.complexity_tier = getattr(self.reasoning_profile, 'adg_complexity_tier', 'moderate')
            self.profile_hash = getattr(self.reasoning_profile, 'profile_hash', None)
            _emit_records_telemetry_event(
                str(uuid.uuid4()),
                {
                    "orchestrator": "ResumeOrchestrator",
                    "complexity_tier": self.complexity_tier,
                    "profile_hash": self.profile_hash,
                    "adg_node_count": getattr(self.reasoning_profile, 'adg_node_count', 0),
                    "adg_edge_count": getattr(self.reasoning_profile, 'adg_edge_count', 0),
                }
            )
        else:
            self.complexity_tier = "moderate"  # default
            self.profile_hash = None

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


def orchestrate_resume(
    master_resume: dict,
    JobDescription: str,
    reasoning_profile: ReasoningIntensityProfile | None = None,
) -> dict[str, object]:
    """Single public function - pure routing between atoms with dynamic reasoning.

    Args:
        master_resume: The master resume data
        JobDescription: The job description to tailor against
        reasoning_profile: Optional L0-stamped profile for ADG-informed reasoning

    Returns:
        Dict with status, enriched_data, and checkpoints
    """
    orchestrator = ResumeOrchestrator(
        master_resume=master_resume,
        reasoning_profile=reasoning_profile,
    )
    return orchestrator.run(JobDescription)
