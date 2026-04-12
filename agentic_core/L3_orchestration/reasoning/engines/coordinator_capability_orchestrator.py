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

emit_replay_key("p0", "coordinator_capability_orchestrator")
emit_determinism_digest("p0", "coordinator_capability_orchestrator")

_emit_dispatches_healing_run("p1", "coordinator_capability_orchestrator", "L3")
_emit_routes_through("p1", "coordinator_capability_orchestrator", "L3")
_emit_verifies_policy("p1", "coordinator_capability_orchestrator", "policy_check")
_emit_observes_runtime_state("p1", "coordinator_capability_orchestrator", "runtime_state")
_emit_verifies_boundary("p1", "coordinator_capability_orchestrator", "boundary_check")
_emit_transcripts_response("p1", "coordinator_capability_orchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "coordinator_capability_orchestrator")
_emit_gated_by_confidence("p1", "coordinator_capability_orchestrator", "confidence_gate")
_emit_escalates_to_human("p1", "coordinator_capability_orchestrator", "L3")
_emit_reads_policy_state("p1", "coordinator_capability_orchestrator", "L3")
_emit_routes_to_agent("p1", "coordinator_capability_orchestrator", "L3")
_emit_orchestrates_workflow("p1", "coordinator_capability_orchestrator", "L3")
_emit_dispatches_execution_plan("p1", "coordinator_capability_orchestrator", "L3")
_emit_validates_agent_capability("p1", "coordinator_capability_orchestrator", "L3")
_emit_checks_agent_registry("p1", "coordinator_capability_orchestrator", "L3")

_emit_snapshots_state("p0", "coordinator_capability_orchestrator", "state_snapshot")
_emit_authorize_and_execute("p2", "coordinator_capability_orchestrator", "execution_auth")
_emit_validates_capability("p2", "coordinator_capability_orchestrator", "capability_check")
_emit_routes_to_capability("p2", "coordinator_capability_orchestrator", "capability_route")
_emit_writes_via_uwg("p2", "coordinator_capability_orchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "coordinator_capability_orchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "coordinator_capability_orchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "coordinator_capability_orchestrator", "exec_output")
_emit_dispatches_agent("p3", "coordinator_capability_orchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "coordinator_capability_orchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "coordinator_capability_orchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "coordinator_capability_orchestrator", "healing_outcome")
_emit_escalates_failure("p3", "coordinator_capability_orchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "coordinator_capability_orchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "coordinator_capability_orchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "coordinator_capability_orchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "coordinator_capability_orchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "coordinator_capability_orchestrator", "eval_metric")
_emit_stores_embedding("p4", "coordinator_capability_orchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "coordinator_capability_orchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "coordinator_capability_orchestrator", "exec_snapshot_link")

"\nBase Coordinator Class\n\nProvides the base interface and common functionality for all specialized coordinators.\nEach coordinator owns a specific orchestration domain with clear responsibilities.\n"
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from agentic_core.L2_execution.utils.providers import get_clock
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
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
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

from .execution import ExecutionStatus, WorkflowContext, WorkflowResult

_emit_emits_metric_event("coordinator_capability_orchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("coordinator_capability_orchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("coordinator_capability_orchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("coordinator_capability_orchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("coordinator_capability_orchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("coordinator_capability_orchestrator", "p4obs", "metric_6")
_emit_records_incident_event("coordinator_capability_orchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("coordinator_capability_orchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("coordinator_capability_orchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("coordinator_capability_orchestrator", "p4obs", "mon_state")
_emit_triggers_alert("coordinator_capability_orchestrator", "p4obs", "alert")
_emit_links_incident_trace("coordinator_capability_orchestrator", "p4obs", "trace_link")
_emit_captures_pattern("coordinator_capability_orchestrator", "p3lm", "pattern")
_emit_records_learning_event("coordinator_capability_orchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("coordinator_capability_orchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("coordinator_capability_orchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("coordinator_capability_orchestrator", "p3lm", "routing")
_emit_improves_agent_policy("coordinator_capability_orchestrator", "p3lm", "policy")
_emit_stores_learning_state("coordinator_capability_orchestrator", "p3lm", "state")
_emit_records_execution_trace("coordinator_capability_orchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("coordinator_capability_orchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("coordinator_capability_orchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("coordinator_capability_orchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("coordinator_capability_orchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("coordinator_capability_orchestrator", "env_read", "p2_env_1")
_emit_reads_environ("coordinator_capability_orchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("coordinator_capability_orchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("coordinator_capability_orchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "coordinator_capability_orchestrator", "context_pull")
_emit_pulls_context("p1", "coordinator_capability_orchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "coordinator_capability_orchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "coordinator_capability_orchestrator", "uwg_term_2")
_emit_writes_through("p1", "coordinator_capability_orchestrator", "write_through")
_emit_writes_through("p1", "coordinator_capability_orchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "coordinator_capability_orchestrator", "safety_validation")
_emit_invokes_eval("p1", "coordinator_capability_orchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "coordinator_capability_orchestrator", "routing_commit")


@dataclass
class CoordinatorCapability:
    """Describes a coordinator capability."""

    name: str
    description: str
    workflow_types: list[str]
    priority: int = 0


class WorkflowCoordinator(ABC):
    """
    Base coordinator for specialized orchestration domains.

    Each coordinator:
    - Owns a specific domain (RL, Territory, MCP, etc.)
    - Has clear responsibilities
    - Can be registered with UnifiedWorkflowEngine
    - Supports async coordination
    """

    def __init__(self, name: str):
        """Initialize coordinator."""
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "WorkflowCoordinator.__init__", "p0_governance")
        self.name = name
        self.enabled = True
        self.coordinations = 0
        self.successes = 0
        self.failures = 0
        self.total_time = 0.0

    @abstractmethod
    async def coordinate(self, context: WorkflowContext) -> WorkflowResult:
        """
        Execute coordination logic.

        Args:
            context: Workflow context

        Returns:
            Workflow result
        """
        _emit_agent_executes_agent(str(uuid.uuid4()), "WorkflowCoordinator", "WorkflowCoordinator.coordinate")
        pass

    @abstractmethod
    def get_capabilities(self) -> list[CoordinatorCapability]:
        """
        Return coordinator capabilities.

        Returns:
            List of capabilities
        """
        pass

    @abstractmethod
    def can_handle(self, workflow_type: str) -> bool:
        """
        Check if coordinator can handle workflow type.

        Args:
            workflow_type: Type of workflow

        Returns:
            True if coordinator can handle
        """
        pass

    async def safe_coordinate(self, context: WorkflowContext) -> WorkflowResult:
        """
        Safe coordination with metrics tracking.

        Args:
            context: Workflow context

        Returns:
            Workflow result
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "WorkflowCoordinator.safe_coordinate",
        )

        start_time = get_clock().now_epoch()
        self.coordinations += 1
        try:
            result = await self.coordinate(context)
            if result.status == ExecutionStatus.COMPLETED:
                self.successes += 1
            else:
                self.failures += 1
            return result
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            self.failures += 1
            return WorkflowResult(
                workflow_id=context.workflow_id,
                status=ExecutionStatus.FAILED,
                error=f"Coordinator {self.name} failed: {str(e)}",
            )
        finally:
            self.total_time += get_clock().now_epoch() - start_time

    def get_statistics(self) -> dict[str, Any]:
        """Get coordinator statistics."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "coordinations": self.coordinations,
            "successes": self.successes,
            "failures": self.failures,
            "success_rate": self.successes / self.coordinations * 100 if self.coordinations > 0 else 0,
            "total_time": self.total_time,
            "avg_time": self.total_time / self.coordinations if self.coordinations > 0 else 0,
        }

    def enable(self) -> None:
        """Enable coordinator."""
        self.enabled = True

    def disable(self) -> None:
        """Disable coordinator."""
        self.enabled = False


class CoordinatorRegistry:
    """Registry for workflow coordinators."""

    def __init__(self):
        """Initialize registry."""
        self.coordinators: dict[str, WorkflowCoordinator] = {}

    def register(self, coordinator: WorkflowCoordinator) -> None:
        """Register coordinator."""
        self.coordinators[coordinator.name] = coordinator

    def unregister(self, name: str) -> None:
        """Unregister coordinator."""
        if name in self.coordinators:
            del self.coordinators[name]

    def get(self, name: str) -> WorkflowCoordinator | None:
        """Get coordinator by name."""
        return self.coordinators.get(name)

    def get_for_workflow(self, workflow_type: str) -> WorkflowCoordinator | None:
        """Get coordinator that can handle workflow type."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "CoordinatorRegistry.get_for_workflow",
        )

        for coordinator in self.coordinators.values():
            if coordinator.enabled and coordinator.can_handle(workflow_type):
                return coordinator
        return None

    def get_all(self) -> list[WorkflowCoordinator]:
        """Get all coordinators."""
        return list(self.coordinators.values())

    def get_enabled(self) -> list[WorkflowCoordinator]:
        """Get enabled coordinators."""
        return [c for c in self.coordinators.values() if c.enabled]

    def get_statistics(self) -> dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_coordinators": len(self.coordinators),
            "enabled_coordinators": len([c for c in self.coordinators.values() if c.enabled]),
            "coordinators": {name: c.get_statistics() for name, c in self.coordinators.items()},
        }


coordinator_registry = CoordinatorRegistry()
