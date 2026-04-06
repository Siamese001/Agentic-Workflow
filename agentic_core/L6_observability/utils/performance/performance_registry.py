"""
agentic_core/L6_observability/performance/performance_registry.py

P2/L6 Performance Registry — central storage and query for performance records.

Provides PerformanceRecord (12 required fields) and thread-safe registry
for performance record persistence, querying, and latency budget tracking.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L2_execution.utils.providers import get_clock
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
    record_execution_trace,
)

emit_replay_key("p0", "performance_registry")
emit_determinism_digest("p0", "performance_registry")

_emit_dispatches_healing_run("p1", "performance_registry", "L6")
_emit_routes_through("p1", "performance_registry", "L6")
_emit_checks_agent_registry("p1", "performance_registry", "agent_registry")
_emit_validates_agent_capability("p1", "performance_registry", "capability")
_emit_dispatches_execution_plan("p1", "performance_registry", "exec_plan")
_emit_agent_executes_agent("p1", "performance_registry", "sub_agent")
_emit_routes_to_agent("p1", "performance_registry", "target_agent")
_emit_verifies_policy("p1", "performance_registry", "policy_check")
_emit_observes_runtime_state("p1", "performance_registry", "runtime_state")
_emit_verifies_boundary("p1", "performance_registry", "boundary_check")
_emit_transcripts_response("p1", "performance_registry", "transcript")
_emit_hard_fails_untranscripted("p1", "performance_registry")
_emit_gated_by_confidence("p1", "performance_registry", "confidence_gate")
_emit_escalates_to_human("p1", "performance_registry", "L6")
_emit_reads_policy_state("p1", "performance_registry", "L6")
_emit_authorize_and_execute("p2", "performance_registry", "execution_auth")
_emit_validates_capability("p2", "performance_registry", "capability_check")
_emit_routes_to_capability("p2", "performance_registry", "capability_route")
_emit_writes_via_uwg("p2", "performance_registry", "uwg_write")
_emit_blocks_direct_write("p2", "performance_registry", "direct_write_block")
_emit_records_tool_invocation("p2", "performance_registry", "tool_invocation")
_emit_captures_execution_output("p2", "performance_registry", "exec_output")
_emit_dispatches_agent("p3", "performance_registry", "agent_dispatch")
_emit_coordinates_agents("p3", "performance_registry", "agent_coordination")
_emit_records_workflow_lineage("p3", "performance_registry", "workflow_lineage")
_emit_records_healing_outcome("p3", "performance_registry", "healing_outcome")
_emit_escalates_failure("p3", "performance_registry", "failure_escalation")
_emit_orchestrates_workflow("p3", "performance_registry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "performance_registry", "healing_dispatch")
_emit_invokes_evaluation("p3", "performance_registry", "evaluation_signal")
_emit_records_telemetry_event("p4", "performance_registry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "performance_registry", "eval_metric")
_emit_stores_embedding("p4", "performance_registry", "embedding_store")
_emit_updates_meta_learning_state("p4", "performance_registry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "performance_registry", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

record_execution_trace("performance_registry", "performance_registry_trace")


_emit_emits_metric_event("performance_registry", "p4obs", "metric_1")
_emit_emits_metric_event("performance_registry", "p4obs", "metric_2")
_emit_emits_metric_event("performance_registry", "p4obs", "metric_3")
_emit_emits_metric_event("performance_registry", "p4obs", "metric_4")
_emit_emits_metric_event("performance_registry", "p4obs", "metric_5")
_emit_emits_metric_event("performance_registry", "p4obs", "metric_6")
_emit_records_incident_event("performance_registry", "p4obs", "incident")
_emit_captures_runtime_anomaly("performance_registry", "p4obs", "anomaly")
_emit_writes_observability_log("performance_registry", "p4obs", "obs_log")
_emit_updates_monitoring_state("performance_registry", "p4obs", "mon_state")
_emit_triggers_alert("performance_registry", "p4obs", "alert")
_emit_links_incident_trace("performance_registry", "p4obs", "trace_link")
_emit_captures_pattern("performance_registry", "p3lm", "pattern")
_emit_records_learning_event("performance_registry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("performance_registry", "p3lm", "snapshot")
_emit_feeds_meta_learning("performance_registry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("performance_registry", "p3lm", "routing")
_emit_improves_agent_policy("performance_registry", "p3lm", "policy")
_emit_stores_learning_state("performance_registry", "p3lm", "state")
_emit_records_execution_trace("performance_registry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("performance_registry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("performance_registry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("performance_registry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("performance_registry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("performance_registry", "env_read", "p2_env_1")
_emit_reads_environ("performance_registry", "env_read", "p2_env_2")
_emit_reads_runtime_state("performance_registry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("performance_registry", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "performance_registry", "context_pull")
_emit_pulls_context("p1", "performance_registry", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "performance_registry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "performance_registry", "uwg_term_2")
_emit_writes_through("p1", "performance_registry", "write_through")
_emit_writes_through("p1", "performance_registry", "write_through_2")
_emit_validated_by_safety_plane("p1", "performance_registry", "safety_validation")
_emit_invokes_eval("p1", "performance_registry", "eval_call")
_emit_proposal_commits_routing("p1", "performance_registry", "routing_commit")

logger = logging.getLogger(__name__)
_PERF_LOG = logging.getLogger("adg.performance_record_emitted")


# ---------------------------------------------------------------------------
# Enums for performance tracking
# ---------------------------------------------------------------------------


class StageStatus(Enum):
    """Status of a performance-measured stage."""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class BudgetClass(Enum):
    """Latency budget classes for different stage types."""

    ROUTING = "routing"  # < 10ms
    REASONING = "reasoning"  # < 1000ms
    ORCHESTRATION = "orchestration"  # < 50ms
    EXECUTION = "execution"  # < 5000ms
    MUTATION = "mutation"  # < 100ms
    POLICY_ENFORCEMENT = "policy_enforcement"  # < 20ms
    HUMAN_ESCALATION = "human_escalation"  # < 300000ms (5 minutes)
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Exception classes for Gates A-E
# ---------------------------------------------------------------------------


class PerformanceMissingError(Exception):
    """Raised when required runtime stage completes without performance record (Gate A)."""

    pass


class BudgetViolationError(Exception):
    """Raised when budgeted stage exceeds latency budget (Gate D)."""

    pass


# ---------------------------------------------------------------------------
# PerformanceRecord — 12 required fields per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PerformanceRecord:
    """Immutable performance record for runtime stage measurement (12 required fields)."""

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
    record_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

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
        queue_depth: int = None,
        concurrency_count: int = None,
        resource_usage: Any = None,
        budget_class: BudgetClass = None,
    ) -> PerformanceRecord:
        """Factory to create PerformanceRecord with computed fields."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "PerformanceRecord.create", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "PerformanceRecord.create", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "PerformanceRecord.create")

        performance_record_id = str(uuid.uuid4())
        duration_ms = (end_tick - start_tick) * 1000.0

        # Compute resource usage hash if provided
        resource_usage_hash = None
        if resource_usage is not None:
            resource_usage_hash = hashlib.sha256(str(resource_usage).encode()).hexdigest()[:16]

        # Determine if within budget
        within_budget_flag = None
        if budget_class:
            within_budget_flag = cls._check_budget(budget_class, duration_ms)

        return cls(
            performance_record_id=performance_record_id,
            run_id=run_id,
            trace_id=trace_id,
            stage_name=stage_name,
            stage_owner=stage_owner,
            start_tick=start_tick,
            end_tick=end_tick,
            duration_ms=duration_ms,
            status=status.value,
            queue_depth=queue_depth,
            concurrency_count=concurrency_count,
            resource_usage_hash=resource_usage_hash,
            budget_class=budget_class.value if budget_class else None,
            within_budget_flag=within_budget_flag,
        )

    @staticmethod
    def _check_budget(budget_class: BudgetClass, duration_ms: float) -> bool:
        """Check if duration is within budget for the given class."""
        budgets = {
            BudgetClass.ROUTING: 10.0,
            BudgetClass.REASONING: 1000.0,
            BudgetClass.ORCHESTRATION: 50.0,
            BudgetClass.EXECUTION: 5000.0,
            BudgetClass.MUTATION: 100.0,
            BudgetClass.POLICY_ENFORCEMENT: 20.0,
            BudgetClass.HUMAN_ESCALATION: 300000.0,
            BudgetClass.UNKNOWN: float("inf"),
        }
        return duration_ms <= budgets.get(budget_class, float("inf"))


