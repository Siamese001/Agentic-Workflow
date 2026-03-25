"""ADG-driven tests for apps_shared/utils/golden_state_datasets_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.utils.golden_state_datasets_util  # noqa: F401


def test_module_importable():
    """Module golden_state_datasets_util must be importable."""
    assert apps_shared.utils.golden_state_datasets_util is not None
