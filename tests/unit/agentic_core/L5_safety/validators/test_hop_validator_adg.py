"""ADG importability contract for agentic_core/L5_safety/validators/hop_validator.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.validators.hop_validator  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.validators.hop_validator  # noqa: F401
    """Module hop_validator must be importable."""
    assert agentic_core.L5_safety.validators.hop_validator is not None
