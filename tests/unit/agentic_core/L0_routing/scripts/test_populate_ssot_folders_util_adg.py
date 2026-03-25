"""ADG-driven tests for agentic_core/L0_routing/scripts/populate_ssot_folders_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.populate_ssot_folders_util  # noqa: F401


def test_module_importable():
    """Module populate_ssot_folders_util must be importable."""
    assert agentic_core.L0_routing.scripts.populate_ssot_folders_util is not None
