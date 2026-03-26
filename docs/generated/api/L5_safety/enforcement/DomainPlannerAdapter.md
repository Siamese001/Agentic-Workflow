# API Documentation: DomainPlannerAdapter

**Target Audience**: developers, api_users

# DomainPlannerAdapter API Documentation

**File**: `DomainPlannerAdapter.py`
**Classes**: 3
**Functions**: 7

## Classes

- **AdapterContext**
- **AdapterResult**
- **DomainPlannerAdapter**

## Functions

- **__init__**
- **_validate_input** -> bool
- **_validate_output** -> bool
- **_execute_legacy** -> Any
- **plan** -> AdapterResult
- **execute** -> AdapterResult
- **heal** -> AdapterResult


## Class: AdapterContext

**Description**: Context passed through adapter chain.



## Class: AdapterResult

**Description**: Standardized result from adapter operations.



## Class: DomainPlannerAdapter

**Description**: 
    V10-Compliant wrapper for DomainPlannerAgent.

    V15 P0.2: Refactored to eliminate AdapterBase/HealingAdapter dependency.
    Circuit breaker and validation logic inlined.
    

### Methods

#### __init__
**Parameters**: self, legacy_agent, project_root

#### _validate_input
**Parameters**: self, context
**Returns**: bool
**Description**: 
        V10 Input validation for DomainPlannerAgent.

        Validates:
        1. Required job_context keys exist
        2. Plan object has required attributes
        3. External touch requirements (API keys if needed)

        Args:
            context: Adapter context
            *args: Positional arguments (plan, job_context, workflow_id)
            **kwargs: Keyword arguments

        Returns:
            True if input is valid, False to reject
        

#### _validate_output
**Parameters**: self, result, context
**Returns**: bool
**Description**: 
        V10 Output validation for DomainPlannerAgent results.

        Validates:
        1. Result is a PlannerAssessment-like object
        2. Required fields are present (vote, confidence, rationale)

        Args:
            result: Result from legacy execution
            context: Adapter context

        Returns:
            True if output is valid, False to reject
        

#### _execute_legacy
**Parameters**: self, context
**Returns**: Any
**Description**: 
        Execute the DomainPlannerAgent's run_async method.

        The legacy agent uses async, so we run it in an event loop.

        Args:
            context: Adapter context
            *args: Positional arguments (plan, job_context, workflow_id)
            **kwargs: Keyword arguments

        Returns:
            PlannerAssessment from the legacy agent
        

#### plan
**Parameters**: self, plan, job_context, workflow_id, context
**Returns**: AdapterResult
**Description**: 
        Convenience method matching the expected domain planner interface.

        Args:
            plan: StrategyPlan object
            job_context: Job context dictionary
            workflow_id: Workflow identifier
            context: Optional adapter context

        Returns:
            AdapterResult with PlannerAssessment data
        

#### execute
**Parameters**: self, context
**Returns**: AdapterResult
**Description**: Execute with circuit breaker + input/output validation.

#### heal
**Parameters**: self, violation, context
**Returns**: AdapterResult
**Description**: Execute healing with V10 compliance.



## Function: __init__

**Parameters**: self, legacy_agent, project_root


## Function: _validate_input

**Parameters**: self, context
**Returns**: bool
**Description**: 
        V10 Input validation for DomainPlannerAgent.

        Validates:
        1. Required job_context keys exist
        2. Plan object has required attributes
        3. External touch requirements (API keys if needed)

        Args:
            context: Adapter context
            *args: Positional arguments (plan, job_context, workflow_id)
            **kwargs: Keyword arguments

        Returns:
            True if input is valid, False to reject
        



## Function: _validate_output

**Parameters**: self, result, context
**Returns**: bool
**Description**: 
        V10 Output validation for DomainPlannerAgent results.

        Validates:
        1. Result is a PlannerAssessment-like object
        2. Required fields are present (vote, confidence, rationale)

        Args:
            result: Result from legacy execution
            context: Adapter context

        Returns:
            True if output is valid, False to reject
        



## Function: _execute_legacy

**Parameters**: self, context
**Returns**: Any
**Description**: 
        Execute the DomainPlannerAgent's run_async method.

        The legacy agent uses async, so we run it in an event loop.

        Args:
            context: Adapter context
            *args: Positional arguments (plan, job_context, workflow_id)
            **kwargs: Keyword arguments

        Returns:
            PlannerAssessment from the legacy agent
        



## Function: plan

**Parameters**: self, plan, job_context, workflow_id, context
**Returns**: AdapterResult
**Description**: 
        Convenience method matching the expected domain planner interface.

        Args:
            plan: StrategyPlan object
            job_context: Job context dictionary
            workflow_id: Workflow identifier
            context: Optional adapter context

        Returns:
            AdapterResult with PlannerAssessment data
        



## Function: execute

**Parameters**: self, context
**Returns**: AdapterResult
**Description**: Execute with circuit breaker + input/output validation.



## Function: heal

**Parameters**: self, violation, context
**Returns**: AdapterResult
**Description**: Execute healing with V10 compliance.



## Usage Examples

### Class Usage

```python
# Using AdapterContext
adaptercontext = AdapterContext()
```

```python
# Using AdapterResult
adapterresult = AdapterResult()
```

```python
# Using DomainPlannerAdapter
domainplanneradapter = DomainPlannerAdapter()
domainplanneradapter.plan()
domainplanneradapter.execute()
```

### Function Usage

```python
# Using __init__
result = __init__(legacy_agent, project_root)
```

```python
# Using _validate_input
result = _validate_input(context)
```

```python
# Using _validate_output
result = _validate_output(result, context)
```



---
**Generated**: 2026-03-26T09:39:04.810496
**Type**: api_reference
**Quality**: comprehensive
