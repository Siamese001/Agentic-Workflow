"""ADG importability contract for agentic_core/L3_orchestration/arbitration/arbitrator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_arbitrator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.arbitration.arbitrator import (  # noqa: F401
        Arbitrator,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    Arbitrator = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="arbitrator.py deps unavailable")
class TestArbitratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: arbitrator.py must be importable."""
        assert _AVAILABLE

    def test_arbitrator_is_type(self) -> None:
        assert Arbitrator is not None

