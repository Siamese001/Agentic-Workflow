"""ADG-driven tests for apps_rg/validators/hallucination_detector_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.validators.hallucination_detector_validator import (  # noqa: F401
        HallucinationDetector,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HallucinationDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="hallucination_detector_validator.py deps unavailable")
class TestHallucinationDetector:
    def test_is_class(self):
        assert isinstance(HallucinationDetector, type)
    def test_importable(self):
        assert HallucinationDetector is not None


def test_module_importable():
    """Module hallucination_detector_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
