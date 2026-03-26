"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/CodeValidatorAgent.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.reasoning.CodeValidatorAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.reasoning.CodeValidatorAgent  # noqa: F401
    """Module CodeValidatorAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.CodeValidatorAgent is not None
