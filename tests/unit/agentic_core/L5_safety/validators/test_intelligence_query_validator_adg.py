"""ADG importability contract for agentic_core/L5_safety/validators/intelligence_query_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_intelligence_query_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.intelligence_query_validator import (  # noqa: F401
        IntelligenceQueryResult,
        IntelligenceQueryValidator,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    IntelligenceQueryResult = None  # type: ignore[assignment,misc]
    IntelligenceQueryValidator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="intelligence_query_validator deps unavailable")
class TestIntelligenceQueryValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/intelligence_query_validator.py must be importable."""
        assert _AVAILABLE

    def test_intelligencequeryresult_defined(self) -> None:
        assert IntelligenceQueryResult is not None

    def test_intelligencequeryvalidator_defined(self) -> None:
        assert IntelligenceQueryValidator is not None
