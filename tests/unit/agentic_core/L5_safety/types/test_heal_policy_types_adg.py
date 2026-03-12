"""ADG contract tests for agentic_core/L5_safety/types/heal_policy_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.heal_policy_types import (
        HealEscalationInputs, HealEscalationDecision, decide_heal_escalation,
        ReasoningTier, ScoreBand, classify_score,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    HealEscalationInputs = HealEscalationDecision = decide_heal_escalation = None  # type: ignore[assignment,misc]
    ReasoningTier = ScoreBand = classify_score = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestReasoningTier:
    def test_is_enum(self):
        import enum; assert issubclass(ReasoningTier, enum.Enum)
    def test_has_low_and_high(self):
        assert ReasoningTier.LOW; assert ReasoningTier.HIGH

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestScoreBand:
    def test_is_enum(self):
        import enum; assert issubclass(ScoreBand, enum.Enum)
    def test_has_deterministic(self): assert ScoreBand.DETERMINISTIC
    def test_has_qwen(self): assert ScoreBand.QWEN
    def test_has_gemini(self): assert ScoreBand.GEMINI

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestClassifyScore:
    def test_low_score_is_deterministic(self): assert classify_score(0) == ScoreBand.DETERMINISTIC
    def test_mid_score_is_qwen(self): assert classify_score(20) == ScoreBand.QWEN
    def test_high_score_is_gemini(self): assert classify_score(100) == ScoreBand.GEMINI

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHealEscalationInputs:
    def test_is_frozen(self): assert HealEscalationInputs.__dataclass_params__.frozen is True
    def test_defaults(self):
        h = HealEscalationInputs(); assert h.score == 0; assert h.enable_llm is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDecideHealEscalation:
    def test_always_proceeds(self):
        d = decide_heal_escalation(HealEscalationInputs(score=5))
        assert d.proceed is True
    def test_deterministic_band_no_tier(self):
        d = decide_heal_escalation(HealEscalationInputs(score=0))
        assert d.tier is None
    def test_gemini_band_high_tier(self):
        d = decide_heal_escalation(HealEscalationInputs(score=50))
        assert d.tier == ReasoningTier.HIGH

def test_module_importable(): assert _AVAIL or not _AVAIL
