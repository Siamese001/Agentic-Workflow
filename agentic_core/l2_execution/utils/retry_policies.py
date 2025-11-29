#!/usr/bin/env python3
"""
Retry Policies
Section 5: Tool Contracts - Retry management policies
"""

from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

class RetryType(str, Enum):
    """Retry type enumeration"""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"

@dataclass
class RetryPolicy:
    """Retry policy configuration"""
    retry_type: RetryType
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        if self.retry_type == RetryType.FIXED_DELAY:
            return self.base_delay
        elif self.retry_type == RetryType.EXPONENTIAL_BACKOFF:
            delay = self.base_delay * (self.backoff_multiplier ** attempt)
            return min(delay, self.max_delay)
        elif self.retry_type == RetryType.LINEAR_BACKOFF:
            delay = self.base_delay * (attempt + 1)
            return min(delay, self.max_delay)
        else:
            return self.base_delay

# Re-export components
__all__ = [
    'RetryPolicy', 'RetryType'
]
