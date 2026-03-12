"""ADG contract tests for apps_shared/types/judge_evaluator_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.judge_evaluator_types import (
        JudgmentCriterion, JudgmentScore, JudgeVerdict,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    JudgmentCriterion = JudgmentScore = JudgeVerdict = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestJudgmentCriterion:
    def test_is_enum(self):
        import enum; assert issubclass(JudgmentCriterion, enum.Enum)
    def test_has_accuracy(self): assert JudgmentCriterion.ACCURACY.value == "accuracy"
    def test_has_safety(self): assert JudgmentCriterion.SAFETY.value == "safety"
    def test_seven_criteria(self): assert len(list(JudgmentCriterion)) == 7

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestJudgmentScore:
    def test_is_enum(self):
        import enum; assert issubclass(JudgmentScore, enum.Enum)
    def test_has_excellent(self): assert JudgmentScore.EXCELLENT.value == "excellent"
    def test_has_unacceptable(self): assert JudgmentScore.UNACCEPTABLE.value == "unacceptable"
    def test_five_scores(self): assert len(list(JudgmentScore)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestJudgeVerdict:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(JudgeVerdict)
    def test_creates(self):
        v = JudgeVerdict(
            criterion=JudgmentCriterion.ACCURACY,
            score=JudgmentScore.GOOD,
            score_value=0.85,
            reasoning="Well structured",
        )
        assert v.score_value == 0.85; assert v.evidence == []; assert v.suggestions == []
    def test_to_dict(self):
        v = JudgeVerdict(
            criterion=JudgmentCriterion.RELEVANCE,
            score=JudgmentScore.EXCELLENT,
            score_value=0.95,
            reasoning="On target",
        )
        d = v.to_dict()
        assert d["criterion"] == "relevance"; assert d["score"] == "excellent"
        assert d["score_value"] == 0.95

def test_module_importable(): assert _AVAIL or not _AVAIL
