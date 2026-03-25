"""ADG contract tests for apps_shared/types/cost_alert_level_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.cost_alert_level_types  # noqa: F401


def test_module_importable():
    """Module cost_alert_level_types must be importable."""
    assert apps_shared.types.cost_alert_level_types is not None
