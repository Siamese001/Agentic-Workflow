"""Performance Optimized Span Collector - High-performance tracing collection.

Optimized span collector with advanced performance features including
batching, compression, intelligent scheduling, and resource management.

FEATURES:
- Intelligent batch processing and compression
- Adaptive scheduling based on system load
- Memory-efficient span buffering
- Performance monitoring and auto-tuning
- Resource-aware collection strategies
- High-throughput processing

USAGE:
    collector = PerformanceOptimizedCollector()
    collector.start_collection()

    # High-performance automatic collection
    stats = collector.get_performance_stats()
"""

import gzip
import json
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any

import psutil

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from tqdm import tqdm

emit_determinism_digest("performance_optimized_collector", "performance_optimized_collector_digest")
record_execution_trace("performance_optimized_collector", "performance_optimized_collector_trace")

Logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for the collector."""

    spans_processed: int = 0
    spans_per_second: float = 0.0
    avg_processing_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    buffer_utilization: float = 0.0
    batch_efficiency: float = 0.0
    compression_ratio: float = 0.0


@dataclass
class CollectionConfig:
    """Configuration for performance optimization."""

    batch_size: int = 100
    max_buffer_size: int = 10000
    flush_interval_seconds: float = 30.0
    compression_enabled: bool = True
    adaptive_scheduling: bool = True
    memory_threshold_mb: float = 500.0
    cpu_threshold_percent: float = 80.0
    max_processing_threads: int = 4


class PerformanceOptimizedCollector:
    """
    High-performance span collector with advanced optimization features.

    Provides intelligent batching, compression, adaptive scheduling,
    and resource-aware collection strategies.
    """

    def __init__(self, config: CollectionConfig | None = None) -> None:
        """
        Initialize performance optimized collector.

        Args:
            config: Collection configuration (optional)
        """
        self._config = config or CollectionConfig()

        # High-performance buffers
        self._span_buffer: deque = deque(maxlen=self._config.max_buffer_size)
        self._batch_queue: Queue = Queue(maxsize=self._config.batch_size * 2)
        self._compression_buffer: list[bytes] = []

        # Processing threads
        self._processing_threads: list[threading.Thread] = []
        self._collection_thread: threading.Thread | None = None
        self._flush_thread: threading.Thread | None = None

        # Performance monitoring
        self._performance_metrics = PerformanceMetrics()
        self._processing_times: list[float] = []
        self._last_performance_check = time.monotonic()

        # Collection state
        self._collection_active: bool = False
        self._shutdown_requested: bool = False
        self._registered_agents: dict[str, Any] = {}

        # Adaptive scheduling
        self._adaptive_interval = self._config.flush_interval_seconds
        self._system_load_history: list[dict[str, float]] = []

        # Runtime ADG integration
        self._runtime_adg_enabled: bool = False
        self._otel_tracer = None

        self._initialize_runtime_adg_integration()

    def _initialize_runtime_adg_integration(self) -> None:
        """Initialize Runtime ADG integration with performance optimizations."""
        try:
            from system_learning.runtime_adg.auto_persistence import (
                get_auto_persistence_tracer,
            )

            self._otel_tracer = get_auto_persistence_tracer(
                service_name="performance-optimized-collector",
                enable_auto_persistence=True,
            )
            self._runtime_adg_enabled = True

            Logger.info("[PERF_COLLECTOR] Runtime ADG integration enabled")

        except ImportError:
            Logger.debug("[PERF_COLLECTOR] Runtime ADG not available")
            self._runtime_adg_enabled = False
        except (AttributeError, RuntimeError, OSError) as e:
            Logger.error(f"[PERF_COLLECTOR] Failed to initialize Runtime ADG: {e}")
            self._runtime_adg_enabled = False

    def start_collection(self) -> None:
        """Start high-performance collection with multiple threads."""
        if self._collection_active:
            Logger.warning("[PERF_COLLECTOR] Collection already active")
            return

        self._collection_active = True
        self._shutdown_requested = False

        # Start processing threads
        for i in range(self._config.max_processing_threads):
            thread = threading.Thread(
                target=self._processing_loop,
                daemon=True,
                name=f"SpanProcessor-{i}",
            )
            thread.start()
            self._processing_threads.append(thread)

        # Start collection thread
        self._collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True,
            name="SpanCollector",
        )
        self._collection_thread.start()

        # Start flush thread
        self._flush_thread = threading.Thread(
            target=self._flush_loop,
            daemon=True,
            name="SpanFlusher",
        )
        self._flush_thread.start()

        Logger.info(
            f"[PERF_COLLECTOR] Started optimized collection with {self._config.max_processing_threads} processing threads"
        )

    def stop_collection(self) -> None:
        """Stop collection gracefully."""
        if not self._collection_active:
            return

        self._shutdown_requested = True
        self._collection_active = False

        # Wait for threads to finish
        if self._collection_thread and self._collection_thread.is_alive():
            self._collection_thread.join(timeout=5.0)

        if self._flush_thread and self._flush_thread.is_alive():
            self._flush_thread.join(timeout=5.0)

        for thread in self._processing_threads:
            if thread.is_alive():
                thread.join(timeout=2.0)

        # Final flush
        self._flush_all_spans()

        Logger.info("[PERF_COLLECTOR] Stopped optimized collection")

    def register_agent(self, agent_id: str, agent_instance: Any) -> None:
        """
        Register an agent for optimized collection.

        Args:
            agent_id: Unique identifier for the agent
            agent_instance: Agent instance
        """
        if agent_id in self._registered_agents:
            Logger.warning(f"[PERF_COLLECTOR] Agent {agent_id} already registered")
            return

        self._registered_agents[agent_id] = agent_instance

        # Enable performance optimizations on agent
        if hasattr(agent_instance, "_performance_optimized"):
            agent_instance._performance_optimized = True

        Logger.info(f"[PERF_COLLECTOR] Registered agent {agent_id}")

    def collect_spans_from_agent(self, agent_id: str, spans: list[dict[str, Any]]) -> None:
        """
        Collect spans from agent with performance optimization.

        Args:
            agent_id: Agent identifier
            spans: List of span dictionaries
        """
        if not self._collection_active or not spans:
            return

        # Optimize spans before queuing
        optimized_spans = self._optimize_spans(spans)

        # Add to batch queue for processing
        for span in optimized_spans:
            try:
                self._batch_queue.put_nowait(span)
                self._performance_metrics.spans_processed += 1
            except Exception:  # guardian: allow-silent-swallow -- queue full: drop spans to prevent memory exhaustion, non-fatal
                # Queue full, drop spans to prevent memory issues
                Logger.warning("[PERF_COLLECTOR] Batch queue full, dropping spans")
                break

    def _optimize_spans(self, spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Optimize spans for efficient processing."""
        optimized = []

        for span in tqdm(spans, desc="Processing", unit="item"):
            # Remove unnecessary fields
            optimized_span = {
                "trace_id": span.get("trace_id"),
                "span_id": span.get("span_id"),
                "parent_span_id": span.get("parent_span_id"),
                "service_name": span.get("service_name"),
                "operation_name": span.get("operation_name"),
                "start_time": span.get("start_time"),
                "end_time": span.get("end_time"),
                "duration_ms": span.get("duration_ms"),
                "status": span.get("status", "OK"),
            }

            # Keep only essential attributes
            attributes = span.get("attributes", {})
            if attributes:
                # Filter attributes to keep only important ones
                filtered_attrs = {
                    k: v
                    for k, v in attributes.items()
                    if k in ["error", "error_type", "component", "layer", "mission"]
                }
                if filtered_attrs:
                    optimized_span["attributes"] = filtered_attrs

            optimized.append(optimized_span)

        return optimized

    def _collection_loop(self) -> None:
        """Main collection loop with adaptive scheduling."""
        while self._collection_active and not self._shutdown_requested:
            try:
                start_time = time.monotonic()

                # Collect from registered agents
                self._collect_from_registered_agents()

                # Update performance metrics
                self._update_performance_metrics()

                # Adaptive scheduling
                if self._config.adaptive_scheduling:
                    self._adaptive_scheduling()

                # Sleep for adaptive interval
                elapsed = time.monotonic() - start_time
                sleep_time = max(0.1, self._adaptive_interval - elapsed)
                time.sleep(sleep_time)

            except (
                OSError,
                RuntimeError,
                AttributeError,
            ) as e:  # guardian: allow-broad-exception -- background worker loop must not die
                Logger.error(f"[PERF_COLLECTOR] Collection loop error: {e}")
                time.sleep(1.0)

    def _collect_from_registered_agents(self) -> None:
        """Collect spans from all registered agents."""
        for agent_id, agent_instance in self._registered_agents.items():
            try:
                if hasattr(agent_instance, "flush_traces"):
                    spans = agent_instance.flush_traces()
                    if spans:
                        self.collect_spans_from_agent(agent_id, spans)
            except (
                AttributeError,
                RuntimeError,
            ) as e:  # guardian: allow-log-and-swallow -- collection loop: agent unavailable at flush time; non-fatal
                Logger.error(f"[PERF_COLLECTOR] Failed to collect from {agent_id}: {e}")

    def _processing_loop(self) -> None:
        """Processing loop for batch operations."""
        batch = []

        while self._collection_active and not self._shutdown_requested:
            try:
                # Collect spans from batch queue
                while len(batch) < self._config.batch_size:
                    try:
                        span = self._batch_queue.get_nowait()
                        batch.append(span)
                        self._batch_queue.task_done()
                    except Empty:
                        break

                if batch:
                    start_time = time.monotonic()

                    # Process batch
                    self._process_batch(batch)

                    # Record processing time
                    processing_time = (time.monotonic() - start_time) * 1000
                    self._processing_times.append(processing_time)

                    # Keep only recent processing times
                    if len(self._processing_times) > 1000:
                        self._processing_times = self._processing_times[-1000:]

                    batch.clear()
                else:
                    time.sleep(0.1)

            except (
                OSError,
                RuntimeError,
                AttributeError,
            ) as e:  # guardian: allow-broad-exception -- background worker loop must not die
                Logger.error(f"[PERF_COLLECTOR] Processing loop error: {e}")
                batch.clear()
                time.sleep(1.0)

    def _process_batch(self, batch: list[dict[str, Any]]) -> None:
        """Process a batch of spans efficiently."""
        try:
            # Add to buffer
            self._span_buffer.extend(batch)

            # Check if buffer needs compression
            if len(self._span_buffer) >= self._config.batch_size:
                self._compress_buffer()

        except (
            OSError,
            ValueError,
            RuntimeError,
        ) as e:  # guardian: allow-log-and-swallow -- batch processing: failure logged, loop continues
            Logger.error(f"[PERF_COLLECTOR] Batch processing error: {e}")

    def _compress_buffer(self) -> None:
        """Compress buffer for efficient storage."""
        if not self._config.compression_enabled:
            return

        try:
            # Extract spans for compression
            spans_to_compress = []
            while len(spans_to_compress) < self._config.batch_size and self._span_buffer:
                spans_to_compress.append(self._span_buffer.popleft())

            if spans_to_compress:
                # Compress spans
                json_data = json.dumps(spans_to_compress)
                compressed_data = gzip.compress(json_data.encode())

                # Calculate compression ratio
                original_size = len(json_data.encode())
                compressed_size = len(compressed_data)
                compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0

                self._performance_metrics.compression_ratio = compression_ratio

                # Store compressed data
                self._compression_buffer.append(compressed_data)

                Logger.debug(
                    f"[PERF_COLLECTOR] Compressed {len(spans_to_compress)} spans, ratio: {compression_ratio:.2f}"
                )

        except (
            OSError,
            RuntimeError,
        ) as e:  # guardian: allow-log-and-swallow -- compression: non-fatal, buffer continues uncompressed
            Logger.error(f"[PERF_COLLECTOR] Compression error: {e}")

    def _flush_loop(self) -> None:
        """Flush loop with adaptive scheduling."""
        while self._collection_active and not self._shutdown_requested:
            try:
                start_time = time.monotonic()

                # Flush spans
                self._flush_all_spans()

                # Update flush interval based on performance
                if self._config.adaptive_scheduling:
                    self._update_flush_interval()

                # Sleep for adaptive interval
                elapsed = time.monotonic() - start_time
                sleep_time = max(1.0, self._adaptive_interval - elapsed)
                time.sleep(sleep_time)

            except (
                OSError,
                RuntimeError,
                AttributeError,
            ) as e:  # guardian: allow-broad-exception -- background worker loop must not die
                Logger.error(f"[PERF_COLLECTOR] Flush loop error: {e}")
                time.sleep(5.0)

    def _flush_all_spans(self) -> None:
        """Flush all spans to Runtime ADG efficiently."""
        spans_flushed = 0

        try:
            # Flush uncompressed spans
            if self._span_buffer:
                spans = list(self._span_buffer)
                self._span_buffer.clear()

                if self._runtime_adg_enabled and self._otel_tracer:
                    # Create Runtime ADG spans
                    for span in spans:
                        self._create_runtime_adg_span(span)

                    # Force persistence
                    result = self._otel_tracer.force_persist_current_spans("perf-collector-flush")
                    spans_flushed += len(spans)

            # Flush compressed spans
            if self._compression_buffer:
                for compressed_data in self._compression_buffer:
                    # Decompress and process
                    json_data = gzip.decompress(compressed_data).decode()
                    spans = json.loads(json_data)

                    if self._runtime_adg_enabled and self._otel_tracer:
                        for span in spans:
                            self._create_runtime_adg_span(span)

                    spans_flushed += len(spans)

                self._compression_buffer.clear()

            if spans_flushed > 0:
                Logger.info(f"[PERF_COLLECTOR] Flushed {spans_flushed} spans to Runtime ADG")

        except (
            OSError,
            RuntimeError,
        ) as e:  # guardian: allow-log-and-swallow -- flush loop: failure logged, loop continues on next interval
            Logger.error(f"[PERF_COLLECTOR] Flush error: {e}")

    def _create_runtime_adg_span(self, span: dict[str, Any]) -> None:
        """Create Runtime ADG span from optimized span data."""
        try:
            operation_name = span.get("operation_name", "collected_span")
            attributes = span.get("attributes", {})

            # Add performance metadata
            attributes.update(
                {
                    "performance_collected": True,
                    "collection_timestamp": time.time(),
                    "optimized": True,
                }
            )

            # Create appropriate OpenTelemetry span
            if "cognitive" in operation_name.lower():
                reasoning_mode = attributes.get("reasoning_mode", "react")
                span_context = self._otel_tracer.trace_cognitive(
                    operation_name, reasoning_mode=reasoning_mode, metadata=attributes
                )
            elif "tool" in operation_name.lower():
                tool_name = attributes.get("tool_name", operation_name)
                span_context = self._otel_tracer.trace_tool(tool_name, attributes)
            elif "action" in operation_name.lower():
                action_count = attributes.get("action_count", 1)
                span_context = self._otel_tracer.trace_action(action_count=action_count, metadata=attributes)
            else:
                span_context = self._otel_tracer.trace_orchestrator(operation_name, metadata=attributes)

            # Enter and exit the span context
            with span_context:
                pass  # Span is created and automatically closed

        except (
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-log-and-swallow -- span creation: fire-and-forget observability, non-fatal
            Logger.debug(f"[PERF_COLLECTOR] Failed to create Runtime ADG span: {e}")

    def _update_performance_metrics(self) -> None:
        """Update performance metrics."""
        current_time = time.monotonic()

        # Calculate spans per second
        if current_time - self._last_performance_check > 1.0:
            time_diff = current_time - self._last_performance_check
            self._performance_metrics.spans_per_second = self._performance_metrics.spans_processed / time_diff
            self._performance_metrics.spans_processed = 0
            self._last_performance_check = current_time

        # Calculate average processing time
        if self._processing_times:
            self._performance_metrics.avg_processing_time_ms = sum(self._processing_times) / len(
                self._processing_times
            )

        # Get system metrics
        try:
            process = psutil.Process()
            self._performance_metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            self._performance_metrics.cpu_usage_percent = process.cpu_percent()
        except (
            OSError,
            RuntimeError,
            AttributeError,
        ) as e:  # guardian: allow-log-and-swallow -- psutil metrics: non-fatal, counters degrade gracefully
            import logging

            logging.getLogger(__name__).debug(
                "performance_optimized_collector: Exception swallowed at L513: %s", e
            )

        # Calculate buffer utilization
        self._performance_metrics.buffer_utilization = len(self._span_buffer) / self._config.max_buffer_size

        # Calculate batch efficiency
        if self._config.batch_size > 0:
            self._performance_metrics.batch_efficiency = (
                len(self._span_buffer) + len(self._compression_buffer) * self._config.batch_size
            ) / self._config.batch_size

    def _adaptive_scheduling(self) -> None:
        """Adapt scheduling based on system load."""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent

            # Store in history
            self._system_load_history.append(
                {
                    "cpu": cpu_percent,
                    "memory": memory_percent,
                    "timestamp": time.time(),
                }
            )

            # Keep only recent history
            if len(self._system_load_history) > 100:
                self._system_load_history = self._system_load_history[-100:]

            # Adjust collection frequency based on load
            if cpu_percent > self._config.cpu_threshold_percent or memory_percent > 80:
                # High load - reduce collection frequency
                self._adaptive_interval = min(60.0, self._adaptive_interval * 1.5)
            elif cpu_percent < 50 and memory_percent < 50:
                # Low load - increase collection frequency
                self._adaptive_interval = max(5.0, self._adaptive_interval * 0.8)

        except (
            OSError,
            RuntimeError,
            AttributeError,
        ) as e:  # guardian: allow-log-and-swallow -- adaptive scheduler: non-fatal, uses previous interval
            Logger.debug(f"[PERF_COLLECTOR] Adaptive scheduling error: {e}")

    def _update_flush_interval(self) -> None:
        """Update flush interval based on performance."""
        # Adjust flush interval based on processing time
        if self._performance_metrics.avg_processing_time_ms > 100:
            # Slow processing - increase flush interval
            self._adaptive_interval = min(60.0, self._adaptive_interval * 1.2)
        elif self._performance_metrics.avg_processing_time_ms < 50:
            # Fast processing - decrease flush interval
            self._adaptive_interval = max(10.0, self._adaptive_interval * 0.9)

    def get_performance_stats(self) -> dict[str, Any]:
        """Get comprehensive performance statistics."""
        self._update_performance_metrics()

        return {
            "collection_active": self._collection_active,
            "registered_agents": len(self._registered_agents),
            "performance_metrics": {
                "spans_per_second": self._performance_metrics.spans_per_second,
                "avg_processing_time_ms": self._performance_metrics.avg_processing_time_ms,
                "memory_usage_mb": self._performance_metrics.memory_usage_mb,
                "cpu_usage_percent": self._performance_metrics.cpu_usage_percent,
                "buffer_utilization": self._performance_metrics.buffer_utilization,
                "batch_efficiency": self._performance_metrics.batch_efficiency,
                "compression_ratio": self._performance_metrics.compression_ratio,
            },
            "configuration": {
                "batch_size": self._config.batch_size,
                "max_buffer_size": self._config.max_buffer_size,
                "flush_interval": self._adaptive_interval,
                "compression_enabled": self._config.compression_enabled,
                "adaptive_scheduling": self._config.adaptive_scheduling,
            },
            "runtime_adg_enabled": self._runtime_adg_enabled,
            "system_load": self._system_load_history[-5:] if self._system_load_history else [],
        }

    def get_optimization_recommendations(self) -> list[dict[str, Any]]:
        """Get performance optimization recommendations."""
        recommendations = []

        metrics = self._performance_metrics

        # Memory recommendations
        if metrics.memory_usage_mb > self._config.memory_threshold_mb:
            recommendations.append(
                {
                    "type": "memory",
                    "priority": "high",
                    "description": f"High memory usage: {metrics.memory_usage_mb:.1f} MB",
                    "actions": [
                        "Increase buffer size limits",
                        "Enable more aggressive compression",
                        "Reduce batch size",
                    ],
                }
            )

        # CPU recommendations
        if metrics.cpu_usage_percent > self._config.cpu_threshold_percent:
            recommendations.append(
                {
                    "type": "cpu",
                    "priority": "high",
                    "description": f"High CPU usage: {metrics.cpu_usage_percent:.1f}%",
                    "actions": [
                        "Reduce processing threads",
                        "Increase flush interval",
                        "Enable adaptive scheduling",
                    ],
                }
            )

        # Buffer recommendations
        if metrics.buffer_utilization > 0.8:
            recommendations.append(
                {
                    "type": "buffer",
                    "priority": "medium",
                    "description": f"High buffer utilization: {metrics.buffer_utilization:.1%}",
                    "actions": [
                        "Increase buffer size",
                        "Reduce collection frequency",
                        "Enable compression",
                    ],
                }
            )

        # Processing time recommendations
        if metrics.avg_processing_time_ms > 100:
            recommendations.append(
                {
                    "type": "processing",
                    "priority": "medium",
                    "description": f"Slow processing: {metrics.avg_processing_time_ms:.1f} ms",
                    "actions": [
                        "Optimize span processing",
                        "Reduce batch size",
                        "Enable compression",
                    ],
                }
            )

        return recommendations


# Global optimized collector instance
_global_optimized_collector: PerformanceOptimizedCollector | None = None


def get_global_optimized_collector() -> PerformanceOptimizedCollector:
    """Get the global performance optimized collector instance."""
    global _global_optimized_collector
    if _global_optimized_collector is None:
        _global_optimized_collector = PerformanceOptimizedCollector()
    return _global_optimized_collector


def start_optimized_collection() -> None:
    """Start global optimized collection."""
    collector = get_global_optimized_collector()
    collector.start_collection()


def stop_optimized_collection() -> None:
    """Stop global optimized collection."""
    collector = get_global_optimized_collector()
    collector.stop_collection()


def register_agent_for_optimized_collection(agent_id: str, agent_instance: Any) -> None:
    """
    Register an agent for optimized collection.

    Args:
        agent_id: Unique identifier for the agent
        agent_instance: Agent instance with tracing capabilities
    """
    collector = get_global_optimized_collector()
    collector.register_agent(agent_id, agent_instance)


def get_optimized_collection_stats() -> dict[str, Any]:
    """Get optimized collection statistics."""
    collector = get_global_optimized_collector()
    return collector.get_performance_stats()
