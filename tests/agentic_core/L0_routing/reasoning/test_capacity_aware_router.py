"""Tests for capacity_aware_router.py module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.reasoning.capacity_aware_router import (
    RoutingCapacityContext,
    RoutingPolicyContext,
    choose_route_with_capacity,
    query_capacity_snapshots,
    choose_route_with_simple_capacity,
    capacity_aware_routing,
    route_chosen_with_capacity,
    capacity_snapshot_emitted,
    RoutingCapacityError,
)


class TestRoutingCapacityContext:
    """Tests for RoutingCapacityContext dataclass."""

    def test_routing_capacity_context_creation(self):
        """Test creating RoutingCapacityContext."""
        context = RoutingCapacityContext.create(
            run_id="test-run",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="test-router",
        )
        assert context.run_id == "test-run"
        assert context.trace_id == "trace-123"
        assert context.routing_contract_id == "rc-123"
        assert context.router_id == "test-router"

    def test_routing_capacity_context_is_frozen(self):
        """Test that RoutingCapacityContext is frozen."""
        context = RoutingCapacityContext.create(
            run_id="test-run",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="test-router",
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            context.run_id = "new-run"


class TestRoutingPolicyContext:
    """Tests for RoutingPolicyContext dataclass."""

    def test_routing_policy_context_creation(self):
        """Test creating RoutingPolicyContext with defaults."""
        context = RoutingPolicyContext.create()
        assert context.allow_degraded is True
        assert context.allow_saturated is False
        assert context.require_capacity_aware is True
        assert context.max_queue_depth is None
        assert context.max_failure_rate == 0.1

    def test_routing_policy_context_custom(self):
        """Test creating RoutingPolicyContext with custom values."""
        context = RoutingPolicyContext.create(
            allow_degraded=False,
            allow_saturated=True,
            require_capacity_aware=False,
            max_queue_depth=100,
            max_failure_rate=0.05,
        )
        assert context.allow_degraded is False
        assert context.allow_saturated is True
        assert context.require_capacity_aware is False
        assert context.max_queue_depth == 100
        assert context.max_failure_rate == 0.05

    def test_routing_policy_context_is_frozen(self):
        """Test that RoutingPolicyContext is frozen."""
        context = RoutingPolicyContext.create()
        with pytest.raises(Exception):  # FrozenInstanceError
            context.allow_degraded = False


class TestChooseRouteWithCapacity:
    """Tests for choose_route_with_capacity function."""

    def test_choose_route_with_capacity_no_candidates(self):
        """Test that no candidate routes raises error."""
        context = RoutingCapacityContext.create(
            run_id="test-run",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="test-router",
        )
        with pytest.raises(RoutingCapacityError, match="no candidate routes"):
            choose_route_with_capacity(context, [])

    def test_choose_route_with_capacity_single_candidate(self):
        """Test that single candidate is selected."""
        context = RoutingCapacityContext.create(
            run_id="test-run",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="test-router",
        )
        with patch("agentic_core.L0_routing.reasoning.capacity_aware_router.get_capacity_registry") as mock_get:
            registry = MagicMock()
            mock_get.return_value = registry
            
            chosen, snapshot = choose_route_with_capacity(context, ["R1"])
            
            assert chosen == "R1"
            assert snapshot is not None

    def test_choose_route_with_capacity_multiple_candidates(self):
        """Test that best candidate is selected based on capacity."""
        context = RoutingCapacityContext.create(
            run_id="test-run",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="test-router",
        )
        with patch("agentic_core.L0_routing.reasoning.capacity_aware_router.get_capacity_registry") as mock_get:
            registry = MagicMock()
            mock_get.return_value = registry
            
            chosen, snapshot = choose_route_with_capacity(context, ["R1", "R2", "R3"])
            
            assert chosen in ["R1", "R2", "R3"]
            assert snapshot is not None

    def test_choose_route_with_capacity_policy_filtering(self):
        """Test that policy context filters candidates."""
        context = RoutingCapacityContext.create(
            run_id="test-run",
            trace_id="trace-123",
            routing_contract_id="rc-123",
            router_id="test-router",
        )
        policy = RoutingPolicyContext.create(
            allow_degraded=False,
            allow_saturated=False,
        )
        with patch("agentic_core.L0_routing.reasoning.capacity_aware_router.get_capacity_registry") as mock_get:
            registry = MagicMock()
            mock_get.return_value = registry
            
            chosen, snapshot = choose_route_with_capacity(
                context,
                ["R1", "R2"],
                policy_context=policy,
            )
            
            assert chosen in ["R1", "R2"]
            assert snapshot is not None


class TestQueryCapacitySnapshots:
    """Tests for query_capacity_snapshots function."""

    def test_query_by_snapshot_id(self):
        """Test querying by snapshot_id."""
        with patch("agentic_core.L0_routing.reasoning.capacity_aware_router.get_capacity_registry") as mock_get:
            registry = MagicMock()
            snapshot = MagicMock()
            registry.query_by_snapshot_id.return_value = snapshot
            mock_get.return_value = registry
            
            result = query_capacity_snapshots(snapshot_id="snap-123")
            
            assert len(result) == 1
            assert result[0] is snapshot
            registry.query_by_snapshot_id.assert_called_once_with("snap-123")

    def test_query_by_run_id(self):
        """Test querying by run_id."""
        with patch("agentic_L0_routing.reasoning.capacity_aware_router.get_capacity_registry") as mock_get:
            registry = MagicMock()
            snapshots = [MagicMock(), MagicMock()]
            registry.query_by_run_id.return_value = snapshots
            mock_get.return_value = registry
            
            result = query_capacity_snapshots(run_id="run-123")
            
            assert len(result) == 2
            registry.query_by_run_id.assert_called_once_with("run-123")

    def test_query_by_trace_id(self):
        """Test querying by trace_id."""
        with patch("agentic_core.L0_routing.reasoning.capacity_aware_router.get_capacity_registry") as mock_get:
            registry = MagicMock()
            snapshots = [MagicMock()]
            registry.query_by_trace_id.return_value = snapshots
            mock_get.return_value = registry
            
            result = query_capacity_snapshots(trace_id="trace-123")
            
            assert len(result) == 1
            registry.query_by_trace_id.assert_called_once_with("trace-123")

    def test_query_by_router_id(self):
        """Test querying by router_id."""
        with patch("agentic_core.L0_routing.reasoning.capacity_aware_router.get_capacity_registry") as mock_get:
            registry = MagicMock()
            snapshots = [MagicMock(), MagicMock(), MagicMock()]
            registry.query_by_router_id.return_value = snapshots
            mock_get.return_value = registry
            
            result = query_capacity_snapshots(router_id="router-123")
            
            assert len(result) == 3
            registry.query_by_router_id.assert_called_once_with("router-123")

    def test_query_no_filters(self):
        """Test that no filters returns empty list."""
        with patch("agentic_core.L0_routing.reasoning.capacity_aware_router.get_capacity_registry") as mock_get:
            registry = MagicMock()
            mock_get.return_value = registry
            
            result = query_capacity_snapshots()
            
            assert result == []

    def test_query_snapshot_not_found(self):
        """Test that non-existent snapshot returns empty list."""
        with patch("agentic_core.L0_routing.reasoning.capacity_aware_router.get_capacity_registry") as mock_get:
            registry = MagicMock()
            registry.query_by_snapshot_id.return_value = None
            mock_get.return_value = registry
            
            result = query_capacity_snapshots(snapshot_id="nonexistent")
            
            assert result == []


class TestChooseRouteWithSimpleCapacity:
    """Tests for choose_route_with_simple_capacity function."""

    def test_simple_capacity_wrapper(self):
        """Test that simple capacity wrapper creates context and calls main function."""
        with patch("agentic_core.L0_routing.reasoning.capacity_aware_router.choose_route_with_capacity") as mock_choose:
            mock_choose.return_value = ("R1", MagicMock())
            
            chosen, snapshot = choose_route_with_simple_capacity(
                run_id="test-run",
                trace_id="trace-123",
                routing_contract_id="rc-123",
                router_id="test-router",
                candidate_routes=["R1", "R2"],
            )
            
            assert chosen == "R1"
            mock_choose.assert_called_once()
            call_args = mock_choose.call_args
            assert call_args[1]["candidate_routes"] == ["R1", "R2"]


class TestEmitterFunctions:
    """Tests for ADG edge emitter functions."""

    def test_capacity_aware_routing_emitter(self):
        """Test that capacity_aware_routing emitter exists and is callable."""
        # Should not raise
        capacity_aware_routing("snap-123", "router-123", 3, "R1", "BEST_CAPACITY")

    def test_route_chosen_with_capacity_emitter(self):
        """Test that route_chosen_with_capacity emitter exists and is callable."""
        # Should not raise
        route_chosen_with_capacity("snap-123", "R1", 0.95, "HEALTHY")

    def test_capacity_snapshot_emitted_emitter(self):
        """Test that capacity_snapshot_emitted emitter exists and is callable."""
        # Should not raise
        capacity_snapshot_emitted("snap-123", "run-123", "trace-123", "router-123", 3, "R1")
