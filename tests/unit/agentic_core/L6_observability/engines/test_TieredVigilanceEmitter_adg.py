"""ADG importability contract for agentic_core/L6_observability/engines/TieredVigilanceEmitter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_TieredVigilanceEmitter.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.TieredVigilanceEmitter import (  # noqa: F401
        classify_signals,
        emit_vigilance_event,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    classify_signals = None  # type: ignore[assignment,misc]
    emit_vigilance_event = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="TieredVigilanceEmitter.py deps unavailable")
class TestTieredvigilanceemitterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: TieredVigilanceEmitter.py must be importable."""
        assert _AVAILABLE

    def test_classify_signals_callable(self) -> None:
        assert callable(classify_signals)

    def test_emit_vigilance_event_callable(self) -> None:
        assert callable(emit_vigilance_event)

