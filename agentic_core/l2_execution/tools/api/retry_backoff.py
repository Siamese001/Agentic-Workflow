"""
L5 Agentic Core - L2 Execution Layer - API Retry Backoff
Implements L2 Pure Execution Layer for safe API retry with exponential backoff
"""

from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import time
import random

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetryStrategy(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    FIBONACCI_BACKOFF = "fibonacci_backoff"

class RetryStatus(Enum):
    """L5 Retry status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    INVALID_STRATEGY = "invalid_strategy"

@dataclass
class RetryConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_retries: int = 3
    max_delay_seconds: float = 60.0
    base_delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    jitter_enabled: bool = True
    jitter_factor: float = 0.1
    retryable_errors: List[str] = field(default_factory=lambda: ["rate_limit", "timeout", "server_error"])
    safety_level: str = "strict"

@dataclass
class RetryAttempt:
    """L5 Retry attempt structure with full type safety"""
    attempt_number: int
    delay_seconds: float
    error_message: str = ""
    timestamp: str = ""

@dataclass
class RetryResult:
    """L5 Retry result structure"""
    strategy: RetryStrategy
    total_attempts: int
    successful: bool
    attempts: List[RetryAttempt] = field(default_factory=list)
    total_delay_time: float = 0.0
    final_result: Any = None
    safety_validated: bool = False
    timestamp: str = ""

class APIRetryBackoff(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def execute_with_retry(self, func: Callable, strategy: RetryStrategy, constraints: RetryConstraints) -> RetryResult:
        """Execute function with retry and backoff"""
        pass
    
    @abstractmethod
    def validate_safety(self, func: Callable, constraints: RetryConstraints) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class APIRetryBackoffImpl(APIRetryBackoff):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure retry execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[RetryConstraints] = None):
        self.constraints = constraints or RetryConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def execute_with_retry(self, func: Callable, strategy: RetryStrategy, constraints: Optional[RetryConstraints] = None) -> RetryResult:
        """Execute function with retry following L5 architecture principles"""
        retry_constraints = constraints or self.constraints
        self.logger.info(f"Executing function with retry strategy: {strategy.value}")
        
        # L5 Input validation
        self._validate_input(func, strategy)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(func, retry_constraints):
            raise SecurityError("Function or constraints failed L5 safety validation")
        
        attempts = []
        total_delay_time = 0.0
        final_result = None
        successful = False
        
        try:
            for attempt in range(retry_constraints.max_retries + 1):
                attempt_start_time = time.time()
                
                try:
                    # Execute the function
                    result = func()
                    
                    # Success - no more retries needed
                    successful = True
                    final_result = result
                    
                    attempt_record = RetryAttempt(
                        attempt_number=attempt + 1,
                        delay_seconds=0.0 if attempt == 0 else attempts[-1].delay_seconds,
                        timestamp=self._get_timestamp()
                    )
                    attempts.append(attempt_record)
                    
                    self.logger.info(f"Function succeeded on attempt {attempt + 1}")
                    break
                    
                except Exception as e:
                    error_message = str(e)
                    
                    # Check if error is retryable
                    if not self._is_retryable_error(error_message, retry_constraints):
                        self.logger.error(f"Non-retryable error: {error_message}")
                        break
                    
                    # Calculate delay for next attempt
                    if attempt < retry_constraints.max_retries:
                        delay = self._calculate_delay(attempt, strategy, retry_constraints)
                        total_delay_time += delay
                        
                        attempt_record = RetryAttempt(
                            attempt_number=attempt + 1,
                            delay_seconds=delay,
                            error_message=error_message,
                            timestamp=self._get_timestamp()
                        )
                        attempts.append(attempt_record)
                        
                        self.logger.warning(f"Attempt {attempt + 1} failed: {error_message}, retrying in {delay:.2f}s")
                        time.sleep(delay)
                    else:
                        # Last attempt failed
                        attempt_record = RetryAttempt(
                            attempt_number=attempt + 1,
                            delay_seconds=0.0,
                            error_message=error_message,
                            timestamp=self._get_timestamp()
                        )
                        attempts.append(attempt_record)
                        
                        self.logger.error(f"Max retries exceeded, last error: {error_message}")
            
            # Create retry result
            result = RetryResult(
                strategy=strategy,
                total_attempts=len(attempts),
                successful=successful,
                attempts=attempts,
                total_delay_time=total_delay_time,
                final_result=final_result,
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Retry execution completed: {len(attempts)} attempts, success: {successful}")
            return result
            
        except Exception as e:
            self.logger.error(f"Retry execution error: {e}")
            return RetryResult(
                strategy=strategy,
                total_attempts=len(attempts),
                successful=False,
                attempts=attempts,
                total_delay_time=total_delay_time,
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
    
    def _calculate_delay(self, attempt: int, strategy: RetryStrategy, constraints: RetryConstraints) -> float:
        """Calculate delay for retry attempt"""
        if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = constraints.base_delay_seconds * (constraints.backoff_multiplier ** attempt)
        elif strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = constraints.base_delay_seconds * (attempt + 1)
        elif strategy == RetryStrategy.FIXED_DELAY:
            delay = constraints.base_delay_seconds
        elif strategy == RetryStrategy.FIBONACCI_BACKOFF:
            delay = constraints.base_delay_seconds * self._fibonacci(attempt + 1)
        else:
            delay = constraints.base_delay_seconds
        
        # Apply jitter if enabled
        if constraints.jitter_enabled:
            jitter = delay * constraints.jitter_factor * (random.random() * 2 - 1)
            delay += jitter
        
        # Ensure delay is within bounds
        delay = max(0, min(delay, constraints.max_delay_seconds))
        
        return delay
    
    def _fibonacci(self, n: int) -> int:
        """Calculate Fibonacci number"""
        if n <= 1:
            return n
        
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        
        return b
    
    def _is_retryable_error(self, error_message: str, constraints: RetryConstraints) -> bool:
        """Check if error is retryable"""
        error_lower = error_message.lower()
        
        for retryable_error in constraints.retryable_errors:
            if retryable_error in error_lower:
                return True
        
        # Common retryable HTTP status codes
        retryable_status_codes = ["429", "500", "502", "503", "504"]
        for status_code in retryable_status_codes:
            if status_code in error_message:
                return True
        
        # Network-related errors
        network_errors = ["connection", "timeout", "network", "dns"]
        for network_error in network_errors:
            if network_error in error_lower:
                return True
        
        return False
    
    def validate_safety(self, func: Callable, constraints: RetryConstraints) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Validate function
            if not callable(func):
                self.logger.error("Provided object is not callable")
                return False
            
            # Validate constraints
            if constraints.max_retries < 0 or constraints.max_retries > 10:
                self.logger.error("Invalid max_retries value")
                return False
            
            if constraints.base_delay_seconds < 0 or constraints.base_delay_seconds > 300:
                self.logger.error("Invalid base_delay_seconds value")
                return False
            
            if constraints.max_delay_seconds < 0 or constraints.max_delay_seconds > 3600:
                self.logger.error("Invalid max_delay_seconds value")
                return False
            
            if constraints.backoff_multiplier <= 0 or constraints.backoff_multiplier > 10:
                self.logger.error("Invalid backoff_multiplier value")
                return False
            
            if constraints.jitter_factor < 0 or constraints.jitter_factor > 1:
                self.logger.error("Invalid jitter_factor value")
                return False
            
            # Check for potentially dangerous function names
            func_name = getattr(func, '__name__', str(func))
            dangerous_names = ["exec", "eval", "compile", "open", "file", "import"]
            if func_name.lower() in dangerous_names:
                self.logger.error(f"Dangerous function name: {func_name}")
                return False
            
            self.logger.info("Function and constraints passed L5 safety validation")
            return True
            
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, func: Callable, strategy: RetryStrategy) -> None:
        """L5 Input validation"""
        if not callable(func):
            raise ValueError("Function must be callable")
        
        if not isinstance(strategy, RetryStrategy):
            raise ValueError("Strategy must be a RetryStrategy enum")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class APIRetryBackoffInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, retry_backoff: APIRetryBackoff):
        self._retry_backoff = retry_backoff
    
    def execute_with_retry(self, func: Callable, strategy: str = "exponential_backoff", max_retries: int = 3) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            retry_strategy = RetryStrategy(strategy)
            constraints = RetryConstraints(max_retries=max_retries)
            
            result = self._retry_backoff.execute_with_retry(func, retry_strategy, constraints)
            
            return {
                "success": result.successful,
                "strategy": result.strategy.value,
                "total_attempts": result.total_attempts,
                "total_delay_time": result.total_delay_time,
                "attempts": [
                    {
                        "attempt_number": attempt.attempt_number,
                        "delay_seconds": attempt.delay_seconds,
                        "error_message": attempt.error_message,
                        "timestamp": attempt.timestamp
                    }
                    for attempt in result.attempts
                ],
                "final_result": str(result.final_result) if result.final_result is not None else None,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp
            }
        except Exception as e:
            self.logger.error(f"Retry execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class APIRetryBackoffFactory:
    """L5 Factory for creating API retry backoff instances"""
    
    @staticmethod
    def create_retry_backoff(constraints: Optional[RetryConstraints] = None) -> APIRetryBackoff:
        return APIRetryBackoffImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[RetryConstraints] = None) -> APIRetryBackoffInterface:
        retry_backoff = APIRetryBackoffFactory.create_retry_backoff(constraints)
        return APIRetryBackoffInterface(retry_backoff)

# L5 Export for module usage
__all__ = [
    "RetryStrategy",
    "RetryStatus",
    "RetryConstraints",
    "RetryAttempt",
    "RetryResult",
    "APIRetryBackoff",
    "APIRetryBackoffImpl",
    "APIRetryBackoffInterface",
    "APIRetryBackoffFactory",
    "SecurityError"
]
