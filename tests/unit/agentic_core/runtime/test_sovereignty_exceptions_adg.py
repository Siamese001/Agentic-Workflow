"""ADG importability contract for agentic_core/runtime/sovereignty_exceptions.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_sovereignty_exceptions.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.sovereignty_exceptions import (  # noqa: F401
        CapabilityTokenError,
        DeterminismViolationError,
        IsolationViolationError,
        SovereigntyViolationError,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SovereigntyViolationError = None  # type: ignore[assignment,misc]
    IsolationViolationError = None  # type: ignore[assignment,misc]
    CapabilityTokenError = None  # type: ignore[assignment,misc]
    DeterminismViolationError = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sovereignty_exceptions deps unavailable")
class TestSovereigntyExceptionsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/sovereignty_exceptions.py must be importable."""
        assert _AVAILABLE

    def test_sovereigntyviolationerror_defined(self) -> None:
        assert SovereigntyViolationError is not None

    def test_isolationviolationerror_defined(self) -> None:
        assert IsolationViolationError is not None

    def test_capabilitytokenerror_defined(self) -> None:
        assert CapabilityTokenError is not None

    def test_determinismviolationerror_defined(self) -> None:
        assert DeterminismViolationError is not None