#!/usr/bin/env python3
"""Detection Signal - Standardized failure detection with structured context.

Implements the SCRIPT (SENSOR) component from target state architecture.
Provides deterministic binary checks with structured failure context,
severity classification, and impact assessment.

Target State Reference:
- Deterministic, binary check
- Structured failure context
- Severity classification
- Impact assessment
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)


class Severity(Enum):
    """Severity levels for detection signals."""

    CRITICAL = 4  # System-breaking, immediate action required
    HIGH = 3  # Significant issue, prompt action required
    MEDIUM = 2  # Moderate issue, scheduled action appropriate
    LOW = 1  # Minor issue, informational
    INFO = 0  # No action required, logging only


class ImpactScope(Enum):
    """Scope of impact for detected issues."""

    SYSTEM_WIDE = "system_wide"  # Affects entire system
    DOMAIN = "domain"  # Affects a specific business domain or vertical
    COMPONENT = "component"  # Affects single component
    FILE = "file"  # Affects single file
    ISOLATED = "isolated"  # No broader impact


@dataclass
class ImpactAssessment:
    """Structured impact assessment for detection signals."""

    scope: ImpactScope = ImpactScope.FILE
    affected_components: list[str] = field(default_factory=list)
    estimated_blast_radius: int = 0  # Number of files potentially affected
    recovery_complexity: str = "low"  # low, medium, high
    downstream_dependencies: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ImpactAssessment.to_dict", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ImpactAssessment.to_dict", "p0_governance")
        return {
            "scope": self.scope.value,
            "affected_components": self.affected_components,
            "estimated_blast_radius": self.estimated_blast_radius,
            "recovery_complexity": self.recovery_complexity,
            "downstream_dependencies": self.downstream_dependencies,
        }


@dataclass
class FailureContext:
    """Structured failure context for detection signals."""

    file_path: Path | None = None
    line_number: int | None = None
    function_name: str | None = None
    class_name: str | None = None
    error_message: str = ""
    stack_trace: str | None = None
    related_files: list[Path] = field(default_factory=list)
    system_state: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": str(self.file_path) if self.file_path else None,
            "line_number": self.line_number,
            "function_name": self.function_name,
            "class_name": self.class_name,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "related_files": [str(f) for f in self.related_files],
            "system_state": self.system_state,
        }


@dataclass
class DetectionSignal:
    """Unified detection signal with structured context.

    This is the standard output format for all sensors in the system.
    Implements the target state SCRIPT (SENSOR) component requirements.

    Attributes:
        signal_id: Unique identifier for this signal
        timestamp: When the signal was generated
        source_sensor: Name of the sensor that generated this signal
        detection_type: Type of detection (e.g., "import_violation")
        is_failure: Binary check result
        failure_context: Structured context about the failure
        severity: Severity level of the detection
        impact: Impact assessment
        confidence: Confidence score (0.0 to 1.0)
        is_auto_fixable: Whether this can be auto-fixed
        suggested_fix: Optional suggested fix description
    """

    signal_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_sensor: str = "unknown"
    detection_type: str = "unknown"

    # Binary check result
    is_failure: bool = True

    # Structured context
    failure_context: FailureContext = field(default_factory=FailureContext)

    # Severity and impact
    severity: Severity = Severity.MEDIUM
    impact: ImpactAssessment = field(default_factory=ImpactAssessment)

    # Confidence scoring (for validator agent)
    confidence: float = 1.0  # 0.0 to 1.0

    # Actionability
    is_auto_fixable: bool = False
    suggested_fix: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization and logging."""
        return {
            "signal_id": self.signal_id,
            "timestamp": self.timestamp.isoformat(),
            "source_sensor": self.source_sensor,
            "detection_type": self.detection_type,
            "is_failure": self.is_failure,
            "failure_context": self.failure_context.to_dict(),
            "severity": self.severity.name,
            "impact": self.impact.to_dict(),
            "confidence": self.confidence,
            "is_auto_fixable": self.is_auto_fixable,
            "suggested_fix": self.suggested_fix,
        }

    def classify_risk_level(self) -> str:
        """Classify risk level based on severity and impact.

        Used by Validator Agent for enforcement policy decisions.
        Returns: 'low', 'medium', or 'high'
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "DetectionSignal.classify_risk_level",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DetectionSignal.classify_risk_level".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self.severity.value >= Severity.CRITICAL.value:
            return "high"
        elif self.severity.value >= Severity.MEDIUM.value:
            if self.impact.scope in {ImpactScope.SYSTEM_WIDE, ImpactScope.DOMAIN}:
                return "high"
            return "medium"
        return "low"


__all__ = [
    "DetectionSignal",
    "FailureContext",
    "ImpactAssessment",
    "Severity",
    "ImpactScope",
]
