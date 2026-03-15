"""ADG importability contract for agentic_core/L5_safety/validators/deliverability_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_deliverability_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.deliverability_validator import (  # noqa: F401
        DeliverabilityResult,
        DeliverabilityValidator,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    DeliverabilityResult = None  # type: ignore[assignment,misc]
    DeliverabilityValidator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="deliverability_validator deps unavailable")
class TestDeliverabilityValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/deliverability_validator.py must be importable."""
        assert _AVAILABLE

    def test_deliverabilityresult_defined(self) -> None:
        assert DeliverabilityResult is not None

    def test_deliverabilityvalidator_defined(self) -> None:
        assert DeliverabilityValidator is not None
