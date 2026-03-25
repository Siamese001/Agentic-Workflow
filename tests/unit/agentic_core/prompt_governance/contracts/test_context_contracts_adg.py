"""ADG-driven tests for agentic_core/prompt_governance/contracts/context_contracts.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.prompt_governance.contracts.context_contracts  # noqa: F401


def test_module_importable():
    """Module context_contracts must be importable."""
    assert agentic_core.prompt_governance.contracts.context_contracts is not None
