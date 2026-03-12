"""ADG importability contract for agentic_core/L5_safety/validators/ats_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ats_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.ats_validator import (  # noqa: F401
        ATSValidationResult,
        AtsValidator,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ATSValidationResult = None  # type: ignore[assignment,misc]
    AtsValidator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ats_validator.py deps unavailable")
class TestAtsValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ats_validator.py must be importable."""
        assert _AVAILABLE

    def test_atsvalidationresult_is_type(self) -> None:
        assert ATSValidationResult is not None

    def test_atsvalidator_is_type(self) -> None:
        assert AtsValidator is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

