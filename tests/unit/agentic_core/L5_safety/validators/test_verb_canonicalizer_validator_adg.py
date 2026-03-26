"""ADG-driven tests for agentic_core/L5_safety/validators/verb_canonicalizer_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.validators.verb_canonicalizer_validator  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.validators.verb_canonicalizer_validator  # noqa: F401
    """Module verb_canonicalizer_validator must be importable."""
    assert agentic_core.L5_safety.validators.verb_canonicalizer_validator is not None
