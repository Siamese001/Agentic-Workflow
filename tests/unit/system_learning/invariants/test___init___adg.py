"""ADG-driven tests for system_learning/invariants/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module invariants must be importable."""
    import system_learning.invariants.__init__ as _mod  # noqa: F401

    assert _mod is not None
