"""ADG-driven tests for agentic_core/L5_safety/invariants/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.invariants.__init__ as _mod  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.invariants.__init__ as _mod  # noqa: F401
    """Module invariants must be importable."""
    assert _mod is not None
