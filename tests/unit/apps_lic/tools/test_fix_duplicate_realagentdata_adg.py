"""ADG-driven tests for apps_lic/tools/fix_duplicate_realagentdata.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module fix_duplicate_realagentdata must be importable."""
    import apps_lic.tools.fix_duplicate_realagentdata  # noqa: F401

    assert apps_lic.tools.fix_duplicate_realagentdata is not None
