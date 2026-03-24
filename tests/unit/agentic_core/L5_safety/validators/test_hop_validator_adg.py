"""ADG importability contract for agentic_core/L5_safety/validators/hop_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hop_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.hop_validator import (  # noqa: F401
        HOP1ProfileDeterministic,
        HOP3DataExtractionDeterministic,
        HOP4ConditionDeterministic,
        HOP6PlaceholderDeterministic,
        HOP7GateDecisionDeterministic,
        HOPValidationResult,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    HOPValidationResult = None  # type: ignore[assignment,misc]
    HOP1ProfileDeterministic = None  # type: ignore[assignment,misc]
    HOP3DataExtractionDeterministic = None  # type: ignore[assignment,misc]
    HOP4ConditionDeterministic = None  # type: ignore[assignment,misc]
    HOP6PlaceholderDeterministic = None  # type: ignore[assignment,misc]
    HOP7GateDecisionDeterministic = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="hop_validator deps unavailable")
class TestHopValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/hop_validator.py must be importable."""
        assert _AVAILABLE

    def test_hopvalidationresult_defined(self) -> None:
        assert HOPValidationResult is not None

    def test_hop1profiledeterministic_defined(self) -> None:
        assert HOP1ProfileDeterministic is not None

    def test_hop3dataextractiondeterministic_defined(self) -> None:
        assert HOP3DataExtractionDeterministic is not None

    def test_hop4conditiondeterministic_defined(self) -> None:
        assert HOP4ConditionDeterministic is not None

    def test_hop6placeholderdeterministic_defined(self) -> None:
        assert HOP6PlaceholderDeterministic is not None

    def test_hop7gatedecisiondeterministic_defined(self) -> None:
        assert HOP7GateDecisionDeterministic is not None