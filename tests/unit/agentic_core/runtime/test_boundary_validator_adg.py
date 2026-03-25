"""ADG-driven tests for agentic_core/runtime/boundary_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.runtime.boundary_validator  # noqa: F401


def test_module_importable():
    """Module boundary_validator must be importable."""
    assert agentic_core.runtime.boundary_validator is not None
