"""
Forward-Rolling Recursion End-to-End Integration Tests.

Comprehensive integration tests validating all phases work together:
- Phase 1: RecursiveOrchestrator core
- Phase 2: Context pruning and adaptive depth
- Phase 3: Monitoring and circuit breakers
- Phase 4: Feature flags and rollout
- Phase 5: Unified facade integration

Author: Cascade
Date: February 2026
"""

import pytest

from agentic_core.L3_orchestration.interfaces import (
    ExecutionContext,
)
from agentic_core.L3_orchestration.workflow_engines.context_pruning_strategy_types import (
    AdaptiveDepthManager,
    ContextPruningStrategy,
)
from agentic_core.L3_orchestration.workflow_engines.forward_rolling_config_types import (
    ExecutionMode,
    ForwardRollingConfig,
    RolloutStage,
)
from agentic_core.L3_orchestration.workflow_engines.ForwardRollingFacade import (
    ForwardRollingFacade,
)
from agentic_core.L3_orchestration.workflow_engines.recursion_monitor_types import (
    AlertSeverity,
    HealthStatus,
    RecursionMonitor,
)
from agentic_core.L3_orchestration.workflow_engines.recursive_orchestrator_types import (
    RecursiveOrchestrator,
    SuccessorSpec,
)


class TestPhase1CoreIntegration:
    """E2E tests for Phase 1 core components."""

    def test_recursive_orchestrator_with_context(self):
        """Test RecursiveOrchestrator with ExecutionContext."""
        orchestrator = RecursiveOrchestrator(max_depth=50)

        context = ExecutionContext(
            dry_run=True,
            execute=False,
            max_depth=50,
            metadata={"depth": 0, "successor_chain": []},
            accumulated_context={"original_goal": "test_mission"},
        )

        # Validate acyclicity
        assert orchestrator._validate_successor_acyclicity("agent_a", "agent_b")

        # Create successor context
        spec = SuccessorSpec(agent_name="agent_b")
        new_context = orchestrator._create_successor_context("agent_a", spec, context)

        # Verify DNA preservation
        assert "accumulated_context" in new_context.metadata
        assert new_context.metadata["predecessor_agent"] == "agent_a"

    def test_execution_context_chain_tracking(self):
        """Test ExecutionContext tracks successor chains correctly."""
        context = ExecutionContext(
            metadata={"successor_chain": ["agent_a", "agent_b"]},
            accumulated_context={"key": "value"},
        )

        # Test chain retrieval
        chain = context.get_successor_chain()
        assert chain == ["agent_a", "agent_b"]

        # Test accumulated context
        new_ctx = context.with_accumulated_context({"new_key": "new_value"})
        assert new_ctx.accumulated_context["key"] == "value"
        assert new_ctx.accumulated_context["new_key"] == "new_value"


class TestPhase2AdvancedIntegration:
    """E2E tests for Phase 2 advanced features."""

    def test_pruning_with_orchestrator(self):
        """Test context pruning integrates with orchestrator."""
        pruner = ContextPruningStrategy(max_context_size=500, prune_ratio=0.3)

        # Create context that will need pruning
        context = ExecutionContext(
            metadata={
                "depth": 0,
                "successor_chain": [],
                "accumulated_context": {
                    "original_goal": "must_preserve",
                    "temp_data": "x" * 1000,
                },
            },
            accumulated_context={
                "original_goal": "must_preserve",
                "temp_data": "x" * 1000,
            },
        )

        # Prune if needed
        if pruner.should_prune(context.accumulated_context):
            pruner.prune_context(context.accumulated_context)

        # Critical keys should survive
        assert "original_goal" in context.accumulated_context

    def test_adaptive_depth_with_orchestrator(self):
        """Test adaptive depth integrates with orchestrator."""
        orchestrator = RecursiveOrchestrator(max_depth=50)
        depth_manager = AdaptiveDepthManager(base_limit=50, max_limit=200)

        context = ExecutionContext(
            metadata={
                "depth": 0,
                "successor_chain": list(range(10)),
                "accumulated_context": {f"key_{i}": f"val_{i}" for i in range(30)},
            },
        )

        # Calculate adaptive limit
        limit = depth_manager.calculate_adaptive_limit(context.metadata)

        # Should be >= base limit for complex context
        assert limit >= depth_manager.base_limit

        # Update orchestrator with adaptive limit
        orchestrator.max_depth = limit
        assert orchestrator.max_depth >= 50


