# API Documentation: system_invariant_scanner

**Target Audience**: developers, api_users

# system_invariant_scanner API Documentation

**File**: `system_invariant_scanner.py`
**Classes**: 2
**Functions**: 15

## Classes

- **BypassViolation**
- **SystemInvariantScanner** (inherits from <ast.Attribute object at 0x000001CBFB8E2350>)

## Functions

- **scan_repository_for_bypasses** -> list[BypassViolation]
- **print_bypass_report** -> None
- **get_bypass_scan_summary** -> dict[str, Any]
- **__init__**
- **__str__** -> str
- **to_dict** -> dict[str, Any]
- **__init__**
- **visit** -> None
- **_is_allowlisted** -> bool
- **_has_allowlist_comment** -> bool
- **visit_Call** -> None
- **visit_Import** -> None
- **visit_ImportFrom** -> None
- **visit_ClassDef** -> None
- **_add_violation** -> None


## Class: BypassViolation

**Description**: Represents a detected bypass violation.

### Methods

#### __init__
**Parameters**: self, file_path, line, rule_id, snippet, description

#### __str__
**Parameters**: self
**Returns**: str

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: SystemInvariantScanner

**Description**: AST visitor to detect sovereignty bypass violations.

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self, file_path

#### visit
**Parameters**: self, node
**Returns**: None
**Description**: Override to track line content.

#### _is_allowlisted
**Parameters**: self
**Returns**: bool
**Description**: Check if current file is allowlisted.

#### _has_allowlist_comment
**Parameters**: self
**Returns**: bool
**Description**: Check if current line has allowlist comment.

#### visit_Call
**Parameters**: self, node
**Returns**: None
**Description**: Check for restricted function calls.

#### visit_Import
**Parameters**: self, node
**Returns**: None
**Description**: Check for restricted imports.

#### visit_ImportFrom
**Parameters**: self, node
**Returns**: None
**Description**: Check for restricted from-imports.

#### visit_ClassDef
**Parameters**: self, node
**Returns**: None
**Description**: Check for restricted class definitions.

#### _add_violation
**Parameters**: self, line, rule_id, snippet, description
**Returns**: None
**Description**: Add a violation to the list.



## Function: scan_repository_for_bypasses

**Parameters**: repo_root
**Returns**: list[BypassViolation]
**Description**: Scan entire repository for sovereignty bypass violations.



## Function: print_bypass_report

**Parameters**: violations
**Returns**: None
**Description**: Print a formatted report of bypass violations.



## Function: get_bypass_scan_summary

**Parameters**: violations
**Returns**: dict[str, Any]
**Description**: Get summary statistics for bypass scan.



## Function: __init__

**Parameters**: self, file_path, line, rule_id, snippet, description


## Function: __str__

**Parameters**: self
**Returns**: str


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: __init__

**Parameters**: self, file_path


## Function: visit

**Parameters**: self, node
**Returns**: None
**Description**: Override to track line content.



## Function: _is_allowlisted

**Parameters**: self
**Returns**: bool
**Description**: Check if current file is allowlisted.



## Function: _has_allowlist_comment

**Parameters**: self
**Returns**: bool
**Description**: Check if current line has allowlist comment.



## Function: visit_Call

**Parameters**: self, node
**Returns**: None
**Description**: Check for restricted function calls.



## Function: visit_Import

**Parameters**: self, node
**Returns**: None
**Description**: Check for restricted imports.



## Function: visit_ImportFrom

**Parameters**: self, node
**Returns**: None
**Description**: Check for restricted from-imports.



## Function: visit_ClassDef

**Parameters**: self, node
**Returns**: None
**Description**: Check for restricted class definitions.



## Function: _add_violation

**Parameters**: self, line, rule_id, snippet, description
**Returns**: None
**Description**: Add a violation to the list.



## Usage Examples

### Class Usage

```python
# Using BypassViolation
bypassviolation = BypassViolation()
bypassviolation.to_dict()
```

```python
# Using SystemInvariantScanner
systeminvariantscanner = SystemInvariantScanner()
systeminvariantscanner.visit()
systeminvariantscanner.visit_Call()
```

### Function Usage

```python
# Using scan_repository_for_bypasses
result = scan_repository_for_bypasses(repo_root)
```

```python
# Using print_bypass_report
result = print_bypass_report(violations)
```

```python
# Using get_bypass_scan_summary
result = get_bypass_scan_summary(violations)
```



---
**Generated**: 2026-03-26T09:39:05.486083
**Type**: api_reference
**Quality**: comprehensive
