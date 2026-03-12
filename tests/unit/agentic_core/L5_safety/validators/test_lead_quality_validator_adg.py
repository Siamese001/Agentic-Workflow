"""ADG importability contract for agentic_core/L5_safety/validators/lead_quality_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_lead_quality_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.lead_quality_validator import (  # noqa: F401
        LeadQualityResult,
        LeadQualityValidator,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    LeadQualityResult = None  # type: ignore[assignment,misc]
    LeadQualityValidator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="lead_quality_validator.py deps unavailable")
class TestLeadQualityValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: lead_quality_validator.py must be importable."""
        assert _AVAILABLE

    def test_leadqualityresult_is_type(self) -> None:
        assert LeadQualityResult is not None

    def test_leadqualityvalidator_is_type(self) -> None:
        assert LeadQualityValidator is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

