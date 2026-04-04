"""
Detection Signal Protocol for structured violation detection output.

This protocol standardizes how agents emit detection signals for violations,
enabling consistent handling across the system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from agentic_core.config.core.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

# Configuration constants

class Severity(Enum):
    """Severity levels for detection signals."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class DetectionRequest:
    """Request for detection operation."""

    file_path: str
    detection_type: str
    context: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.context is None:
            self.context = {}


@dataclass
class DetectionResult:
    """Result of detection operation."""

    source_sensor: str
    detection_type: str
    severity: Severity
    file_path: str
    message: str
    target_node: str | None = None
    suggested_fix: str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)
    auto_fixable: bool = False

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_sensor": self.source_sensor,
            "detection_type": self.detection_type,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "message": self.message,
            "target_node": self.target_node,
            "suggested_fix": self.suggested_fix,
            "metadata": self.metadata,
            "auto_fixable": self.auto_fixable,
        }

    def classify_risk_level(self) -> str:
        """Classify risk level for routing decisions."""
        if self.severity in (Severity.CRITICAL, Severity.HIGH):
            return "high"
        elif self.severity == Severity.MEDIUM:
            return "medium"
        else:
            return "low"


class DetectionSignalProtocol(ABC):
    """Protocol for detection signal emitters.

    Implementations must emit structured detection signals that can be
    processed by downstream components (validators, healers, reviewers).
    """

    @abstractmethod
    def emit_signal(self, result: DetectionResult) -> str:
        """Emit a detection signal.

        Args:
            result: Detection result to emit

        Returns:
            Signal ID for tracking
        """
        pass

    @abstractmethod
    def get_signals(
        self,
        file_path: str | None = None,
        severity: Severity | None = None,
        limit: int = 100,
    ) -> list[DetectionResult]:
        """Get detection signals with optional filtering."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if detection signal emitter is available."""
        pass
