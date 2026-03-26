# API Documentation: agent_gym_engine

**Target Audience**: developers, api_users

# agent_gym_engine API Documentation

**File**: `agent_gym_engine.py`
**Classes**: 1
**Functions**: 13

## Classes

- **AgentGym** (inherits from SovereignBaseAgent)

## Functions

- **create_agent_gym** -> AgentGym
- **_run_self_tests** -> dict
- **__init__**
- **register_scenario** -> None
- **_create_benchmark_result** -> BenchmarkResult
- **_log_benchmark_start** -> None
- **get_scenario** -> TrainingScenario | None
- **list_scenarios** -> list[TrainingScenario]
- **get_session_history** -> list[TrainingSession]
- **_load_default_scenarios** -> None
- **_classify_performance** -> PerformanceLevel
- **_generate_recommendations** -> list[str]
- **_identify_improvement_areas** -> list[str]


## Class: AgentGym

**Description**: Agent Gym for self-evolution and benchmarking.

    Features:
    - Offline simulation environment
    - Golden dataset benchmarking
    - Capability gap identification
    - Performance tracking
    - Improvement recommendations
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, golden_evaluator, JudgeEvaluator, enable_logging
**Description**: Initialize Agent Gym.

        Args:
            golden_evaluator: Golden state evaluator
            JudgeEvaluator: Judge evaluator
            enable_logging: Enable logging
        

#### register_scenario
**Parameters**: self, scenario
**Returns**: None
**Description**: Register a training scenario.

        Args:
            scenario: Training scenario
        

#### _create_benchmark_result
**Parameters**: self, scenario_id, test_cases, reports, start_time
**Returns**: BenchmarkResult
**Description**: Create benchmark result from reports.

#### _log_benchmark_start
**Parameters**: self, scenario_id, scenario
**Returns**: None
**Description**: Log benchmark start.

#### get_scenario
**Parameters**: self, scenario_id
**Returns**: TrainingScenario | None
**Description**: Get a training scenario.

        Args:
            scenario_id: Scenario ID

        Returns:
            TrainingScenario or None
        

#### list_scenarios
**Parameters**: self, ScenarioType
**Returns**: list[TrainingScenario]
**Description**: List all scenarios.

        Args:
            ScenarioType: Optional type filter

        Returns:
            List of scenarios
        

#### get_session_history
**Parameters**: self, agent_id
**Returns**: list[TrainingSession]
**Description**: Get training session history.

        Args:
            agent_id: Optional agent ID filter

        Returns:
            List of training sessions
        

#### _load_default_scenarios
**Parameters**: self
**Returns**: None
**Description**: Load default scenarios from golden datasets.

#### _classify_performance
**Parameters**: self, pass_rate, avg_score
**Returns**: PerformanceLevel
**Description**: Classify performance level.

        Args:
            pass_rate: Pass rate (0.0-1.0)
            avg_score: Average score (0.0-1.0)

        Returns:
            PerformanceLevel
        

#### _generate_recommendations
**Parameters**: self, reports, PerformanceLevel
**Returns**: list[str]
**Description**: Generate improvement recommendations.

        Args:
            reports: Evaluation reports
            PerformanceLevel: Performance level

        Returns:
            List of recommendations
        

#### _identify_improvement_areas
**Parameters**: self, benchmark_results
**Returns**: list[str]
**Description**: Identify improvement areas from benchmark results.

        Args:
            benchmark_results: List of benchmark results

        Returns:
            List of improvement areas
        



## Function: create_agent_gym

**Parameters**: golden_evaluator
**Returns**: AgentGym
**Description**: Factory function to create Agent Gym.

    Args:
        golden_evaluator: Optional golden state evaluator

    Returns:
        AgentGym instance
    



## Function: _run_self_tests

**Parameters**: self
**Returns**: dict
**Description**: Run internal self-tests.



## Function: __init__

**Parameters**: self, golden_evaluator, JudgeEvaluator, enable_logging
**Description**: Initialize Agent Gym.

        Args:
            golden_evaluator: Golden state evaluator
            JudgeEvaluator: Judge evaluator
            enable_logging: Enable logging
        



## Function: register_scenario

**Parameters**: self, scenario
**Returns**: None
**Description**: Register a training scenario.

        Args:
            scenario: Training scenario
        



## Function: _create_benchmark_result

**Parameters**: self, scenario_id, test_cases, reports, start_time
**Returns**: BenchmarkResult
**Description**: Create benchmark result from reports.



## Function: _log_benchmark_start

**Parameters**: self, scenario_id, scenario
**Returns**: None
**Description**: Log benchmark start.



## Function: get_scenario

**Parameters**: self, scenario_id
**Returns**: TrainingScenario | None
**Description**: Get a training scenario.

        Args:
            scenario_id: Scenario ID

        Returns:
            TrainingScenario or None
        



## Function: list_scenarios

**Parameters**: self, ScenarioType
**Returns**: list[TrainingScenario]
**Description**: List all scenarios.

        Args:
            ScenarioType: Optional type filter

        Returns:
            List of scenarios
        



## Function: get_session_history

**Parameters**: self, agent_id
**Returns**: list[TrainingSession]
**Description**: Get training session history.

        Args:
            agent_id: Optional agent ID filter

        Returns:
            List of training sessions
        



## Function: _load_default_scenarios

**Parameters**: self
**Returns**: None
**Description**: Load default scenarios from golden datasets.



## Function: _classify_performance

**Parameters**: self, pass_rate, avg_score
**Returns**: PerformanceLevel
**Description**: Classify performance level.

        Args:
            pass_rate: Pass rate (0.0-1.0)
            avg_score: Average score (0.0-1.0)

        Returns:
            PerformanceLevel
        



## Function: _generate_recommendations

**Parameters**: self, reports, PerformanceLevel
**Returns**: list[str]
**Description**: Generate improvement recommendations.

        Args:
            reports: Evaluation reports
            PerformanceLevel: Performance level

        Returns:
            List of recommendations
        



## Function: _identify_improvement_areas

**Parameters**: self, benchmark_results
**Returns**: list[str]
**Description**: Identify improvement areas from benchmark results.

        Args:
            benchmark_results: List of benchmark results

        Returns:
            List of improvement areas
        



## Usage Examples

### Class Usage

```python
# Using AgentGym
agentgym = AgentGym()
agentgym.register_scenario()
agentgym.get_scenario()
```

### Function Usage

```python
# Using create_agent_gym
result = create_agent_gym(golden_evaluator)
```

```python
# Using _run_self_tests
result = _run_self_tests()
```

```python
# Using __init__
result = __init__(golden_evaluator, JudgeEvaluator)
```



---
**Generated**: 2026-03-26T09:39:04.134199
**Type**: api_reference
**Quality**: comprehensive
