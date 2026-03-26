"""ADG importability contract for agentic_core/L5_safety/validators/path_fragility_validator.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.validators.path_fragility_validator  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.validators.path_fragility_validator  # noqa: F401
    """Module path_fragility_validator must be importable."""
    assert agentic_core.L5_safety.validators.path_fragility_validator is not None
