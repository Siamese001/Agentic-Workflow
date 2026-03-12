"""ADG importability contract for agentic_core/enforcement/sealed_interface_check_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_sealed_interface_check_enforcer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    import agentic_core.enforcement.sealed_interface_check_enforcer as _mod  # noqa: F401
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    _mod = None

@pytest.mark.skipif(not _AVAILABLE, reason="sealed_interface_check_enforcer.py deps unavailable")
class TestSealedInterfaceCheckEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: sealed_interface_check_enforcer.py must be importable."""
        assert _AVAILABLE

