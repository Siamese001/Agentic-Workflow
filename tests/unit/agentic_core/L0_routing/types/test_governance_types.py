"""Foundational behavioral tests for agentic_core/L0_routing/types/governance_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.types.governance_types  # noqa: F401


def test_module_importable():
    """Module governance_types must be importable."""
    assert agentic_core.L0_routing.types.governance_types is not None
