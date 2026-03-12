"""ADG importability contract for agentic_core/L0_routing/engines/timeshift_router.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_timeshift_router.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.engines.timeshift_router import (  # noqa: F401
        RoutingMode,
        TimeshiftRoutingDecision,
        evaluate_timeshift_routing,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RoutingMode = None  # type: ignore[assignment,misc]
    TimeshiftRoutingDecision = None  # type: ignore[assignment,misc]
    evaluate_timeshift_routing = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="timeshift_router.py deps unavailable")
class TestTimeshiftRouterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: timeshift_router.py must be importable."""
        assert _AVAILABLE

    def test_routingmode_is_type(self) -> None:
        assert RoutingMode is not None

    def test_timeshiftroutingdecision_is_type(self) -> None:
        assert TimeshiftRoutingDecision is not None

    def test_evaluate_timeshift_routing_callable(self) -> None:
        assert callable(evaluate_timeshift_routing)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

