"""Foundational behavioral tests for agentic_core/adg/analysis/ownership.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.adg.analysis.ModuleOwnership  # noqa: F401


def test_module_importable():
    """Module ModuleOwnership must be importable."""
    assert agentic_core.adg.analysis.ModuleOwnership is not None
