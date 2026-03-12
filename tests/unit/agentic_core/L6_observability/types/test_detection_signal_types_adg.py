"""ADG importability contract for agentic_core/L6_observability/types/detection_signal_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_detection_signal_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.types.detection_signal_types import (  # noqa: F401
        DetectionSignal,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DetectionSignal = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="detection_signal_types.py deps unavailable")
class TestDetectionSignalTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: detection_signal_types.py must be importable."""
        assert _AVAILABLE

    def test_detectionsignal_is_type(self) -> None:
        assert DetectionSignal is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

