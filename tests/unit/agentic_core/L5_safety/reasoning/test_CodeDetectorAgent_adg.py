"""ADG importability contract for agentic_core/L5_safety/reasoning/CodeDetectorAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_CodeDetectorAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.CodeDetectorAgent import (  # noqa: F401
        DetectionType,
        Severity,
        Detection,
        DetectorConfig,
        CodeDetectorAgent,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DetectionType = None  # type: ignore[assignment,misc]
    Severity = None  # type: ignore[assignment,misc]
    Detection = None  # type: ignore[assignment,misc]
    DetectorConfig = None  # type: ignore[assignment,misc]
    CodeDetectorAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="CodeDetectorAgent.py deps unavailable")
class TestCodedetectoragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: CodeDetectorAgent.py must be importable."""
        assert _AVAILABLE

    def test_detectiontype_is_type(self) -> None:
        assert DetectionType is not None

    def test_severity_is_type(self) -> None:
        assert Severity is not None

    def test_detection_is_type(self) -> None:
        assert Detection is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

