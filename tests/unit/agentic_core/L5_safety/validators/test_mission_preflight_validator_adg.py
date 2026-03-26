"""ADG-driven tests for agentic_core/L5_safety/validators/mission_preflight_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.validators.mission_preflight_validator  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.validators.mission_preflight_validator  # noqa: F401
    """Module mission_preflight_validator must be importable."""
    assert agentic_core.L5_safety.validators.mission_preflight_validator is not None
