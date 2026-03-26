"""ADG-driven tests for L5_safety/reasoning/RedTeamAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.reasoning.RedTeamAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.reasoning.RedTeamAgent  # noqa: F401
    """Module RedTeamAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.RedTeamAgent is not None
