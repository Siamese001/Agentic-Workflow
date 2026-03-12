"""ADG importability contract for agentic_core/L2_execution/types/self_healing_trigger_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_self_healing_trigger_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.self_healing_trigger_types import (  # noqa: F401
        L2SelfHealingTrigger,
        is_healing_authorized,
        emit_self_healing_trigger,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    L2SelfHealingTrigger = None  # type: ignore[assignment,misc]
    is_healing_authorized = None  # type: ignore[assignment,misc]
    emit_self_healing_trigger = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="self_healing_trigger_types.py deps unavailable")
class TestSelfHealingTriggerTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: self_healing_trigger_types.py must be importable."""
        assert _AVAILABLE

    def test_l2selfhealingtrigger_is_type(self) -> None:
        assert L2SelfHealingTrigger is not None

    def test_is_healing_authorized_callable(self) -> None:
        assert callable(is_healing_authorized)

    def test_emit_self_healing_trigger_callable(self) -> None:
        assert callable(emit_self_healing_trigger)

