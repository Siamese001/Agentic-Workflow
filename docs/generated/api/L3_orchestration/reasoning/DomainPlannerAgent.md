# API Documentation: DomainPlannerAgent

**Target Audience**: developers, api_users

# DomainPlannerAgent API Documentation

**File**: `DomainPlannerAgent.py`
**Classes**: 11
**Functions**: 24

## Classes

- **DomainPlannerOutput**
- **PlannerAssessment**
- **ScenarioSimulationResult**
- **StrategyPlan**
- **WorkflowContext**
- **DomainPlannerAgent** (inherits from L3OrchestrationBase)
- **RiskAssessorAgent** (inherits from SovereignBaseAgent)
- **FeasibilityAnalystAgent** (inherits from SovereignBaseAgent)
- **StrategyScenarioSimulatorAgent** (inherits from SovereignBaseAgent)
- **StrategyCoordinatorAgent** (inherits from SovereignBaseAgent)
- **SubatomicTestingMixin**

## Functions

- **_truncate** -> str
- **__init__**
- **model_dump**
- **__init__**
- **__init__**
- **__init__**
- **model_copy**
- **log_feedback**
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **log_feedback**
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **log_feedback**
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **log_feedback**
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **__init__**
- **_apply_feedback** -> list[str]
- **log_feedback**
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]


## Class: DomainPlannerOutput

### Methods

#### __init__
**Parameters**: self

#### model_dump
**Parameters**: self



## Class: PlannerAssessment

### Methods

#### __init__
**Parameters**: self



## Class: ScenarioSimulationResult

### Methods

#### __init__
**Parameters**: self



## Class: StrategyPlan

### Methods

#### __init__
**Parameters**: self

#### model_copy
**Parameters**: self, deep



## Class: WorkflowContext



## Class: DomainPlannerAgent

**Description**: Evaluates strategic alignment with the job domain.

    V10 Refactored: Now inherits from AtomicExecutionMixin for rollback capability
    and L3OrchestrationBase for proper layer positioning.

    MRO: DomainPlannerAgent -> AtomicExecutionMixin -> L3OrchestrationBase -> ...
    

**Inherits from**: L3OrchestrationBase

### Methods

#### log_feedback
**Parameters**: self
**Description**: Log feedback for domain planning operations.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        L3 Orchestration Agent - Domain Planner Healing.

        WIRED CAPABILITIES:
        - Validates domain alignment logic
        - Checks focus area processing
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by DomainPlannerAgent.

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
        



## Class: RiskAssessorAgent

**Description**: Assesses risk and potential failure modes in the strategy.

**Inherits from**: SovereignBaseAgent

### Methods

#### log_feedback
**Parameters**: self
**Description**: Log feedback for risk assessment operations.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 Orchestration Agent - Risk Assessor Healing.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by RiskAssessorAgent.

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
        



## Class: FeasibilityAnalystAgent

**Description**: Evaluates whether the plan is grounded in achievable achievements.

**Inherits from**: SovereignBaseAgent

### Methods

#### log_feedback
**Parameters**: self
**Description**: Log feedback for feasibility analysis operations.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 Orchestration Agent - Feasibility Analyst Healing.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by FeasibilityAnalystAgent.

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
        



## Class: StrategyScenarioSimulatorAgent

**Description**: Runs lightweight scenario stress tests on a strategy plan.

**Inherits from**: SovereignBaseAgent

### Methods

#### log_feedback
**Parameters**: self
**Description**: Log feedback for scenario simulation operations.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 Orchestration Agent - Strategy Scenario Simulator Healing.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by StrategyScenarioSimulatorAgent.

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
        



## Class: StrategyCoordinatorAgent

**Description**: Coordinates specialist planner inputs and produces an aggregated plan.

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, context, debug_mode

#### _apply_feedback
**Parameters**: self, plan, downstream_feedback
**Returns**: list[str]

#### log_feedback
**Parameters**: self
**Description**: Log feedback for strategy coordination operations.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 Orchestration Agent - Strategy Coordinator Healing.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by StrategyCoordinatorAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: "success", "partial_success", "failed", or "skipped"
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Class: SubatomicTestingMixin



## Function: _truncate

**Parameters**: text, limit
**Returns**: str


## Function: __init__

**Parameters**: self


## Function: model_dump

**Parameters**: self


## Function: __init__

**Parameters**: self


## Function: __init__

**Parameters**: self


## Function: __init__

**Parameters**: self


## Function: model_copy

**Parameters**: self, deep


## Function: log_feedback

**Parameters**: self
**Description**: Log feedback for domain planning operations.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        L3 Orchestration Agent - Domain Planner Healing.

        WIRED CAPABILITIES:
        - Validates domain alignment logic
        - Checks focus area processing
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by DomainPlannerAgent.

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
        



## Function: log_feedback

**Parameters**: self
**Description**: Log feedback for risk assessment operations.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 Orchestration Agent - Risk Assessor Healing.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by RiskAssessorAgent.

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
        



## Function: log_feedback

**Parameters**: self
**Description**: Log feedback for feasibility analysis operations.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 Orchestration Agent - Feasibility Analyst Healing.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by FeasibilityAnalystAgent.

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
        



## Function: log_feedback

**Parameters**: self
**Description**: Log feedback for scenario simulation operations.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 Orchestration Agent - Strategy Scenario Simulator Healing.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by StrategyScenarioSimulatorAgent.

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

**Parameters**: self, context, debug_mode


## Function: _apply_feedback

**Parameters**: self, plan, downstream_feedback
**Returns**: list[str]


## Function: log_feedback

**Parameters**: self
**Description**: Log feedback for strategy coordination operations.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 Orchestration Agent - Strategy Coordinator Healing.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by StrategyCoordinatorAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: "success", "partial_success", "failed", or "skipped"
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Usage Examples

### Class Usage

```python
# Using DomainPlannerOutput
domainplanneroutput = DomainPlannerOutput()
domainplanneroutput.model_dump()
```

```python
# Using PlannerAssessment
plannerassessment = PlannerAssessment()
```

```python
# Using ScenarioSimulationResult
scenariosimulationresult = ScenarioSimulationResult()
```

### Function Usage

```python
# Using _truncate
result = _truncate(text, limit)
```

```python
# Using __init__
result = __init__()
```

```python
# Using model_dump
result = model_dump()
```



---
**Generated**: 2026-03-26T09:39:04.277584
**Type**: api_reference
**Quality**: comprehensive
