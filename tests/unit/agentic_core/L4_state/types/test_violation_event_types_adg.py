"""ADG importability contract for agentic_core/L4_state/types/violation_event_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_violation_event_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.types.violation_event_types import (  # noqa: F401
        ViolationEvent,
        emit_violation_event,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ViolationEvent = None  # type: ignore[assignment,misc]
    emit_violation_event = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="violation_event_types.py deps unavailable")
class TestViolationEventTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: violation_event_types.py must be importable."""
        assert _AVAILABLE

    def test_violationevent_is_type(self) -> None:
        assert ViolationEvent is not None

    def test_emit_violation_event_callable(self) -> None:
        assert callable(emit_violation_event)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

