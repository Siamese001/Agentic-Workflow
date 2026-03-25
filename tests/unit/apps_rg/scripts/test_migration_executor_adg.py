"""ADG-driven tests for apps_rg/scripts/migration_executor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.scripts.migration_executor  # noqa: F401


def test_module_importable():
    """Module migration_executor must be importable."""
    assert apps_rg.scripts.migration_executor is not None
