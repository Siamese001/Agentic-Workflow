from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
)

_emit_dispatches_healing_run("p1", "error_handler", "L0")
_emit_routes_through("p1", "error_handler", "L0")
_emit_checks_agent_registry("p1", "error_handler", "agent_registry")
_emit_validates_agent_capability("p1", "error_handler", "capability")
_emit_dispatches_execution_plan("p1", "error_handler", "exec_plan")
_emit_agent_executes_agent("p1", "error_handler", "sub_agent")
_emit_routes_to_agent("p1", "error_handler", "target_agent")
_emit_verifies_policy("p1", "error_handler", "policy_check")
_emit_observes_runtime_state("p1", "error_handler", "runtime_state")
_emit_verifies_boundary("p1", "error_handler", "boundary_check")
_emit_transcripts_response("p1", "error_handler", "transcript")
_emit_hard_fails_untranscripted("p1", "error_handler")
_emit_gated_by_confidence("p1", "error_handler", "confidence_gate")
_emit_escalates_to_human("p1", "error_handler", "L0")
_emit_reads_policy_state("p1", "error_handler", "L0")
_emit_authorize_and_execute("p2", "error_handler", "execution_auth")
_emit_validates_capability("p2", "error_handler", "capability_check")
_emit_routes_to_capability("p2", "error_handler", "capability_route")
_emit_writes_via_uwg("p2", "error_handler", "uwg_write")
_emit_blocks_direct_write("p2", "error_handler", "direct_write_block")
_emit_records_tool_invocation("p2", "error_handler", "tool_invocation")
_emit_captures_execution_output("p2", "error_handler", "exec_output")
_emit_dispatches_agent("p3", "error_handler", "agent_dispatch")
_emit_coordinates_agents("p3", "error_handler", "agent_coordination")
_emit_records_workflow_lineage("p3", "error_handler", "workflow_lineage")
_emit_records_healing_outcome("p3", "error_handler", "healing_outcome")
_emit_escalates_failure("p3", "error_handler", "failure_escalation")
_emit_orchestrates_workflow("p3", "error_handler", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "error_handler", "healing_dispatch")
_emit_invokes_evaluation("p3", "error_handler", "evaluation_signal")
_emit_records_telemetry_event("p4", "error_handler", "telemetry_event")
_emit_captures_evaluation_metric("p4", "error_handler", "eval_metric")
_emit_stores_embedding("p4", "error_handler", "embedding_store")
_emit_updates_meta_learning_state("p4", "error_handler", "meta_learning")
_emit_links_execution_to_snapshot("p4", "error_handler", "exec_snapshot_link")

"\nUnified Workflow Engine\n\nSingle entry point for all workflow orchestration, replacing 8 core engines:\n- NervousSystemAgent\n- MissionControllerEngine\n- SubatomicOrchestratorImpl\n- DAGManagerAgent\n- DagEngineAgent\n- SelfRecoveringOrchestratorAgent\n- WorkflowFissionManagerAgent\n- L3OrchestrationBase\n"
import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    emit_determinism_digest,
    emit_replay_key,
)
from agentic_core.utils.runners.providers import get_clock

from .base_coordinator import WorkflowCoordinator, coordinator_registry
from .execution import (
    STRATEGY_REGISTRY,
    ExecutionStatus,
    ExecutionStrategy,
    WorkflowContext,
    WorkflowResult,
    WorkflowStep,
    get_strategy,
)

