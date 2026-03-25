"""ADG-driven tests for agentic_core/runtime/enforcement/envelope_factory.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.runtime.enforcement.envelope_factory  # noqa: F401


def test_module_importable():
    """Module envelope_factory must be importable."""
    assert agentic_core.runtime.enforcement.envelope_factory is not None
