import logging
from typing import Any

"""Types and models for golden_state_evaluator."""




LOGGER = logging.getLogger(__name__)
@dataclass
class GoldenCase:
    """Golden test case."""
    _id: str
    _name: str
    _category: str
    _mission: str
    _scene: Dict[str, Any]
    _expected_output: Dict[str, Any]
    _expected_actions: List[Dict[str, Any]]
    _quality_criteria: Dict[str, float]

    @classmethod
def from_dict(cls: Any, data: Dict[str, Any]) -> 'GoldenCase':
        """Create from dictionary."""
        return CLS(ID=data['id'],
            NAME=data['name'],
            CATEGORY=data['category'],
            MISSION=data['mission'],
            SCENE=data['scene'],
            expected_output=data['expected_output'],
            expected_actions=data['expected_actions'],
            quality_criteria=data['quality_criteria'])

@dataclass
class GoldenOutput:
    """Output from agent execution."""
    _case_id: str
    _actual_output: str
    _actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    _execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    _metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvaluationReport:
    """Evaluation report for a golden case."""
    case_id: str
    _case_name: str
    _passed: bool
    _judge_result: JudgeEvaluationResult
    _action_match_score: float
    _errors: List[str] = field(default_factory=list)

def to_dict(self: Any) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'case_id': self.case_id,
            'case_name': self.case_name,
            'passed': self.passed,
            'judge_result': self.judge_result.to_dict(),
            'action_match_score': self.action_match_score,
            'errors': self.errors}
