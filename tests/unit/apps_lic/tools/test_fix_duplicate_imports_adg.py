"""ADG-driven tests for apps_lic/tools/fix_duplicate_imports.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.fix_duplicate_imports  # noqa: F401


def test_module_importable():
    """Module fix_duplicate_imports must be importable."""
    assert apps_lic.tools.fix_duplicate_imports is not None
