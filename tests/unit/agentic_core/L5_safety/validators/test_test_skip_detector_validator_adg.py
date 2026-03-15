"""ADG importability contract for agentic_core/L5_safety/validators/test_skip_detector_validator.py.

Behavioral tests live in tests/guardian/test_test_silent_skip_detector.py.
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.test_skip_detector_validator import (  # noqa: F401
        TestSilentSkipDetector,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    TestSilentSkipDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="test_skip_detector_validator deps unavailable")
class TestTestSkipDetectorValidatorImportability:
    def test_module_importable(self) -> None:
        assert _AVAILABLE

    def test_class_defined(self) -> None:
        assert TestSilentSkipDetector is not None

    def test_instantiates(self) -> None:
        det = TestSilentSkipDetector()
        assert det is not None

    def test_category_is_test_silent_skip(self) -> None:
        from agentic_core.L5_safety.validators.base_detector_validator import AntiPatternCategory

        det = TestSilentSkipDetector()
        assert det.category == AntiPatternCategory.TEST_SILENT_SKIP

    def test_all_exports_present(self) -> None:
        import agentic_core.L5_safety.validators.test_skip_detector_validator as mod

        assert hasattr(mod, "TestSilentSkipDetector")
        assert "TestSilentSkipDetector" in mod.__all__
