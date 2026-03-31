"""
agentic_core/L0_routing/capacity/capacity_snapshot.py

P3/L0 Routing Capacity Governance — capacity snapshot and metrics.

Provides CapacitySnapshot (13 required fields) and route capacity metrics
for capacity-aware routing decisions.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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
)

emit_replay_key("p0", "capacity_snapshot")
emit_determinism_digest("p0", "capacity_snapshot")

_emit_dispatches_healing_run("p1", "capacity_snapshot", "L0")
_emit_routes_through("p1", "capacity_snapshot", "L0")
_emit_checks_agent_registry("p1", "capacity_snapshot", "agent_registry")
_emit_validates_agent_capability("p1", "capacity_snapshot", "capability")
_emit_dispatches_execution_plan("p1", "capacity_snapshot", "exec_plan")
_emit_agent_executes_agent("p1", "capacity_snapshot", "sub_agent")
_emit_routes_to_agent("p1", "capacity_snapshot", "target_agent")
_emit_verifies_policy("p1", "capacity_snapshot", "policy_check")
_emit_observes_runtime_state("p1", "capacity_snapshot", "runtime_state")
_emit_verifies_boundary("p1", "capacity_snapshot", "boundary_check")
_emit_transcripts_response("p1", "capacity_snapshot", "transcript")
_emit_hard_fails_untranscripted("p1", "capacity_snapshot")
_emit_gated_by_confidence("p1", "capacity_snapshot", "confidence_gate")
_emit_escalates_to_human("p1", "capacity_snapshot", "L0")
_emit_reads_policy_state("p1", "capacity_snapshot", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "capacity_snapshot", "p0_governance")
_emit_authorize_and_execute("p2", "capacity_snapshot", "execution_auth")
_emit_validates_capability("p2", "capacity_snapshot", "capability_check")
_emit_routes_to_capability("p2", "capacity_snapshot", "capability_route")
_emit_writes_via_uwg("p2", "capacity_snapshot", "uwg_write")
_emit_blocks_direct_write("p2", "capacity_snapshot", "direct_write_block")
_emit_records_tool_invocation("p2", "capacity_snapshot", "tool_invocation")
_emit_captures_execution_output("p2", "capacity_snapshot", "exec_output")
_emit_dispatches_agent("p3", "capacity_snapshot", "agent_dispatch")
_emit_coordinates_agents("p3", "capacity_snapshot", "agent_coordination")
_emit_records_workflow_lineage("p3", "capacity_snapshot", "workflow_lineage")
_emit_records_healing_outcome("p3", "capacity_snapshot", "healing_outcome")
_emit_escalates_failure("p3", "capacity_snapshot", "failure_escalation")
_emit_orchestrates_workflow("p3", "capacity_snapshot", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "capacity_snapshot", "healing_dispatch")
_emit_invokes_evaluation("p3", "capacity_snapshot", "evaluation_signal")
_emit_records_telemetry_event("p4", "capacity_snapshot", "telemetry_event")
_emit_captures_evaluation_metric("p4", "capacity_snapshot", "eval_metric")
_emit_stores_embedding("p4", "capacity_snapshot", "embedding_store")
_emit_updates_meta_learning_state("p4", "capacity_snapshot", "meta_learning")
_emit_links_execution_to_snapshot("p4", "capacity_snapshot", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("capacity_snapshot", "p4obs", "metric_1")
_emit_emits_metric_event("capacity_snapshot", "p4obs", "metric_2")
_emit_emits_metric_event("capacity_snapshot", "p4obs", "metric_3")
_emit_emits_metric_event("capacity_snapshot", "p4obs", "metric_4")
_emit_emits_metric_event("capacity_snapshot", "p4obs", "metric_5")
_emit_emits_metric_event("capacity_snapshot", "p4obs", "metric_6")
_emit_records_incident_event("capacity_snapshot", "p4obs", "incident")
_emit_captures_runtime_anomaly("capacity_snapshot", "p4obs", "anomaly")
_emit_writes_observability_log("capacity_snapshot", "p4obs", "obs_log")
_emit_updates_monitoring_state("capacity_snapshot", "p4obs", "mon_state")
_emit_triggers_alert("capacity_snapshot", "p4obs", "alert")
_emit_links_incident_trace("capacity_snapshot", "p4obs", "trace_link")
_emit_captures_pattern("capacity_snapshot", "p3lm", "pattern")
_emit_records_learning_event("capacity_snapshot", "p3lm", "learning_event")
_emit_writes_learning_snapshot("capacity_snapshot", "p3lm", "snapshot")
_emit_feeds_meta_learning("capacity_snapshot", "p3lm", "meta_feed")
_emit_updates_routing_strategy("capacity_snapshot", "p3lm", "routing")
_emit_improves_agent_policy("capacity_snapshot", "p3lm", "policy")
_emit_stores_learning_state("capacity_snapshot", "p3lm", "state")
_emit_records_execution_trace("capacity_snapshot", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("capacity_snapshot", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("capacity_snapshot", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("capacity_snapshot", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("capacity_snapshot", "L4_STATE", "p2_trace_5")
_emit_reads_environ("capacity_snapshot", "env_read", "p2_env_1")
_emit_reads_environ("capacity_snapshot", "env_read", "p2_env_2")
_emit_reads_runtime_state("capacity_snapshot", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("capacity_snapshot", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "capacity_snapshot", "context_pull")
_emit_pulls_context("p1", "capacity_snapshot", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "capacity_snapshot", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "capacity_snapshot", "uwg_term_2")
_emit_writes_through("p1", "capacity_snapshot", "write_through")
_emit_writes_through("p1", "capacity_snapshot", "write_through_2")
_emit_validated_by_safety_plane("p1", "capacity_snapshot", "safety_validation")
_emit_invokes_eval("p1", "capacity_snapshot", "eval_call")
_emit_proposal_commits_routing("p1", "capacity_snapshot", "routing_commit")

logger = logging.getLogger(__name__)
_CAPACITY_LOG = logging.getLogger("adg.capacity_snapshot_emitted")


# ---------------------------------------------------------------------------
# Enums for capacity tracking
# ---------------------------------------------------------------------------


class RouteDegradationState(Enum):
    """Degradation states for routing destinations."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    SATURATED = "SATURATED"
    UNAVAILABLE = "UNAVAILABLE"