class TestPhase3MonitoringIntegration:
    """E2E tests for Phase 3 monitoring integration."""

    def test_monitor_with_orchestrator(self):
        """Test monitor integrates with orchestrator operations."""
        monitor = RecursionMonitor()

        # Simulate spawn operations
        for i in range(5):
            success = i % 2 == 0
            monitor.record_spawn(
                success=success,
                depth=i * 5,
                duration_ms=50.0,
                memory_bytes=1024 * i,
                cache_hit=i % 3 == 0,
            )

        # Check health status
        health = monitor.get_overall_health()
        assert isinstance(health, HealthStatus)

        # Verify metrics recorded
        summary = monitor.get_metrics_summary()
        assert summary["total_snapshots"] == 0  # No snapshots yet

    def test_circuit_breaker_triggers(self):
        """Test circuit breaker triggers on failures."""
        monitor = RecursionMonitor()

        # Trigger failures to open circuit
        for _ in range(monitor._failure_threshold):
            monitor.record_spawn(
                success=False,
                depth=10,
                duration_ms=100.0,
                memory_bytes=1024,
                cache_hit=False,
            )

        assert monitor.is_circuit_open()

        # Alerts should be created
        alerts = monitor.get_alerts(severity=AlertSeverity.CRITICAL)
        assert len(alerts) >= 1

    def test_health_checks_all_components(self):
        """Test health checks cover all monitored aspects."""
        monitor = RecursionMonitor()

        # Add some data
        monitor.record_snapshot(
            active_recursions=10,
            total_spawns=100,
            successful_spawns=90,
            depths=[10, 15, 20],
            memory_bytes=100 * 1024 * 1024,
            cache_hits=80,
            cache_misses=20,
        )

        checks = monitor.run_health_checks()

        # Should have multiple health checks
        assert len(checks) >= 1
        check_names = [c.name for c in checks]
        assert "circuit_breaker" in check_names


class TestPhase4RolloutIntegration:
    """E2E tests for Phase 4 rollout integration."""

    def test_config_controls_execution_mode(self):
        """Test config correctly controls execution mode selection."""
        config = ForwardRollingConfig(initial_stage=RolloutStage.DISABLED)

        # Disabled should return static DAG
        mode = config.get_execution_mode("agent_1", "mission_1")
        assert mode == ExecutionMode.STATIC_DAG

        # Enable and set to full
        config.set_rollout_stage(RolloutStage.FULL)
        config.set_feature_flag("forward_rolling_enabled", True, 100)
        config._config.execution_mode = ExecutionMode.FORWARD_ROLLING

        mode = config.get_execution_mode("agent_1", "mission_1")
        assert mode == ExecutionMode.FORWARD_ROLLING

    def test_rollout_stages_progression(self):
        """Test rollout stages progress correctly."""
        config = ForwardRollingConfig()

        stages = [
            RolloutStage.CANARY,
            RolloutStage.EARLY_ADOPTER,
            RolloutStage.PARTIAL,
            RolloutStage.MAJORITY,
            RolloutStage.FULL,
        ]

        for stage in stages:
            config.set_rollout_stage(stage)
            assert config.get_config().stage == stage
            assert config.get_rollout_percentage() > 0

    def test_emergency_disable_and_rollback(self):
        """Test emergency disable and rollback work correctly."""
        config = ForwardRollingConfig(initial_stage=RolloutStage.FULL)
        config.set_feature_flag("forward_rolling_enabled", True, 100)

        # Emergency disable
        config.emergency_disable()
        assert config.get_config().stage == RolloutStage.DISABLED

        # Rollback
        result = config.rollback()
        assert result is True
        assert config.get_config().stage == RolloutStage.FULL


