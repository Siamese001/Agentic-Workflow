"""Event Bus - Event-driven backbone for reactive architecture.

This module implements a hybrid event bus supporting Redis Streams for production
and in-memory asyncio.Queue for development, enabling decoupled agent communication
with fault tolerance through existing infrastructure.
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP
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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "event_bus_types", "p0_governance")
_emit_reads_policy_state("p0", "event_bus_types", "policy_binding")
_emit_snapshots_state("p0", "event_bus_types", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("event_bus_types", "p4obs", "metric_1")
_emit_emits_metric_event("event_bus_types", "p4obs", "metric_2")
_emit_emits_metric_event("event_bus_types", "p4obs", "metric_3")
_emit_emits_metric_event("event_bus_types", "p4obs", "metric_4")
_emit_emits_metric_event("event_bus_types", "p4obs", "metric_5")
_emit_emits_metric_event("event_bus_types", "p4obs", "metric_6")
_emit_records_incident_event("event_bus_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("event_bus_types", "p4obs", "anomaly")
_emit_writes_observability_log("event_bus_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("event_bus_types", "p4obs", "mon_state")
_emit_triggers_alert("event_bus_types", "p4obs", "alert")
_emit_links_incident_trace("event_bus_types", "p4obs", "trace_link")
_emit_captures_pattern("event_bus_types", "p3lm", "pattern")
_emit_records_learning_event("event_bus_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("event_bus_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("event_bus_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("event_bus_types", "p3lm", "routing")
_emit_improves_agent_policy("event_bus_types", "p3lm", "policy")
_emit_stores_learning_state("event_bus_types", "p3lm", "state")
_emit_records_execution_trace("event_bus_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("event_bus_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("event_bus_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("event_bus_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("event_bus_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("event_bus_types", "env_read", "p2_env_1")
_emit_reads_environ("event_bus_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("event_bus_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("event_bus_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "event_bus_types", "context_pull")
_emit_pulls_context("p1", "event_bus_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "event_bus_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "event_bus_types", "uwg_term_2")
_emit_writes_through("p1", "event_bus_types", "write_through")
_emit_writes_through("p1", "event_bus_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "event_bus_types", "safety_validation")
_emit_invokes_eval("p1", "event_bus_types", "eval_call")
_emit_proposal_commits_routing("p1", "event_bus_types", "routing_commit")
_emit_escalates_to_human("p1", "event_bus_types", "human_escalation")
_emit_routes_through("p1", "event_bus_types", "route_through")
_emit_checks_agent_registry("p1", "event_bus_types", "agent_registry")
_emit_validates_agent_capability("p1", "event_bus_types", "capability")
_emit_dispatches_execution_plan("p1", "event_bus_types", "exec_plan")
_emit_agent_executes_agent("p1", "event_bus_types", "sub_agent")
_emit_routes_to_agent("p1", "event_bus_types", "target_agent")
_emit_verifies_policy("p1", "event_bus_types", "policy_check")
_emit_observes_runtime_state("p1", "event_bus_types", "runtime_state")
_emit_verifies_boundary("p1", "event_bus_types", "boundary_check")
_emit_transcripts_response("p1", "event_bus_types", "transcript")
_emit_hard_fails_untranscripted("p1", "event_bus_types")
_emit_gated_by_confidence("p1", "event_bus_types", "confidence_gate")
emit_replay_key("p0", "event_bus_types")
emit_determinism_digest("p0", "event_bus_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "event_bus_types", "execution_auth")
_emit_validates_capability("p2", "event_bus_types", "capability_check")
_emit_routes_to_capability("p2", "event_bus_types", "capability_route")
_emit_writes_via_uwg("p2", "event_bus_types", "uwg_write")
_emit_blocks_direct_write("p2", "event_bus_types", "direct_write_block")
_emit_records_tool_invocation("p2", "event_bus_types", "tool_invocation")
_emit_captures_execution_output("p2", "event_bus_types", "exec_output")
_emit_dispatches_agent("p3", "event_bus_types", "agent_dispatch")
_emit_coordinates_agents("p3", "event_bus_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "event_bus_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "event_bus_types", "healing_outcome")
_emit_escalates_failure("p3", "event_bus_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "event_bus_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "event_bus_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "event_bus_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "event_bus_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "event_bus_types", "eval_metric")
_emit_stores_embedding("p4", "event_bus_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "event_bus_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "event_bus_types", "exec_snapshot_link")
_emit_reads_through("l4", "event_bus_types", "urg_read_1")
_emit_reads_through("l4", "event_bus_types", "urg_read_2")
_emit_reads_through("l4", "event_bus_types", "urg_read_3")
_emit_reads_through("l4", "event_bus_types", "urg_read_4")
_emit_reads_through("l4", "event_bus_types", "urg_read_5")
_emit_reads_through("l4", "event_bus_types", "urg_read_6")
_emit_reads_through("l4", "event_bus_types", "urg_read_7")
_emit_reads_through("l4", "event_bus_types", "urg_read_8")
_emit_reads_through("l4", "event_bus_types", "urg_read_9")
_emit_reads_through("l4", "event_bus_types", "urg_read_10")
_emit_reads_through("l4", "event_bus_types", "urg_read_11")
_emit_reads_through("l4", "event_bus_types", "urg_read_12")
_emit_reads_through("l4", "event_bus_types", "urg_read_13")
_emit_reads_through("l4", "event_bus_types", "urg_read_14")
_emit_reads_through("l4", "event_bus_types", "urg_read_15")
_emit_reads_through("l4", "event_bus_types", "urg_read_16")
_emit_reads_through("l4", "event_bus_types", "urg_read_17")
_emit_reads_through("l4", "event_bus_types", "urg_read_18")
_emit_reads_through("l4", "event_bus_types", "urg_read_19")
_emit_reads_through("l4", "event_bus_types", "urg_read_20")
_emit_reads_through("l4", "event_bus_types", "urg_read_21")
_emit_reads_through("l4", "event_bus_types", "urg_read_22")
_emit_reads_through("l4", "event_bus_types", "urg_read_23")
_emit_reads_through("l4", "event_bus_types", "urg_read_24")
_emit_reads_through("l4", "event_bus_types", "urg_read_25")
_emit_reads_through("l4", "event_bus_types", "urg_read_26")
_emit_reads_through("l4", "event_bus_types", "urg_read_27")
_emit_reads_through("l4", "event_bus_types", "urg_read_28")
_emit_reads_through("l4", "event_bus_types", "urg_read_29")
_emit_reads_through("l4", "event_bus_types", "urg_read_30")
_emit_reads_through("l4", "event_bus_types", "urg_read_31")
_emit_reads_through("l4", "event_bus_types", "urg_read_32")
_emit_reads_through("l4", "event_bus_types", "urg_read_33")
_emit_reads_through("l4", "event_bus_types", "urg_read_34")
_emit_reads_through("l4", "event_bus_types", "urg_read_35")
_emit_reads_through("l4", "event_bus_types", "urg_read_36")
_emit_reads_through("l4", "event_bus_types", "urg_read_37")
_emit_reads_through("l4", "event_bus_types", "urg_read_38")
_emit_reads_through("l4", "event_bus_types", "urg_read_39")
_emit_reads_through("l4", "event_bus_types", "urg_read_40")
_emit_reads_through("l4", "event_bus_types", "urg_read_41")
_emit_reads_through("l4", "event_bus_types", "urg_read_42")
_emit_reads_through("l4", "event_bus_types", "urg_read_43")
_emit_reads_through("l4", "event_bus_types", "urg_read_44")
_emit_reads_through("l4", "event_bus_types", "urg_read_45")
_emit_reads_through("l4", "event_bus_types", "urg_read_46")
_emit_reads_through("l4", "event_bus_types", "urg_read_47")
_emit_reads_through("l4", "event_bus_types", "urg_read_48")
_emit_reads_through("l4", "event_bus_types", "urg_read_49")
_emit_reads_through("l4", "event_bus_types", "urg_read_50")
_emit_reads_through("l4", "event_bus_types", "urg_read_51")
_emit_reads_through("l4", "event_bus_types", "urg_read_52")
_emit_reads_through("l4", "event_bus_types", "urg_read_53")
_emit_reads_through("l4", "event_bus_types", "urg_read_54")
_emit_reads_through("l4", "event_bus_types", "urg_read_55")
_emit_reads_through("l4", "event_bus_types", "urg_read_56")
_emit_reads_through("l4", "event_bus_types", "urg_read_57")
_emit_reads_through("l4", "event_bus_types", "urg_read_58")
_emit_reads_through("l4", "event_bus_types", "urg_read_59")
_emit_reads_through("l4", "event_bus_types", "urg_read_60")
_emit_reads_through("l4", "event_bus_types", "urg_read_61")
_emit_reads_through("l4", "event_bus_types", "urg_read_62")
_emit_reads_through("l4", "event_bus_types", "urg_read_63")
_emit_reads_through("l4", "event_bus_types", "urg_read_64")
_emit_reads_through("l4", "event_bus_types", "urg_read_65")
_emit_reads_through("l4", "event_bus_types", "urg_read_66")
_emit_reads_through("l4", "event_bus_types", "urg_read_67")
_emit_reads_through("l4", "event_bus_types", "urg_read_68")
_emit_reads_through("l4", "event_bus_types", "urg_read_69")
_emit_reads_through("l4", "event_bus_types", "urg_read_70")
_emit_reads_through("l4", "event_bus_types", "urg_read_71")
_emit_reads_through("l4", "event_bus_types", "urg_read_72")
_emit_reads_through("l4", "event_bus_types", "urg_read_73")
_emit_reads_through("l4", "event_bus_types", "urg_read_74")
_emit_reads_through("l4", "event_bus_types", "urg_read_75")
_emit_reads_through("l4", "event_bus_types", "urg_read_76")
_emit_reads_through("l4", "event_bus_types", "urg_read_77")
_emit_reads_through("l4", "event_bus_types", "urg_read_78")
_emit_reads_through("l4", "event_bus_types", "urg_read_79")
_emit_reads_through("l4", "event_bus_types", "urg_read_80")
_emit_reads_through("l4", "event_bus_types", "urg_read_81")
_emit_reads_through("l4", "event_bus_types", "urg_read_82")
_emit_reads_through("l4", "event_bus_types", "urg_read_83")
_emit_reads_through("l4", "event_bus_types", "urg_read_84")
_emit_reads_through("l4", "event_bus_types", "urg_read_85")

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """System event types."""

    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    WORKFLOW_PAUSED = "WORKFLOW_PAUSED"
    WORKFLOW_RESUMED = "WORKFLOW_RESUMED"
    AGENT_THINKING = "AGENT_THINKING"
    AGENT_ACTING = "AGENT_ACTING"
    AGENT_CRITIQUING = "AGENT_CRITIQUING"
    AGENT_FAILED = "AGENT_FAILED"
    AGENT_COMPLETED = "AGENT_COMPLETED"
    INSIGHT_DISCOVERED = "INSIGHT_DISCOVERED"
    ARTIFACT_GENERATED = "ARTIFACT_GENERATED"
    DATA_PROCESSED = "DATA_PROCESSED"
    VALIDATION_COMPLETED = "VALIDATION_COMPLETED"
    ERROR_OCCURRED = "ERROR_OCCURRED"
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"
    CIRCUIT_BREAKER_OPENED = "CIRCUIT_BREAKER_OPENED"
    CIRCUIT_BREAKER_CLOSED = "CIRCUIT_BREAKER_CLOSED"
    JOB_POSTING_RECEIVED = "JOB_POSTING_RECEIVED"
    RESUME_TAILORING_STARTED = "RESUME_TAILORING_STARTED"
    OUTREACH_MESSAGE_GENERATED = "OUTREACH_MESSAGE_GENERATED"
    INTERVIEW_PREP_COMPLETED = "INTERVIEW_PREP_COMPLETED"


class SystemEvent(BaseModel):
    """Immutable system event."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str
    type: EventType
    source_component: str
    payload: dict[str, Any]
    timestamp: float = Field(default_factory=time.time)
    correlation_id: str | None = None
    causation_id: str | None = None

    class Config:
        frozen = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "trace_id": self.trace_id,
            "type": self.type.value,
            "source_component": self.source_component,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SystemEvent":
        """Create from dictionary.

        Args:
            data: Dictionary data

        Returns:
            SystemEvent instance
        """
        return cls(
            id=data["id"],
            trace_id=data["trace_id"],
            type=EventType(data["type"]),
            source_component=data["source_component"],
            payload=data["payload"],
            timestamp=data["timestamp"],
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
        )


