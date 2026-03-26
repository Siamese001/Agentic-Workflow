# API Documentation: pre_deploy_check_util

**Target Audience**: developers, api_users

# pre_deploy_check_util API Documentation

**File**: `pre_deploy_check_util.py`
**Classes**: 0
**Functions**: 5


## Functions

- **print_banner**
- **run_e2e_tests** -> bool
- **check_ssot_files_exist** -> bool
- **check_data_freshness** -> bool
- **main**


## Function: print_banner

**Parameters**: message, char
**Description**: Print a banner message.



## Function: run_e2e_tests

**Returns**: bool
**Description**: Run the E2E dashboard tests and return True if all pass.



## Function: check_ssot_files_exist

**Returns**: bool
**Description**: Verify all SSOT files exist.



## Function: check_data_freshness

**Returns**: bool
**Description**: Check that dashboard data is not stale (regenerated recently).



## Function: main

**Description**: Main entry point for pre-deployment checks.



## Usage Examples

### Function Usage

```python
# Using print_banner
result = print_banner(message, char)
```

```python
# Using run_e2e_tests
result = run_e2e_tests()
```

```python
# Using check_ssot_files_exist
result = check_ssot_files_exist()
```



---
**Generated**: 2026-03-26T09:39:05.671519
**Type**: api_reference
**Quality**: comprehensive
