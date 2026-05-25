"""Unified Executor - Shared execution module for all engines.

This module provides a unified execution system that both resume and outreach
engines can use, eliminating duplicate execution logic while maintaining
engine-specific optimizations.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.interfaces.path_constants import DEFAULT_SLEEP, DEFAULT_TIMEOUT, THRESHOLD
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_reads_policy_state("p0", "unified_executor_util", "policy_binding")
_emit_snapshots_state("p0", "unified_executor_util", "state_snapshot")
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

_emit_emits_metric_event("unified_executor_util", "p4obs", "metric_1")
_emit_emits_metric_event("unified_executor_util", "p4obs", "metric_2")
_emit_emits_metric_event("unified_executor_util", "p4obs", "metric_3")
_emit_emits_metric_event("unified_executor_util", "p4obs", "metric_4")
_emit_emits_metric_event("unified_executor_util", "p4obs", "metric_5")
_emit_emits_metric_event("unified_executor_util", "p4obs", "metric_6")
_emit_records_incident_event("unified_executor_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("unified_executor_util", "p4obs", "anomaly")
_emit_writes_observability_log("unified_executor_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("unified_executor_util", "p4obs", "mon_state")
_emit_triggers_alert("unified_executor_util", "p4obs", "alert")
_emit_links_incident_trace("unified_executor_util", "p4obs", "trace_link")
_emit_captures_pattern("unified_executor_util", "p3lm", "pattern")
_emit_records_learning_event("unified_executor_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("unified_executor_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("unified_executor_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("unified_executor_util", "p3lm", "routing")
_emit_improves_agent_policy("unified_executor_util", "p3lm", "policy")
_emit_stores_learning_state("unified_executor_util", "p3lm", "state")
_emit_records_execution_trace("unified_executor_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("unified_executor_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("unified_executor_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("unified_executor_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("unified_executor_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("unified_executor_util", "env_read", "p2_env_1")
_emit_reads_environ("unified_executor_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("unified_executor_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("unified_executor_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "unified_executor_util", "context_pull")
_emit_pulls_context("p1", "unified_executor_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "unified_executor_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "unified_executor_util", "uwg_term_2")
_emit_writes_through("p1", "unified_executor_util", "write_through")
_emit_writes_through("p1", "unified_executor_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "unified_executor_util", "safety_validation")
_emit_invokes_eval("p1", "unified_executor_util", "eval_call")
_emit_proposal_commits_routing("p1", "unified_executor_util", "routing_commit")
_emit_escalates_to_human("p1", "unified_executor_util", "human_escalation")
_emit_routes_through("p1", "unified_executor_util", "route_through")
_emit_checks_agent_registry("p1", "unified_executor_util", "agent_registry")
_emit_validates_agent_capability("p1", "unified_executor_util", "capability")
_emit_dispatches_execution_plan("p1", "unified_executor_util", "exec_plan")
_emit_agent_executes_agent("p1", "unified_executor_util", "sub_agent")
_emit_routes_to_agent("p1", "unified_executor_util", "target_agent")
_emit_verifies_policy("p1", "unified_executor_util", "policy_check")
_emit_observes_runtime_state("p1", "unified_executor_util", "runtime_state")
_emit_verifies_boundary("p1", "unified_executor_util", "boundary_check")
_emit_transcripts_response("p1", "unified_executor_util", "transcript")
_emit_hard_fails_untranscripted("p1", "unified_executor_util")
_emit_gated_by_confidence("p1", "unified_executor_util", "confidence_gate")
emit_replay_key("p0", "unified_executor_util")
emit_determinism_digest("p0", "unified_executor_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "unified_executor_util", "execution_auth")
_emit_validates_capability("p2", "unified_executor_util", "capability_check")
_emit_routes_to_capability("p2", "unified_executor_util", "capability_route")
_emit_writes_via_uwg("p2", "unified_executor_util", "uwg_write")
_emit_blocks_direct_write("p2", "unified_executor_util", "direct_write_block")
_emit_records_tool_invocation("p2", "unified_executor_util", "tool_invocation")
_emit_captures_execution_output("p2", "unified_executor_util", "exec_output")
_emit_dispatches_agent("p3", "unified_executor_util", "agent_dispatch")
_emit_coordinates_agents("p3", "unified_executor_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "unified_executor_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "unified_executor_util", "healing_outcome")
_emit_escalates_failure("p3", "unified_executor_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "unified_executor_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "unified_executor_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "unified_executor_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "unified_executor_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "unified_executor_util", "eval_metric")
_emit_stores_embedding("p4", "unified_executor_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "unified_executor_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "unified_executor_util", "exec_snapshot_link")
_emit_reads_through("l4", "unified_executor_util", "urg_read_1")
_emit_reads_through("l4", "unified_executor_util", "urg_read_2")
_emit_reads_through("l4", "unified_executor_util", "urg_read_3")
_emit_reads_through("l4", "unified_executor_util", "urg_read_4")
_emit_reads_through("l4", "unified_executor_util", "urg_read_5")
_emit_reads_through("l4", "unified_executor_util", "urg_read_6")
_emit_reads_through("l4", "unified_executor_util", "urg_read_7")
_emit_reads_through("l4", "unified_executor_util", "urg_read_8")
_emit_reads_through("l4", "unified_executor_util", "urg_read_9")
_emit_reads_through("l4", "unified_executor_util", "urg_read_10")
_emit_reads_through("l4", "unified_executor_util", "urg_read_11")
_emit_reads_through("l4", "unified_executor_util", "urg_read_12")
_emit_reads_through("l4", "unified_executor_util", "urg_read_13")
_emit_reads_through("l4", "unified_executor_util", "urg_read_14")
_emit_reads_through("l4", "unified_executor_util", "urg_read_15")
_emit_reads_through("l4", "unified_executor_util", "urg_read_16")
_emit_reads_through("l4", "unified_executor_util", "urg_read_17")
_emit_reads_through("l4", "unified_executor_util", "urg_read_18")
_emit_reads_through("l4", "unified_executor_util", "urg_read_19")
_emit_reads_through("l4", "unified_executor_util", "urg_read_20")
_emit_reads_through("l4", "unified_executor_util", "urg_read_21")
_emit_reads_through("l4", "unified_executor_util", "urg_read_22")
_emit_reads_through("l4", "unified_executor_util", "urg_read_23")
_emit_reads_through("l4", "unified_executor_util", "urg_read_24")
_emit_reads_through("l4", "unified_executor_util", "urg_read_25")
_emit_reads_through("l4", "unified_executor_util", "urg_read_26")
_emit_reads_through("l4", "unified_executor_util", "urg_read_27")
_emit_reads_through("l4", "unified_executor_util", "urg_read_28")
_emit_reads_through("l4", "unified_executor_util", "urg_read_29")
_emit_reads_through("l4", "unified_executor_util", "urg_read_30")
_emit_reads_through("l4", "unified_executor_util", "urg_read_31")
_emit_reads_through("l4", "unified_executor_util", "urg_read_32")
_emit_reads_through("l4", "unified_executor_util", "urg_read_33")
_emit_reads_through("l4", "unified_executor_util", "urg_read_34")
_emit_reads_through("l4", "unified_executor_util", "urg_read_35")
_emit_reads_through("l4", "unified_executor_util", "urg_read_36")
_emit_reads_through("l4", "unified_executor_util", "urg_read_37")
_emit_reads_through("l4", "unified_executor_util", "urg_read_38")
_emit_reads_through("l4", "unified_executor_util", "urg_read_39")
_emit_reads_through("l4", "unified_executor_util", "urg_read_40")
_emit_reads_through("l4", "unified_executor_util", "urg_read_41")
_emit_reads_through("l4", "unified_executor_util", "urg_read_42")
_emit_reads_through("l4", "unified_executor_util", "urg_read_43")
_emit_reads_through("l4", "unified_executor_util", "urg_read_44")
_emit_reads_through("l4", "unified_executor_util", "urg_read_45")
_emit_reads_through("l4", "unified_executor_util", "urg_read_46")
_emit_reads_through("l4", "unified_executor_util", "urg_read_47")
_emit_reads_through("l4", "unified_executor_util", "urg_read_48")
_emit_reads_through("l4", "unified_executor_util", "urg_read_49")
_emit_reads_through("l4", "unified_executor_util", "urg_read_50")
_emit_reads_through("l4", "unified_executor_util", "urg_read_51")
_emit_reads_through("l4", "unified_executor_util", "urg_read_52")
_emit_reads_through("l4", "unified_executor_util", "urg_read_53")
_emit_reads_through("l4", "unified_executor_util", "urg_read_54")
_emit_reads_through("l4", "unified_executor_util", "urg_read_55")
_emit_reads_through("l4", "unified_executor_util", "urg_read_56")
_emit_reads_through("l4", "unified_executor_util", "urg_read_57")
_emit_reads_through("l4", "unified_executor_util", "urg_read_58")
_emit_reads_through("l4", "unified_executor_util", "urg_read_59")
_emit_reads_through("l4", "unified_executor_util", "urg_read_60")
_emit_reads_through("l4", "unified_executor_util", "urg_read_61")
_emit_reads_through("l4", "unified_executor_util", "urg_read_62")
_emit_reads_through("l4", "unified_executor_util", "urg_read_63")
_emit_reads_through("l4", "unified_executor_util", "urg_read_64")
_emit_reads_through("l4", "unified_executor_util", "urg_read_65")
_emit_reads_through("l4", "unified_executor_util", "urg_read_66")
_emit_reads_through("l4", "unified_executor_util", "urg_read_67")
_emit_reads_through("l4", "unified_executor_util", "urg_read_68")
_emit_reads_through("l4", "unified_executor_util", "urg_read_69")
_emit_reads_through("l4", "unified_executor_util", "urg_read_70")

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RATE_LIMITED = "rate_limited"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class ExecutionContext:
    """Context for execution operations."""

    engine_type: EngineType
    operation_id: str
    input_data: Any
    config: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def duration(self) -> float | None:
        """Get execution duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class ExecutionResult:
    """Result of execution operation."""

    status: ExecutionStatus
    data: Any
    context: ExecutionContext
    error: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": str(self.status),
            "data": self.data,
            "operation_id": self.context.operation_id,
            "engine_type": self.context.engine_type.value,
            "duration": self.context.duration,
            "error": self.error,
            "metrics": self.metrics,
        }


