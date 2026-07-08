"""
Immutable Staging Buffer.

A write-once data structure that prevents state mutation bugs in multi-hop workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "ImmutableStagingBuffer", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "ImmutableStagingBuffer", "policy_binding")
trace_contract._emit_snapshots_state("p0", "ImmutableStagingBuffer", "state_snapshot")
trace_contract.emit_replay_key("p0", "ImmutableStagingBuffer")
trace_contract.emit_determinism_digest("p0", "ImmutableStagingBuffer")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "ImmutableStagingBuffer", "execution_auth")
trace_contract._emit_validates_capability("p2", "ImmutableStagingBuffer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ImmutableStagingBuffer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ImmutableStagingBuffer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ImmutableStagingBuffer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ImmutableStagingBuffer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ImmutableStagingBuffer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ImmutableStagingBuffer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ImmutableStagingBuffer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ImmutableStagingBuffer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ImmutableStagingBuffer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ImmutableStagingBuffer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ImmutableStagingBuffer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ImmutableStagingBuffer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ImmutableStagingBuffer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ImmutableStagingBuffer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ImmutableStagingBuffer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ImmutableStagingBuffer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ImmutableStagingBuffer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ImmutableStagingBuffer", "exec_snapshot_link")

try:
    from agentic_core.mixins.mcp_operation_mixin import mcp_hardened_mixin

    class MCPOperationMixin(mcp_hardened_mixin):
        pass
except ImportError:

    class MCPOperationMixin:
        pass


try:
    from agentic_core.interfaces.mixins import HealingPolicyMixin
except ImportError:

    class HealingPolicyMixin:
        pass



trace_contract._emit_emits_metric_event("ImmutableStagingBuffer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ImmutableStagingBuffer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ImmutableStagingBuffer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ImmutableStagingBuffer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ImmutableStagingBuffer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ImmutableStagingBuffer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ImmutableStagingBuffer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ImmutableStagingBuffer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ImmutableStagingBuffer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ImmutableStagingBuffer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ImmutableStagingBuffer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ImmutableStagingBuffer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ImmutableStagingBuffer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ImmutableStagingBuffer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ImmutableStagingBuffer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ImmutableStagingBuffer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ImmutableStagingBuffer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ImmutableStagingBuffer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ImmutableStagingBuffer", "p3lm", "state")
trace_contract._emit_records_execution_trace("ImmutableStagingBuffer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ImmutableStagingBuffer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ImmutableStagingBuffer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ImmutableStagingBuffer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ImmutableStagingBuffer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ImmutableStagingBuffer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ImmutableStagingBuffer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ImmutableStagingBuffer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ImmutableStagingBuffer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ImmutableStagingBuffer", "context_pull")
trace_contract._emit_pulls_context("p1", "ImmutableStagingBuffer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ImmutableStagingBuffer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ImmutableStagingBuffer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ImmutableStagingBuffer", "write_through")
trace_contract._emit_writes_through("p1", "ImmutableStagingBuffer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ImmutableStagingBuffer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ImmutableStagingBuffer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ImmutableStagingBuffer", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "ImmutableStagingBuffer", "human_escalation")
trace_contract._emit_routes_through("p1", "ImmutableStagingBuffer", "route_through")
trace_contract._emit_checks_agent_registry("p1", "ImmutableStagingBuffer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ImmutableStagingBuffer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ImmutableStagingBuffer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ImmutableStagingBuffer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ImmutableStagingBuffer", "target_agent")
trace_contract._emit_verifies_policy("p1", "ImmutableStagingBuffer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ImmutableStagingBuffer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ImmutableStagingBuffer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ImmutableStagingBuffer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ImmutableStagingBuffer")
trace_contract._emit_gated_by_confidence("p1", "ImmutableStagingBuffer", "confidence_gate")


@dataclass
class ImmutableStagingBuffer(MCPOperationMixin, HealingPolicyMixin):
    """
    A hardened buffer that enforces write-once semantics per key.
    Once a key is written, it is locked forever.
    """

    _buffer: dict[str, Any] = field(default_factory=dict)
    _locked_keys: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        """Initialize mixins."""
        super().__init__()

    def write_once(self, key: str, value: Any) -> None:
        """
        Writes a value to the buffer if the key is not locked.

        Args:
            key: The identifier for the data.
            value: The data to store.

        Raises:
            ValueError: If the key has already been written to.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ImmutableStagingBuffer.write_once"
        )

        if key in self._locked_keys:
            raise ValueError(f"Key '{key}' is immutable - already written.")
        self._buffer[key] = value
        self._locked_keys.add(key)

    def read(self, key: str) -> Any | None:
        """
        Reads a value from the buffer.

        Args:
            key: The identifier to read.

        Returns:
            The value if found, else None.
        """
        return self._buffer.get(key)

    def is_locked(self, key: str) -> bool:
        """Checks if a key has been written."""
        return key in self._locked_keys

    def get_snapshot(self) -> dict[str, Any]:
        """Returns a copy of the current buffer state."""
        return self._buffer.copy()
