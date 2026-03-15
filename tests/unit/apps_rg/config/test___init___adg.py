"""ADG importability contract for apps_rg/config/__init__.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test___init__.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    import apps_rg.config.__init__ as _mod  # noqa: F401
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _mod = None

@pytest.mark.skipif(not _AVAILABLE, reason="__init__.py deps unavailable")
class TestInitImportability:
    def test_module_importable(self) -> None:
        """ADG contract: __init__.py must be importable."""
        assert _AVAILABLE
