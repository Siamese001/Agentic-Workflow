"""ADG-driven tests for L1_cognition/utils/constants_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L1_cognition.utils.constants_util  # noqa: F401


def test_module_importable():
    import agentic_core.L1_cognition.utils.constants_util  # noqa: F401
    """Module constants_util must be importable."""
    assert agentic_core.L1_cognition.utils.constants_util is not None
