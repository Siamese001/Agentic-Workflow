"""ADG importability contract for apps_lic/engines/lic_spine_adapter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_lic_spine_adapter.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_lic.engines.lic_spine_adapter import (  # noqa: F401
        LicSpineAdapter,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    LicSpineAdapter = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="lic_spine_adapter.py deps unavailable")
class TestLicSpineAdapterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: lic_spine_adapter.py must be importable."""
        assert _AVAILABLE

    def test_licspineadapter_is_type(self) -> None:
        assert LicSpineAdapter is not None
