"""
Unit Tests for Unified Agent Monitor - Phase 7

Tests the monitoring and observability infrastructure including:
- Execution metrics recording
- Aggregated metrics calculation
- Health status reporting
- Execution timer context manager
"""

from __future__ import annotations

import pytest
import time
from datetime import datetime

from agentic_core.base_agents.unified_agent_monitor import (
    ExecutionMetrics,
    AggregatedMetrics,
    UnifiedAgentMonitor,
    ExecutionTimer,
    get_monitor,
)


class TestExecutionMetrics:
    """Tests for ExecutionMetrics dataclass."""

    def test_creation(self):
        """Test ExecutionMetrics creation."""
        metric = ExecutionMetrics(
            agent_name="TestAgent",
            category="validator",
            strategy_type="ValidatorStrategy",
            execution_time_ms=100.5,
            success=True,
        )

        assert metric.agent_name == "TestAgent"
        assert metric.category == "validator"
        assert metric.strategy_type == "ValidatorStrategy"
        assert metric.execution_time_ms == 100.5
        assert metric.success is True
        assert isinstance(metric.timestamp, datetime)

    def test_with_metadata(self):
        """Test ExecutionMetrics with metadata."""
        metric = ExecutionMetrics(
            agent_name="TestAgent",
            category="healer",
            strategy_type="HealingStrategy",
            execution_time_ms=50.0,
            success=False,
            metadata={"error": "test error"},
        )

        assert metric.metadata == {"error": "test error"}


class TestAggregatedMetrics:
    """Tests for AggregatedMetrics dataclass."""

    def test_default_values(self):
        """Test AggregatedMetrics default values."""
        metrics = AggregatedMetrics()

        assert metrics.total_executions == 0
        assert metrics.successful_executions == 0
        assert metrics.failed_executions == 0
        assert metrics.total_execution_time_ms == 0.0
        assert metrics.avg_execution_time_ms == 0.0
        assert metrics.executions_by_category == {}
        assert metrics.executions_by_strategy == {}


