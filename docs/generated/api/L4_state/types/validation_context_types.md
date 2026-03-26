# API Documentation: validation_context_types

**Target Audience**: developers, api_users

# validation_context_types API Documentation

**File**: `validation_context_types.py`
**Classes**: 3
**Functions**: 24

## Classes

- **IValidationContextProtocol** (inherits from Protocol)
- **IValidationContextManager** (inherits from Protocol)
- **Historian**

## Functions

- **_get_write_gateway**
- **get_historian** -> Historian
- **initialize_historian**
- **should_skip_file** -> bool
- **record_validation_result**
- **update_file_hash**
- **mark_flapping**
- **get_last_file_hashes** -> dict[str, str]
- **get_flapping_files** -> dict[str, int]
- **start_new_cycle** -> IValidationContextProtocol
- **complete_cycle**
- **load_memory** -> bool
- **__init__**
- **_load_memory**
- **_save_memory**
- **calculate_file_hash** -> str
- **should_skip_file** -> bool
- **_is_flapping** -> bool
- **record_file_result**
- **get_unchanged_files** -> tuple[set[Path], set[Path]]
- **start_cycle** -> IValidationContextProtocol
- **complete_cycle**
- **get_file_statistics** -> dict
- **get_cycle_summary** -> dict


## Class: IValidationContextProtocol

**Description**: Brief description of functionality and purpose.

**Inherits from**: Protocol

### Methods

#### update_file_hash
**Parameters**: self, file_path, file_hash
**Description**: Ellipsis

#### mark_flapping
**Parameters**: self, file_path
**Description**: Ellipsis



## Class: IValidationContextManager

**Description**: Brief description of functionality and purpose.

**Inherits from**: Protocol

### Methods

#### get_last_file_hashes
**Parameters**: self
**Returns**: dict[str, str]
**Description**: Ellipsis

#### get_flapping_files
**Parameters**: self
**Returns**: dict[str, int]
**Description**: Ellipsis

#### start_new_cycle
**Parameters**: self, cycle_id
**Returns**: IValidationContextProtocol
**Description**: Ellipsis

#### complete_cycle
**Parameters**: self, status
**Description**: Ellipsis

#### load_memory
**Parameters**: self
**Returns**: bool
**Description**: Ellipsis



## Class: Historian

**Description**: 
    Tracks validation history and optimizes file scanning.

    Features:
    - MD5 hash-based change detection
    - Skip logic for unchanged files
    - Flapping detection for unstable files
    - Cycle history tracking
    

### Methods

#### __init__
**Parameters**: self, context_manager, memory_dir
**Description**: 
        Initialize the Historian.

        Args:
            context_manager: An instance conforming to IValidationContextManager protocol.
            memory_dir: Directory to store historical data
        

#### _load_memory
**Parameters**: self

#### _save_memory
**Parameters**: self
**Description**: Save historical data to memory files.

#### calculate_file_hash
**Parameters**: self, file_path
**Returns**: str
**Description**: 
        Calculate MD5 hash of file contents.

        Args:
            file_path: Path to the file

        Returns:
            MD5 hash as hex string
        

#### should_skip_file
**Parameters**: self, file_path
**Returns**: bool
**Description**: 
        Check if a file should be skipped based on hash comparison.

        Args:
            file_path: Path to the file

        Returns:
            True if file should be skipped (unchanged)
        

#### _is_flapping
**Parameters**: self, file_path
**Returns**: bool
**Description**: 
        Check if a file is flapping (toggling status frequently).

        Args:
            file_path: Relative file path

        Returns:
            True if file is flapping
        

#### record_file_result
**Parameters**: self, file_path, status, violations
**Description**: 
        Record validation result for a file.

        Args:
            file_path: Path to the file
            status: Validation status (PASS/FAIL)
            violations: List of violations found
        

#### get_unchanged_files
**Parameters**: self, file_list
**Returns**: tuple[set[Path], set[Path]]
**Description**: 
        Separate files into unchanged and modified sets.

        Args:
            file_list: List of files to check

        Returns:
            Tuple of (unchanged_files, modified_files)
        

#### start_cycle
**Parameters**: self, cycle_id
**Returns**: IValidationContextProtocol
**Description**: 
        Start a new validation cycle.

        Args:
            cycle_id: Optional cycle ID

        Returns:
            New ValidationContext
        

#### complete_cycle
**Parameters**: self, status
**Description**: 
        Complete the current cycle and save history.

        Args:
            status: Cycle completion status
        

#### get_file_statistics
**Parameters**: self, file_path
**Returns**: dict
**Description**: 
        Get validation statistics for a file.

        Args:
            file_path: Path to the file

        Returns:
            Statistics dictionary
        

#### get_cycle_summary
**Parameters**: self
**Returns**: dict
**Description**: 
        Get summary of the current cycle.

        Returns:
            Cycle summary dictionary
        



