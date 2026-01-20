#!/usr/bin/env python3
"""
CoreOrchestrationAgent - Unified L3 Orchestration

Phase 1 Consolidation: Merges functionality from:
- CachedOrchestratorAgent (caching logic)
- SelfRecoveringOrchestratorAgent (retry/fallback mechanisms)
- IntelligentOrchestratorAgent (intelligent routing)
- HardenedWorkflowOrchestratorAgent (error handling)
- ConsolidatedOrchestratorAgent (unified interface)

Features:
- Caching layer for repeated orchestration patterns
- Self-recovery with automatic retry and exponential backoff
- Intelligent routing based on task type via strategy pattern
- Hardened error handling with fallback strategies
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Type, TypeVar

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

Logger = logging.getLogger(__name__)

T = TypeVar("T")


class TaskType(Enum):
    """Task types for intelligent routing."""
    VALIDATION = auto()
    HEALING = auto()
    ORCHESTRATION = auto()
    FISSION = auto()
    ROUTING = auto()
    GENERIC = auto()


class RecoveryStrategy(Enum):
    """Recovery strategies for failed operations."""
    RETRY = "retry"
    SKIP = "skip"
    FALLBACK = "fallback"
    ABORT = "abort"


@dataclass
class Task:
    """Represents an orchestration task."""
    task_id: str
    task_type: TaskType
    payload: Dict[str, Any]
    priority: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    cache_ttl: int = 3600
    created_at: datetime = field(default_factory=datetime.now)
    
    def cache_key(self) -> str:
        """Generate cache key for this task."""
        payload_str = json.dumps(self.payload, sort_keys=True, default=str)
        content = f"{self.task_type.name}:{payload_str}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]


@dataclass
class Result:
    """Represents an orchestration result."""
    task_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    retries_used: int = 0
    from_cache: bool = False
    recovery_applied: Optional[RecoveryStrategy] = None


class OrchestrationStrategy(ABC):
    """Abstract base for task-specific orchestration strategies."""
    
    @abstractmethod
    async def execute(self, task: Task, context: Dict[str, Any]) -> Result:
        """Execute the task using this strategy."""
        pass
    
    @abstractmethod
    def can_handle(self, task: Task) -> bool:
        """Check if this strategy can handle the task."""
        pass


class ValidationStrategy(OrchestrationStrategy):
    """Strategy for validation tasks."""
    
    async def execute(self, task: Task, context: Dict[str, Any]) -> Result:
        Logger.info(f"Executing validation task: {task.task_id}")
        # Validation logic would go here
        return Result(
            task_id=task.task_id,
            success=True,
            data={"validated": True, "checks_passed": task.payload.get("checks", 0)},
        )
    
    def can_handle(self, task: Task) -> bool:
        return task.task_type == TaskType.VALIDATION


class HealingStrategy(OrchestrationStrategy):
    """Strategy for healing tasks."""
    
    async def execute(self, task: Task, context: Dict[str, Any]) -> Result:
        Logger.info(f"Executing healing task: {task.task_id}")
        # Healing logic would go here
        return Result(
            task_id=task.task_id,
            success=True,
            data={"healed": True, "fixes_applied": task.payload.get("fixes", 0)},
        )
    
    def can_handle(self, task: Task) -> bool:
        return task.task_type == TaskType.HEALING


class GenericStrategy(OrchestrationStrategy):
    """Fallback strategy for generic tasks."""
    
    async def execute(self, task: Task, context: Dict[str, Any]) -> Result:
        Logger.info(f"Executing generic task: {task.task_id}")
        return Result(
            task_id=task.task_id,
            success=True,
            data=task.payload,
        )
    
    def can_handle(self, task: Task) -> bool:
        return True  # Handles any task as fallback


@dataclass
class CoreOrchestrationAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Unified L3 orchestration with caching, self-recovery, and intelligent routing.
    
    Consolidates:
    - CachedOrchestratorAgent (caching)
    - SelfRecoveringOrchestratorAgent (retry/fallback)
    - IntelligentOrchestratorAgent (smart routing)
    - HardenedWorkflowOrchestratorAgent (error handling)
    
    Usage:
        agent = CoreOrchestrationAgent(cache_enabled=True, max_retries=3)
        task = Task(task_id="t1", task_type=TaskType.VALIDATION, payload={})
        result = await agent.orchestrate(task)
    """
    
    cache_enabled: bool = True
    max_retries: int = 3
    retry_backoff_base: float = 2.0
    default_timeout: int = 300
    
    def __post_init__(self) -> None:
        """Initialize the orchestration agent."""
        self._cache: Dict[str, Result] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._strategies: List[OrchestrationStrategy] = [
            ValidationStrategy(),
            HealingStrategy(),
            GenericStrategy(),  # Fallback
        ]
        self._execution_history: List[Dict[str, Any]] = []
        self._failure_patterns: Dict[str, int] = {}
        Logger.info("CoreOrchestrationAgent initialized")
    
    def register_strategy(self, strategy: OrchestrationStrategy) -> None:
        """Register a custom orchestration strategy."""
        # Insert before GenericStrategy (fallback)
        self._strategies.insert(-1, strategy)
        Logger.info(f"Registered strategy: {strategy.__class__.__name__}")
    
    def _select_strategy(self, task: Task) -> OrchestrationStrategy:
        """Select the appropriate strategy for a task (intelligent routing)."""
        for strategy in self._strategies:
            if strategy.can_handle(task):
                Logger.debug(f"Selected strategy {strategy.__class__.__name__} for task {task.task_id}")
                return strategy
        # Should never reach here due to GenericStrategy fallback
        return self._strategies[-1]
    
    def _get_cached_result(self, task: Task) -> Optional[Result]:
        """Check cache for existing result."""
        if not self.cache_enabled:
            return None
        
        cache_key = task.cache_key()
        if cache_key not in self._cache:
            return None
        
        # Check TTL
        cached_time = self._cache_timestamps.get(cache_key)
        if cached_time:
            age = (datetime.now() - cached_time).total_seconds()
            if age > task.cache_ttl:
                # Expired
                del self._cache[cache_key]
                del self._cache_timestamps[cache_key]
                return None
        
        result = self._cache[cache_key]
        Logger.info(f"Cache hit for task {task.task_id}")
        return Result(
            task_id=task.task_id,
            success=result.success,
            data=result.data,
            error=result.error,
            from_cache=True,
        )
    
    def _store_cached_result(self, task: Task, result: Result) -> None:
        """Store result in cache."""
        if not self.cache_enabled or not result.success:
            return
        
        cache_key = task.cache_key()
        self._cache[cache_key] = result
        self._cache_timestamps[cache_key] = datetime.now()
        Logger.debug(f"Cached result for task {task.task_id}")
    
    async def _execute_with_retry(
        self,
        task: Task,
        strategy: OrchestrationStrategy,
        context: Dict[str, Any],
    ) -> Result:
        """Execute task with retry logic and exponential backoff."""
        last_error: Optional[Exception] = None
        retries_used = 0
        
        for attempt in range(task.max_retries):
            try:
                if attempt > 0:
                    backoff = self.retry_backoff_base ** attempt
                    Logger.info(f"Retry {attempt}/{task.max_retries} for {task.task_id} after {backoff}s")
                    await asyncio.sleep(backoff)
                
                start_time = datetime.now()
                result = await asyncio.wait_for(
                    strategy.execute(task, context),
                    timeout=task.timeout_seconds,
                )
                execution_time = (datetime.now() - start_time).total_seconds()
                result.execution_time = execution_time
                result.retries_used = retries_used
                
                # Clear failure pattern on success
                if task.task_id in self._failure_patterns:
                    del self._failure_patterns[task.task_id]
                
                return result
                
            except asyncio.TimeoutError:
                last_error = TimeoutError(f"Task {task.task_id} timed out after {task.timeout_seconds}s")
                retries_used += 1
                Logger.warning(f"Task {task.task_id} attempt {attempt + 1} timed out")
                
            except Exception as e:
                last_error = e
                retries_used += 1
                Logger.warning(f"Task {task.task_id} attempt {attempt + 1} failed: {e}")
        
        # All retries exhausted
        self._failure_patterns[task.task_id] = self._failure_patterns.get(task.task_id, 0) + 1
        
        return Result(
            task_id=task.task_id,
            success=False,
            error=str(last_error) if last_error else "Unknown error after retries",
            retries_used=retries_used,
            recovery_applied=RecoveryStrategy.RETRY,
        )
    
    def _apply_fallback(self, task: Task, failed_result: Result) -> Result:
        """Apply fallback strategy for failed tasks."""
        Logger.info(f"Applying fallback for task {task.task_id}")
        
        # Check if task has a fallback payload
        fallback_data = task.payload.get("fallback")
        if fallback_data:
            return Result(
                task_id=task.task_id,
                success=True,
                data=fallback_data,
                recovery_applied=RecoveryStrategy.FALLBACK,
            )
        
        # Return failed result with fallback marker
        failed_result.recovery_applied = RecoveryStrategy.ABORT
        return failed_result
    
    async def orchestrate(self, task: Task) -> Result:
        """
        Main orchestration entry point.
        
        Implements the strategy pattern for intelligent routing,
        with caching and self-recovery.
        
        Args:
            task: The task to orchestrate
            
        Returns:
            Result of the orchestration
        """
        Logger.info(f"Orchestrating task {task.task_id} (type={task.task_type.name})")
        
        # Check cache first
        cached = self._get_cached_result(task)
        if cached:
            return cached
        
        # Select strategy (intelligent routing)
        strategy = self._select_strategy(task)
        
        # Build context
        context: Dict[str, Any] = {
            "agent": self,
            "timestamp": datetime.now(),
            "failure_history": self._failure_patterns.get(task.task_id, 0),
        }
        
        # Execute with retry
        result = await self._execute_with_retry(task, strategy, context)
        
        # Apply fallback if failed
        if not result.success:
            result = self._apply_fallback(task, result)
        
        # Cache successful results
        if result.success:
            self._store_cached_result(task, result)
        
        # Record execution
        self._execution_history.append({
            "task_id": task.task_id,
            "task_type": task.task_type.name,
            "success": result.success,
            "from_cache": result.from_cache,
            "retries_used": result.retries_used,
            "execution_time": result.execution_time,
            "timestamp": datetime.now().isoformat(),
        })
        
        return result
    
    def clear_cache(self) -> int:
        """Clear all cached results. Returns count of cleared entries."""
        count = len(self._cache)
        self._cache.clear()
        self._cache_timestamps.clear()
        Logger.info(f"Cleared {count} cached entries")
        return count
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self._execution_history:
            return {"total": 0}
        
        total = len(self._execution_history)
        successful = sum(1 for e in self._execution_history if e["success"])
        cached = sum(1 for e in self._execution_history if e["from_cache"])
        avg_time = sum(e["execution_time"] for e in self._execution_history) / total
        
        return {
            "total": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "cache_hit_rate": cached / total if total > 0 else 0,
            "avg_execution_time": avg_time,
        }
    
    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[set] = None,
    ) -> Dict[str, int]:
        """L3 orchestration agent - operational healing."""
        if _call_path is None:
            _call_path = set()
        
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        
        _call_path.add(agent_name)
        try:
            Logger.info(f"[{agent_name}] L3 orchestration healing")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


