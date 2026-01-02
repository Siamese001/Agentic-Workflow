from __future__ import annotations
from dataclasses import dataclass, field
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol
'Types and models for JudgeEvaluator.'
import logging
Logger: Any = logging.getLogger(__name__)

class JudgmentCriterion(Enum):
    """Criteria for judging output quality."""
    ACCURACY: Any = 'accuracy'
    COMPLETENESS: Any = 'completeness'
    RELEVANCE: Any = 'relevance'
    COHERENCE: Any = 'coherence'
    FACTUALITY: Any = 'factuality'
    SAFETY: Any = 'safety'
    HELPFULNESS: Any = 'helpfulness'

class JudgmentScore(Enum):
    """Judgment score levels."""
    EXCELLENT: Any = 'excellent'
    GOOD: Any = 'good'
    ACCEPTABLE: Any = 'acceptable'
    POOR: Any = 'poor'
    UNACCEPTABLE: Any = 'unacceptable'

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
        return {'criterion': self.criterion.value, 'score': self.score.value, 'score_value': self.score_value, 'reasoning': self.reasoning, 'evidence': self.evidence, 'suggestions': self.suggestions}

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
        return {'overall_score': self.overall_score, 'verdicts': [v.to_dict() for v in self.verdicts], 'passed': self.passed, 'threshold': self.threshold, 'summary': self.summary, 'metadata': self.metadata}

    def get_failing_criteria(self) -> List[JudgmentCriterion]:
        """Get criteria that failed."""
        return [v.criterion for v in self.verdicts if v.score in {JudgmentScore.POOR, JudgmentScore.UNACCEPTABLE}]
