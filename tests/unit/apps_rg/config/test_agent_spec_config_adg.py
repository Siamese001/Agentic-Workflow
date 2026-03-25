"""ADG-driven tests for apps_rg/config/agent_spec_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.config.agent_spec_config  # noqa: F401


def test_module_importable():
    """Module agent_spec_config must be importable."""
    assert apps_rg.config.agent_spec_config is not None
