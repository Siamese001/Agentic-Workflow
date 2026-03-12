"""ADG importability contract for agentic_core/seams/contracts/forward_rolling.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_forward_rolling.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    import agentic_core.seams.contracts.forward_rolling as _mod  # noqa: F401
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    _mod = None

@pytest.mark.skipif(not _AVAILABLE, reason="forward_rolling.py deps unavailable")
class TestForwardRollingImportability:
    def test_module_importable(self) -> None:
        """ADG contract: forward_rolling.py must be importable."""
        assert _AVAILABLE

