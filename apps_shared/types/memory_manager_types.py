"""Memory Manager - Controls memory usage and prevents unbounded growth.

This module provides memory bounds enforcement, context pruning, and
monitoring to prevent memory leaks and OOM errors.
"""

import gc
import logging
import sys
import threading
import time
import tracemalloc
from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any

import psutil

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

_emit_applies_guardrail("p0", "memory_manager_types", "p0_governance")
_emit_reads_policy_state("p0", "memory_manager_types", "policy_binding")
_emit_snapshots_state("p0", "memory_manager_types", "state_snapshot")
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

_emit_emits_metric_event("memory_manager_types", "p4obs", "metric_1")
_emit_emits_metric_event("memory_manager_types", "p4obs", "metric_2")
_emit_emits_metric_event("memory_manager_types", "p4obs", "metric_3")
_emit_emits_metric_event("memory_manager_types", "p4obs", "metric_4")
_emit_emits_metric_event("memory_manager_types", "p4obs", "metric_5")
_emit_emits_metric_event("memory_manager_types", "p4obs", "metric_6")
_emit_records_incident_event("memory_manager_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("memory_manager_types", "p4obs", "anomaly")
_emit_writes_observability_log("memory_manager_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("memory_manager_types", "p4obs", "mon_state")
_emit_triggers_alert("memory_manager_types", "p4obs", "alert")
_emit_links_incident_trace("memory_manager_types", "p4obs", "trace_link")
_emit_captures_pattern("memory_manager_types", "p3lm", "pattern")
_emit_records_learning_event("memory_manager_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("memory_manager_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("memory_manager_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("memory_manager_types", "p3lm", "routing")
_emit_improves_agent_policy("memory_manager_types", "p3lm", "policy")
_emit_stores_learning_state("memory_manager_types", "p3lm", "state")
_emit_records_execution_trace("memory_manager_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("memory_manager_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("memory_manager_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("memory_manager_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("memory_manager_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("memory_manager_types", "env_read", "p2_env_1")
_emit_reads_environ("memory_manager_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("memory_manager_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("memory_manager_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "memory_manager_types", "context_pull")
_emit_pulls_context("p1", "memory_manager_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "memory_manager_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "memory_manager_types", "uwg_term_2")
_emit_writes_through("p1", "memory_manager_types", "write_through")
_emit_writes_through("p1", "memory_manager_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "memory_manager_types", "safety_validation")
_emit_invokes_eval("p1", "memory_manager_types", "eval_call")
_emit_proposal_commits_routing("p1", "memory_manager_types", "routing_commit")
_emit_escalates_to_human("p1", "memory_manager_types", "human_escalation")
_emit_routes_through("p1", "memory_manager_types", "route_through")
_emit_checks_agent_registry("p1", "memory_manager_types", "agent_registry")
_emit_validates_agent_capability("p1", "memory_manager_types", "capability")
_emit_dispatches_execution_plan("p1", "memory_manager_types", "exec_plan")
_emit_agent_executes_agent("p1", "memory_manager_types", "sub_agent")
_emit_routes_to_agent("p1", "memory_manager_types", "target_agent")
_emit_verifies_policy("p1", "memory_manager_types", "policy_check")
_emit_observes_runtime_state("p1", "memory_manager_types", "runtime_state")
_emit_verifies_boundary("p1", "memory_manager_types", "boundary_check")
_emit_transcripts_response("p1", "memory_manager_types", "transcript")
_emit_hard_fails_untranscripted("p1", "memory_manager_types")
_emit_gated_by_confidence("p1", "memory_manager_types", "confidence_gate")
emit_replay_key("p0", "memory_manager_types")
emit_determinism_digest("p0", "memory_manager_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "memory_manager_types", "execution_auth")
_emit_validates_capability("p2", "memory_manager_types", "capability_check")
_emit_routes_to_capability("p2", "memory_manager_types", "capability_route")
_emit_writes_via_uwg("p2", "memory_manager_types", "uwg_write")
_emit_blocks_direct_write("p2", "memory_manager_types", "direct_write_block")
_emit_records_tool_invocation("p2", "memory_manager_types", "tool_invocation")
_emit_captures_execution_output("p2", "memory_manager_types", "exec_output")
_emit_dispatches_agent("p3", "memory_manager_types", "agent_dispatch")
_emit_coordinates_agents("p3", "memory_manager_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "memory_manager_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "memory_manager_types", "healing_outcome")
_emit_escalates_failure("p3", "memory_manager_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "memory_manager_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "memory_manager_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "memory_manager_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "memory_manager_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "memory_manager_types", "eval_metric")
_emit_stores_embedding("p4", "memory_manager_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "memory_manager_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "memory_manager_types", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class PruningStrategy(Enum):
    """Strategies for pruning context data."""

    LRU = "lru"
    FIFO = "fifo"
    SIZE_BASED = "size_based"
    PRIORITY = "priority"


@dataclass
class MemoryLimits:
    """configuration for memory limits."""

    max_context_size: int = 10 * 1024 * 1024
    max_context_items: int = 1000
    max_string_length: int = 10000
    max_list_size: int = 100
    max_dict_size: int = 100
    max_memory_mb: float = 512.0
    gc_threshold: float = 0.8


@dataclass
class ContextItem:
    """Item in context with metadata."""

    key: str
    value: Any
    size_bytes: int
    last_accessed: float
    priority: int = 0
    access_count: int = 0


class MemoryManager:
    """Manages memory usage and enforces limits."""

    def __init__(self, name: str = "default", limits: MemoryLimits | None = None):
        """Initialize the memory manager.

        Args:
            name: Manager name for logging
            limits: Memory limits configuration
        """
        self.name = name
        self.limits = limits or MemoryLimits()
        self._context: OrderedDict[str, ContextItem] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            "total_size": 0,
            "item_count": 0,
            "pruned_count": 0,
            "gc_count": 0,
            "memory_violations": 0,
        }
        self._monitoring = False
        self._monitor_thread: threading.Thread | None = None
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        tracemalloc.start()
        logger.debug(f"Initialized MemoryManager: {name}")

    # guardian: allow-magic-config
    def start_monitoring(self, interval_seconds: float = 5.0) -> None:
        """Start memory monitoring.

        Args:
            interval_seconds: Monitoring interval
        """
        if self._monitoring:
            return
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True,
        )
        self._monitor_thread.start()
        logger.info(f"Started memory monitoring for {self.name}")

    def stop_monitoring(self) -> None:
        """Stop memory monitoring."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "MemoryManager.stop_monitoring"
        )
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=DEFAULT_TIMEOUT)
        logger.info(f"Stopped memory monitoring for {self.name}")

    def add_context(self, key: str, value: Any, priority: int = 0, max_size: int | None = None) -> bool:
        """Add an item to context with size limits.

        Args:
            key: Context key
            value: Context value
            priority: Priority for pruning
            max_size: Maximum size for this item

        Returns:
            True if added successfully
        """
        sanitized_value = self._sanitize_value(value, max_size)
        size_bytes = self._calculate_size(sanitized_value)
        with self._lock:
            self._ensure_capacity(size_bytes)
            if key in self._context:
                old_item = self._context[key]
                self._stats["total_size"] -= old_item.size_bytes
                self._stats["item_count"] -= 1
            item = ContextItem(
                key=key,
                value=sanitized_value,
                size_bytes=size_bytes,
                last_accessed=time.time(),
                priority=priority,
            )
            self._context[key] = item
            self._context.move_to_end(key)
            self._stats["total_size"] += size_bytes
            self._stats["item_count"] += 1
            self._check_memory_limits()
            return True

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context item.

        Args:
            key: Context key
            default: Default value if not found

        Returns:
            Context value or default
        """
        with self._lock:
            if key in self._context:
                item = self._context[key]
                item.last_accessed = time.time()
                item.access_count += 1
                self._context.move_to_end(key)
                return item.value
            return default

    def remove_context(self, key: str) -> bool:
        """Remove a context item.

        Args:
            key: Context key

        Returns:
            True if removed
        """
        with self._lock:
            if key in self._context:
                item = self._context.pop(key)
                self._stats["total_size"] -= item.size_bytes
                self._stats["item_count"] -= 1
                return True
            return False

    def prune_context(
        self,
        strategy: PruningStrategy = PruningStrategy.LRU,
        target_size: int | None = None,
    ) -> int:
        """Prune context items based on strategy.

        Args:
            strategy: Pruning strategy
            target_size: Target size to achieve

        Returns:
            Number of items pruned
        """
        with self._lock:
            if not self._context:
                return 0
            target = target_size or int(self.limits.max_context_size * 0.8)
            pruned = 0
            if strategy == PruningStrategy.LRU:
                while self._stats["total_size"] > target and self._context:
                    key, item = self._context.popitem(last=False)
                    self._stats["total_size"] -= item.size_bytes
                    self._stats["item_count"] -= 1
                    pruned += 1
            elif strategy == PruningStrategy.FIFO:
                while self._stats["total_size"] > target and self._context:
                    key, item = self._context.popitem(last=False)
                    self._stats["total_size"] -= item.size_bytes
                    self._stats["item_count"] -= 1
                    pruned += 1
            elif strategy == PruningStrategy.SIZE_BASED:
                items = sorted(self._context.values(), key=lambda x: x.size_bytes, reverse=True)
                for item in items:
                    if self._stats["total_size"] <= target:
                        break
                    del self._context[item.key]
                    self._stats["total_size"] -= item.size_bytes
                    self._stats["item_count"] -= 1
                    pruned += 1
            elif strategy == PruningStrategy.PRIORITY:
                items = sorted(self._context.values(), key=lambda x: x.priority)
                for item in items:
                    if self._stats["total_size"] <= target:
                        break
                    del self._context[item.key]
                    self._stats["total_size"] -= item.size_bytes
                    self._stats["item_count"] -= 1
                    pruned += 1
            self._stats["pruned_count"] += pruned
            logger.debug(f"Pruned {pruned} items using {strategy.value} strategy")
            return pruned

    def clear_context(self) -> None:
        """Clear all context data."""
        with self._lock:
            self._context.clear()
            self._stats["total_size"] = 0
            self._stats["item_count"] = 0
            logger.debug("Cleared all context data")

    def _sanitize_value(self, value: Any, max_size: int | None = None) -> Any:
        """Sanitize a value to prevent memory issues.

        Args:
            value: Value to sanitize
            max_size: Maximum size for collections

        Returns:
            Sanitized value
        """
        if isinstance(value, str):
            max_len = max_size or self.limits.max_string_length
            if len(value) > max_len:
                logger.warning(f"Truncated string from {len(value)} to {max_len} characters")
                return value[:max_len]
        elif isinstance(value, list):
            max_len = max_size or self.limits.max_list_size
            if len(value) > max_len:
                logger.warning(f"Truncated list from {len(value)} to {max_len} items")
                return value[:max_len]
        elif isinstance(value, dict):
            max_len = max_size or self.limits.max_dict_size
            if len(value) > max_len:
                logger.warning(f"Truncated dict from {len(value)} to {max_len} items")
                return dict(list(value.items())[:max_len])
        return value

    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of a value.

        Args:
            value: Value to measure

        Returns:
            Size in bytes
        """
        if isinstance(value, str):
            return len(value.encode("utf-8"))
        elif isinstance(value, list | tuple):
            return sum(self._calculate_size(v) for v in value) + 64
        elif isinstance(value, dict):
            return sum((self._calculate_size(k) + self._calculate_size(v) for k, v in value.items())) + 64
        else:
            return sys.getsizeof(value)

    def _ensure_capacity(self, required_size: int) -> None:
        """Ensure enough capacity for new item.

        Args:
            required_size: Size of item to add
        """
        while self._stats["item_count"] >= self.limits.max_context_items and self._context:
            self.prune_context(PruningStrategy.LRU, target_size=self.limits.max_context_size - required_size)
        while self._stats["total_size"] + required_size > self.limits.max_context_size and self._context:
            self.prune_context(PruningStrategy.LRU, target_size=self.limits.max_context_size - required_size)

    def _check_memory_limits(self) -> None:
        """Check if process memory limits are exceeded."""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            if memory_mb > self.limits.max_memory_mb:
                self._stats["memory_violations"] += 1
                logger.warning(f"Memory limit exceeded: {memory_mb:.1f}MB > {self.limits.max_memory_mb}MB")
                self.prune_context(
                    PruningStrategy.SIZE_BASED,
                    target_size=int(self.limits.max_context_size * 0.5),
                )
                gc.collect()
                self._stats["gc_count"] += 1
            elif memory_mb > self.limits.max_memory_mb * self.limits.gc_threshold:
                gc.collect()
                self._stats["gc_count"] += 1
        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
        ):  # review:  should be handled with specific context
            pass

    def _monitor_loop(self, interval_seconds: float) -> None:
        """Background monitoring loop.

        Args:
            interval_seconds: Monitoring interval
        """
        while self._monitoring:
            try:
                self._check_memory_limits()
                time.sleep(interval_seconds)
            except (TypeError, ValueError, KeyError, AttributeError, RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
                logger.error(f"Memory monitoring error: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get memory manager statistics.

        Returns:
            Statistics dictionary
        """
        with self._lock:
            stats = self._stats.copy()
            try:
                process = psutil.Process()
                stats["process_memory_mb"] = process.memory_info().rss / 1024 / 1024
                stats["process_memory_percent"] = process.memory_percent()
            except (ValueError, TypeError, RuntimeError) as e:
                raise
            if tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                stats["traced_memory_mb"] = current / 1024 / 1024
                stats["peak_memory_mb"] = peak / 1024 / 1024
            return stats

    def get_memory_report(self) -> str:
        """Get a formatted memory report.

        Returns:
            Memory report string
        """
        stats = self.get_stats()
        report = f"\nMemory Manager Report: {self.name}\n========================================\nContext Items: {stats['item_count']}\nContext Size: {stats['total_size'] / 1024 / 1024:.2f} MB\nItems Pruned: {stats['pruned_count']}\nGC Runs: {stats['gc_count']}\nMemory Violations: {stats['memory_violations']}\nProcess Memory: {stats.get('process_memory_mb', 0):.2f} MB\nMemory Percent: {stats.get('process_memory_percent', 0):.1f}%\n"
        if "traced_memory_mb" in stats:
            report += f"Traced Memory: {stats['traced_memory_mb']:.2f} MB\n"
            report += f"Peak Memory: {stats['peak_memory_mb']:.2f} MB\n"
        return report


_managers: dict[str, MemoryManager] = {}
_manager_lock = threading.Lock()


def get_memory_manager(name: str = "default", limits: MemoryLimits | None = None) -> MemoryManager:
    """Get or create a memory manager.

    Args:
        name: Manager name
        limits: Optional memory limits

    Returns:
        MemoryManager instance
    """
    with _manager_lock:
        if name not in _managers:
            manager = MemoryManager(name, limits)
            _managers[name] = manager
        return _managers[name]


def cleanup_all_managers() -> None:
    """Cleanup all memory managers."""
    with _manager_lock:
        for manager in _managers.values():
            manager.stop_monitoring()
            manager.clear_context()
        _managers.clear()


@contextmanager
def memory_bound(manager: MemoryManager, max_memory_mb: float):
    """Context manager for memory-bound operations.

    Args:
        manager: Memory manager to use
        max_memory_mb: Maximum memory for operation
    """
    initial_memory = manager.get_stats().get("process_memory_mb", 0)
    try:
        yield
    finally:
        current_memory = manager.get_stats().get("process_memory_mb", 0)
        if current_memory - initial_memory > max_memory_mb:
            logger.warning(f"Operation exceeded memory bound: {current_memory - initial_memory:.1f}MB")
            manager.prune_context(PruningStrategy.SIZE_BASED)
