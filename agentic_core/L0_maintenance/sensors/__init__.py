"""Sensors module - Unified detection signal interface.

Implements the SCRIPT (SENSOR) component from target state architecture.
"""

from agentic_core.L0_maintenance.sensors.detection_signal import (
    DetectionSignal,
    FailureContext,
    ImpactAssessment,
    ImpactScope,
    Severity,
)

__all__ = [
    "DetectionSignal",
    "FailureContext",
    "ImpactAssessment",
    "ImpactScope",
    "Severity",
]
