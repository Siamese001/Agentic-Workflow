"""ADG-driven tests for agentic_core/L6_observability/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L6_observability.__init__ as _mod  # noqa: F401


def test_module_importable():
    import agentic_core.L6_observability.__init__ as _mod  # noqa: F401
    """Module L6_observability must be importable."""
    assert _mod is not None
