# API Documentation: ssot_audit_util

**Target Audience**: developers, api_users

# ssot_audit_util API Documentation

**File**: `ssot_audit_util.py`
**Classes**: 0
**Functions**: 4


## Functions

- **find_duplicates**
- **find_gravity_violations**
- **find_syntax_errors**
- **find_naming_violations**


## Function: find_duplicates

**Description**: Find duplicate filenames across approved folders.



## Function: find_gravity_violations

**Description**: Find upward import violations (higher layer importing from lower layer).



## Function: find_syntax_errors

**Description**: Find files with syntax errors.



## Function: find_naming_violations

**Description**: Find files with naming convention violations.



## Usage Examples

### Function Usage

```python
# Using find_duplicates
result = find_duplicates()
```

```python
# Using find_gravity_violations
result = find_gravity_violations()
```

```python
# Using find_syntax_errors
result = find_syntax_errors()
```



---
**Generated**: 2026-03-26T09:39:03.269437
**Type**: api_reference
**Quality**: comprehensive
