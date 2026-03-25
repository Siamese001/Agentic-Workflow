"""ADG importability contract for agentic_core/L5_safety/validators/governance_validator.py."""
from __future__ import annotations

import agentic_core.L5_safety.validators.governance_validator  # noqa: F401


def test_module_importable():
    """Module governance_validator must be importable."""
    assert agentic_core.L5_safety.validators.governance_validator is not None
