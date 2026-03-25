"""ADG-driven tests for apps_shared/utils/contextual_compressor_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.utils.contextual_compressor_util  # noqa: F401


def test_module_importable():
    """Module contextual_compressor_util must be importable."""
    assert apps_shared.utils.contextual_compressor_util is not None