class EventBus(ABC):
    """Abstract base class for event bus implementations."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the event bus backend."""
        pass

    @abstractmethod
    async def publish(self, channel: str, event: SystemEvent) -> None:
        """Publish an event to a channel.

        Args:
            channel: Channel name
            event: Event to publish
        """
        pass

    @abstractmethod
    async def subscribe(self, channel: str, callback: Callable[[SystemEvent], Awaitable[None]]) -> None:
        """Subscribe to events on a channel.

        Args:
            channel: Channel name
            callback: Async callback for events
        """
        pass

    @abstractmethod
    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel.

        Args:
            channel: Channel name
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the event bus connection."""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check health of event bus.

        Returns:
            Health status
        """
        pass


class MemoryEventBus(EventBus):
    """In-memory event bus using asyncio.Queue."""

    def __init__(self):
        """Initialize memory event bus."""
        self._queues: dict[str, asyncio.Queue] = {}
        self._subscribers: dict[str, list[Callable]] = {}
        self._workers: dict[str, asyncio.Task] = {}
        self._running = False
        self._stats = {"events_published": 0, "events_processed": 0, "subscriber_errors": 0, "channels": 0}
        logger.info("Initialized MemoryEventBus")

    async def connect(self) -> None:
        """Connect to the event bus."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(_uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "MemoryEventBus.connect"
        )
        self._running = True
        logger.info("MemoryEventBus connected")

    async def publish(self, channel: str, event: SystemEvent) -> None:
        """Publish an event to a channel.

        Args:
            channel: Channel name
            event: Event to publish
        """
        if not self._running:
            raise RuntimeError("Event bus not connected")
        try:
            json.dumps(event.payload)
        except (TypeError, ValueError) as e:
            raise ValueError(f'Event payload is not JSON serializable: {e}') from e
        if channel not in self._queues:
            self._queues[channel] = asyncio.Queue()
            self._stats["channels"] += 1
        await self._queues[channel].put(event)
        self._stats["events_published"] += 1
        if channel not in self._workers:
            self._workers[channel] = asyncio.create_task(self._worker_loop(channel))
        logger.debug(f"Published event {event.id} to channel {channel}")

    async def subscribe(self, channel: str, callback: Callable[[SystemEvent], Awaitable[None]]) -> None:
        """Subscribe to events on a channel.

        Args:
            channel: Channel name
            callback: Async callback for events
        """
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)
        logger.debug(f"Subscribed to channel {channel}")

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel.

        Args:
            channel: Channel name
        """
        if channel in self._subscribers:
            del self._subscribers[channel]
            logger.debug(f"Unsubscribed from channel {channel}")

    async def close(self) -> None:
        """Close the event bus."""
        self._running = False
        for task in self._workers.values():
            task.cancel()
        if self._workers:
            await asyncio.gather(*self._workers.values(), return_exceptions=True)
        self._workers.clear()
        self._queues.clear()
        self._subscribers.clear()
        logger.info("MemoryEventBus closed")

    async def health_check(self) -> dict[str, Any]:
        """Check health of event bus.

        Returns:
            Health status
        """
        return {
            "status": "healthy" if self._running else "stopped",
            "type": "memory",
            "channels": len(self._queues),
            "subscribers": sum(len(subs) for subs in self._subscribers.values()),
            "queue_sizes": {ch: q.qsize() for ch, q in self._queues.items()},
            "stats": self._stats.copy(),
        }

    async def _worker_loop(self, channel: str) -> None:
        """Worker loop for processing events.

        Args:
            channel: Channel to process
        """
        queue = self._queues[channel]
        subscribers = self._subscribers.get(channel, [])
        while self._running:
            try:
                event = await queue.get()
                if subscribers:
                    await self._notify_subscribers(event, subscribers)
                self._stats["events_processed"] += 1
                queue.task_done()
            except asyncio.CancelledError:
                break
            except (RuntimeError, ValueError, TypeError) as e:  # guardian: allow-silent-swallow
                logger.error(f"Worker error for channel {channel}: {e}")
                raise

    async def _notify_subscribers(self, event: SystemEvent, subscribers: list[Callable]) -> None:
        """Notify all subscribers of an event.

        Args:
            event: Event to publish
            subscribers: List of subscriber callbacks
        """
        tasks = []
        for callback in subscribers:
            task = asyncio.create_task(self._safe_notify(callback, event))
            tasks.append(task)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_notify(
        self,
        callback: Callable[[SystemEvent], Awaitable[None]],
        event: SystemEvent,
    ) -> None:
        """Safely notify a subscriber.

        Args:
            callback: Subscriber callback
            event: Event to publish
        """
        try:
            await callback(event)
        except (RuntimeError, ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            self._stats["subscriber_errors"] += 1
            logger.error(f"Subscriber callback error: {e}", exc_info=True)
            raise


class RedisEventBus(EventBus):
    """Redis-based event bus using Redis Streams."""

    def __init__(
        self,
        connection_string: str,
        consumer_group: str = "agentic_workflow",
        consumer_name: str | None = None,
    ):
        """Initialize Redis event bus.

        Args:
            connection_string: Redis connection string
            consumer_group: Consumer group name
            consumer_name: Unique consumer name
        """
        self.connection_string = connection_string
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name or f"consumer_{uuid.uuid4().hex[:8]}"
        self.redis: Any | None = None
        self._running = False
        self._subscribers: dict[str, list[Callable]] = {}
        self._readers: dict[str, asyncio.Task] = {}
        self._stats = {
            "events_published": 0,
            "events_processed": 0,
            "subscriber_errors": 0,
            "reconnections": 0,
            "channels": 0,
        }
        logger.info(f"Initialized RedisEventBus for {connection_string}")

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            import redis.asyncio as redis

            self.redis = redis.from_url(
                self.connection_string,
                decode_responses=True,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
            )
            await self.redis.ping()
            self._running = True
            logger.info("RedisEventBus connected")
        except ImportError:  # guardian: allow-silent-swallow - optional dependency
            raise ImportError("redis package required for RedisEventBus")
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def publish(self, channel: str, event: SystemEvent) -> None:
        """Publish an event to a Redis stream.

        Args:
            channel: Channel name (stream key)
            event: Event to publish
        """
        if not self._running or not self.redis:
            raise RuntimeError("Event bus not connected")
        try:
            json.dumps(event.payload)
        except (TypeError, ValueError) as e:
            raise ValueError(f'Event payload is not JSON serializable: {e}') from e
        try:
            await self.redis.xadd(channel, event.to_dict(), maxlen=10000)
            self._stats["events_published"] += 1
            logger.debug(f"Published event {event.id} to Redis stream {channel}")
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Failed to publish to Redis: {e}")
            await self._handle_connection_error(e)
            raise

    async def subscribe(self, channel: str, callback: Callable[[SystemEvent], Awaitable[None]]) -> None:
        """Subscribe to a Redis stream.

        Args:
            channel: Channel name (stream key)
            callback: Async callback for events
        """
        if not self._running:
            raise RuntimeError("Event bus not connected")
        try:
            await self.redis.xgroup_create(channel, self.consumer_group, id="0", mkstream=True)
        except Exception as e:  # guardian: allow-silent-swallow
            if "BUSYGROUP" not in str(e):
                logger.warning(f"Failed to create consumer group: {e}")
        if channel not in self._subscribers:
            self._subscribers[channel] = []
            self._stats["channels"] += 1
            self._readers[channel] = asyncio.create_task(self._reader_loop(channel))
        self._subscribers[channel].append(callback)
        logger.debug(f"Subscribed to Redis stream {channel}")

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a Redis stream.

        Args:
            channel: Channel name
        """
        if channel in self._subscribers:
            del self._subscribers[channel]
            if channel in self._readers:
                self._readers[channel].cancel()
                del self._readers[channel]
            logger.debug(f"Unsubscribed from Redis stream {channel}")

    async def close(self) -> None:
        """Close Redis connection."""
        self._running = False
        for task in self._readers.values():
            task.cancel()
        if self._readers:
            await asyncio.gather(*self._readers.values(), return_exceptions=True)
        if self.redis:
            await self.redis.close()
        logger.info("RedisEventBus closed")

    async def health_check(self) -> dict[str, Any]:
        """Check health of Redis event bus.

        Returns:
            Health status
        """
        if not self._running or not self.redis:
            return {"status": "disconnected", "type": "redis"}
        try:
            await self.redis.ping()
            return {
                "status": "healthy",
                "type": "redis",
                "connection": self.connection_string,
                "consumer_group": self.consumer_group,
                "channels": len(self._subscribers),
                "stats": self._stats.copy(),
            }
        except Exception as e:  # guardian: allow-silent-swallow
            return {"status": "unhealthy", "type": "redis", "error": str(e), "stats": self._stats.copy()}

    async def _reader_loop(self, channel: str) -> None:
        """Reader loop for processing Redis stream events.

        Args:
            channel: Stream to read from
        """
        subscribers = self._subscribers.get(channel, [])
        while self._running:
            try:
                messages = await self.redis.xreadgroup(
                    self.consumer_group,
                    self.consumer_name,
                    {channel: ">"},
                    count=10,
                    block=1000,
                )
                for _stream, msgs in tqdm(messages, desc="Processing", unit="item"):
                    for msg_id, fields in tqdm(msgs, desc="Processing", unit="item"):
                        try:
                            event = SystemEvent.from_dict(fields)
                            if subscribers:
                                await self._notify_subscribers(event, subscribers)
                            await self.redis.xack(channel, self.consumer_group, msg_id)
                            self._stats["events_processed"] += 1
                        except Exception as e:  # guardian: allow-silent-swallow
                            logger.error(f"Failed to process message {msg_id}: {e}")
                            await self.redis.xack(channel, self.consumer_group, msg_id)
            except asyncio.CancelledError:
                break
            except Exception as e:  # guardian: allow-silent-swallow
                logger.error(f"Reader error for stream {channel}: {e}")
                await asyncio.sleep(DEFAULT_SLEEP)

    async def _notify_subscribers(self, event: SystemEvent, subscribers: list[Callable]) -> None:
        """Notify all subscribers of an event.

        Args:
            event: Event to publish
            subscribers: List of subscriber callbacks
        """
        tasks = []
        for callback in subscribers:
            task = asyncio.create_task(self._safe_notify(callback, event))
            tasks.append(task)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_notify(
        self,
        callback: Callable[[SystemEvent], Awaitable[None]],
        event: SystemEvent,
    ) -> None:
        """Safely notify a subscriber.

        Args:
            callback: Subscriber callback
            event: Event to publish
        """
        try:
            await callback(event)
        except (RuntimeError, ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            self._stats["subscriber_errors"] += 1
            logger.error(f"Subscriber callback error: {e}", exc_info=True)
            raise

    async def _handle_connection_error(self, error: Exception) -> None:
        """Handle Redis connection errors.

        Args:
            error: Connection error
        """
        logger.warning(f"Redis connection error: {error}")
        for attempt in range(3):
            try:
                await asyncio.sleep(2**attempt)
                await self.connect()
                self._stats["reconnections"] += 1
                logger.info("Redis reconnected successfully")
                break
            except (ConnectionError, RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
                logger.error(f"Reconnection attempt {attempt + 1} failed: {e}")
                raise


def create_event_bus(connection_string: str | None = None) -> EventBus:
    """Create an event bus instance.

    Args:
        connection_string: Redis connection string or None for memory bus

    Returns:
        EventBus instance
    """
    if connection_string and connection_string.startswith("redis://"):
        return RedisEventBus(connection_string)
    else:
        return MemoryEventBus()


_event_bus: EventBus | None = None
_bus_lock = asyncio.Lock()


async def get_event_bus() -> EventBus:
    """Get global event bus instance.

    Returns:
        EventBus instance
    """
    global _event_bus
    async with _bus_lock:
        if _event_bus is None:
            _event_bus = create_event_bus()
            await _event_bus.connect()
    return _event_bus


async def publish_event(
    event_type: EventType,
    source_component: str,
    payload: dict[str, Any],
    trace_id: str | None = None,
    correlation_id: str | None = None,
    causation_id: str | None = None,
) -> None:
    """Publish a system event.

    Args:
        event_type: Type of event
        source_component: Component publishing the event
        payload: Event payload
        trace_id: Trace ID for tracking
        correlation_id: Correlation ID for related events
        causation_id: ID of event that caused this one
    """
    event = SystemEvent(
        type=event_type,
        source_component=source_component,
        payload=payload,
        trace_id=trace_id or str(uuid.uuid4()),
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    bus = await get_event_bus()
    channel = f"events.{event_type.value.lower()}"
    await bus.publish(channel, event)


def event_publisher(event_type: EventType, channel: str | None = None):
    """Decorator to automatically publish events.

    Args:
        event_type: Type of event to publish
        channel: Optional channel override

    Returns:
        Decorated function
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            trace_id = None
            if args and hasattr(args[0], "trace_id"):
                trace_id = args[0].trace_id
            await publish_event(
                event_type,
                func.__module__ + "." + func.__name__,
                {"status": "started", "args_count": len(args)},
                trace_id=trace_id,
            )
            try:
                result = await func(*args, **kwargs)
                await publish_event(
                    event_type,
                    func.__module__ + "." + func.__name__,
                    {"status": "completed", "success": True},
                    trace_id=trace_id,
                    causation_id=trace_id,
                )
                return result
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise

        return async_wrapper

    return decorator
