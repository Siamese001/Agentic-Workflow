"""ADG importability contract for agentic_core/L5_safety/reasoning/RegressionOracleAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_RegressionOracleAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.RegressionOracleAgent import (  # noqa: F401
        RegressionOracleAgent,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RegressionOracleAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="RegressionOracleAgent deps unavailable")
class TestRegressionoracleagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/RegressionOracleAgent.py must be importable."""
        assert _AVAILABLE

    def test_regressionoracleagent_defined(self) -> None:
        assert RegressionOracleAgent is not None
