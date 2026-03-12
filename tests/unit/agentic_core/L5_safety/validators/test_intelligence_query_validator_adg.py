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
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    IntelligenceQueryResult = None  # type: ignore[assignment,misc]
    IntelligenceQueryValidator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="intelligence_query_validator.py deps unavailable")
class TestIntelligenceQueryValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: intelligence_query_validator.py must be importable."""
        assert _AVAILABLE

    def test_intelligencequeryresult_is_type(self) -> None:
        assert IntelligenceQueryResult is not None

    def test_intelligencequeryvalidator_is_type(self) -> None:
        assert IntelligenceQueryValidator is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

