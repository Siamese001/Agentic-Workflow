"""ADG-driven tests for apps_lic/utils/cot_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module cot_util must be importable."""
    import apps_lic.utils.cot_util  # noqa: F401

    assert apps_lic.utils.cot_util is not None