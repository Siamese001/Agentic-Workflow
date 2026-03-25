"""ADG-driven tests for apps_shared/utils/unified_config_helper_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.utils.unified_config_helper_util  # noqa: F401


def test_module_importable():
    """Module unified_config_helper_util must be importable."""
    assert apps_shared.utils.unified_config_helper_util is not None
