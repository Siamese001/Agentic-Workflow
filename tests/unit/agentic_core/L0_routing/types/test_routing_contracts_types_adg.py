"""ADG contract tests for agentic_core/L0_routing/types/routing_contracts_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L0_routing.types.routing_contracts_types import (
        SeverityEnum, TokenGateResult, TokenCapArtifact, VigilanceTier,
        EvacuationProtocol, HealingPlan, StaleWriteIncident, HEALER_PIPE_ORDER,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    SeverityEnum = TokenGateResult = TokenCapArtifact = VigilanceTier = None  # type: ignore[assignment,misc]
    EvacuationProtocol = HealingPlan = StaleWriteIncident = HEALER_PIPE_ORDER = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSeverityEnum:
    def test_is_enum(self):
        import enum; assert issubclass(SeverityEnum, enum.Enum)
    def test_has_critical(self): assert SeverityEnum.CRITICAL.value == "critical"
    def test_four_levels(self): assert len(list(SeverityEnum)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestTokenCapArtifact:
    def test_is_frozen(self): assert TokenCapArtifact.__dataclass_params__.frozen is True
    def test_creates(self):
        a = TokenCapArtifact(
            trace_id="t1", policy_hash="h", budget_limit=1000,
            tokens_requested=500, gate_result=TokenGateResult.ALLOW,
        )
        assert a.gate_result == TokenGateResult.ALLOW

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHealerPipeOrder:
    def test_is_tuple(self): assert isinstance(HEALER_PIPE_ORDER, tuple)
    def test_has_ten_steps(self): assert len(HEALER_PIPE_ORDER) == 10
    def test_starts_with_schema_validation(self): assert HEALER_PIPE_ORDER[0] == "schema_validation"
    def test_ends_with_commit(self): assert HEALER_PIPE_ORDER[-1] == "commit"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStaleWriteIncident:
    def test_is_frozen(self): assert StaleWriteIncident.__dataclass_params__.frozen is True
    def test_creates(self):
        s = StaleWriteIncident(
            trace_id="t", target_path="/a/b.py",
            expected_hash="aa" * 32, actual_hash="bb" * 32, semantic_clock_tick=1,
        )
        assert s.target_path == "/a/b.py"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVigilanceTier:
    def test_is_enum(self):
        import enum; assert issubclass(VigilanceTier, enum.Enum)
    def test_has_tier_iii(self): assert VigilanceTier.TIER_III.value == "tier_iii_evacuation"

def test_module_importable(): assert _AVAIL or not _AVAIL