## Function: _get_write_gateway

**Description**: Get UWG instance - L4 may only use, not import tools.



## Function: get_historian

**Returns**: Historian
**Description**: Get the global Historian instance. Must be initialized first.



## Function: initialize_historian

**Parameters**: context_manager, memory_dir
**Description**: 
    Initialize the Historian system.

    Args:
        context_manager: An instance conforming to IValidationContextManager protocol.
        memory_dir: Directory for storing historical data
    



## Function: should_skip_file

**Parameters**: file_path
**Returns**: bool
**Description**: Check if a file should be skipped.



## Function: record_validation_result

**Parameters**: file_path, status, violations
**Description**: Record validation result for a file.



## Function: update_file_hash

**Parameters**: self, file_path, file_hash
**Description**: Ellipsis



## Function: mark_flapping

**Parameters**: self, file_path
**Description**: Ellipsis



## Function: get_last_file_hashes

**Parameters**: self
**Returns**: dict[str, str]
**Description**: Ellipsis



## Function: get_flapping_files

**Parameters**: self
**Returns**: dict[str, int]
**Description**: Ellipsis



## Function: start_new_cycle

**Parameters**: self, cycle_id
**Returns**: IValidationContextProtocol
**Description**: Ellipsis



## Function: complete_cycle

**Parameters**: self, status
**Description**: Ellipsis



## Function: load_memory

**Parameters**: self
**Returns**: bool
**Description**: Ellipsis



## Function: __init__

**Parameters**: self, context_manager, memory_dir
**Description**: 
        Initialize the Historian.

        Args:
            context_manager: An instance conforming to IValidationContextManager protocol.
            memory_dir: Directory to store historical data
        



## Function: _load_memory

**Parameters**: self


## Function: _save_memory

**Parameters**: self
**Description**: Save historical data to memory files.



## Function: calculate_file_hash

**Parameters**: self, file_path
**Returns**: str
**Description**: 
        Calculate MD5 hash of file contents.

        Args:
            file_path: Path to the file

        Returns:
            MD5 hash as hex string
        



## Function: should_skip_file

**Parameters**: self, file_path
**Returns**: bool
**Description**: 
        Check if a file should be skipped based on hash comparison.

        Args:
            file_path: Path to the file

        Returns:
            True if file should be skipped (unchanged)
        



## Function: _is_flapping

**Parameters**: self, file_path
**Returns**: bool
**Description**: 
        Check if a file is flapping (toggling status frequently).

        Args:
            file_path: Relative file path

        Returns:
            True if file is flapping
        



## Function: record_file_result

**Parameters**: self, file_path, status, violations
**Description**: 
        Record validation result for a file.

        Args:
            file_path: Path to the file
            status: Validation status (PASS/FAIL)
            violations: List of violations found
        



## Function: get_unchanged_files

**Parameters**: self, file_list
**Returns**: tuple[set[Path], set[Path]]
**Description**: 
        Separate files into unchanged and modified sets.

        Args:
            file_list: List of files to check

        Returns:
            Tuple of (unchanged_files, modified_files)
        



## Function: start_cycle

**Parameters**: self, cycle_id
**Returns**: IValidationContextProtocol
**Description**: 
        Start a new validation cycle.

        Args:
            cycle_id: Optional cycle ID

        Returns:
            New ValidationContext
        



## Function: complete_cycle

**Parameters**: self, status
**Description**: 
        Complete the current cycle and save history.

        Args:
            status: Cycle completion status
        



## Function: get_file_statistics

**Parameters**: self, file_path
**Returns**: dict
**Description**: 
        Get validation statistics for a file.

        Args:
            file_path: Path to the file

        Returns:
            Statistics dictionary
        



## Function: get_cycle_summary

**Parameters**: self
**Returns**: dict
**Description**: 
        Get summary of the current cycle.

        Returns:
            Cycle summary dictionary
        



## Usage Examples

### Class Usage

```python
# Using IValidationContextProtocol
ivalidationcontextprotocol = IValidationContextProtocol()
ivalidationcontextprotocol.update_file_hash()
ivalidationcontextprotocol.mark_flapping()
```

```python
# Using IValidationContextManager
ivalidationcontextmanager = IValidationContextManager()
ivalidationcontextmanager.get_last_file_hashes()
ivalidationcontextmanager.get_flapping_files()
```

```python
# Using Historian
historian = Historian()
historian.calculate_file_hash()
historian.should_skip_file()
```

### Function Usage

```python
# Using _get_write_gateway
result = _get_write_gateway()
```

```python
# Using get_historian
result = get_historian()
```

```python
# Using initialize_historian
result = initialize_historian(context_manager, memory_dir)
```



---
**Generated**: 2026-03-26T09:39:04.652128
**Type**: api_reference
**Quality**: comprehensive
