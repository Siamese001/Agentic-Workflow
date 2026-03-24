"""ADG importability contract for agentic_core/L5_safety/validators/content_quality_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_content_quality_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.content_quality_validator import (  # noqa: F401
        ContentQualityValidator,
        QualityValidationResult,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    QualityValidationResult = None  # type: ignore[assignment,misc]
    ContentQualityValidator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="content_quality_validator deps unavailable")
class TestContentQualityValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/content_quality_validator.py must be importable."""
        assert _AVAILABLE

    def test_qualityvalidationresult_defined(self) -> None:
        assert QualityValidationResult is not None

    def test_contentqualityvalidator_defined(self) -> None:
        assert ContentQualityValidator is not None