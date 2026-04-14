"""Smoke tests for the mission status surface."""

from __future__ import annotations

import pytest

from L1_cognition.test_support import assert_module_surface


@pytest.mark.unit
def test_mission_status_surface():
    assert_module_surface(
        "agentic_core.mission_status_adg",
        "MissionStatusAdg",
        "validate_mission_status_adg",
    )
