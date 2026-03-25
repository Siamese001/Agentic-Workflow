"""ADG importability contract for agentic_core/runtime/sovereignty_exceptions.py.

Auto-generated stub - covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_sovereignty_exceptions.py (no _adg suffix).
"""
from __future__ import annotations

from agentic_core.runtime.sovereignty_exceptions import (
    CapabilityTokenError,
    DeterminismViolationError,
    IsolationViolationError,
    SovereigntyViolationError,
)  # noqa: F401


class TestSovereigntyExceptionsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/sovereignty_exceptions.py must be importable."""

        pass  # Import verified at module level

    def test_sovereigntyviolationerror_defined(self) -> None:
        assert SovereigntyViolationError is not None

    def test_isolationviolationerror_defined(self) -> None:
        assert IsolationViolationError is not None

    def test_capabilitytokenerror_defined(self) -> None:
        assert CapabilityTokenError is not None

    def test_determinismviolationerror_defined(self) -> None:
        assert DeterminismViolationError is not None
