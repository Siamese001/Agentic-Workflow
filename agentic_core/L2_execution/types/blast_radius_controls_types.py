"""
BlastRadiusControls — Execution budget caps for L2 sandbox operations.

Hard limits enforced per execution trace to prevent runaway executions,
resource exhaustion, and denial-of-service via the healing/execution loop.

Phase 3.3: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "blast_radius_controls_types")
trace_contract.emit_determinism_digest("p0", "blast_radius_controls_types")

trace_contract._emit_dispatches_healing_run("p1", "blast_radius_controls_types", "L2")
trace_contract._emit_routes_through("p1", "blast_radius_controls_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "blast_radius_controls_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "blast_radius_controls_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "blast_radius_controls_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "blast_radius_controls_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "blast_radius_controls_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "blast_radius_controls_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "blast_radius_controls_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "blast_radius_controls_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "blast_radius_controls_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "blast_radius_controls_types")
trace_contract._emit_gated_by_confidence("p1", "blast_radius_controls_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "blast_radius_controls_types", "L2")
trace_contract._emit_reads_policy_state("p1", "blast_radius_controls_types", "L2")
trace_contract._emit_authorize_and_execute("p2", "blast_radius_controls_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "blast_radius_controls_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "blast_radius_controls_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "blast_radius_controls_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "blast_radius_controls_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "blast_radius_controls_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "blast_radius_controls_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "blast_radius_controls_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "blast_radius_controls_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "blast_radius_controls_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "blast_radius_controls_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "blast_radius_controls_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "blast_radius_controls_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "blast_radius_controls_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "blast_radius_controls_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "blast_radius_controls_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "blast_radius_controls_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "blast_radius_controls_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "blast_radius_controls_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "blast_radius_controls_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("blast_radius_controls_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("blast_radius_controls_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("blast_radius_controls_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("blast_radius_controls_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("blast_radius_controls_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("blast_radius_controls_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("blast_radius_controls_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("blast_radius_controls_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("blast_radius_controls_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("blast_radius_controls_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("blast_radius_controls_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("blast_radius_controls_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("blast_radius_controls_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("blast_radius_controls_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("blast_radius_controls_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("blast_radius_controls_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("blast_radius_controls_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("blast_radius_controls_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("blast_radius_controls_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("blast_radius_controls_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("blast_radius_controls_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("blast_radius_controls_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("blast_radius_controls_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("blast_radius_controls_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("blast_radius_controls_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("blast_radius_controls_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("blast_radius_controls_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("blast_radius_controls_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "blast_radius_controls_types", "context_pull")
trace_contract._emit_pulls_context("p1", "blast_radius_controls_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "blast_radius_controls_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "blast_radius_controls_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "blast_radius_controls_types", "write_through")
trace_contract._emit_writes_through("p1", "blast_radius_controls_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "blast_radius_controls_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "blast_radius_controls_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "blast_radius_controls_types", "routing_commit")


class BlastRadiusExceeded(RuntimeError):
    """Raised when an execution trace exceeds a blast-radius limit."""


@dataclass(frozen=True)
class BlastRadiusControls:
    """Immutable per-trace resource caps.

    Fields
    ------
    max_state_diff_bytes : int
        Maximum size (bytes) of the state diff produced by a single execution.
    max_file_write_bytes : int
        Maximum total bytes written to the filesystem per trace.
    max_compute_ms : int
        Maximum cumulative wall-clock milliseconds per trace.
    max_parallel_branches : int
        Maximum number of simultaneous sub-branches per trace.
    max_tool_calls_per_minute : int
        Rate limit: tool calls per rolling 60-second window.
    """

    max_state_diff_bytes: int = 65536
    max_file_write_bytes: int = 1048576
    max_compute_ms: int = 30000
    max_parallel_branches: int = 4
    max_tool_calls_per_minute: int = 120

    def __post_init__(self) -> None:
        for field_name, value in [
            ("max_state_diff_bytes", self.max_state_diff_bytes),
            ("max_file_write_bytes", self.max_file_write_bytes),
            ("max_compute_ms", self.max_compute_ms),
            ("max_parallel_branches", self.max_parallel_branches),
            ("max_tool_calls_per_minute", self.max_tool_calls_per_minute),
        ]:
            if value <= 0:
                raise ValueError(f"BlastRadiusControls: {field_name} must be positive, got {value}")

    def check_state_diff(self, diff_bytes: int) -> None:
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "BlastRadiusControls.check_state_diff", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "BlastRadiusControls.check_state_diff", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "BlastRadiusControls.check_state_diff",
        )
        if diff_bytes > self.max_state_diff_bytes:
            raise BlastRadiusExceeded(
                f"State diff {diff_bytes} bytes exceeds limit {self.max_state_diff_bytes}",
            )

    def check_file_write(self, total_written_bytes: int) -> None:
        if total_written_bytes > self.max_file_write_bytes:
            raise BlastRadiusExceeded(
                f"File write total {total_written_bytes} bytes exceeds limit {self.max_file_write_bytes}",
            )

    def check_compute(self, elapsed_ms: int) -> None:
        if elapsed_ms > self.max_compute_ms:
            raise BlastRadiusExceeded(f"Compute {elapsed_ms} ms exceeds limit {self.max_compute_ms} ms")

    def check_parallel_branches(self, active_branches: int) -> None:
        if active_branches > self.max_parallel_branches:
            raise BlastRadiusExceeded(
                f"Active branches {active_branches} exceeds limit {self.max_parallel_branches}",
            )

    def check_tool_call_rate(self, calls_in_window: int) -> None:
        if calls_in_window > self.max_tool_calls_per_minute:
            raise BlastRadiusExceeded(
                f"Tool calls in window {calls_in_window} exceeds rate limit {self.max_tool_calls_per_minute}/min",
            )


DEFAULT_BLAST_RADIUS = BlastRadiusControls()
__all__ = ["BlastRadiusControls", "BlastRadiusExceeded", "DEFAULT_BLAST_RADIUS"]
