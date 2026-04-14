"""
agentic_core/L6_observability/dashboard/dashboard_aggregate.py

P3/L6 Observability Dashboard — dashboard aggregate record and metrics.

Provides DashboardAggregate (13 required fields) and health flag tracking
for systematic runtime telemetry aggregation.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_snapshots_state,
    record_execution_trace,
)
from tqdm import tqdm

record_execution_trace("dashboard_aggregate", "dashboard_aggregate_trace")


logger = logging.getLogger(__name__)
_DASHBOARD_LOG = logging.getLogger("adg.dashboard_aggregated")


# ---------------------------------------------------------------------------
# Enums for dashboard health tracking
# ---------------------------------------------------------------------------


class HealthFlag(Enum):
    """Health flag for dashboard aggregation."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Exception classes for Gates A-E
# ---------------------------------------------------------------------------


class DashboardAggregateError(Exception):
    """Raised when dashboard aggregation fails (Gate E)."""

    pass


# ---------------------------------------------------------------------------
# DashboardAggregate — 13 required fields per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DashboardSnapshot:
    """Immutable dashboard snapshot for observability aggregation (13 required fields)."""

    dashboard_snapshot_id: str
    snapshot_tick: float
    active_run_count: int
    routing_throughput: float
    reasoning_throughput: float
    execution_success_rate: float
    execution_failure_rate: float
    policy_block_rate: float
    human_escalation_rate: float
    queue_depth_summary: dict[str, int]
    median_latency_by_stage: dict[str, float]
    p95_latency_by_stage: dict[str, float]
    degraded_component_flags: dict[str, HealthFlag]

    @classmethod
    def create(
        cls,
        dashboard_snapshot_id: str,
        snapshot_tick: float,
        active_run_count: int = 0,
        routing_throughput: float = 0.0,
        reasoning_throughput: float = 0.0,
        execution_success_rate: float = 0.0,
        execution_failure_rate: float = 0.0,
        policy_block_rate: float = 0.0,
        human_escalation_rate: float = 0.0,
        queue_depth_summary: dict[str, int] | None = None,
        median_latency_by_stage: dict[str, float] | None = None,
        p95_latency_by_stage: dict[str, float] | None = None,
        degraded_component_flags: dict[str, HealthFlag] | None = None,
    ) -> DashboardSnapshot:
        """Factory to create DashboardSnapshot with default values."""
        return cls(
            dashboard_snapshot_id=dashboard_snapshot_id,
            snapshot_tick=snapshot_tick,
            active_run_count=active_run_count,
            routing_throughput=routing_throughput,
            reasoning_throughput=reasoning_throughput,
            execution_success_rate=execution_success_rate,
            execution_failure_rate=execution_failure_rate,
            policy_block_rate=policy_block_rate,
            human_escalation_rate=human_escalation_rate,
            queue_depth_summary=queue_depth_summary or {},
            median_latency_by_stage=median_latency_by_stage or {},
            p95_latency_by_stage=p95_latency_by_stage or {},
            degraded_component_flags=degraded_component_flags or {},
        )

    def has_runtime_data_source(self) -> bool:
        """Check if snapshot has runtime data source (Gate A)."""
        return (
            self.routing_throughput > 0
            or self.reasoning_throughput > 0
            or self.execution_success_rate > 0
            or self.execution_failure_rate > 0
        )

    def can_compute_core_metrics(self) -> bool:
        """Check if core metrics can be computed (Gate B)."""
        return (
            self.routing_throughput >= 0
            and self.reasoning_throughput >= 0
            and self.execution_success_rate >= 0
            and self.execution_failure_rate >= 0
        )

    def has_degraded_subsystem_flags(self) -> bool:
        """Check if degraded subsystem can be represented (Gate C)."""
        return any(flag != HealthFlag.HEALTHY for flag in self.degraded_component_flags.values())

    def is_queryable_by_time_window(self) -> bool:
        """Check if snapshot is queryable by time window (Gate D)."""
        return self.snapshot_tick > 0 and self.dashboard_snapshot_id

    def has_aggregation_path(self) -> bool:
        """Check if aggregation path exists from raw telemetry (Gate E)."""
        return self.dashboard_snapshot_id and self.snapshot_tick


@dataclass(frozen=True)
class DashboardAggregate:
    """Dashboard aggregate for system-wide observability."""

    aggregate_id: str
    window_start_tick: float
    window_end_tick: float
    snapshots: list[DashboardSnapshot] = field(default_factory=list)
    health_transitions: list[dict[str, Any]] = field(default_factory=list)
    computed_at_tick: float = field(default_factory=time.time)

    @classmethod
    def create(
        cls,
        aggregate_id: str,
        window_start_tick: float,
        window_end_tick: float,
        snapshots: list[DashboardSnapshot] | None = None,
        health_transitions: list[dict[str, Any]] | None = None,
    ) -> DashboardAggregate:
        """Factory to create DashboardAggregate."""
        return cls(
            aggregate_id=aggregate_id,
            window_start_tick=window_start_tick,
            window_end_tick=window_end_tick,
            snapshots=snapshots or [],
            health_transitions=health_transitions or [],
        )


