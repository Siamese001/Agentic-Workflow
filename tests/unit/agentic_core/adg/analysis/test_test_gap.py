"""Foundational behavioral tests for agentic_core/adg/analysis/test_gap.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.adg.analysis.test_gap_types  # noqa: F401


def test_module_importable():
    """Module test_gap_types must be importable."""
    assert agentic_core.adg.analysis.test_gap_types is not None
