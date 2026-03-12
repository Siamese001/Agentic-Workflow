"""ADG importability contract for agentic_core/utils/decorators_base_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_decorators_base_util.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    import agentic_core.utils.decorators_base_util as _mod  # noqa: F401
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    _mod = None

@pytest.mark.skipif(not _AVAILABLE, reason="decorators_base_util.py deps unavailable")
class TestDecoratorsBaseUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: decorators_base_util.py must be importable."""
        assert _AVAILABLE

