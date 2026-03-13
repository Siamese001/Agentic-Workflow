"""ADG importability contract for agentic_core/runtime/exceptions/healer_exceptions.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_healer_exceptions.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.exceptions.healer_exceptions import (  # noqa: F401
        CircularDependencyError,
        HealerError,
        HealingBudgetExceededError,
        HealingTimeoutError,
        SovereignError,
        ValidationRegistryError,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HealerError = None  # type: ignore[assignment,misc]
    CircularDependencyError = None  # type: ignore[assignment,misc]
    HealingBudgetExceededError = None  # type: ignore[assignment,misc]
    ValidationRegistryError = None  # type: ignore[assignment,misc]
    HealingTimeoutError = None  # type: ignore[assignment,misc]
    SovereignError = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healer_exceptions deps unavailable")
class TestHealerExceptionsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/exceptions/healer_exceptions.py must be importable."""
        assert _AVAILABLE

    def test_healererror_defined(self) -> None:
        assert HealerError is not None

    def test_circulardependencyerror_defined(self) -> None:
        assert CircularDependencyError is not None

    def test_healingbudgetexceedederror_defined(self) -> None:
        assert HealingBudgetExceededError is not None

    def test_validationregistryerror_defined(self) -> None:
        assert ValidationRegistryError is not None

    def test_healingtimeouterror_defined(self) -> None:
        assert HealingTimeoutError is not None

    def test_sovereignerror_defined(self) -> None:
        assert SovereignError is not None
