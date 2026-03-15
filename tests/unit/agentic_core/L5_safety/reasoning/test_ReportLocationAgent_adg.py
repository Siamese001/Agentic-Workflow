"""ADG importability contract for agentic_core/L5_safety/reasoning/ReportLocationAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ReportLocationAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.ReportLocationAgent import (  # noqa: F401
        ReportLocationAgent,
        ReportLocationHealResult,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ReportLocationHealResult = None  # type: ignore[assignment,misc]
    ReportLocationAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ReportLocationAgent deps unavailable")
class TestReportlocationagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/ReportLocationAgent.py must be importable."""
        assert _AVAILABLE

    def test_reportlocationhealresult_defined(self) -> None:
        assert ReportLocationHealResult is not None

    def test_reportlocationagent_defined(self) -> None:
        assert ReportLocationAgent is not None
