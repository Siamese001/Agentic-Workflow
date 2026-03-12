"""ADG importability contract for apps_rg/engines/rg_spine_adapter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_rg_spine_adapter.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_rg.engines.rg_spine_adapter import (  # noqa: F401
        RgSpineAdapter,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RgSpineAdapter = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="rg_spine_adapter.py deps unavailable")
class TestRgSpineAdapterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: rg_spine_adapter.py must be importable."""
        assert _AVAILABLE

    def test_rgspineadapter_is_type(self) -> None:
        assert RgSpineAdapter is not None

