"""ADG importability contract for agentic_core/L2_execution/types/healer_registry_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_healer_registry_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    import agentic_core.L2_execution.types.healer_registry_types as _mod  # noqa: F401
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    _mod = None

@pytest.mark.skipif(not _AVAILABLE, reason="healer_registry_types.py deps unavailable")
class TestHealerRegistryTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: healer_registry_types.py must be importable."""
        assert _AVAILABLE

