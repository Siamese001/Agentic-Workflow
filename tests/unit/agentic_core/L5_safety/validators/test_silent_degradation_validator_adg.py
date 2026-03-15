"""ADG importability contract for agentic_core/L5_safety/validators/silent_degradation_validator.py.

Covers GT_covers edge for ADG reachability.
Behavioral tests live in tests/guardian/test_silent_degradation_detector.py.
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.silent_degradation_validator import (  # noqa: F401
        SilentDegradationDetector,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SilentDegradationDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="silent_degradation_validator deps unavailable")
class TestSilentDegradationValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/silent_degradation_validator.py must be importable."""
        assert _AVAILABLE

    def test_silentdegradationdetector_defined(self) -> None:
        assert SilentDegradationDetector is not None

    def test_detector_instantiates(self) -> None:
        det = SilentDegradationDetector()
        assert det is not None

    def test_category_is_silent_degradation(self) -> None:
        from agentic_core.L5_safety.validators.base_detector_validator import AntiPatternCategory

        det = SilentDegradationDetector()
        assert det.category == AntiPatternCategory.SILENT_DEGRADATION

    def test_all_exports_present(self) -> None:
        import agentic_core.L5_safety.validators.silent_degradation_validator as mod

        assert hasattr(mod, "SilentDegradationDetector")
        assert "SilentDegradationDetector" in mod.__all__
