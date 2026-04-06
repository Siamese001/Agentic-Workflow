"""Error Classifier.

Error categorization and root cause analysis.
"""

import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Categories of errors."""
    RETRIEVAL_FAILURE = "retrieval_failure"
    GENERATION_FAILURE = "generation_failure"
    CACHE_FAILURE = "cache_failure"
    VALIDATION_FAILURE = "validation_failure"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    NETWORK = "network"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ErrorClassification:
    """Classified error."""
    error_type: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    root_cause: str
    is_transient: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class ErrorClassifier:
    """Classifies errors for analysis.

    The ErrorClassifier categorizes errors and attempts to
    identify root causes for better handling.
    """

    def __init__(self):
        """Initialize the error classifier."""
        self._error_patterns = self._setup_patterns()
        self._error_counts: dict[ErrorCategory, int] = defaultdict(int)

        log.info("ErrorClassifier initialized")

    def _setup_patterns(self) -> dict[ErrorCategory, list[str]]:
        """Setup error detection patterns."""
        return {
            ErrorCategory.RETRIEVAL_FAILURE: [
                r"retrieval",
                r"search",
                r"index",
                r"vector.*store",
            ],
            ErrorCategory.GENERATION_FAILURE: [
                r"generation",
                r"llm",
                r"model",
                r"inference",
            ],
            ErrorCategory.CACHE_FAILURE: [
                r"cache",
                r"redis",
                r"memcached",
            ],
            ErrorCategory.VALIDATION_FAILURE: [
                r"validation",
                r"schema",
                r"format",
            ],
            ErrorCategory.TIMEOUT: [
                r"timeout",
                r"timed out",
                r"deadline",
            ],
            ErrorCategory.RATE_LIMIT: [
                r"rate.*limit",
                r"too many requests",
                r"throttled",
            ],
            ErrorCategory.NETWORK: [
                r"network",
                r"connection",
                r"socket",
                r"dns",
            ],
        }

    def classify(
        self,
        error: Exception,
        context: dict[str, Any] | None = None,
    ) -> ErrorClassification:
        """Classify an error.

        Args:
            error: The exception to classify
            context: Optional context

        Returns:
            ErrorClassification with category and analysis
        """
        trace_id = f"error_{hash(str(error)) % 10000}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "ErrorClassifier.classify"
        )

        error_msg = str(error).lower()
        error_type = type(error).__name__

        # Detect category
        category = self._detect_category(error_msg, error_type)

        # Assess severity
        severity = self._assess_severity(error, category)

        # Determine if transient
        is_transient = self._is_transient(category, error_msg)

        # Identify root cause
        root_cause = self._identify_root_cause(error, category)

        classification = ErrorClassification(
            error_type=error_type,
            category=category,
            severity=severity,
            message=str(error),
            root_cause=root_cause,
            is_transient=is_transient,
            metadata=context or {},
        )

        # Track error count
        self._error_counts[category] += 1

        log.debug(f"Classified error: {category.value} (severity={severity.value})")
        return classification

    def _detect_category(self, error_msg: str, error_type: str) -> ErrorCategory:
        """Detect error category from message and type."""
        for category, patterns in self._error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_msg, re.IGNORECASE):
                    return category

        return ErrorCategory.UNKNOWN

    def _assess_severity(
        self,
        error: Exception,
        category: ErrorCategory,
    ) -> ErrorSeverity:
        """Assess error severity."""
        # Critical errors
        if category in [ErrorCategory.GENERATION_FAILURE]:
            return ErrorSeverity.CRITICAL

        # High severity
        if category in [ErrorCategory.RETRIEVAL_FAILURE, ErrorCategory.CACHE_FAILURE]:
            return ErrorSeverity.HIGH

        # Medium severity
        if category in [ErrorCategory.TIMEOUT, ErrorCategory.RATE_LIMIT]:
            return ErrorSeverity.MEDIUM

        return ErrorSeverity.LOW

    def _is_transient(self, category: ErrorCategory, error_msg: str) -> bool:
        """Determine if error is transient."""
        transient_categories = [
            ErrorCategory.TIMEOUT,
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.NETWORK,
        ]

        return category in transient_categories

    def _identify_root_cause(self, error: Exception, category: ErrorCategory) -> str:
        """Identify root cause."""
        if category == ErrorCategory.TIMEOUT:
            return "operation_exceeded_deadline"
        elif category == ErrorCategory.RATE_LIMIT:
            return "request_throttling"
        elif category == ErrorCategory.NETWORK:
            return "connectivity_issue"
        elif category == ErrorCategory.RETRIEVAL_FAILURE:
            return "search_backend_failure"

        return "unknown"

    def get_error_summary(self) -> dict[str, int]:
        """Get summary of error counts by category.

        Returns:
            Dictionary mapping categories to counts
        """
        return {cat.value: count for cat, count in self._error_counts.items()}


# Global instance
_global_classifier: ErrorClassifier | None = None


def get_error_classifier() -> ErrorClassifier:
    """Get or create the global error classifier."""
    global _global_classifier
    if _global_classifier is None:
        _global_classifier = ErrorClassifier()
    return _global_classifier
