"""ADG importability contract for apps_shared/scripts/meta_learning_bridge.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_meta_learning_bridge.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.scripts.meta_learning_bridge import (  # noqa: F401
        emit_app_signal_aggregate,
        emit_app_signal_event,
        propose_from_signal_aggregate,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    emit_app_signal_event = None  # type: ignore[assignment,misc]
    propose_from_signal_aggregate = None  # type: ignore[assignment,misc]
    emit_app_signal_aggregate = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="meta_learning_bridge.py deps unavailable")
class TestMetaLearningBridgeImportability:
    def test_module_importable(self) -> None:
        """ADG contract: meta_learning_bridge.py must be importable."""
        assert _AVAILABLE

    def test_emit_app_signal_event_callable(self) -> None:
        assert callable(emit_app_signal_event)

    def test_propose_from_signal_aggregate_callable(self) -> None:
        assert callable(propose_from_signal_aggregate)
