"""apps_lic.signals — Resurfacing Signal Detection (W3)

Signal detection and trigger→wake mapping for multi-touch resurfacing.

Modules
-------
types : Signal type definitions (SignalType, ResurfacingSignal, etc.)
detector : Signal detection from multiple sources
trigger_wake_mapper : Maps signals to wake scheduler requests

Usage
-----
>>> from apps_lic.signals import SignalDetector, ResurfacingSignal
>>> detector = SignalDetector()
>>> result = detector.detect_signals(company_id="acme-corp")
>>> for signal in result.signals:
...     print(f"Detected: {signal.signal_type} ({signal.strength})")
"""

from apps_lic.signals.types import (
    SignalType,
    SignalStrength,
    SignalSource,
    ResurfacingSignal,
    SignalDetectionResult,
    sort_signals_by_priority,
    SIGNAL_PRIORITY,
)

from apps_lic.signals.detector import (
    SignalDetector,
    SignalDetectorConfig,
)

from apps_lic.signals.trigger_wake_mapper import (
    TriggerWakeMapper,
    WakeMappingDecision,
)

__all__ = [
    # Types
    "SignalType",
    "SignalStrength",
    "SignalSource",
    "ResurfacingSignal",
    "SignalDetectionResult",
    "sort_signals_by_priority",
    "SIGNAL_PRIORITY",
    # Detector
    "SignalDetector",
    "SignalDetectorConfig",
    # Mapper
    "TriggerWakeMapper",
    "WakeMappingDecision",
]
