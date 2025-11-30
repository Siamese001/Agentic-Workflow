"""
Safety Profile Configuration

Defines safety parameters and constraints for agentic operations
across the L1-L5 architecture.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class SafetyLevel(str, Enum):
    """Safety enforcement levels."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    STRICT = "strict"
    MAXIMUM = "maximum"


@dataclass
class SafetyProfile:
    """Configuration for safety parameters."""
    name: str
    safety_level: SafetyLevel = SafetyLevel.STANDARD
    content_filters: List[str] = field(default_factory=list)
    blocked_patterns: List[str] = field(default_factory=list)
    max_response_length: int = 10000
    require_human_approval: bool = False
    audit_logging: bool = True
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        
        # Set default content filters based on safety level
        if not self.content_filters:
            if self.safety_level == SafetyLevel.MINIMAL:
                self.content_filters = ["basic_toxicity"]
            elif self.safety_level == SafetyLevel.STANDARD:
                self.content_filters = ["basic_toxicity", "harmful_content", "pii_detection"]
            elif self.safety_level == SafetyLevel.STRICT:
                self.content_filters = ["basic_toxicity", "harmful_content", "pii_detection", "bias_detection"]
            else:  # MAXIMUM
                self.content_filters = ["basic_toxicity", "harmful_content", "pii_detection", "bias_detection", "advanced_safety"]


# Default safety profiles
DEFAULT_SAFETY_PROFILE = SafetyProfile(
    name="default",
    safety_level=SafetyLevel.STANDARD
)

STRICT_SAFETY_PROFILE = SafetyProfile(
    name="strict",
    safety_level=SafetyLevel.STRICT,
    require_human_approval=True
)

__all__ = [
    "SafetyProfile",
    "SafetyLevel",
    "DEFAULT_SAFETY_PROFILE",
    "STRICT_SAFETY_PROFILE",
]
