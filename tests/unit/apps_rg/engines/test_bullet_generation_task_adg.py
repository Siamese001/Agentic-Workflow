"""ADG-driven tests for apps_rg/engines/bullet_generation_task.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module bullet_generation_task must be importable."""
    import apps_rg.engines.bullet_generation_task  # noqa: F401

    assert apps_rg.engines.bullet_generation_task is not None
