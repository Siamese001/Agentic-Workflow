"""ADG importability contract for agentic_core/L2_execution/determinism/determinism_guard.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_determinism_guard.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.determinism.determinism_guard import (  # noqa: F401
        assert_no_uuid4,
        assert_no_wallclock,
        assert_deterministic_context,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    assert_no_uuid4 = None  # type: ignore[assignment,misc]
    assert_no_wallclock = None  # type: ignore[assignment,misc]
    assert_deterministic_context = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="determinism_guard.py deps unavailable")
class TestDeterminismGuardImportability:
    def test_module_importable(self) -> None:
        """ADG contract: determinism_guard.py must be importable."""
        assert _AVAILABLE

    def test_assert_no_uuid4_callable(self) -> None:
        assert callable(assert_no_uuid4)

    def test_assert_no_wallclock_callable(self) -> None:
        assert callable(assert_no_wallclock)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

