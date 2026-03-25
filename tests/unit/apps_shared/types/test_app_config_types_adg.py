"""ADG contract tests for apps_shared/types/app_config_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.app_config_types  # noqa: F401


def test_module_importable():
    """Module app_config_types must be importable."""
    assert apps_shared.types.app_config_types is not None
