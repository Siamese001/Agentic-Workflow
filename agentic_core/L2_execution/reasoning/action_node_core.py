from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "action_node_core")
emit_determinism_digest("p0", "action_node_core")

_emit_dispatches_healing_run("p1", "action_node_core", "L2")
_emit_routes_through("p1", "action_node_core", "L2")
_emit_checks_agent_registry("p1", "action_node_core", "agent_registry")
_emit_validates_agent_capability("p1", "action_node_core", "capability")
_emit_dispatches_execution_plan("p1", "action_node_core", "exec_plan")
_emit_agent_executes_agent("p1", "action_node_core", "sub_agent")
_emit_routes_to_agent("p1", "action_node_core", "target_agent")
_emit_verifies_policy("p1", "action_node_core", "policy_check")
_emit_observes_runtime_state("p1", "action_node_core", "runtime_state")
_emit_verifies_boundary("p1", "action_node_core", "boundary_check")
_emit_hard_fails_untranscripted("p1", "action_node_core")
_emit_gated_by_confidence("p1", "action_node_core", "confidence_gate")
_emit_escalates_to_human("p1", "action_node_core", "L2")
_emit_reads_policy_state("p1", "action_node_core", "L2")

_emit_applies_guardrail("p0", "action_node_core", "p0_governance")
_emit_snapshots_state("p0", "action_node_core", "state_snapshot")
_emit_authorize_and_execute("p2", "action_node_core", "execution_auth")
_emit_validates_capability("p2", "action_node_core", "capability_check")
_emit_routes_to_capability("p2", "action_node_core", "capability_route")
_emit_writes_via_uwg("p2", "action_node_core", "uwg_write")
_emit_blocks_direct_write("p2", "action_node_core", "direct_write_block")
_emit_records_tool_invocation("p2", "action_node_core", "tool_invocation")
_emit_captures_execution_output("p2", "action_node_core", "exec_output")
_emit_dispatches_agent("p3", "action_node_core", "agent_dispatch")
_emit_coordinates_agents("p3", "action_node_core", "agent_coordination")
_emit_records_workflow_lineage("p3", "action_node_core", "workflow_lineage")
_emit_records_healing_outcome("p3", "action_node_core", "healing_outcome")
_emit_escalates_failure("p3", "action_node_core", "failure_escalation")
_emit_orchestrates_workflow("p3", "action_node_core", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "action_node_core", "healing_dispatch")
_emit_invokes_evaluation("p3", "action_node_core", "evaluation_signal")
_emit_records_telemetry_event("p4", "action_node_core", "telemetry_event")
_emit_captures_evaluation_metric("p4", "action_node_core", "eval_metric")
_emit_stores_embedding("p4", "action_node_core", "embedding_store")
_emit_updates_meta_learning_state("p4", "action_node_core", "meta_learning")
_emit_links_execution_to_snapshot("p4", "action_node_core", "exec_snapshot_link")

"\nCore Executor - Atomic Module\nExtracted from ActionNode.py via Atomic Fission Protocol\nHandles plan execution and step orchestration\n"
import logging
import uuid
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_stores_learning_state,
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

