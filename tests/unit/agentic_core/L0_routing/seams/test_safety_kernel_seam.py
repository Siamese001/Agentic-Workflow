"""Foundational behavioral tests for agentic_core/L0_routing/seams/safety_kernel_seam.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.seams.safety_kernel_seam  # noqa: F401


def test_module_importable():
    """Module safety_kernel_seam must be importable."""
    assert agentic_core.L0_routing.seams.safety_kernel_seam is not None
