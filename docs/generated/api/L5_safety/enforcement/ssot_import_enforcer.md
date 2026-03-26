# API Documentation: ssot_import_enforcer

**Target Audience**: developers, api_users

# ssot_import_enforcer API Documentation

**File**: `ssot_import_enforcer.py`
**Classes**: 0
**Functions**: 3


## Functions

- **needs_ssot_import** -> bool
- **add_ssot_import** -> bool
- **main**


## Function: needs_ssot_import

**Parameters**: content
**Returns**: bool
**Description**: Check if file references layers but doesn't import SSOT.



## Function: add_ssot_import

**Parameters**: file_path
**Returns**: bool
**Description**: Add SSOT import to a file if needed.



## Function: main

**Description**: Process all Python files in agentic_core, tests, apps_shared, apps_rg, apps_lic.



## Usage Examples

### Function Usage

```python
# Using needs_ssot_import
result = needs_ssot_import(content)
```

```python
# Using add_ssot_import
result = add_ssot_import(file_path)
```

```python
# Using main
result = main()
```



---
**Generated**: 2026-03-26T09:39:04.947456
**Type**: api_reference
**Quality**: comprehensive