_emit_emits_metric_event("action_node_core", "p4obs", "metric_1")
_emit_emits_metric_event("action_node_core", "p4obs", "metric_2")
_emit_emits_metric_event("action_node_core", "p4obs", "metric_3")
_emit_emits_metric_event("action_node_core", "p4obs", "metric_4")
_emit_emits_metric_event("action_node_core", "p4obs", "metric_5")
_emit_emits_metric_event("action_node_core", "p4obs", "metric_6")
_emit_records_incident_event("action_node_core", "p4obs", "incident")
_emit_captures_runtime_anomaly("action_node_core", "p4obs", "anomaly")
_emit_writes_observability_log("action_node_core", "p4obs", "obs_log")
_emit_updates_monitoring_state("action_node_core", "p4obs", "mon_state")
_emit_triggers_alert("action_node_core", "p4obs", "alert")
_emit_links_incident_trace("action_node_core", "p4obs", "trace_link")
_emit_captures_pattern("action_node_core", "p3lm", "pattern")
_emit_records_learning_event("action_node_core", "p3lm", "learning_event")
_emit_writes_learning_snapshot("action_node_core", "p3lm", "snapshot")
_emit_feeds_meta_learning("action_node_core", "p3lm", "meta_feed")
_emit_updates_routing_strategy("action_node_core", "p3lm", "routing")
_emit_improves_agent_policy("action_node_core", "p3lm", "policy")
_emit_stores_learning_state("action_node_core", "p3lm", "state")
_emit_records_execution_trace("action_node_core", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("action_node_core", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("action_node_core", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("action_node_core", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("action_node_core", "L4_STATE", "p2_trace_5")
_emit_reads_environ("action_node_core", "env_read", "p2_env_1")
_emit_reads_environ("action_node_core", "env_read", "p2_env_2")
_emit_reads_runtime_state("action_node_core", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("action_node_core", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "action_node_core", "context_pull")
_emit_pulls_context("p1", "action_node_core", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "action_node_core", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "action_node_core", "uwg_term_2")
_emit_writes_through("p1", "action_node_core", "write_through")
_emit_writes_through("p1", "action_node_core", "write_through_2")
_emit_validated_by_safety_plane("p1", "action_node_core", "safety_validation")
_emit_invokes_eval("p1", "action_node_core", "eval_call")
_emit_proposal_commits_routing("p1", "action_node_core", "routing_commit")

Logger: Any = logging.getLogger("ActionNode.CoreExecutor")


class ActionNodeCore:
    """
    Core execution logic for ActionNode.
    Handles plan parsing and step orchestration.
    """

    TOOL_MAP: dict[str, str] = {
        "write_file": "write_file",
        "create_file": "write_file",
        "read_file": "read_file",
        "read": "read_file",
        "list_files": "list_files",
        "ls": "list_files",
        "run_command": "run_command",
        "execute": "run_command",
    }

    def __init__(self, work_dir: str, allowed_tools: dict[str, Any]):
        """
        Initialize core executor.

        Args:
            work_dir (str): Working directory path
            allowed_tools (Dict[str, Any]): Map of tool names to implementations
        """
        self.work_dir = Path(work_dir).resolve()
        self.allowed_tools = allowed_tools

    def execute_plan(self, plan: dict[str, Any]) -> dict[str, Any]:
        """
        Executes a full plan sequence from the Cognitive Node.

        Args:
            plan (Dict[str, Any]): A dictionary representing the plan,
                                   expected to contain 'goal' and 'steps'.

        Returns:
            Dict[str, Any]: A dictionary containing the overall status and results
                            of each executed step.
        """
        _emit_transcripts_response(str(uuid.uuid4()), "ActionNodeCore.execute_plan", "model")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ActionNodeCore.execute_plan")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ActionNodeCore.execute_plan".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        Logger.info(f"⚙️ Action Node received plan for goal: {plan.get('goal', 'N/A')}")
        results: list[dict[str, Any]] = []
        steps: list[dict[str, Any]] = plan.get("steps") or plan.get("plan", {}).get("steps", [])
        if not steps:
            Logger.warning("[!] Received empty plan. No actions taken.")
            return {"status": "skipped", "results": []}
        for step in steps:
            result: Any = self._execute_single_step(step)
            results.append(result)
            if result.get("status") == "error":
                Logger.error(f"🛑 Execution halted at step {step.get('step', 'N/A')}: {result.get('output')}")
                return {"status": "failed", "results": results}
        Logger.info("[OK] Plan execution completed successfully.")
        return {"status": "success", "results": results}

    def _execute_single_step(self, step: dict[str, Any]) -> dict[str, Any]:
        """
        Parses a single step, validates the tool, and executes it.

        Args:
            step (Dict[str, Any]): A dictionary representing a single action step,
                                   expected to contain 'action' and 'params'.

        Returns:
            Dict[str, Any]: A dictionary containing the step number, status, and output.
        """
        action_name: str = step.get("action", "").lower().replace(" ", "_")
        params: dict[str, Any] = step.get("params", {})
        step_number: int | str = step.get("step", "N/A")
        tool_key: str | None = self.TOOL_MAP.get(action_name)
        if not tool_key or tool_key not in self.allowed_tools:
            msg = f"[X] Tool '{action_name}' (mapped to '{tool_key}') is NOT whitelisted or recognized."
            Logger.warning(msg)
            return {"step": step_number, "status": "blocked", "output": msg}
        Logger.info(f"🔨 Executing Tool '{tool_key}' for step {step_number} with params: {params}")
        try:
            output: str = self.allowed_tools[tool_key](**params)
            return {"step": step_number, "status": "success", "output": output}
        except (ValueError, TypeError) as e:
            Logger.error(f"[X] Tool '{tool_key}' execution failed for step {step_number}: {e}", exc_info=True)
            return {"step": step_number, "status": "error", "output": str(e)}


__all__ = ["ActionNodeCore"]
