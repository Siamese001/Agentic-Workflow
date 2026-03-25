"""ADG contract tests for L3_orchestration/types/healer_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L3_orchestration.types.healer_types  # noqa: F401


def test_module_importable():
    """Module healer_types must be importable."""
    assert agentic_core.L3_orchestration.types.healer_types is not None
