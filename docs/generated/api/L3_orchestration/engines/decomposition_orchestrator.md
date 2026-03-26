# API Documentation: decomposition_orchestrator

**Target Audience**: developers, api_users

# decomposition_orchestrator API Documentation

**File**: `decomposition_orchestrator.py`
**Classes**: 7
**Functions**: 17

## Classes

- **AtomicTask**
- **MissionPlan**
- **DecompositionOrchestrator** (inherits from SovereignBaseAgent)
- **WorkerResult**
- **WorkerPool**
- **SynthesizerNode**
- **ReplanArtifact**

## Functions

- **create_decomposition_orchestrator** -> DecompositionOrchestrator
- **replan_on_failure** -> tuple[MissionPlan, ReplanArtifact]
- **__post_init__** -> None
- **_load_agent_registry** -> None
- **_build_capability_index** -> None
- **_match_agent_for_task** -> tuple[str, str]
- **decompose** -> MissionPlan
- **_extract_task_hints** -> list[str]
- **_estimate_complexity** -> str
- **to_json** -> str
- **execute** -> dict[str, Any]
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **__init__** -> None
- **register_worker** -> None
- **collect_results** -> dict[str, Any]
- **__init__** -> None


## Class: AtomicTask

**Description**: Represents a single atomic task in the mission plan.



## Class: MissionPlan

**Description**: Complete mission plan with DAG of atomic tasks.



## Class: DecompositionOrchestrator

**Description**: 
    Multi-Agent Task Decomposition Engine.

    KEYS: Phase 33 (Task Decomposition)
    ROLE: The Strategist. Decomposes high-level prompts into atomic agent tasks.

    Capabilities:
    - Semantic matching of tasks to available agents
    - DAG construction with dependency resolution
    - Parallel execution planning
    - L5 validation gate integration

    Usage:
        orchestrator = DecompositionOrchestrator()
        plan = orchestrator.decompose("Refactor all L2 agents to use new base class")
        orchestrator.execute(plan, dry_run=True)
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the decomposition orchestrator.

#### _load_agent_registry
**Parameters**: self
**Returns**: None
**Description**: Load agent capabilities from SSOT discovery JSON.

#### _build_capability_index
**Parameters**: self
**Returns**: None
**Description**: Build semantic capability index for agent matching.

#### _match_agent_for_task
**Parameters**: self, task_description
**Returns**: tuple[str, str]
**Description**: 
        Semantic matching of task description to available agent.

        Returns:
            (agent_name, agent_path) tuple
        

#### decompose
**Parameters**: self, prompt, max_tasks
**Returns**: MissionPlan
**Description**: 
        Decompose a high-level prompt into atomic agent tasks.

        Args:
            prompt: High-level task description
            max_tasks: Maximum number of atomic tasks to generate

        Returns:
            MissionPlan with DAG of atomic tasks
        

#### _extract_task_hints
**Parameters**: self, prompt
**Returns**: list[str]
**Description**: Extract atomic task hints from prompt.

#### _estimate_complexity
**Parameters**: self, task_description
**Returns**: str
**Description**: Estimate task complexity based on keywords.

#### to_json
**Parameters**: self, plan
**Returns**: str
**Description**: Serialize mission plan to JSON.

#### execute
**Parameters**: self, plan, dry_run
**Returns**: dict[str, Any]
**Description**: 
        Execute a mission plan.

        Args:
            plan: MissionPlan to execute
            dry_run: If True, log proposed actions without executing

        Returns:
            Execution results dictionary
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        L3 orchestration healing - coordinates healing across agents.

        Maintains healer chain by calling super().heal_repository().
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by DecompositionOrchestrator.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Class: WorkerResult

**Description**: Output from a single worker dispatch.



## Class: WorkerPool

**Description**: Register workers and dispatch AtomicTasks to them by name.

    Provides a clean Orchestrator → Workers → Synthesizer separation.

    Usage::

        pool = WorkerPool()
        pool.register_worker("CodeHealerAgent", healer_fn)
        pool.register_worker("NamingAgent", naming_fn)
        results = await pool.dispatch_plan(plan)
        summary = await synthesizer.synthesize(results)
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### register_worker
**Parameters**: self, name, fn
**Returns**: None
**Description**: Register an async worker function for a named agent.

