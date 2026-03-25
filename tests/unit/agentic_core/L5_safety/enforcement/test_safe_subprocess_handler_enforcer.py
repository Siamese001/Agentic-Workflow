"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.enforcement.safe_subprocess_handler_enforcer  # noqa: F401


def test_module_importable():
    """Module safe_subprocess_handler_enforcer must be importable."""
    assert agentic_core.L5_safety.enforcement.safe_subprocess_handler_enforcer is not None
