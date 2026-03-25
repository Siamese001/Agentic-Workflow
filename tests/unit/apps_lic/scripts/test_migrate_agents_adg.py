"""ADG-driven tests for apps_lic/scripts/migrate_agents.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.scripts.migrate_agents  # noqa: F401


def test_module_importable():
    """Module migrate_agents must be importable."""
    assert apps_lic.scripts.migrate_agents is not None