class TestUnifiedAgentMonitor:
    """Tests for UnifiedAgentMonitor class."""

    @pytest.fixture
    def monitor(self):
        """Create a fresh monitor instance."""
        # Reset singleton for testing
        UnifiedAgentMonitor._instance = None
        return UnifiedAgentMonitor()

    def test_singleton_pattern(self, monitor):
        """Test monitor uses singleton pattern."""
        monitor2 = UnifiedAgentMonitor()
        assert monitor is monitor2

    def test_record_execution(self, monitor):
        """Test recording an execution."""
        monitor.record_execution(
            agent_name="TestAgent",
            category="validator",
            strategy_type="ValidatorStrategy",
            execution_time_ms=100.0,
            success=True,
        )

        metrics = monitor.get_metrics()
        assert metrics.total_executions == 1
        assert metrics.successful_executions == 1
        assert metrics.failed_executions == 0

    def test_record_failed_execution(self, monitor):
        """Test recording a failed execution."""
        monitor.record_execution(
            agent_name="TestAgent",
            category="healer",
            strategy_type="HealingStrategy",
            execution_time_ms=50.0,
            success=False,
        )

        metrics = monitor.get_metrics()
        assert metrics.total_executions == 1
        assert metrics.successful_executions == 0
        assert metrics.failed_executions == 1

    def test_aggregated_timing(self, monitor):
        """Test aggregated timing calculations."""
        monitor.record_execution(
            agent_name="Agent1",
            category="validator",
            strategy_type="ValidatorStrategy",
            execution_time_ms=100.0,
            success=True,
        )
        monitor.record_execution(
            agent_name="Agent2",
            category="validator",
            strategy_type="ValidatorStrategy",
            execution_time_ms=200.0,
            success=True,
        )

        metrics = monitor.get_metrics()
        assert metrics.total_execution_time_ms == 300.0
        assert metrics.avg_execution_time_ms == 150.0
        assert metrics.min_execution_time_ms == 100.0
        assert metrics.max_execution_time_ms == 200.0

    def test_category_tracking(self, monitor):
        """Test execution tracking by category."""
        monitor.record_execution(
            agent_name="Agent1",
            category="validator",
            strategy_type="ValidatorStrategy",
            execution_time_ms=100.0,
            success=True,
        )
        monitor.record_execution(
            agent_name="Agent2",
            category="healer",
            strategy_type="HealingStrategy",
            execution_time_ms=50.0,
            success=True,
        )
        monitor.record_execution(
            agent_name="Agent3",
            category="validator",
            strategy_type="ValidatorStrategy",
            execution_time_ms=75.0,
            success=True,
        )

        metrics = monitor.get_metrics()
        assert metrics.executions_by_category["validator"] == 2
        assert metrics.executions_by_category["healer"] == 1

    def test_strategy_tracking(self, monitor):
        """Test execution tracking by strategy."""
        monitor.record_execution(
            agent_name="Agent1",
            category="validator",
            strategy_type="ValidatorStrategy",
            execution_time_ms=100.0,
            success=True,
        )
        monitor.record_execution(
            agent_name="Agent2",
            category="orchestrator",
            strategy_type="OrchestrationStrategy",
            execution_time_ms=50.0,
            success=True,
        )

        metrics = monitor.get_metrics()
        assert metrics.executions_by_strategy["ValidatorStrategy"] == 1
        assert metrics.executions_by_strategy["OrchestrationStrategy"] == 1

    def test_health_status_healthy(self, monitor):
        """Test health status when healthy."""
        for _ in range(10):
            monitor.record_execution(
                agent_name="Agent",
                category="validator",
                strategy_type="ValidatorStrategy",
                execution_time_ms=100.0,
                success=True,
            )

        health = monitor.get_health_status()
        assert health["status"] == "healthy"
        assert health["success_rate"] == 1.0
        assert health["total_executions"] == 10

    def test_health_status_degraded(self, monitor):
        """Test health status when degraded."""
        # 4 failures out of 10 = 60% success rate
        for i in range(10):
            monitor.record_execution(
                agent_name="Agent",
                category="validator",
                strategy_type="ValidatorStrategy",
                execution_time_ms=100.0,
                success=(i < 6),
            )

        health = monitor.get_health_status()
        assert health["status"] == "degraded"
        assert health["success_rate"] == 0.6

    def test_get_recent_metrics(self, monitor):
        """Test getting recent metrics."""
        for i in range(5):
            monitor.record_execution(
                agent_name=f"Agent{i}",
                category="validator",
                strategy_type="ValidatorStrategy",
                execution_time_ms=float(i * 10),
                success=True,
            )

        recent = monitor.get_recent_metrics(count=3)
        assert len(recent) == 3
        assert recent[-1].agent_name == "Agent4"

    def test_reset(self, monitor):
        """Test resetting metrics."""
        monitor.record_execution(
            agent_name="Agent",
            category="validator",
            strategy_type="ValidatorStrategy",
            execution_time_ms=100.0,
            success=True,
        )

        monitor.reset()

        metrics = monitor.get_metrics()
        assert metrics.total_executions == 0


class TestExecutionTimer:
    """Tests for ExecutionTimer context manager."""

    @pytest.fixture
    def monitor(self):
        """Create a fresh monitor instance."""
        UnifiedAgentMonitor._instance = None
        return UnifiedAgentMonitor()

    def test_timer_records_execution(self, monitor):
        """Test timer records execution."""
        with ExecutionTimer(
            monitor=monitor,
            agent_name="TestAgent",
            category="validator",
            strategy_type="ValidatorStrategy",
        ):
            time.sleep(0.01)  # 10ms

        metrics = monitor.get_metrics()
        assert metrics.total_executions == 1
        assert metrics.successful_executions == 1
        assert metrics.avg_execution_time_ms >= 10.0

    def test_timer_records_failure(self, monitor):
        """Test timer records failure on exception."""
        try:
            with ExecutionTimer(
                monitor=monitor,
                agent_name="TestAgent",
                category="validator",
                strategy_type="ValidatorStrategy",
            ):
                raise ValueError("Test error")
        except ValueError:
            pass

        metrics = monitor.get_metrics()
        assert metrics.total_executions == 1
        assert metrics.failed_executions == 1

    def test_timer_captures_error_metadata(self, monitor):
        """Test timer captures error in metadata."""
        try:
            with ExecutionTimer(
                monitor=monitor,
                agent_name="TestAgent",
                category="validator",
                strategy_type="ValidatorStrategy",
            ):
                raise ValueError("Test error message")
        except ValueError:
            pass

        recent = monitor.get_recent_metrics(count=1)
        assert "error" in recent[0].metadata
        assert "Test error message" in recent[0].metadata["error"]


class TestGetMonitor:
    """Tests for get_monitor function."""

    def test_returns_singleton(self):
        """Test get_monitor returns singleton."""
        UnifiedAgentMonitor._instance = None

        monitor1 = get_monitor()
        monitor2 = get_monitor()

        assert monitor1 is monitor2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
