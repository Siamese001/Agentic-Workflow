"""ADG-driven tests for agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L3_orchestration.reasoning.SemanticGatekeeperAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L3_orchestration.reasoning.SemanticGatekeeperAgent  # noqa: F401
        """Module SemanticGatekeeperAgent must be importable."""
        assert agentic_core.L3_orchestration.reasoning.SemanticGatekeeperAgent is not None

    assert agentic_core.L3_orchestration.reasoning.SemanticGatekeeperAgent is not None
