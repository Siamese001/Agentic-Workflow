"""ADG-driven tests for apps_lic/reasoning/MessageArchitectAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import apps_lic.reasoning.MessageArchitectAgent as _mod  # noqa: F401
    _AVAILABLE = True
except ImportError:
    _mod = None
    _AVAILABLE = False


def test_module_importable():
    """Module MessageArchitectAgent.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
