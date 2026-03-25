"""ADG-driven tests for agentic_core/mixins/ast_enforcement_mixin.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.mixins.ast_enforcement_mixin  # noqa: F401


def test_module_importable():
    """Module ast_enforcement_mixin must be importable."""
    assert agentic_core.mixins.ast_enforcement_mixin is not None
