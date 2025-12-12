"""Agent Gym for Self-Evolution and Benchmarking.

Phase 4 - Pillar 5: Capability Maturity (Self-Evolving System)
Offline simulation environment for agent training and capability assessment.

Integrates with:
- Phase 2 Golden Datasets (Pillar 12) for benchmarking
- Phase 2 Observability (Pillar 10) for metrics
- Phase 3 Identity (Pillar 2) for agent tracking
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Awaitable

from apps_shared.core.golden_state_evaluator import (
    GoldenStateEvaluator,
    GoldenCase,
    GoldenOutput,
)
from observability.golden_state import JudgeEvaluator

logger = logging.getLogger(__name__)


class ScenarioType(Enum):
    """Types of training scenarios."""
    GOLDEN_DATASET = "golden_dataset"
    ADVERSARIAL = "adversarial"
    CAPABILITY_GAP = "capability_gap"
    STRESS_TEST = "stress_test"
    REGRESSION = "regression"


class PerformanceLevel(Enum):
    """Performance level classifications."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"
    CRITICAL = "critical"


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
        return {
            "id": self.id,
            "name": self.name,
            "scenario_type": self.scenario_type.value,
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
    performance_level: PerformanceLevel
    execution_time_seconds: float
    detailed_results: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "pass_rate": self.pass_rate,
            "avg_score": self.avg_score,
            "performance_level": self.performance_level.value,
            "execution_time_seconds": self.execution_time_seconds,
            "detailed_results": self.detailed_results,
            "recommendations": self.recommendations,
        }


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
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "scenarios_run": self.scenarios_run,
            "overall_pass_rate": self.overall_pass_rate,
            "overall_score": self.overall_score,
            "performance_level": self.performance_level.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_seconds": self.completed_at - self.started_at,
            "benchmark_results": [r.to_dict() for r in self.benchmark_results],
            "improvement_areas": self.improvement_areas,
        }


