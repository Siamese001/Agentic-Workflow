# API Documentation: RedSentinelAgent

**Target Audience**: developers, api_users

# RedSentinelAgent API Documentation

**File**: `RedSentinelAgent.py`
**Classes**: 1
**Functions**: 5

## Classes

- **RedSentinelAgent** (inherits from SovereignBaseAgent)

## Functions

- **get_red_sentinel** -> RedSentinelAgent
- **__init__** -> None
- **_get_default_hostile_inputs** -> list[dict[str, Any]]
- **heal_repository** -> dict[str, int]
- **heal** -> dict


## Class: RedSentinelAgent

**Description**: L5 Safety agent that generates hostile inputs for security testing.

    This active defense system creates edge cases and malformed inputs to test
    function robustness including type errors, boundary conditions, buffer
    overflow attempts, malformed JSON, and special characters.

    Attributes:
        llm_client: LLM client for generating hostile inputs (deprecated).
        enabled: Whether fuzzing is enabled (via ENABLE_FUZZ env var).
        audit_path: Path to audit log file for fuzz results.

    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, llm_client
**Returns**: None
**Description**: Initialize the RedSentinelAgent.

        Args:
            llm_client: LLM client for generating hostile inputs (deprecated, uses MCP).
        

#### _get_default_hostile_inputs
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get default hostile inputs when LLM fails.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal red sentinel violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (vulnerability, injection, fuzzing)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Function: get_red_sentinel

**Returns**: RedSentinelAgent
**Description**: Get or create the global RedSentinelAgent instance.

    Returns:
        Global RedSentinelAgent singleton instance.
    



## Function: __init__

**Parameters**: self, llm_client
**Returns**: None
**Description**: Initialize the RedSentinelAgent.

        Args:
            llm_client: LLM client for generating hostile inputs (deprecated, uses MCP).
        



## Function: _get_default_hostile_inputs

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get default hostile inputs when LLM fails.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal red sentinel violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (vulnerability, injection, fuzzing)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Usage Examples

### Class Usage

```python
# Using RedSentinelAgent
redsentinelagent = RedSentinelAgent()
redsentinelagent.heal_repository()
redsentinelagent.heal()
```

### Function Usage

```python
# Using get_red_sentinel
result = get_red_sentinel()
```

```python
# Using __init__
result = __init__(llm_client)
```

```python
# Using _get_default_hostile_inputs
result = _get_default_hostile_inputs()
```



---
**Generated**: 2026-03-26T09:39:05.358786
**Type**: api_reference
**Quality**: comprehensive
