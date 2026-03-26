"""ADG-driven tests for apps_lic/tools/fix_duplicate_imports.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module fix_duplicate_imports must be importable."""
    import apps_lic.tools.fix_duplicate_imports  # noqa: F401

    assert apps_lic.tools.fix_duplicate_imports is not None
