# API Documentation: autonomous_workflow_engine

**Target Audience**: developers, api_users

# autonomous_workflow_engine API Documentation

**File**: `autonomous_workflow_engine.py`
**Classes**: 5
**Functions**: 3

## Classes

- **StopSignal** (inherits from Enum)
- **EnvironmentToolSet** (inherits from Protocol)
- **WorkflowStep**
- **WorkflowResult**
- **AutonomousWorkflowEngine**

## Functions

- **is_goal_achieved** -> bool
- **reset** -> None
- **__init__** -> None


## Class: StopSignal

**Description**: Reason the loop was halted.

**Inherits from**: Enum



## Class: EnvironmentToolSet

**Description**: Protocol for environment interaction — implement to plug in any domain.

**Inherits from**: Protocol

### Methods

#### is_goal_achieved
**Parameters**: self, observation
**Returns**: bool
**Description**: Return True when the environment signals the goal is complete.

#### reset
**Parameters**: self
**Returns**: None
**Description**: Reset environment state between runs (optional).



## Class: WorkflowStep

**Description**: Record of a single action-observation step.



## Class: WorkflowResult

**Description**: Full result of an autonomous workflow run.



## Class: AutonomousWorkflowEngine

**Description**: General-purpose autonomous action loop.

    Usage::

        engine = AutonomousWorkflowEngine(
            policy_fn=my_policy,
            env=my_env_toolset,
            max_iterations=10,
        )
        result = await engine.run(goal="Deploy service to staging")

    Args:
        policy_fn:      async (goal, steps_so_far, last_obs) -> (action, params)
                        Decides the next action given the current trajectory.
        env:            EnvironmentToolSet instance.
        max_iterations: Hard cap on action steps (default 20).
        max_consecutive_failures: Circuit-breaker threshold (default 5).
    

### Methods

#### __init__
**Parameters**: self, policy_fn, env, max_iterations, max_consecutive_failures
**Returns**: None



## Function: is_goal_achieved

**Parameters**: self, observation
**Returns**: bool
**Description**: Return True when the environment signals the goal is complete.



## Function: reset

**Parameters**: self
**Returns**: None
**Description**: Reset environment state between runs (optional).



## Function: __init__

**Parameters**: self, policy_fn, env, max_iterations, max_consecutive_failures
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using StopSignal
stopsignal = StopSignal()
```

```python
# Using EnvironmentToolSet
environmenttoolset = EnvironmentToolSet()
environmenttoolset.is_goal_achieved()
environmenttoolset.reset()
```

```python
# Using WorkflowStep
workflowstep = WorkflowStep()
```

### Function Usage

```python
# Using is_goal_achieved
result = is_goal_achieved(observation)
```

```python
# Using reset
result = reset()
```

```python
# Using __init__
result = __init__(policy_fn, env)
```



---
**Generated**: 2026-03-26T09:39:04.140340
**Type**: api_reference
**Quality**: comprehensive