# =============================================================================
# BACKWARD COMPATIBILITY FACTORY METHODS
# =============================================================================

def create_legacy_cached_orchestrator(
    project_root: Optional[Path] = None,
    mission_id: str = "default",
    **kwargs: Any,
) -> CoreOrchestrationAgent:
    """
    Factory for backward compatibility with CachedOrchestratorAgent.
    
    DEPRECATED: Use CoreOrchestrationAgent directly.
    This factory will be removed after the 30-day migration period.
    """
    warnings.warn(
        "CachedOrchestratorAgent is deprecated. Use CoreOrchestrationAgent instead. "
        "This factory will be removed after 2026-02-19.",
        DeprecationWarning,
        stacklevel=2,
    )
    return CoreOrchestrationAgent(cache_enabled=True, **kwargs)


def create_legacy_self_recovering_orchestrator(**kwargs: Any) -> CoreOrchestrationAgent:
    """
    Factory for backward compatibility with SelfRecoveringOrchestratorAgent.
    
    DEPRECATED: Use CoreOrchestrationAgent directly.
    This factory will be removed after the 30-day migration period.
    """
    warnings.warn(
        "SelfRecoveringOrchestratorAgent is deprecated. Use CoreOrchestrationAgent instead. "
        "This factory will be removed after 2026-02-19.",
        DeprecationWarning,
        stacklevel=2,
    )
    return CoreOrchestrationAgent(max_retries=3, retry_backoff_base=2.0, **kwargs)


