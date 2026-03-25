"""ADG-driven tests for L0_routing/types/v15_contracts_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.types.v15_contracts_types  # noqa: F401


def test_module_importable():
    """Module v15_contracts_types must be importable."""
    assert agentic_core.L0_routing.types.v15_contracts_types is not None
