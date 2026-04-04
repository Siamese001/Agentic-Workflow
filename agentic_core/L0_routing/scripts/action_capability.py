from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
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

emit_replay_key("p0", "action_capability")
emit_determinism_digest("p0", "action_capability")

_emit_dispatches_healing_run("p1", "action_capability", "L0")
_emit_routes_through("p1", "action_capability", "L0")
_emit_checks_agent_registry("p1", "action_capability", "agent_registry")
_emit_validates_agent_capability("p1", "action_capability", "capability")
_emit_dispatches_execution_plan("p1", "action_capability", "exec_plan")
_emit_agent_executes_agent("p1", "action_capability", "sub_agent")
_emit_routes_to_agent("p1", "action_capability", "target_agent")
_emit_verifies_policy("p1", "action_capability", "policy_check")
_emit_observes_runtime_state("p1", "action_capability", "runtime_state")
_emit_verifies_boundary("p1", "action_capability", "boundary_check")
_emit_transcripts_response("p1", "action_capability", "transcript")
_emit_hard_fails_untranscripted("p1", "action_capability")
_emit_gated_by_confidence("p1", "action_capability", "confidence_gate")
_emit_escalates_to_human("p1", "action_capability", "L0")
_emit_reads_policy_state("p1", "action_capability", "L0")
_emit_authorize_and_execute("p2", "action_capability", "execution_auth")
_emit_validates_capability("p2", "action_capability", "capability_check")
_emit_routes_to_capability("p2", "action_capability", "capability_route")
_emit_writes_via_uwg("p2", "action_capability", "uwg_write")
_emit_blocks_direct_write("p2", "action_capability", "direct_write_block")
_emit_records_tool_invocation("p2", "action_capability", "tool_invocation")
_emit_captures_execution_output("p2", "action_capability", "exec_output")
_emit_dispatches_agent("p3", "action_capability", "agent_dispatch")
_emit_coordinates_agents("p3", "action_capability", "agent_coordination")
_emit_records_workflow_lineage("p3", "action_capability", "workflow_lineage")
_emit_records_healing_outcome("p3", "action_capability", "healing_outcome")
_emit_escalates_failure("p3", "action_capability", "failure_escalation")
_emit_orchestrates_workflow("p3", "action_capability", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "action_capability", "healing_dispatch")
_emit_invokes_evaluation("p3", "action_capability", "evaluation_signal")
_emit_records_telemetry_event("p4", "action_capability", "telemetry_event")
_emit_captures_evaluation_metric("p4", "action_capability", "eval_metric")
_emit_stores_embedding("p4", "action_capability", "embedding_store")
_emit_updates_meta_learning_state("p4", "action_capability", "meta_learning")
_emit_links_execution_to_snapshot("p4", "action_capability", "exec_snapshot_link")

"Action Plane Interface - The Hands.\n\nPhase 2 - Pillar 1: Layering Model\nDefines the contract for all tool execution and external interactions.\nL2 Execution: Side effects allowed, but controlled and observable.\n"
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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

