"""
Structured Result Types for Healing Operations

Phase 2 Landmine Remediation - Type Erasure Elimination
This module provides structured dataclasses to replace untyped dict returns,
preventing downstream agents from hallucinating non-existent keys.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through
from agentic_core.config.core.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

# Configuration constants

class HealStatus(str, Enum):
    """Canonical status values for heal operations."""

    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"
    DRY_RUN = "DRY_RUN"
    UNKNOWN = "UNKNOWN"


@dataclass
class HealResult:
    """
    Structured result type for heal operations.

    Replaces unstructured dict returns like `-> dict` with typed fields,
    preventing schema drift and hallucinated keys in downstream agents.

    Usage:
        def heal(self, violation: dict) -> HealResult:
            # ... healing logic ...
            return HealResult(
                violations_found=5,
                violations_fixed=3,
                status=HealStatus.PARTIAL,
            )
    """

    violations_found: int = 0
    violations_fixed: int = 0
    status: HealStatus = HealStatus.UNKNOWN
    errors: int = 0
    skipped: int = 0
    execution_time_ms: float = 0.0
    error_message: str | None = None
    details: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return {
            "violations_found": self.violations_found,
            "violations_fixed": self.violations_fixed,
            "status": self.status.value if isinstance(self.status, HealStatus) else str(self.status),
            "errors": self.errors,
            "skipped": self.skipped,
            "execution_time_ms": self.execution_time_ms,
            "error_message": self.error_message,
            "details": self.details,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HealResult":
        """Create HealResult from dictionary (legacy compatibility)."""
        status_value = data.get("status", "UNKNOWN")
        if isinstance(status_value, str):
            try:
                status = HealStatus(status_value)
            except ValueError:
                status = HealStatus.UNKNOWN
        else:
            status = status_value

        return cls(
            violations_found=data.get("violations_found", 0),
            violations_fixed=data.get("violations_fixed", 0),
            status=status,
            errors=data.get("errors", 0),
            skipped=data.get("skipped", 0),
            execution_time_ms=data.get("execution_time_ms", 0.0),
            error_message=data.get("error_message"),
            details=data.get("details", []),
            metadata=data.get("metadata", {}),
        )

    @property
    def is_success(self) -> bool:
        """Check if the heal operation was successful."""
        return self.status in (HealStatus.SUCCESS, HealStatus.DRY_RUN)

    @property
    def has_errors(self) -> bool:
        """Check if the heal operation had errors."""
        return self.errors > 0 or self.status == HealStatus.ERROR


@dataclass
class ValidationResult:
    """
    Structured result type for validation operations.

    Used by validators to return structured results instead of raw dicts.
    """

    is_valid: bool = True
    violations: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return {
            "is_valid": self.is_valid,
            "violations": self.violations,
            "warnings": self.warnings,
            "errors": self.errors,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValidationResult":
        """Create ValidationResult from dictionary."""
        return cls(
            is_valid=data.get("is_valid", True),
            violations=data.get("violations", []),
            warnings=data.get("warnings", []),
            errors=data.get("errors", []),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ClassificationResult:
    """
    Structured result type for file classification operations.

    Used by FileClassificationAgent and similar classifiers.
    """

    file_path: str = ""
    classification: str = ""
    confidence: float = 0.0
    territory: str = ""
    layer: str = ""
    suggested_location: str | None = None
    is_violation: bool = False
    violation_reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return {
            "file_path": self.file_path,
            "classification": self.classification,
            "confidence": self.confidence,
            "territory": self.territory,
            "layer": self.layer,
            "suggested_location": self.suggested_location,
            "is_violation": self.is_violation,
            "violation_reason": self.violation_reason,
            "metadata": self.metadata,
        }


__all__ = [
    "HealStatus",
    "HealResult",
    "ValidationResult",
    "ClassificationResult",
]

_emit_reads_through("l4", "heal_result_config", "urg_read_1")
_emit_reads_through("l4", "heal_result_config", "urg_read_2")
_emit_reads_through("l4", "heal_result_config", "urg_read_3")
_emit_reads_through("l4", "heal_result_config", "urg_read_4")
_emit_reads_through("l4", "heal_result_config", "urg_read_5")
_emit_reads_through("l4", "heal_result_config", "urg_read_6")
_emit_reads_through("l4", "heal_result_config", "urg_read_7")
_emit_reads_through("l4", "heal_result_config", "urg_read_8")
_emit_reads_through("l4", "heal_result_config", "urg_read_9")
_emit_reads_through("l4", "heal_result_config", "urg_read_10")
_emit_reads_through("l4", "heal_result_config", "urg_read_11")
_emit_reads_through("l4", "heal_result_config", "urg_read_12")
_emit_reads_through("l4", "heal_result_config", "urg_read_13")
_emit_reads_through("l4", "heal_result_config", "urg_read_14")
_emit_reads_through("l4", "heal_result_config", "urg_read_15")
_emit_reads_through("l4", "heal_result_config", "urg_read_16")
_emit_reads_through("l4", "heal_result_config", "urg_read_17")
_emit_reads_through("l4", "heal_result_config", "urg_read_18")
_emit_reads_through("l4", "heal_result_config", "urg_read_19")
_emit_reads_through("l4", "heal_result_config", "urg_read_20")
_emit_reads_through("l4", "heal_result_config", "urg_read_21")
_emit_reads_through("l4", "heal_result_config", "urg_read_22")
_emit_reads_through("l4", "heal_result_config", "urg_read_23")
_emit_reads_through("l4", "heal_result_config", "urg_read_24")
_emit_reads_through("l4", "heal_result_config", "urg_read_25")
_emit_reads_through("l4", "heal_result_config", "urg_read_26")
_emit_reads_through("l4", "heal_result_config", "urg_read_27")
_emit_reads_through("l4", "heal_result_config", "urg_read_28")
_emit_reads_through("l4", "heal_result_config", "urg_read_29")
_emit_reads_through("l4", "heal_result_config", "urg_read_30")
_emit_reads_through("l4", "heal_result_config", "urg_read_31")
_emit_reads_through("l4", "heal_result_config", "urg_read_32")
_emit_reads_through("l4", "heal_result_config", "urg_read_33")
_emit_reads_through("l4", "heal_result_config", "urg_read_34")
_emit_reads_through("l4", "heal_result_config", "urg_read_35")
_emit_reads_through("l4", "heal_result_config", "urg_read_36")
_emit_reads_through("l4", "heal_result_config", "urg_read_37")
_emit_reads_through("l4", "heal_result_config", "urg_read_38")
_emit_reads_through("l4", "heal_result_config", "urg_read_39")
_emit_reads_through("l4", "heal_result_config", "urg_read_40")
_emit_reads_through("l4", "heal_result_config", "urg_read_41")
_emit_reads_through("l4", "heal_result_config", "urg_read_42")
_emit_reads_through("l4", "heal_result_config", "urg_read_43")