def create_legacy_intelligent_orchestrator(
    target: Optional[str] = None,
    **kwargs: Any,
) -> CoreOrchestrationAgent:
    """
    Factory for backward compatibility with IntelligentOrchestratorAgent.
    
    DEPRECATED: Use CoreOrchestrationAgent directly.
    This factory will be removed after the 30-day migration period.
    """
    warnings.warn(
        "IntelligentOrchestratorAgent is deprecated. Use CoreOrchestrationAgent instead. "
        "This factory will be removed after 2026-02-19.",
        DeprecationWarning,
        stacklevel=2,
    )
    return CoreOrchestrationAgent(**kwargs)


def create_legacy_hardened_orchestrator(**kwargs: Any) -> CoreOrchestrationAgent:
    """
    Factory for backward compatibility with HardenedWorkflowOrchestratorAgent.
    
    DEPRECATED: Use CoreOrchestrationAgent directly.
    This factory will be removed after the 30-day migration period.
    """
    warnings.warn(
        "HardenedWorkflowOrchestratorAgent is deprecated. Use CoreOrchestrationAgent instead. "
        "This factory will be removed after 2026-02-19.",
        DeprecationWarning,
        stacklevel=2,
    )
    return CoreOrchestrationAgent(max_retries=5, **kwargs)
