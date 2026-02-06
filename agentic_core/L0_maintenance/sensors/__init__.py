"""Sensors module - Unified detection signal interface.

Implements the SCRIPT (SENSOR) component from target state architecture.
"""

from agentic_core.L0_maintenance.sensors.detection_signal_config import (
    DetectionSignal,
    FailureContext,
    ImpactAssessment,
    ImpactScope,
    Severity,
)
from agentic_core.L0_maintenance.sensors.git_health_sensor import (
    GitHealthSensor,
    check_git_health,
)

__all__ = [
    "DetectionSignal",
    "FailureContext",
    "ImpactAssessment",
    "ImpactScope",
    "Severity",
    "GitHealthSensor",
    "check_git_health",
]
