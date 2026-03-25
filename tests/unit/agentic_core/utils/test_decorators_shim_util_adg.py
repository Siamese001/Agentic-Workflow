"""ADG-driven tests for agentic_core/utils/decorators_shim_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.decorators_shim_util as _mod  # noqa: F401


def test_module_importable():
    """Module decorators_shim_util must be importable."""
    assert _mod is not None
