"""Foundational behavioral tests for agentic_core/interfaces/write_gateway.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.write_gateway  # noqa: F401


def test_module_importable():
    """Module write_gateway must be importable."""
    assert agentic_core.interfaces.write_gateway is not None
