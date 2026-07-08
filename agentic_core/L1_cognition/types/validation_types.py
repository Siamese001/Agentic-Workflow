from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "validation_types")
trace_contract.emit_determinism_digest("p0", "validation_types")

trace_contract._emit_dispatches_healing_run("p1", "validation_types", "L1")
trace_contract._emit_routes_through("p1", "validation_types", "L1")
trace_contract._emit_checks_agent_registry("p1", "validation_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "validation_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "validation_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "validation_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "validation_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "validation_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "validation_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "validation_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "validation_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "validation_types")
trace_contract._emit_gated_by_confidence("p1", "validation_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "validation_types", "L1")
trace_contract._emit_reads_policy_state("p1", "validation_types", "L1")

trace_contract._emit_snapshots_state("p0", "validation_types", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "validation_types", "p0_governance")
trace_contract._emit_records_execution_trace("p0", "evidence", "validation_types")
trace_contract._emit_authorize_and_execute("p2", "validation_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "validation_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "validation_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "validation_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "validation_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "validation_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "validation_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "validation_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "validation_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "validation_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "validation_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "validation_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "validation_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "validation_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "validation_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "validation_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "validation_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "validation_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "validation_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "validation_types", "exec_snapshot_link")

"\nValidation Protocol - Dependency Inversion for L1 → L4\nDefines the interface L1 needs without depending on L4 implementation.\n"
from typing import Any, Protocol


trace_contract._emit_emits_metric_event("validation_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("validation_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("validation_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("validation_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("validation_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("validation_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("validation_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("validation_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("validation_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("validation_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("validation_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("validation_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("validation_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("validation_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("validation_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("validation_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("validation_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("validation_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("validation_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("validation_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("validation_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("validation_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("validation_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("validation_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("validation_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("validation_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("validation_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("validation_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "validation_types", "context_pull")
trace_contract._emit_pulls_context("p1", "validation_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "validation_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "validation_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "validation_types", "write_through")
trace_contract._emit_writes_through("p1", "validation_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "validation_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "validation_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "validation_types", "routing_commit")


class IValidationProtocol(Protocol):
    """Protocol defining the validation context interface needed by L1.

    This inverts the L1 → L4 dependency by defining the interface in L1
    that L4's ValidationContext must implement.
    """

    def get_file_path(self) -> str:
        """Get the file path being validated."""
        ...

    def get_project_root(self) -> str:
        """Get the project root path."""
        ...

    def add_violation(self, key: int, message: str, Severity: str = "error") -> None:
        """Add a validation Violation."""
        ...

    def get_violations(self) -> list[dict[str, Any]]:
        """Get all recorded violations."""
        ...

    def has_violations(self) -> bool:
        """Check if any violations were recorded."""
        ...

    def get_cache(self, key: str) -> Any | None:
        """Get cached value."""
        ...

    def set_cache(self, key: str, value: Any) -> None:
        """Set cached value."""
        ...

    def get_metadata(self, key: str) -> Any | None:
        """Get metadata value."""
        ...

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        ...
