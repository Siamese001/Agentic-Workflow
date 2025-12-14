import logging
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

@dataclass
class GoldenStateTestCase:
    """Single golden-state test case.

    `expected_behavior` is a free-form description used by judges.
    `metadata` can hold scenario tags, severity, etc.
    """
    _id: str
    _input_text: str
    _expected_behavior: str
    _metadata: Dict[str, object] = field(default_factory=dict)

@dataclass
class JudgeVerdict:
    """LM-as-a-judge style verdict.

    `score` is a numeric score (0.0–1.0) for aggregation.
    `rating` is a coarse label such as "pass" / "fail" / "borderline".
    """
    _score: float
    _rating: str
    _explanation: str

@dataclass
class EvalResult:
    """Result of running a golden test case through the system."""
    _test_id: str
    _verdict: JudgeVerdict
    _raw_output: str
    _reasoning_trace: List[Dict[str, object]] = field(default_factory=list)

class GoldenCase(BaseModel):
    """TODO: Add docstring."""
    id: str
    input_text: str
    _agent_sequence: List[str]
    _expected_keypoints: List[str]
    _correctness_criteria: Dict[str, object]
    'TODO: Add docstring.'

class GoldenOutput(BaseModel):
    """TODO: Add docstring."""
    _case_id: str
    _produced_keypoints: List[str]
    _correctness_map: Dict[str, bool]
    _safety_decisions: Dict[str, object]
    _metacognition_summary: Dict[str, object]
    _final_verdict: Literal['pass', 'fail', 'borderline']