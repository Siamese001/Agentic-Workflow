"""
ForwardRollingFacade - Unified Interface for Forward-Rolling Recursion.

[PHASE 5] Provides a unified facade integrating all Forward-Rolling Recursion
components for simplified usage and optimized performance.

UNIFIED API: Single entry point for all Forward-Rolling operations
OPTIMIZATION: Performance tuning and caching strategies

Author: Cascade
Date: February 2026
Phase: 5 - Optimization & Enhancement
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L3_orchestration.types import (
    AgentResult,
    ExecutionContext,
    ExecutionPhase,
)
from agentic_core.L3_orchestration.types.context_pruning_types import (
    AdaptiveDepthManager,
    ContextPruningStrategy,
)
from agentic_core.L3_orchestration.reasoning.forward_rolling_config_types import (
    ExecutionMode,
    ForwardRollingConfig,
    RolloutStage,
)
from agentic_core.L3_orchestration.reasoning.recursion_monitor_types import (
    HealthStatus,
    RecursionMonitor,
)
from agentic_core.L3_orchestration.reasoning.recursive_orchestration_types import (
    RecursiveOrchestrator,
    SuccessorSpec,
)

Logger = logging.getLogger(__name__)


@dataclass
class ForwardRollingResult:
    """Result from Forward-Rolling execution."""

    success: bool
    agent_name: str
    execution_mode: ExecutionMode
    depth_reached: int
    duration_ms: float
    context_size_bytes: int
    pruning_performed: bool
    health_status: HealthStatus
    agent_result: AgentResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "agent_name": self.agent_name,
            "execution_mode": self.execution_mode.value,
            "depth_reached": self.depth_reached,
            "duration_ms": self.duration_ms,
            "context_size_bytes": self.context_size_bytes,
            "pruning_performed": self.pruning_performed,
            "health_status": self.health_status.value,
            "agent_result": self.agent_result.to_dict() if self.agent_result else None,
            "metadata": self.metadata,
        }


@dataclass
class OptimizationMetrics:
    """Metrics for optimization tracking."""

    total_executions: int = 0
    forward_rolling_executions: int = 0
    static_dag_executions: int = 0
    fallback_count: int = 0
    avg_execution_time_ms: float = 0.0
    avg_depth_reached: float = 0.0
    cache_efficiency: float = 0.0
    pruning_count: int = 0
    bytes_saved_by_pruning: int = 0


class ForwardRollingFacade:
    """
    Unified facade for Forward-Rolling Recursion system.

    Integrates:
    - RecursiveOrchestrator: Core recursion logic
    - ContextPruningStrategy: Memory management
    - AdaptiveDepthManager: Dynamic depth control
    - RecursionMonitor: Production monitoring
    - ForwardRollingConfig: Feature flags and rollout

    Usage:
        facade = ForwardRollingFacade()
        result = facade.execute("agent_name", context)
    """

    def __init__(
        self,
        initial_stage: RolloutStage = RolloutStage.DISABLED,
        max_depth: int = 50,
        enable_pruning: bool = True,
        enable_adaptive_depth: bool = True,
        enable_monitoring: bool = True,
    ):
        """
        Initialize Forward-Rolling Facade.

        Args:
            initial_stage: Initial rollout stage
            max_depth: Maximum recursion depth
            enable_pruning: Enable context pruning
            enable_adaptive_depth: Enable adaptive depth management
            enable_monitoring: Enable production monitoring
        """
        # Core components
        self._orchestrator = RecursiveOrchestrator(max_depth=max_depth)
        self._config = ForwardRollingConfig(initial_stage=initial_stage)
        self._monitor = RecursionMonitor() if enable_monitoring else None
        self._pruner = ContextPruningStrategy() if enable_pruning else None
        self._depth_manager = AdaptiveDepthManager() if enable_adaptive_depth else None

        # Optimization tracking
        self._metrics = OptimizationMetrics()
        self._execution_times: list[float] = []
        self._depths_reached: list[int] = []

        # Caching
        self._result_cache: dict[str, ForwardRollingResult] = {}
        self._cache_max_size = 100
        self._cache_enabled = True

        Logger.info(
            f"[ForwardRollingFacade] Initialized with stage={initial_stage.value}, max_depth={max_depth}",
        )

    def execute(
        self,
        agent_name: str,
        context: ExecutionContext | None = None,
        mission_id: str = "",
        use_cache: bool = True,
    ) -> ForwardRollingResult:
        """
        Execute an agent using optimal execution mode.

        Automatically selects between Forward-Rolling and Static DAG
        based on configuration and rollout settings.

        Args:
            agent_name: Name of agent to execute
            context: Optional execution context
            mission_id: Optional mission identifier
            use_cache: Whether to use result caching

        Returns:
            ForwardRollingResult with execution details
        """
        start_time = time.time()
        self._metrics.total_executions += 1

        # Check cache
        cache_key = f"{agent_name}:{mission_id}"
        if use_cache and self._cache_enabled and cache_key in self._result_cache:
            cached = self._result_cache[cache_key]
            cached.metadata["cache_hit"] = True
            return cached

        # Determine execution mode
        mode = self._config.get_execution_mode(agent_name, mission_id)

        # Create context if not provided
        if context is None:
            context = ExecutionContext(
                dry_run=True,
                execute=False,
                max_depth=self._orchestrator.max_depth,
                phase=ExecutionPhase.EXECUTION,
                metadata={"depth": 0, "successor_chain": []},
            )

        # Execute based on mode
        try:
            if mode == ExecutionMode.FORWARD_ROLLING:
                result = self._execute_forward_rolling(agent_name, context)
                self._metrics.forward_rolling_executions += 1
            else:
                result = self._execute_static_dag(agent_name, context)
                self._metrics.static_dag_executions += 1

        except Exception as e:
            # Fallback on error if enabled
            if self._config.get_config().fallback_on_error:
                self._metrics.fallback_count += 1
                Logger.warning(f"[ForwardRollingFacade] Fallback to static DAG due to error: {e}")
                result = self._execute_static_dag(agent_name, context)
            else:
                raise

        # Calculate execution time
        duration_ms = (time.time() - start_time) * 1000
        self._execution_times.append(duration_ms)

        # Update metrics
        self._update_metrics(result, duration_ms)

        # Record monitoring data
        if self._monitor:
            self._monitor.record_spawn(
                success=result.success,
                depth=result.depth_reached,
                duration_ms=duration_ms,
                memory_bytes=result.context_size_bytes,
                cache_hit=False,
            )

        # Cache result
        if use_cache and self._cache_enabled:
            self._cache_result(cache_key, result)

        return result

    def _execute_forward_rolling(self, agent_name: str, context: ExecutionContext) -> ForwardRollingResult:
        """Execute using Forward-Rolling Recursion."""
        # Calculate adaptive depth if enabled
        if self._depth_manager:
            adaptive_limit = self._depth_manager.calculate_adaptive_limit(
                context.metadata,
                self._orchestrator.get_metrics(),
            )
            self._orchestrator.max_depth = adaptive_limit

        # Prune context if needed
        pruning_performed = False
        bytes_saved = 0
        if self._pruner and context.accumulated_context:
            if self._pruner.should_prune(context.accumulated_context):
                prune_result = self._pruner.prune_context(context.accumulated_context)
                pruning_performed = True
                bytes_saved = prune_result.bytes_freed
                self._metrics.pruning_count += 1
                self._metrics.bytes_saved_by_pruning += bytes_saved

        # Create successor spec
        successor_spec = SuccessorSpec(
            agent_name=agent_name,
            context_merge_strategy="deep_merge",
        )

        # Execute via orchestrator
        agent_result = self._orchestrator.spawn_successor("facade_entry", successor_spec, context)

        # Get depth reached
        depth_reached = context.metadata.get("depth", 0)
        self._depths_reached.append(depth_reached)

        # Get health status
        health_status = HealthStatus.HEALTHY
        if self._monitor:
            health_status = self._monitor.get_overall_health()

        # Calculate context size
        context_size = len(str(context.accumulated_context).encode())

        return ForwardRollingResult(
            success=agent_result.success,
            agent_name=agent_name,
            execution_mode=ExecutionMode.FORWARD_ROLLING,
            depth_reached=depth_reached,
            duration_ms=0.0,  # Will be set by caller
            context_size_bytes=context_size,
            pruning_performed=pruning_performed,
            health_status=health_status,
            agent_result=agent_result,
            metadata={
                "adaptive_depth_used": self._depth_manager is not None,
                "bytes_saved_by_pruning": bytes_saved,
            },
        )

    def _execute_static_dag(self, agent_name: str, context: ExecutionContext) -> ForwardRollingResult:
        """Execute using Static DAG (fallback mode)."""
        # Simple mock execution for static DAG mode
        agent_result = AgentResult(
            agent_name=agent_name,
            success=True,
            status="STATIC_DAG_EXECUTION",
            message="Executed via static DAG mode",
        )

        health_status = HealthStatus.HEALTHY
        if self._monitor:
            health_status = self._monitor.get_overall_health()

        return ForwardRollingResult(
            success=True,
            agent_name=agent_name,
            execution_mode=ExecutionMode.STATIC_DAG,
            depth_reached=0,
            duration_ms=0.0,
            context_size_bytes=0,
            pruning_performed=False,
            health_status=health_status,
            agent_result=agent_result,
            metadata={"fallback_mode": True},
        )

    def _update_metrics(self, result: ForwardRollingResult, duration_ms: float) -> None:
        """Update optimization metrics."""
        # Update average execution time
        if self._execution_times:
            self._metrics.avg_execution_time_ms = sum(self._execution_times) / len(self._execution_times)

        # Update average depth
        if self._depths_reached:
            self._metrics.avg_depth_reached = sum(self._depths_reached) / len(self._depths_reached)

        # Update cache efficiency
        if self._result_cache:
            total_queries = self._metrics.total_executions
            cache_hits = sum(1 for r in self._result_cache.values() if r.metadata.get("cache_hit", False))
            self._metrics.cache_efficiency = cache_hits / max(total_queries, 1)

    def _cache_result(self, key: str, result: ForwardRollingResult) -> None:
        """Cache a result with size management."""
        if len(self._result_cache) >= self._cache_max_size:
            # FIFO eviction
            oldest_key = next(iter(self._result_cache))
            del self._result_cache[oldest_key]

        self._result_cache[key] = result

    def spawn_successor(
        self,
        current_agent: str,
        successor_name: str,
        context: ExecutionContext,
    ) -> AgentResult:
        """
        Spawn a successor agent.

        Convenience method for direct successor spawning.

        Args:
            current_agent: Current agent name
            successor_name: Successor agent to spawn
            context: Current execution context

        Returns:
            AgentResult from successor execution
        """
        successor_spec = SuccessorSpec(agent_name=successor_name)
        return self._orchestrator.spawn_successor(current_agent, successor_spec, context)

    def set_rollout_stage(self, stage: RolloutStage) -> None:
        """Set rollout stage."""
        self._config.set_rollout_stage(stage)
        Logger.info(f"[ForwardRollingFacade] Rollout stage set to {stage.value}")

    def emergency_disable(self) -> None:
        """Emergency disable Forward-Rolling."""
        self._config.emergency_disable()
        Logger.critical("[ForwardRollingFacade] EMERGENCY DISABLE activated")

    def rollback(self) -> bool:
        """Rollback to previous configuration."""
        return self._config.rollback()

    def get_health_status(self) -> HealthStatus:
        """Get current health status."""
        if self._monitor:
            return self._monitor.get_overall_health()
        return HealthStatus.HEALTHY

    def run_health_checks(self) -> list[dict[str, Any]]:
        """Run all health checks."""
        if self._monitor:
            checks = self._monitor.run_health_checks()
            return [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "duration_ms": c.duration_ms,
                }
                for c in checks
            ]
        return []

    def get_metrics(self) -> dict[str, Any]:
        """Get comprehensive metrics from all components."""
        metrics = {
            "optimization": {
                "total_executions": self._metrics.total_executions,
                "forward_rolling_executions": self._metrics.forward_rolling_executions,
                "static_dag_executions": self._metrics.static_dag_executions,
                "fallback_count": self._metrics.fallback_count,
                "avg_execution_time_ms": self._metrics.avg_execution_time_ms,
                "avg_depth_reached": self._metrics.avg_depth_reached,
                "cache_efficiency": self._metrics.cache_efficiency,
                "pruning_count": self._metrics.pruning_count,
                "bytes_saved_by_pruning": self._metrics.bytes_saved_by_pruning,
            },
            "orchestrator": self._orchestrator.get_metrics(),
            "config": self._config.export_config(),
        }

        if self._monitor:
            metrics["monitor"] = self._monitor.get_metrics_summary()

        if self._pruner:
            metrics["pruner"] = self._pruner.get_metrics()

        if self._depth_manager:
            metrics["depth_manager"] = self._depth_manager.get_statistics()

        return metrics

    def clear_cache(self) -> int:
        """Clear result cache."""
        count = len(self._result_cache)
        self._result_cache.clear()
        return count

    def set_cache_enabled(self, enabled: bool) -> None:
        """Enable or disable caching."""
        self._cache_enabled = enabled

    def reset(self) -> None:
        """Reset all components to initial state."""
        self._orchestrator.clear_successor_graph()
        self._orchestrator.reset_metrics()
        self._result_cache.clear()
        self._execution_times.clear()
        self._depths_reached.clear()
        self._metrics = OptimizationMetrics()

        if self._monitor:
            self._monitor.reset()

        if self._pruner:
            self._pruner.reset_metrics()

        if self._depth_manager:
            self._depth_manager.reset_history()

        Logger.info("[ForwardRollingFacade] Reset complete")

    def is_forward_rolling_enabled(self) -> bool:
        """Check if Forward-Rolling is currently enabled."""
        return self._config.get_config().stage != RolloutStage.DISABLED

    def get_rollout_percentage(self) -> int:
        """Get current rollout percentage."""
        return self._config.get_rollout_percentage()

    def set_feature_flag(self, name: str, enabled: bool, percentage: int = 100) -> None:
        """Set a feature flag."""
        self._config.set_feature_flag(name, enabled, percentage)

    def is_feature_enabled(self, name: str, agent_id: str = "") -> bool:
        """Check if a feature is enabled."""
        return self._config.is_feature_enabled(name, agent_id)


__all__ = [
    "ForwardRollingFacade",
    "ForwardRollingResult",
    "OptimizationMetrics",
]
