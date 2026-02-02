"""
Phase 5 Optimization & Enhancement Test Suite.

Tests for unified facade, performance optimization, and component integration.

Author: Cascade
Date: February 2026
Phase: 5 - Optimization & Enhancement Testing
"""

import pytest

from agentic_core.L3_orchestration.interfaces import ExecutionContext, ExecutionPhase
from agentic_core.L3_orchestration.workflow_engines.ForwardRollingConfig import (
    ExecutionMode,
    RolloutStage,
)
from agentic_core.L3_orchestration.workflow_engines.ForwardRollingFacade import (
    ForwardRollingFacade,
    ForwardRollingResult,
    OptimizationMetrics,
)
from agentic_core.L3_orchestration.workflow_engines.RecursionMonitor import HealthStatus


class TestForwardRollingFacadeInitialization:
    """Test ForwardRollingFacade initialization."""

    def test_default_initialization(self):
        """Test facade initializes with defaults."""
        facade = ForwardRollingFacade()

        assert facade._orchestrator is not None
        assert facade._config is not None
        assert facade._monitor is not None
        assert facade._pruner is not None
        assert facade._depth_manager is not None

    def test_disabled_components(self):
        """Test facade with components disabled."""
        facade = ForwardRollingFacade(
            enable_pruning=False,
            enable_adaptive_depth=False,
            enable_monitoring=False,
        )

        assert facade._pruner is None
        assert facade._depth_manager is None
        assert facade._monitor is None

    def test_custom_initial_stage(self):
        """Test facade with custom initial stage."""
        facade = ForwardRollingFacade(initial_stage=RolloutStage.CANARY)

        assert facade._config.get_config().stage == RolloutStage.CANARY

    def test_custom_max_depth(self):
        """Test facade with custom max depth."""
        facade = ForwardRollingFacade(max_depth=100)

        assert facade._orchestrator.max_depth == 100


class TestFacadeExecution:
    """Test facade execution methods."""

    @pytest.fixture
    def facade(self):
        """Create test facade."""
        return ForwardRollingFacade(
            initial_stage=RolloutStage.DISABLED,
            enable_monitoring=False,
        )

    def test_execute_returns_result(self, facade):
        """Test execute returns ForwardRollingResult."""
        result = facade.execute("test_agent")

        assert isinstance(result, ForwardRollingResult)
        assert result.agent_name == "test_agent"

    def test_execute_disabled_uses_static_dag(self, facade):
        """Test disabled stage uses static DAG."""
        result = facade.execute("test_agent")

        assert result.execution_mode == ExecutionMode.STATIC_DAG

    def test_execute_with_context(self, facade):
        """Test execute with provided context."""
        context = ExecutionContext(
            dry_run=True,
            phase=ExecutionPhase.EXECUTION,
            metadata={"depth": 0},
        )

        result = facade.execute("test_agent", context=context)

        assert result.success

    def test_execute_tracks_metrics(self, facade):
        """Test execution tracks metrics."""
        facade.execute("test_agent")
        facade.execute("test_agent_2")

        assert facade._metrics.total_executions == 2


class TestForwardRollingExecution:
    """Test Forward-Rolling execution mode."""

    @pytest.fixture
    def facade(self):
        """Create facade with Forward-Rolling enabled."""
        f = ForwardRollingFacade(
            initial_stage=RolloutStage.FULL,
            enable_monitoring=False,
        )
        f._config._config.execution_mode = ExecutionMode.FORWARD_ROLLING
        # Enable the feature flag
        f._config.set_feature_flag("forward_rolling_enabled", True, 100)
        return f

    def test_forward_rolling_execution(self, facade):
        """Test Forward-Rolling execution mode."""
        context = ExecutionContext(
            dry_run=True,
            metadata={"depth": 0, "successor_chain": []},
        )

        result = facade.execute("test_agent", context=context)

        # At FULL rollout with feature enabled, should use forward rolling
        assert result.execution_mode == ExecutionMode.FORWARD_ROLLING
        assert facade._metrics.forward_rolling_executions >= 1


