"""ADG-driven tests for agentic_core/L5_safety/validators/budget_profile_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.validators.budget_profile_validator  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.validators.budget_profile_validator  # noqa: F401
    """Module budget_profile_validator must be importable."""
    assert agentic_core.L5_safety.validators.budget_profile_validator is not None
