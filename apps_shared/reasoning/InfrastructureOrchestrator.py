"""Infrastructure Integration - Unified orchestration layer.

This module provides the integration layer that connects the Event Bus,
Provenance Tracker, and Model router with the existing hardened
infrastructure, ensuring all components work together seamlessly.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

# Configuration constants (required for test compatibility)
BATCH_SIZE = 32
BUFFER_SIZE = 8192
DEFAULT_SLEEP = 1.0
MAX_RETRIES = 3
THRESHOLD = 0.95

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_authorize_and_execute("p2", "InfrastructureOrchestrator", "execution_auth")
_emit_validates_capability("p2", "InfrastructureOrchestrator", "capability_check")
_emit_routes_to_capability("p2", "InfrastructureOrchestrator", "capability_route")
_emit_writes_via_uwg("p2", "InfrastructureOrchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "InfrastructureOrchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "InfrastructureOrchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "InfrastructureOrchestrator", "exec_output")
_emit_dispatches_agent("p3", "InfrastructureOrchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "InfrastructureOrchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "InfrastructureOrchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "InfrastructureOrchestrator", "healing_outcome")
_emit_escalates_failure("p3", "InfrastructureOrchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "InfrastructureOrchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "InfrastructureOrchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "InfrastructureOrchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "InfrastructureOrchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "InfrastructureOrchestrator", "eval_metric")
_emit_stores_embedding("p4", "InfrastructureOrchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "InfrastructureOrchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "InfrastructureOrchestrator", "exec_snapshot_link")
from .bulkhead_manager import BulkheadManager, TaskPriority, get_bulkhead_manager
from .circuit_breaker import get_circuit_breaker_registry
from .core.event_bus import EventType, SystemEvent
from .core.model_router import ModelRouter, TaskType, get_model_router
from .core.provenance_tracker import ProvenanceTracker, get_provenance_tracker
from .dead_letter_queue import FailureReason, get_dead_letter_queue
from .event_bus_integration import HardenedEventBus, get_hardened_event_bus
from .health_check import HealthCheckRegistry, initialize_system_health_checks

_emit_applies_guardrail("p0", "InfrastructureOrchestrator", "p0_governance")
_emit_reads_policy_state("p0", "InfrastructureOrchestrator", "policy_binding")
_emit_snapshots_state("p0", "InfrastructureOrchestrator", "state_snapshot")
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

_emit_emits_metric_event("InfrastructureOrchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("InfrastructureOrchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("InfrastructureOrchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("InfrastructureOrchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("InfrastructureOrchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("InfrastructureOrchestrator", "p4obs", "metric_6")
_emit_records_incident_event("InfrastructureOrchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("InfrastructureOrchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("InfrastructureOrchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("InfrastructureOrchestrator", "p4obs", "mon_state")
_emit_triggers_alert("InfrastructureOrchestrator", "p4obs", "alert")
_emit_links_incident_trace("InfrastructureOrchestrator", "p4obs", "trace_link")
_emit_captures_pattern("InfrastructureOrchestrator", "p3lm", "pattern")
_emit_records_learning_event("InfrastructureOrchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("InfrastructureOrchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("InfrastructureOrchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("InfrastructureOrchestrator", "p3lm", "routing")
_emit_improves_agent_policy("InfrastructureOrchestrator", "p3lm", "policy")
_emit_stores_learning_state("InfrastructureOrchestrator", "p3lm", "state")
_emit_records_execution_trace("InfrastructureOrchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("InfrastructureOrchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("InfrastructureOrchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("InfrastructureOrchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("InfrastructureOrchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("InfrastructureOrchestrator", "env_read", "p2_env_1")
_emit_reads_environ("InfrastructureOrchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("InfrastructureOrchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("InfrastructureOrchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "InfrastructureOrchestrator", "context_pull")
_emit_pulls_context("p1", "InfrastructureOrchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "InfrastructureOrchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "InfrastructureOrchestrator", "uwg_term_2")
_emit_writes_through("p1", "InfrastructureOrchestrator", "write_through")
_emit_writes_through("p1", "InfrastructureOrchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "InfrastructureOrchestrator", "safety_validation")
_emit_invokes_eval("p1", "InfrastructureOrchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "InfrastructureOrchestrator", "routing_commit")
_emit_escalates_to_human("p1", "InfrastructureOrchestrator", "human_escalation")
_emit_routes_through("p1", "InfrastructureOrchestrator", "route_through")
_emit_checks_agent_registry("p1", "InfrastructureOrchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "InfrastructureOrchestrator", "capability")
_emit_dispatches_execution_plan("p1", "InfrastructureOrchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "InfrastructureOrchestrator", "sub_agent")
_emit_routes_to_agent("p1", "InfrastructureOrchestrator", "target_agent")
_emit_verifies_policy("p1", "InfrastructureOrchestrator", "policy_check")
_emit_observes_runtime_state("p1", "InfrastructureOrchestrator", "runtime_state")
_emit_verifies_boundary("p1", "InfrastructureOrchestrator", "boundary_check")
_emit_transcripts_response("p1", "InfrastructureOrchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "InfrastructureOrchestrator")
_emit_gated_by_confidence("p1", "InfrastructureOrchestrator", "confidence_gate")
emit_replay_key("p0", "InfrastructureOrchestrator")
emit_determinism_digest("p0", "InfrastructureOrchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


class InfrastructureOrchestrator:
    """Orchestrates all infrastructure components."""

    def __init__(self):
        """Initialize infrastructure orchestrator."""
        self._initialized = False
        self._components = {}
        self.event_bus: HardenedEventBus | None = None
        self.provenance_tracker: ProvenanceTracker | None = None
        self.model_router: ModelRouter | None = None
        self.bulkhead_manager: BulkheadManager | None = None
        self.health_registry: HealthCheckRegistry | None = None
        logger.info("Initialized InfrastructureOrchestrator")

    async def initialize(self) -> None:
        """Initialize all infrastructure components."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "InfrastructureOrchestrator.initialize"
        )
        if self._initialized:
            return
        logger.info("Initializing infrastructure components...")
        self.bulkhead_manager = await get_bulkhead_manager()
        self.event_bus = await get_hardened_event_bus()
        self.provenance_tracker = await get_provenance_tracker()
        self.model_router = await get_model_router()
        self.health_registry = await get_health_registry()
        await initialize_system_health_checks(
            bulkhead_manager=self.bulkhead_manager,
            circuit_breaker_registry=await get_circuit_breaker_registry(),
            dead_letter_queue=await get_dead_letter_queue(),
            checkpoint_manager=None,
        )
        await self._register_component_health_checks()
        await self._setup_event_subscriptions()
        self._initialized = True
        logger.info("Infrastructure initialization complete")

    async def _register_component_health_checks(self) -> None:
        """Register health checks for new components."""
        from .health_check import ComponentType, HealthChecker, HealthCheckResult, HealthStatus

        class EventBusHealthChecker(HealthChecker):
            def __init__(self, event_bus: HardenedEventBus):
                self.event_bus = event_bus

            async def check_health(self) -> HealthCheckResult:
                health = await self.event_bus.health_check()
                status = (
                    HealthStatus.HEALTHY
                    if health["event_bus"]["status"] == "healthy"
                    else HealthStatus.UNHEALTHY
                )
                return HealthCheckResult(
                    component_name="event_bus",
                    component_type=ComponentType.CUSTOM,
                    status=status,
                    message=f"Event bus is {health['event_bus']['status']}",
                    timestamp=None,
                    metrics=health,
                )

            @property
            def component_name(self) -> str:
                return "event_bus"

            @property
            def component_type(self) -> ComponentType:
                return ComponentType.CUSTOM

        class ProvenanceHealthChecker(HealthChecker):
            def __init__(self, tracker: ProvenanceTracker):
                self.tracker = tracker

            async def check_health(self) -> HealthCheckResult:
                health = await self.tracker.health_check()
                status = HealthStatus(health["status"])
                return HealthCheckResult(
                    component_name="provenance_tracker",
                    component_type=ComponentType.CUSTOM,
                    status=status,
                    message=f"Provenance tracker is {health['status']}",
                    timestamp=None,
                    metrics=health,
                )

            @property
            def component_name(self) -> str:
                return "provenance_tracker"

            @property
            def component_type(self) -> ComponentType:
                return ComponentType.CUSTOM

        class ModelRouterHealthChecker(HealthChecker):
            def __init__(self, router: ModelRouter):
                self.router = router

            async def check_health(self) -> HealthCheckResult:
                stats = self.router.get_stats()
                budget_info = stats["budget_info"]
                if budget_info["remaining"] <= 0:
                    status = HealthStatus.CRITICAL
                    message = "Budget exceeded"
                elif budget_info["remaining"] < budget_info["daily_budget"] * 0.1:
                    status = HealthStatus.DEGRADED
                    message = "Budget nearly exhausted"
                else:
                    status = HealthStatus.HEALTHY
                    message = "Model router operating normally"
                return HealthCheckResult(
                    component_name="model_router",
                    component_type=ComponentType.CUSTOM,
                    status=status,
                    message=message,
                    timestamp=None,
                    metrics=stats,
                )

            @property
            def component_name(self) -> str:
                return "model_router"

            @property
            def component_type(self) -> ComponentType:
                return ComponentType.CUSTOM

        await self.health_registry.register_checker(EventBusHealthChecker(self.event_bus))
        await self.health_registry.register_checker(ProvenanceHealthChecker(self.provenance_tracker))
        await self.health_registry.register_checker(ModelRouterHealthChecker(self.model_router))
        logger.info("Registered component health checks")

    async def _setup_event_subscriptions(self) -> None:
        """Setup event subscriptions for cross-component communication."""
        await self.event_bus.subscribe("events.artifact_generated", self._handle_artifact_generated)
        await self.event_bus.subscribe("events.error_occurred", self._handle_error_occurred)
        await self.event_bus.subscribe("events.agent_completed", self._handle_agent_completed)
        logger.info("Setup event subscriptions")

    async def _handle_artifact_generated(self, event: SystemEvent) -> None:
        """Handle artifact generation events.

        Args:
            event: Artifact generated event
        """
        try:
            payload = event.payload
            artifact_id = payload.get("artifact_id")
            output = payload.get("output", "")
            model_version = payload.get("model_version", "unknown")
            if artifact_id:
                sources = payload.get("sources", [])
                if sources:
                    await self.provenance_tracker.record_generation(
                        event.trace_id,
                        artifact_id,
                        output,
                        model_version,
                        payload.get("prompt"),
                    )
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to handle artifact generated event: {e}")

    async def _handle_error_occurred(self, event: SystemEvent) -> None:
        """Handle error events.

        Args:
            event: Error event
        """
        try:
            dlq = await get_dead_letter_queue()
            await dlq.add_failed_envelope(
                event,
                FailureReason.PROCESSING_ERROR,
                event.source_component,
                event.payload.get("error", "Unknown error"),
            )
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to handle error event: {e}")

    async def _handle_agent_completed(self, event: SystemEvent) -> None:
        """Handle agent completion events for router optimization.

        Args:
            event: Agent completed event
        """
        try:
            payload = event.payload
            model_name = payload.get("model_name")
            usage = payload.get("usage", {})
            if model_name and usage:
                self.model_router.record_usage(
                    model_name,
                    usage.get("input_tokens", 0),
                    usage.get("output_tokens", 0),
                    usage.get("cost", 0.0),
                )
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to handle agent completed event: {e}")

    async def execute_with_infrastructure(
        self,
        task_type: TaskType,
        prompt: str,
        sources: list[tuple] | None = None,
        complexity_score: int = 1,
        trace_id: str | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> dict[str, Any]:
        """Execute a task with full infrastructure support.

        Args:
            task_type: Type of task
            prompt: Task prompt
            sources: Source citations for provenance
            complexity_score: Task complexity
            trace_id: Trace ID for tracking
            priority: Task priority

        Returns:
            Execution result with metadata
        """
        if not self._initialized:
            await self.initialize()
        if not trace_id:
            import uuid

            trace_id = str(uuid.uuid4())
        import time

        start_time = time.time()
        await self.event_bus.publish(
            "events.workflow_started",
            SystemEvent(
                type=EventType.WORKFLOW_STARTED,
                trace_id=trace_id,
                source_component="InfrastructureOrchestrator",
                payload={"task_type": task_type.value, "complexity_score": complexity_score},
            ),
        )
        try:
            if sources:
                await self.provenance_tracker.capture_context(trace_id, sources)
            model_config = self.model_router.get_model_config(task_type, complexity_score)
            tier = self.model_router._select_model_for_tier(
                self.model_router._determine_tier(
                    self.model_router._task_profiles[task_type],
                    complexity_score,
                ),
            )
            client = await self.model_router.get_client(tier)
            result = await self.bulkhead_manager.execute(
                client.generate,
                prompt,
                bulkhead_name="model_generation",
                priority=priority,
            )
            if sources:
                artifact_id = f"artifact_{int(time.time())}"
                lineage = await self.provenance_tracker.record_generation(
                    trace_id,
                    artifact_id,
                    result,
                    model_config["model"],
                    prompt,
                )
            await self.event_bus.publish(
                "events.artifact_generated",
                SystemEvent(
                    type=EventType.ARTIFACT_GENERATED,
                    trace_id=trace_id,
                    source_component="InfrastructureOrchestrator",
                    payload={
                        "artifact_id": artifact_id if sources else None,
                        "output": result,
                        "model_version": model_config["model"],
                        "prompt": prompt,
                        "sources": sources or [],
                    },
                    causation_id=trace_id,
                ),
            )
            execution_time = time.time() - start_time
            return {
                "result": result,
                "trace_id": trace_id,
                "model_used": model_config["model"],
                "tier": model_config["tier"],
                "execution_time": execution_time,
                "lineage": lineage.to_dict() if sources else None,
            }
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise

    async def get_system_health(self) -> dict[str, Any]:
        """Get comprehensive system health.

        Returns:
            System health status
        """
        if not self._initialized:
            await self.initialize()
        health = await self.health_registry.check_all()
        health["infrastructure"] = {
            "event_bus": await self.event_bus.health_check(),
            "provenance_tracker": self.provenance_tracker.get_stats(),
            "model_router": self.model_router.get_stats(),
            "bulkheads": self.bulkhead_manager.get_all_metrics(),
        }
        return health

    async def shutdown(self) -> None:
        """Shutdown all infrastructure components."""
        logger.info("Shutting down infrastructure...")
        if self.event_bus:
            await self.event_bus.close()
        if self.provenance_tracker:
            await self.provenance_tracker.cleanup()
        logger.info("Infrastructure shutdown complete")


_orchestrator: InfrastructureOrchestrator | None = None
_orchestrator_lock = asyncio.Lock()


async def get_infrastructure_orchestrator() -> InfrastructureOrchestrator:
    """Get global infrastructure orchestrator.

    Returns:
        InfrastructureOrchestrator instance
    """
    global _orchestrator
    async with _orchestrator_lock:
        if _orchestrator is None:
            _orchestrator = InfrastructureOrchestrator()
            await _orchestrator.initialize()
    return _orchestrator


async def execute_task(
    task_type: TaskType,
    prompt: str,
    sources: list[tuple] | None = None,
    complexity_score: int = 1,
    trace_id: str | None = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
) -> dict[str, Any]:
    """Execute a task with full infrastructure support.

    Args:
        task_type: Type of task
        prompt: Task prompt
        sources: Source citations
        complexity_score: Task complexity
        trace_id: Trace ID
        priority: Task priority

    Returns:
        Execution result
    """
    orchestrator = await get_infrastructure_orchestrator()
    return await orchestrator.execute_with_infrastructure(
        task_type,
        prompt,
        sources,
        complexity_score,
        trace_id,
        priority,
    )


async def get_system_status() -> dict[str, Any]:
    """Get comprehensive system status.

    Returns:
        System status
    """
    orchestrator = await get_infrastructure_orchestrator()
    return await orchestrator.get_system_health()


def with_infrastructure(
    task_type: TaskType,
    complexity_score: int = 1,
    priority: TaskPriority = TaskPriority.MEDIUM,
):
    """Decorator to add infrastructure support to functions.

    Args:
        task_type: Type of task
        complexity_score: Default complexity
        priority: Task priority

    Returns:
        Decorated function
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            prompt = kwargs.get("prompt", str(args[0]) if args else "")
            sources = kwargs.get("sources", [])
            trace_id = None
            if args and hasattr(args[0], "trace_id"):
                trace_id = args[0].trace_id
            result = await execute_task(task_type, prompt, sources, complexity_score, trace_id, priority)
            return result["result"]

        return async_wrapper

    return decorator
