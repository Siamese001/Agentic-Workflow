"""
L2 Tool Circuit Breakers

Defines circuit breaker patterns for L2 execution tools.
"""

import time
from enum import Enum
from typing import Dict, Any, Callable, Optional

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """Circuit breaker implementation for tool resilience."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Execute function through circuit breaker."""
        result = {"status": "running", "circuit_state": self.state.value}
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                result.update({
                    "status": "rejected",
                    "message": "Circuit breaker is OPEN",
                    "time_until_reset": self._get_time_until_reset()
                })
                return result
        
        try:
            func_result = func(*args, **kwargs)
            self._on_success()
            result.update({
                "status": "completed",
                "result": func_result,
                "circuit_state": self.state.value
            })
            return result
        
        except Exception as e:
            self._on_failure()
            result.update({
                "status": "failed",
                "error": str(e),
                "circuit_state": self.state.value,
                "failure_count": self.failure_count
            })
            return result
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        return (self.last_failure_time and 
                time.time() - self.last_failure_time >= self.timeout)
    
    def _get_time_until_reset(self) -> int:
        """Get time until circuit breaker can attempt reset."""
        if not self.last_failure_time:
            return 0
        return max(0, self.timeout - int(time.time() - self.last_failure_time))
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "time_until_reset": self._get_time_until_reset()
        }

class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""
    
    def __init__(self):
        self.circuit_breakers = {}
    
    def register(self, tool_name: str, circuit_breaker: CircuitBreaker):
        """Register a circuit breaker for a tool."""
        self.circuit_breakers[tool_name] = circuit_breaker
    
    def call(self, tool_name: str, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Execute function through registered circuit breaker."""
        if tool_name not in self.circuit_breakers:
            # Create default circuit breaker if none exists
            self.circuit_breakers[tool_name] = CircuitBreaker()
        
        return self.circuit_breakers[tool_name].call(func, *args, **kwargs)
    
    def get_state(self, tool_name: str) -> Dict[str, Any]:
        """Get state of specific circuit breaker."""
        if tool_name in self.circuit_breakers:
            return self.circuit_breakers[tool_name].get_state()
        return {"state": "not_registered"}

# Global circuit breaker registry
circuit_breaker_registry = CircuitBreakerRegistry()

__all__ = ['CircuitState', 'CircuitBreaker', 'CircuitBreakerRegistry', 'circuit_breaker_registry']
