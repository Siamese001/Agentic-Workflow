"""ADG-driven tests for mixins/llm_provider_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.mixins.llm_provider_mixin  # noqa: F401


def test_module_importable():
    """Module llm_provider_mixin must be importable."""
    assert agentic_core.mixins.llm_provider_mixin is not None
