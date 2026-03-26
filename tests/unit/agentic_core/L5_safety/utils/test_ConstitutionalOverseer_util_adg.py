"""ADG-driven tests for agentic_core/L5_safety/utils/ConstitutionalOverseer_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.utils.ConstitutionalOverseer_util  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.utils.ConstitutionalOverseer_util  # noqa: F401
    """Module ConstitutionalOverseer_util must be importable."""
    assert agentic_core.L5_safety.utils.ConstitutionalOverseer_util is not None
