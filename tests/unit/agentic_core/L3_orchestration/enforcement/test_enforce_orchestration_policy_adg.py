"""ADG-driven tests for agentic_core/L3_orchestration/enforcement/enforce_orchestration_policy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L3_orchestration.enforcement.enforce_orchestration_policy  # noqa: F401


def test_module_importable():
        import agentic_core.L3_orchestration.enforcement.enforce_orchestration_policy  # noqa: F401
        """Module enforce_orchestration_policy must be importable."""
        assert agentic_core.L3_orchestration.enforcement.enforce_orchestration_policy is not None

    assert agentic_core.L3_orchestration.enforcement.enforce_orchestration_policy is not None
