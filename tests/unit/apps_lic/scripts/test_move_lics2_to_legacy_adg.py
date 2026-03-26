"""ADG-driven tests for apps_lic/scripts/move_lics2_to_legacy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module move_lics2_to_legacy must be importable."""
    import apps_lic.scripts.move_lics2_to_legacy  # noqa: F401

    assert apps_lic.scripts.move_lics2_to_legacy is not None
