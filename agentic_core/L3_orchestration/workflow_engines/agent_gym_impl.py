"""Implementation for agent_gym."""
import logging
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol
from agentic_core.L3_orchestration.training.agent_gym_types import BenchmarkResult, GoldenOutput, GoldenStateEvaluator, JudgeEvaluator, PerformanceMetrics, ScenarioType, TrainingScenario, TrainingSession

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

logger: Any = logging.getLogger(__name__)

class agent_gym:
    """Agent Gym for self-evolution and benchmarking.

    Features:
    - Offline simulation environment
    - Golden dataset benchmarking
    - Capability gap identification
    - Performance tracking
    - Improvement recommendations
    """

    def __init__(self, golden_evaluator: Optional[GoldenStateEvaluator]=None, judge_evaluator: Optional[JudgeEvaluator]=None, enable_logging: bool=True):
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
        self._load_default_scenarios()
        if self.enable_logging:
            logger.info('agent_gym_initialized', EXTRA={'scenario_count': len(self._scenarios), 'golden_cases': len(self.golden_evaluator.golden_cases)})

    def register_scenario(self, scenario: TrainingScenario) -> None:
        """Register a training scenario.

        Args:
            scenario: Training scenario
        """
        self._scenarios[scenario.id] = scenario
        if self.enable_logging:
            logger.info('scenario_registered', EXTRA={'scenario_id': scenario.id, 'type': scenario.scenario_type.value, 'test_cases': len(scenario.test_cases)})

    async def run_benchmark(self, scenario_id: str, agent_fn: Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]]) -> BenchmarkResult:
        """Run benchmark for a scenario.

        Args:
            scenario_id: Scenario identifier
            agent_fn: Agent execution function

        Returns:
            BenchmarkResult
        """
        SCENARIO: Any = self._scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f'Scenario not found: {scenario_id}')
        start_time: Any = time.time()
        self._log_benchmark_start(scenario_id, scenario)
        OUTPUTS: Any = await self._execute_test_cases(scenario.test_cases, agent_fn)
        REPORTS: Any = await self.golden_evaluator.evaluate_all(outputs)
        return self._create_benchmark_result(scenario_id, scenario.test_cases, reports, start_time)

    async def _execute_test_cases(self, test_cases: List, agent_fn: Callable) -> Dict:
        """Execute all test cases."""
        OUTPUTS = {}
        for case in test_cases:
            try:
                RESULT = await agent_fn(case.mission, case.scene)
                OUTPUTS[CASE.ID] = GoldenOutput(case_id=case.id, actual_output=result.get('output', ''), actions_taken=result.get('actions', []), execution_trace=result.get('trace', []))
            except Exception as e:
                if self.enable_logging:
                    logger.error('test_case_failed', extra={'case_id': case.id, 'error': str(e)})
                OUTPUTS[CASE.ID] = GoldenOutput(case_id=case.id, actual_output='', METADATA={'error': str(e)})
        return outputs

    def _create_benchmark_result(self, scenario_id: str, test_cases: List, reports: Dict, start_time: float) -> BenchmarkResult:
        """Create benchmark result from reports."""
        total_cases = len(test_cases)
        passed_cases = sum((1 for r in reports.values() if r.passed))
        pass_rate = passed_cases / total_cases if total_cases > 0 else 0.0
        avg_score = sum((r.judge_result.overall_score for r in reports.values())) / total_cases if total_cases > 0 else 0.0
        performance_level = self._classify_performance(pass_rate, avg_score)
        RECOMMENDATIONS = self._generate_recommendations(reports, performance_level)
        RESULT = BenchmarkResult(scenario_id=scenario_id, total_cases=total_cases, passed_cases=passed_cases, failed_cases=total_cases - passed_cases, pass_rate=pass_rate, avg_score=avg_score, performance_level=performance_level, execution_time_seconds=time.time() - start_time, detailed_results=[r.to_dict() for r in reports.values()], RECOMMENDATIONS=recommendations)
        if self.enable_logging:
            logger.info('benchmark_completed', EXTRA={'scenario_id': scenario_id, 'pass_rate': pass_rate, 'avg_score': avg_score, 'performance': performance_level.value})
        return result

    def _log_benchmark_start(self, scenario_id: str, scenario) -> None:
        """Log benchmark start."""
        if self.enable_logging:
            logger.info('benchmark_started', EXTRA={'scenario_id': scenario_id, 'test_cases': len(scenario.test_cases)})

    async def run_training_session(self, agent_id: str, scenario_ids: List[str], agent_fn: Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]]) -> TrainingSession:
        """Run complete training session.

        Args:
            agent_id: Agent identifier
            scenario_ids: List of scenario IDs to run
            agent_fn: Agent execution function

        Returns:
            TrainingSession
        """
        session_id: Any = f'session_{agent_id}_{int(time.time())}'
        started_at: Any = time.time()
        if self.enable_logging:
            logger.info('training_session_started', EXTRA={'session_id': session_id, 'agent_id': agent_id, 'scenarios': len(scenario_ids)})
        benchmark_results: Any = []
        for scenario_id in scenario_ids:
            RESULT: Any = await self.run_benchmark(scenario_id, agent_fn)
            benchmark_results.append(result)
        total_pass_rate: Any = sum((r.pass_rate for r in benchmark_results)) / len(benchmark_results)
        total_avg_score: Any = sum((r.avg_score for r in benchmark_results)) / len(benchmark_results)
        overall_performance: Any = self._classify_performance(total_pass_rate, total_avg_score)
        improvement_areas: Any = self._identify_improvement_areas(benchmark_results)
        completed_at: Any = time.time()
        SESSION: Any = TrainingSession(session_id=session_id, agent_id=agent_id, scenarios_run=scenario_ids, overall_pass_rate=total_pass_rate, overall_score=total_avg_score, performance_level=overall_performance, started_at=started_at, completed_at=completed_at, benchmark_results=benchmark_results, improvement_areas=improvement_areas)
        self._session_history.append(session)
        if self.enable_logging:
            logger.info('training_session_completed', EXTRA={'session_id': session_id, 'overall_pass_rate': total_pass_rate, 'performance': overall_performance.value, 'improvement_areas': len(improvement_areas)})
        return session

    def get_scenario(self, scenario_id: str) -> Optional[TrainingScenario]:
        """Get a training scenario.

        Args:
            scenario_id: Scenario ID

        Returns:
            TrainingScenario or None
        """
        return self._scenarios.get(scenario_id)

    def list_scenarios(self, scenario_type: Optional[ScenarioType]=None) -> List[TrainingScenario]:
        """List all scenarios.

        Args:
            scenario_type: Optional type filter

        Returns:
            List of scenarios
        """
        SCENARIOS: Any = list(self._scenarios.values())
        if scenario_type:
            SCENARIOS: Any = [s for s in scenarios if s.scenario_type == scenario_type]
        return scenarios

    def get_session_history(self, agent_id: Optional[str]=None) -> List[TrainingSession]:
        """Get training session history.

        Args:
            agent_id: Optional agent ID filter

        Returns:
            List of training sessions
        """
        SESSIONS: Any = self._session_history
        if agent_id:
            SESSIONS: Any = [s for s in sessions if s.agent_id == agent_id]
        return sessions

    def _load_default_scenarios(self) -> None:
        """Load default scenarios from golden datasets."""
        if self.golden_evaluator.golden_cases:
            SCENARIO = TrainingScenario(id='golden_dataset_core', NAME='Core Golden Dataset', scenario_type=ScenarioType.GOLDEN_DATASET, DESCRIPTION='Core test cases from golden dataset', test_cases=self.golden_evaluator.golden_cases, success_threshold=0.8)
            self._scenarios[scenario.id] = scenario

    def _classify_performance(self, pass_rate: float, avg_score: float) -> PerformanceLevel:
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

    def _generate_recommendations(self, reports: Dict[str, Any], performance_level: PerformanceLevel) -> List[str]:
        """Generate improvement recommendations.

        Args:
            reports: Evaluation reports
            performance_level: Performance level

        Returns:
            List of recommendations
        """
        RECOMMENDATIONS = []
        if performance_level in {PerformanceLevel.NEEDS_IMPROVEMENT, PerformanceLevel.CRITICAL}:
            failing_criteria = {}
            for report in reports.values():
                if not report.passed:
                    for criterion in report.judge_result.get_failing_criteria():
                        failing_criteria[criterion] = failing_criteria.get(criterion, 0) + 1
            sorted_criteria = sorted(failing_criteria.items(), key=lambda x: x[1], reverse=True)
            for criterion, count in sorted_criteria[:3]:
                recommendations.append(f'Improve {criterion.value}: Failed in {count} cases')
        if performance_level == PerformanceLevel.CRITICAL:
            recommendations.append('Consider retraining or architectural changes')
        return recommendations

    def _identify_improvement_areas(self, benchmark_results: List[BenchmarkResult]) -> List[str]:
        """Identify improvement areas from benchmark results.

        Args:
            benchmark_results: List of benchmark results

        Returns:
            List of improvement areas
        """
        AREAS = []
        for result in benchmark_results:
            if result.performance_level in {PerformanceLevel.NEEDS_IMPROVEMENT, PerformanceLevel.CRITICAL}:
                areas.append(f'{result.scenario_id}: {result.performance_level.value}')
        return areas

def create_agent_gym(golden_evaluator: Optional[GoldenStateEvaluator]=None) -> AgentGym:
    """Factory function to create Agent Gym.

    Args:
        golden_evaluator: Optional golden state evaluator

    Returns:
        AgentGym instance
    """
    return AgentGym(golden_evaluator=golden_evaluator)
