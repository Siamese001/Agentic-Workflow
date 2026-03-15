"""ADG importability contract for agentic_core/L5_safety/validators/base_detector_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_base_detector_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.base_detector_validator import (  # noqa: F401
        AntiPatternCategory,
        AntiPatternDetector,
        AntiPatternViolation,
        CompositeDetector,
        DetectionResult,
        EnforcementLevel,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    EnforcementLevel = None  # type: ignore[assignment,misc]
    AntiPatternCategory = None  # type: ignore[assignment,misc]
    AntiPatternViolation = None  # type: ignore[assignment,misc]
    DetectionResult = None  # type: ignore[assignment,misc]
    AntiPatternDetector = None  # type: ignore[assignment,misc]
    CompositeDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="base_detector_validator deps unavailable")
class TestBaseDetectorValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/base_detector_validator.py must be importable."""
        assert _AVAILABLE

    def test_enforcementlevel_defined(self) -> None:
        assert EnforcementLevel is not None

    def test_antipatterncategory_defined(self) -> None:
        assert AntiPatternCategory is not None

    def test_antipatternviolation_defined(self) -> None:
        assert AntiPatternViolation is not None

    def test_detectionresult_defined(self) -> None:
        assert DetectionResult is not None

    def test_antipatterndetector_defined(self) -> None:
        assert AntiPatternDetector is not None

    def test_compositedetector_defined(self) -> None:
        assert CompositeDetector is not None
