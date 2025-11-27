"""
ExecutionBudgetManager - Resource budget tracking and limits enforcement.

Provides centralized budget management for tokens, requests, and recursion depth
to ensure system resilience under load. Singleton pattern consistent with TelemetryBus.
"""

import threading
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class BudgetUsage:
    """Current budget usage tracking."""
    tokens_used: int = 0
    requests_made: int = 0
    current_depth: int = 0
    active_concurrent: int = 0
    stages_completed: Dict[str, int] = field(default_factory=dict)
    last_activity: float = field(default_factory=time.time)


@dataclass
class BudgetLimits:
    """Budget limits configuration."""
    max_tokens: int = 1000000  # 1M tokens default
    max_requests: int = 1000   # 1K requests default
    max_depth: int = 10        # 10 levels default
    max_parallel: int = 5      # 5 concurrent operations default
    max_context_size: int = 500000  # 500KB context default
    max_message_length: int = 10000  # 10K message default
    executor_timeout: float = 30.0    # 30s timeout default


class ExecutionBudgetManager:
    """Singleton budget manager for execution resource tracking."""
    
    _instance: Optional['ExecutionBudgetManager'] = None
    _class_lock = threading.Lock()
    
    def __new__(cls) -> 'ExecutionBudgetManager':
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._class_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize budget tracking."""
        if not hasattr(self, '_initialized'):
            self._usage = BudgetUsage()
            self._limits = BudgetLimits()
            self._lock = threading.RLock()
            self._semaphore = threading.Semaphore(self._limits.max_parallel)
            self._initialized = True
    
    def configure(self, limits: BudgetLimits) -> None:
        """Configure budget limits."""
        with self._lock:
            self._limits = limits
            # Update semaphore with new parallel limit
            self._semaphore = threading.Semaphore(limits.max_parallel)
    
    def start_stage(self, name: str) -> bool:
        """Start a new execution stage and check budget."""
        with self._lock:
            # Check if we can start a new stage
            if not self._check_budget_internal(name):
                return False
            
            # Track stage start
            if name not in self._usage.stages_completed:
                self._usage.stages_completed[name] = 0
            self._usage.stages_completed[name] += 1
            self._usage.last_activity = time.time()
            
            return True
    
    def acquire_concurrent_slot(self, timeout: Optional[float] = None) -> bool:
        """Acquire a concurrent execution slot."""
        if timeout is None:
            timeout = self._limits.executor_timeout
        
        try:
            acquired = self._semaphore.acquire(timeout=timeout)
            if acquired:
                with self._lock:
                    self._usage.active_concurrent += 1
                    self._usage.last_activity = time.time()
            return acquired
        except Exception:
            return False
    
    def release_concurrent_slot(self) -> None:
        """Release a concurrent execution slot."""
        try:
            self._semaphore.release()
            with self._lock:
                self._usage.active_concurrent = max(0, self._usage.active_concurrent - 1)
                self._usage.last_activity = time.time()
        except Exception:
            pass  # Semaphore release might fail if over-released
    
    def record_tokens(self, name: str, tokens: int) -> None:
        """Record token usage for a stage."""
        with self._lock:
            self._usage.tokens_used += tokens
            self._usage.last_activity = time.time()
    
    def increment_depth(self, name: str) -> bool:
        """Increment recursion depth and check limit."""
        with self._lock:
            if self._usage.current_depth >= self._limits.max_depth:
                return False
            
            self._usage.current_depth += 1
            self._usage.last_activity = time.time()
            return True
    
    def decrement_depth(self, name: str) -> None:
        """Decrement recursion depth."""
        with self._lock:
            self._usage.current_depth = max(0, self._usage.current_depth - 1)
            self._usage.last_activity = time.time()
    
    def check_budget(self, name: str) -> bool:
        """Check if budget allows starting a new stage."""
        with self._lock:
            return self._check_budget_internal(name)
    
    def _check_budget_internal(self, name: str) -> bool:
        """Internal budget check without lock (caller must hold lock)."""
        # Check token budget
        if self._usage.tokens_used >= self._limits.max_tokens:
            return False
        
        # Check request budget
        if self._usage.requests_made >= self._limits.max_requests:
            return False
        
        # Check depth budget
        if self._usage.current_depth >= self._limits.max_depth:
            return False
        
        return True
    
    def check_context_size(self, context_size: int) -> bool:
        """Check if context size is within limits."""
        return context_size <= self._limits.max_context_size
    
    def check_message_length(self, message_length: int) -> bool:
        """Check if message length is within limits."""
        return message_length <= self._limits.max_message_length
    
    def record_request(self) -> None:
        """Record a new request."""
        with self._lock:
            self._usage.requests_made += 1
            self._usage.last_activity = time.time()
    
    def current_usage(self) -> Dict[str, Any]:
        """Get current budget usage statistics."""
        with self._lock:
            return {
                "tokens_used": self._usage.tokens_used,
                "tokens_remaining": max(0, self._limits.max_tokens - self._usage.tokens_used),
                "requests_made": self._usage.requests_made,
                "requests_remaining": max(0, self._limits.max_requests - self._usage.requests_made),
                "current_depth": self._usage.current_depth,
                "max_depth": self._limits.max_depth,
                "active_concurrent": self._usage.active_concurrent,
                "max_parallel": self._limits.max_parallel,
                "stages_completed": self._usage.stages_completed.copy(),
                "last_activity": self._usage.last_activity,
                "budget_exceeded": {
                    "tokens": self._usage.tokens_used >= self._limits.max_tokens,
                    "requests": self._usage.requests_made >= self._limits.max_requests,
                    "depth": self._usage.current_depth >= self._limits.max_depth,
                    "concurrent": self._usage.active_concurrent >= self._limits.max_parallel
                }
            }
    
    def get_limits(self) -> Dict[str, Any]:
        """Get current budget limits."""
        with self._lock:
            return {
                "max_tokens": self._limits.max_tokens,
                "max_requests": self._limits.max_requests,
                "max_depth": self._limits.max_depth,
                "max_parallel": self._limits.max_parallel,
                "max_context_size": self._limits.max_context_size,
                "max_message_length": self._limits.max_message_length,
                "executor_timeout": self._limits.executor_timeout
            }
    
    def reset_usage(self) -> None:
        """Reset usage statistics (for testing)."""
        with self._lock:
            self._usage = BudgetUsage()
    
    def get_budget_exceeded_reason(self) -> Optional[str]:
        """Get reason for budget exceeded, if any."""
        with self._lock:
            if self._usage.tokens_used >= self._limits.max_tokens:
                return "Token budget exceeded"
            if self._usage.requests_made >= self._limits.max_requests:
                return "Request budget exceeded"
            if self._usage.current_depth >= self._limits.max_depth:
                return "Recursion depth exceeded"
            if self._usage.active_concurrent >= self._limits.max_parallel:
                return "Concurrent execution limit exceeded"
            return None
    
    # Phase 9 required method aliases
    def check_token_budget(self) -> bool:
        """Check if token budget allows further execution."""
        return self.check_budget("token_check")
    
    def check_context_limit(self, context_size: int) -> bool:
        """Check if context size is within limits."""
        return self.check_context_size(context_size)
    
    def check_depth(self) -> bool:
        """Check if recursion depth is within limits."""
        with self._lock:
            return self._usage.current_depth < self._limits.max_depth
    
    def acquire_slot(self, timeout: Optional[float] = None) -> bool:
        """Acquire a concurrent execution slot."""
        return self.acquire_concurrent_slot(timeout)
    
    def release_slot(self) -> None:
        """Release a concurrent execution slot."""
        self.release_concurrent_slot()


# Global singleton instance
_budget_manager: Optional[ExecutionBudgetManager] = None


def get_budget_manager() -> ExecutionBudgetManager:
    """Get the global ExecutionBudgetManager singleton instance."""
    global _budget_manager
    if _budget_manager is None:
        _budget_manager = ExecutionBudgetManager()
    return _budget_manager


def create_budget_limits_from_config(config: Dict[str, Any]) -> BudgetLimits:
    """Create BudgetLimits from configuration dictionary."""
    return BudgetLimits(
        max_tokens=config.get("max_tokens", 1000000),
        max_requests=config.get("max_requests", 1000),
        max_depth=config.get("max_depth", config.get("max_fallback_attempts", 10)),  # Backward compatibility
        max_parallel=config.get("max_parallel", config.get("max_parallel_research", 5)),  # Backward compatibility
        max_context_size=config.get("max_context_size", 500000),
        max_message_length=config.get("max_message_length", 10000),
        executor_timeout=config.get("executor_timeout", config.get("max_executor_timeout", 30.0))  # Backward compatibility
    )
