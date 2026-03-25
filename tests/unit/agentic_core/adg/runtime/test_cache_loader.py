"""Foundational behavioral tests for agentic_core/adg/runtime/cache_loader.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.adg.runtime.cache_loader  # noqa: F401


def test_module_importable():
    """Module cache_loader must be importable."""
    assert agentic_core.adg.runtime.cache_loader is not None
