"""ADG-driven tests for apps_shared/scripts/compare_agent_lists.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.compare_agent_lists  # noqa: F401


def test_module_importable():
    """Module compare_agent_lists must be importable."""
    assert apps_shared.scripts.compare_agent_lists is not None
