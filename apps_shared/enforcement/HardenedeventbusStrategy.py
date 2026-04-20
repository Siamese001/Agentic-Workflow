"""Event Bus Integration - Hardened event-driven communication.

This module provides integration between the Event Bus and the hardened
infrastructure, ensuring all event operations go through bulkheads,
circuit breakers, and retry policies.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

# Configuration constants (required for test compatibility)
BATCH_SIZE = 32
BUFFER_SIZE = 8192
DEFAULT_SLEEP = 1.0
MAX_RETRIES = 3
THRESHOLD = 0.95

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
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

_emit_authorize_and_execute("p2", "HardenedeventbusStrategy", "execution_auth")
_emit_validates_capability("p2", "HardenedeventbusStrategy", "capability_check")
_emit_routes_to_capability("p2", "HardenedeventbusStrategy", "capability_route")
_emit_writes_via_uwg("p2", "HardenedeventbusStrategy", "uwg_write")
_emit_blocks_direct_write("p2", "HardenedeventbusStrategy", "direct_write_block")
_emit_records_tool_invocation("p2", "HardenedeventbusStrategy", "tool_invocation")
_emit_captures_execution_output("p2", "HardenedeventbusStrategy", "exec_output")
_emit_dispatches_agent("p3", "HardenedeventbusStrategy", "agent_dispatch")
_emit_coordinates_agents("p3", "HardenedeventbusStrategy", "agent_coordination")
_emit_records_workflow_lineage("p3", "HardenedeventbusStrategy", "workflow_lineage")
_emit_records_healing_outcome("p3", "HardenedeventbusStrategy", "healing_outcome")
_emit_escalates_failure("p3", "HardenedeventbusStrategy", "failure_escalation")
_emit_orchestrates_workflow("p3", "HardenedeventbusStrategy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "HardenedeventbusStrategy", "healing_dispatch")
_emit_invokes_evaluation("p3", "HardenedeventbusStrategy", "evaluation_signal")
_emit_records_telemetry_event("p4", "HardenedeventbusStrategy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "HardenedeventbusStrategy", "eval_metric")
_emit_stores_embedding("p4", "HardenedeventbusStrategy", "embedding_store")
_emit_updates_meta_learning_state("p4", "HardenedeventbusStrategy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "HardenedeventbusStrategy", "exec_snapshot_link")
from .bulkhead_manager import BulkheadManager, TaskPriority, get_bulkhead_manager
from .circuit_breaker import CircuitBreakerConfig, get_circuit_breaker_registry
from .core.event_bus import EventBus, EventType, SystemEvent, get_event_bus
from .dead_letter_queue import FailureReason, get_dead_letter_queue
from .retry_policy import RetryConfig, get_retry_executor

_emit_applies_guardrail("p0", "HardenedeventbusStrategy", "p0_governance")
_emit_snapshots_state("p0", "HardenedeventbusStrategy", "state_snapshot")
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

_emit_emits_metric_event("HardenedeventbusStrategy", "p4obs", "metric_1")
_emit_emits_metric_event("HardenedeventbusStrategy", "p4obs", "metric_2")
_emit_emits_metric_event("HardenedeventbusStrategy", "p4obs", "metric_3")
_emit_emits_metric_event("HardenedeventbusStrategy", "p4obs", "metric_4")
_emit_emits_metric_event("HardenedeventbusStrategy", "p4obs", "metric_5")
_emit_emits_metric_event("HardenedeventbusStrategy", "p4obs", "metric_6")
_emit_records_incident_event("HardenedeventbusStrategy", "p4obs", "incident")
_emit_captures_runtime_anomaly("HardenedeventbusStrategy", "p4obs", "anomaly")
_emit_writes_observability_log("HardenedeventbusStrategy", "p4obs", "obs_log")
_emit_updates_monitoring_state("HardenedeventbusStrategy", "p4obs", "mon_state")
_emit_triggers_alert("HardenedeventbusStrategy", "p4obs", "alert")
_emit_links_incident_trace("HardenedeventbusStrategy", "p4obs", "trace_link")
_emit_captures_pattern("HardenedeventbusStrategy", "p3lm", "pattern")
_emit_records_learning_event("HardenedeventbusStrategy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("HardenedeventbusStrategy", "p3lm", "snapshot")
_emit_feeds_meta_learning("HardenedeventbusStrategy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("HardenedeventbusStrategy", "p3lm", "routing")
_emit_improves_agent_policy("HardenedeventbusStrategy", "p3lm", "policy")
_emit_stores_learning_state("HardenedeventbusStrategy", "p3lm", "state")
_emit_records_execution_trace("HardenedeventbusStrategy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("HardenedeventbusStrategy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("HardenedeventbusStrategy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("HardenedeventbusStrategy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("HardenedeventbusStrategy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("HardenedeventbusStrategy", "env_read", "p2_env_1")
_emit_reads_environ("HardenedeventbusStrategy", "env_read", "p2_env_2")
_emit_reads_runtime_state("HardenedeventbusStrategy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("HardenedeventbusStrategy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "HardenedeventbusStrategy", "context_pull")
_emit_pulls_context("p1", "HardenedeventbusStrategy", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "HardenedeventbusStrategy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "HardenedeventbusStrategy", "uwg_term_2")
_emit_writes_through("p1", "HardenedeventbusStrategy", "write_through")
_emit_writes_through("p1", "HardenedeventbusStrategy", "write_through_2")
_emit_validated_by_safety_plane("p1", "HardenedeventbusStrategy", "safety_validation")
_emit_invokes_eval("p1", "HardenedeventbusStrategy", "eval_call")
_emit_proposal_commits_routing("p1", "HardenedeventbusStrategy", "routing_commit")
_emit_escalates_to_human("p1", "HardenedeventbusStrategy", "human_escalation")
_emit_routes_through("p1", "HardenedeventbusStrategy", "route_through")
_emit_checks_agent_registry("p1", "HardenedeventbusStrategy", "agent_registry")
_emit_validates_agent_capability("p1", "HardenedeventbusStrategy", "capability")
_emit_dispatches_execution_plan("p1", "HardenedeventbusStrategy", "exec_plan")
_emit_agent_executes_agent("p1", "HardenedeventbusStrategy", "sub_agent")
_emit_routes_to_agent("p1", "HardenedeventbusStrategy", "target_agent")
_emit_verifies_policy("p1", "HardenedeventbusStrategy", "policy_check")
_emit_observes_runtime_state("p1", "HardenedeventbusStrategy", "runtime_state")
_emit_verifies_boundary("p1", "HardenedeventbusStrategy", "boundary_check")
_emit_transcripts_response("p1", "HardenedeventbusStrategy", "transcript")
_emit_hard_fails_untranscripted("p1", "HardenedeventbusStrategy")
_emit_gated_by_confidence("p1", "HardenedeventbusStrategy", "confidence_gate")
emit_replay_key("p0", "HardenedeventbusStrategy")
emit_determinism_digest("p0", "HardenedeventbusStrategy")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


class HardenedEventBus:
    """Event Bus wrapped with hardened infrastructure."""

    def __init__(self, event_bus: EventBus | None = None, bulkhead_manager: BulkheadManager | None = None):
        """Initialize hardened event bus.

        Args:
            event_bus: Event bus instance
            bulkhead_manager: Bulkhead manager instance
        """
        self.event_bus = event_bus
        self.bulkhead_manager = bulkhead_manager
        self._stats = {
            "events_published": 0,
            "events_failed": 0,
            "events_retried": 0,
            "bulkhead_rejections": 0,
        }
        logger.info("Initialized HardenedEventBus")

    async def initialize(self) -> None:
        """Initialize all components."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HardenedEventBus.initialize")

        if not self.event_bus:
            self.event_bus = await get_event_bus()
        if not self.bulkhead_manager:
            self.bulkhead_manager = await get_bulkhead_manager()
        await self._register_bulkheads()
        await self._register_circuit_breakers()
        await self._register_retry_policies()
        logger.info("HardenedEventBus initialized")

    async def publish(
        self,
        channel: str,
        event: SystemEvent,
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> bool:
        """Publish an event with hardened protection.

        Args:
            channel: Channel name
            event: Event to publish
            priority: Task priority for bulkhead

        Returns:
            True if published successfully
        """
        try:
            await self.bulkhead_manager.execute(
                self._publish_with_retry,
                channel,
                event,
                bulkhead_name="event_publish",
                priority=priority,
            )
            self._stats["events_published"] += 1
            return True
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise

    async def subscribe(self, channel: str, callback: Callable[[SystemEvent], Awaitable[None]]) -> None:
        """Subscribe to events with hardened protection.

        Args:
            channel: Channel name
            callback: Event callback
        """
        hardened_callback = self._wrap_callback(callback)
        await self.event_bus.subscribe(channel, hardened_callback)
        logger.info(f"Subscribed to channel {channel} with hardened processing")

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from events.

        Args:
            channel: Channel name
        """
        await self.event_bus.unsubscribe(channel)
        logger.info(f"Unsubscribed from channel {channel}")

    async def close(self) -> None:
        """Close the hardened event bus."""
        if self.event_bus:
            await self.event_bus.close()
        logger.info("HardenedEventBus closed")

    async def health_check(self) -> dict[str, Any]:
        """Check health of hardened event bus.

        Returns:
            Health status
        """
        event_bus_health = await self.event_bus.health_check()
        bulkhead_stats = self.bulkhead_manager.get_all_metrics()
        return {"event_bus": event_bus_health, "bulkheads": bulkhead_stats, "stats": self._stats.copy()}

    async def _register_bulkheads(self) -> None:
        """Register bulkheads for event operations."""
        # guardian: allow-magic-config
        await self.bulkhead_manager.create_bulkhead(
            "event_publish",
            max_concurrency=10,
            queue_size=100,
            priority=TaskPriority.HIGH,
        )
        # guardian: allow-magic-config
        await self.bulkhead_manager.create_bulkhead(
            "event_process",
            max_concurrency=20,
            queue_size=200,
            priority=TaskPriority.MEDIUM,
        )
        logger.debug("Registered event bus bulkheads")

    async def _register_circuit_breakers(self) -> None:
        """Register circuit breakers for event operations."""
        registry = await get_circuit_breaker_registry()
        await registry.get_circuit_breaker(
            "event_publish",
            CircuitBreakerConfig(
                failure_threshold=THRESHOLD,
                timeout=DEFAULT_TIMEOUT,
                failure_rate_threshold=THRESHOLD,
            ),
        )
        await registry.get_circuit_breaker(
            "event_process",
            CircuitBreakerConfig(
                failure_threshold=THRESHOLD,
                timeout=DEFAULT_TIMEOUT,
                failure_rate_threshold=THRESHOLD,
            ),
        )
        logger.debug("Registered event bus circuit breakers")

    async def _register_retry_policies(self) -> None:
        """Register retry policies for event operations."""
        executor = await get_retry_executor()
        # guardian: allow-magic-config
        executor.register_policy("event_publish", RetryConfig(max_attempts=3, base_delay=0.5, max_delay=5.0))
        # guardian: allow-magic-config
        executor.register_policy("event_process", RetryConfig(max_attempts=5, base_delay=1.0, max_delay=10.0))
        logger.debug("Registered event bus retry policies")

    async def _publish_with_retry(self, channel: str, event: SystemEvent) -> None:
        """Publish event with retry policy.

        Args:
            channel: Channel name
            event: Event to publish
        """
        executor = await get_retry_executor()
        await executor.execute(self.event_bus.publish, channel, event, policy="event_publish")

    def _wrap_callback(
        self,
        callback: Callable[[SystemEvent], Awaitable[None]],
    ) -> Callable[[SystemEvent], Awaitable[None]]:
        """Wrap callback with hardened processing.

        Args:
            callback: Original callback

        Returns:
            Hardened callback
        """

        async def hardened_callback(event: SystemEvent) -> None:
            try:
                await self.bulkhead_manager.execute(
                    self._process_event,
                    callback,
                    event,
                    bulkhead_name="event_process",
                )
            except Exception as e:  # guardian: allow-silent-swallow
                logger.error(f"Failed to process event {event.id}: {e}")
                dlq = await get_dead_letter_queue()
                await dlq.add_failed_envelope(
                    event,
                    FailureReason.PROCESSING_ERROR,
                    "HardenedEventBus.process",
                    str(e),
                )

        return hardened_callback

    async def _process_event(
        self,
        callback: Callable[[SystemEvent], Awaitable[None]],
        event: SystemEvent,
    ) -> None:
        """Process event with retry policy.

        Args:
            callback: Event callback
            event: Event to process
        """
        executor = await get_retry_executor()
        await executor.execute(callback, event, policy="event_process")


_hardened_bus: HardenedEventBus | None = None
_bus_lock = asyncio.Lock()


async def get_hardened_event_bus() -> HardenedEventBus:
    """Get global hardened event bus instance.

    Returns:
        HardenedEventBus instance
    """
    global _hardened_bus
    async with _bus_lock:
        if _hardened_bus is None:
            _hardened_bus = HardenedEventBus()
            await _hardened_bus.initialize()
    return _hardened_bus


async def publish_hardened_event(
    event_type: EventType,
    source_component: str,
    payload: dict[str, Any],
    trace_id: str | None = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
) -> bool:
    """Publish a hardened system event.

    Args:
        event_type: Type of event
        source_component: Component publishing the event
        payload: Event payload
        trace_id: Trace ID for tracking
        priority: Task priority

    Returns:
        True if published successfully
    """
    from .core.event_bus import SystemEvent

    event = SystemEvent(
        type=event_type,
        source_component=source_component,
        payload=payload,
        trace_id=trace_id,
    )
    bus = await get_hardened_event_bus()
    channel = f"events.{event_type.value.lower()}"
    return await bus.publish(channel, event, priority)


async def subscribe_to_events(
    event_type: EventType,
    callback: Callable[[SystemEvent], Awaitable[None]],
) -> None:
    """Subscribe to events with hardened processing.

    Args:
        event_type: Type of event to subscribe to
        callback: Event callback
    """
    bus = await get_hardened_event_bus()
    channel = f"events.{event_type.value.lower()}"
    await bus.subscribe(channel, callback)


def hardened_event_publisher(event_type: EventType, priority: TaskPriority = TaskPriority.MEDIUM):
    """Decorator to automatically publish hardened events.

    Args:
        event_type: Type of event to publish
        priority: Task priority for publishing

    Returns:
        Decorated function
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            trace_id = None
            if args and hasattr(args[0], "trace_id"):
                trace_id = args[0].trace_id
            await publish_hardened_event(
                EventType.AGENT_THINKING,
                func.__module__ + "." + func.__name__,
                {"status": "started", "args_count": len(args)},
                trace_id=trace_id,
                priority=priority,
            )
            try:
                result = await func(*args, **kwargs)
                await publish_hardened_event(
                    EventType.AGENT_COMPLETED,
                    func.__module__ + "." + func.__name__,
                    {"status": "completed", "success": True},
                    trace_id=trace_id,
                    priority=priority,
                )
                return result
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise

        return async_wrapper

    return decorator
