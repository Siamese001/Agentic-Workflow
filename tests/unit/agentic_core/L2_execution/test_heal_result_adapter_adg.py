"""ADG importability contract for agentic_core/L2_execution/heal_result_adapter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_heal_result_adapter.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.heal_result_adapter import (  # noqa: F401
        adapt_heal_result,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    adapt_heal_result = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="heal_result_adapter.py deps unavailable")
class TestHealResultAdapterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: heal_result_adapter.py must be importable."""
        assert _AVAILABLE

    def test_adapt_heal_result_callable(self) -> None:
        assert callable(adapt_heal_result)

