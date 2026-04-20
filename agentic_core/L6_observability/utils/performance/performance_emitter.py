"""Performance emission helpers for runtime stages."""

from __future__ import annotations

import contextlib
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterator

from agentic_core.L6_observability.utils.performance.performance_registry import (
    BudgetClass,
    BudgetViolationError,
    PerformanceMissingError,
    PerformanceRecord,
    PerformanceRegistry,
    StageStatus,
    get_performance_registry,
)

logger = logging.getLogger(__name__)


def performance_record_emitted(
    record_id: str,
    run_id: str,
    trace_id: str,
    stage: str,
    owner: str,
    duration_ms: float,
    status: str,
    budget: str,
    within_budget: bool,
) -> None:
    logger.debug(
        "performance_record_emitted record_id=%s run_id=%s trace_id=%s stage=%s owner=%s duration_ms=%s status=%s budget=%s within_budget=%s",
        record_id,
        run_id,
        trace_id,
        stage,
        owner,
        duration_ms,
        status,
        budget,
        within_budget,
    )


@dataclass(frozen=True)
class PerformanceContext:
    run_id: str
    trace_id: str
    queue_depth: int | None = None
    concurrency_count: int | None = None
    resource_usage: Any = None

    @classmethod
    def create(
        cls,
        run_id: str,
        trace_id: str,
        queue_depth: int | None = None,
        concurrency_count: int | None = None,
        resource_usage: Any = None,
    ) -> "PerformanceContext":
        return cls(
            run_id=run_id,
            trace_id=trace_id,
            queue_depth=queue_depth,
            concurrency_count=concurrency_count,
            resource_usage=resource_usage,
        )


class StageOwner(Enum):
    ROUTER = "router"
    REASONING_ENGINE = "reasoning_engine"
    ORCHESTRATOR = "orchestrator"
    EXECUTOR = "executor"
    STATE_AUTHORITY = "state_authority"
    POLICY_ENFORCER = "policy_enforcer"
    HUMAN_REVIEWER = "human_reviewer"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class LatencyBudget:
    budget_class: BudgetClass
    warn_threshold_ms: float
    error_threshold_ms: float

    @classmethod
    def for_stage(cls, stage_name: str) -> "LatencyBudget":
        stage_lower = (stage_name or "").lower()
        if "routing" in stage_lower or "route" in stage_lower:
            return cls(BudgetClass.ROUTING, 5.0, 10.0)
        if "reasoning" in stage_lower:
            return cls(BudgetClass.REASONING, 500.0, 1000.0)
        if "orchestrat" in stage_lower or "handoff" in stage_lower:
            return cls(BudgetClass.ORCHESTRATION, 25.0, 50.0)
        if "execution" in stage_lower or "tool" in stage_lower:
            return cls(BudgetClass.EXECUTION, 2500.0, 5000.0)
        if "mutation" in stage_lower or "commit" in stage_lower or "write" in stage_lower:
            return cls(BudgetClass.MUTATION, 50.0, 100.0)
        if "policy" in stage_lower or "guardrail" in stage_lower:
            return cls(BudgetClass.POLICY_ENFORCEMENT, 10.0, 20.0)
        if "human" in stage_lower or "escalat" in stage_lower:
            return cls(BudgetClass.HUMAN_ESCALATION, 150000.0, 300000.0)
        return cls(BudgetClass.UNKNOWN, float("inf"), float("inf"))


def _normalize_status(status: StageStatus | str) -> StageStatus:
    if isinstance(status, StageStatus):
        return status
    try:
        return StageStatus(str(status).lower())
    except ValueError:
        return StageStatus.ERROR


def _normalize_owner(stage_owner: StageOwner | str) -> str:
    if isinstance(stage_owner, StageOwner):
        return stage_owner.value
    return str(stage_owner or StageOwner.UNKNOWN.value)