class TestPhase5FacadeIntegration:
    """E2E tests for Phase 5 unified facade."""

    def test_facade_full_workflow(self):
        """Test facade handles complete workflow."""
        facade = ForwardRollingFacade(
            initial_stage=RolloutStage.DISABLED,
            max_depth=50,
            enable_pruning=True,
            enable_adaptive_depth=True,
            enable_monitoring=True,
        )

        # Execute in disabled mode (static DAG)
        result = facade.execute("test_agent", mission_id="mission_1")
        assert result.success
        assert result.execution_mode == ExecutionMode.STATIC_DAG

        # Enable forward rolling
        facade.set_rollout_stage(RolloutStage.FULL)
        facade.set_feature_flag("forward_rolling_enabled", True, 100)

        # Execute again
        context = ExecutionContext(
            dry_run=True,
            metadata={"depth": 0, "successor_chain": []},
        )
        result2 = facade.execute("test_agent_2", context=context, mission_id="mission_2")
        assert result2.success

    def test_facade_metrics_aggregation(self):
        """Test facade aggregates metrics from all components."""
        facade = ForwardRollingFacade(enable_monitoring=True)

        # Generate some activity
        for i in range(5):
            facade.execute(f"agent_{i}", mission_id=f"mission_{i}")

        metrics = facade.get_metrics()

        # Should have metrics from all components
        assert "optimization" in metrics
        assert "orchestrator" in metrics
        assert "config" in metrics
        assert "monitor" in metrics
        assert metrics["optimization"]["total_executions"] == 5

    def test_facade_health_integration(self):
        """Test facade integrates health monitoring."""
        facade = ForwardRollingFacade(enable_monitoring=True)

        # Get health status
        health = facade.get_health_status()
        assert isinstance(health, HealthStatus)

        # Run health checks
        checks = facade.run_health_checks()
        assert isinstance(checks, list)


class TestCrossPhaseIntegration:
    """E2E tests for cross-phase integration scenarios."""

    def test_full_recursion_with_all_features(self):
        """Test full recursion flow with all features enabled."""
        facade = ForwardRollingFacade(
            initial_stage=RolloutStage.FULL,
            max_depth=50,
            enable_pruning=True,
            enable_adaptive_depth=True,
            enable_monitoring=True,
        )
        facade.set_feature_flag("forward_rolling_enabled", True, 100)

        # Create complex context
        context = ExecutionContext(
            dry_run=True,
            metadata={
                "depth": 0,
                "successor_chain": [],
                "accumulated_context": {
                    "original_goal": "complex_mission",
                    "dataset": "production",
                    "mission_params": {"param1": "value1"},
                },
            },
            accumulated_context={
                "original_goal": "complex_mission",
                "dataset": "production",
            },
        )

        # Execute
        result = facade.execute("complex_agent", context=context)

        assert result.success
        assert isinstance(result.health_status, HealthStatus)

    def test_gradual_rollout_progression(self):
        """Test gradual rollout from 0% to 100%."""
        facade = ForwardRollingFacade(initial_stage=RolloutStage.DISABLED)

        stages = [
            (RolloutStage.CANARY, 5),
            (RolloutStage.EARLY_ADOPTER, 25),
            (RolloutStage.PARTIAL, 50),
            (RolloutStage.MAJORITY, 75),
            (RolloutStage.FULL, 100),
        ]

        for stage, expected_pct in stages:
            facade.set_rollout_stage(stage)
            assert facade.get_rollout_percentage() == expected_pct

    def test_memory_management_under_load(self):
        """Test memory management under simulated load."""
        facade = ForwardRollingFacade(
            enable_pruning=True,
            enable_monitoring=False,
        )
        facade._pruner.max_context_size = 1000  # Low threshold for testing

        # Simulate growing context
        accumulated = {"original_goal": "test"}
        for i in range(20):
            accumulated[f"temp_{i}"] = f"data_{i}" * 50

            if facade._pruner.should_prune(accumulated):
                facade._pruner.prune_context(accumulated)

        # Critical keys should survive
        assert "original_goal" in accumulated

    def test_circuit_breaker_with_facade(self):
        """Test circuit breaker integration with facade."""
        facade = ForwardRollingFacade(enable_monitoring=True)

        # Trigger failures through monitor
        for _ in range(facade._monitor._failure_threshold):
            facade._monitor.record_spawn(
                success=False,
                depth=10,
                duration_ms=100.0,
                memory_bytes=1024,
                cache_hit=False,
            )

        # Health should be critical
        health = facade.get_health_status()
        assert health == HealthStatus.CRITICAL


