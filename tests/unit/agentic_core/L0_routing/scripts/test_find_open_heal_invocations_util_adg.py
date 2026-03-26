"""ADG-driven tests for agentic_core/L0_routing/scripts/find_open_heal_invocations_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L0_routing.scripts.find_open_heal_invocations_util  # noqa: F401


def test_module_importable():
    import agentic_core.L0_routing.scripts.find_open_heal_invocations_util  # noqa: F401
    """Module find_open_heal_invocations_util must be importable."""
    assert agentic_core.L0_routing.scripts.find_open_heal_invocations_util is not None
