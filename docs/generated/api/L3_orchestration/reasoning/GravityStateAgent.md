# API Documentation: GravityStateAgent

**Target Audience**: developers, api_users

# GravityStateAgent API Documentation

**File**: `GravityStateAgent.py`
**Classes**: 2
**Functions**: 13

## Classes

- **HealingRecord**
- **GravityStateAgent** (inherits from SovereignBaseAgent)

## Functions

- **heal_repository** -> dict[str, Any]
- **heal** -> dict[str, Any]
- **__init__** -> None
- **_load_state** -> dict[str, Any]
- **_save_state** -> None
- **_normalize_and_hash** -> str
- **record_healing** -> None
- **is_healed** -> bool
- **get_file_healings** -> list[HealingRecord]
- **get_healing_summary** -> dict[str, Any]
- **create_checkpoint** -> str
- **rollback_to_checkpoint** -> bool
- **clear_state** -> None


## Class: HealingRecord

**Description**: Record of a single healing operation.



## Class: GravityStateAgent

**Description**: 
    [L4 STATE] Tracks gravity healing operations and prevents re-flagging.

    Maintains persistent state of healed files to ensure:
    - Converted dynamic imports are not re-flagged as violations
    - Healing history is preserved for audit and rollback
    - Multiple healing sessions can be coordinated
    

**Inherits from**: SovereignBaseAgent

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
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        IHealerProtocol compliance method for gravity state violations.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with healing result following HEAL_RESULT_SCHEMA
        

#### __init__
**Parameters**: self, project_root
**Returns**: None
**Description**: Initialize the instance.

#### _load_state
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Load healing state from disk.

#### _save_state
**Parameters**: self
**Returns**: None
**Description**: Persist healing state to disk.

#### _normalize_and_hash
**Parameters**: self, import_line
**Returns**: str
**Description**: 
        Normalizes an import statement by removing whitespace and comments
        to create a stable hash for comparison.
        

#### record_healing
**Parameters**: self, record
**Returns**: None
**Description**: 
        Record a successful healing operation.

        Args:
            record: HealingRecord with details of the healing
        

#### is_healed
**Parameters**: self, file_path, import_line
**Returns**: bool
**Description**: 
        Check if a specific import has already been healed.

        Args:
            file_path: Path to the file
            import_line: The import statement to check

        Returns:
            True if this import has been healed, False otherwise
        

#### get_file_healings
**Parameters**: self, file_path
**Returns**: list[HealingRecord]
**Description**: 
        Get all healing records for a specific file.

        Args:
            file_path: Path to the file

        Returns:
            List of HealingRecord objects for this file
        

#### get_healing_summary
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Get summary of all healing operations.

        Returns:
            Dict with healing statistics and summary
        

#### create_checkpoint
**Parameters**: self, name
**Returns**: str
**Description**: 
        Create a checkpoint of current healing state for rollback.

        Args:
            name: Name for this checkpoint

        Returns:
            Path to the checkpoint file
        

#### rollback_to_checkpoint
**Parameters**: self, checkpoint_file
**Returns**: bool
**Description**: 
        Rollback state to a previous checkpoint.

        Args:
            checkpoint_file: Path to the checkpoint file

        Returns:
            True if rollback successful, False otherwise
        

#### clear_state
**Parameters**: self
**Returns**: None
**Description**: Clear all healing state (use with caution).



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
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        IHealerProtocol compliance method for gravity state violations.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with healing result following HEAL_RESULT_SCHEMA
        



## Function: __init__

**Parameters**: self, project_root
**Returns**: None
**Description**: Initialize the instance.



## Function: _load_state

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Load healing state from disk.



## Function: _save_state

**Parameters**: self
**Returns**: None
**Description**: Persist healing state to disk.



## Function: _normalize_and_hash

**Parameters**: self, import_line
**Returns**: str
**Description**: 
        Normalizes an import statement by removing whitespace and comments
        to create a stable hash for comparison.
        



## Function: record_healing

**Parameters**: self, record
**Returns**: None
**Description**: 
        Record a successful healing operation.

        Args:
            record: HealingRecord with details of the healing
        



## Function: is_healed

**Parameters**: self, file_path, import_line
**Returns**: bool
**Description**: 
        Check if a specific import has already been healed.

        Args:
            file_path: Path to the file
            import_line: The import statement to check

        Returns:
            True if this import has been healed, False otherwise
        



## Function: get_file_healings

**Parameters**: self, file_path
**Returns**: list[HealingRecord]
**Description**: 
        Get all healing records for a specific file.

        Args:
            file_path: Path to the file

        Returns:
            List of HealingRecord objects for this file
        



## Function: get_healing_summary

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Get summary of all healing operations.

        Returns:
            Dict with healing statistics and summary
        



## Function: create_checkpoint

**Parameters**: self, name
**Returns**: str
**Description**: 
        Create a checkpoint of current healing state for rollback.

        Args:
            name: Name for this checkpoint

        Returns:
            Path to the checkpoint file
        



## Function: rollback_to_checkpoint

**Parameters**: self, checkpoint_file
**Returns**: bool
**Description**: 
        Rollback state to a previous checkpoint.

        Args:
            checkpoint_file: Path to the checkpoint file

        Returns:
            True if rollback successful, False otherwise
        



## Function: clear_state

**Parameters**: self
**Returns**: None
**Description**: Clear all healing state (use with caution).



## Usage Examples

### Class Usage

```python
# Using HealingRecord
healingrecord = HealingRecord()
```

```python
# Using GravityStateAgent
gravitystateagent = GravityStateAgent()
gravitystateagent.heal_repository()
gravitystateagent.heal()
```

### Function Usage

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```

```python
# Using heal
result = heal(violation)
```

```python
# Using __init__
result = __init__(project_root)
```



---
**Generated**: 2026-03-26T09:39:04.283235
**Type**: api_reference
**Quality**: comprehensive
