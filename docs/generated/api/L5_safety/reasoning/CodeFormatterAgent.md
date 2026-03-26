# API Documentation: CodeFormatterAgent

**Target Audience**: developers, api_users

# CodeFormatterAgent API Documentation

**File**: `CodeFormatterAgent.py`
**Classes**: 1
**Functions**: 2

## Classes

- **CodeFormatterAgent** (inherits from CodeToolRunnerCapability, SovereignBaseAgent)

## Functions

- **heal**
- **heal_repository** -> dict


## Class: CodeFormatterAgent

**Description**: L5 Safety agent that enforces consistent formatting using Black + Ruff.

    This atomic agent applies Black formatting and Ruff lint auto-fixes to
    Python files, ensuring consistent code style across the project.

    Architecture (Composition over Inheritance):
        - SovereignBaseAgent: Provides sovereign infrastructure (config, healing, telemetry)
        - CodeToolRunnerCapability: Provides shared heal_repository, heal plumbing
        - This class: Provides execute() with Black + Ruff logic
    

**Inherits from**: CodeToolRunnerCapability, SovereignBaseAgent

### Methods

#### heal
**Parameters**: self, violation

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for CodeFormatterAgent.



## Function: heal

**Parameters**: self, violation


## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for CodeFormatterAgent.



## Usage Examples

### Class Usage

```python
# Using CodeFormatterAgent
codeformatteragent = CodeFormatterAgent()
codeformatteragent.heal()
codeformatteragent.heal_repository()
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
**Generated**: 2026-03-26T09:39:05.083879
**Type**: api_reference
**Quality**: comprehensive
