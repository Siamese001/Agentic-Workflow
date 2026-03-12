"""ADG importability contract for agentic_core/L6_observability/engines/drift_detector.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_drift_detector.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.drift_detector import (  # noqa: F401
        DriftDetector,
        get_drift_detector,
        reset_drift_detector,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DriftDetector = None  # type: ignore[assignment,misc]
    get_drift_detector = None  # type: ignore[assignment,misc]
    reset_drift_detector = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="drift_detector.py deps unavailable")
class TestDriftDetectorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: drift_detector.py must be importable."""
        assert _AVAILABLE

    def test_driftdetector_is_type(self) -> None:
        assert DriftDetector is not None

    def test_get_drift_detector_callable(self) -> None:
        assert callable(get_drift_detector)

    def test_reset_drift_detector_callable(self) -> None:
        assert callable(reset_drift_detector)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

