"""Foundational behavioral tests for apps_rg/engines/base_rg_engine.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.engines.base_rg_engine  # noqa: F401


def test_module_importable():
    """Module base_rg_engine must be importable."""
    assert apps_rg.engines.base_rg_engine is not None
