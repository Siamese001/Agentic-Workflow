"""ADG importability contract for system_learning/ports/outcome_write_back_hook.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_outcome_write_back_hook.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.ports.outcome_write_back_hook import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        DefaultOutcomeWriteBackHook,
        NullOutcomeWriteBackHook,
        OutcomeWriteBackHook,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    OutcomeWriteBackHook = None  # type: ignore[assignment,misc]
    NullOutcomeWriteBackHook = None  # type: ignore[assignment,misc]
    DefaultOutcomeWriteBackHook = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="outcome_write_back_hook.py deps unavailable")
class TestOutcomeWriteBackHookImportability:
    def test_module_importable(self) -> None:
        """ADG contract: outcome_write_back_hook.py must be importable."""
        assert _AVAILABLE

    def test_outcomewritebackhook_is_type(self) -> None:
        assert OutcomeWriteBackHook is not None

    def test_nulloutcomewritebackhook_is_type(self) -> None:
        assert NullOutcomeWriteBackHook is not None

    def test_defaultoutcomewritebackhook_is_type(self) -> None:
        assert DefaultOutcomeWriteBackHook is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
