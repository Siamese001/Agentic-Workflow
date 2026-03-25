"""Foundational behavioral tests for agentic_core/mixins/safety_mixin.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.mixins.safety_mixin  # noqa: F401


def test_module_importable():
    """Module safety_mixin must be importable."""
    assert agentic_core.mixins.safety_mixin is not None
