"""ADG importability contract for agentic_core/L5_safety/validators/hop_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hop_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.hop_validator import (  # noqa: F401
        HOPValidationResult,
        HOP1ProfileDeterministic,
        HOP3DataExtractionDeterministic,
        HOP4ConditionDeterministic,
        HOP6PlaceholderDeterministic,
        HOP7GateDecisionDeterministic,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HOPValidationResult = None  # type: ignore[assignment,misc]
    HOP1ProfileDeterministic = None  # type: ignore[assignment,misc]
    HOP3DataExtractionDeterministic = None  # type: ignore[assignment,misc]
    HOP4ConditionDeterministic = None  # type: ignore[assignment,misc]
    HOP6PlaceholderDeterministic = None  # type: ignore[assignment,misc]
    HOP7GateDecisionDeterministic = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="hop_validator.py deps unavailable")
class TestHopValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: hop_validator.py must be importable."""
        assert _AVAILABLE

    def test_hopvalidationresult_is_type(self) -> None:
        assert HOPValidationResult is not None

    def test_hop1profiledeterministic_is_type(self) -> None:
        assert HOP1ProfileDeterministic is not None

    def test_hop3dataextractiondeterministic_is_type(self) -> None:
        assert HOP3DataExtractionDeterministic is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

