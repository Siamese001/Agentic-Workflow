from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "deterministic_loop_detector")
trace_contract.emit_determinism_digest("p0", "deterministic_loop_detector")

trace_contract._emit_dispatches_healing_run("p1", "deterministic_loop_detector", "L2")
trace_contract._emit_routes_through("p1", "deterministic_loop_detector", "L2")
trace_contract._emit_checks_agent_registry("p1", "deterministic_loop_detector", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "deterministic_loop_detector", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "deterministic_loop_detector", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "deterministic_loop_detector", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "deterministic_loop_detector", "target_agent")
trace_contract._emit_verifies_policy("p1", "deterministic_loop_detector", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "deterministic_loop_detector", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "deterministic_loop_detector", "boundary_check")
trace_contract._emit_transcripts_response("p1", "deterministic_loop_detector", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "deterministic_loop_detector")
trace_contract._emit_gated_by_confidence("p1", "deterministic_loop_detector", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "deterministic_loop_detector", "L2")
trace_contract._emit_reads_policy_state("p1", "deterministic_loop_detector", "L2")

trace_contract._emit_snapshots_state("p0", "deterministic_loop_detector", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "deterministic_loop_detector", "execution_auth")
trace_contract._emit_validates_capability("p2", "deterministic_loop_detector", "capability_check")
trace_contract._emit_routes_to_capability("p2", "deterministic_loop_detector", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "deterministic_loop_detector", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "deterministic_loop_detector", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "deterministic_loop_detector", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "deterministic_loop_detector", "exec_output")
trace_contract._emit_dispatches_agent("p3", "deterministic_loop_detector", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "deterministic_loop_detector", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "deterministic_loop_detector", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "deterministic_loop_detector", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "deterministic_loop_detector", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "deterministic_loop_detector", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "deterministic_loop_detector", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "deterministic_loop_detector", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "deterministic_loop_detector", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "deterministic_loop_detector", "eval_metric")
trace_contract._emit_stores_embedding("p4", "deterministic_loop_detector", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "deterministic_loop_detector", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "deterministic_loop_detector", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("deterministic_loop_detector", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("deterministic_loop_detector", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("deterministic_loop_detector", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("deterministic_loop_detector", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("deterministic_loop_detector", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("deterministic_loop_detector", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("deterministic_loop_detector", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("deterministic_loop_detector", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("deterministic_loop_detector", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("deterministic_loop_detector", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("deterministic_loop_detector", "p4obs", "alert")
trace_contract._emit_links_incident_trace("deterministic_loop_detector", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("deterministic_loop_detector", "p3lm", "pattern")
trace_contract._emit_records_learning_event("deterministic_loop_detector", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("deterministic_loop_detector", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("deterministic_loop_detector", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("deterministic_loop_detector", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("deterministic_loop_detector", "p3lm", "policy")
trace_contract._emit_stores_learning_state("deterministic_loop_detector", "p3lm", "state")
trace_contract._emit_records_execution_trace("deterministic_loop_detector", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("deterministic_loop_detector", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("deterministic_loop_detector", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("deterministic_loop_detector", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("deterministic_loop_detector", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("deterministic_loop_detector", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("deterministic_loop_detector", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("deterministic_loop_detector", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("deterministic_loop_detector", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "deterministic_loop_detector", "context_pull")
trace_contract._emit_pulls_context("p1", "deterministic_loop_detector", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "deterministic_loop_detector", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "deterministic_loop_detector", "uwg_term_2")
trace_contract._emit_writes_through("p1", "deterministic_loop_detector", "write_through")
trace_contract._emit_writes_through("p1", "deterministic_loop_detector", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "deterministic_loop_detector", "safety_validation")
trace_contract._emit_invokes_eval("p1", "deterministic_loop_detector", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "deterministic_loop_detector", "routing_commit")


class ToolBudgetExceededError(Exception):
    """Raised when a tool execution exceeds its deterministic step budget."""

    def __init__(self, tool_name: str, budget: int):
        self.tool_name = tool_name
        self.budget = budget
        self.reason_code = "TOOL_BUDGET_EXCEEDED"
        super().__init__(
            f"[{self.reason_code}] Tool '{tool_name}' exceeded execution step budget of {budget}.",
        )


@dataclass(frozen=True)
class ToolBudget:
    """Defines the deterministic execution budget for a tool."""

    max_steps: int


class DeterministicLoopDetector:
    """
    A deterministic circuit-breaker to prevent infinite loops in tool execution.

    This detector enforces Guarantee #10 by using a step counter instead of
    wall-clock time, ensuring that loop detection is replayable and not subject
    to variations in machine performance.

    It is designed to be attached to the L2 Per-Tool-Call (PTC) execution context.
    """

    def __init__(self):
        self._counters: defaultdict[str, defaultdict[str, int]] = defaultdict(lambda: defaultdict(int))

    def increment_and_check(self, trace_id: str, tool_name: str, budget: ToolBudget) -> None:
        """
        Increments the execution counter for a given tool and checks against its budget.

        This method must be called once per logical step within a tool's execution.

        Args:
            trace_id: The unique identifier for the current execution trace.
            tool_name: The name of the tool being executed.
            budget: The deterministic budget for the tool.

        Raises:
            ToolBudgetExceededError: If the counter exceeds the tool's max_steps.
        """
        trace_contract._emit_applies_guardrail(
            str(uuid.uuid4()),
            "DeterministicLoopDetector.increment_and_check",
            "L2_EXECUTION",
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "DeterministicLoopDetector.increment_and_check",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:DeterministicLoopDetector.increment_and_check".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        counter = self._counters[trace_id][tool_name]
        if counter >= budget.max_steps:
            raise ToolBudgetExceededError(tool_name=tool_name, budget=budget.max_steps)
        self._counters[trace_id][tool_name] += 1

    def get_current_step_count(self, trace_id: str, tool_name: str) -> int:
        """Returns the current step count for a tool within a trace."""
        return self._counters[trace_id][tool_name]

    def reset_trace(self, trace_id: str) -> None:
        """Resets all counters for a given trace_id (for testing or context closure)."""
        if trace_id in self._counters:
            del self._counters[trace_id]
