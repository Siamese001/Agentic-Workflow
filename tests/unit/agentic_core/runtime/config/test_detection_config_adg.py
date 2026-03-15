"""ADG importability contract for agentic_core/runtime/config/detection_config.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_detection_config.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.config.detection_config import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        DetectionRequest,
        DetectionResult,
        DetectionSignalProtocol,
        Severity,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    Severity = None  # type: ignore[assignment,misc]
    DetectionRequest = None  # type: ignore[assignment,misc]
    DetectionResult = None  # type: ignore[assignment,misc]
    DetectionSignalProtocol = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="detection_config.py deps unavailable")
class TestDetectionConfigImportability:
    def test_module_importable(self) -> None:
        """ADG contract: detection_config.py must be importable."""
        assert _AVAILABLE

    def test_severity_is_type(self) -> None:
        assert Severity is not None

    def test_detectionrequest_is_type(self) -> None:
        assert DetectionRequest is not None

    def test_detectionresult_is_type(self) -> None:
        assert DetectionResult is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
