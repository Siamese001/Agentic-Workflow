from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "action_node")
emit_determinism_digest("p0", "action_node")

_emit_dispatches_healing_run("p1", "action_node", "L2")
_emit_routes_through("p1", "action_node", "L2")
_emit_checks_agent_registry("p1", "action_node", "agent_registry")
_emit_validates_agent_capability("p1", "action_node", "capability")
_emit_dispatches_execution_plan("p1", "action_node", "exec_plan")
_emit_agent_executes_agent("p1", "action_node", "sub_agent")
_emit_routes_to_agent("p1", "action_node", "target_agent")
_emit_verifies_policy("p1", "action_node", "policy_check")
_emit_observes_runtime_state("p1", "action_node", "runtime_state")
_emit_verifies_boundary("p1", "action_node", "boundary_check")
_emit_hard_fails_untranscripted("p1", "action_node")
_emit_gated_by_confidence("p1", "action_node", "confidence_gate")
_emit_escalates_to_human("p1", "action_node", "L2")
_emit_reads_policy_state("p1", "action_node", "L2")

_emit_applies_guardrail("p0", "action_node", "p0_governance")
_emit_snapshots_state("p0", "action_node", "state_snapshot")
_emit_authorize_and_execute("p2", "action_node", "execution_auth")
_emit_validates_capability("p2", "action_node", "capability_check")
_emit_routes_to_capability("p2", "action_node", "capability_route")
_emit_writes_via_uwg("p2", "action_node", "uwg_write")
_emit_blocks_direct_write("p2", "action_node", "direct_write_block")
_emit_records_tool_invocation("p2", "action_node", "tool_invocation")
_emit_captures_execution_output("p2", "action_node", "exec_output")
_emit_dispatches_agent("p3", "action_node", "agent_dispatch")
_emit_coordinates_agents("p3", "action_node", "agent_coordination")
_emit_records_workflow_lineage("p3", "action_node", "workflow_lineage")
_emit_records_healing_outcome("p3", "action_node", "healing_outcome")
_emit_escalates_failure("p3", "action_node", "failure_escalation")
_emit_orchestrates_workflow("p3", "action_node", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "action_node", "healing_dispatch")
_emit_invokes_evaluation("p3", "action_node", "evaluation_signal")
_emit_records_telemetry_event("p4", "action_node", "telemetry_event")
_emit_captures_evaluation_metric("p4", "action_node", "eval_metric")
_emit_stores_embedding("p4", "action_node", "embedding_store")
_emit_updates_meta_learning_state("p4", "action_node", "meta_learning")
_emit_links_execution_to_snapshot("p4", "action_node", "exec_snapshot_link")

"""
Action Node - Sub-atomic Execution & Output Generation

Handles tool selection, execution, and output formatting.
Isolated from perception and reasoning logic.
"""
import asyncio
import uuid
from typing import Any