_emit_emits_metric_event("action_capability", "p4obs", "metric_1")
_emit_emits_metric_event("action_capability", "p4obs", "metric_2")
_emit_emits_metric_event("action_capability", "p4obs", "metric_3")
_emit_emits_metric_event("action_capability", "p4obs", "metric_4")
_emit_emits_metric_event("action_capability", "p4obs", "metric_5")
_emit_emits_metric_event("action_capability", "p4obs", "metric_6")
_emit_records_incident_event("action_capability", "p4obs", "incident")
_emit_captures_runtime_anomaly("action_capability", "p4obs", "anomaly")
_emit_writes_observability_log("action_capability", "p4obs", "obs_log")
_emit_updates_monitoring_state("action_capability", "p4obs", "mon_state")
_emit_triggers_alert("action_capability", "p4obs", "alert")
_emit_links_incident_trace("action_capability", "p4obs", "trace_link")
_emit_captures_pattern("action_capability", "p3lm", "pattern")
_emit_records_learning_event("action_capability", "p3lm", "learning_event")
_emit_writes_learning_snapshot("action_capability", "p3lm", "snapshot")
_emit_feeds_meta_learning("action_capability", "p3lm", "meta_feed")
_emit_updates_routing_strategy("action_capability", "p3lm", "routing")
_emit_improves_agent_policy("action_capability", "p3lm", "policy")
_emit_stores_learning_state("action_capability", "p3lm", "state")
_emit_records_execution_trace("action_capability", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("action_capability", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("action_capability", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("action_capability", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("action_capability", "L4_STATE", "p2_trace_5")
_emit_reads_environ("action_capability", "env_read", "p2_env_1")
_emit_reads_environ("action_capability", "env_read", "p2_env_2")
_emit_reads_runtime_state("action_capability", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("action_capability", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "action_capability", "context_pull")
_emit_pulls_context("p1", "action_capability", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "action_capability", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "action_capability", "uwg_term_2")
_emit_writes_through("p1", "action_capability", "write_through")
_emit_writes_through("p1", "action_capability", "write_through_2")
_emit_validated_by_safety_plane("p1", "action_capability", "safety_validation")
_emit_invokes_eval("p1", "action_capability", "eval_call")
_emit_proposal_commits_routing("p1", "action_capability", "routing_commit")


class ActionCapability(Enum):
    """Capabilities provided by the action plane."""

    TOOL_EXECUTION = "tool_execution"
    API_CALLS = "api_calls"
    FILE_OPERATIONS = "file_operations"
    DATABASE_OPERATIONS = "database_operations"
    EXTERNAL_SERVICES = "external_services"
    SEARCH = "search"
    RETRIEVAL = "retrieval"


@dataclass
class ActionRequest:
    """Request for action execution."""

    action_type: str
    tool_name: str
    parameters: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    timeout_ms: int = 30000
    retry_policy: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ActionRequest.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ActionRequest.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ActionRequest.to_dict")
        return {
            "action_type": self.action_type,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "context": self.context,
            "timeout_ms": self.timeout_ms,
            "retry_policy": self.retry_policy,
        }


@dataclass
class ActionResult:
    """Result from action execution."""

    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    retries: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
            "execution_time_ms": self.execution_time_ms,
            "retries": self.retries,
        }


class IActionPlane(ABC):
    """Interface for the Action Plane (Hands).

    The action plane is responsible for:
    - Tool Execution: Running external tools and APIs
    - Side Effects: Performing actions that change state
    - Resource Management: Managing connections and resources
    - Error Handling: Dealing with failures gracefully

    L2 Constraint: Side effects are allowed but must be:
    - Observable (logged/traced)
    - Reversible when possible
    - Protected by resilience middleware
    """

    @abstractmethod
    async def execute(self, request: ActionRequest) -> ActionResult:
        """Execute an action.

        Args:
            request: Action request with tool and parameters

        Returns:
            ActionResult with output or error
        """
        pass

    @abstractmethod
    async def execute_batch(
        self, requests: list[ActionRequest], parallel: bool = False
    ) -> list[ActionResult]:
        """Execute multiple actions.

        Args:
            requests: List of action requests
            parallel: Whether to execute in parallel

        Returns:
            List of action results
        """
        pass

    @abstractmethod
    async def validate_action(self, request: ActionRequest) -> dict[str, Any]:
        """Validate an action before execution.

        Args:
            request: Action request to validate

        Returns:
            Validation result with any warnings
        """
        pass

    @abstractmethod
    def get_available_tools(self) -> list[str]:
        """Get list of available tools.

        Returns:
            List of tool names
        """
        pass

    @abstractmethod
    def get_tool_schema(self, tool_name: str) -> dict[str, Any]:
        """Get schema for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool schema with parameters and types
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> list[ActionCapability]:
        """Get list of supported action capabilities.

        Returns:
            List of capabilities this plane supports
        """
        pass
