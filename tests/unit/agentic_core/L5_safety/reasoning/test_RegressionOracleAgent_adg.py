"""ADG importability contract for agentic_core/L5_safety/reasoning/RegressionOracleAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.RegressionOracleAgent  # noqa: F401


def test_module_importable():
    """Module RegressionOracleAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.RegressionOracleAgent is not None
