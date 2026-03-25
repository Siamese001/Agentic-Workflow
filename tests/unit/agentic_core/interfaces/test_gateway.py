"""Foundational behavioral tests for agentic_core/interfaces/gateway.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.gateway as _mod  # noqa: F401


def test_module_importable():
    """Module gateway must be importable."""
    assert _mod is not None
