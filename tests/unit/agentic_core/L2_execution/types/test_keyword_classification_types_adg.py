"""ADG-driven tests for L2_execution/types/keyword_classification_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.types.keyword_classification_types  # noqa: F401


def test_module_importable():
    """Module keyword_classification_types must be importable."""
    assert agentic_core.L2_execution.types.keyword_classification_types is not None
