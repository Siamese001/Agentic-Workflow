"""Foundational behavioral tests for agentic_core/utils/timeout_decorator_util.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.timeout_decorator_util  # noqa: F401


def test_module_importable():
    """Module timeout_decorator_util must be importable."""
    assert agentic_core.utils.timeout_decorator_util is not None
