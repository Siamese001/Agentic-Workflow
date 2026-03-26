"""ADG contract tests for L3_orchestration/types/hop_status_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
#  # MOVED: from agentic_core.L3_orchestration.types.hop_status_types import GateDecision, HopStatus


class TestHopStatus:
    def test_is_enum(self):
        from agentic_core.L3_orchestration.types.hop_status_types import GateDecision, HopStatus
        import enum; assert issubclass(HopStatus, enum.Enum)

class TestGateDecision:
    def test_is_enum(self):
        import enum; assert issubclass(GateDecision, enum.Enum)
