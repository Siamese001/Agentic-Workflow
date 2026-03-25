"""ADG-driven tests for apps_lic/scripts/fix_lic_imports.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.scripts.fix_lic_imports  # noqa: F401


def test_module_importable():
    """Module fix_lic_imports must be importable."""
    assert apps_lic.scripts.fix_lic_imports is not None
