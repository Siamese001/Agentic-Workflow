"""Foundational behavioral tests for agentic_core/L2_execution/types/heal_contract_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.types.heal_contract_types  # noqa: F401


def test_module_importable():
    """Module heal_contract_types must be importable."""
    assert agentic_core.L2_execution.types.heal_contract_types is not None
