# API Documentation: BootstrapAgent

**Target Audience**: developers, api_users

# BootstrapAgent API Documentation

**File**: `BootstrapAgent.py`
**Classes**: 1
**Functions**: 5

## Classes

- **BootstrapAgent** (inherits from L0RoutingBase)

## Functions

- **__init__** -> None
- **_verify_redis_connection** -> bool
- **run_bootstrap** -> bool
- **heal_repository** -> dict
- **heal** -> dict[str, any]


## Class: BootstrapAgent

**Description**: 
    Autonomous boot integrity agent - Phase 21.1 Normalized.
    Inherits from L0RoutingBaseAgent which inherits from SovereignBaseAgent.
    

**Inherits from**: L0RoutingBase

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None

#### _verify_redis_connection
**Parameters**: self
**Returns**: bool

#### run_bootstrap
**Parameters**: self
**Returns**: bool

#### heal_repository
**Parameters**: self, target_path, dry_run
**Returns**: dict
**Description**: Heal bootstrap configuration and dependencies.

        Args:
            target_path: Optional path to heal (defaults to project root)

        Returns:
            dict: Healing results with canonical keys
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, any]
**Description**: 
        Heal violations detected by BootstrapAgent.

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

**Parameters**: self, project_root
**Returns**: None


## Function: _verify_redis_connection

**Parameters**: self
**Returns**: bool


## Function: run_bootstrap

**Parameters**: self
**Returns**: bool


## Function: heal_repository

**Parameters**: self, target_path, dry_run
**Returns**: dict
**Description**: Heal bootstrap configuration and dependencies.

        Args:
            target_path: Optional path to heal (defaults to project root)

        Returns:
            dict: Healing results with canonical keys
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, any]
**Description**: 
        Heal violations detected by BootstrapAgent.

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
        



## Usage Examples

### Class Usage

```python
# Using BootstrapAgent
bootstrapagent = BootstrapAgent()
bootstrapagent.run_bootstrap()
bootstrapagent.heal_repository()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using _verify_redis_connection
result = _verify_redis_connection()
```

```python
# Using run_bootstrap
result = run_bootstrap()
```



---
**Generated**: 2026-03-26T09:39:05.057657
**Type**: api_reference
**Quality**: comprehensive
