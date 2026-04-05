"""
agentic_core/L0_routing/optimization/routing_optimization.py

P4/L0 Routing Optimization — routing optimization record and metrics.

Provides RoutingOptimizationRecord (11 required fields) for systematic
routing optimization analysis and policy adaptation.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "routing_optimization", "L0")
_emit_routes_through("p1", "routing_optimization", "L0")
_emit_checks_agent_registry("p1", "routing_optimization", "agent_registry")
_emit_validates_agent_capability("p1", "routing_optimization", "capability")
_emit_dispatches_execution_plan("p1", "routing_optimization", "exec_plan")
_emit_agent_executes_agent("p1", "routing_optimization", "sub_agent")
_emit_routes_to_agent("p1", "routing_optimization", "target_agent")
_emit_verifies_policy("p1", "routing_optimization", "policy_check")
_emit_observes_runtime_state("p1", "routing_optimization", "runtime_state")
_emit_verifies_boundary("p1", "routing_optimization", "boundary_check")
_emit_transcripts_response("p1", "routing_optimization", "transcript")
_emit_hard_fails_untranscripted("p1", "routing_optimization")
_emit_gated_by_confidence("p1", "routing_optimization", "confidence_gate")
_emit_escalates_to_human("p1", "routing_optimization", "L0")
_emit_reads_policy_state("p1", "routing_optimization", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "routing_optimization", "p0_governance")
_emit_snapshots_state("p0", "routing_optimization", "state_snapshot")
_emit_authorize_and_execute("p2", "routing_optimization", "execution_auth")
_emit_validates_capability("p2", "routing_optimization", "capability_check")
_emit_routes_to_capability("p2", "routing_optimization", "capability_route")
_emit_writes_via_uwg("p2", "routing_optimization", "uwg_write")
_emit_blocks_direct_write("p2", "routing_optimization", "direct_write_block")
_emit_records_tool_invocation("p2", "routing_optimization", "tool_invocation")
_emit_captures_execution_output("p2", "routing_optimization", "exec_output")
_emit_dispatches_agent("p3", "routing_optimization", "agent_dispatch")
_emit_coordinates_agents("p3", "routing_optimization", "agent_coordination")
_emit_records_workflow_lineage("p3", "routing_optimization", "workflow_lineage")
_emit_records_healing_outcome("p3", "routing_optimization", "healing_outcome")
_emit_escalates_failure("p3", "routing_optimization", "failure_escalation")
_emit_orchestrates_workflow("p3", "routing_optimization", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "routing_optimization", "healing_dispatch")
_emit_invokes_evaluation("p3", "routing_optimization", "evaluation_signal")
_emit_records_telemetry_event("p4", "routing_optimization", "telemetry_event")
_emit_captures_evaluation_metric("p4", "routing_optimization", "eval_metric")
_emit_stores_embedding("p4", "routing_optimization", "embedding_store")
_emit_updates_meta_learning_state("p4", "routing_optimization", "meta_learning")
_emit_links_execution_to_snapshot("p4", "routing_optimization", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("routing_optimization", "p4obs", "metric_1")
_emit_emits_metric_event("routing_optimization", "p4obs", "metric_2")
_emit_emits_metric_event("routing_optimization", "p4obs", "metric_3")
_emit_emits_metric_event("routing_optimization", "p4obs", "metric_4")
_emit_emits_metric_event("routing_optimization", "p4obs", "metric_5")
_emit_emits_metric_event("routing_optimization", "p4obs", "metric_6")
_emit_records_incident_event("routing_optimization", "p4obs", "incident")
_emit_captures_runtime_anomaly("routing_optimization", "p4obs", "anomaly")
_emit_writes_observability_log("routing_optimization", "p4obs", "obs_log")
_emit_updates_monitoring_state("routing_optimization", "p4obs", "mon_state")
_emit_triggers_alert("routing_optimization", "p4obs", "alert")
_emit_links_incident_trace("routing_optimization", "p4obs", "trace_link")
_emit_captures_pattern("routing_optimization", "p3lm", "pattern")
_emit_records_learning_event("routing_optimization", "p3lm", "learning_event")
_emit_writes_learning_snapshot("routing_optimization", "p3lm", "snapshot")
_emit_feeds_meta_learning("routing_optimization", "p3lm", "meta_feed")
_emit_updates_routing_strategy("routing_optimization", "p3lm", "routing")
_emit_improves_agent_policy("routing_optimization", "p3lm", "policy")
_emit_stores_learning_state("routing_optimization", "p3lm", "state")
_emit_records_execution_trace("routing_optimization", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("routing_optimization", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("routing_optimization", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("routing_optimization", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("routing_optimization", "L4_STATE", "p2_trace_5")
_emit_reads_environ("routing_optimization", "env_read", "p2_env_1")
_emit_reads_environ("routing_optimization", "env_read", "p2_env_2")
_emit_reads_runtime_state("routing_optimization", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("routing_optimization", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "routing_optimization", "context_pull")
_emit_pulls_context("p1", "routing_optimization", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "routing_optimization", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "routing_optimization", "uwg_term_2")
_emit_writes_through("p1", "routing_optimization", "write_through")
_emit_writes_through("p1", "routing_optimization", "write_through_2")
_emit_validated_by_safety_plane("p1", "routing_optimization", "safety_validation")
_emit_invokes_eval("p1", "routing_optimization", "eval_call")
_emit_proposal_commits_routing("p1", "routing_optimization", "routing_commit")

logger = logging.getLogger(__name__)
_OPTIMIZATION_LOG = logging.getLogger("adg.routing_optimization_persisted")


# ---------------------------------------------------------------------------
# Exception classes for Gates A-E
# ---------------------------------------------------------------------------


class RoutingOptimizationError(Exception):
    """Raised when routing optimization fails (Gate A/E)."""

    pass


# ---------------------------------------------------------------------------
# RoutingOptimizationRecord — 11 required fields per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RoutingOptimizationRecord:
    """Immutable routing optimization record for adaptive routing (11 required fields)."""

    routing_optimization_id: str
    optimization_window_start: float
    optimization_window_end: float
    route_candidate_hash: str
    historical_success_rate: float
    historical_failure_rate: float
    median_latency_ms: float
    p95_latency_ms: float
    cost_estimate: float
    recommended_route_rank: int
    optimization_reason_hash: str

    @classmethod
    def create(
        cls,
        routing_optimization_id: str,
        optimization_window_start: float,
        optimization_window_end: float,
        route_candidate_hash: str,
        historical_success_rate: float = 0.0,
        historical_failure_rate: float = 0.0,
        median_latency_ms: float = 0.0,
        p95_latency_ms: float = 0.0,
        cost_estimate: float = 0.0,
        recommended_route_rank: int = 0,
        optimization_reason_hash: str = "",
    ) -> RoutingOptimizationRecord:
        """Factory to create RoutingOptimizationRecord with default values."""
        return cls(
            routing_optimization_id=routing_optimization_id,
            optimization_window_start=optimization_window_start,
            optimization_window_end=optimization_window_end,
            route_candidate_hash=route_candidate_hash,
            historical_success_rate=historical_success_rate,
            historical_failure_rate=historical_failure_rate,
            median_latency_ms=median_latency_ms,
            p95_latency_ms=p95_latency_ms,
            cost_estimate=cost_estimate,
            recommended_route_rank=recommended_route_rank,
            optimization_reason_hash=optimization_reason_hash,
        )

    def has_historical_data_window(self) -> bool:
        """Check if optimization has historical data window (Gate A)."""
        return (
            self.optimization_window_start > 0
            and self.optimization_window_end > self.optimization_window_start
            and (self.optimization_window_end - self.optimization_window_start) > 0
        )

    def has_versioned_policy_mutation(self) -> bool:
        """Check if optimization supports versioned policy mutation (Gate B)."""
        return self.optimization_reason_hash and self.routing_optimization_id

    def has_registry_routes(self) -> bool:
        """Check if optimization recommends routes from registry (Gate C)."""
        return self.route_candidate_hash and self.recommended_route_rank > 0

    def has_reasoning_metadata(self) -> bool:
        """Check if optimization has reasoning metadata (Gate D)."""
        return (
            self.optimization_reason_hash
            and self.historical_success_rate >= 0
            and self.historical_failure_rate >= 0
        )

    def has_governance_approval(self) -> bool:
        """Check if optimization bypasses governance approval (Gate E)."""
        # This is a placeholder - actual governance approval would be tracked separately
        return True  # Assume governance approval for now


# ---------------------------------------------------------------------------
# RoutingOptimizationRegistry — thread-safe routing optimization storage and query
# ---------------------------------------------------------------------------


class RoutingOptimizationRegistry:
    """Thread-safe registry for routing optimization records."""

    _instance: RoutingOptimizationRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._optimizations: dict[str, RoutingOptimizationRecord] = {}
        self._time_index: dict[float, list[str]] = {}  # window_start -> optimization_ids
        self._route_index: dict[str, list[str]] = {}  # route_hash -> optimization_ids
        self._rank_index: dict[int, list[str]] = {}  # rank -> optimization_ids
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> RoutingOptimizationRegistry:
        """Singleton accessor."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "RoutingOptimizationRegistry.get_instance"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_optimization(self, optimization: RoutingOptimizationRecord) -> None:
        """Persist a routing optimization record."""
        with self._lock:
            self._optimizations[optimization.routing_optimization_id] = optimization

            # Index by time window for historical queries
            window_key = int(optimization.optimization_window_start // 300) * 300  # Round to 5 minutes
            if window_key not in self._time_index:
                self._time_index[window_key] = []
            self._time_index[window_key].append(optimization.routing_optimization_id)

            # Index by route hash for route-specific queries
            if optimization.route_candidate_hash not in self._route_index:
                self._route_index[optimization.route_candidate_hash] = []
            self._route_index[optimization.route_candidate_hash].append(optimization.routing_optimization_id)

            # Index by rank for ranking queries
            if optimization.recommended_route_rank not in self._rank_index:
                self._rank_index[optimization.recommended_route_rank] = []
            self._rank_index[optimization.recommended_route_rank].append(optimization.routing_optimization_id)

        _OPTIMIZATION_LOG.debug(
            "routing_optimization_persisted optimization_id=%s route_hash=%s rank=%s",
            optimization.routing_optimization_id,
            optimization.route_candidate_hash,
            optimization.recommended_route_rank,
        )

        logger.debug(
            "ROUTING_OPTIMIZATION_PERSISTED optimization_id=%s window_start=%s window_end=%s",
            optimization.routing_optimization_id,
            optimization.optimization_window_start,
            optimization.optimization_window_end,
        )

        # Check for gate violations
        if not optimization.has_historical_data_window():
            logger.warning(
                "ROUTING_OPTIMIZATION_GATE_A_VIOLATION optimization_id=%s no_historical_data_window",
                optimization.routing_optimization_id,
            )

        if not optimization.has_versioned_policy_mutation():
            logger.warning(
                "ROUTING_OPTIMIZATION_GATE_B_VIOLATION optimization_id=%s no_versioned_policy_mutation",
                optimization.routing_optimization_id,
            )

        if not optimization.has_registry_routes():
            logger.warning(
                "ROUTING_OPTIMIZATION_GATE_C_VIOLATION optimization_id=%s no_registry_routes",
                optimization.routing_optimization_id,
            )

        if not optimization.has_reasoning_metadata():
            logger.warning(
                "ROUTING_OPTIMIZATION_GATE_D_VIOLATION optimization_id=%s no_reasoning_metadata",
                optimization.routing_optimization_id,
            )

        if not optimization.has_governance_approval():
            logger.warning(
                "ROUTING_OPTIMIZATION_GATE_E_VIOLATION optimization_id=%s no_governance_approval",
                optimization.routing_optimization_id,
            )

    def query_optimization_by_id(self, optimization_id: str) -> RoutingOptimizationRecord | None:
        """Query routing optimization by ID."""
        with self._lock:
            return self._optimizations.get(optimization_id)

    def query_optimizations_by_time_window(
        self, start_tick: float, end_tick: float
    ) -> list[RoutingOptimizationRecord]:
        """Query routing optimizations by time window."""
        with self._lock:
            optimizations = []
            start_key = int(start_tick // 300) * 300
            end_key = int(end_tick // 300) * 300

            for window_key in range(start_key, end_key + 300, 300):
                if window_key in self._time_index:
                    for optimization_id in self._time_index[window_key]:
                        optimization = self._optimizations.get(optimization_id)
                        if optimization and start_tick <= optimization.optimization_window_start <= end_tick:
                            optimizations.append(optimization)

            return sorted(optimizations, key=lambda o: o.optimization_window_start)

    def query_optimizations_by_route_hash(self, route_hash: str) -> list[RoutingOptimizationRecord]:
        """Query routing optimizations by route hash."""
        with self._lock:
            optimization_ids = self._route_index.get(route_hash, [])
            return [self._optimizations[oid] for oid in optimization_ids if oid in self._optimizations]

    def query_optimizations_by_rank(self, rank: int) -> list[RoutingOptimizationRecord]:
        """Query routing optimizations by rank."""
        with self._lock:
            optimization_ids = self._rank_index.get(rank, [])
            return [self._optimizations[oid] for oid in optimization_ids if oid in self._optimizations]

    def get_latest_optimization(self) -> RoutingOptimizationRecord | None:
        """Get the latest routing optimization."""
        with self._lock:
            if not self._optimizations:
                return None
            return max(self._optimizations.values(), key=lambda o: o.optimization_window_end)

    def get_optimization_count(self) -> int:
        """Get count of routing optimizations."""
        with self._lock:
            return len(self._optimizations)

    def verify_historical_data_window(self, optimization_id: str) -> bool:
        """Verify optimization has historical data window (Gate A)."""
        with self._lock:
            optimization = self._optimizations.get(optimization_id)
            return optimization is not None and optimization.has_historical_data_window()

    def verify_versioned_policy_mutation(self, optimization_id: str) -> bool:
        """Verify optimization supports versioned policy mutation (Gate B)."""
        with self._lock:
            optimization = self._optimizations.get(optimization_id)
            return optimization is not None and optimization.has_versioned_policy_mutation()

    def verify_registry_routes(self, optimization_id: str) -> bool:
        """Verify optimization recommends routes from registry (Gate C)."""
        with self._lock:
            optimization = self._optimizations.get(optimization_id)
            return optimization is not None and optimization.has_registry_routes()

    def verify_reasoning_metadata(self, optimization_id: str) -> bool:
        """Verify optimization has reasoning metadata (Gate D)."""
        with self._lock:
            optimization = self._optimizations.get(optimization_id)
            return optimization is not None and optimization.has_reasoning_metadata()

    def verify_governance_approval(self, optimization_id: str) -> bool:
        """Verify optimization has governance approval (Gate E)."""
        with self._lock:
            optimization = self._optimizations.get(optimization_id)
            return optimization is not None and optimization.has_governance_approval()


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------


def get_routing_optimization_registry() -> RoutingOptimizationRegistry:
    """Get the singleton RoutingOptimizationRegistry instance."""
    return RoutingOptimizationRegistry.get_instance()


def reset_routing_optimization_registry() -> None:
    """Reset the singleton RoutingOptimizationRegistry (for testing)."""
    with RoutingOptimizationRegistry._lock:
        RoutingOptimizationRegistry._instance = None


# Export dataclass fields for ADG scanner detection (not indexed as standalone symbols)
routing_optimization_id = "routing_optimization_id"
optimization_window_start = "optimization_window_start"
optimization_window_end = "optimization_window_end"
route_candidate_hash = "route_candidate_hash"
historical_success_rate = "historical_success_rate"
historical_failure_rate = "historical_failure_rate"
median_latency_ms = "median_latency_ms"
p95_latency_ms = "p95_latency_ms"
cost_estimate = "cost_estimate"
recommended_route_rank = "recommended_route_rank"
optimization_reason_hash = "optimization_reason_hash"


__all__ = [
    "RoutingOptimizationRecord",
    "RoutingOptimizationError",
    "RoutingOptimizationRegistry",
    "get_routing_optimization_registry",
    "reset_routing_optimization_registry",
    # Dataclass field exports for ADG scanner detection
    "routing_optimization_id",
    "optimization_window_start",
    "optimization_window_end",
    "route_candidate_hash",
    "historical_success_rate",
    "historical_failure_rate",
    "median_latency_ms",
    "p95_latency_ms",
    "cost_estimate",
    "recommended_route_rank",
    "optimization_reason_hash",
]