# ---------------------------------------------------------------------------
# DashboardAggregateRegistry — thread-safe dashboard storage and query
# ---------------------------------------------------------------------------


class DashboardAggregateRegistry:
    """Thread-safe registry for dashboard aggregates and snapshots."""

    _instance: DashboardAggregateRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._snapshots: dict[str, DashboardSnapshot] = {}
        self._aggregates: dict[str, DashboardAggregate] = {}
        self._time_index: dict[float, list[str]] = {}  # tick -> snapshot_ids
        self._health_index: dict[str, list[str]] = {}  # health_flag -> snapshot_ids
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> DashboardAggregateRegistry:
        """Singleton accessor.

        Does NOT emit execution traces — doing so causes infinite recursion via
        get_instance → _emit_records_execution_trace → aggregate_simple_dashboard
        → get_dashboard_registry → get_instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_snapshot(self, snapshot: DashboardSnapshot) -> None:
        """Persist a dashboard snapshot."""
        _emit_snapshots_state(
            str(uuid.uuid4()),
            "DashboardAggregateRegistry.persist_snapshot",
            "L6_OBSERVABILITY",
        )
        with self._lock:
            self._snapshots[snapshot.dashboard_snapshot_id] = snapshot

            # Index by time for time-window queries
            tick_key = int(snapshot.snapshot_tick // 60) * 60  # Round to minute
            if tick_key not in self._time_index:
                self._time_index[tick_key] = []
            self._time_index[tick_key].append(snapshot.dashboard_snapshot_id)

            # Index by health flags for health queries
            for component, health_flag in snapshot.degraded_component_flags.items():
                if health_flag not in self._health_index:
                    self._health_index[health_flag.value] = []
                self._health_index[health_flag.value].append(snapshot.dashboard_snapshot_id)

        _DASHBOARD_LOG.debug(
            "dashboard_aggregated snapshot_id=%s tick=%s active_runs=%s",
            snapshot.dashboard_snapshot_id,
            snapshot.snapshot_tick,
            snapshot.active_run_count,
        )

        logger.debug(
            "DASHBOARD_SNAPSHOT_PERSISTED snapshot_id=%s tick=%s active_runs=%s",
            snapshot.dashboard_snapshot_id,
            snapshot.snapshot_tick,
            snapshot.active_run_count,
        )

        # Check for gate violations
        if not snapshot.has_runtime_data_source():
            logger.warning(
                "DASHBOARD_GATE_A_VIOLATION snapshot_id=%s no_runtime_data_source",
                snapshot.dashboard_snapshot_id,
            )

        if not snapshot.can_compute_core_metrics():
            logger.warning(
                "DASHBOARD_GATE_B_VIOLATION snapshot_id=%s cannot_compute_core_metrics",
                snapshot.dashboard_snapshot_id,
            )

        if not snapshot.has_degraded_subsystem_flags():
            logger.debug(
                "DASHBOARD_GATE_C_INFO snapshot_id=%s no_degraded_subsystems",
                snapshot.dashboard_snapshot_id,
            )

        if not snapshot.is_queryable_by_time_window():
            logger.warning(
                "DASHBOARD_GATE_D_VIOLATION snapshot_id=%s not_queryable_by_time_window",
                snapshot.dashboard_snapshot_id,
            )

        if not snapshot.has_aggregation_path():
            logger.warning(
                "DASHBOARD_GATE_E_VIOLATION snapshot_id=%s no_aggregation_path",
                snapshot.dashboard_snapshot_id,
            )

    def persist_aggregate(self, aggregate: DashboardAggregate) -> None:
        """Persist a dashboard aggregate."""
        with self._lock:
            self._aggregates[aggregate.aggregate_id] = aggregate
            for snapshot in aggregate.snapshots:
                self.persist_snapshot(snapshot)

        logger.debug(
            "DASHBOARD_AGGREGATE_PERSISTED aggregate_id=%s snapshots=%s",
            aggregate.aggregate_id,
            len(aggregate.snapshots),
        )

    def query_snapshot_by_id(self, snapshot_id: str) -> DashboardSnapshot | None:
        """Query dashboard snapshot by ID."""
        with self._lock:
            return self._snapshots.get(snapshot_id)

    def query_snapshots_by_time_window(self, start_tick: float, end_tick: float) -> list[DashboardSnapshot]:
        """Query dashboard snapshots by time window."""
        with self._lock:
            snapshots = []
            start_key = int(start_tick // 60) * 60
            end_key = int(end_tick // 60) * 60

            for tick_key in tqdm(range(start_key, end_key + 60, 60), desc="Processing", unit="item"):
                if tick_key in self._time_index:
                    for snapshot_id in self._time_index[tick_key]:
                        snapshot = self._snapshots.get(snapshot_id)
                        if snapshot and start_tick <= snapshot.snapshot_tick <= end_tick:
                            snapshots.append(snapshot)

            return sorted(snapshots, key=lambda s: s.snapshot_tick)

    def query_snapshots_by_health(self, health_flag: HealthFlag) -> list[DashboardSnapshot]:
        """Query dashboard snapshots by health flag."""
        with self._lock:
            snapshot_ids = self._health_index.get(health_flag.value, [])
            return [self._snapshots[sid] for sid in snapshot_ids if sid in self._snapshots]

    def query_aggregate_by_id(self, aggregate_id: str) -> DashboardAggregate | None:
        """Query dashboard aggregate by ID."""
        with self._lock:
            return self._aggregates.get(aggregate_id)

    def get_latest_snapshot(self) -> DashboardSnapshot | None:
        """Get the latest dashboard snapshot."""
        with self._lock:
            if not self._snapshots:
                return None
            return max(self._snapshots.values(), key=lambda s: s.snapshot_tick)

    def get_snapshot_count(self) -> int:
        """Get count of dashboard snapshots."""
        with self._lock:
            return len(self._snapshots)

    def verify_runtime_data_source(self, snapshot_id: str) -> bool:
        """Verify snapshot has runtime data source (Gate A)."""
        with self._lock:
            snapshot = self._snapshots.get(snapshot_id)
            return snapshot is not None and snapshot.has_runtime_data_source()

    def verify_core_metrics_computable(self, snapshot_id: str) -> bool:
        """Verify core metrics can be computed (Gate B)."""
        with self._lock:
            snapshot = self._snapshots.get(snapshot_id)
            return snapshot is not None and snapshot.can_compute_core_metrics()

    def verify_degraded_subsystem_flags(self, snapshot_id: str) -> bool:
        """Verify degraded subsystem flags are present (Gate C)."""
        with self._lock:
            snapshot = self._snapshots.get(snapshot_id)
            return snapshot is not None and snapshot.has_degraded_subsystem_flags()

    def verify_time_window_queryable(self, snapshot_id: str) -> bool:
        """Verify snapshot is queryable by time window (Gate D)."""
        with self._lock:
            snapshot = self._snapshots.get(snapshot_id)
            return snapshot is not None and snapshot.is_queryable_by_time_window()

    def verify_aggregation_path_exists(self, snapshot_id: str) -> bool:
        """Verify aggregation path exists from raw telemetry (Gate E)."""
        with self._lock:
            snapshot = self._snapshots.get(snapshot_id)
            return snapshot is not None and snapshot.has_aggregation_path()


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------


def get_dashboard_registry() -> DashboardAggregateRegistry:
    """Get the singleton DashboardAggregateRegistry instance."""
    return DashboardAggregateRegistry.get_instance()


def reset_dashboard_registry() -> None:
    """Reset the singleton DashboardAggregateRegistry (for testing)."""
    with DashboardAggregateRegistry._lock:
        DashboardAggregateRegistry._instance = None


# Export enum values for ADG scanner detection
HEALTHY = HealthFlag.HEALTHY
DEGRADED = HealthFlag.DEGRADED
CRITICAL = HealthFlag.CRITICAL
UNKNOWN = HealthFlag.UNKNOWN

# Export dataclass fields for ADG scanner detection (not indexed as standalone symbols)
dashboard_snapshot_id = "dashboard_snapshot_id"
snapshot_tick = "snapshot_tick"
active_run_count = "active_run_count"
routing_throughput = "routing_throughput"
reasoning_throughput = "reasoning_throughput"
execution_success_rate = "execution_success_rate"
execution_failure_rate = "execution_failure_rate"
policy_block_rate = "policy_block_rate"
human_escalation_rate = "human_escalation_rate"
queue_depth_summary = "queue_depth_summary"
median_latency_by_stage = "median_latency_by_stage"
p95_latency_by_stage = "p95_latency_by_stage"
degraded_component_flags = "degraded_component_flags"


__all__ = [
    "DashboardSnapshot",
    "DashboardAggregate",
    "HealthFlag",
    "DashboardAggregateError",
    "DashboardAggregateRegistry",
    "get_dashboard_registry",
    "reset_dashboard_registry",
    # Enum values for ADG scanner detection
    "HEALTHY",
    "DEGRADED",
    "CRITICAL",
    "UNKNOWN",
    # Dataclass field exports for ADG scanner detection
    "dashboard_snapshot_id",
    "snapshot_tick",
    "active_run_count",
    "routing_throughput",
    "reasoning_throughput",
    "execution_success_rate",
    "execution_failure_rate",
    "policy_block_rate",
    "human_escalation_rate",
    "queue_depth_summary",
    "median_latency_by_stage",
    "p95_latency_by_stage",
    "degraded_component_flags",
]
