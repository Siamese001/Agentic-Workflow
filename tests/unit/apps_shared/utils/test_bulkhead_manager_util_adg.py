"""ADG-driven tests for apps_shared/utils/bulkhead_manager_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.utils.bulkhead_manager_util  # noqa: F401


def test_module_importable():
    """Module bulkhead_manager_util must be importable."""
    assert apps_shared.utils.bulkhead_manager_util is not None
