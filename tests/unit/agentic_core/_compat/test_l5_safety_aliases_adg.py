"""ADG-driven tests for agentic_core/_compat/l5_safety_aliases.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core._compat.l5_safety_aliases as _mod  # noqa: F401


def test_module_importable():
    import agentic_core._compat.l5_safety_aliases as _mod  # noqa: F401
    """Module l5_safety_aliases must be importable."""
    assert _mod is not None
