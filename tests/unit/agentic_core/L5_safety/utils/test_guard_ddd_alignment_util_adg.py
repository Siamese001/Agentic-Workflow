"""ADG-driven tests for agentic_core/L5_safety/utils/guard_ddd_alignment_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.utils.guard_ddd_alignment_util  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.utils.guard_ddd_alignment_util  # noqa: F401
    """Module guard_ddd_alignment_util must be importable."""
    assert agentic_core.L5_safety.utils.guard_ddd_alignment_util is not None
