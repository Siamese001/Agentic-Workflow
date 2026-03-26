"""ADG-driven tests for agentic_core/utils/timeout_decorator_impl_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.utils.timeout_decorator_impl_util  # noqa: F401


def test_module_importable():
    import agentic_core.utils.timeout_decorator_impl_util  # noqa: F401
    """Module timeout_decorator_impl_util must be importable."""
    assert agentic_core.utils.timeout_decorator_impl_util is not None
