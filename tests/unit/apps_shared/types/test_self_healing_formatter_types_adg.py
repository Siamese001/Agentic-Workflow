"""ADG contract tests for apps_shared/types/self_healing_formatter_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.self_healing_formatter_types  # noqa: F401


def test_module_importable():
    """Module self_healing_formatter_types must be importable."""
    assert apps_shared.types.self_healing_formatter_types is not None
