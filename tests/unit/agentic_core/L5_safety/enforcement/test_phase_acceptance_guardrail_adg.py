"""ADG-driven tests for agentic_core/L5_safety/enforcement/phase_acceptance_guardrail.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.enforcement.phase_acceptance_guardrail  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.enforcement.phase_acceptance_guardrail  # noqa: F401
        """Module phase_acceptance_guardrail must be importable."""
        assert agentic_core.L5_safety.enforcement.phase_acceptance_guardrail is not None

    assert agentic_core.L5_safety.enforcement.phase_acceptance_guardrail is not None
