# models - Golden evaluation data models
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class GoldenStateTestCase:
    """Test case for golden state evaluation"""
    id: str
    input_text: str
    expected_behavior: str
    metadata: Dict[str, Any]

@dataclass
class JudgeVerdict:
    """Verdict from a judge evaluation"""
    score: float
    rating: str
    explanation: str

class EvaluationStatus(Enum):
    """Status of golden evaluation"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class OutputType(Enum):
    """Types of golden outputs"""
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    EXTRACTION = "extraction"
    SCORING = "scoring"

@dataclass
class GoldenOutput:
    """Golden output reference for evaluation"""
    case_id: str
    produced_keypoints: List[str] = None
    correctness_map: Dict[str, Any] = None
    safety_decisions: Dict[str, Any] = None
    metacognition_summary: Dict[str, Any] = None
    final_verdict: str = "borderline"
    output_type: OutputType = OutputType.CLASSIFICATION
    expected_result: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.produced_keypoints is None:
            self.produced_keypoints = []
        if self.correctness_map is None:
            self.correctness_map = {}
        if self.safety_decisions is None:
            self.safety_decisions = {}
        if self.metacognition_summary is None:
            self.metacognition_summary = {}
        if self.expected_result is None:
            self.expected_result = {}
        if self.metadata is None:
            self.metadata = {}
    
    def matches(self, actual_output: Dict[str, Any], tolerance: float = 0.1) -> bool:
        """Check if actual output matches expected result"""
        for key, expected_value in self.expected_result.items():
            if key not in actual_output:
                return False
            
            actual_value = actual_output[key]
            
            if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                if abs(actual_value - expected_value) > tolerance:
                    return False
            elif expected_value != actual_value:
                return False
        
        return True

@dataclass
class EvaluationMetrics:
    """Metrics from golden evaluation"""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    custom_metrics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.custom_metrics is None:
            self.custom_metrics = {}

@dataclass
class GoldenEvaluation:
    """Complete golden evaluation result"""
    evaluation_id: str
    status: EvaluationStatus
    total_cases: int
    passed_cases: int
    failed_cases: int
    metrics: EvaluationMetrics
    outputs: List[GoldenOutput]
    error_details: List[str] = None
    
    def __post_init__(self):
        if self.error_details is None:
            self.error_details = []
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate"""
        if self.total_cases == 0:
            return 0.0
        return self.passed_cases / self.total_cases
    
    @property
    def is_successful(self) -> bool:
        """Check if evaluation meets success criteria"""
        return self.pass_rate >= 0.8 and self.status == EvaluationStatus.COMPLETED

@dataclass
class GoldenTestCase:
    """Individual golden test case"""
    case_id: str
    input_data: Dict[str, Any]
    golden_output: GoldenOutput
    description: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class GoldenModel:
    """Mock model for golden evaluation"""
    
    def __init__(self, model_name: str = "mock_model"):
        self.model_name = model_name
    
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock prediction function"""
        # Simple mock logic based on input
        if "text" in input_data:
            text = input_data["text"].lower()
            if "hello" in text or "good" in text:
                return {"classification": "positive", "confidence": 0.9}
            elif "terrible" in text or "bad" in text:
                return {"classification": "negative", "confidence": 0.85}
            else:
                return {"classification": "neutral", "confidence": 0.7}
        
        return {"result": "mock_output", "confidence": 0.8}

# Global model instance
_global_model: Optional[GoldenModel] = None

def get_golden_model() -> GoldenModel:
    """Get the global golden model"""
    global _global_model
    if _global_model is None:
        _global_model = GoldenModel()
    return _global_model

def reset_golden_model() -> None:
    """Reset the global golden model (for testing)"""
    global _global_model
    _global_model = None
