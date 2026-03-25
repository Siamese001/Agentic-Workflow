"""ADG-driven tests for apps_shared/scripts/refactor_agents_to_subatomic.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.refactor_agents_to_subatomic  # noqa: F401


def test_module_importable():
    """Module refactor_agents_to_subatomic must be importable."""
    assert apps_shared.scripts.refactor_agents_to_subatomic is not None
