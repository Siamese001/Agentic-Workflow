"""ADG-driven tests for apps_lic/scripts/migrate_agents.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module migrate_agents must be importable."""
    import apps_lic.scripts.migrate_agents  # noqa: F401

    assert apps_lic.scripts.migrate_agents is not None