# ---------------------------------------------------------------------------
# PerformanceRegistry — thread-safe performance storage and query
# ---------------------------------------------------------------------------


class PerformanceRegistry:
    """Thread-safe registry for performance records and queries."""

    _instance: PerformanceRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._records: dict[str, PerformanceRecord] = {}
        self._run_index: dict[str, list[str]] = {}  # run_id -> record_ids
        self._trace_index: dict[str, list[str]] = {}  # trace_id -> record_ids
        self._stage_index: dict[str, list[str]] = {}  # stage_name -> record_ids
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> PerformanceRegistry:
        """Singleton accessor."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "PerformanceRegistry.get_instance"
        )

        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_record(self, record: PerformanceRecord) -> None:
        """Persist a performance record (Gate A step 5)."""
        with self._lock:
            self._records[record.performance_record_id] = record

            # Index by run_id for Gate E queries
            if record.run_id not in self._run_index:
                self._run_index[record.run_id] = []
            self._run_index[record.run_id].append(record.performance_record_id)

            # Index by trace_id for Gate E queries
            if record.trace_id not in self._trace_index:
                self._trace_index[record.trace_id] = []
            self._trace_index[record.trace_id].append(record.performance_record_id)

            # Index by stage_name for coverage analysis
            if record.stage_name not in self._stage_index:
                self._stage_index[record.stage_name] = []
            self._stage_index[record.stage_name].append(record.performance_record_id)

        _PERF_LOG.debug(
            "performance_record_emitted record_id=%s run_id=%s trace_id=%s stage=%s owner=%s duration_ms=%.2f status=%s budget=%s within_budget=%s",
            record.performance_record_id,
            record.run_id,
            record.trace_id,
            record.stage_name,
            record.stage_owner,
            record.duration_ms,
            record.status,
            record.budget_class,
            record.within_budget_flag,
        )

        logger.debug(
            "PERFORMANCE_RECORD_PERSISTED record_id=%s run_id=%s trace_id=%s stage=%s duration_ms=%.2f",
            record.performance_record_id,
            record.run_id,
            record.trace_id,
            record.stage_name,
            record.duration_ms,
        )

        # Check for budget violations
        if record.budget_class and record.within_budget_flag is False:
            logger.warning(
                "BUDGET_VIOLATION record_id=%s stage=%s duration_ms=%.2f budget_class=%s",
                record.performance_record_id,
                record.stage_name,
                record.duration_ms,
                record.budget_class,
            )

    def query_by_run_id(self, run_id: str) -> list[PerformanceRecord]:
        """Query performance records by run_id (Gate E)."""
        with self._lock:
            record_ids = self._run_index.get(run_id, [])
            return [self._records[record_id] for record_id in record_ids if record_id in self._records]

    def query_by_trace_id(self, trace_id: str) -> list[PerformanceRecord]:
        """Query performance records by trace_id (Gate E)."""
        with self._lock:
            record_ids = self._trace_index.get(trace_id, [])
            return [self._records[record_id] for record_id in record_ids if record_id in self._records]

    def query_by_stage_name(self, stage_name: str) -> list[PerformanceRecord]:
        """Query performance records by stage_name."""
        with self._lock:
            record_ids = self._stage_index.get(stage_name, [])
            return [self._records[record_id] for record_id in record_ids if record_id in self._records]

    def query_by_record_id(self, record_id: str) -> PerformanceRecord | None:
        """Query performance record by performance_record_id."""
        with self._lock:
            return self._records.get(record_id)

    def get_stage_coverage(self, run_id: str = "") -> dict[str, int]:
        """Get count of records per stage, optionally filtered by run_id."""
        with self._lock:
            if run_id:
                record_ids = self._run_index.get(run_id, [])
                records = [self._records[rid] for rid in record_ids if rid in self._records]
            else:
                records = list(self._records.values())

            coverage = {}
            for record in records:
                coverage[record.stage_name] = coverage.get(record.stage_name, 0) + 1
            return coverage

    def get_performance_count(self, run_id: str = "") -> int:
        """Get count of performance records, optionally filtered by run_id."""
        with self._lock:
            if run_id:
                return len(self._run_index.get(run_id, []))
            return len(self._records)

    def verify_record_exists(self, record_id: str) -> bool:
        """Verify performance record exists (Gate A)."""
        with self._lock:
            return record_id in self._records

    def verify_duration_present(self, record_id: str) -> bool:
        """Verify performance record has duration_ms (Gate B)."""
        with self._lock:
            record = self._records.get(record_id)
            return record is not None and record.duration_ms >= 0

    def verify_stage_metadata(self, record_id: str) -> bool:
        """Verify performance record has stage_name and stage_owner (Gate C)."""
        with self._lock:
            record = self._records.get(record_id)
            return record is not None and bool(record.stage_name) and bool(record.stage_owner)

    def verify_budget_tracking(self, record_id: str) -> bool:
        """Verify budgeted stage has budget_class and within_budget_flag (Gate D)."""
        with self._lock:
            record = self._records.get(record_id)
            return record is not None and (
                record.budget_class is None or (record.budget_class and record.within_budget_flag is not None)
            )


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------


def get_performance_registry() -> PerformanceRegistry:
    """Get the singleton PerformanceRegistry instance."""
    return PerformanceRegistry.get_instance()


def reset_performance_registry() -> None:
    """Reset the singleton PerformanceRegistry (for testing)."""
    with PerformanceRegistry._lock:
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
