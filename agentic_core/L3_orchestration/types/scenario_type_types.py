from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Types and models for agent_gym."""
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

Logger: Any = logging.getLogger(__name__)


class ScenarioType(Enum):
    """Types of training scenarios."""

    GOLDEN_DATASET: Any = "golden_dataset"
    ADVERSARIAL: Any = "adversarial"
    CAPABILITY_GAP: Any = "CapabilityGap"
    STRESS_TEST: Any = "stress_test"
    REGRESSION: Any = "regression"


class PerformanceLevel(Enum):
    """Performance level classifications."""

    EXCELLENT: Any = "excellent"
    GOOD: Any = "good"
    ACCEPTABLE: Any = "acceptable"
    NEEDS_IMPROVEMENT: Any = "needs_improvement"
    CRITICAL: Any = "critical"


@dataclass
class TrainingScenario:
    """Training scenario for agent evaluation."""

    id: str
    name: str
    ScenarioType: ScenarioType
    description: str
    test_cases: list[Any]
    success_threshold: float = 0.8
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "ScenarioType": self.ScenarioType.value,
            "description": self.description,
            "test_case_count": len(self.test_cases),
            "success_threshold": self.success_threshold,
            "metadata": self.metadata,
        }


@dataclass
class BenchmarkResult:
    """Result from benchmark execution."""

    scenario_id: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    avg_score: float
    PerformanceLevel: PerformanceLevel
    execution_time_seconds: float
    detailed_results: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "pass_rate": self.pass_rate,
            "avg_score": self.avg_score,
            "PerformanceLevel": self.PerformanceLevel.value,
            "execution_time_seconds": self.execution_time_seconds,
            "detailed_results": self.detailed_results,
            "recommendations": self.recommendations,
        }


@dataclass
class TrainingSession:
    """Complete training session."""

    session_id: str
    agent_id: str
    scenarios_run: list[str]
    overall_pass_rate: float
    overall_score: float
    PerformanceLevel: PerformanceLevel
    started_at: float
    completed_at: float
    benchmark_results: list[Any] = field(default_factory=list)
    improvement_areas: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "scenarios_run": self.scenarios_run,
            "overall_pass_rate": self.overall_pass_rate,
            "overall_score": self.overall_score,
            "PerformanceLevel": self.PerformanceLevel.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_seconds": self.completed_at - self.started_at,
            "benchmark_results": [r.to_dict() for r in self.benchmark_results],
            "improvement_areas": self.improvement_areas,
        }