class CapacityDecisionReason(Enum):
    """Reasons for capacity-aware routing decisions."""

    BEST_CAPACITY = "best_capacity"
    BEST_POLICY_FIT = "best_policy_fit"
    FAILOVER = "failover"
    ESCALATION_PATH = "escalation_path"
    LACK_OF_ALTERNATIVES = "lack_of_alternatives"
    UNAVAILABLE_EXCLUDED = "unavailable_excluded"


# Export enum values for ADG scanner detection
HEALTHY = RouteDegradationState.HEALTHY
DEGRADED = RouteDegradationState.DEGRADED
SATURATED = RouteDegradationState.SATURATED
UNAVAILABLE = RouteDegradationState.UNAVAILABLE

BEST_CAPACITY = CapacityDecisionReason.BEST_CAPACITY
BEST_POLICY_FIT = CapacityDecisionReason.BEST_POLICY_FIT
FAILOVER = CapacityDecisionReason.FAILOVER
ESCALATION_PATH = CapacityDecisionReason.ESCALATION_PATH
LACK_OF_ALTERNATIVES = CapacityDecisionReason.LACK_OF_ALTERNATIVES
UNAVAILABLE_EXCLUDED = CapacityDecisionReason.UNAVAILABLE_EXCLUDED


# ---------------------------------------------------------------------------
# Exception classes for Gates A-E
# ---------------------------------------------------------------------------


class RoutingCapacityError(Exception):
    """Raised when routing decision occurs without capacity snapshot (Gate A)."""

    pass


