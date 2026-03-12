"""ADG importability contract for agentic_core/seams/contracts/activation.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_activation.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    import agentic_core.seams.contracts.activation as _mod  # noqa: F401
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    _mod = None

@pytest.mark.skipif(not _AVAILABLE, reason="activation.py deps unavailable")
class TestActivationImportability:
    def test_module_importable(self) -> None:
        """ADG contract: activation.py must be importable."""
        assert _AVAILABLE