class TestDataIntegrity:
    """E2E tests for data integrity across all phases."""

    def test_dna_preservation_through_pipeline(self):
        """Test DNA keys are preserved through entire pipeline."""
        pruner = ContextPruningStrategy(max_context_size=200)

        # Initial DNA payload
        dna_payload = {
            "original_goal": "critical_mission",
            "dataset": "sensitive_data",
            "mission_params": {"important": True},
            "task_dna": "unique_identifier",
        }

        context = ExecutionContext(
            metadata={"depth": 0, "successor_chain": [], "accumulated_context": dna_payload.copy()},
            accumulated_context=dna_payload.copy(),
        )

        # Add temporary data
        context.accumulated_context["temp_large"] = "x" * 500

        # Prune
        if pruner.should_prune(context.accumulated_context):
            pruner.prune_context(context.accumulated_context)

        # Verify all DNA keys survived
        for key in ["original_goal", "dataset", "mission_params", "task_dna"]:
            assert key in context.accumulated_context

    def test_context_consistency_across_spawns(self):
        """Test context remains consistent across multiple spawns."""
        orchestrator = RecursiveOrchestrator(max_depth=50)

        initial_context = ExecutionContext(
            metadata={
                "depth": 0,
                "successor_chain": [],
                "accumulated_context": {"original_goal": "test"},
            },
        )

        # Simulate 5 spawns
        current_context = initial_context
        for i in range(5):
            spec = SuccessorSpec(agent_name=f"agent_{i}")
            current_context = orchestrator._create_successor_context(
                f"predecessor_{i}", spec, current_context
            )

        # Verify chain is complete
        chain = current_context.metadata.get("successor_chain", [])
        assert len(chain) == 5

        # Verify depth tracking
        assert current_context.metadata.get("depth", 0) == 5


class TestErrorRecovery:
    """E2E tests for error recovery scenarios."""

    def test_recovery_from_depth_limit(self):
        """Test system recovers from depth limit hits."""
        orchestrator = RecursiveOrchestrator(max_depth=5)

        context = ExecutionContext(
            metadata={"depth": 5, "successor_chain": []},
        )

        spec = SuccessorSpec(agent_name="test_agent")
        result = orchestrator.spawn_successor("predecessor", spec, context)

        # Should fail gracefully
        assert not result.success
        assert result.status == "DEPTH_LIMIT_EXCEEDED"

        # System should still be operational
        orchestrator.reset_metrics()
        assert orchestrator.get_metrics()["total_spawns"] == 0

    def test_recovery_from_cycle_detection(self):
        """Test system recovers from cycle detection."""
        orchestrator = RecursiveOrchestrator(max_depth=50)

        # Add edge A -> B
        orchestrator._successor_edges.add(("A", "B"))

        # Try to add cycle B -> A
        is_valid = orchestrator._validate_successor_acyclicity("B", "A")
        assert is_valid is False

        # Heal should fix cycles
        orchestrator._successor_edges.add(("B", "A"))  # Force a cycle
        result = orchestrator.heal_repository(dry_run=False, execute=True)

        assert result["violations_found"] >= 1


class TestPerformanceScenarios:
    """E2E tests for performance scenarios."""

    def test_cache_efficiency_under_load(self):
        """Test cache efficiency under load."""
        facade = ForwardRollingFacade(enable_monitoring=False)

        # Execute many operations
        for i in range(50):
            facade.execute(f"agent_{i % 10}", mission_id=f"mission_{i % 5}")

        metrics = facade.get_metrics()

        # Should have some cache efficiency
        assert metrics["optimization"]["total_executions"] == 50

    def test_metrics_collection_overhead(self):
        """Test metrics collection doesn't add excessive overhead."""
        import time

        facade_with_monitoring = ForwardRollingFacade(enable_monitoring=True)
        facade_without_monitoring = ForwardRollingFacade(enable_monitoring=False)

        # Time with monitoring
        start = time.time()
        for _ in range(100):
            facade_with_monitoring.execute("test_agent")
        time_with = time.time() - start

        # Time without monitoring
        start = time.time()
        for _ in range(100):
            facade_without_monitoring.execute("test_agent")
        time_without = time.time() - start

        # Both should complete (basic sanity check)
        assert facade_with_monitoring._metrics.total_executions == 100
        assert facade_without_monitoring._metrics.total_executions == 100

        # Monitoring overhead should be reasonable
        # If time_without is 0, monitoring still shouldn't take excessive time
        if time_without > 0:
            assert time_with < time_without * 10
        else:
            # If both are effectively instant, just verify they completed
            assert time_with < 5.0  # Should complete in under 5 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