class AgentGym:
    """Agent Gym for self-evolution and benchmarking.
    
    Features:
    - Offline simulation environment
    - Golden dataset benchmarking
    - Capability gap identification
    - Performance tracking
    - Improvement recommendations
    """
    
    def __init__(
        self,
        golden_evaluator: Optional[GoldenStateEvaluator] = None,
        judge_evaluator: Optional[JudgeEvaluator] = None,
        enable_logging: bool = True,
    ):
        """Initialize Agent Gym.
        
        Args:
            golden_evaluator: Golden state evaluator
            judge_evaluator: Judge evaluator
            enable_logging: Enable logging
        """
        self.golden_evaluator = golden_evaluator or GoldenStateEvaluator()
        self.judge_evaluator = judge_evaluator
        self.enable_logging = enable_logging
        
        self._scenarios: Dict[str, TrainingScenario] = {}
        self._session_history: List[TrainingSession] = []
        
        # Load default scenarios from golden datasets
        self._load_default_scenarios()
        
        if self.enable_logging:
            logger.info(
                "agent_gym_initialized",
                extra={
                    "scenario_count": len(self._scenarios),
                    "golden_cases": len(self.golden_evaluator.golden_cases),
                }
            )
    
    def register_scenario(self, scenario: TrainingScenario) -> None:
        """Register a training scenario.
        
        Args:
            scenario: Training scenario
        """
        self._scenarios[scenario.id] = scenario
        
        if self.enable_logging:
            logger.info(
                "scenario_registered",
                extra={
                    "scenario_id": scenario.id,
                    "type": scenario.scenario_type.value,
                    "test_cases": len(scenario.test_cases),
                }
            )
    
    async def run_benchmark(
        self,
        scenario_id: str,
        agent_fn: Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]],
    ) -> BenchmarkResult:
        """Run benchmark for a scenario.
        
        Args:
            scenario_id: Scenario identifier
            agent_fn: Agent execution function
            
        Returns:
            BenchmarkResult
        """
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario not found: {scenario_id}")
        
        start_time = time.time()
        
        if self.enable_logging:
            logger.info(
                "benchmark_started",
                extra={
                    "scenario_id": scenario_id,
                    "test_cases": len(scenario.test_cases),
                }
            )
        
        # Execute test cases
        outputs = {}
        for case in scenario.test_cases:
            try:
                result = await agent_fn(case.mission, case.scene)
                
                outputs[case.id] = GoldenOutput(
                    case_id=case.id,
                    actual_output=result.get("output", ""),
                    actions_taken=result.get("actions", []),
                    execution_trace=result.get("trace", []),
                )
            except Exception as e:
                if self.enable_logging:
                    logger.error(
                        "test_case_failed",
                        extra={
                            "case_id": case.id,
                            "error": str(e),
                        }
                    )
                
                outputs[case.id] = GoldenOutput(
                    case_id=case.id,
                    actual_output="",
                    metadata={"error": str(e)},
                )
        
        # Evaluate results
        reports = await self.golden_evaluator.evaluate_all(outputs)
        
        # Calculate metrics
        total_cases = len(scenario.test_cases)
        passed_cases = sum(1 for r in reports.values() if r.passed)
        failed_cases = total_cases - passed_cases
        pass_rate = passed_cases / total_cases if total_cases > 0 else 0.0
        
        avg_score = sum(
            r.judge_result.overall_score for r in reports.values()
        ) / total_cases if total_cases > 0 else 0.0
        
        # Determine performance level
        performance_level = self._classify_performance(pass_rate, avg_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            reports,
            performance_level,
        )
        
        # Detailed results
        detailed_results = [r.to_dict() for r in reports.values()]
        
        execution_time = time.time() - start_time
        
        result = BenchmarkResult(
            scenario_id=scenario_id,
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            pass_rate=pass_rate,
            avg_score=avg_score,
            performance_level=performance_level,
            execution_time_seconds=execution_time,
            detailed_results=detailed_results,
            recommendations=recommendations,
        )
        
        if self.enable_logging:
            logger.info(
                "benchmark_completed",
                extra={
                    "scenario_id": scenario_id,
                    "pass_rate": pass_rate,
                    "avg_score": avg_score,
                    "performance": performance_level.value,
                }
            )
        
        return result
    
    async def run_training_session(
        self,
        agent_id: str,
        scenario_ids: List[str],
        agent_fn: Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]],
    ) -> TrainingSession:
        """Run complete training session.
        
        Args:
            agent_id: Agent identifier
            scenario_ids: List of scenario IDs to run
            agent_fn: Agent execution function
            
        Returns:
            TrainingSession
        """
        session_id = f"session_{agent_id}_{int(time.time())}"
        started_at = time.time()
        
        if self.enable_logging:
            logger.info(
                "training_session_started",
                extra={
                    "session_id": session_id,
                    "agent_id": agent_id,
                    "scenarios": len(scenario_ids),
                }
            )
        
        # Run all scenarios
        benchmark_results = []
        for scenario_id in scenario_ids:
            result = await self.run_benchmark(scenario_id, agent_fn)
            benchmark_results.append(result)
        
        # Calculate overall metrics
        total_pass_rate = sum(r.pass_rate for r in benchmark_results) / len(benchmark_results)
        total_avg_score = sum(r.avg_score for r in benchmark_results) / len(benchmark_results)
        overall_performance = self._classify_performance(total_pass_rate, total_avg_score)
        
        # Identify improvement areas
        improvement_areas = self._identify_improvement_areas(benchmark_results)
        
        completed_at = time.time()
        
        session = TrainingSession(
            session_id=session_id,
            agent_id=agent_id,
            scenarios_run=scenario_ids,
            overall_pass_rate=total_pass_rate,
            overall_score=total_avg_score,
            performance_level=overall_performance,
            started_at=started_at,
            completed_at=completed_at,
            benchmark_results=benchmark_results,
            improvement_areas=improvement_areas,
        )
        
        self._session_history.append(session)
        
        if self.enable_logging:
            logger.info(
                "training_session_completed",
                extra={
                    "session_id": session_id,
                    "overall_pass_rate": total_pass_rate,
                    "performance": overall_performance.value,
                    "improvement_areas": len(improvement_areas),
                }
            )
        
        return session
    
    def get_scenario(self, scenario_id: str) -> Optional[TrainingScenario]:
        """Get a training scenario.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            TrainingScenario or None
        """
        return self._scenarios.get(scenario_id)
    
    def list_scenarios(
        self,
        scenario_type: Optional[ScenarioType] = None,
    ) -> List[TrainingScenario]:
        """List all scenarios.
        
        Args:
            scenario_type: Optional type filter
            
        Returns:
            List of scenarios
        """
        scenarios = list(self._scenarios.values())
        
        if scenario_type:
            scenarios = [s for s in scenarios if s.scenario_type == scenario_type]
        
        return scenarios
    
    def get_session_history(
        self,
        agent_id: Optional[str] = None,
    ) -> List[TrainingSession]:
        """Get training session history.
        
        Args:
            agent_id: Optional agent ID filter
            
        Returns:
            List of training sessions
        """
        sessions = self._session_history
        
        if agent_id:
            sessions = [s for s in sessions if s.agent_id == agent_id]
        
        return sessions
    
    def _load_default_scenarios(self) -> None:
        """Load default scenarios from golden datasets."""
        # Create scenario from golden cases
        if self.golden_evaluator.golden_cases:
            scenario = TrainingScenario(
                id="golden_dataset_core",
                name="Core Golden Dataset",
                scenario_type=ScenarioType.GOLDEN_DATASET,
                description="Core test cases from golden dataset",
                test_cases=self.golden_evaluator.golden_cases,
                success_threshold=0.8,
            )
            self._scenarios[scenario.id] = scenario
    
    def _classify_performance(
        self,
        pass_rate: float,
        avg_score: float,
    ) -> PerformanceLevel:
        """Classify performance level.
        
        Args:
            pass_rate: Pass rate (0.0-1.0)
            avg_score: Average score (0.0-1.0)
            
        Returns:
            PerformanceLevel
        """
        combined_score = (pass_rate + avg_score) / 2
        
        if combined_score >= 0.9:
            return PerformanceLevel.EXCELLENT
        elif combined_score >= 0.75:
            return PerformanceLevel.GOOD
        elif combined_score >= 0.6:
            return PerformanceLevel.ACCEPTABLE
        elif combined_score >= 0.4:
            return PerformanceLevel.NEEDS_IMPROVEMENT
        else:
            return PerformanceLevel.CRITICAL
    
    def _generate_recommendations(
        self,
        reports: Dict[str, Any],
        performance_level: PerformanceLevel,
    ) -> List[str]:
        """Generate improvement recommendations.
        
        Args:
            reports: Evaluation reports
            performance_level: Performance level
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if performance_level in {PerformanceLevel.NEEDS_IMPROVEMENT, PerformanceLevel.CRITICAL}:
            # Analyze common failure patterns
            failing_criteria = {}
            for report in reports.values():
                if not report.passed:
                    for criterion in report.judge_result.get_failing_criteria():
                        failing_criteria[criterion] = failing_criteria.get(criterion, 0) + 1
            
            # Top 3 failing criteria
            sorted_criteria = sorted(failing_criteria.items(), key=lambda x: x[1], reverse=True)
            for criterion, count in sorted_criteria[:3]:
                recommendations.append(
                    f"Improve {criterion.value}: Failed in {count} cases"
                )
        
        if performance_level == PerformanceLevel.CRITICAL:
            recommendations.append("Consider retraining or architectural changes")
        
        return recommendations
    
    def _identify_improvement_areas(
        self,
        benchmark_results: List[BenchmarkResult],
    ) -> List[str]:
        """Identify improvement areas from benchmark results.
        
        Args:
            benchmark_results: List of benchmark results
            
        Returns:
            List of improvement areas
        """
        areas = []
        
        # Find scenarios with low performance
        for result in benchmark_results:
            if result.performance_level in {
                PerformanceLevel.NEEDS_IMPROVEMENT,
                PerformanceLevel.CRITICAL,
            }:
                areas.append(f"{result.scenario_id}: {result.performance_level.value}")
        
        return areas


def create_agent_gym(
    golden_evaluator: Optional[GoldenStateEvaluator] = None,
) -> AgentGym:
    """Factory function to create Agent Gym.
    
    Args:
        golden_evaluator: Optional golden state evaluator
        
    Returns:
        AgentGym instance
    """
    return AgentGym(golden_evaluator=golden_evaluator)
