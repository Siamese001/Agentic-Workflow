"""ADG-driven tests for agentic_core/L5_safety/enforcement/circular_import_fixer_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.enforcement.circular_import_fixer_enforcer  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.enforcement.circular_import_fixer_enforcer  # noqa: F401
    """Module circular_import_fixer_enforcer must be importable."""
    assert agentic_core.L5_safety.enforcement.circular_import_fixer_enforcer is not None
