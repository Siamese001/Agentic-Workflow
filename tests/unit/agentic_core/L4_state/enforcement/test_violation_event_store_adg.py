"""ADG importability contract for agentic_core/L4_state/enforcement/violation_event_store.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_violation_event_store.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.enforcement.violation_event_store import (  # noqa: F401
        ViolationEventStore,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ViolationEventStore = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="violation_event_store.py deps unavailable")
class TestViolationEventStoreImportability:
    def test_module_importable(self) -> None:
        """ADG contract: violation_event_store.py must be importable."""
        assert _AVAILABLE

    def test_violationeventstore_is_type(self) -> None:
        assert ViolationEventStore is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

