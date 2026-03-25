"""ADG contract tests for L5_safety/types/specificity_prose_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.types.specificity_prose_types  # noqa: F401


def test_module_importable():
    """Module specificity_prose_types must be importable."""
    assert agentic_core.L5_safety.types.specificity_prose_types is not None
