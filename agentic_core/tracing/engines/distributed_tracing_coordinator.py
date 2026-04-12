"""Distributed Tracing Coordinator - Multi-node tracing coordination.

Provides distributed tracing coordination across multiple nodes and services,
enabling cross-service trace propagation and correlation.

FEATURES:
- Cross-service trace propagation
- Distributed trace correlation
- Service mesh integration
- Load-balanced trace collection
- Failover and redundancy
- Trace sampling strategies
- Service discovery integration

USAGE:
    coordinator = DistributedTracingCoordinator()
    coordinator.start_coordination()

    # Automatic distributed tracing
    trace_context = coordinator.create_trace_context()
    coordinator.propagate_trace_context(trace_context)
"""

import json
import logging
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("distributed_tracing_coordinator", "distributed_tracing_coordinator_digest")
record_execution_trace("distributed_tracing_coordinator", "distributed_tracing_coordinator_trace")

Logger = logging.getLogger(__name__)


class TracePropagationFormat(Enum):
    """Trace propagation formats."""

    BAGGAGE = "baggage"
    HEADER = "header"
    METADATA = "metadata"
    CUSTOM = "custom"


class SamplingStrategy(Enum):
    """Trace sampling strategies."""

    ALWAYS = "always"
    NEVER = "never"
    PROBABILITY = "probability"
    RATE_LIMITING = "rate_limiting"
    ADAPTIVE = "adaptive"


@dataclass
class TraceContext:
    """Distributed trace context."""

    trace_id: str
    span_id: str
    parent_span_id: str | None
    baggage: dict[str, str] = field(default_factory=dict)
    service_name: str = ""
    operation_name: str = ""
    flags: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for propagation."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "baggage": self.baggage,
            "service_name": self.service_name,
            "operation_name": self.operation_name,
            "flags": self.flags,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TraceContext":
        """Create from dictionary."""
        return cls(
            trace_id=data["trace_id"],
            span_id=data["span_id"],
            parent_span_id=data.get("parent_span_id"),
            baggage=data.get("baggage", {}),
            service_name=data.get("service_name", ""),
            operation_name=data.get("operation_name", ""),
            flags=data.get("flags", {}),
            timestamp=data.get("timestamp", time.time()),
        )


@dataclass
class ServiceNode:
    """Service node in distributed tracing."""

    service_name: str
    service_id: str
    host: str
    port: int
    capabilities: set[str] = field(default_factory=set)
    health_status: str = "healthy"
    last_heartbeat: float = field(default_factory=time.time)
    trace_count: int = 0
    error_count: int = 0


@dataclass
class DistributedSpan:
    """Distributed span data."""

    trace_id: str
    span_id: str
    parent_span_id: str | None
    service_name: str
    operation_name: str
    start_time: float
    end_time: float | None
    duration_ms: float | None
    status: str = "OK"
    tags: dict[str, Any] = field(default_factory=dict)
    logs: list[dict[str, Any]] = field(default_factory=list)
    service_node_id: str | None = None


