"""Foundational behavioral tests for apps_rg/types/SovereignContext.py."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module SovereignContext must be importable."""
    import apps_rg.types.SovereignContext  # noqa: F401

    assert apps_rg.types.SovereignContext is not None
