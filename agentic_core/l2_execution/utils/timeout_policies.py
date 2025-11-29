#!/usr/bin/env python3
"""
Timeout Policies
Section 5: Tool Contracts - Timeout management policies
"""

from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

class TimeoutType(str, Enum):
    """Timeout type enumeration"""
    FIXED = "fixed"
    ADAPTIVE = "adaptive"
    DYNAMIC = "dynamic"

@dataclass
class TimeoutPolicy:
    """Timeout policy configuration"""
    timeout_type: TimeoutType
    base_timeout: int
    max_timeout: int = 3600
    multiplier: float = 1.0
    
    def get_timeout(self, context: Optional[Dict[str, Any]] = None) -> int:
        """Calculate timeout based on policy and context"""
        if self.timeout_type == TimeoutType.FIXED:
            return self.base_timeout
        elif self.timeout_type == TimeoutType.ADAPTIVE:
            return min(self.base_timeout * self.multiplier, self.max_timeout)
        else:
            return self.base_timeout

# Re-export components
__all__ = [
    'TimeoutPolicy', 'TimeoutType'
]





