"""Foundational behavioral tests for agentic_core/adg/analysis/hotspot_index.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.adg.analysis.hotspot_index_types  # noqa: F401


def test_module_importable():
    """Module hotspot_index_types must be importable."""
    assert agentic_core.adg.analysis.hotspot_index_types is not None
