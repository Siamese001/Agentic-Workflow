"""ADG-driven tests for apps_rg/engines/message_generation_task.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.engines.message_generation_task  # noqa: F401


def test_module_importable():
    """Module message_generation_task must be importable."""
    assert apps_rg.engines.message_generation_task is not None
