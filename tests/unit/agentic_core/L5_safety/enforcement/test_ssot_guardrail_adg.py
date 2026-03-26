"""ADG-driven tests for agentic_core/L5_safety/enforcement/ssot_guardrail.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.enforcement.ssot_guardrail  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.enforcement.ssot_guardrail  # noqa: F401
    """Module ssot_guardrail must be importable."""
    assert agentic_core.L5_safety.enforcement.ssot_guardrail is not None
