"""ADG contract tests for apps_shared/types/config_type_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.config_type_types  # noqa: F401


def test_module_importable():
    """Module config_type_types must be importable."""
    assert apps_shared.types.config_type_types is not None
