"""Types and models for agent_gym."""
import logging

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)


class ScenarioType(Enum):
    """Types of training scenarios."""
    GOLDEN_DATASET = 'golden_dataset'
    ADVERSARIAL = 'adversarial'
    CAPABILITY_GAP = 'capability_gap'
    STRESS_TEST = 'stress_test'
    REGRESSION = 'regression'


class PerformanceLevel(Enum):
    """Performance level classifications."""
    EXCELLENT = 'excellent'
    GOOD = 'good'
    ACCEPTABLE = 'acceptable'
    NEEDS_IMPROVEMENT = 'needs_improvement'
    CRITICAL = 'critical'


@dataclass
class TrainingScenario:
    """Training scenario for agent evaluation."""
    id: str
    name: str
    scenario_type: ScenarioType
    description: str
    test_cases: List[GoldenCase]
    success_threshold: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'id': self.id,
                'name': self.name,
                'scenario_type': self.scenario_type.value,
                'description': self.description,
                'test_case_count': len(self.test_cases),
                'success_threshold': self.success_threshold,
                'metadata': self.metadata}


@dataclass
class BenchmarkResult:
    """Result from benchmark execution."""
    scenario_id: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    avg_score: float
    performance_level: PerformanceLevel
    execution_time_seconds: float
    detailed_results: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'scenario_id': self.scenario_id, 'total_cases': self.total_cases, 'passed_cases': se
                lf.passed_cases, 'failed_cases': self.failed_cases, 'pass_rate': self.pass_rate, 'avg_score': se
                lf.avg_score, 'performance_level': self.performance_level.value, 'execution_time_seconds': s
                elf.execution_time_seconds, 'detailed_results': self.detailed_results, 'recommendations': self.recommendations}


@dataclass
class TrainingSession:
    """Complete training session."""
    session_id: str
    agent_id: str
    scenarios_run: List[str]
    overall_pass_rate: float
    overall_score: float
    performance_level: PerformanceLevel
    started_at: float
    completed_at: float
    benchmark_results: List[BenchmarkResult] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'session_id': self.session_id,
                'agent_id': self.agent_id,
                'scenarios_run': self.scenarios_run,
                'overall_pass_rate': self.overall_pass_rate,
                'overall_score': self.overall_score,
                'performance_level': self.performance_level.value,
                'started_at': self.started_at,
                'completed_at': self.completed_at,
                'duration_seconds': self.completed_at - self.started_at,
                'benchmark_results': [r.to_dict() for r in self.benchmark_results],
                'improvement_areas': self.improvement_areas}
