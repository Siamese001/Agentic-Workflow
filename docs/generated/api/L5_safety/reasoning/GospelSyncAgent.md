# API Documentation: GospelSyncAgent

**Target Audience**: developers, api_users

# GospelSyncAgent API Documentation

**File**: `GospelSyncAgent.py`
**Classes**: 1
**Functions**: 7

## Classes

- **GospelSyncAgent** (inherits from L0RoutingBase)

## Functions

- **heal_repository** -> dict[str, Any]
- **__init__** -> None
- **perform_sync_audit** -> dict[str, Any]
- **_get_canonical_files** -> set[str]
- **_get_actual_files** -> set[str]
- **report_drift** -> None
- **heal** -> dict[str, Any]


## Class: GospelSyncAgent

**Description**: 
    THE SSOT GUARDIAN
    Ensures the 'World as it Is' (Filesystem) matches the 'World as it Should Be' (Blueprint).
    Detects heretical files and missing canonical files to protect Toxic Hubs.

    Inherits from L0RoutingBaseAgent: HealerMixin, MCPHardenedMixin, L0DelegationTestingMixin
    

**Inherits from**: L0RoutingBase

### Methods

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        

#### __init__
**Parameters**: self, root_dir
**Returns**: None
**Description**: 
        Initialize the Sync Agent with root directory context.
        

#### perform_sync_audit
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        VERBOSE HUNK: Scans the filesystem and compares against the STRUCTURE_BLUEPRINT.
        Identifies drift violations in real-time.
        

#### _get_canonical_files
**Parameters**: self
**Returns**: set[str]
**Description**: 
        SUB-LINE PRECISION: Recursively extracts all expected file paths from the Gospel.
        

#### _get_actual_files
**Parameters**: self
**Returns**: set[str]
**Description**: 
        Scans the physical agentic_core directory for .py files, ignoring __init__.
        

#### report_drift
**Parameters**: self
**Returns**: None
**Description**: 
        Generates a Sovereign Sync Report for L6 observability consumption.
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by GospelSyncAgent.

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
        



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        



## Function: __init__

**Parameters**: self, root_dir
**Returns**: None
**Description**: 
        Initialize the Sync Agent with root directory context.
        



## Function: perform_sync_audit

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        VERBOSE HUNK: Scans the filesystem and compares against the STRUCTURE_BLUEPRINT.
        Identifies drift violations in real-time.
        



## Function: _get_canonical_files

**Parameters**: self
**Returns**: set[str]
**Description**: 
        SUB-LINE PRECISION: Recursively extracts all expected file paths from the Gospel.
        



## Function: _get_actual_files

**Parameters**: self
**Returns**: set[str]
**Description**: 
        Scans the physical agentic_core directory for .py files, ignoring __init__.
        



## Function: report_drift

**Parameters**: self
**Returns**: None
**Description**: 
        Generates a Sovereign Sync Report for L6 observability consumption.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by GospelSyncAgent.

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
# Using GospelSyncAgent
gospelsyncagent = GospelSyncAgent()
gospelsyncagent.heal_repository()
gospelsyncagent.perform_sync_audit()
```

### Function Usage

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```

```python
# Using __init__
result = __init__(root_dir)
```

```python
# Using perform_sync_audit
result = perform_sync_audit()
```



---
**Generated**: 2026-03-26T09:39:05.222701
**Type**: api_reference
**Quality**: comprehensive
