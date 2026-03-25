"""ADG-driven tests for agentic_core/interfaces/ shim modules — fan_in batch."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.meta_control  # noqa: F401


def test_module_importable():
    """Module meta_control must be importable."""
    assert agentic_core.interfaces.meta_control is not None
