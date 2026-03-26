# API Documentation: GenerativeGuardAgent

**Target Audience**: developers, api_users

# GenerativeGuardAgent API Documentation

**File**: `GenerativeGuardAgent.py`
**Classes**: 2
**Functions**: 10

## Classes

- **GenerativeGuardAgent** (inherits from SovereignBaseAgent, HealerMixin, CanonBaseAgentInterface, MCPHardenedMixin)
- **CanonBaseAgentInterface**

## Functions

- **__init__** -> None
- **get_capabilities** -> list[str]
- **validate_state** -> bool
- **_purge_single_file** -> Any
- **_process_found_violations** -> Any
- **_is_runaway_file** -> bool
- **_find_runaway_violations_in_dir** -> list[str]
- **heal_repository** -> dict[str, int]
- **heal** -> dict
- **get_validated_project_root** -> Path


## Class: GenerativeGuardAgent

**Description**: 
    KEYS: 45 (Dead Code/Runaway Generation)
    ROLE: The Watchdog. Identifies and deletes recursively-generated files.

    Detects files matching runaway generation patterns:
    - *_copy*.py
    - *_backup*.py
    - *_old*.py
    - *_temp*.py
    

**Inherits from**: SovereignBaseAgent, HealerMixin, CanonBaseAgentInterface, MCPHardenedMixin

### Methods

#### __init__
**Parameters**: self, ctx
**Returns**: None
**Description**: Initialize the instance.

#### get_capabilities
**Parameters**: self
**Returns**: list[str]
**Description**: Return agent capabilities.

#### validate_state
**Parameters**: self
**Returns**: bool
**Description**: Validate agent state.

#### _purge_single_file
**Parameters**: self, file_path
**Returns**: Any
**Description**: Helper to attempt purging a single file and report.

#### _process_found_violations
**Parameters**: self, violations
**Returns**: Any
**Description**: Helper to process and optionally purge detected runaway files.

#### _is_runaway_file
**Parameters**: self, normalized_file_path
**Returns**: bool
**Description**: Helper to check if a file path matches any runaway pattern.

#### _find_runaway_violations_in_dir
**Parameters**: self, root, files
**Returns**: list[str]
**Description**: Helper to find runaway violations within a specific directory.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L1 cognition agent - operational only.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal generative guard violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (runaway_generation)
                - path: Path to the runaway file
                - pattern: Pattern that matched

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Class: CanonBaseAgentInterface



## Function: __init__

**Parameters**: self, ctx
**Returns**: None
**Description**: Initialize the instance.



## Function: get_capabilities

**Parameters**: self
**Returns**: list[str]
**Description**: Return agent capabilities.



## Function: validate_state

**Parameters**: self
**Returns**: bool
**Description**: Validate agent state.



## Function: _purge_single_file

**Parameters**: self, file_path
**Returns**: Any
**Description**: Helper to attempt purging a single file and report.



## Function: _process_found_violations

**Parameters**: self, violations
**Returns**: Any
**Description**: Helper to process and optionally purge detected runaway files.



## Function: _is_runaway_file

**Parameters**: self, normalized_file_path
**Returns**: bool
**Description**: Helper to check if a file path matches any runaway pattern.



## Function: _find_runaway_violations_in_dir

**Parameters**: self, root, files
**Returns**: list[str]
**Description**: Helper to find runaway violations within a specific directory.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L1 cognition agent - operational only.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal generative guard violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (runaway_generation)
                - path: Path to the runaway file
                - pattern: Pattern that matched

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: get_validated_project_root

**Returns**: Path


## Usage Examples

### Class Usage

```python
# Using GenerativeGuardAgent
generativeguardagent = GenerativeGuardAgent()
generativeguardagent.get_capabilities()
generativeguardagent.validate_state()
```

```python
# Using CanonBaseAgentInterface
canonbaseagentinterface = CanonBaseAgentInterface()
```

### Function Usage

```python
# Using __init__
result = __init__(ctx)
```

```python
# Using get_capabilities
result = get_capabilities()
```

```python
# Using validate_state
result = validate_state()
```



---
**Generated**: 2026-03-26T09:39:05.216691
**Type**: api_reference
**Quality**: comprehensive
