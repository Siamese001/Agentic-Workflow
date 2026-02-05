"""
Unit Tests for Facade Migration Monitoring - Phase 4

Tests the monitoring infrastructure for facade migration including:
- Facade execution tracking
- Migration status reporting
- Health status with facade metrics
"""

from __future__ import annotations

import pytest

from agentic_core.base_agents.unified_agent_monitor import (
    AggregatedMetrics,
    UnifiedAgentMonitor,
    get_monitor,
)


class TestFacadeMigrationMonitoring:
    """Tests for facade migration monitoring."""

    @pytest.fixture
    def monitor(self):
        """Create a fresh monitor instance."""
        monitor = UnifiedAgentMonitor()
        monitor.reset()
        return monitor

    def test_aggregated_metrics_has_facade_fields(self):
        """Test AggregatedMetrics has facade tracking fields."""
        metrics = AggregatedMetrics()
        assert hasattr(metrics, "facade_executions")
        assert hasattr(metrics, "facade_agents")
        assert metrics.facade_executions == 0
        assert metrics.facade_agents == {}

    def test_record_facade_execution(self, monitor):
        """Test recording facade executions."""
        monitor.record_facade_execution(
            facade_agent="StructureHealerAgent",
            strategy_type="StructureHealingStrategy",
            execution_time_ms=50.0,
            success=True,
        )

        metrics = monitor.get_metrics()
        assert metrics.facade_executions == 1
        assert "StructureHealerAgent" in metrics.facade_agents
        assert metrics.facade_agents["StructureHealerAgent"] == 1

    def test_record_multiple_facade_executions(self, monitor):
        """Test recording multiple facade executions."""
        # Record multiple executions for different facades
        facades = [
            ("StructureHealerAgent", "StructureHealingStrategy"),
            ("CodeValidatorAgent", "CodeValidatorStrategy"),
            ("StructuralValidatorAgent", "StructuralValidatorStrategy"),
            ("LocationHealerAgent", "LocationHealingStrategy"),
        ]

        for facade, strategy in facades:
            monitor.record_facade_execution(
                facade_agent=facade,
                strategy_type=strategy,
                execution_time_ms=25.0,
                success=True,
            )

        metrics = monitor.get_metrics()
        assert metrics.facade_executions == 4
        assert len(metrics.facade_agents) == 4

    def test_facade_migration_status(self, monitor):
        """Test get_facade_migration_status method."""
        # Record some facade executions
        monitor.record_facade_execution(
            facade_agent="StructureHealerAgent",
            strategy_type="StructureHealingStrategy",
            execution_time_ms=30.0,
            success=True,
        )

        status = monitor.get_facade_migration_status()

        assert status["migration_phase"] == "Phase 4 - Monitoring"
        assert "StructureHealerAgent" in status["converted_facades"]
        assert "CodeValidatorAgent" in status["converted_facades"]
        assert "StructuralValidatorAgent" in status["converted_facades"]
        assert "LocationHealerAgent" in status["converted_facades"]
        assert status["total_facade_calls"] == 1
        assert "StructureHealerAgent" in status["facades_with_activity"]

    def test_facade_migration_status_no_activity(self, monitor):
        """Test migration status with no facade activity."""
        status = monitor.get_facade_migration_status()

        assert status["total_facade_calls"] == 0
        assert status["facades_with_activity"] == []
        # Should be healthy if no executions at all
        assert status["migration_health"] == "healthy"

    def test_health_status_includes_facade_metrics(self, monitor):
        """Test health status includes facade metrics."""
        monitor.record_facade_execution(
            facade_agent="CodeValidatorAgent",
            strategy_type="CodeValidatorStrategy",
            execution_time_ms=40.0,
            success=True,
        )

        health = monitor.get_health_status()

        assert "facade_executions" in health
        assert "facade_agents_active" in health
        assert health["facade_executions"] == 1
        assert "CodeValidatorAgent" in health["facade_agents_active"]

    def test_facade_execution_also_recorded_as_regular(self, monitor):
        """Test facade executions are also recorded as regular executions."""
        monitor.record_facade_execution(
            facade_agent="LocationHealerAgent",
            strategy_type="LocationHealingStrategy",
            execution_time_ms=35.0,
            success=True,
        )

        metrics = monitor.get_metrics()
        assert metrics.total_executions == 1
        assert "facade" in metrics.executions_by_category

    def test_facade_execution_failure_tracking(self, monitor):
        """Test facade execution failure tracking."""
        monitor.record_facade_execution(
            facade_agent="StructuralValidatorAgent",
            strategy_type="StructuralValidatorStrategy",
            execution_time_ms=100.0,
            success=False,
        )

        metrics = monitor.get_metrics()
        assert metrics.facade_executions == 1
        assert metrics.failed_executions == 1


class TestMonitorSingleton:
    """Tests for monitor singleton pattern."""

    def test_get_monitor_returns_singleton(self):
        """Test get_monitor returns singleton instance."""
        monitor1 = get_monitor()
        monitor2 = get_monitor()
        assert monitor1 is monitor2

    def test_monitor_reset_clears_facade_metrics(self):
        """Test reset clears facade metrics."""
        monitor = get_monitor()
        monitor.record_facade_execution(
            facade_agent="StructureHealerAgent",
            strategy_type="StructureHealingStrategy",
            execution_time_ms=20.0,
            success=True,
        )

        monitor.reset()

        metrics = monitor.get_metrics()
        assert metrics.facade_executions == 0
        assert metrics.facade_agents == {}


class TestConvertedFacadesList:
    """Tests for the converted facades list."""

    def test_all_converted_facades_listed(self):
        """Test all Phase 1-3 converted facades are listed."""
        monitor = UnifiedAgentMonitor()
        monitor.reset()

        status = monitor.get_facade_migration_status()
        converted = status["converted_facades"]

        # Phase 1
        assert "StructureHealerAgent" in converted
        # Phase 2
        assert "CodeValidatorAgent" in converted
        assert "StructuralValidatorAgent" in converted
        # Phase 3
        assert "LocationHealerAgent" in converted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
