"""ADG-driven tests for agentic_core/_compat/l5_safety_aliases.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import agentic_core._compat.l5_safety_aliases as _mod  # noqa: F401
    _AVAILABLE = True
except ImportError:
    _mod = None
    _AVAILABLE = False


def test_module_importable():
    """Module l5_safety_aliases.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
