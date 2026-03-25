"""Foundational behavioral tests for agentic_core/utils/decorators_util.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.decorators_util  # noqa: F401


def test_module_importable():
    """Module decorators_util must be importable."""
    assert agentic_core.utils.decorators_util is not None
