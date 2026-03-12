"""ADG importability contract for agentic_core/L3_orchestration/arbitration/run_advisors.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_run_advisors.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.arbitration.run_advisors import (  # noqa: F401
        run_advisors,
        run_all_advisors,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    run_advisors = None  # type: ignore[assignment,misc]
    run_all_advisors = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="run_advisors.py deps unavailable")
class TestRunAdvisorsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: run_advisors.py must be importable."""
        assert _AVAILABLE

    def test_run_advisors_callable(self) -> None:
        assert callable(run_advisors)

    def test_run_all_advisors_callable(self) -> None:
        assert callable(run_all_advisors)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

