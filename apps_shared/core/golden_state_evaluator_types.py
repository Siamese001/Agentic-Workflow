"""Types and models for golden_state_evaluator."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

@dataclass
class GoldenCase:
    """Golden test case."""
    id: str
    name: str
    category: str
    mission: str
    scene: Dict[str, Any]
    expected_output: Dict[str, Any]
    expected_actions: List[Dict[str, Any]]
    quality_criteria: Dict[str, float]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GoldenCase':
        """Create from dictionary."""
        return cls(id=data['id'], name=data['name'], category=data['category'], mission=data['mission'], scene=data['scene'], expected_output=data['expected_output'], expected_actions=data['expected_actions'], quality_criteria=data['quality_criteria'])

@dataclass
class GoldenOutput:
    """Output from agent execution."""
    case_id: str
    actual_output: str
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvaluationReport:
    """Evaluation report for a golden case."""
    case_id: str
    case_name: str
    passed: bool
    judge_result: JudgeEvaluationResult
    action_match_score: float
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'case_id': self.case_id, 'case_name': self.case_name, 'passed': self.passed, 'judge_result': self.judge_result.to_dict(), 'action_match_score': self.action_match_score, 'errors': self.errors}
