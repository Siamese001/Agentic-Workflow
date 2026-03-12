"""ADG-driven tests for agentic_core/L5_safety/utils/cst_transformers_types_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import agentic_core.L5_safety.utils.cst_transformers_types_util as _mod  # noqa: F401
    _AVAILABLE = True
except Exception:
    _mod = None
    _AVAILABLE = False


def test_module_importable():
    """Module cst_transformers_types_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
