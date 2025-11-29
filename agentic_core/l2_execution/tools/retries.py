"""
L2 Tool Retries

Defines retry mechanisms for L2 execution tools.
"""

import time
from typing import Dict, Any, Callable, Optional
from enum import Enum

class RetryStrategy(Enum):
    """Retry strategy types."""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    NO_RETRY = "no_retry"

class RetryHandler:
    """Handles retry logic for L2 tools."""
    
    def __init__(self):
        self.retry_configs = {}
        self.default_config = {
            "max_retries": 3,
            "strategy": RetryStrategy.EXPONENTIAL_BACKOFF,
            "base_delay": 1.0,
            "max_delay": 60.0,
            "backoff_multiplier": 2.0
        }
    
    def configure_retry(self, tool_name: str, config: Dict[str, Any]):
        """Configure retry settings for a specific tool."""
        self.retry_configs[tool_name] = {
            **self.default_config,
            **config
        }
    
    def execute_with_retry(self, tool_name: str, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Execute a function with retry logic."""
        config = self.retry_configs.get(tool_name, self.default_config)
        
        result = {
            "status": "running",
            "attempts": 0,
            "max_retries": config["max_retries"]
        }
        
        last_exception = None
        
        for attempt in range(config["max_retries"] + 1):
            result["attempts"] = attempt + 1
            
            try:
                func_result = func(*args, **kwargs)
                result.update({
                    "status": "completed",
                    "result": func_result,
                    "attempts_used": attempt + 1
                })
                return result
            
            except Exception as e:
                last_exception = e
                
                if attempt < config["max_retries"]:
                    delay = self._calculate_delay(attempt, config)
                    time.sleep(delay)
                else:
                    break
        
        result.update({
            "status": "failed",
            "error": str(last_exception),
            "attempts_used": config["max_retries"] + 1
        })
        return result
    
    def _calculate_delay(self, attempt: int, config: Dict[str, Any]) -> float:
        """Calculate delay based on retry strategy."""
        strategy = config["strategy"]
        base_delay = config["base_delay"]
        max_delay = config["max_delay"]
        
        if strategy == RetryStrategy.FIXED_DELAY:
            delay = base_delay
        elif strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = base_delay * (config["backoff_multiplier"] ** attempt)
        elif strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = base_delay * (attempt + 1)
        else:
            delay = 0
        
        return min(delay, max_delay)
    
    def get_retry_config(self, tool_name: str) -> Dict[str, Any]:
        """Get retry configuration for a tool."""
        return self.retry_configs.get(tool_name, self.default_config).copy()

# Global retry handler
retry_handler = RetryHandler()

__all__ = ['RetryStrategy', 'RetryHandler', 'retry_handler']
