"""ADG-driven tests for apps_shared/scripts/meta_learning_operator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.meta_learning_operator  # noqa: F401


def test_module_importable():
    """Module meta_learning_operator must be importable."""
    assert apps_shared.scripts.meta_learning_operator is not None
