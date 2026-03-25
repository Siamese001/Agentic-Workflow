"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.reasoning.CodeEnforcerAgent  # noqa: F401


def test_module_importable():
    """Module CodeEnforcerAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.CodeEnforcerAgent is not None
