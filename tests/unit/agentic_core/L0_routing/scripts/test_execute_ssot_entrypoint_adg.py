"""ADG-driven tests for agentic_core/L0_routing/scripts/execute_ssot_entrypoint.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.execute_ssot_entrypoint  # noqa: F401


def test_module_importable():
    """Module execute_ssot_entrypoint must be importable."""
    assert agentic_core.L0_routing.scripts.execute_ssot_entrypoint is not None
