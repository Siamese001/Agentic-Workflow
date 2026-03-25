"""ADG importability contract for agentic_core/L5_safety/validators/golden_state_test_case_validator.py."""
from __future__ import annotations

import agentic_core.L5_safety.validators.golden_state_test_case_validator  # noqa: F401


def test_module_importable():
    """Module golden_state_test_case_validator must be importable."""
    assert agentic_core.L5_safety.validators.golden_state_test_case_validator is not None
