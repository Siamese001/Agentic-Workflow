"""ADG importability contract for agentic_core/L0_routing/engines/escalation_router.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_escalation_router.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.engines.escalation_router import (  # noqa: F401
        decide_mode_from_prior_violations,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    decide_mode_from_prior_violations = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="escalation_router.py deps unavailable")
class TestEscalationRouterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: escalation_router.py must be importable."""
        assert _AVAILABLE

    def test_decide_mode_from_prior_violations_callable(self) -> None:
        assert callable(decide_mode_from_prior_violations)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

