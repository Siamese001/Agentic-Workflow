"""ADG importability contract for agentic_core/runtime/exceptions/SovereignError.py.

Auto-generated stub - covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SovereignError.py (no _adg suffix).
"""
from __future__ import annotations

from agentic_core.runtime.exceptions.SovereignError import (
    CircularDependencyError,
    ConfigurationError,
    HealerError,
    HygieneError,
    SovereignError,
    StructuralError,
)  # noqa: F401


class TestSovereignerrorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/exceptions/SovereignError.py must be importable."""

        pass  # Import verified at module level

    def test_sovereignerror_defined(self) -> None:
        assert SovereignError is not None

    def test_healererror_defined(self) -> None:
        assert HealerError is not None

    def test_circulardependencyerror_defined(self) -> None:
        assert CircularDependencyError is not None

    def test_configurationerror_defined(self) -> None:
        assert ConfigurationError is not None

    def test_structuralerror_defined(self) -> None:
        assert StructuralError is not None

    def test_hygieneerror_defined(self) -> None:
        assert HygieneError is not None
