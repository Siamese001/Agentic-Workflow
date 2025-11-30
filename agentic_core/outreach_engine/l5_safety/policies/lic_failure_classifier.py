# LIC Failure Classifier module
from typing import Any, List, Optional, Dict
from dataclasses import dataclass
from enum import Enum

class FailureType(str, Enum):
    """Types of failures that can be classified."""
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    UNKNOWN = "unknown"

@dataclass
class LICFailureClassifierConfig:
    """Configuration for LIC failure classifier"""
    enabled: bool = True
    threshold: float = 0.5
    categories: List[str] = None

    def __post_init__(self):
        if self.categories is None:
            self.categories = ["network", "validation", "timeout", "auth"]

@dataclass
class FailureClassification:
    """Result of failure classification."""
    failure_type: FailureType
    confidence: float
    is_recoverable: bool
    suggested_action: str
    metadata: Dict[str, Any]

class FailureClassifier:
    """Failure classifier for outreach operations."""
    
    def __init__(self, config: Optional[LICFailureClassifierConfig] = None):
        self.config = config or LICFailureClassifierConfig()
    
    def classify_failure(self, error: Any, context: Optional[Dict[str, Any]] = None) -> FailureClassification:
        """Classify a failure based on error and context."""
        error_str = str(error).lower()
        
        if "timeout" in error_str:
            return FailureClassification(
                failure_type=FailureType.TIMEOUT,
                confidence=0.9,
                is_recoverable=True,
                suggested_action="Retry with exponential backoff",
                metadata={"classifier": "FailureClassifier", "error": error_str}
            )
        elif "network" in error_str or "connection" in error_str:
            return FailureClassification(
                failure_type=FailureType.NETWORK_ERROR,
                confidence=0.8,
                is_recoverable=True,
                suggested_action="Check network connectivity and retry",
                metadata={"classifier": "FailureClassifier", "error": error_str}
            )
        elif "validation" in error_str or "invalid" in error_str:
            return FailureClassification(
                failure_type=FailureType.VALIDATION_ERROR,
                confidence=0.7,
                is_recoverable=False,
                suggested_action="Fix input data and retry",
                metadata={"classifier": "FailureClassifier", "error": error_str}
            )
        else:
            return FailureClassification(
                failure_type=FailureType.UNKNOWN,
                confidence=0.5,
                is_recoverable=True,
                suggested_action="Log and investigate",
                metadata={"classifier": "FailureClassifier", "error": error_str}
            )

# Alias for facade import compatibility
LICFailureClassifier = FailureClassifier
