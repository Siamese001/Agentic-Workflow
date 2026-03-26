"""ADG-driven tests for agentic_core/L5_safety/utils/tiered_batch_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.utils.tiered_batch_util  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.utils.tiered_batch_util  # noqa: F401
    """Module tiered_batch_util must be importable."""
    assert agentic_core.L5_safety.utils.tiered_batch_util is not None
