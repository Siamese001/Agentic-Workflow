"""ADG-driven tests for agentic_core/L5_safety/utils/enforce_length_limits_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.utils.enforce_length_limits_util  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.utils.enforce_length_limits_util  # noqa: F401
        """Module enforce_length_limits_util must be importable."""
        assert agentic_core.L5_safety.utils.enforce_length_limits_util is not None

    assert agentic_core.L5_safety.utils.enforce_length_limits_util is not None
