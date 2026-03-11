"""
detection_protocol - canonical re-export shim.

The implementation lives in agentic_core.runtime.config.detection_config.
This module re-exports for callers using
``from agentic_core.utils.detection_protocol_util import DetectionRequest, ...``.
"""

from agentic_core.runtime.config.detection_config import (  # noqa: F401
    DetectionRequest,
    DetectionResult,
    Severity,
)

__all__ = [
    "DetectionRequest",
    "DetectionResult",
    "Severity",
]


class DetectionSignalProtocol:
    """Protocol interface for detection signal emitters."""

    def detect(self, request: DetectionRequest) -> list[DetectionResult]:
        """Run detection and return results."""
        raise NotImplementedError