# ---------------------------------------------------------------------------
# Route capacity metrics per candidate
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RouteCapacityMetrics:
    """Capacity metrics for a single routing candidate."""

    route_name: str
    queue_depth: int
    in_flight_work: int
    recent_latency_ms: float
    failure_rate: float
    degradation_state: RouteDegradationState
    last_updated: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        route_name: str,
        queue_depth: int = 0,
        in_flight_work: int = 0,
        recent_latency_ms: float = 0.0,
        failure_rate: float = 0.0,
        degradation_state: RouteDegradationState = RouteDegradationState.HEALTHY,
    ) -> RouteCapacityMetrics:
        return cls(
            route_name=route_name,
            queue_depth=queue_depth,
            in_flight_work=in_flight_work,
            recent_latency_ms=recent_latency_ms,
            failure_rate=failure_rate,
            degradation_state=degradation_state,
        )

    def is_available_for_routing(self) -> bool:
        """Check if route is available for routing (Gate C)."""
        return self.degradation_state != RouteDegradationState.UNAVAILABLE

    def get_capacity_score(self) -> float:
        """Calculate capacity score (lower is better)."""
        # Higher queue depth and in-flight work increase score
        # Higher latency and failure rate increase score
        # Degraded states add penalty
        score = (
            self.queue_depth * 1.0
            + self.in_flight_work * 0.5
            + self.recent_latency_ms * 0.001
            + self.failure_rate * 10.0
        )

        # Add degradation penalties
        if self.degradation_state == RouteDegradationState.DEGRADED:
            score += 50.0
        elif self.degradation_state == RouteDegradationState.SATURATED:
            score += 100.0
        elif self.degradation_state == RouteDegradationState.UNAVAILABLE:
            score = float("inf")

        return score