#### collect_results
**Parameters**: self, results
**Returns**: dict[str, Any]
**Description**: Aggregate worker results into a summary dict.



## Class: SynthesizerNode

**Description**: Aggregates worker outputs back to the orchestrator.

    Args:
        synthesize_fn: Optional async fn(results: list[WorkerResult]) -> str.
                       If not provided, returns a JSON summary.
    

### Methods

#### __init__
**Parameters**: self, synthesize_fn
**Returns**: None



## Class: ReplanArtifact

**Description**: Tracks a single replan event for observability.



## Function: create_decomposition_orchestrator

**Returns**: DecompositionOrchestrator
**Description**: Factory function to create DecompositionOrchestrator.



## Function: replan_on_failure

**Parameters**: orchestrator, plan, failed_task, reason
**Returns**: tuple[MissionPlan, ReplanArtifact]
**Description**: Generate an updated plan after a task failure.

    Replaces the failed task with a re-decomposition of its description,
    appends the new sub-tasks after the failure point, and returns both
    the updated plan and a ReplanArtifact for observability.

    Args:
        orchestrator: The DecompositionOrchestrator instance to use for re-decomposition.
        plan:         The current MissionPlan with the failed task.
        failed_task:  The AtomicTask that failed.
        reason:       Human-readable failure reason.

    Returns:
        (updated_plan, replan_artifact) tuple.
    



## Function: __post_init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the decomposition orchestrator.



## Function: _load_agent_registry

**Parameters**: self
**Returns**: None
**Description**: Load agent capabilities from SSOT discovery JSON.



## Function: _build_capability_index

**Parameters**: self
**Returns**: None
**Description**: Build semantic capability index for agent matching.



## Function: _match_agent_for_task

**Parameters**: self, task_description
**Returns**: tuple[str, str]
**Description**: 
        Semantic matching of task description to available agent.

        Returns:
            (agent_name, agent_path) tuple
        



## Function: decompose

**Parameters**: self, prompt, max_tasks
**Returns**: MissionPlan
**Description**: 
        Decompose a high-level prompt into atomic agent tasks.

        Args:
            prompt: High-level task description
            max_tasks: Maximum number of atomic tasks to generate

        Returns:
            MissionPlan with DAG of atomic tasks
        



## Function: _extract_task_hints

**Parameters**: self, prompt
**Returns**: list[str]
**Description**: Extract atomic task hints from prompt.



## Function: _estimate_complexity

**Parameters**: self, task_description
**Returns**: str
**Description**: Estimate task complexity based on keywords.



## Function: to_json

**Parameters**: self, plan
**Returns**: str
**Description**: Serialize mission plan to JSON.



## Function: execute

**Parameters**: self, plan, dry_run
**Returns**: dict[str, Any]
**Description**: 
        Execute a mission plan.

        Args:
            plan: MissionPlan to execute
            dry_run: If True, log proposed actions without executing

        Returns:
            Execution results dictionary
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        L3 orchestration healing - coordinates healing across agents.

        Maintains healer chain by calling super().heal_repository().
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by DecompositionOrchestrator.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: register_worker

**Parameters**: self, name, fn
**Returns**: None
**Description**: Register an async worker function for a named agent.



## Function: collect_results

**Parameters**: self, results
**Returns**: dict[str, Any]
**Description**: Aggregate worker results into a summary dict.



## Function: __init__

**Parameters**: self, synthesize_fn
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using AtomicTask
atomictask = AtomicTask()
```

```python
# Using MissionPlan
missionplan = MissionPlan()
```

```python
# Using DecompositionOrchestrator
decompositionorchestrator = DecompositionOrchestrator()
decompositionorchestrator.decompose()
decompositionorchestrator.to_json()
```

### Function Usage

```python
# Using create_decomposition_orchestrator
result = create_decomposition_orchestrator()
```

```python
# Using replan_on_failure
result = replan_on_failure(orchestrator, plan)
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:04.160256
**Type**: api_reference
**Quality**: comprehensive