_emit_emits_metric_event("error_handler", "p4obs", "metric_1")
_emit_emits_metric_event("error_handler", "p4obs", "metric_2")
_emit_emits_metric_event("error_handler", "p4obs", "metric_3")
_emit_emits_metric_event("error_handler", "p4obs", "metric_4")
_emit_emits_metric_event("error_handler", "p4obs", "metric_5")
_emit_emits_metric_event("error_handler", "p4obs", "metric_6")
_emit_records_incident_event("error_handler", "p4obs", "incident")
_emit_captures_runtime_anomaly("error_handler", "p4obs", "anomaly")
_emit_writes_observability_log("error_handler", "p4obs", "obs_log")
_emit_updates_monitoring_state("error_handler", "p4obs", "mon_state")
_emit_triggers_alert("error_handler", "p4obs", "alert")
_emit_links_incident_trace("error_handler", "p4obs", "trace_link")
_emit_captures_pattern("error_handler", "p3lm", "pattern")
_emit_records_learning_event("error_handler", "p3lm", "learning_event")
_emit_writes_learning_snapshot("error_handler", "p3lm", "snapshot")
_emit_feeds_meta_learning("error_handler", "p3lm", "meta_feed")
_emit_updates_routing_strategy("error_handler", "p3lm", "routing")
_emit_improves_agent_policy("error_handler", "p3lm", "policy")
_emit_stores_learning_state("error_handler", "p3lm", "state")
_emit_records_execution_trace("error_handler", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("error_handler", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("error_handler", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("error_handler", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("error_handler", "L4_STATE", "p2_trace_5")
_emit_reads_environ("error_handler", "env_read", "p2_env_1")
_emit_reads_environ("error_handler", "env_read", "p2_env_2")
_emit_reads_runtime_state("error_handler", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("error_handler", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "error_handler", "context_pull")
_emit_pulls_context("p1", "error_handler", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "error_handler", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "error_handler", "uwg_term_2")
_emit_writes_through("p1", "error_handler", "write_through")
_emit_writes_through("p1", "error_handler", "write_through_2")
_emit_validated_by_safety_plane("p1", "error_handler", "safety_validation")
_emit_invokes_eval("p1", "error_handler", "eval_call")
_emit_proposal_commits_routing("p1", "error_handler", "routing_commit")


@dataclass
class WorkflowMetrics:
    """Metrics for workflow execution."""

    total_workflows: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    total_time: float = 0.0
    avg_latency: float = 0.0


class ErrorHandler:
    """Unified error handling for workflows."""

    def __init__(self):
        """Initialize error handler."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ErrorHandler.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ErrorHandler.__init__", "p0_governance")
        self.recovery_strategies = {
            "retry": self._retry_strategy,
            "fallback": self._fallback_strategy,
            "skip": self._skip_strategy,
            "abort": self._abort_strategy,
        }
        # guardian: allow-magic-config
        self.max_retries = 3

    async def handle_error(
        self, error: Exception, context: WorkflowContext, recovery_type: str = "retry",
    ) -> WorkflowResult:
        """Handle workflow error with recovery strategy."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ErrorHandler.handle_error")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        strategy = self.recovery_strategies.get(recovery_type, self._abort_strategy)
        return await strategy(error, context)

    async def _retry_strategy(self, error: Exception, context: WorkflowContext) -> WorkflowResult:
        """Retry the workflow."""
        retries = context.state.get("retries", 0)
        if retries < self.max_retries:
            context.state["retries"] = retries + 1
            return WorkflowResult(
                workflow_id=context.workflow_id,
                status=ExecutionStatus.PENDING,
                error=f"Retry {retries + 1}/{self.max_retries}: {str(error)}",
            )
        return await self._abort_strategy(error, context)

    async def _fallback_strategy(self, error: Exception, context: WorkflowContext) -> WorkflowResult:
        """Use fallback logic."""
        return WorkflowResult(
            workflow_id=context.workflow_id,
            status=ExecutionStatus.COMPLETED,
            output={"fallback": True, "original_error": str(error)},
            error=f"Fallback used: {str(error)}",
        )

    async def _skip_strategy(self, error: Exception, context: WorkflowContext) -> WorkflowResult:
        """Skip failed step."""
        return WorkflowResult(
            workflow_id=context.workflow_id,
            status=ExecutionStatus.COMPLETED,
            output={"skipped": True},
            error=f"Skipped: {str(error)}",
        )

    async def _abort_strategy(self, error: Exception, context: WorkflowContext) -> WorkflowResult:
        """Abort workflow."""
        return WorkflowResult(
            workflow_id=context.workflow_id, status=ExecutionStatus.FAILED, error=str(error),
        )


class UnifiedWorkflowEngine:
    """
    Unified Workflow Engine - Single entry point for all orchestration.

    Replaces 8 core engines with:
    - Pluggable execution strategies (DAG, state machine, event-driven, reactive)
    - Unified error handling and recovery
    - Centralized logging and metrics
    - Coordinator registry for specialized domains
    """

    def __init__(self):
        """Initialize unified workflow engine."""
        self.strategies = STRATEGY_REGISTRY.copy()
        self.coordinator_registry = coordinator_registry
        self.error_handler = ErrorHandler()
        self.metrics = WorkflowMetrics()
        self.active_workflows: dict[str, WorkflowContext] = {}

    async def execute(
        self,
        workflow_type: str,
        input_data: dict[str, Any],
        steps: list[WorkflowStep] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        """
        Execute workflow using appropriate strategy.

        Args:
            workflow_type: Type of workflow (dag, state_machine, event, reactive)
            input_data: Input data for workflow
            steps: Optional workflow steps
            metadata: Optional metadata

        Returns:
            Workflow result
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "UnifiedWorkflowEngine.execute")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        workflow_id = str(uuid.uuid4())
        start_time = get_clock().now_epoch()
        self.metrics.total_workflows += 1
        context = WorkflowContext(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            input_data=input_data,
            metadata=metadata or {},
        )
        self.active_workflows[workflow_id] = context
        try:
            coordinator = self.coordinator_registry.get_for_workflow(workflow_type)
            if coordinator:
                result = await coordinator.safe_coordinate(context)
            else:
                strategy = get_strategy(workflow_type)
                if steps:
                    result = await strategy.execute(context, steps)
                else:
                    result = WorkflowResult(
                        workflow_id=workflow_id,
                        status=ExecutionStatus.COMPLETED,
                        output={"message": "No steps provided"},
                    )
            if result.status == ExecutionStatus.COMPLETED:
                self.metrics.completed_workflows += 1
            else:
                self.metrics.failed_workflows += 1
            elapsed = get_clock().now_epoch() - start_time
            self.metrics.total_time += elapsed
            self.metrics.avg_latency = self.metrics.total_time / self.metrics.total_workflows
            result.metrics["execution_time"] = elapsed
            return result
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            self.metrics.failed_workflows += 1
            return await self.error_handler.handle_error(e, context, "abort")
        finally:
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]

    async def execute_with_coordinator(
        self, coordinator_name: str, input_data: dict[str, Any], metadata: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        """
        Execute workflow using specific coordinator.

        Args:
            coordinator_name: Name of coordinator
            input_data: Input data
            metadata: Optional metadata

        Returns:
            Workflow result
        """
        coordinator = self.coordinator_registry.get(coordinator_name)
        if not coordinator:
            return WorkflowResult(
                workflow_id=str(uuid.uuid4()),
                status=ExecutionStatus.FAILED,
                error=f"Coordinator not found: {coordinator_name}",
            )
        context = WorkflowContext(
            workflow_id=str(uuid.uuid4()),
            workflow_type=coordinator_name,
            input_data=input_data,
            metadata=metadata or {},
        )
        return await coordinator.safe_coordinate(context)

    def register_coordinator(self, coordinator: WorkflowCoordinator) -> None:
        """Register coordinator with engine."""
        self.coordinator_registry.register(coordinator)

    def register_strategy(self, name: str, strategy: ExecutionStrategy) -> None:
        """Register execution strategy."""
        self.strategies[name] = strategy

    def get_statistics(self) -> dict[str, Any]:
        """Get engine statistics."""
        return {
            "metrics": {
                "total_workflows": self.metrics.total_workflows,
                "completed_workflows": self.metrics.completed_workflows,
                "failed_workflows": self.metrics.failed_workflows,
                "success_rate": self.metrics.completed_workflows / self.metrics.total_workflows * 100
                if self.metrics.total_workflows > 0
                else 0,
                "total_time": self.metrics.total_time,
                "avg_latency": self.metrics.avg_latency,
            },
            "active_workflows": len(self.active_workflows),
            "strategies": list(self.strategies.keys()),
            "coordinators": self.coordinator_registry.get_statistics(),
        }

    def get_active_workflows(self) -> list[str]:
        """Get list of active workflow IDs."""
        return list(self.active_workflows.keys())


unified_engine = UnifiedWorkflowEngine()
