"""ADG-driven tests for apps_lic/utils/hop_stage_capability_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module hop_stage_capability_util must be importable."""
    import apps_lic.utils.hop_stage_capability_util  # noqa: F401

    assert apps_lic.utils.hop_stage_capability_util is not None