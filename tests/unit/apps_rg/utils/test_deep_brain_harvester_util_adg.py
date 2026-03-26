"""ADG-driven tests for apps_rg/utils/deep_brain_harvester_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module deep_brain_harvester_util must be importable."""
    import apps_rg.utils.deep_brain_harvester_util  # noqa: F401

    assert apps_rg.utils.deep_brain_harvester_util is not None
