"""Foundational behavioral tests for agentic_core/interfaces/execution_agents.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.execution_agents  # noqa: F401


def test_module_importable():
    """Module execution_agents must be importable."""
    assert agentic_core.interfaces.execution_agents is not None
