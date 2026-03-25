"""ADG-driven tests for apps_shared/scripts/batch_refactor_agents.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.batch_refactor_agents  # noqa: F401


def test_module_importable():
    """Module batch_refactor_agents must be importable."""
    assert apps_shared.scripts.batch_refactor_agents is not None
