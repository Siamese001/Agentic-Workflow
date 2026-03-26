# API Documentation: agent_validation_util

**Target Audience**: developers, api_users

# agent_validation_util API Documentation

**File**: `agent_validation_util.py`
**Classes**: 0
**Functions**: 3


## Functions

- **run_code_deduplication_check** -> tuple[bool, str]
- **run_architecture_governance_check** -> tuple[bool, str]
- **main** -> int


## Function: run_code_deduplication_check

**Returns**: tuple[bool, str]
**Description**: 
    Run CodeDeduplicationAgent to detect duplicate filenames.

    Returns:
        Tuple of (success, message)
    



## Function: run_architecture_governance_check

**Returns**: tuple[bool, str]
**Description**: 
    Run ArchitectureGovernorAgent to validate SSOT folder structure.

    Returns:
        Tuple of (success, message)
    



## Function: main

**Returns**: int
**Description**: 
    Run all agent validations.

    Returns:
        Exit code (0 for success, 1 for failure)
    



## Usage Examples

### Function Usage

```python
# Using run_code_deduplication_check
result = run_code_deduplication_check()
```

```python
# Using run_architecture_governance_check
result = run_architecture_governance_check()
```

```python
# Using main
result = main()
```



---
**Generated**: 2026-03-26T09:39:02.746469
**Type**: api_reference
**Quality**: comprehensive
