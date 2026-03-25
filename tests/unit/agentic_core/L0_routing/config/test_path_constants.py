"""Foundational behavioral tests for agentic_core/L0_routing/config/path_constants.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.config.path_constants  # noqa: F401


def test_module_importable():
    """Module path_constants must be importable."""
    assert agentic_core.L0_routing.config.path_constants is not None
