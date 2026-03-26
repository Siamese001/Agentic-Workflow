# API Documentation: healing_invocation_audit_enforcer

**Target Audience**: developers, api_users

# healing_invocation_audit_enforcer API Documentation

**File**: `healing_invocation_audit_enforcer.py`
**Classes**: 1
**Functions**: 7

## Classes

- **HealingInvocationAudit**

## Functions

- **main**
- **__init__**
- **audit_all_methods** -> dict
- **_extract_agent_name** -> str
- **_check_super_presence** -> bool
- **generate_report** -> str
- **print_summary**


## Class: HealingInvocationAudit

**Description**: Audit heal_repository() methods for super() presence and chain completeness.

### Methods

#### __init__
**Parameters**: self, project_root
**Description**: Initialize audit tool.

#### audit_all_methods
**Parameters**: self
**Returns**: dict
**Description**: 
        Audit all heal_repository() methods in codebase.

        Returns:
            Audit results dictionary
        

#### _extract_agent_name
**Parameters**: self, file_path
**Returns**: str
**Description**: Extract agent class name from file path and content.

#### _check_super_presence
**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if super().heal_repository() is present in method.

#### generate_report
**Parameters**: self, output_file
**Returns**: str
**Description**: 
        Generate markdown audit report.

        Args:
            output_file: Path to save report

        Returns:
            Report markdown string
        

#### print_summary
**Parameters**: self
**Description**: Print audit summary to console.



## Function: main

**Description**: Main entry point.



## Function: __init__

**Parameters**: self, project_root
**Description**: Initialize audit tool.



## Function: audit_all_methods

**Parameters**: self
**Returns**: dict
**Description**: 
        Audit all heal_repository() methods in codebase.

        Returns:
            Audit results dictionary
        



## Function: _extract_agent_name

**Parameters**: self, file_path
**Returns**: str
**Description**: Extract agent class name from file path and content.



## Function: _check_super_presence

**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if super().heal_repository() is present in method.



## Function: generate_report

**Parameters**: self, output_file
**Returns**: str
**Description**: 
        Generate markdown audit report.

        Args:
            output_file: Path to save report

        Returns:
            Report markdown string
        



## Function: print_summary

**Parameters**: self
**Description**: Print audit summary to console.



## Usage Examples

### Class Usage

```python
# Using HealingInvocationAudit
healinginvocationaudit = HealingInvocationAudit()
healinginvocationaudit.audit_all_methods()
healinginvocationaudit.generate_report()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using audit_all_methods
result = audit_all_methods()
```



---
**Generated**: 2026-03-26T09:39:04.835005
**Type**: api_reference
**Quality**: comprehensive
