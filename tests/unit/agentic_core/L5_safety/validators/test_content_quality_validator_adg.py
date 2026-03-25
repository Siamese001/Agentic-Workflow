"""ADG importability contract for agentic_core/L5_safety/validators/content_quality_validator.py."""
from __future__ import annotations

import agentic_core.L5_safety.validators.content_quality_validator  # noqa: F401


def test_module_importable():
    """Module content_quality_validator must be importable."""
    assert agentic_core.L5_safety.validators.content_quality_validator is not None
