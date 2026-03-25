"""ADG-driven tests for agentic_core/L4_state/enforcement/genealogy_registry.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L4_state.enforcement.genealogy_registry  # noqa: F401


def test_module_importable():
    """Module genealogy_registry must be importable."""
    assert agentic_core.L4_state.enforcement.genealogy_registry is not None
