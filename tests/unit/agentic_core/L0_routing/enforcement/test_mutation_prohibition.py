"""Foundational behavioral tests for agentic_core/L0_routing/enforcement/mutation_prohibition.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.enforcement.mutation_prohibition  # noqa: F401


def test_module_importable():
    """Module mutation_prohibition must be importable."""
    assert agentic_core.L0_routing.enforcement.mutation_prohibition is not None
