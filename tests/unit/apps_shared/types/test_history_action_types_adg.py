"""ADG contract tests for apps_shared/types/history_action_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.history_action_types  # noqa: F401


def test_module_importable():
    """Module history_action_types must be importable."""
    assert apps_shared.types.history_action_types is not None
