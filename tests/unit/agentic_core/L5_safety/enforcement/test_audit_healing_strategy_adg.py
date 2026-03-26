"""ADG-driven tests for agentic_core/L5_safety/enforcement/audit_healing_strategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.enforcement.audit_healing_strategy  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.enforcement.audit_healing_strategy  # noqa: F401
    """Module audit_healing_strategy must be importable."""
    assert agentic_core.L5_safety.enforcement.audit_healing_strategy is not None
