"""ADG-driven tests for agentic_core/L5_safety/utils/cst_transformers_types_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.utils.cst_transformers_types_util as _mod  # noqa: F401


def test_module_importable():
    """Module cst_transformers_types_util must be importable."""
    assert _mod is not None
