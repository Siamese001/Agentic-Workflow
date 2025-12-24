from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field
from enum import Enum, auto
"""Types and models for judge_evaluator."""
import logging

LOGGER = logging.getLogger(__name__)
class JudgmentCriterion(Enum):
    """Criteria for judging output quality."""
    ACCURACY = 'accuracy'
    COMPLETENESS = 'completeness'
    RELEVANCE = 'relevance'
    COHERENCE = 'coherence'
    FACTUALITY = 'factuality'
    SAFETY = 'safety'
    HELPFULNESS = 'helpfulness'

class JudgmentScore(Enum):
    """Judgment score levels."""
    EXCELLENT = 'excellent'
    GOOD = 'good'
    ACCEPTABLE = 'acceptable'
    POOR = 'poor'
    UNACCEPTABLE = 'unacceptable'

@dataclass
class JudgeVerdict:
    """Verdict from LM-as-a-Judge evaluation."""
    criterion: JudgmentCriterion
    score: JudgmentScore
    score_value: float
    reasoning: str
    evidence: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'criterion': self.criterion.value, 'score': self.score.value, 'score_value': self.score_value,
        'reasoning': self.reasoning,
        'evidence': self.evidence,
        'suggestions': self.suggestions}

@dataclass
class JudgeEvaluationResult:
    """Complete evaluation result from judge."""
    overall_score: float
    verdicts: List[JudgeVerdict]
    passed: bool
    threshold: float
    summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'overall_score': self.overall_score,
            'verdicts': [v.to_dict() for v in self.verdicts],
            'passed': self.passed,
            'threshold': self.threshold,
            'summary': self.summary,
            'metadata': self.metadata}

    def get_failing_criteria(self) -> List[JudgmentCriterion]:
        """Get criteria that failed."""
        return [v.criterion for v in self.verdicts if v.score in {JudgmentScore.POOR, JudgmentScore.UNACCEPTABLE}]