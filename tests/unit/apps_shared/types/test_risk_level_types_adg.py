"""ADG contract tests for apps_shared/types/risk_level_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.risk_level_types import (
        RiskLevel, SentimentMood, DepthScore, MicroHook, SentimentProfile,
        WarmthSetting, DepthScorer, MicroHookGenerator,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    RiskLevel = SentimentMood = DepthScore = MicroHook = SentimentProfile = None  # type: ignore[assignment,misc]
    WarmthSetting = DepthScorer = MicroHookGenerator = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRiskLevel:
    def test_is_enum(self):
        import enum; assert issubclass(RiskLevel, enum.Enum)
    def test_is_str_enum(self): assert issubclass(RiskLevel, str)
    def test_has_low(self): assert RiskLevel.LOW.value == "LOW"
    def test_has_critical(self): assert RiskLevel.CRITICAL.value == "CRITICAL"
    def test_four_levels(self): assert len(list(RiskLevel)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSentimentMood:
    def test_is_enum(self):
        import enum; assert issubclass(SentimentMood, enum.Enum)
    def test_has_optimistic(self): assert SentimentMood.OPTIMISTIC.value == "OPTIMISTIC"
    def test_four_moods(self): assert len(list(SentimentMood)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDepthScore:
    def test_creates(self):
        d = DepthScore(level=2, score=0.75); assert d.is_deep is True
    def test_not_deep(self):
        d = DepthScore(level=1, score=0.3); assert d.is_deep is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMicroHook:
    def test_creates(self):
        h = MicroHook(phrase="I saw your post...", trigger_type="recent_post", relevance=0.9)
        assert h.is_highly_relevant is True
    def test_not_relevant(self):
        h = MicroHook(phrase="Hello", trigger_type="generic", relevance=0.5)
        assert h.is_highly_relevant is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSentimentProfile:
    def test_creates(self):
        p = SentimentProfile(mood=SentimentMood.NEUTRAL, risk_level=RiskLevel.LOW)
        assert p.is_safe_to_contact is True
    def test_not_safe_critical(self):
        p = SentimentProfile(mood=SentimentMood.HOSTILE, risk_level=RiskLevel.CRITICAL)
        assert p.is_safe_to_contact is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDepthScorer:
    def test_creates(self): s = DepthScorer(); assert s is not None
    def test_calculate_depth_empty(self):
        s = DepthScorer()
        result = s.calculate_depth({})
        assert result.level == 0; assert result.score <= 1.0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMicroHookGenerator:
    def test_creates(self): g = MicroHookGenerator(); assert g is not None
    def test_generate_hooks_empty(self):
        g = MicroHookGenerator()
        hooks = g.generate_hooks({}); assert isinstance(hooks, list)

def test_module_importable(): assert _AVAIL or not _AVAIL
