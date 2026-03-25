"""ADG importability contract for agentic_core/L5_safety/validators/config_with_logic_validator.py."""
from __future__ import annotations

import agentic_core.L5_safety.validators.config_with_logic_validator  # noqa: F401


def test_module_importable():
    """Module config_with_logic_validator must be importable."""
    assert agentic_core.L5_safety.validators.config_with_logic_validator is not None
