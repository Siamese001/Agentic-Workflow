"""Safety Policy Types Module

Minimal types module for safety policy compatibility.
"""

from __future__ import annotations

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class SafetyPolicyType(str, Enum):
    """Types of safety policies."""
    CONTENT_FILTER = "content_filter"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"

@dataclass
class SafetyPolicy:
    """Base safety policy configuration."""
    policy_type: SafetyPolicyType
    enabled: bool = True
    threshold: float = 0.5
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ContentFilterPolicy(SafetyPolicy):
    """Content filtering policy."""
    blocked_patterns: List[str] = None
    max_length: int = 10000

    def __post_init__(self):
        super().__post_init__()
        if self.blocked_patterns is None:
            self.blocked_patterns = []

@dataclass
class RateLimitPolicy(SafetyPolicy):
    """Rate limiting policy."""
    requests_per_minute: int = 60
    burst_limit: int = 10

@dataclass
class SafetyContext:
    """Safety context for policy evaluation."""
    user_id: str = ""
    session_id: str = ""
    request_type: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class Verdict(str, Enum):
    """Safety verdict outcomes."""
    SAFE = "safe"
    UNSAFE = "unsafe"
    WARNING = "warning"
    REVIEW_REQUIRED = "review_required"

__all__ = [
    "SafetyPolicyType",
    "SafetyPolicy",
    "ContentFilterPolicy",
    "RateLimitPolicy",
    "SafetyContext",
    "Verdict",
]
