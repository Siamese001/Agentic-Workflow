"""Retry Policy - Exponential backoff for transient failures.

This module implements sophisticated retry policies with exponential backoff,
jitter, and circuit breaker integration to handle transient failures gracefully.
"""

import asyncio
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union

logger = logging.getLogger(__name__)


class RetryStrategy(str, Enum):
    """Retry strategy types."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    IMMEDIATE = "immediate"


class RetryableError(Exception):
    """Base class for retryable errors."""
    pass


class NonRetryableError(Exception):
    """Base class for non-retryable errors."""
    pass


@dataclass
class RetryConfig:
    """Configuration for retry policy."""
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    multiplier: float = 2.0  # for exponential backoff
    jitter: bool = True  # Add randomness to prevent thundering herd
    retryable_exceptions: List[Type[Exception]] = field(default_factory=lambda: [
        ConnectionError,
        TimeoutError,
        asyncio.TimeoutError,
        RetryableError
    ])
    non_retryable_exceptions: List[Type[Exception]] = field(default_factory=lambda: [
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        NonRetryableError
    ])
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Check if exception should be retried.
        
        Args:
            exception: Exception that occurred
            attempt: Current attempt number
            
        Returns:
            True if should retry
        """
        # Check attempt limit
        if attempt >= self.max_attempts:
            return False
        
        # Check non-retryable exceptions
        for exc_type in self.non_retryable_exceptions:
            if isinstance(exception, exc_type):
                return False
        
        # Check retryable exceptions
        for exc_type in self.retryable_exceptions:
            if isinstance(exception, exc_type):
                return True
        
        # Default: retry unknown exceptions
        return True


@dataclass
class RetryAttempt:
    """Information about a retry attempt."""
    attempt: int
    delay: float
    exception: Optional[Exception]
    timestamp: datetime
    success: bool


@dataclass
class RetryResult:
    """Result of retry execution."""
    success: bool
    result: Any = None
    attempts: int = 0
    total_delay: float = 0.0
    attempts_history: List[RetryAttempt] = field(default_factory=list)
    final_exception: Optional[Exception] = None


class DelayCalculator:
    """Calculates delay between retry attempts."""
    
    @staticmethod
    def calculate_delay(
        config: RetryConfig,
        attempt: int,
        base_delay: Optional[float] = None
    ) -> float:
        """Calculate delay for next attempt.
        
        Args:
            config: Retry configuration
            attempt: Current attempt number (0-based)
            base_delay: Override base delay
            
        Returns:
            Delay in seconds
        """
        base = base_delay or config.base_delay
        
        if config.strategy == RetryStrategy.IMMEDIATE:
            delay = 0.0
        elif config.strategy == RetryStrategy.FIXED_DELAY:
            delay = base
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = base * (attempt + 1)
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = base * (config.multiplier ** attempt)
        else:
            delay = base
        
        # Apply max delay limit
        delay = min(delay, config.max_delay)
        
        # Add jitter if enabled
        if config.jitter and delay > 0:
            # Add up to ±25% jitter
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay)  # Ensure non-negative
        
        return delay