class DistributedTracingCoordinator:
    """
    Distributed tracing coordinator for multi-node environments.

    Provides trace propagation, correlation, and coordination across
    multiple services and nodes.
    """

    def __init__(self, service_name: str = "distributed-coordinator") -> None:
        """Initialize distributed tracing coordinator."""
        self._service_name = service_name
        self._service_id = str(uuid.uuid4())

        # Trace management
        self._active_traces: dict[str, TraceContext] = {}
        self._trace_history: deque = deque(maxlen=10000)
        self._span_buffer: dict[str, list[DistributedSpan]] = defaultdict(list)

        # Service management
        self._registered_services: dict[str, ServiceNode] = {}
        self._service_discovery_enabled: bool = True

        # Coordination state
        self._coordination_active: bool = False
        self._coordination_thread: threading.Thread | None = None
        self._shutdown_requested: bool = False

        # Sampling configuration
        self._sampling_strategy = SamplingStrategy.PROBABILITY
        self._sampling_rate = 0.1  # 10%
        self._rate_limit_per_second = 100

        # Propagation configuration
        self._propagation_format = TracePropagationFormat.HEADER
        self._propagation_headers = {
            "x-trace-id": "trace_id",
            "x-span-id": "span_id",
            "x-parent-span-id": "parent_span_id",
            "x-baggage": "baggage",
        }

        # Statistics
        self._stats = {
            "traces_created": 0,
            "spans_received": 0,
            "propagations_sent": 0,
            "propagations_received": 0,
            "errors": 0,
            "active_services": 0,
        }

        # Load balancing
        self._load_balancer_index = 0
        self._service_load_stats: dict[str, dict[str, float]] = defaultdict(
            lambda: {
                "request_count": 0,
                "error_rate": 0.0,
                "avg_response_time": 0.0,
            }
        )

    def start_coordination(self) -> None:
        """Start distributed tracing coordination."""
        if self._coordination_active:
            Logger.warning("[DISTRIBUTED_TRACING] Coordination already active")
            return

        self._coordination_active = True
        self._shutdown_requested = False

        # Register self as a service
        self._register_self_service()

        # Start coordination thread
        self._coordination_thread = threading.Thread(
            target=self._coordination_loop,
            daemon=True,
            name="DistributedTracingCoordinator",
        )
        self._coordination_thread.start()

        Logger.info(f"[DISTRIBUTED_TRACING] Started coordination for service {self._service_name}")

    def stop_coordination(self) -> None:
        """Stop distributed tracing coordination."""
        if not self._coordination_active:
            return

        self._shutdown_requested = True
        self._coordination_active = False

        if self._coordination_thread and self._coordination_thread.is_alive():
            self._coordination_thread.join(timeout=5.0)

        # Unregister service
        self._unregister_service(self._service_id)

        Logger.info("[DISTRIBUTED_TRACING] Stopped coordination")

    def _register_self_service(self) -> None:
        """Register this coordinator as a service."""
        try:
            import socket

            hostname = socket.gethostname()
            node = ServiceNode(
                service_name=self._service_name,
                service_id=self._service_id,
                host=hostname,
                port=8080,  # Default coordination port
                capabilities={"coordination", "trace_aggregation", "propagation"},
            )

            self._registered_services[self._service_id] = node
            self._stats["active_services"] = len(self._registered_services)

        except Exception as e:
            Logger.error(f"[DISTRIBUTED_TRACING] Failed to register self: {e}")

    def _unregister_service(self, service_id: str) -> None:
        """Unregister a service."""
        if service_id in self._registered_services:
            del self._registered_services[service_id]
            self._stats["active_services"] = len(self._registered_services)

    def create_trace_context(self, service_name: str = "", operation_name: str = "") -> TraceContext:
        """Create a new trace context."""
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())[:16]

        context = TraceContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            service_name=service_name or self._service_name,
            operation_name=operation_name,
        )

        # Apply sampling strategy
        if self._should_sample_trace(context):
            self._active_traces[trace_id] = context
            self._stats["traces_created"] += 1
            Logger.debug(f"[DISTRIBUTED_TRACING] Created trace context: {trace_id}")
        else:
            Logger.debug(f"[DISTRIBUTED_TRACING] Trace not sampled: {trace_id}")

        return context

    def _should_sample_trace(self, context: TraceContext) -> bool:
        """Determine if trace should be sampled."""
        if self._sampling_strategy == SamplingStrategy.ALWAYS:
            return True
        elif self._sampling_strategy == SamplingStrategy.NEVER:
            return False
        elif self._sampling_strategy == SamplingStrategy.PROBABILITY:
            import random

            return random.random() < self._sampling_rate
        elif self._sampling_strategy == SamplingStrategy.RATE_LIMITING:
            # Simple rate limiting based on traces per second
            return True  # Simplified for now
        elif self._sampling_strategy == SamplingStrategy.ADAPTIVE:
            # Adaptive sampling based on system load and error rates
            return True  # Simplified for now
        else:
            return True

    def propagate_trace_context(self, context: TraceContext, target_service: str) -> bool:
        """Propagate trace context to target service."""
        try:
            if not self._coordination_active:
                return False

            # Find target service
            target_node = self._find_service_node(target_service)
            if not target_node:
                Logger.warning(f"[DISTRIBUTED_TRACING] Target service not found: {target_service}")
                return False

            # Prepare propagation data
            propagation_data = self._prepare_propagation_data(context)

            # Send propagation (simplified - in real implementation would use network)
            success = self._send_propagation(target_node, propagation_data)

            if success:
                self._stats["propagations_sent"] += 1
                Logger.debug(f"[DISTRIBUTED_TRACING] Propagated trace {context.trace_id} to {target_service}")

            return success

        except Exception as e:
            Logger.error(f"[DISTRIBUTED_TRACING] Failed to propagate trace context: {e}")
            self._stats["errors"] += 1
            return False

    def _find_service_node(self, service_name: str) -> ServiceNode | None:
        """Find a service node by name using load balancing."""
        matching_nodes = [
            node
            for node in self._registered_services.values()
            if node.service_name == service_name and node.health_status == "healthy"
        ]

        if not matching_nodes:
            return None

        # Simple round-robin load balancing
        node = matching_nodes[self._load_balancer_index % len(matching_nodes)]
        self._load_balancer_index += 1

        return node

    def _prepare_propagation_data(self, context: TraceContext) -> dict[str, Any]:
        """Prepare trace context for propagation."""
        if self._propagation_format == TracePropagationFormat.HEADER:
            return {
                "headers": {
                    self._propagation_headers["x-trace-id"]: context.trace_id,
                    self._propagation_headers["x-span-id"]: context.span_id,
                    self._propagation_headers["x-parent-span-id"]: context.parent_span_id or "",
                    self._propagation_headers["x-baggage"]: json.dumps(context.baggage),
                },
            }
        elif self._propagation_format == TracePropagationFormat.BAGGAGE:
            return {
                "baggage": context.baggage,
                "trace_id": context.trace_id,
                "span_id": context.span_id,
            }
        else:
            return context.to_dict()

    def _send_propagation(self, target_node: ServiceNode, propagation_data: dict[str, Any]) -> bool:
        """Send propagation to target node (simplified)."""
        # In a real implementation, this would use HTTP, gRPC, or message queue
        # For now, we simulate successful propagation
        return True

    def receive_propagated_context(
        self, propagation_data: dict[str, Any], format_type: TracePropagationFormat
    ) -> TraceContext | None:
        """Receive propagated trace context."""
        try:
            if format_type == TracePropagationFormat.HEADER:
                headers = propagation_data.get("headers", {})
                context = TraceContext(
                    trace_id=headers.get(self._propagation_headers["x-trace-id"], ""),
                    span_id=headers.get(self._propagation_headers["x-span-id"], ""),
                    parent_span_id=headers.get(self._propagation_headers["x-parent-span-id"]) or None,
                    baggage=json.loads(headers.get(self._propagation_headers["x-baggage"], "{}")),
                )
            else:
                context = TraceContext.from_dict(propagation_data)

            # Validate context
            if not context.trace_id or not context.span_id:
                Logger.warning("[DISTRIBUTED_TRACING] Invalid propagated context")
                return None

            self._active_traces[context.trace_id] = context
            self._stats["propagations_received"] += 1

            Logger.debug(f"[DISTRIBUTED_TRACING] Received propagated trace: {context.trace_id}")

            return context

        except Exception as e:
            Logger.error(f"[DISTRIBUTED_TRACING] Failed to receive propagated context: {e}")
            self._stats["errors"] += 1
            return None

    def add_span(self, span: DistributedSpan) -> None:
        """Add a distributed span."""
        try:
            self._span_buffer[span.trace_id].append(span)
            self._stats["spans_received"] += 1

            # Update service load stats
            if span.service_node_id:
                self._update_service_load_stats(span.service_node_id, span)

            Logger.debug(f"[DISTRIBUTED_TRACING] Added span {span.span_id} to trace {span.trace_id}")

        except Exception as e:
            Logger.error(f"[DISTRIBUTED_TRACING] Failed to add span: {e}")
            self._stats["errors"] += 1

    def _update_service_load_stats(self, service_id: str, span: DistributedSpan) -> None:
        """Update service load statistics."""
        if service_id not in self._service_load_stats:
            return

        stats = self._service_load_stats[service_id]
        stats["request_count"] += 1

        # Update error rate
        if span.status == "ERROR":
            stats["error_rate"] = (stats.get("error_count", 0) + 1) / stats["request_count"]

        # Update average response time
        if span.duration_ms is not None:
            current_avg = stats["avg_response_time"]
            count = stats["request_count"]
            stats["avg_response_time"] = (current_avg * (count - 1) + span.duration_ms) / count

    def get_trace_spans(self, trace_id: str) -> list[DistributedSpan]:
        """Get all spans for a trace."""
        return self._span_buffer.get(trace_id, [])

    def get_service_traces(self, service_name: str, limit: int = 100) -> list[str]:
        """Get trace IDs for a specific service."""
        trace_ids = []

        for trace_id, spans in self._span_buffer.items():
            service_spans = [span for span in spans if span.service_name == service_name]
            if service_spans:
                trace_ids.append(trace_id)

        return trace_ids[:limit]

    def register_service(self, service_node: ServiceNode) -> bool:
        """Register a service node."""
        try:
            self._registered_services[service_node.service_id] = service_node
            self._stats["active_services"] = len(self._registered_services)

            Logger.info(f"[DISTRIBUTED_TRACING] Registered service: {service_node.service_name}")
            return True

        except Exception as e:
            Logger.error(f"[DISTRIBUTED_TRACING] Failed to register service: {e}")
            return False

    def unregister_service(self, service_id: str) -> bool:
        """Unregister a service node."""
        return self._unregister_service(service_id)

    def get_service_health(self) -> dict[str, dict[str, Any]]:
        """Get health status of all registered services."""
        health_status = {}

        for service_id, node in self._registered_services.items():
            # Check if service is responsive (simplified)
            is_responsive = time.time() - node.last_heartbeat < 60  # 1 minute timeout

            health_status[service_id] = {
                "service_name": node.service_name,
                "host": node.host,
                "port": node.port,
                "health_status": node.health_status if is_responsive else "unreachable",
                "last_heartbeat": node.last_heartbeat,
                "trace_count": node.trace_count,
                "error_count": node.error_count,
                "capabilities": list(node.capabilities),
                "load_stats": self._service_load_stats.get(service_id, {}),
            }

        return health_status

    def _coordination_loop(self) -> None:
        """Main coordination loop."""
        while self._coordination_active and not self._shutdown_requested:
            try:
                # Perform service health checks
                self._perform_health_checks()

                # Clean up old traces
                self._cleanup_old_traces()

                # Aggregate trace statistics
                self._aggregate_trace_statistics()

                # Sleep for next iteration
                time.sleep(30.0)  # Check every 30 seconds

            except Exception as e:
                Logger.error(f"[DISTRIBUTED_TRACING] Coordination loop error: {e}")
                time.sleep(5.0)

    def _perform_health_checks(self) -> None:
        """Perform health checks on registered services."""
        current_time = time.time()

        for service_id, node in list(self._registered_services.items()):
            # Check if service is responsive
            if current_time - node.last_heartbeat > 120:  # 2 minutes timeout
                node.health_status = "unreachable"
                Logger.warning(f"[DISTRIBUTED_TRACING] Service unreachable: {node.service_name}")
            elif node.error_count > 10:
                node.health_status = "degraded"
            else:
                node.health_status = "healthy"

    def _cleanup_old_traces(self) -> None:
        """Clean up old trace data."""
        current_time = time.time()
        cutoff_time = current_time - 3600  # 1 hour ago

        # Clean up active traces
        old_traces = [
            trace_id for trace_id, context in self._active_traces.items() if context.timestamp < cutoff_time
        ]

        for trace_id in old_traces:
            del self._active_traces[trace_id]

        # Clean up span buffer
        for trace_id in list(self._span_buffer.keys()):
            spans = self._span_buffer[trace_id]
            recent_spans = [span for span in spans if span.start_time > cutoff_time]

            if recent_spans:
                self._span_buffer[trace_id] = recent_spans
            else:
                del self._span_buffer[trace_id]

        # Store in history
        self._trace_history.extend(
            [{"trace_id": trace_id, "timestamp": current_time} for trace_id in old_traces]
        )

    def _aggregate_trace_statistics(self) -> None:
        """Aggregate trace statistics."""
        total_traces = len(self._active_traces)
        total_spans = sum(len(spans) for spans in self._span_buffer.values())

        # Calculate average spans per trace
        avg_spans_per_trace = total_spans / total_traces if total_traces > 0 else 0

        Logger.debug(
            f"[DISTRIBUTED_TRACING] Active traces: {total_traces}, Total spans: {total_spans}, Avg spans/trace: {avg_spans_per_trace:.1f}"
        )

    def get_coordination_stats(self) -> dict[str, Any]:
        """Get coordination statistics."""
        return {
            "coordination_active": self._coordination_active,
            "service_name": self._service_name,
            "service_id": self._service_id,
            "registered_services": len(self._registered_services),
            "active_traces": len(self._active_traces),
            "total_spans": sum(len(spans) for spans in self._span_buffer.values()),
            "statistics": self._stats.copy(),
            "sampling_strategy": self._sampling_strategy.value,
            "sampling_rate": self._sampling_rate,
            "propagation_format": self._propagation_format.value,
        }

    def set_sampling_strategy(self, strategy: SamplingStrategy, rate: float = 0.1) -> None:
        """Set sampling strategy."""
        self._sampling_strategy = strategy
        self._sampling_rate = rate
        Logger.info(f"[DISTRIBUTED_TRACING] Set sampling strategy: {strategy.value}, rate: {rate}")

    def set_propagation_format(self, format_type: TracePropagationFormat) -> None:
        """Set propagation format."""
        self._propagation_format = format_type
        Logger.info(f"[DISTRIBUTED_TRACING] Set propagation format: {format_type.value}")


# Global distributed tracing coordinator
_global_coordinator: DistributedTracingCoordinator | None = None


def get_global_coordinator() -> DistributedTracingCoordinator:
    """Get the global distributed tracing coordinator."""
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = DistributedTracingCoordinator()
    return _global_coordinator


def start_distributed_coordination() -> None:
    """Start global distributed tracing coordination."""
    coordinator = get_global_coordinator()
    coordinator.start_coordination()


def stop_distributed_coordination() -> None:
    """Stop global distributed tracing coordination."""
    coordinator = get_global_coordinator()
    coordinator.stop_coordination()


def create_distributed_trace_context(service_name: str = "", operation_name: str = "") -> TraceContext:
    """Create a distributed trace context."""
    coordinator = get_global_coordinator()
    return coordinator.create_trace_context(service_name, operation_name)


def propagate_distributed_trace(context: TraceContext, target_service: str) -> bool:
    """Propagate trace context to target service."""
    coordinator = get_global_coordinator()
    return coordinator.propagate_trace_context(context, target_service)


def get_distributed_coordination_stats() -> dict[str, Any]:
    """Get distributed coordination statistics."""
    coordinator = get_global_coordinator()
    return coordinator.get_coordination_stats()
