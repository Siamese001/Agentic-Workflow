"""Tests for capacity_snapshot.py module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.reasoning.capacity_snapshot import (
    RouteDegradationState,
    CapacityDecisionReason,
    RoutingCapacityError,
    RouteCapacityMetrics,
    CapacitySnapshot,
    CapacityRegistry,
    get_capacity_registry,
    reset_capacity_registry,
    # Enum values for ADG scanner detection
    HEALTHY,
    DEGRADED,
    SATURATED,
    UNAVAILABLE,
    BEST_CAPACITY,
    BEST_POLICY_FIT,
    FAILOVER,
    ESCALATION_PATH,
    LACK_OF_ALTERNATIVES,
    UNAVAILABLE_EXCLUDED,
)


class TestRouteDegradationState:
    """Tests for RouteDegradationState enum."""

    def test_enum_values(self):
        """Test that enum values are defined."""
        assert RouteDegradationState.HEALTHY.value == "HEALTHY"
        assert RouteDegradationState.DEGRADED.value == "DEGRADED"
        assert RouteDegradationState.SATURATED.value == "SATURATED"
        assert RouteDegradationState.UNAVAILABLE.value == "UNAVAILABLE"

    def test_exported_enum_values(self):
        """Test that enum values are exported for ADG scanner."""
        assert HEALTHY == RouteDegradationState.HEALTHY
        assert DEGRADED == RouteDegradationState.DEGRADED
        assert SATURATED == RouteDegradationState.SATURATED
        assert UNAVAILABLE == RouteDegradationState.UNAVAILABLE


class TestCapacityDecisionReason:
    """Tests for CapacityDecisionReason enum."""

    def test_enum_values(self):
        """Test that enum values are defined."""
        assert CapacityDecisionReason.BEST_CAPACITY.value == "best_capacity"
        assert CapacityDecisionReason.BEST_POLICY_FIT.value == "best_policy_fit"
        assert CapacityDecisionReason.FAILOVER.value == "failover"
        assert CapacityDecisionReason.ESCALATION_PATH.value == "escalation_path"
        assert CapacityDecisionReason.LACK_OF_ALTERNATIVES.value == "lack_of_alternatives"
        assert CapacityDecisionReason.UNAVAILABLE_EXCLUDED.value == "unavailable_excluded"

    def test_exported_enum_values(self):
        """Test that enum values are exported for ADG scanner."""
        assert BEST_CAPACITY == CapacityDecisionReason.BEST_CAPACITY
        assert BEST_POLICY_FIT == CapacityDecisionReason.BEST_POLICY_FIT
        assert FAILOVER == CapacityDecisionReason.FAILOVER
        assert ESCALATION_PATH == CapacityDecisionReason.ESCALATION_PATH
        assert LACK_OF_ALTERNATIVES == CapacityDecisionReason.LACK_OF_ALTERNATIVES
        assert UNAVAILABLE_EXCLUDED == CapacityDecisionReason.UNAVAILABLE_EXCLUDED


class TestRouteCapacityMetrics:
    """Tests for RouteCapacityMetrics dataclass."""

    def test_route_capacity_metrics_creation(self):
        """Test creating RouteCapacityMetrics."""
        metrics = RouteCapacityMetrics.create(
            route_name="R1",
            queue_depth=5,
            in_flight_work=10,
            recent_latency_ms=100.0,
            failure_rate=0.01,
            degradation_state=RouteDegradationState.HEALTHY,
        )
        assert metrics.route_name == "R1"
        assert metrics.queue_depth == 5
        assert metrics.in_flight_work == 10
        assert metrics.recent_latency_ms == 100.0
        assert metrics.failure_rate == 0.01
        assert metrics.degradation_state == RouteDegradationState.HEALTHY

    def test_route_capacity_metrics_defaults(self):
        """Test RouteCapacityMetrics with default values."""
        metrics = RouteCapacityMetrics.create(route_name="R1")
        assert metrics.queue_depth == 0
        assert metrics.in_flight_work == 0
        assert metrics.recent_latency_ms == 0.0
        assert metrics.failure_rate == 0.0
        assert metrics.degradation_state == RouteDegradationState.HEALTHY

    def test_route_capacity_metrics_is_frozen(self):
        """Test that RouteCapacityMetrics is frozen."""
        metrics = RouteCapacityMetrics.create(route_name="R1")
        with pytest.raises(Exception):  # FrozenInstanceError
            metrics.queue_depth = 10

    def test_is_available_for_routing_healthy(self):
        """Test is_available_for_routing for healthy route."""
        metrics = RouteCapacityMetrics.create(
            route_name="R1",
            degradation_state=RouteDegradationState.HEALTHY,
        )
        assert metrics.is_available_for_routing() is True

    def test_is_available_for_routing_unavailable(self):
        """Test is_available_for_routing for unavailable route."""
        metrics = RouteCapacityMetrics.create(
            route_name="R1",
            degradation_state=RouteDegradationState.UNAVAILABLE,
        )
        assert metrics.is_available_for_routing() is False

    def test_get_capacity_score_healthy(self):
        """Test get_capacity_score for healthy route."""
        metrics = RouteCapacityMetrics.create(
            route_name="R1",
            queue_depth=10,
            in_flight_work=20,
            recent_latency_ms=100.0,
            failure_rate=0.01,
            degradation_state=RouteDegradationState.HEALTHY,
        )
        score = metrics.get_capacity_score()
        assert score == 10 * 1.0 + 20 * 0.5 + 100.0 * 0.001 + 0.01 * 10.0

    def test_get_capacity_score_degraded(self):
        """Test get_capacity_score for degraded route includes penalty."""
        metrics = RouteCapacityMetrics.create(
            route_name="R1",
            queue_depth=10,
            in_flight_work=20,
            recent_latency_ms=100.0,
            failure_rate=0.01,
            degradation_state=RouteDegradationState.DEGRADED,
        )
        score = metrics.get_capacity_score()
        assert score == (10 * 1.0 + 20 * 0.5 + 100.0 * 0.001 + 0.01 * 10.0) + 50.0

    def test_get_capacity_score_saturated(self):
        """Test get_capacity_score for saturated route includes penalty."""
        metrics = RouteCapacityMetrics.create(
            route_name="R1",
            queue_depth=10,
            in_flight_work=20,
            recent_latency_ms=100.0,
            failure_rate=0.01,
            degradation_state=RouteDegradationState.SATURATED,
        )
        score = metrics.get_capacity_score()
        assert score == (10 * 1.0 + 20 * 0.5 + 100.0 * 0.001 + 0.01 * 10.0) + 100.0

    def test_get_capacity_score_unavailable(self):
        """Test get_capacity_score for unavailable route returns infinity."""
        metrics = RouteCapacityMetrics.create(
            route_name="R1",
            degradation_state=RouteDegradationState.UNAVAILABLE,
        )
        score = metrics.get_capacity_score()
        assert score == float("inf")


class TestCapacitySnapshot:
    """Tests for CapacitySnapshot dataclass."""

    def test_capacity_snapshot_create(self):
        """Test creating CapacitySnapshot via factory."""
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(route_name="R1", queue_depth=5, in_flight_work=10),
            "R2": RouteCapacityMetrics.create(route_name="R2", queue_depth=3, in_flight_work=7),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1", "R2"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        assert snapshot.run_id == "run-123"
        assert snapshot.trace_id == "trace-123"
        assert snapshot.candidate_route_count == 2
        assert snapshot.queue_depth_by_candidate["R1"] == 5
        assert snapshot.queue_depth_by_candidate["R2"] == 3

    def test_capacity_snapshot_is_frozen(self):
        """Test that CapacitySnapshot is frozen."""
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(route_name="R1"),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            snapshot.run_id = "new-run"

    def test_get_chosen_route_metrics(self):
        """Test getting metrics for chosen route."""
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(route_name="R1", queue_depth=5),
            "R2": RouteCapacityMetrics.create(route_name="R2", queue_depth=3),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1", "R2"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        metrics = snapshot.get_chosen_route_metrics()
        assert metrics is not None
        assert metrics.route_name == "R1"
        assert metrics.queue_depth == 5

    def test_get_chosen_route_metrics_not_found(self):
        """Test getting metrics when chosen route not found."""
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(route_name="R1", queue_depth=5),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R2",  # Not in candidates
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        metrics = snapshot.get_chosen_route_metrics()
        assert metrics is None

    def test_has_unavailable_chosen_route(self):
        """Test detection of unavailable chosen route."""
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(
                route_name="R1",
                degradation_state=RouteDegradationState.UNAVAILABLE,
            ),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.LACK_OF_ALTERNATIVES,
        )
        assert snapshot.has_unavailable_chosen_route() is True

    def test_has_unavailable_chosen_route_healthy(self):
        """Test that healthy route is not flagged as unavailable."""
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(
                route_name="R1",
                degradation_state=RouteDegradationState.HEALTHY,
            ),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        assert snapshot.has_unavailable_chosen_route() is False

    def test_has_degraded_chosen_route_without_reason(self):
        """Test detection of degraded route without capacity reason."""
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(
                route_name="R1",
                degradation_state=RouteDegradationState.DEGRADED,
            ),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_POLICY_FIT,
        )
        assert snapshot.has_degraded_chosen_route_without_reason() is True

    def test_has_degraded_chosen_route_with_reason(self):
        """Test that degraded route with capacity reason is not flagged."""
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(
                route_name="R1",
                degradation_state=RouteDegradationState.DEGRADED,
            ),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        assert snapshot.has_degraded_chosen_route_without_reason() is False


class TestCapacityRegistry:
    """Tests for CapacityRegistry class."""

    def setup_method(self):
        """Reset registry before each test."""
        reset_capacity_registry()

    def test_singleton_pattern(self):
        """Test that CapacityRegistry is a singleton."""
        registry1 = get_capacity_registry()
        registry2 = get_capacity_registry()
        assert registry1 is registry2

    def test_persist_snapshot(self):
        """Test persisting a capacity snapshot."""
        registry = get_capacity_registry()
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(route_name="R1", queue_depth=5),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        registry.persist_snapshot(snapshot)
        assert registry.query_by_snapshot_id(snapshot.capacity_snapshot_id) is snapshot

    def test_query_by_run_id(self):
        """Test querying snapshots by run_id."""
        registry = get_capacity_registry()
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(route_name="R1"),
        }
        snapshot1 = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-1",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        snapshot2 = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-2",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        snapshot3 = CapacitySnapshot.create(
            run_id="run-456",
            trace_id="trace-3",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        registry.persist_snapshot(snapshot1)
        registry.persist_snapshot(snapshot2)
        registry.persist_snapshot(snapshot3)

        results = registry.query_by_run_id("run-123")
        assert len(results) == 2
        assert snapshot1 in results
        assert snapshot2 in results
        assert snapshot3 not in results

    def test_query_by_trace_id(self):
        """Test querying snapshots by trace_id."""
        registry = get_capacity_registry()
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(route_name="R1"),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        registry.persist_snapshot(snapshot)

        results = registry.query_by_trace_id("trace-123")
        assert len(results) == 1
        assert results[0] is snapshot

    def test_query_by_router_id(self):
        """Test querying snapshots by router_id."""
        registry = get_capacity_registry()
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(route_name="R1"),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        registry.persist_snapshot(snapshot)

        results = registry.query_by_router_id("router-123")
        assert len(results) == 1
        assert results[0] is snapshot

    def test_query_by_snapshot_id(self):
        """Test querying snapshot by snapshot_id."""
        registry = get_capacity_registry()
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(route_name="R1"),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        registry.persist_snapshot(snapshot)

        result = registry.query_by_snapshot_id(snapshot.capacity_snapshot_id)
        assert result is snapshot

    def test_query_by_snapshot_id_not_found(self):
        """Test querying non-existent snapshot returns None."""
        registry = get_capacity_registry()
        result = registry.query_by_snapshot_id("nonexistent")
        assert result is None

    def test_get_snapshot_count(self):
        """Test getting snapshot count."""
        registry = get_capacity_registry()
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(route_name="R1"),
        }
        snapshot1 = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-1",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        snapshot2 = CapacitySnapshot.create(
            run_id="run-456",
            trace_id="trace-2",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        registry.persist_snapshot(snapshot1)
        registry.persist_snapshot(snapshot2)

        assert registry.get_snapshot_count() == 2
        assert registry.get_snapshot_count(run_id="run-123") == 1
        assert registry.get_snapshot_count(run_id="run-456") == 1

    def test_verify_snapshot_exists(self):
        """Test verifying snapshot exists."""
        registry = get_capacity_registry()
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(route_name="R1"),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        registry.persist_snapshot(snapshot)

        assert registry.verify_snapshot_exists(snapshot.capacity_snapshot_id) is True
        assert registry.verify_snapshot_exists("nonexistent") is False

    def test_verify_capacity_metrics_present(self):
        """Test verifying capacity metrics are present."""
        registry = get_capacity_registry()
        capacity_metrics = {
            "R1": RouteCapacityMetrics.create(route_name="R1", queue_depth=5, in_flight_work=10),
        }
        snapshot = CapacitySnapshot.create(
            run_id="run-123",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="router-123",
            candidate_routes=["R1"],
            chosen_route="R1",
            capacity_metrics=capacity_metrics,
            decision_reason=CapacityDecisionReason.BEST_CAPACITY,
        )
        registry.persist_snapshot(snapshot)

        assert registry.verify_capacity_metrics_present(snapshot.capacity_snapshot_id) is True
        assert registry.verify_capacity_metrics_present("nonexistent") is False


class TestResetCapacityRegistry:
    """Tests for reset_capacity_registry function."""

    def test_reset_clears_singleton(self):
        """Test that reset clears the singleton instance."""
        registry1 = get_capacity_registry()
        reset_capacity_registry()
        registry2 = get_capacity_registry()
        # Should be a new instance
        assert registry1 is not registry2


class TestRoutingCapacityError:
    """Tests for RoutingCapacityError exception."""

    def test_routing_capacity_error(self):
        """Test that RoutingCapacityError can be raised."""
        with pytest.raises(RoutingCapacityError, match="test error"):
            raise RoutingCapacityError("test error")