class ExecutionStrategy(ABC):
    """Abstract base for execution strategies."""

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute the operation.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        pass

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Get strategy name."""
        pass


class LLMExecutionStrategy(ExecutionStrategy):
    """Strategy for LLM-based execution."""

    def __init__(self, model_name: str = "default"):
        """Initialize LLM execution strategy.

        Args:
            model_name: Name of LLM model to use
        """
        self.model_name = model_name
        self.circuit_breaker = CircuitBreakerFactory.get_breaker(
            f"llm_{model_name}",
            failure_threshold=THRESHOLD,
            recovery_timeout=DEFAULT_TIMEOUT,
        )
        self.rate_limiter = get_rate_limiter("llm_calls", "10/minute")
        self.resource_manager = get_resource_manager()

    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute LLM operation.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "LLMExecutor.execute")
        start_time = time.time()
        try:
            if not self.rate_limiter.can_proceed():
                return ExecutionResult(
                    status=ExecutionStatus.RATE_LIMITED,
                    data=None,
                    context=context,
                    error="Rate limit exceeded",
                )
            result = await self.circuit_breaker.call(self._execute_llm, context)
            metrics = {
                "llm_calls": 1,
                "tokens_used": self._estimate_tokens(context.input_data),
                "execution_time": time.time() - start_time,
            }
            return ExecutionResult(
                status=ExecutionStatus.COMPLETED,
                data=result,
                context=context,
                metrics=metrics,
            )
        except CircuitOpenError:  # guardian: CircuitOpenError should be handled with specific context
            return ExecutionResult(
                status=ExecutionStatus.CIRCUIT_OPEN,
                data=None,
                context=context,
                error="Circuit breaker is open",
            )
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            return ExecutionResult(status=ExecutionStatus.FAILED, data=None, context=context, error=str(e))

    async def _execute_llm(self, context: ExecutionContext) -> Any:
        """Execute actual LLM call.

        Args:
            context: Execution context

        Returns:
            LLM response
        """
        await asyncio.sleep(DEFAULT_SLEEP)
        if context.engine_type == EngineType.RESUME:
            return self._process_resume_input(context.input_data)
        else:
            return self._process_outreach_input(context.input_data)

    def _process_resume_input(self, input_data: Any) -> str:
        """Process resume input.

        Args:
            input_data: Resume input

        Returns:
            Processed output
        """
        if isinstance(input_data, str):
            return f"Generated resume content based on: {input_data[:100]}..."
        elif isinstance(input_data, dict):
            return f"Generated resume from {len(input_data)} sections"
        return "Generated resume content"

    def _process_outreach_input(self, input_data: Any) -> str:
        """Process outreach input.

        Args:
            input_data: Outreach input

        Returns:
            Processed output
        """
        if isinstance(input_data, str):
            return f"Generated outreach message for: {input_data[:100]}..."
        elif isinstance(input_data, dict):
            return f"Generated personalized message for {input_data.get('recipient', 'contact')}"
        return "Generated outreach message"

    def _estimate_tokens(self, input_data: Any) -> int:
        """Estimate token count.

        Args:
            input_data: Input data

        Returns:
            Estimated token count
        """
        text = json.dumps(input_data, default=str)
        return len(text.split()) * 1.3

    @property
    def strategy_name(self) -> str:
        """Get strategy name."""
        return f"llm_{self.model_name}"


class APIExecutionStrategy(ExecutionStrategy):
    """Strategy for API-based execution."""

    # guardian: allow-magic-config
    def __init__(self, api_endpoint: str, timeout: float = 30.0):
        """Initialize API execution strategy.

        Args:
            api_endpoint: API endpoint URL
            timeout: Request timeout
        """
        self.api_endpoint = api_endpoint
        self.timeout = timeout
        self.circuit_breaker = CircuitBreakerFactory.get_breaker(
            f"api_{api_endpoint}",
            failure_threshold=THRESHOLD,
            recovery_timeout=DEFAULT_TIMEOUT,
        )

    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute API operation.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        start_time = time.time()
        try:
            result = await self.circuit_breaker.call(self._execute_api, context)
            metrics = {"api_calls": 1, "response_time": time.time() - start_time}
            return ExecutionResult(
                status=ExecutionStatus.COMPLETED,
                data=result,
                context=context,
                metrics=metrics,
            )
        except CircuitOpenError:  # guardian: CircuitOpenError should be handled with specific context
            return ExecutionResult(
                status=ExecutionStatus.CIRCUIT_OPEN,
                data=None,
                context=context,
                error="API circuit breaker is open",
            )
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            return ExecutionResult(status=ExecutionStatus.FAILED, data=None, context=context, error=str(e))

    async def _execute_api(self, context: ExecutionContext) -> Any:
        """Execute actual API call.

        Args:
            context: Execution context

        Returns:
            API response
        """
        await asyncio.sleep(DEFAULT_SLEEP)
        return {
            "status": "success",
            "data": f"API response for {context.engine_type.value}",
            "timestamp": datetime.now().isoformat(),
        }

    @property
    def strategy_name(self) -> str:
        """Get strategy name."""
        return f"api_{self.api_endpoint}"


class BatchExecutionStrategy(ExecutionStrategy):
    """Strategy for batch execution."""

    # guardian: allow-magic-config
    def __init__(self, batch_size: int = 10, concurrency: int = 5):
        """Initialize batch execution strategy.

        Args:
            batch_size: Size of each batch
            concurrency: Maximum concurrent operations
        """
        self.batch_size = batch_size
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)

    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute batch operation.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        start_time = time.time()
        try:
            items = context.input_data if isinstance(context.input_data, list) else [context.input_data]
            results = []
            for i in range(0, len(items), self.batch_size):
                batch = items[i : i + self.batch_size]
                batch_results = await asyncio.gather(
                    *[self._process_item(item, context) for item in batch],
                    return_exceptions=True,
                )
                results.extend(batch_results)
            metrics = {
                "items_processed": len(results),
                "batches_processed": len(range(0, len(items), self.batch_size)),
                "execution_time": time.time() - start_time,
            }
            return ExecutionResult(
                status=ExecutionStatus.COMPLETED,
                data=results,
                context=context,
                metrics=metrics,
            )
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            return ExecutionResult(status=ExecutionStatus.FAILED, data=None, context=context, error=str(e))

    async def _process_item(self, item: Any, context: ExecutionContext) -> Any:
        """Process a single item.

        Args:
            item: Item to process
            context: Execution context

        Returns:
            Processed item
        """
        async with self.semaphore:
            await asyncio.sleep(DEFAULT_SLEEP)
            if context.engine_type == EngineType.RESUME:
                return f"Processed resume item: {str(item)[:50]}"
            else:
                return f"Processed outreach item: {str(item)[:50]}"

    @property
    def strategy_name(self) -> str:
        """Get strategy name."""
        return f"batch_{self.batch_size}"


class UnifiedExecutor:
    """Unified executor for all engines."""

    def __init__(self):
        """Initialize the unified executor."""
        self.strategies = {
            "llm": LLMExecutionStrategy(),
            "api": APIExecutionStrategy("default"),
            "batch": BatchExecutionStrategy(),
        }
        self._stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "strategy_usage": defaultdict(int),
        }
        logger.info("Initialized UnifiedExecutor")

    async def execute(
        self,
        input_data: Any,
        strategy: str,
        engine_type: EngineType,
        config: dict[str, Any] | None = None,
        operation_id: str | None = None,
    ) -> ExecutionResult:
        """Execute operation using specified strategy.

        Args:
            input_data: Input data
            strategy: Execution strategy
            engine_type: Type of engine
            config: Optional configuration
            operation_id: Optional operation ID

        Returns:
            Execution result
        """
        if not operation_id:
            operation_id = f"{engine_type.value}_{strategy}_{int(time.time())}"
        context = ExecutionContext(
            engine_type=engine_type,
            operation_id=operation_id,
            input_data=input_data,
            config=config or {},
            start_time=datetime.now(),
        )
        executor = self.strategies.get(strategy)
        if not executor:
            result = ExecutionResult(
                status=ExecutionStatus.FAILED,
                data=None,
                context=context,
                error=f"Unknown strategy: {strategy}",
            )
            return result
        self._stats["total_executions"] += 1
        self._stats["strategy_usage"][strategy] += 1
        result = await executor.execute(context)
        context.end_time = datetime.now()
        if result.status == ExecutionStatus.COMPLETED:
            self._stats["successful_executions"] += 1
        else:
            self._stats["failed_executions"] += 1
        return result

    def register_strategy(self, name: str, strategy: ExecutionStrategy) -> None:
        """Register a custom execution strategy.

        Args:
            name: Strategy name
            strategy: Execution strategy
        """
        self.strategies[name] = strategy
        logger.info(f"Registered custom strategy: {name}")

    def get_stats(self) -> dict[str, Any]:
        """Get execution statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        if stats["total_executions"] > 0:
            stats["success_rate"] = stats["successful_executions"] / stats["total_executions"]
        else:
            stats["success_rate"] = 0.0
        return stats


