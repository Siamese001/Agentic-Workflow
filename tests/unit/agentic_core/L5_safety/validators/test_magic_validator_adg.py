"""ADG importability contract for agentic_core/L5_safety/validators/magic_validator.py."""
from __future__ import annotations

import agentic_core.L5_safety.validators.magic_validator  # noqa: F401


def test_module_importable():
    """Module magic_validator must be importable."""
    assert agentic_core.L5_safety.validators.magic_validator is not None
