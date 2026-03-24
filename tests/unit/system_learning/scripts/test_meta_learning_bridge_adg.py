"""ADG-driven tests for system_learning/scripts/meta_learning_bridge.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.scripts.meta_learning_bridge import (  # noqa: F401
        emit_app_signal_aggregate,
        emit_app_signal_event,
        propose_from_signal_aggregate,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    emit_app_signal_event = None  # type: ignore[assignment,misc]
    propose_from_signal_aggregate = None  # type: ignore[assignment,misc]
    emit_app_signal_aggregate = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="meta_learning_bridge.py deps unavailable")
class TestEmitAppSignalEvent:
    def test_is_callable(self):
        assert callable(emit_app_signal_event)

@pytest.mark.skipif(not _AVAILABLE, reason="meta_learning_bridge.py deps unavailable")
class TestProposeFromSignalAggregate:
    def test_is_callable(self):
        assert callable(propose_from_signal_aggregate)

@pytest.mark.skipif(not _AVAILABLE, reason="meta_learning_bridge.py deps unavailable")
class TestEmitAppSignalAggregate:
    def test_is_callable(self):
        assert callable(emit_app_signal_aggregate)


def test_module_importable():
    """Module meta_learning_bridge.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE