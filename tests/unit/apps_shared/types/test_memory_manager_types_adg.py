"""ADG contract tests for apps_shared/types/memory_manager_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.memory_manager_types  # noqa: F401


def test_module_importable():
    """Module memory_manager_types must be importable."""
    assert apps_shared.types.memory_manager_types is not None