def record_stage_performance(
    performance_context: PerformanceContext,
    stage_name: str,
    stage_owner: StageOwner | str,
    start_tick: float,
    end_tick: float,
    status: StageStatus | str,
    *,
    registry: PerformanceRegistry | None = None,
) -> PerformanceRecord:
    if end_tick < start_tick:
        raise PerformanceMissingError("record_stage_performance: end_tick must be >= start_tick")
    if not performance_context.trace_id:
        raise PerformanceMissingError("record_stage_performance: trace_id is required")
    if not performance_context.run_id:
        raise PerformanceMissingError("record_stage_performance: run_id is required")
    if not stage_name:
        raise PerformanceMissingError("record_stage_performance: stage_name is required")

    registry = registry or get_performance_registry()
    normalized_status = _normalize_status(status)
    budget = LatencyBudget.for_stage(stage_name)
    record = PerformanceRecord.create(
        run_id=performance_context.run_id,
        trace_id=performance_context.trace_id,
        stage_name=stage_name,
        stage_owner=_normalize_owner(stage_owner),
        start_tick=start_tick,
        end_tick=end_tick,
        status=normalized_status,
        queue_depth=performance_context.queue_depth,
        concurrency_count=performance_context.concurrency_count,
        resource_usage=performance_context.resource_usage,
        budget_class=budget.budget_class,
    )
    registry.persist_record(record)
    performance_record_emitted(
        record.performance_record_id,
        record.run_id,
        record.trace_id,
        record.stage_name,
        record.stage_owner,
        record.duration_ms,
        record.status,
        record.budget_class or BudgetClass.UNKNOWN.value,
        bool(record.within_budget_flag),
    )
    if record.duration_ms > budget.error_threshold_ms:
        raise BudgetViolationError(
            f"Stage {stage_name!r} exceeded latency budget: {record.duration_ms:.3f}ms > {budget.error_threshold_ms:.3f}ms"
        )
    return record


def query_performance_records(
    *,
    run_id: str | None = None,
    trace_id: str | None = None,
    stage_name: str | None = None,
    record_id: str | None = None,
    registry: PerformanceRegistry | None = None,
) -> list[PerformanceRecord]:
    registry = registry or get_performance_registry()
    if record_id:
        record = registry.query_by_record_id(record_id)
        return [record] if record is not None else []
    if run_id:
        return registry.query_by_run_id(run_id)
    if trace_id:
        return registry.query_by_trace_id(trace_id)
    if stage_name:
        return registry.query_by_stage_name(stage_name)
    return list(getattr(registry, "_records", {}).values())


@contextlib.contextmanager
def measure_stage_timing(
    performance_context: PerformanceContext,
    stage_name: str,
    stage_owner: StageOwner | str,
    *,
    registry: PerformanceRegistry | None = None,
) -> Iterator[float]:
    start_tick = time.time()
    status = StageStatus.SUCCESS
    try:
        yield start_tick
    except (RuntimeError, TypeError, ValueError):
        status = StageStatus.ERROR
        raise
    finally:
        end_tick = time.time()
        try:
            record_stage_performance(
                performance_context=performance_context,
                stage_name=stage_name,
                stage_owner=stage_owner,
                start_tick=start_tick,
                end_tick=end_tick,
                status=status,
                registry=registry,
            )
        except (AttributeError, RuntimeError, TypeError, ValueError) as perf_exc:  # guardian: allow-log-and-swallow -- performance recording: non-fatal, logger.error already called
            logger.error("PERFORMANCE_RECORDING_FAILED stage=%s error=%s", stage_name, perf_exc)


def record_routing_performance(
    run_id: str,
    trace_id: str,
    start_tick: float,
    end_tick: float,
    status: StageStatus | str = StageStatus.SUCCESS,
    queue_depth: int | None = None,
) -> PerformanceRecord:
    return record_stage_performance(
        performance_context=PerformanceContext.create(
            run_id=run_id, trace_id=trace_id, queue_depth=queue_depth
        ),
        stage_name="routing",
        stage_owner=StageOwner.ROUTER,
        start_tick=start_tick,
        end_tick=end_tick,
        status=status,
    )


def record_reasoning_performance(
    run_id: str,
    trace_id: str,
    start_tick: float,
    end_tick: float,
    status: StageStatus | str = StageStatus.SUCCESS,
    concurrency_count: int | None = None,
) -> PerformanceRecord:
    return record_stage_performance(
        performance_context=PerformanceContext.create(
            run_id=run_id,
            trace_id=trace_id,
            concurrency_count=concurrency_count,
        ),
        stage_name="reasoning",
        stage_owner=StageOwner.REASONING_ENGINE,
        start_tick=start_tick,
        end_tick=end_tick,
        status=status,
    )


def record_execution_performance(
    run_id: str,
    trace_id: str,
    tool_name: str,
    start_tick: float,
    end_tick: float,
    status: StageStatus | str = StageStatus.SUCCESS,
    resource_usage: Any = None,
) -> PerformanceRecord:
    return record_stage_performance(
        performance_context=PerformanceContext.create(
            run_id=run_id,
            trace_id=trace_id,
            resource_usage=resource_usage,
        ),
        stage_name=f"execution_{tool_name}",
        stage_owner=StageOwner.EXECUTOR,
        start_tick=start_tick,
        end_tick=end_tick,
        status=status,
    )


__all__ = [
    "PerformanceContext",
    "StageOwner",
    "LatencyBudget",
    "record_stage_performance",
    "query_performance_records",
    "measure_stage_timing",
    "record_routing_performance",
    "record_reasoning_performance",
    "record_execution_performance",
    "performance_record_emitted",
]
