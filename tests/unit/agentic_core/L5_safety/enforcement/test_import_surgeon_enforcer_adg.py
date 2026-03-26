"""ADG-driven tests for agentic_core/L5_safety/enforcement/import_surgeon_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.enforcement.import_surgeon_enforcer  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.enforcement.import_surgeon_enforcer  # noqa: F401
    """Module import_surgeon_enforcer must be importable."""
    assert agentic_core.L5_safety.enforcement.import_surgeon_enforcer is not None
