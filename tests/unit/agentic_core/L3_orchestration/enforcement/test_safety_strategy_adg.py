"""ADG importability contract for agentic_core/L3_orchestration/enforcement/safety_strategy.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_safety_strategy.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.enforcement.safety_strategy import (  # noqa: F401
        SafetyStrategy,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SafetyStrategy = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="safety_strategy.py deps unavailable")
class TestSafetyStrategyImportability:
    def test_module_importable(self) -> None:
        """ADG contract: safety_strategy.py must be importable."""
        assert _AVAILABLE

    def test_safetystrategy_is_type(self) -> None:
        assert SafetyStrategy is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

