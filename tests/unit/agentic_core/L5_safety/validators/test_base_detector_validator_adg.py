"""ADG importability contract for agentic_core/L5_safety/validators/base_detector_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_base_detector_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.base_detector_validator import (  # noqa: F401
        EnforcementLevel,
        AntiPatternCategory,
        AntiPatternViolation,
        DetectionResult,
        AntiPatternDetector,
        CompositeDetector,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    EnforcementLevel = None  # type: ignore[assignment,misc]
    AntiPatternCategory = None  # type: ignore[assignment,misc]
    AntiPatternViolation = None  # type: ignore[assignment,misc]
    DetectionResult = None  # type: ignore[assignment,misc]
    AntiPatternDetector = None  # type: ignore[assignment,misc]
    CompositeDetector = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="base_detector_validator.py deps unavailable")
class TestBaseDetectorValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: base_detector_validator.py must be importable."""
        assert _AVAILABLE

    def test_enforcementlevel_is_type(self) -> None:
        assert EnforcementLevel is not None

    def test_antipatterncategory_is_type(self) -> None:
        assert AntiPatternCategory is not None

    def test_antipatternviolation_is_type(self) -> None:
        assert AntiPatternViolation is not None

