# API Documentation: ssot_cli

**Target Audience**: developers, api_users

# ssot_cli API Documentation

**File**: `ssot_cli.py`
**Classes**: 0
**Functions**: 6


## Functions

- **print_header** -> None
- **cmd_scan** -> int
- **cmd_validate** -> int
- **cmd_enforce** -> int
- **cmd_status** -> int
- **main**


## Function: print_header

**Parameters**: title, char, width
**Returns**: None
**Description**: Print formatted section header.



## Function: cmd_scan

**Parameters**: args
**Returns**: int
**Description**: 
    Scan command: List all discovered agents and their metadata.

    Returns:
        Exit code (0 for success)
    



## Function: cmd_validate

**Parameters**: args
**Returns**: int
**Description**: 
    Validate command: Run comprehensive SSOT validation.

    Returns:
        Exit code (0 if compliant, 1 if violations found)
    



## Function: cmd_enforce

**Parameters**: args
**Returns**: int
**Description**: 
    Enforce command: Apply automated remediation.

    Returns:
        Exit code (0 for success)
    



## Function: cmd_status

**Parameters**: args
**Returns**: int
**Description**: 
    Status command: Show high-level compliance dashboard.

    Returns:
        Exit code (0 for success)
    



## Function: main

**Description**: Main entry point for SSOT CLI.



## Usage Examples

### Function Usage

```python
# Using print_header
result = print_header(title, char)
```

```python
# Using cmd_scan
result = cmd_scan(args)
```

```python
# Using cmd_validate
result = cmd_validate(args)
```



---
**Generated**: 2026-03-26T09:39:03.272998
**Type**: api_reference
**Quality**: comprehensive
