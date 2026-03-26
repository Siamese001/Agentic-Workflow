# API Documentation: code_validator_runner

**Target Audience**: developers, api_users

# code_validator_runner API Documentation

**File**: `code_validator_runner.py`
**Classes**: 0
**Functions**: 4


## Functions

- **get_project_root** -> Path
- **validate_repository** -> dict
- **validate_directory** -> dict
- **main** -> int


## Function: get_project_root

**Returns**: Path
**Description**: Get project root from this file's location.



## Function: validate_repository

**Parameters**: project_root
**Returns**: dict
**Description**: Validate entire repository with CodeValidatorAgent.



## Function: validate_directory

**Parameters**: project_root, directory
**Returns**: dict
**Description**: Validate specific directory with CodeValidatorAgent.



## Function: main

**Returns**: int
**Description**: CLI entry point for subprocess invocation.



## Usage Examples

### Function Usage

```python
# Using get_project_root
result = get_project_root()
```

```python
# Using validate_repository
result = validate_repository(project_root)
```

```python
# Using validate_directory
result = validate_directory(project_root, directory)
```



---
**Generated**: 2026-03-26T09:39:05.457828
**Type**: api_reference
**Quality**: comprehensive
