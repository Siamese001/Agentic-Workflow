"""ADG-driven tests for agentic_core/L5_safety/config/structure_blueprint/_verify.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.config.structure_blueprint._verify  # noqa: F401


def test_module_importable():
    """Module _verify must be importable."""
    assert agentic_core.L5_safety.config.structure_blueprint._verify is not None
