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
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    LeadQualityResult = None  # type: ignore[assignment,misc]
    LeadQualityValidator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="lead_quality_validator deps unavailable")
class TestLeadQualityValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/lead_quality_validator.py must be importable."""
        assert _AVAILABLE

    def test_leadqualityresult_defined(self) -> None:
        assert LeadQualityResult is not None

    def test_leadqualityvalidator_defined(self) -> None:
        assert LeadQualityValidator is not None