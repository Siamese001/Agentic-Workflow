"""ADG-driven tests for agentic_core/L1_cognition/utils/template_matcher_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L1_cognition.utils.template_matcher_util  # noqa: F401


def test_module_importable():
    import agentic_core.L1_cognition.utils.template_matcher_util  # noqa: F401
    """Module template_matcher_util must be importable."""
    assert agentic_core.L1_cognition.utils.template_matcher_util is not None
