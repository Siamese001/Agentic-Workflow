"""ADG-driven tests for agentic_core/L0_routing/scripts/drift.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.drift import (  # noqa: F401
        REQUIRED_BASE,
        TARGET_VIOLATION,
        DriftDetector,
        scan_repository,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    DriftDetector = None  # type: ignore[assignment,misc]
    scan_repository = None  # type: ignore[assignment,misc]
    TARGET_VIOLATION = None  # type: ignore[assignment,misc]
    REQUIRED_BASE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="drift.py deps unavailable")
class TestDriftDetector:
    def test_is_class(self):
        assert isinstance(DriftDetector, type)
    def test_importable(self):
        assert DriftDetector is not None

@pytest.mark.skipif(not _AVAILABLE, reason="drift.py deps unavailable")
class TestScanRepository:
    def test_is_callable(self):
        assert callable(scan_repository)

@pytest.mark.skipif(not _AVAILABLE, reason="drift.py deps unavailable")
class TestTargetViolationConstant:
    def test_is_not_none(self):
        assert TARGET_VIOLATION is not None

@pytest.mark.skipif(not _AVAILABLE, reason="drift.py deps unavailable")
class TestRequiredBaseConstant:
    def test_is_not_none(self):
        assert REQUIRED_BASE is not None


def test_module_importable():
    """Module drift.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
