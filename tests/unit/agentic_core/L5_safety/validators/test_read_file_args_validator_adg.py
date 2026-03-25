"""ADG importability contract for agentic_core/L5_safety/validators/read_file_args_validator.py."""
from __future__ import annotations

import agentic_core.L5_safety.validators.read_file_args_validator  # noqa: F401


def test_module_importable():
    """Module read_file_args_validator must be importable."""
    assert agentic_core.L5_safety.validators.read_file_args_validator is not None
