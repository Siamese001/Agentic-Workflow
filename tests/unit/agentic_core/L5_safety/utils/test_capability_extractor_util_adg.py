"""ADG-driven tests for agentic_core/L5_safety/utils/capability_extractor_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.utils.capability_extractor_util  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.utils.capability_extractor_util  # noqa: F401
        """Module capability_extractor_util must be importable."""
        assert agentic_core.L5_safety.utils.capability_extractor_util is not None

    assert agentic_core.L5_safety.utils.capability_extractor_util is not None
