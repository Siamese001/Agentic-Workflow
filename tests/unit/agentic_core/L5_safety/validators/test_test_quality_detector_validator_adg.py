"""ADG importability contract for agentic_core/L5_safety/validators/test_quality_detector_validator.py.

Behavioral tests live in tests/guardian/test_test_quality_detector.py.
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.test_quality_detector_validator import (  # noqa: F401
        TestQualityDetector,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    TestQualityDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="test_quality_detector_validator deps unavailable")
class TestTestQualityDetectorValidatorImportability:
    def test_module_importable(self) -> None:
        assert _AVAILABLE

    def test_class_defined(self) -> None:
        assert TestQualityDetector is not None

    def test_instantiates(self) -> None:
        det = TestQualityDetector()
        assert det is not None

    def test_category_is_test_quality(self) -> None:
        from agentic_core.L5_safety.validators.base_detector_validator import AntiPatternCategory

        det = TestQualityDetector()
        assert det.category == AntiPatternCategory.TEST_QUALITY

    def test_all_exports_present(self) -> None:
        import agentic_core.L5_safety.validators.test_quality_detector_validator as mod

        assert hasattr(mod, "TestQualityDetector")
        assert "TestQualityDetector" in mod.__all__
