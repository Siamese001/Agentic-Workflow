"""ADG-driven tests for L0_routing/enforcement/runtime_mutation_guard.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.enforcement.runtime_mutation_guard  # noqa: F401


def test_module_importable():
    """Module runtime_mutation_guard must be importable."""
    assert agentic_core.L0_routing.enforcement.runtime_mutation_guard is not None
