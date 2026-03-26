# API Documentation: UnusedCleanupAgent

**Target Audience**: developers, api_users

# UnusedCleanupAgent API Documentation

**File**: `UnusedCleanupAgent.py`
**Classes**: 1
**Functions**: 2

## Classes

- **UnusedCleanupAgent** (inherits from CodeToolRunnerCapability, SovereignBaseAgent)

## Functions

- **heal**
- **heal_repository** -> dict


## Class: UnusedCleanupAgent

**Description**: L5 Safety agent that removes unused imports and variables using autoflake.

    This atomic agent uses autoflake to clean up unused imports and variables
    from Python files.

    Architecture (Composition over Inheritance):
        - SovereignBaseAgent: Provides sovereign infrastructure (config, healing, telemetry)
        - CodeToolRunnerCapability: Provides shared heal_repository, heal plumbing
        - This class: Provides execute() with autoflake logic
    

**Inherits from**: CodeToolRunnerCapability, SovereignBaseAgent

### Methods

#### heal
**Parameters**: self, violation

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for UnusedCleanupAgent.



## Function: heal

**Parameters**: self, violation


## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for UnusedCleanupAgent.



## Usage Examples

### Class Usage

```python
# Using UnusedCleanupAgent
unusedcleanupagent = UnusedCleanupAgent()
unusedcleanupagent.heal()
unusedcleanupagent.heal_repository()
```

### Function Usage

```python
# Using heal
result = heal(violation)
```

```python
# Using heal_repository
result = heal_repository()
```



---
**Generated**: 2026-03-26T09:39:05.449300
**Type**: api_reference
**Quality**: comprehensive
