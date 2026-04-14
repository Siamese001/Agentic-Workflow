"""Smoke tests for the ReAct config surface."""

from __future__ import annotations

import pytest

from L1_cognition.test_support import assert_module_surface


@pytest.mark.unit
def test_react_config_surface():
    assert_module_surface(
        "agentic_core.react_config_adg",
        "ReactConfigAdg",
        "validate_react_config_adg",
    )
