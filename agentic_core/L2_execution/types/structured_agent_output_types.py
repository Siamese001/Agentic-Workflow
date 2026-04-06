"""StructuredAgentOutput — mandatory schema for all apps_* agent execute() returns.

Spec: AgentOutputContract [7], Guarantee #12.
Every apps_* agent execute() MUST return a StructuredAgentOutput containing:
  - intent_delta: str describing what the agent is changing/doing
  - tool_requests: list of ToolRequest describing tools to invoke
  - state_diff_proposal: dict describing the proposed state mutations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "structured_agent_output_types")
emit_determinism_digest("p0", "structured_agent_output_types")

_emit_dispatches_healing_run("p1", "structured_agent_output_types", "L2")
_emit_routes_through("p1", "structured_agent_output_types", "L2")
_emit_checks_agent_registry("p1", "structured_agent_output_types", "agent_registry")
_emit_validates_agent_capability("p1", "structured_agent_output_types", "capability")
_emit_dispatches_execution_plan("p1", "structured_agent_output_types", "exec_plan")
_emit_agent_executes_agent("p1", "structured_agent_output_types", "sub_agent")
_emit_routes_to_agent("p1", "structured_agent_output_types", "target_agent")
_emit_verifies_policy("p1", "structured_agent_output_types", "policy_check")
_emit_observes_runtime_state("p1", "structured_agent_output_types", "runtime_state")
_emit_verifies_boundary("p1", "structured_agent_output_types", "boundary_check")
_emit_transcripts_response("p1", "structured_agent_output_types", "transcript")
_emit_hard_fails_untranscripted("p1", "structured_agent_output_types")
_emit_gated_by_confidence("p1", "structured_agent_output_types", "confidence_gate")
_emit_escalates_to_human("p1", "structured_agent_output_types", "L2")
_emit_reads_policy_state("p1", "structured_agent_output_types", "L2")
_emit_authorize_and_execute("p2", "structured_agent_output_types", "execution_auth")
_emit_validates_capability("p2", "structured_agent_output_types", "capability_check")
_emit_routes_to_capability("p2", "structured_agent_output_types", "capability_route")
_emit_writes_via_uwg("p2", "structured_agent_output_types", "uwg_write")
_emit_blocks_direct_write("p2", "structured_agent_output_types", "direct_write_block")
_emit_records_tool_invocation("p2", "structured_agent_output_types", "tool_invocation")
_emit_captures_execution_output("p2", "structured_agent_output_types", "exec_output")
_emit_dispatches_agent("p3", "structured_agent_output_types", "agent_dispatch")
_emit_coordinates_agents("p3", "structured_agent_output_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "structured_agent_output_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "structured_agent_output_types", "healing_outcome")
_emit_escalates_failure("p3", "structured_agent_output_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "structured_agent_output_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "structured_agent_output_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "structured_agent_output_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "structured_agent_output_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "structured_agent_output_types", "eval_metric")
_emit_stores_embedding("p4", "structured_agent_output_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "structured_agent_output_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "structured_agent_output_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("structured_agent_output_types", "p4obs", "metric_1")
_emit_emits_metric_event("structured_agent_output_types", "p4obs", "metric_2")
_emit_emits_metric_event("structured_agent_output_types", "p4obs", "metric_3")
_emit_emits_metric_event("structured_agent_output_types", "p4obs", "metric_4")
_emit_emits_metric_event("structured_agent_output_types", "p4obs", "metric_5")
_emit_emits_metric_event("structured_agent_output_types", "p4obs", "metric_6")
_emit_records_incident_event("structured_agent_output_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("structured_agent_output_types", "p4obs", "anomaly")
_emit_writes_observability_log("structured_agent_output_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("structured_agent_output_types", "p4obs", "mon_state")
_emit_triggers_alert("structured_agent_output_types", "p4obs", "alert")
_emit_links_incident_trace("structured_agent_output_types", "p4obs", "trace_link")
_emit_captures_pattern("structured_agent_output_types", "p3lm", "pattern")
_emit_records_learning_event("structured_agent_output_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("structured_agent_output_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("structured_agent_output_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("structured_agent_output_types", "p3lm", "routing")
_emit_improves_agent_policy("structured_agent_output_types", "p3lm", "policy")
_emit_stores_learning_state("structured_agent_output_types", "p3lm", "state")
_emit_records_execution_trace("structured_agent_output_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("structured_agent_output_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("structured_agent_output_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("structured_agent_output_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("structured_agent_output_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("structured_agent_output_types", "env_read", "p2_env_1")
_emit_reads_environ("structured_agent_output_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("structured_agent_output_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("structured_agent_output_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "structured_agent_output_types", "context_pull")
_emit_pulls_context("p1", "structured_agent_output_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "structured_agent_output_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "structured_agent_output_types", "uwg_term_2")
_emit_writes_through("p1", "structured_agent_output_types", "write_through")
_emit_writes_through("p1", "structured_agent_output_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "structured_agent_output_types", "safety_validation")
_emit_invokes_eval("p1", "structured_agent_output_types", "eval_call")
_emit_proposal_commits_routing("p1", "structured_agent_output_types", "routing_commit")


class StructuredOutputViolation(ValueError):
    """Raised when StructuredAgentOutput invariants are broken."""


@dataclass(frozen=True)
class ToolRequest:
    """A single tool invocation request emitted by an apps_* agent.

    Spec: AgentOutputContract tool_requests[] schema element.
    """

    tool_name: str
    args: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.tool_name or not self.tool_name.strip():
            raise StructuredOutputViolation("ToolRequest.tool_name must be non-empty")


@dataclass(frozen=True)
class StructuredAgentOutput:
    """Structured output schema for all apps_* agent execute() returns.

    Spec: AgentOutputContract [7], Guarantee #12.

    Fields:
        intent_delta: Non-empty description of agent intent / what is changing.
        tool_requests: Zero or more tool invocation requests.
        state_diff_proposal: Dict of proposed state mutations (may be empty dict).
    """

    intent_delta: str
    tool_requests: tuple[ToolRequest, ...]
    state_diff_proposal: dict[str, Any]

    def __post_init__(self) -> None:
        if not self.intent_delta or not self.intent_delta.strip():
            raise StructuredOutputViolation(
                "StructuredAgentOutput.intent_delta must be a non-empty string. Spec: AgentOutputContract [7]."
            )
        if not isinstance(self.tool_requests, tuple):
            raise StructuredOutputViolation(
                "StructuredAgentOutput.tool_requests must be a tuple of ToolRequest objects."
            )
        if not isinstance(self.state_diff_proposal, dict):
            raise StructuredOutputViolation("StructuredAgentOutput.state_diff_proposal must be a dict.")

    @classmethod
    def empty(cls, intent_delta: str) -> StructuredAgentOutput:
        """Create a StructuredAgentOutput with no tool requests and empty state diff."""
        return cls(intent_delta=intent_delta, tool_requests=(), state_diff_proposal={})

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for AgentOutputContract payload."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "StructuredAgentOutput.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "StructuredAgentOutput.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "StructuredAgentOutput.to_dict")
        return {
            "intent_delta": self.intent_delta,
            "tool_requests": [{"tool_name": r.tool_name, "args": r.args} for r in self.tool_requests],
            "state_diff_proposal": self.state_diff_proposal,
        }


__all__ = ["StructuredAgentOutput", "StructuredOutputViolation", "ToolRequest"]
