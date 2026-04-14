"""Smoke tests for the L1 config init surface."""

from __future__ import annotations

import pytest

from L1_cognition.test_support import assert_module_surface


@pytest.mark.unit
def test_l1_config_init_surface():
    assert_module_surface(
        "agentic_core.l1_config_init_adg",
        "L1ConfigInitAdg",
        "validate_l1_config_init_adg",
    )
