"""Foundational behavioral tests for agentic_core/L0_routing/enforcement/runtime_guard.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.enforcement.runtime_guard  # noqa: F401


def test_module_importable():
    """Module runtime_guard must be importable."""
    assert agentic_core.L0_routing.enforcement.runtime_guard is not None