class RetryPolicy:
    """Implements retry policy with configurable strategies."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """Initialize retry policy.
        
        Args:
            config: Retry configuration
        """
        self.config = config or RetryConfig()
        self._stats = {
            "total_retries": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "average_attempts": 0.0
        }
        
        logger.debug(f"Initialized RetryPolicy with strategy: {self.config.strategy}")
    
    async def execute(
        self,
        func: Callable,
        *args,
        config: Optional[RetryConfig] = None,
        on_retry: Optional[Callable[[RetryAttempt], None]] = None,
        **kwargs
    ) -> RetryResult:
        """Execute function with retry policy.
        
        Args:
            func: Function to execute
            *args: Function arguments
            config: Override retry config
            on_retry: Callback for each retry attempt
            **kwargs: Function keyword arguments
            
        Returns:
            Retry result
        """
        retry_config = config or self.config
        attempts_history = []
        total_delay = 0.0
        last_exception = None
        
        for attempt in range(retry_config.max_attempts):
            start_time = time.time()
            
            try:
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Success
                attempt_info = RetryAttempt(
                    attempt=attempt + 1,
                    delay=0.0,
                    exception=None,
                    timestamp=datetime.utcnow(),
                    success=True
                )
                attempts_history.append(attempt_info)
                
                # Update stats
                self._update_stats(attempt + 1, True)
                
                logger.debug(f"Function succeeded on attempt {attempt + 1}")
                
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempt + 1,
                    total_delay=total_delay,
                    attempts_history=attempts_history
                )
                
            except Exception as e:
                last_exception = e
                delay = DelayCalculator.calculate_delay(retry_config, attempt)
                total_delay += delay
                
                attempt_info = RetryAttempt(
                    attempt=attempt + 1,
                    delay=delay,
                    exception=e,
                    timestamp=datetime.utcnow(),
                    success=False
                )
                attempts_history.append(attempt_info)
                
                # Check if should retry
                if not retry_config.should_retry(e, attempt):
                    logger.warning(f"Function failed on attempt {attempt + 1}, not retryable: {e}")
                    break
                
                # Last attempt?
                if attempt == retry_config.max_attempts - 1:
                    logger.error(f"Function failed after {attempt + 1} attempts: {e}")
                    break
                
                # Wait before retry
                logger.warning(f"Function failed on attempt {attempt + 1}, retrying in {delay:.2f}s: {e}")
                
                if delay > 0:
                    await asyncio.sleep(delay)
                
                # Call retry callback
                if on_retry:
                    try:
                        on_retry(attempt_info)
                    except Exception as callback_error:
                        logger.error(f"Retry callback failed: {callback_error}")
        
        # All attempts failed
        self._update_stats(len(attempts_history), False)
        
        return RetryResult(
            success=False,
            result=None,
            attempts=len(attempts_history),
            total_delay=total_delay,
            attempts_history=attempts_history,
            final_exception=last_exception
        )
    
    def _update_stats(self, attempts: int, success: bool) -> None:
        """Update retry statistics.
        
        Args:
            attempts: Number of attempts
            success: Whether eventually successful
        """
        self._stats["total_retries"] += 1
        
        if success:
            self._stats["successful_retries"] += 1
        else:
            self._stats["failed_retries"] += 1
        
        # Update average attempts
        total = self._stats["total_retries"]
        if total > 0:
            current_avg = self._stats["average_attempts"]
            self._stats["average_attempts"] = (
                (current_avg * (total - 1) + attempts) / total
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retry statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        if stats["total_retries"] > 0:
            stats["success_rate"] = stats["successful_retries"] / stats["total_retries"]
        else:
            stats["success_rate"] = 0.0
        return stats


class RetryableExecutor:
    """Executor with built-in retry capabilities."""
    
    def __init__(self, default_config: Optional[RetryConfig] = None):
        """Initialize retryable executor.
        
        Args:
            default_config: Default retry configuration
        """
        self.default_config = default_config or RetryConfig()
        self.policies: Dict[str, RetryPolicy] = {}
    
    def register_policy(self, name: str, config: RetryConfig) -> None:
        """Register a named retry policy.
        
        Args:
            name: Policy name
            config: Retry configuration
        """
        self.policies[name] = RetryPolicy(config)
        logger.debug(f"Registered retry policy: {name}")
    
    async def execute(
        self,
        func: Callable,
        *args,
        policy: Optional[str] = None,
        config: Optional[RetryConfig] = None,
        **kwargs
    ) -> Any:
        """Execute function with retry policy.
        
        Args:
            func: Function to execute
            *args: Function arguments
            policy: Named policy to use
            config: Override configuration
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: Last exception if all retries failed
        """
        # Get retry policy
        if policy and policy in self.policies:
            retry_policy = self.policies[policy]
        else:
            retry_policy = RetryPolicy(config or self.default_config)
        
        # Execute with retry
        result = await retry_policy.execute(func, *args, **kwargs)
        
        if not result.success:
            raise result.final_exception
        
        return result.result


# Global retry executor
_retry_executor: Optional[RetryableExecutor] = None
_executor_lock = asyncio.Lock()


async def get_retry_executor() -> RetryableExecutor:
    """Get global retry executor instance.
    
    Returns:
        RetryableExecutor instance
    """
    global _retry_executor
    async with _executor_lock:
        if _retry_executor is None:
            _retry_executor = RetryableExecutor()
    return _retry_executor


# Decorators for automatic retry
def retry(
    max_attempts: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: Optional[List[Type[Exception]]] = None
):
    """Decorator to add retry to functions.
    
    Args:
        max_attempts: Maximum retry attempts
        strategy: Retry strategy
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        retryable_exceptions: List of retryable exceptions
        
    Returns:
        Decorated function
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            config = RetryConfig(
                max_attempts=max_attempts,
                strategy=strategy,
                base_delay=base_delay,
                max_delay=max_delay,
                retryable_exceptions=retryable_exceptions or []
            )
            
            retry_policy = RetryPolicy(config)
            result = await retry_policy.execute(func, *args, **kwargs)
            
            if not result.success:
                raise result.final_exception
            
            return result.result
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, run in thread pool
            async def async_func():
                return func(*args, **kwargs)
            
            return asyncio.run(async_wrapper())
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_with_policy(policy_name: str):
    """Decorator to use named retry policy.
    
    Args:
        policy_name: Name of registered policy
        
    Returns:
        Decorated function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            executor = await get_retry_executor()
            return await executor.execute(func, *args, policy=policy_name, **kwargs)
        return wrapper
    return decorator


# Predefined configurations
RETRY_CONFIGS = {
    "aggressive": RetryConfig(
        max_attempts=5,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        base_delay=0.5,
        max_delay=30.0
    ),
    "conservative": RetryConfig(
        max_attempts=3,
        strategy=RetryStrategy.LINEAR_BACKOFF,
        base_delay=2.0,
        max_delay=60.0
    ),
    "fast": RetryConfig(
        max_attempts=3,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        base_delay=0.1,
        max_delay=5.0
    ),
    "slow": RetryConfig(
        max_attempts=5,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        base_delay=5.0,
        max_delay=300.0
    )
}


# Initialize default policies
async def init_default_policies() -> None:
    """Initialize default retry policies."""
    executor = await get_retry_executor()
    
    for name, config in RETRY_CONFIGS.items():
        executor.register_policy(name, config)
    
    logger.info("Initialized default retry policies")