class TestResultCaching:
    """Test result caching functionality."""

    @pytest.fixture
    def facade(self):
        """Create test facade with caching."""
        return ForwardRollingFacade(enable_monitoring=False)

    def test_cache_enabled_by_default(self, facade):
        """Test caching is enabled by default."""
        assert facade._cache_enabled is True

    def test_result_cached(self, facade):
        """Test results are cached."""
        facade.execute("agent_1", mission_id="mission_1")

        assert "agent_1:mission_1" in facade._result_cache

    def test_cache_hit(self, facade):
        """Test cache hit returns cached result."""
        facade.execute("agent_1", mission_id="mission_1")
        result = facade.execute("agent_1", mission_id="mission_1", use_cache=True)

        assert result.metadata.get("cache_hit") is True

    def test_cache_bypass(self, facade):
        """Test cache can be bypassed."""
        facade.execute("agent_1", mission_id="mission_1")
        facade.execute("agent_1", mission_id="mission_1", use_cache=False)

        # Should have executed twice (not used cache)
        assert facade._metrics.total_executions == 2

    def test_clear_cache(self, facade):
        """Test clearing cache."""
        facade.execute("agent_1")
        facade.execute("agent_2")

        count = facade.clear_cache()

        assert count == 2
        assert len(facade._result_cache) == 0

    def test_disable_cache(self, facade):
        """Test disabling cache."""
        facade.set_cache_enabled(False)
        facade.execute("agent_1")

        assert len(facade._result_cache) == 0


class TestRolloutControl:
    """Test rollout control methods."""

    @pytest.fixture
    def facade(self):
        """Create test facade."""
        return ForwardRollingFacade()

    def test_set_rollout_stage(self, facade):
        """Test setting rollout stage."""
        facade.set_rollout_stage(RolloutStage.CANARY)

        assert facade._config.get_config().stage == RolloutStage.CANARY

    def test_emergency_disable(self, facade):
        """Test emergency disable."""
        facade.set_rollout_stage(RolloutStage.FULL)
        facade.emergency_disable()

        assert facade._config.get_config().stage == RolloutStage.DISABLED

    def test_rollback(self, facade):
        """Test rollback functionality."""
        facade.set_rollout_stage(RolloutStage.CANARY)
        facade.set_rollout_stage(RolloutStage.PARTIAL)

        result = facade.rollback()

        assert result is True
        assert facade._config.get_config().stage == RolloutStage.CANARY

    def test_is_forward_rolling_enabled(self, facade):
        """Test checking if Forward-Rolling is enabled."""
        assert facade.is_forward_rolling_enabled() is False

        facade.set_rollout_stage(RolloutStage.CANARY)
        assert facade.is_forward_rolling_enabled() is True

    def test_get_rollout_percentage(self, facade):
        """Test getting rollout percentage."""
        facade.set_rollout_stage(RolloutStage.PARTIAL)

        assert facade.get_rollout_percentage() == 50


class TestHealthMonitoring:
    """Test health monitoring integration."""

    @pytest.fixture
    def facade(self):
        """Create facade with monitoring enabled."""
        return ForwardRollingFacade(enable_monitoring=True)

    def test_get_health_status(self, facade):
        """Test getting health status."""
        status = facade.get_health_status()

        assert isinstance(status, HealthStatus)

    def test_run_health_checks(self, facade):
        """Test running health checks."""
        checks = facade.run_health_checks()

        assert isinstance(checks, list)

    def test_health_status_without_monitor(self):
        """Test health status when monitor disabled."""
        facade = ForwardRollingFacade(enable_monitoring=False)

        status = facade.get_health_status()

        assert status == HealthStatus.HEALTHY


class TestFeatureFlags:
    """Test feature flag integration."""

    @pytest.fixture
    def facade(self):
        """Create test facade."""
        return ForwardRollingFacade()

    def test_set_feature_flag(self, facade):
        """Test setting feature flag."""
        facade.set_feature_flag("test_feature", True, 75)

        assert facade.is_feature_enabled("test_feature") is True

    def test_is_feature_enabled(self, facade):
        """Test checking feature enabled."""
        facade.set_feature_flag("enabled_feature", True)
        facade.set_feature_flag("disabled_feature", False)

        assert facade.is_feature_enabled("enabled_feature") is True
        assert facade.is_feature_enabled("disabled_feature") is False