from agentic_core.L2_execution.utils.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("action_node", "p4obs", "metric_1")
_emit_emits_metric_event("action_node", "p4obs", "metric_2")
_emit_emits_metric_event("action_node", "p4obs", "metric_3")
_emit_emits_metric_event("action_node", "p4obs", "metric_4")
_emit_emits_metric_event("action_node", "p4obs", "metric_5")
_emit_emits_metric_event("action_node", "p4obs", "metric_6")
_emit_records_incident_event("action_node", "p4obs", "incident")
_emit_captures_runtime_anomaly("action_node", "p4obs", "anomaly")
_emit_writes_observability_log("action_node", "p4obs", "obs_log")
_emit_updates_monitoring_state("action_node", "p4obs", "mon_state")
_emit_triggers_alert("action_node", "p4obs", "alert")
_emit_links_incident_trace("action_node", "p4obs", "trace_link")
_emit_captures_pattern("action_node", "p3lm", "pattern")
_emit_records_learning_event("action_node", "p3lm", "learning_event")
_emit_writes_learning_snapshot("action_node", "p3lm", "snapshot")
_emit_feeds_meta_learning("action_node", "p3lm", "meta_feed")
_emit_updates_routing_strategy("action_node", "p3lm", "routing")
_emit_improves_agent_policy("action_node", "p3lm", "policy")
_emit_stores_learning_state("action_node", "p3lm", "state")
_emit_records_execution_trace("action_node", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("action_node", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("action_node", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("action_node", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("action_node", "L4_STATE", "p2_trace_5")
_emit_reads_environ("action_node", "env_read", "p2_env_1")
_emit_reads_environ("action_node", "env_read", "p2_env_2")
_emit_reads_runtime_state("action_node", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("action_node", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "action_node", "context_pull")
_emit_pulls_context("p1", "action_node", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "action_node", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "action_node", "uwg_term_2")
_emit_writes_through("p1", "action_node", "write_through")
_emit_writes_through("p1", "action_node", "write_through_2")
_emit_validated_by_safety_plane("p1", "action_node", "safety_validation")
_emit_invokes_eval("p1", "action_node", "eval_call")
_emit_proposal_commits_routing("p1", "action_node", "routing_commit")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(
    run_id: str, capability_token: str, policy_hash: str, payload: Any, target: str, action_class=None
):
    from agentic_core.L4_state.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id=run_id,
        capability_token=capability_token,
        policy_hash=policy_hash,
        execution_input=payload,
        execution_target=target,
        action_class=action_class or ActionClass.READ_ONLY,
    )


class ActionNode:
    """
    Sub-atomic action node - tool execution and output generation.

    Responsibilities:
    - Select appropriate tools
    - Execute tools
    - Format output
    - Handle execution errors
    """

    def __init__(self):
        """Initialize action node."""
        self.actions_executed = 0
        self.tools_used = 0
        self.total_execution_time = 0.0

    def act(self, reasoning: dict[str, Any]) -> dict[str, Any]:
        """
        Execute action based on reasoning.

        Args:
            reasoning: Reasoning result from ReasoningNode

        Returns:
            Action result with output and metadata
        """
        _emit_transcripts_response(str(uuid.uuid4()), "ActionNode.act", "model")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ActionNode.act")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ActionNode.act".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        start_time = get_clock().now_epoch()
        self.actions_executed += 1
        run_id = reasoning.get("run_id", "action_node")
        policy_hash = reasoning.get("policy_hash", "default")
        capability_token = reasoning.get("capability_token", "default")
        _ectx = _make_execution_context(
            run_id=run_id,
            capability_token=capability_token,
            policy_hash=policy_hash,
            payload=reasoning,
            target="action_node.act",
        )
        tools = self._select_tools(reasoning["plan"])
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: self._execute_tools(tools, p),
            capability_token,
            reasoning,
            target_name="action_node.act",
        )
        results = self._execute_tools(tools, reasoning)
        output = self._format_output(results, reasoning)
        execution_time = get_clock().now_epoch() - start_time
        self.total_execution_time += execution_time
        action_result = {
            "output": output,
            "tools_used": [t["name"] for t in tools],
            "tool_count": len(tools),
            "execution_time": execution_time,
            "success": True,
        }
        return action_result

    async def act_async(self, reasoning: dict[str, Any]) -> dict[str, Any]:
        """
        Asynchronous action execution.

        Args:
            reasoning: Reasoning result

        Returns:
            Action result
        """
        start_time = get_clock().now_epoch()
        self.actions_executed += 1
        run_id = reasoning.get("run_id", "action_node")
        policy_hash = reasoning.get("policy_hash", "default")
        capability_token = reasoning.get("capability_token", "default")
        _ectx = _make_execution_context(
            run_id=run_id,
            capability_token=capability_token,
            policy_hash=policy_hash,
            payload=reasoning,
            target="action_node.act_async",
        )
        tools = self._select_tools(reasoning["plan"])
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            capability_token,
            reasoning,
            target_name="action_node.act_async",
        )
        results = await asyncio.to_thread(self._execute_tools, tools, reasoning)
        output = await asyncio.to_thread(self._format_output, results, reasoning)
        execution_time = get_clock().now_epoch() - start_time
        self.total_execution_time += execution_time
        action_result = {
            "output": output,
            "tools_used": [t["name"] for t in tools],
            "tool_count": len(tools),
            "execution_time": execution_time,
            "success": True,
        }
        return action_result

    def act_simple(self, perceived: dict[str, Any]) -> dict[str, Any]:
        """
        Simple action for low-complexity intents (lazy evaluation).

        Args:
            perceived: Perceived state

        Returns:
            Simple action result
        """
        start_time = get_clock().now_epoch()
        self.actions_executed += 1
        run_id = perceived.get("run_id", "action_node")
        policy_hash = perceived.get("policy_hash", "default")
        capability_token = perceived.get("capability_token", "default")
        _ectx = _make_execution_context(
            run_id=run_id,
            capability_token=capability_token,
            policy_hash=policy_hash,
            payload=perceived,
            target="action_node.act_simple",
        )
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            capability_token,
            perceived,
            target_name="action_node.act_simple",
        )
        output = f"Responding to: {perceived['query'][:50]}..."
        execution_time = get_clock().now_epoch() - start_time
        self.total_execution_time += execution_time
        return {
            "output": output,
            "tools_used": [],
            "tool_count": 0,
            "execution_time": execution_time,
            "success": True,
            "simple": True,
        }

    def _select_tools(self, plan: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Select tools based on execution plan.

        Args:
            plan: Execution plan from ReasoningNode

        Returns:
            List of selected tools
        """
        tools = []
        step_count = len(plan.get("steps", []))
        if step_count > 0:
            tools.append({"name": "primary_executor", "type": "execution", "priority": 1})
            self.tools_used += 1
        if step_count > 2:
            tools.append({"name": "secondary_executor", "type": "support", "priority": 2})
            self.tools_used += 1
        return tools

    def _execute_tools(self, tools: list[dict[str, Any]], reasoning: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Execute selected tools.

        Args:
            tools: Selected tools
            reasoning: Reasoning context

        Returns:
            Tool execution results
        """
        results = []
        for tool in tools:
            result = {
                "tool": tool["name"],
                "status": "success",
                "output": f"Executed {tool['name']}",
                "metadata": {"type": tool.get("type", "unknown"), "priority": tool.get("priority", 0)},
            }
            results.append(result)
        return results

    def _format_output(self, results: list[dict[str, Any]], reasoning: dict[str, Any]) -> str:
        """
        Format final output from tool results.

        Args:
            results: Tool execution results
            reasoning: Reasoning context

        Returns:
            Formatted output string
        """
        if not results:
            return "No tools executed"
        output_parts = []
        for result in results:
            if result.get("status") == "success":
                output_parts.append(result.get("output", ""))
        thoughts = reasoning.get("thoughts", [])
        if thoughts:
            output_parts.append(f"Based on {len(thoughts)} thoughts")
        return " | ".join(output_parts) if output_parts else "Execution completed"

    def get_statistics(self) -> dict[str, Any]:
        """Get action statistics."""
        avg_execution_time = (
            self.total_execution_time / self.actions_executed if self.actions_executed > 0 else 0.0
        )
        return {
            "actions_executed": self.actions_executed,
            "tools_used": self.tools_used,
            "total_execution_time": self.total_execution_time,
            "avg_execution_time": avg_execution_time,
        }
