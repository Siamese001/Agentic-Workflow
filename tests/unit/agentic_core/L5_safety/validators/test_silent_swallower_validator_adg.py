"""ADG importability contract for agentic_core/L5_safety/validators/silent_swallower_validator.py."""
from __future__ import annotations

import agentic_core.L5_safety.validators.silent_swallower_validator  # noqa: F401


def test_module_importable():
    """Module silent_swallower_validator must be importable."""
    assert agentic_core.L5_safety.validators.silent_swallower_validator is not None
