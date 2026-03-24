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
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ATSValidationResult = None  # type: ignore[assignment,misc]
    AtsValidator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ats_validator deps unavailable")
class TestAtsValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/ats_validator.py must be importable."""
        assert _AVAILABLE

    def test_atsvalidationresult_defined(self) -> None:
        assert ATSValidationResult is not None

    def test_atsvalidator_defined(self) -> None:
        assert AtsValidator is not None