class TestMetrics:
    """Test metrics collection and retrieval."""

    @pytest.fixture
    def facade(self):
        """Create test facade."""
        return ForwardRollingFacade(enable_monitoring=False)

    def test_get_metrics(self, facade):
        """Test getting comprehensive metrics."""
        facade.execute("agent_1")
        facade.execute("agent_2")

        metrics = facade.get_metrics()

        assert "optimization" in metrics
        assert "orchestrator" in metrics
        assert "config" in metrics
        assert metrics["optimization"]["total_executions"] == 2

    def test_metrics_track_execution_mode(self, facade):
        """Test metrics track execution mode distribution."""
        facade.execute("agent_1")

        metrics = facade.get_metrics()

        assert metrics["optimization"]["static_dag_executions"] >= 1


class TestSpawnSuccessor:
    """Test successor spawning."""

    @pytest.fixture
    def facade(self):
        """Create test facade."""
        return ForwardRollingFacade()

    def test_spawn_successor(self, facade):
        """Test spawning a successor."""
        context = ExecutionContext(
            dry_run=True,
            metadata={"depth": 0, "successor_chain": []},
        )

        result = facade.spawn_successor("current_agent", "successor_agent", context)

        assert result is not None
        assert result.agent_name == "successor_agent"


class TestReset:
    """Test reset functionality."""

    def test_reset_clears_all_state(self):
        """Test reset clears all component state."""
        facade = ForwardRollingFacade(enable_monitoring=True)

        # Generate some state
        facade.execute("agent_1")
        facade.execute("agent_2")

        facade.reset()

        assert facade._metrics.total_executions == 0
        assert len(facade._result_cache) == 0
        assert len(facade._execution_times) == 0


class TestForwardRollingResult:
    """Test ForwardRollingResult dataclass."""

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = ForwardRollingResult(
            success=True,
            agent_name="test_agent",
            execution_mode=ExecutionMode.FORWARD_ROLLING,
            depth_reached=10,
            duration_ms=50.0,
            context_size_bytes=1024,
            pruning_performed=False,
            health_status=HealthStatus.HEALTHY,
        )

        d = result.to_dict()

        assert d["success"] is True
        assert d["agent_name"] == "test_agent"
        assert d["execution_mode"] == "forward_rolling"
        assert d["depth_reached"] == 10

    def test_result_with_agent_result(self):
        """Test result with nested agent result."""
        from agentic_core.L3_orchestration.interfaces import AgentResult

        agent_result = AgentResult(
            agent_name="test",
            success=True,
            status="PASS",
        )

        result = ForwardRollingResult(
            success=True,
            agent_name="test_agent",
            execution_mode=ExecutionMode.STATIC_DAG,
            depth_reached=0,
            duration_ms=10.0,
            context_size_bytes=0,
            pruning_performed=False,
            health_status=HealthStatus.HEALTHY,
            agent_result=agent_result,
        )

        d = result.to_dict()

        assert d["agent_result"] is not None
        assert d["agent_result"]["agent_name"] == "test"


class TestOptimizationMetrics:
    """Test OptimizationMetrics dataclass."""

    def test_default_values(self):
        """Test default metric values."""
        metrics = OptimizationMetrics()

        assert metrics.total_executions == 0
        assert metrics.forward_rolling_executions == 0
        assert metrics.static_dag_executions == 0
        assert metrics.fallback_count == 0
        assert metrics.avg_execution_time_ms == 0.0


class TestFallbackBehavior:
    """Test fallback behavior on errors."""

    def test_fallback_on_error(self):
        """Test fallback to static DAG on error."""
        facade = ForwardRollingFacade(
            initial_stage=RolloutStage.FULL,
            enable_monitoring=False,
        )
        facade._config._config.execution_mode = ExecutionMode.FORWARD_ROLLING
        facade._config._config.fallback_on_error = True
        # Enable the feature flag for forward rolling
        facade._config.set_feature_flag("forward_rolling_enabled", True, 100)

        # Mock forward rolling to raise exception
        def mock_error(*args, **kwargs):
            raise RuntimeError("Test error")

        facade._execute_forward_rolling = mock_error

        # Should fall back to static DAG
        result = facade.execute("test_agent")

        assert result.execution_mode == ExecutionMode.STATIC_DAG
        assert facade._metrics.fallback_count >= 1


class TestCacheSizeManagement:
    """Test cache size management."""

    def test_cache_eviction(self):
        """Test cache evicts old entries when full."""
        facade = ForwardRollingFacade(enable_monitoring=False)
        facade._cache_max_size = 5

        # Fill cache beyond max
        for i in range(10):
            facade.execute(f"agent_{i}", mission_id=f"mission_{i}", use_cache=True)

        assert len(facade._result_cache) <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
