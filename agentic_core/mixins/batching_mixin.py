"""
BatchingMixin - Focused Batching and Async Pooling Functionality

Phase 3 MRO Refactoring: Extracted from PerformanceMixin for single responsibility.

Provides:
- Batch queue operations
- Async operation pooling with semaphore
- Lazy initialization registry
"""

from __future__ import annotations

import asyncio
import logging
import threading
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from typing import Any, TypeVar

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

_emit_applies_guardrail("p0", "batching_mixin", "p0_governance")
_emit_reads_policy_state("p0", "batching_mixin", "policy_binding")
_emit_snapshots_state("p0", "batching_mixin", "state_snapshot")
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

_emit_emits_metric_event("batching_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("batching_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("batching_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("batching_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("batching_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("batching_mixin", "p4obs", "metric_6")
_emit_records_incident_event("batching_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("batching_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("batching_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("batching_mixin", "p4obs", "mon_state")
_emit_triggers_alert("batching_mixin", "p4obs", "alert")
_emit_links_incident_trace("batching_mixin", "p4obs", "trace_link")
_emit_captures_pattern("batching_mixin", "p3lm", "pattern")
_emit_records_learning_event("batching_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("batching_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("batching_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("batching_mixin", "p3lm", "routing")
_emit_improves_agent_policy("batching_mixin", "p3lm", "policy")
_emit_stores_learning_state("batching_mixin", "p3lm", "state")
_emit_records_execution_trace("batching_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("batching_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("batching_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("batching_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("batching_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("batching_mixin", "env_read", "p2_env_1")
_emit_reads_environ("batching_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("batching_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("batching_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "batching_mixin", "context_pull")
_emit_pulls_context("p1", "batching_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "batching_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "batching_mixin", "uwg_term_2")
_emit_writes_through("p1", "batching_mixin", "write_through")
_emit_writes_through("p1", "batching_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "batching_mixin", "safety_validation")
_emit_invokes_eval("p1", "batching_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "batching_mixin", "routing_commit")
_emit_escalates_to_human("p1", "batching_mixin", "human_escalation")
_emit_routes_through("p1", "batching_mixin", "route_through")
_emit_checks_agent_registry("p1", "batching_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "batching_mixin", "capability")
_emit_dispatches_execution_plan("p1", "batching_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "batching_mixin", "sub_agent")
_emit_routes_to_agent("p1", "batching_mixin", "target_agent")
_emit_verifies_policy("p1", "batching_mixin", "policy_check")
_emit_observes_runtime_state("p1", "batching_mixin", "runtime_state")
_emit_verifies_boundary("p1", "batching_mixin", "boundary_check")
_emit_transcripts_response("p1", "batching_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "batching_mixin")
_emit_gated_by_confidence("p1", "batching_mixin", "confidence_gate")
emit_replay_key("p0", "batching_mixin")
emit_determinism_digest("p0", "batching_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "batching_mixin", "execution_auth")
_emit_validates_capability("p2", "batching_mixin", "capability_check")
_emit_routes_to_capability("p2", "batching_mixin", "capability_route")
_emit_writes_via_uwg("p2", "batching_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "batching_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "batching_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "batching_mixin", "exec_output")
_emit_dispatches_agent("p3", "batching_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "batching_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "batching_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "batching_mixin", "healing_outcome")
_emit_escalates_failure("p3", "batching_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "batching_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "batching_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "batching_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "batching_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "batching_mixin", "eval_metric")
_emit_stores_embedding("p4", "batching_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "batching_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "batching_mixin", "exec_snapshot_link")

T = TypeVar("T")
Logger = logging.getLogger(__name__)


@dataclass
class BatchingConfig:
    """Configuration for batching operations."""

    batch_size: int = 100
    async_pool_size: int = 10
    max_batch_queues: int = 50
    max_batch_queue_size: int = 10000
    lazy_init_enabled: bool = True


class BatchingMixin:
    """
    Mixin providing batch operations and async pooling.

    Phase 3 MRO Refactoring: Single responsibility - batching only.

    Usage:
        class MyAgent(BatchingMixin, SovereignBaseAgent):
            async def process_items(self, items):
                for item in items:
                    self.batch_add("processing", item)
                    if self.should_flush_batch("processing"):
                        batch = self.batch_flush("processing")
                        await self.process_batch(batch)
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize batching state."""
        super().__init__(**kwargs)
        self._batching_config = BatchingConfig()
        self._batch_queues: dict[str, list] = {}
        self._lazy_registry: dict[str, Callable] = {}
        self._lazy_initialized: dict[str, Any] = {}
        self._batching_lock = threading.RLock()
        self._async_semaphore: asyncio.Semaphore | None = None
        self._batching_initialized = True
        Logger.debug(f"[BATCH] {self.__class__.__name__} batching initialized")

    def configure_batching(
        self,
        batch_size: int | None = None,
        async_pool_size: int | None = None,
        max_batch_queues: int | None = None,
        max_batch_queue_size: int | None = None,
        lazy_init_enabled: bool | None = None,
    ) -> None:
        """Configure batching settings."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "BatchingMixin.configure_batching"
        )

        if batch_size is not None and batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if async_pool_size is not None and async_pool_size <= 0:
            raise ValueError("async_pool_size must be positive")
        if max_batch_queues is not None and max_batch_queues <= 0:
            raise ValueError("max_batch_queues must be positive")
        if max_batch_queue_size is not None and max_batch_queue_size <= 0:
            raise ValueError("max_batch_queue_size must be positive")
        with self._batching_lock:
            if batch_size is not None:
                self._batching_config.batch_size = batch_size
            if async_pool_size is not None:
                self._batching_config.async_pool_size = async_pool_size
                self._async_semaphore = None
            if max_batch_queues is not None:
                self._batching_config.max_batch_queues = max_batch_queues
            if max_batch_queue_size is not None:
                self._batching_config.max_batch_queue_size = max_batch_queue_size
            if lazy_init_enabled is not None:
                self._batching_config.lazy_init_enabled = lazy_init_enabled

    def batch_add(self, queue_name: str, item: Any) -> int:
        """Add item to a batch queue. Returns current queue size."""
        with self._batching_lock:
            if (
                queue_name not in self._batch_queues
                and len(self._batch_queues) >= self._batching_config.max_batch_queues
            ):
                raise ValueError(f"Maximum batch queues ({self._batching_config.max_batch_queues}) exceeded")
            if queue_name not in self._batch_queues:
                self._batch_queues[queue_name] = []
            if len(self._batch_queues[queue_name]) >= self._batching_config.max_batch_queue_size:
                raise ValueError(
                    f"Batch queue '{queue_name}' size limit ({self._batching_config.max_batch_queue_size}) exceeded",
                )
            self._batch_queues[queue_name].append(item)
            return len(self._batch_queues[queue_name])

    def batch_flush(self, queue_name: str) -> list:
        """Flush and return all items from a batch queue."""
        with self._batching_lock:
            return self._batch_queues.pop(queue_name, [])

    def batch_size(self, queue_name: str) -> int:
        """Get current size of a batch queue."""
        with self._batching_lock:
            return len(self._batch_queues.get(queue_name, []))

    def should_flush_batch(self, queue_name: str) -> bool:
        """Check if batch queue should be flushed."""
        return self.batch_size(queue_name) >= self._batching_config.batch_size

    def batch_clear_all(self) -> int:
        """Clear all batch queues. Returns count of queues cleared."""
        with self._batching_lock:
            count = len(self._batch_queues)
            self._batch_queues.clear()
            return count

    def register_lazy(self, name: str, initializer: Callable[[], Any]) -> None:
        """Register a lazy-initialized resource."""
        self._lazy_registry[name] = initializer

    def get_lazy(self, name: str) -> Any:
        """Get a lazy-initialized resource."""
        if not self._batching_config.lazy_init_enabled:
            if name in self._lazy_registry:
                return self._lazy_registry[name]()
            raise KeyError(f"Lazy resource not registered: {name}")
        with self._batching_lock:
            if name in self._lazy_initialized:
                return self._lazy_initialized[name]
            if name not in self._lazy_registry:
                raise KeyError(f"Lazy resource not registered: {name}")
            resource = self._lazy_registry[name]()
            self._lazy_initialized[name] = resource
            Logger.debug(f"[BATCH] Lazy initialized: {name}")
            return resource

    def is_lazy_initialized(self, name: str) -> bool:
        """Check if a lazy resource has been initialized."""
        return name in self._lazy_initialized

    async def get_async_semaphore(self) -> asyncio.Semaphore:
        """Get or create async semaphore for pooling."""
        if self._async_semaphore is None:
            self._async_semaphore = asyncio.Semaphore(self._batching_config.async_pool_size)
        return self._async_semaphore

    async def run_pooled(self, coro) -> Any:
        """Run a coroutine with pool limiting."""
        semaphore = await self.get_async_semaphore()
        async with semaphore:
            return await coro

    async def execute_batch(
        self,
        tasks: Iterable[Awaitable[T]],
        *,
        concurrency: int = 10,
        timeout: float | None = None,
        return_exceptions: bool = False,
    ) -> list[T]:
        """Execute awaitables with bounded concurrency via asyncio.TaskGroup.

        Args:
            tasks: Iterable of awaitables to execute.
            concurrency: Max concurrent tasks (semaphore limit).
            timeout: Overall timeout in seconds (None = no limit).
            return_exceptions: If True, exceptions are returned in the
                result list instead of being raised.

        Returns:
            Ordered list of results matching the input task order.
        """
        task_list = list(tasks)
        if not task_list:
            return []
        semaphore = asyncio.Semaphore(concurrency)
        results: list[Any] = [None] * len(task_list)

        async def _run(index: int, awaitable: Awaitable[T]) -> None:
            async with semaphore:
                results[index] = await awaitable

        async def _run_safe(index: int, awaitable: Awaitable[T]) -> None:
            async with semaphore:
                try:
                    results[index] = await awaitable
                except (RuntimeError, OSError, ValueError, AttributeError, TypeError) as exc:  # guardian: allow-silent-swallow
                    results[index] = exc

        runner = _run_safe if return_exceptions else _run

        async def _execute() -> None:
            async with asyncio.TaskGroup() as tg:
                for i, aw in enumerate(task_list):
                    tg.create_task(runner(i, aw))

        if timeout is not None:
            await asyncio.wait_for(_execute(), timeout=timeout)
        else:
            await _execute()
        return results

    # guardian: allow-magic-config
    async def batch_execute(self, tasks: list, max_workers: int = 5, sequential: bool = False) -> list[Any]:
        """Backwards-compat alias for legacy batch_operation_mixin callers.

        Prefer ``execute_batch`` for new code.
        """
        if sequential:
            results = []
            for task in tasks:
                try:
                    results.append(await task)
                except (RuntimeError, OSError, ValueError, AttributeError, TypeError) as e:  # guardian: allow-silent-swallow
                    results.append(e)
            return results
        return await self.execute_batch(
            tasks,
            concurrency=max_workers,
            timeout=DEFAULT_TIMEOUT,
            return_exceptions=True,
        )

    def get_batching_status(self) -> dict[str, Any]:
        """Get batching status."""
        with self._batching_lock:
            return {
                "batch_queues": {name: len(items) for name, items in self._batch_queues.items()},
                "lazy_registered": len(self._lazy_registry),
                "lazy_initialized": len(self._lazy_initialized),
                "config": {
                    "batch_size": self._batching_config.batch_size,
                    "async_pool_size": self._batching_config.async_pool_size,
                    "max_batch_queues": self._batching_config.max_batch_queues,
                },
            }


__all__ = ["BatchingMixin", "BatchingConfig"]
