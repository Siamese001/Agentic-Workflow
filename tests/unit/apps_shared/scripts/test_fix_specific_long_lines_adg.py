"""ADG-driven tests for apps_shared/scripts/fix_specific_long_lines.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module fix_specific_long_lines must be importable."""
    import apps_shared.scripts.fix_specific_long_lines  # noqa: F401

    assert apps_shared.scripts.fix_specific_long_lines is not None