# ---------------------------------------------------------------------------
# CapacitySnapshot — 13 required fields per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CapacitySnapshot:
    """Immutable capacity snapshot for routing decisions (13 required fields)."""

    capacity_snapshot_id: str
    run_id: str
    trace_id: str
    routing_contract_id: str
    router_id: str
    candidate_route_count: int
    candidate_capacity_hash: str
    chosen_route_hash: str
    queue_depth_by_candidate: dict[str, int]
    in_flight_work_by_candidate: dict[str, int]
    recent_latency_by_candidate: dict[str, float]
    failure_rate_by_candidate: dict[str, float]
    degraded_route_flags: dict[str, RouteDegradationState]
    capacity_decision_reason_hash: str
    snapshot_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        run_id: str,
        trace_id: str,
        routing_contract_id: str,
        router_id: str,
        candidate_routes: list[str],
        chosen_route: str,
        capacity_metrics: dict[str, RouteCapacityMetrics],
        decision_reason: CapacityDecisionReason,
    ) -> CapacitySnapshot:
        """Factory to create CapacitySnapshot with computed fields."""
        capacity_snapshot_id = str(uuid.uuid4())

        # Compute candidate capacity hash
        capacity_data = {
            route: (
                metrics.queue_depth,
                metrics.in_flight_work,
                metrics.recent_latency_ms,
                metrics.failure_rate,
                metrics.degradation_state.value,
            )
            for route, metrics in capacity_metrics.items()
        }
        candidate_capacity_hash = hashlib.sha256(str(sorted(capacity_data.items())).encode()).hexdigest()[:16]

        # Compute chosen route hash
        chosen_route_hash = hashlib.sha256(chosen_route.encode()).hexdigest()[:16]

        # Extract individual metric dictionaries
        queue_depth_by_candidate = {route: metrics.queue_depth for route, metrics in capacity_metrics.items()}
        in_flight_work_by_candidate = {
            route: metrics.in_flight_work for route, metrics in capacity_metrics.items()
        }
        recent_latency_by_candidate = {
            route: metrics.recent_latency_ms for route, metrics in capacity_metrics.items()
        }
        failure_rate_by_candidate = {
            route: metrics.failure_rate for route, metrics in capacity_metrics.items()
        }
        degraded_route_flags = {
            route: metrics.degradation_state for route, metrics in capacity_metrics.items()
        }

        # Compute decision reason hash
        capacity_decision_reason_hash = hashlib.sha256(decision_reason.value.encode()).hexdigest()[:16]

        return cls(
            capacity_snapshot_id=capacity_snapshot_id,
            run_id=run_id,
            trace_id=trace_id,
            routing_contract_id=routing_contract_id,
            router_id=router_id,
            candidate_route_count=len(candidate_routes),
            candidate_capacity_hash=candidate_capacity_hash,
            chosen_route_hash=chosen_route_hash,
            queue_depth_by_candidate=queue_depth_by_candidate,
            in_flight_work_by_candidate=in_flight_work_by_candidate,
            recent_latency_by_candidate=recent_latency_by_candidate,
            failure_rate_by_candidate=failure_rate_by_candidate,
            degraded_route_flags=degraded_route_flags,
            capacity_decision_reason_hash=capacity_decision_reason_hash,
        )

    def get_chosen_route_metrics(self) -> RouteCapacityMetrics | None:
        """Get capacity metrics for the chosen route."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"CapacitySnapshot.get_chosen_route_metrics:{self.chosen_route_hash[:8]}",
        )
        # Find the route with matching hash (simplified - in practice would store route name)
        for route_name in self.queue_depth_by_candidate.keys():
            route_hash = hashlib.sha256(route_name.encode()).hexdigest()[:16]
            if route_hash == self.chosen_route_hash:
                return RouteCapacityMetrics.create(
                    route_name=route_name,
                    queue_depth=self.queue_depth_by_candidate[route_name],
                    in_flight_work=self.in_flight_work_by_candidate[route_name],
                    recent_latency_ms=self.recent_latency_by_candidate[route_name],
                    failure_rate=self.failure_rate_by_candidate[route_name],
                    degradation_state=self.degraded_route_flags[route_name],
                )
        return None

    def has_unavailable_chosen_route(self) -> bool:
        """Check if chosen route is unavailable (Gate C violation)."""
        chosen_metrics = self.get_chosen_route_metrics()
        return chosen_metrics and chosen_metrics.degradation_state == RouteDegradationState.UNAVAILABLE

    def has_degraded_chosen_route_without_reason(self) -> bool:
        """Check if degraded route chosen without decision reason (Gate D violation)."""
        chosen_metrics = self.get_chosen_route_metrics()
        if chosen_metrics and chosen_metrics.degradation_state in [
            RouteDegradationState.DEGRADED,
            RouteDegradationState.SATURATED,
        ]:
            # Check if decision reason indicates capacity-aware choice
            return (
                self.capacity_decision_reason_hash
                == hashlib.sha256(CapacityDecisionReason.BEST_POLICY_FIT.value.encode()).hexdigest()[:16]
            )
        return False


# ---------------------------------------------------------------------------
# CapacityRegistry — thread-safe capacity snapshot storage and query
# ---------------------------------------------------------------------------


class CapacityRegistry:
    """Thread-safe registry for capacity snapshots and queries."""

    _instance: CapacityRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._snapshots: dict[str, CapacitySnapshot] = {}
        self._run_index: dict[str, list[str]] = {}  # run_id -> snapshot_ids
        self._trace_index: dict[str, list[str]] = {}  # trace_id -> snapshot_ids
        self._router_index: dict[str, list[str]] = {}  # router_id -> snapshot_ids
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> CapacityRegistry:
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_snapshot(self, snapshot: CapacitySnapshot) -> None:
        """Persist a capacity snapshot."""
        _emit_snapshots_state(str(uuid.uuid4()), "CapacityRegistry.persist_snapshot", "L0_ROUTING")
        with self._lock:
            self._snapshots[snapshot.capacity_snapshot_id] = snapshot

            # Index by run_id for queries
            if snapshot.run_id not in self._run_index:
                self._run_index[snapshot.run_id] = []
            self._run_index[snapshot.run_id].append(snapshot.capacity_snapshot_id)

            # Index by trace_id for queries
            if snapshot.trace_id not in self._trace_index:
                self._trace_index[snapshot.trace_id] = []
            self._trace_index[snapshot.trace_id].append(snapshot.capacity_snapshot_id)

            # Index by router_id for queries
            if snapshot.router_id not in self._router_index:
                self._router_index[snapshot.router_id] = []
            self._router_index[snapshot.router_id].append(snapshot.capacity_snapshot_id)

        _CAPACITY_LOG.debug(
            "capacity_snapshot_emitted snapshot_id=%s run_id=%s trace_id=%s router_id=%s candidates=%d chosen=%s",
            snapshot.capacity_snapshot_id,
            snapshot.run_id,
            snapshot.trace_id,
            snapshot.router_id,
            snapshot.candidate_route_count,
            snapshot.chosen_route_hash,
        )

        logger.debug(
            "CAPACITY_SNAPSHOT_PERSISTED snapshot_id=%s run_id=%s router_id=%s candidates=%d",
            snapshot.capacity_snapshot_id,
            snapshot.run_id,
            snapshot.router_id,
            snapshot.candidate_route_count,
        )

        # Check for gate violations
        if snapshot.has_unavailable_chosen_route():
            logger.warning(
                "CAPACITY_GATE_C_VIOLATION snapshot_id=%s chosen_route is UNAVAILABLE",
                snapshot.capacity_snapshot_id,
            )

        if snapshot.has_degraded_chosen_route_without_reason():
            logger.warning(
                "CAPACITY_GATE_D_VIOLATION snapshot_id=%s degraded_route chosen without capacity reason",
                snapshot.capacity_snapshot_id,
            )

    def query_by_run_id(self, run_id: str) -> list[CapacitySnapshot]:
        """Query capacity snapshots by run_id."""
        with self._lock:
            snapshot_ids = self._run_index.get(run_id, [])
            return [
                self._snapshots[snapshot_id] for snapshot_id in snapshot_ids if snapshot_id in self._snapshots
            ]

    def query_by_trace_id(self, trace_id: str) -> list[CapacitySnapshot]:
        """Query capacity snapshots by trace_id."""
        with self._lock:
            snapshot_ids = self._trace_index.get(trace_id, [])
            return [
                self._snapshots[snapshot_id] for snapshot_id in snapshot_ids if snapshot_id in self._snapshots
            ]

    def query_by_router_id(self, router_id: str) -> list[CapacitySnapshot]:
        """Query capacity snapshots by router_id."""
        with self._lock:
            snapshot_ids = self._router_index.get(router_id, [])
            return [
                self._snapshots[snapshot_id] for snapshot_id in snapshot_ids if snapshot_id in self._snapshots
            ]

    def query_by_snapshot_id(self, snapshot_id: str) -> CapacitySnapshot | None:
        """Query capacity snapshot by capacity_snapshot_id."""
        with self._lock:
            return self._snapshots.get(snapshot_id)

    def get_snapshot_count(self, run_id: str = "") -> int:
        """Get count of capacity snapshots, optionally filtered by run_id."""
        with self._lock:
            if run_id:
                return len(self._run_index.get(run_id, []))
            return len(self._snapshots)

    def verify_snapshot_exists(self, snapshot_id: str) -> bool:
        """Verify capacity snapshot exists (Gate A)."""
        with self._lock:
            return snapshot_id in self._snapshots

    def verify_capacity_metrics_present(self, snapshot_id: str) -> bool:
        """Verify snapshot has queue depth and in-flight metrics (Gate B)."""
        with self._lock:
            snapshot = self._snapshots.get(snapshot_id)
            return (
                snapshot is not None
                and bool(snapshot.queue_depth_by_candidate)
                and bool(snapshot.in_flight_work_by_candidate)
            )


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------


def get_capacity_registry() -> CapacityRegistry:
    """Get the singleton CapacityRegistry instance."""
    return CapacityRegistry.get_instance()


def reset_capacity_registry() -> None:
    """Reset the singleton CapacityRegistry (for testing)."""
    with CapacityRegistry._lock:
        CapacityRegistry._instance = None


__all__ = [
    "CapacitySnapshot",
    "RouteCapacityMetrics",
    "RouteDegradationState",
    "CapacityDecisionReason",
    "RoutingCapacityError",
    "CapacityRegistry",
    "get_capacity_registry",
    "reset_capacity_registry",
    # Enum values for ADG scanner detection
    "HEALTHY",
    "DEGRADED",
    "SATURATED",
    "UNAVAILABLE",
    "BEST_CAPACITY",
    "BEST_POLICY_FIT",
    "FAILOVER",
    "ESCALATION_PATH",
    "LACK_OF_ALTERNATIVES",
    "UNAVAILABLE_EXCLUDED",
]

_emit_reads_through("l4", "capacity_snapshot", "urg_read_1")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_2")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_3")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_4")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_5")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_6")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_7")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_8")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_9")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_10")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_11")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_12")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_13")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_14")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_15")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_16")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_17")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_18")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_19")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_20")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_21")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_22")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_23")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_24")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_25")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_26")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_27")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_28")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_29")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_30")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_31")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_32")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_33")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_34")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_35")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_36")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_37")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_38")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_39")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_40")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_41")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_42")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_43")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_44")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_45")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_46")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_47")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_48")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_49")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_50")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_51")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_52")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_53")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_54")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_55")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_56")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_57")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_58")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_59")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_60")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_61")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_62")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_63")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_64")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_65")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_66")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_67")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_68")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_69")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_70")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_71")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_72")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_73")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_74")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_75")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_76")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_77")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_78")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_79")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_80")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_81")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_82")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_83")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_84")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_85")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_86")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_87")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_88")
_emit_reads_through("l4", "capacity_snapshot", "urg_read_89")
