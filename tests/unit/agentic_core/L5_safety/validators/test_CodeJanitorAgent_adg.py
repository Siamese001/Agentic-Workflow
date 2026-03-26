"""ADG-driven tests for agentic_core/L5_safety/validators/CodeJanitorAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.validators.CodeJanitorAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.validators.CodeJanitorAgent  # noqa: F401
    """Module CodeJanitorAgent must be importable."""
    assert agentic_core.L5_safety.validators.CodeJanitorAgent is not None
