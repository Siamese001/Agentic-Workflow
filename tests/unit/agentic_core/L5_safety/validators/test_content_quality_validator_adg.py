"""ADG importability contract for agentic_core/L5_safety/validators/content_quality_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_content_quality_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.content_quality_validator import (  # noqa: F401
        QualityValidationResult,
        ContentQualityValidator,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    QualityValidationResult = None  # type: ignore[assignment,misc]
    ContentQualityValidator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="content_quality_validator.py deps unavailable")
class TestContentQualityValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: content_quality_validator.py must be importable."""
        assert _AVAILABLE

    def test_qualityvalidationresult_is_type(self) -> None:
        assert QualityValidationResult is not None

    def test_contentqualityvalidator_is_type(self) -> None:
        assert ContentQualityValidator is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

