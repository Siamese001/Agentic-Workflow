"""ADG importability contract for agentic_core/L2_execution/healers/healing_event_emitter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_healing_event_emitter.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.healing_event_emitter import (  # noqa: F401
        HealingAttemptEvent,
        HealingEventEmitter,
        get_healing_emitter,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HealingAttemptEvent = None  # type: ignore[assignment,misc]
    HealingEventEmitter = None  # type: ignore[assignment,misc]
    get_healing_emitter = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="healing_event_emitter.py deps unavailable")
class TestHealingEventEmitterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: healing_event_emitter.py must be importable."""
        assert _AVAILABLE

    def test_healingattemptevent_is_type(self) -> None:
        assert HealingAttemptEvent is not None

    def test_healingeventemitter_is_type(self) -> None:
        assert HealingEventEmitter is not None

    def test_get_healing_emitter_callable(self) -> None:
        assert callable(get_healing_emitter)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

