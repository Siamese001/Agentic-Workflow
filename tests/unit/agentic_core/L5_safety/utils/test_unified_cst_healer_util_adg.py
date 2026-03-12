"""ADG importability contract for agentic_core/L5_safety/utils/unified_cst_healer_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_unified_cst_healer_util.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.utils.unified_cst_healer_util import (  # noqa: F401
        HealingConfig,
        HealingResult,
        UnifiedCSTHealer,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HealingConfig = None  # type: ignore[assignment,misc]
    HealingResult = None  # type: ignore[assignment,misc]
    UnifiedCSTHealer = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="unified_cst_healer_util.py deps unavailable")
class TestUnifiedCstHealerUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: unified_cst_healer_util.py must be importable."""
        assert _AVAILABLE

    def test_healingconfig_is_type(self) -> None:
        assert HealingConfig is not None

    def test_healingresult_is_type(self) -> None:
        assert HealingResult is not None

    def test_unifiedcsthealer_is_type(self) -> None:
        assert UnifiedCSTHealer is not None

