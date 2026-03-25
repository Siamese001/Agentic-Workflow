"""ADG importability contract for agentic_core/L5_safety/validators/gravity_validator.py."""
from __future__ import annotations

import agentic_core.L5_safety.validators.gravity_validator  # noqa: F401


def test_module_importable():
    """Module gravity_validator must be importable."""
    assert agentic_core.L5_safety.validators.gravity_validator is not None
