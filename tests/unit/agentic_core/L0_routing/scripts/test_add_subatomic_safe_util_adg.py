"""ADG-driven tests for agentic_core/L0_routing/scripts/add_subatomic_safe_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L0_routing.scripts.add_subatomic_safe_util  # noqa: F401


def test_module_importable():
        import agentic_core.L0_routing.scripts.add_subatomic_safe_util  # noqa: F401
        """Module add_subatomic_safe_util must be importable."""
        assert agentic_core.L0_routing.scripts.add_subatomic_safe_util is not None

    assert agentic_core.L0_routing.scripts.add_subatomic_safe_util is not None
