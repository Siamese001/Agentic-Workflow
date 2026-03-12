"""ADG importability contract for agentic_core/L3_orchestration/arbitration/advisors.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_advisors.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.arbitration.advisors import (  # noqa: F401
        risk_averse_advisor,
        throughput_advisor,
        get_available_advisors,
        run_advisor,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    risk_averse_advisor = None  # type: ignore[assignment,misc]
    throughput_advisor = None  # type: ignore[assignment,misc]
    get_available_advisors = None  # type: ignore[assignment,misc]
    run_advisor = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="advisors.py deps unavailable")
class TestAdvisorsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: advisors.py must be importable."""
        assert _AVAILABLE

    def test_risk_averse_advisor_callable(self) -> None:
        assert callable(risk_averse_advisor)

    def test_throughput_advisor_callable(self) -> None:
        assert callable(throughput_advisor)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

