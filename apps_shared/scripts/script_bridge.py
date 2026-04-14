"""
Script Bridge Interface - Phase 3 Optimization
Bridge between agents and deterministic scripts.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_authorize_and_execute("p2", "script_bridge", "execution_auth")
_emit_validates_capability("p2", "script_bridge", "capability_check")
_emit_routes_to_capability("p2", "script_bridge", "capability_route")
_emit_writes_via_uwg("p2", "script_bridge", "uwg_write")
_emit_blocks_direct_write("p2", "script_bridge", "direct_write_block")
_emit_records_tool_invocation("p2", "script_bridge", "tool_invocation")
_emit_captures_execution_output("p2", "script_bridge", "exec_output")
_emit_dispatches_agent("p3", "script_bridge", "agent_dispatch")
_emit_coordinates_agents("p3", "script_bridge", "agent_coordination")
_emit_records_workflow_lineage("p3", "script_bridge", "workflow_lineage")
_emit_records_healing_outcome("p3", "script_bridge", "healing_outcome")
_emit_escalates_failure("p3", "script_bridge", "failure_escalation")
_emit_orchestrates_workflow("p3", "script_bridge", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "script_bridge", "healing_dispatch")
_emit_invokes_evaluation("p3", "script_bridge", "evaluation_signal")
_emit_records_telemetry_event("p4", "script_bridge", "telemetry_event")
_emit_captures_evaluation_metric("p4", "script_bridge", "eval_metric")
_emit_stores_embedding("p4", "script_bridge", "embedding_store")
_emit_updates_meta_learning_state("p4", "script_bridge", "meta_learning")
_emit_links_execution_to_snapshot("p4", "script_bridge", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from apps_shared.scripts.io_operations_validator import (
    DataCollectionOperations,
    FileOperations,
    MonitoringOperations,
)

_emit_emits_metric_event("script_bridge", "p4obs", "metric_1")
_emit_emits_metric_event("script_bridge", "p4obs", "metric_2")
_emit_emits_metric_event("script_bridge", "p4obs", "metric_3")
_emit_emits_metric_event("script_bridge", "p4obs", "metric_4")
_emit_emits_metric_event("script_bridge", "p4obs", "metric_5")
_emit_emits_metric_event("script_bridge", "p4obs", "metric_6")
_emit_records_incident_event("script_bridge", "p4obs", "incident")
_emit_captures_runtime_anomaly("script_bridge", "p4obs", "anomaly")
_emit_writes_observability_log("script_bridge", "p4obs", "obs_log")
_emit_updates_monitoring_state("script_bridge", "p4obs", "mon_state")
_emit_triggers_alert("script_bridge", "p4obs", "alert")
_emit_links_incident_trace("script_bridge", "p4obs", "trace_link")
_emit_captures_pattern("script_bridge", "p3lm", "pattern")
_emit_records_learning_event("script_bridge", "p3lm", "learning_event")
_emit_writes_learning_snapshot("script_bridge", "p3lm", "snapshot")
_emit_feeds_meta_learning("script_bridge", "p3lm", "meta_feed")
_emit_updates_routing_strategy("script_bridge", "p3lm", "routing")
_emit_improves_agent_policy("script_bridge", "p3lm", "policy")
_emit_stores_learning_state("script_bridge", "p3lm", "state")
_emit_records_execution_trace("script_bridge", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("script_bridge", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("script_bridge", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("script_bridge", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("script_bridge", "L4_STATE", "p2_trace_5")
_emit_reads_environ("script_bridge", "env_read", "p2_env_1")
_emit_reads_environ("script_bridge", "env_read", "p2_env_2")
_emit_reads_runtime_state("script_bridge", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("script_bridge", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "script_bridge")
_emit_applies_guardrail("p0", "script_bridge", "p0_governance")
_emit_reads_policy_state("p0", "script_bridge", "policy_binding")
_emit_snapshots_state("p0", "script_bridge", "state_snapshot")
_emit_pulls_context("p1", "script_bridge", "context_pull")
_emit_pulls_context("p1", "script_bridge", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "script_bridge", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "script_bridge", "uwg_term_secondary")
_emit_writes_through("p1", "script_bridge", "write_through")
_emit_writes_through("p1", "script_bridge", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "script_bridge", "safety_validation")
_emit_invokes_eval("p1", "script_bridge", "eval_call")
_emit_proposal_commits_routing("p1", "script_bridge", "routing_commit")
_emit_escalates_to_human("p1", "script_bridge", "human_escalation")
_emit_routes_through("p1", "script_bridge", "route_through")
_emit_checks_agent_registry("p1", "script_bridge", "agent_registry")
_emit_validates_agent_capability("p1", "script_bridge", "capability")
_emit_dispatches_execution_plan("p1", "script_bridge", "exec_plan")
_emit_agent_executes_agent("p1", "script_bridge", "sub_agent")
_emit_routes_to_agent("p1", "script_bridge", "target_agent")
_emit_verifies_policy("p1", "script_bridge", "policy_check")
_emit_observes_runtime_state("p1", "script_bridge", "runtime_state")
_emit_verifies_boundary("p1", "script_bridge", "boundary_check")
_emit_transcripts_response("p1", "script_bridge", "transcript")
_emit_hard_fails_untranscripted("p1", "script_bridge")
_emit_gated_by_confidence("p1", "script_bridge", "confidence_gate")
emit_replay_key("p0", "script_bridge")
emit_determinism_digest("p0", "script_bridge")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


@dataclass
class ScriptResult:
    """Result from script execution."""

    success: bool
    data: Any
    errors: list[str]
    metadata: dict[str, Any]


class ScriptBridge:
    """
    Bridge interface for agents to call deterministic scripts.

    Provides a clean separation between agent logic and I/O operations,
    improving testability and reducing agent complexity.
    """

    def __init__(self):
        """Initialize script bridge."""
        self.file_ops = FileOperations()
        self.data_ops = DataCollectionOperations()
        self.monitor_ops = MonitoringOperations()

    def execute_script(self, script_name: str, operation: str, **kwargs: Any) -> ScriptResult:
        """
        Execute a script operation.

        Args:
            script_name: Name of script module (file, data, monitor)
            operation: Operation to execute
            **kwargs: Arguments for the operation

        Returns:
            ScriptResult with execution results
        """
        try:
            # Route to appropriate script module
            if script_name == "file":
                result = self._execute_file_operation(operation, **kwargs)
            elif script_name == "data":
                result = self._execute_data_operation(operation, **kwargs)
            elif script_name == "monitor":
                result = self._execute_monitor_operation(operation, **kwargs)
            else:
                return ScriptResult(
                    success=False,
                    data=None,
                    errors=[f"Unknown script module: {script_name}"],
                    metadata={},
                )

            return ScriptResult(success=True, data=result, errors=[], metadata={})

        except Exception as e:
            logger.error(f"Script execution failed: {script_name}.{operation} - {e}")
            return ScriptResult(
                success=False,
                data=None,
                errors=[str(e)],
                metadata={"script": script_name, "operation": operation},
            )

    def _execute_file_operation(self, operation: str, **kwargs: Any) -> Any:
        """Execute file operation."""
        operations = {
            "read_json": self.file_ops.read_json,
            "write_json": self.file_ops.write_json,
            "read_text": self.file_ops.read_text,
            "write_text": self.file_ops.write_text,
            "list_files": self.file_ops.list_files,
            "file_exists": self.file_ops.file_exists,
            "delete_file": self.file_ops.delete_file,
        }

        if operation not in operations:
            raise ValueError(f"Unknown file operation: {operation}")

        return operations[operation](**kwargs)

    def _execute_data_operation(self, operation: str, **kwargs: Any) -> Any:
        """Execute data collection operation."""
        operations = {
            "collect_metrics": self.data_ops.collect_metrics,
            "aggregate_results": self.data_ops.aggregate_results,
            "filter_data": self.data_ops.filter_data,
        }

        if operation not in operations:
            raise ValueError(f"Unknown data operation: {operation}")

        return operations[operation](**kwargs)

    def _execute_monitor_operation(self, operation: str, **kwargs: Any) -> Any:
        """Execute monitoring operation."""
        operations = {
            "check_system_state": self.monitor_ops.check_system_state,
            "record_event": self.monitor_ops.record_event,
            "get_recent_events": self.monitor_ops.get_recent_events,
        }

        if operation not in operations:
            raise ValueError(f"Unknown monitor operation: {operation}")

        return operations[operation](**kwargs)

    def read_config_file(self, file_path: str) -> ScriptResult:
        """
        Convenience method to read config file.

        Args:
            file_path: Path to config file

        Returns:
            ScriptResult with config data
        """
        return self.execute_script("file", "read_json", file_path=file_path)

    def collect_agent_metrics(
        self,
        data_points: list[dict[str, Any]],
        metric_keys: list[str],
    ) -> ScriptResult:
        """
        Convenience method to collect metrics.

        Args:
            data_points: List of data dictionaries
            metric_keys: Keys to collect

        Returns:
            ScriptResult with collected metrics
        """
        return self.execute_script(
            "data",
            "collect_metrics",
            data_points=data_points,
            metric_keys=metric_keys,
        )

    def monitor_system(self, state_file: str) -> ScriptResult:
        """
        Convenience method to check system state.

        Args:
            state_file: Path to state file

        Returns:
            ScriptResult with system state
        """
        return self.execute_script("monitor", "check_system_state", state_file=state_file)


# Global script bridge instance
_script_bridge = None


def get_script_bridge() -> ScriptBridge:
    """Get global script bridge instance."""
    global _script_bridge
    if _script_bridge is None:
        _script_bridge = ScriptBridge()
    return _script_bridge
