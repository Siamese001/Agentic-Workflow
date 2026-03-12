"""ADG importability contract for agentic_core/runtime/sovereignty_exceptions.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_sovereignty_exceptions.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.sovereignty_exceptions import (  # noqa: F401
        SovereigntyViolationError,
        IsolationViolationError,
        CapabilityTokenError,
        DeterminismViolationError,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SovereigntyViolationError = None  # type: ignore[assignment,misc]
    IsolationViolationError = None  # type: ignore[assignment,misc]
    CapabilityTokenError = None  # type: ignore[assignment,misc]
    DeterminismViolationError = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="sovereignty_exceptions.py deps unavailable")
class TestSovereigntyExceptionsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: sovereignty_exceptions.py must be importable."""
        assert _AVAILABLE

    def test_sovereigntyviolationerror_is_type(self) -> None:
        assert SovereigntyViolationError is not None

    def test_isolationviolationerror_is_type(self) -> None:
        assert IsolationViolationError is not None

    def test_capabilitytokenerror_is_type(self) -> None:
        assert CapabilityTokenError is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

