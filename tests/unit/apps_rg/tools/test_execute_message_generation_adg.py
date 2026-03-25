"""ADG-driven tests for apps_rg/tools/execute_message_generation.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.execute_message_generation  # noqa: F401


def test_module_importable():
    """Module execute_message_generation must be importable."""
    assert apps_rg.tools.execute_message_generation is not None
