"""ADG-driven tests for agentic_core/L5_safety/enforcement/artifact_emission_prohibition_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.enforcement.artifact_emission_prohibition_enforcer  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.enforcement.artifact_emission_prohibition_enforcer  # noqa: F401
        """Module artifact_emission_prohibition_enforcer must be importable."""
        assert agentic_core.L5_safety.enforcement.artifact_emission_prohibition_enforcer is not None

    assert agentic_core.L5_safety.enforcement.artifact_emission_prohibition_enforcer is not None
