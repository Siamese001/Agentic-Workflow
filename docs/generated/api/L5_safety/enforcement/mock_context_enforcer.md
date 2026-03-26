# API Documentation: mock_context_enforcer

**Target Audience**: developers, api_users

# mock_context_enforcer API Documentation

**File**: `mock_context_enforcer.py`
**Classes**: 1
**Functions**: 6

## Classes

- **MockContext**

## Functions

- **validate_l2_l3_structure** -> dict
- **validate_depth_precision** -> dict
- **validate_tests_depth** -> dict
- **validate_universal_depth** -> dict
- **main**
- **report**


## Class: MockContext

**Description**: Mock context for dry-run mode.

### Methods

#### report
**Parameters**: self, agent_name, key, passed, details



## Function: validate_l2_l3_structure

**Parameters**: project_root
**Returns**: dict
**Description**: Validate L2/L3 structure (CORE_SUBFOLDER_MAP) without making changes.



## Function: validate_depth_precision

**Parameters**: project_root
**Returns**: dict
**Description**: Validate apps_* depth without archiving.



## Function: validate_tests_depth

**Parameters**: project_root
**Returns**: dict
**Description**: Validate tests depth without archiving.



## Function: validate_universal_depth

**Parameters**: project_root
**Returns**: dict
**Description**: Validate universal depth for non-Python files without archiving.



## Function: main



## Function: report

**Parameters**: self, agent_name, key, passed, details


## Usage Examples

### Class Usage

```python
# Using MockContext
mockcontext = MockContext()
mockcontext.report()
```

### Function Usage

```python
# Using validate_l2_l3_structure
result = validate_l2_l3_structure(project_root)
```

```python
# Using validate_depth_precision
result = validate_depth_precision(project_root)
```

```python
# Using validate_tests_depth
result = validate_tests_depth(project_root)
```



---
**Generated**: 2026-03-26T09:39:04.875625
**Type**: api_reference
**Quality**: comprehensive
