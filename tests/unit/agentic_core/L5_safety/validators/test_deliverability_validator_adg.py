"""ADG importability contract for agentic_core/L5_safety/validators/deliverability_validator.py."""
from __future__ import annotations

import agentic_core.L5_safety.validators.deliverability_validator  # noqa: F401


def test_module_importable():
    """Module deliverability_validator must be importable."""
    assert agentic_core.L5_safety.validators.deliverability_validator is not None
