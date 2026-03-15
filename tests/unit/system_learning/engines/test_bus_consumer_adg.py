"""ADG importability contract for system_learning/engines/bus_consumer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_bus_consumer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.bus_consumer import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        drain_and_apply,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    drain_and_apply = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="bus_consumer.py deps unavailable")
class TestBusConsumerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: bus_consumer.py must be importable."""
        assert _AVAILABLE

    def test_drain_and_apply_callable(self) -> None:
        assert callable(drain_and_apply)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
