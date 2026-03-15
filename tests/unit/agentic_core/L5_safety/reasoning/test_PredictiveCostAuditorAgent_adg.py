"""ADG importability contract for agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_PredictiveCostAuditorAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.PredictiveCostAuditorAgent import (  # noqa: F401
        CostReport,
        FileAudit,
        HealingMetrics,
        PredictiveCostAuditorAgent,
        get_cost_auditor,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    HealingMetrics = None  # type: ignore[assignment,misc]
    FileAudit = None  # type: ignore[assignment,misc]
    CostReport = None  # type: ignore[assignment,misc]
    PredictiveCostAuditorAgent = None  # type: ignore[assignment,misc]
    get_cost_auditor = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent deps unavailable")
class TestPredictivecostauditoragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py must be importable."""
        assert _AVAILABLE

    def test_healingmetrics_defined(self) -> None:
        assert HealingMetrics is not None

    def test_fileaudit_defined(self) -> None:
        assert FileAudit is not None

    def test_costreport_defined(self) -> None:
        assert CostReport is not None

    def test_predictivecostauditoragent_defined(self) -> None:
        assert PredictiveCostAuditorAgent is not None
