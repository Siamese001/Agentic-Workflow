"""Central storage and query helpers for performance records."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

get_clock: Any = None

try:
    from agentic_core.L2_execution.utils.providers import (
        get_clock,
    )  # guardian: allow-layer-violation -- L6 observability module uses L2 execution type; intentional cross-layer instrumentation dependency
except ImportError:
    get_clock = None


class StageStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class BudgetClass(Enum):
    ROUTING = "routing"
    REASONING = "reasoning"
    ORCHESTRATION = "orchestration"
    EXECUTION = "execution"
    MUTATION = "mutation"
    POLICY_ENFORCEMENT = "policy_enforcement"
    HUMAN_ESCALATION = "human_escalation"
    UNKNOWN = "unknown"


class PerformanceMissingError(Exception):
    """Raised when a required performance record is missing."""


class BudgetViolationError(Exception):
    """Raised when a budgeted stage exceeds its configured latency budget."""


_BUDGET_LIMITS_MS = {
    BudgetClass.ROUTING: 10.0,
    BudgetClass.REASONING: 1000.0,
    BudgetClass.ORCHESTRATION: 50.0,
    BudgetClass.EXECUTION: 5000.0,
    BudgetClass.MUTATION: 100.0,
    BudgetClass.POLICY_ENFORCEMENT: 20.0,
    BudgetClass.HUMAN_ESCALATION: 300000.0,
    BudgetClass.UNKNOWN: float("inf"),
}


def _now_epoch() -> float:
    if get_clock is not None:
        try:
            return float(get_clock().now_epoch())
        except (
            AttributeError,
            RuntimeError,
            TypeError,
            ValueError,
        ):  # guardian: allow-silent-swallow  -- ADG-burn: silent_exception_swallow
            pass
    return time.time()


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(encoded).hexdigest()[:16]}"


@dataclass(frozen=True)
class PerformanceRecord:
    performance_record_id: str
    run_id: str
    trace_id: str
    stage_name: str
    stage_owner: str
    start_tick: float
    end_tick: float
    duration_ms: float
    status: str
    queue_depth: int | None
    concurrency_count: int | None
    resource_usage_hash: str | None
    budget_class: str | None
    within_budget_flag: bool | None
    record_epoch: float = field(default_factory=_now_epoch)

    @classmethod
    def create(
        cls,
        run_id: str,
        trace_id: str,
        stage_name: str,
        stage_owner: str,
        start_tick: float,
        end_tick: float,
        status: StageStatus,
        queue_depth: int | None = None,
        concurrency_count: int | None = None,
        resource_usage: Any = None,
        budget_class: BudgetClass | None = None,
    ) -> "PerformanceRecord":
        start = float(start_tick)
        end = float(end_tick)
        if end < start:
            raise PerformanceMissingError("end_tick must be greater than or equal to start_tick")
        duration_ms = round((end - start) * 1000.0, 6)
        resource_usage_hash = None
        if resource_usage is not None:
            resource_usage_hash = hashlib.sha256(
                json.dumps(resource_usage, sort_keys=True, default=str).encode("utf-8")
            ).hexdigest()[:16]
        within_budget_flag = None
        if budget_class is not None:
            within_budget_flag = duration_ms <= _BUDGET_LIMITS_MS.get(budget_class, float("inf"))
        record_payload = {
            "run_id": run_id,
            "trace_id": trace_id,
            "stage_name": stage_name,
            "stage_owner": stage_owner,
            "start_tick": start,
            "end_tick": end,
            "status": status.value,
            "queue_depth": queue_depth,
            "concurrency_count": concurrency_count,
            "budget_class": budget_class.value if budget_class else None,
        }
        return cls(
            performance_record_id=_stable_id("perf", record_payload),
            run_id=run_id,
            trace_id=trace_id,
            stage_name=stage_name,
            stage_owner=stage_owner,
            start_tick=start,
            end_tick=end,
            duration_ms=duration_ms,
            status=status.value,
            queue_depth=queue_depth,
            concurrency_count=concurrency_count,
            resource_usage_hash=resource_usage_hash,
            budget_class=budget_class.value if budget_class else None,
            within_budget_flag=within_budget_flag,
        )


class PerformanceRegistry:
    _instance: "PerformanceRegistry | None" = None
    _singleton_lock = threading.Lock()

    def __init__(self) -> None:
        self._records: dict[str, PerformanceRecord] = {}
        self._run_index: dict[str, list[str]] = {}
        self._trace_index: dict[str, list[str]] = {}
        self._stage_index: dict[str, list[str]] = {}
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> "PerformanceRegistry":
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_record(self, record: PerformanceRecord) -> PerformanceRecord:
        with self._lock:
            self._records[record.performance_record_id] = record
            self._run_index.setdefault(record.run_id, []).append(record.performance_record_id)
            self._trace_index.setdefault(record.trace_id, []).append(record.performance_record_id)
            self._stage_index.setdefault(record.stage_name, []).append(record.performance_record_id)
        return record

    def query_by_run_id(self, run_id: str) -> list[PerformanceRecord]:
        with self._lock:
            return [self._records[rid] for rid in self._run_index.get(run_id, []) if rid in self._records]

    def query_by_trace_id(self, trace_id: str) -> list[PerformanceRecord]:
        with self._lock:
            return [self._records[rid] for rid in self._trace_index.get(trace_id, []) if rid in self._records]

    def query_by_stage_name(self, stage_name: str) -> list[PerformanceRecord]:
        with self._lock:
            return [
                self._records[rid] for rid in self._stage_index.get(stage_name, []) if rid in self._records
            ]

    def query_by_record_id(self, record_id: str) -> PerformanceRecord | None:
        with self._lock:
            return self._records.get(record_id)

    def get_stage_coverage(self, run_id: str = "") -> dict[str, int]:
        with self._lock:
            records = self.query_by_run_id(run_id) if run_id else list(self._records.values())
        coverage: dict[str, int] = {}
        for record in records:
            coverage[record.stage_name] = coverage.get(record.stage_name, 0) + 1
        return coverage

    def get_performance_count(self, run_id: str = "") -> int:
        with self._lock:
            if run_id:
                return len(self._run_index.get(run_id, []))
            return len(self._records)

    def verify_record_exists(self, record_id: str) -> bool:
        return self.query_by_record_id(record_id) is not None

    def verify_duration_present(self, record_id: str) -> bool:
        record = self.query_by_record_id(record_id)
        return record is not None and record.duration_ms >= 0.0

    def verify_stage_metadata(self, record_id: str) -> bool:
        record = self.query_by_record_id(record_id)
        return record is not None and bool(record.stage_name) and bool(record.stage_owner)

    def verify_budget_tracking(self, record_id: str) -> bool:
        record = self.query_by_record_id(record_id)
        return record is not None and (record.budget_class is None or record.within_budget_flag is not None)


def get_performance_registry() -> PerformanceRegistry:
    return PerformanceRegistry.get_instance()


def reset_performance_registry() -> None:
    with PerformanceRegistry._singleton_lock:
        PerformanceRegistry._instance = None


__all__ = [
    "PerformanceRecord",
    "PerformanceRegistry",
    "StageStatus",
    "BudgetClass",
    "PerformanceMissingError",
    "BudgetViolationError",
    "get_performance_registry",
    "reset_performance_registry",
]