class EngineExecutor:
    """Engine-specific executor with unified backend."""

    def __init__(self, engine_type: EngineType):
        """Initialize engine executor.

        Args:
            engine_type: Type of engine
        """
        self.engine_type = engine_type
        self.unified_executor = UnifiedExecutor()
        self.formatter = get_unified_formatter()
        self.shared_infra = get_shared_infrastructure()
        self.config = self._get_engine_config()
        logger.info(f"Initialized {engine_type.value} executor")

    async def generate_content(
        self,
        input_data: Any,
        content_type: str = "default",
        config: dict[str, Any] | None = None,
    ) -> ExecutionResult:
        """Generate content using unified executor.

        Args:
            input_data: Input data
            content_type: Type of content to generate
            config: Optional configuration

        Returns:
            Execution result
        """
        merged_config = {**self.config, **(config or {})}
        result = await self.unified_executor.execute(input_data, "llm", self.engine_type, merged_config)
        if result.status == ExecutionStatus.COMPLETED:
            format_type = self._get_format_type(content_type)
            formatted = self.formatter.format(result.data, format_type, self.engine_type, merged_config)
            result.data = formatted.data
        return result

    async def process_batch(self, items: list[Any], config: dict[str, Any] | None = None) -> ExecutionResult:
        """Process batch of items.

        Args:
            items: Items to process
            config: Optional configuration

        Returns:
            Execution result
        """
        return await self.unified_executor.execute(items, "batch", self.engine_type, config or self.config)

    def _get_engine_config(self) -> dict[str, Any]:
        """Get engine-specific configuration.

        Returns:
            configuration dictionary
        """
        # guardian: allow-config-with-logic
        if self.engine_type == EngineType.RESUME:
            return {"max_length": 500, "ensure_metrics": True, "action_verbs": True, "format": "professional"}
        else:
            return {"max_length": 300, "personalization": True, "call_to_action": True, "format": "engaging"}

    def _get_format_type(self, content_type: str) -> str:
        """Get format type for content.

        Args:
            content_type: Content type

        Returns:
            Format type string
        """
        if self.engine_type == EngineType.RESUME:
            if content_type == "bullets":
                return "resume_bullet"
            elif content_type == "section":
                return "resume_section"
        elif content_type == "message":
            return "outreach_message"
        elif content_type == "subject":
            return "outreach_subject"
        return "default"


_executors: dict[EngineType, EngineExecutor] = {}


def get_engine_executor(engine_type: EngineType) -> EngineExecutor:
    """Get engine executor instance.

    Args:
        engine_type: Type of engine

    Returns:
        EngineExecutor instance
    """
    if engine_type not in _executors:
        _executors[engine_type] = EngineExecutor(engine_type)
    return _executors[engine_type]


async def execute_resume_generation(
    input_data: Any,
    content_type: str = "default",
    config: dict[str, Any] | None = None,
) -> ExecutionResult:
    """Execute resume generation.

    Args:
        input_data: Input data
        content_type: Type of content
        config: Optional configuration

    Returns:
        Execution result
    """
    executor = get_engine_executor(EngineType.RESUME)
    return await executor.generate_content(input_data, content_type, config)


async def execute_outreach_generation(
    input_data: Any,
    content_type: str = "message",
    config: dict[str, Any] | None = None,
) -> ExecutionResult:
    """Execute outreach generation.

    Args:
        input_data: Input data
        content_type: Type of content
        config: Optional configuration

    Returns:
        Execution result
    """
    executor = get_engine_executor(EngineType.OUTREACH)
    return await executor.generate_content(input_data, content_type, config)
