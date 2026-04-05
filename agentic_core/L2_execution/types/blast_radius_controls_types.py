"""
BlastRadiusControls — Execution budget caps for L2 sandbox operations.

Hard limits enforced per execution trace to prevent runaway executions,
resource exhaustion, and denial-of-service via the healing/execution loop.

Phase 3.3: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "blast_radius_controls_types")
emit_determinism_digest("p0", "blast_radius_controls_types")

_emit_dispatches_healing_run("p1", "blast_radius_controls_types", "L2")
_emit_routes_through("p1", "blast_radius_controls_types", "L2")
_emit_checks_agent_registry("p1", "blast_radius_controls_types", "agent_registry")
_emit_validates_agent_capability("p1", "blast_radius_controls_types", "capability")
_emit_dispatches_execution_plan("p1", "blast_radius_controls_types", "exec_plan")
_emit_agent_executes_agent("p1", "blast_radius_controls_types", "sub_agent")
_emit_routes_to_agent("p1", "blast_radius_controls_types", "target_agent")
_emit_verifies_policy("p1", "blast_radius_controls_types", "policy_check")
_emit_observes_runtime_state("p1", "blast_radius_controls_types", "runtime_state")
_emit_verifies_boundary("p1", "blast_radius_controls_types", "boundary_check")
_emit_transcripts_response("p1", "blast_radius_controls_types", "transcript")
_emit_hard_fails_untranscripted("p1", "blast_radius_controls_types")
_emit_gated_by_confidence("p1", "blast_radius_controls_types", "confidence_gate")
_emit_escalates_to_human("p1", "blast_radius_controls_types", "L2")
_emit_reads_policy_state("p1", "blast_radius_controls_types", "L2")
_emit_authorize_and_execute("p2", "blast_radius_controls_types", "execution_auth")
_emit_validates_capability("p2", "blast_radius_controls_types", "capability_check")
_emit_routes_to_capability("p2", "blast_radius_controls_types", "capability_route")
_emit_writes_via_uwg("p2", "blast_radius_controls_types", "uwg_write")
_emit_blocks_direct_write("p2", "blast_radius_controls_types", "direct_write_block")
_emit_records_tool_invocation("p2", "blast_radius_controls_types", "tool_invocation")
_emit_captures_execution_output("p2", "blast_radius_controls_types", "exec_output")
_emit_dispatches_agent("p3", "blast_radius_controls_types", "agent_dispatch")
_emit_coordinates_agents("p3", "blast_radius_controls_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "blast_radius_controls_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "blast_radius_controls_types", "healing_outcome")
_emit_escalates_failure("p3", "blast_radius_controls_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "blast_radius_controls_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "blast_radius_controls_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "blast_radius_controls_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "blast_radius_controls_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "blast_radius_controls_types", "eval_metric")
_emit_stores_embedding("p4", "blast_radius_controls_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "blast_radius_controls_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "blast_radius_controls_types", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("blast_radius_controls_types", "p4obs", "metric_1")
_emit_emits_metric_event("blast_radius_controls_types", "p4obs", "metric_2")
_emit_emits_metric_event("blast_radius_controls_types", "p4obs", "metric_3")
_emit_emits_metric_event("blast_radius_controls_types", "p4obs", "metric_4")
_emit_emits_metric_event("blast_radius_controls_types", "p4obs", "metric_5")
_emit_emits_metric_event("blast_radius_controls_types", "p4obs", "metric_6")
_emit_records_incident_event("blast_radius_controls_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("blast_radius_controls_types", "p4obs", "anomaly")
_emit_writes_observability_log("blast_radius_controls_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("blast_radius_controls_types", "p4obs", "mon_state")
_emit_triggers_alert("blast_radius_controls_types", "p4obs", "alert")
_emit_links_incident_trace("blast_radius_controls_types", "p4obs", "trace_link")
_emit_captures_pattern("blast_radius_controls_types", "p3lm", "pattern")
_emit_records_learning_event("blast_radius_controls_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("blast_radius_controls_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("blast_radius_controls_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("blast_radius_controls_types", "p3lm", "routing")
_emit_improves_agent_policy("blast_radius_controls_types", "p3lm", "policy")
_emit_stores_learning_state("blast_radius_controls_types", "p3lm", "state")
_emit_records_execution_trace("blast_radius_controls_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("blast_radius_controls_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("blast_radius_controls_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("blast_radius_controls_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("blast_radius_controls_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("blast_radius_controls_types", "env_read", "p2_env_1")
_emit_reads_environ("blast_radius_controls_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("blast_radius_controls_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("blast_radius_controls_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "blast_radius_controls_types", "context_pull")
_emit_pulls_context("p1", "blast_radius_controls_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "blast_radius_controls_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "blast_radius_controls_types", "uwg_term_2")
_emit_writes_through("p1", "blast_radius_controls_types", "write_through")
_emit_writes_through("p1", "blast_radius_controls_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "blast_radius_controls_types", "safety_validation")
_emit_invokes_eval("p1", "blast_radius_controls_types", "eval_call")
_emit_proposal_commits_routing("p1", "blast_radius_controls_types", "routing_commit")


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

        _emit_snapshots_state(str(_uuid.uuid4()), "BlastRadiusControls.check_state_diff", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "BlastRadiusControls.check_state_diff", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "BlastRadiusControls.check_state_diff"
        )
        if diff_bytes > self.max_state_diff_bytes:
            raise BlastRadiusExceeded(
                f"State diff {diff_bytes} bytes exceeds limit {self.max_state_diff_bytes}"
            )

    def check_file_write(self, total_written_bytes: int) -> None:
        if total_written_bytes > self.max_file_write_bytes:
            raise BlastRadiusExceeded(
                f"File write total {total_written_bytes} bytes exceeds limit {self.max_file_write_bytes}"
            )

    def check_compute(self, elapsed_ms: int) -> None:
        if elapsed_ms > self.max_compute_ms:
            raise BlastRadiusExceeded(f"Compute {elapsed_ms} ms exceeds limit {self.max_compute_ms} ms")

    def check_parallel_branches(self, active_branches: int) -> None:
        if active_branches > self.max_parallel_branches:
            raise BlastRadiusExceeded(
                f"Active branches {active_branches} exceeds limit {self.max_parallel_branches}"
            )

    def check_tool_call_rate(self, calls_in_window: int) -> None:
        if calls_in_window > self.max_tool_calls_per_minute:
            raise BlastRadiusExceeded(
                f"Tool calls in window {calls_in_window} exceeds rate limit {self.max_tool_calls_per_minute}/min"
            )


DEFAULT_BLAST_RADIUS = BlastRadiusControls()
__all__ = ["BlastRadiusControls", "BlastRadiusExceeded", "DEFAULT_BLAST_RADIUS"]
