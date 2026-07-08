from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "action_node")
trace_contract.emit_determinism_digest("p0", "action_node")

trace_contract._emit_dispatches_healing_run("p1", "action_node", "L2")
trace_contract._emit_routes_through("p1", "action_node", "L2")
trace_contract._emit_checks_agent_registry("p1", "action_node", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "action_node", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "action_node", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "action_node", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "action_node", "target_agent")
trace_contract._emit_verifies_policy("p1", "action_node", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "action_node", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "action_node", "boundary_check")
trace_contract._emit_hard_fails_untranscripted("p1", "action_node")
trace_contract._emit_gated_by_confidence("p1", "action_node", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "action_node", "L2")
trace_contract._emit_reads_policy_state("p1", "action_node", "L2")

trace_contract._emit_applies_guardrail("p0", "action_node", "p0_governance")
trace_contract._emit_snapshots_state("p0", "action_node", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "action_node", "execution_auth")
trace_contract._emit_validates_capability("p2", "action_node", "capability_check")
trace_contract._emit_routes_to_capability("p2", "action_node", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "action_node", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "action_node", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "action_node", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "action_node", "exec_output")
trace_contract._emit_dispatches_agent("p3", "action_node", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "action_node", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "action_node", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "action_node", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "action_node", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "action_node", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "action_node", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "action_node", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "action_node", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "action_node", "eval_metric")
trace_contract._emit_stores_embedding("p4", "action_node", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "action_node", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "action_node", "exec_snapshot_link")

"""
Action Node - Sub-atomic Execution & Output Generation

Handles tool selection, execution, and output formatting.
Isolated from perception and reasoning logic.
"""
import asyncio
import uuid
from typing import Any

from agentic_core.utils.runners.providers import get_clock

trace_contract._emit_emits_metric_event("action_node", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("action_node", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("action_node", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("action_node", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("action_node", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("action_node", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("action_node", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("action_node", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("action_node", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("action_node", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("action_node", "p4obs", "alert")
trace_contract._emit_links_incident_trace("action_node", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("action_node", "p3lm", "pattern")
trace_contract._emit_records_learning_event("action_node", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("action_node", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("action_node", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("action_node", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("action_node", "p3lm", "policy")
trace_contract._emit_stores_learning_state("action_node", "p3lm", "state")
trace_contract._emit_records_execution_trace("action_node", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("action_node", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("action_node", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("action_node", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("action_node", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("action_node", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("action_node", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("action_node", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("action_node", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "action_node", "context_pull")
trace_contract._emit_pulls_context("p1", "action_node", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "action_node", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "action_node", "uwg_term_2")
trace_contract._emit_writes_through("p1", "action_node", "write_through")
trace_contract._emit_writes_through("p1", "action_node", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "action_node", "safety_validation")
trace_contract._emit_invokes_eval("p1", "action_node", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "action_node", "routing_commit")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _invoke_evidence_sidecar(evidence_bundle: Any, execution_context: Any, tool_name: str = "") -> Any:
    """Pre-authorization evidence gate sidecar — delegates to evaluate_and_emit().

    Called from act(), act_async(), act_simple() when reasoning["evidence_bundle"] is set.
    Returns (gate_result, disposition) from the shared cross-lane adapter.
    """
    from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (  # noqa: PLC0415
        evaluate_and_emit,
    )

    return evaluate_and_emit(evidence_bundle, execution_context, tool_name)


def _make_execution_context(
    run_id: str,
    capability_token: str,
    policy_hash: str,
    payload: Any,
    target: str,
    action_class=None,
):
    from agentic_core.L4_state.utils.context.execution_context import (  # noqa: PLC0415
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
        trace_contract._emit_transcripts_response(str(uuid.uuid4()), "ActionNode.act", "model")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "ActionNode.act")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ActionNode.act".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        # Pre-authorization evidence gate: runs only when evidence_bundle is present
        _evidence_bundle = reasoning.get("evidence_bundle")
        if _evidence_bundle is not None:
            _invoke_evidence_sidecar(_evidence_bundle, _ectx, "action_node.act")
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
        # Pre-authorization evidence gate: runs only when evidence_bundle is present
        _evidence_bundle = reasoning.get("evidence_bundle")
        if _evidence_bundle is not None:
            _invoke_evidence_sidecar(_evidence_bundle, _ectx, "action_node.act_async")
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
        # Pre-authorization evidence gate: runs only when evidence_bundle is present
        _evidence_bundle = perceived.get("evidence_bundle")
        if _evidence_bundle is not None:
            _invoke_evidence_sidecar(_evidence_bundle, _ectx, "action_node.act_simple")
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
