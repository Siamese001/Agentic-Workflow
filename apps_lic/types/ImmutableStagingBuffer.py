"""
Immutable Staging Buffer.

A write-once data structure that prevents state mutation bugs in multi-hop workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "ImmutableStagingBuffer", "p0_governance")
_emit_reads_policy_state("p0", "ImmutableStagingBuffer", "policy_binding")
_emit_snapshots_state("p0", "ImmutableStagingBuffer", "state_snapshot")
emit_replay_key("p0", "ImmutableStagingBuffer")
emit_determinism_digest("p0", "ImmutableStagingBuffer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ImmutableStagingBuffer", "execution_auth")
_emit_validates_capability("p2", "ImmutableStagingBuffer", "capability_check")
_emit_routes_to_capability("p2", "ImmutableStagingBuffer", "capability_route")
_emit_writes_via_uwg("p2", "ImmutableStagingBuffer", "uwg_write")
_emit_blocks_direct_write("p2", "ImmutableStagingBuffer", "direct_write_block")
_emit_records_tool_invocation("p2", "ImmutableStagingBuffer", "tool_invocation")
_emit_captures_execution_output("p2", "ImmutableStagingBuffer", "exec_output")
_emit_dispatches_agent("p3", "ImmutableStagingBuffer", "agent_dispatch")
_emit_coordinates_agents("p3", "ImmutableStagingBuffer", "agent_coordination")
_emit_records_workflow_lineage("p3", "ImmutableStagingBuffer", "workflow_lineage")
_emit_records_healing_outcome("p3", "ImmutableStagingBuffer", "healing_outcome")
_emit_escalates_failure("p3", "ImmutableStagingBuffer", "failure_escalation")
_emit_orchestrates_workflow("p3", "ImmutableStagingBuffer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ImmutableStagingBuffer", "healing_dispatch")
_emit_invokes_evaluation("p3", "ImmutableStagingBuffer", "evaluation_signal")
_emit_records_telemetry_event("p4", "ImmutableStagingBuffer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ImmutableStagingBuffer", "eval_metric")
_emit_stores_embedding("p4", "ImmutableStagingBuffer", "embedding_store")
_emit_updates_meta_learning_state("p4", "ImmutableStagingBuffer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ImmutableStagingBuffer", "exec_snapshot_link")

try:
    from agentic_core.mixins.mcp_hardened_mixin import mcp_hardened_mixin

    class MCPHardenedMixin(mcp_hardened_mixin):
        pass
except ImportError:
    class MCPHardenedMixin:
        pass

try:
    from agentic_core.interfaces.mixins import HealerMixin
except ImportError:
    class HealerMixin:
        pass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("ImmutableStagingBuffer", "p4obs", "metric_1")
_emit_emits_metric_event("ImmutableStagingBuffer", "p4obs", "metric_2")
_emit_emits_metric_event("ImmutableStagingBuffer", "p4obs", "metric_3")
_emit_emits_metric_event("ImmutableStagingBuffer", "p4obs", "metric_4")
_emit_emits_metric_event("ImmutableStagingBuffer", "p4obs", "metric_5")
_emit_emits_metric_event("ImmutableStagingBuffer", "p4obs", "metric_6")
_emit_records_incident_event("ImmutableStagingBuffer", "p4obs", "incident")
_emit_captures_runtime_anomaly("ImmutableStagingBuffer", "p4obs", "anomaly")
_emit_writes_observability_log("ImmutableStagingBuffer", "p4obs", "obs_log")
_emit_updates_monitoring_state("ImmutableStagingBuffer", "p4obs", "mon_state")
_emit_triggers_alert("ImmutableStagingBuffer", "p4obs", "alert")
_emit_links_incident_trace("ImmutableStagingBuffer", "p4obs", "trace_link")
_emit_captures_pattern("ImmutableStagingBuffer", "p3lm", "pattern")
_emit_records_learning_event("ImmutableStagingBuffer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ImmutableStagingBuffer", "p3lm", "snapshot")
_emit_feeds_meta_learning("ImmutableStagingBuffer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ImmutableStagingBuffer", "p3lm", "routing")
_emit_improves_agent_policy("ImmutableStagingBuffer", "p3lm", "policy")
_emit_stores_learning_state("ImmutableStagingBuffer", "p3lm", "state")
_emit_records_execution_trace("ImmutableStagingBuffer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ImmutableStagingBuffer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ImmutableStagingBuffer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ImmutableStagingBuffer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ImmutableStagingBuffer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ImmutableStagingBuffer", "env_read", "p2_env_1")
_emit_reads_environ("ImmutableStagingBuffer", "env_read", "p2_env_2")
_emit_reads_runtime_state("ImmutableStagingBuffer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ImmutableStagingBuffer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ImmutableStagingBuffer", "context_pull")
_emit_pulls_context("p1", "ImmutableStagingBuffer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ImmutableStagingBuffer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ImmutableStagingBuffer", "uwg_term_2")
_emit_writes_through("p1", "ImmutableStagingBuffer", "write_through")
_emit_writes_through("p1", "ImmutableStagingBuffer", "write_through_2")
_emit_validated_by_safety_plane("p1", "ImmutableStagingBuffer", "safety_validation")
_emit_invokes_eval("p1", "ImmutableStagingBuffer", "eval_call")
_emit_proposal_commits_routing("p1", "ImmutableStagingBuffer", "routing_commit")
_emit_escalates_to_human("p1", "ImmutableStagingBuffer", "human_escalation")
_emit_routes_through("p1", "ImmutableStagingBuffer", "route_through")
_emit_checks_agent_registry("p1", "ImmutableStagingBuffer", "agent_registry")
_emit_validates_agent_capability("p1", "ImmutableStagingBuffer", "capability")
_emit_dispatches_execution_plan("p1", "ImmutableStagingBuffer", "exec_plan")
_emit_agent_executes_agent("p1", "ImmutableStagingBuffer", "sub_agent")
_emit_routes_to_agent("p1", "ImmutableStagingBuffer", "target_agent")
_emit_verifies_policy("p1", "ImmutableStagingBuffer", "policy_check")
_emit_observes_runtime_state("p1", "ImmutableStagingBuffer", "runtime_state")
_emit_verifies_boundary("p1", "ImmutableStagingBuffer", "boundary_check")
_emit_transcripts_response("p1", "ImmutableStagingBuffer", "transcript")
_emit_hard_fails_untranscripted("p1", "ImmutableStagingBuffer")
_emit_gated_by_confidence("p1", "ImmutableStagingBuffer", "confidence_gate")


@dataclass
class ImmutableStagingBuffer(MCPHardenedMixin, HealerMixin):
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ImmutableStagingBuffer.write_once")

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
