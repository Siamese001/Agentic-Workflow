# API Documentation: ptc_invariants

**Target Audience**: developers, api_users

# ptc_invariants API Documentation

**File**: `ptc_invariants.py`
**Classes**: 1
**Functions**: 7

## Classes

- **PTCInvariantVisitor** (inherits from <ast.Attribute object at 0x000001CBFCB84A50>)

## Functions

- **scan_file_for_ptc_invariants** -> list[tuple[int, str, str]]
- **scan_repository_for_ptc_invariants** -> list[tuple[str, int, str, str]]
- **__init__**
- **visit** -> None
- **_check_allowlist** -> bool
- **visit_Call** -> None
- **visit_ClassDef** -> None


## Class: PTCInvariantVisitor

**Description**: AST visitor to check PTC invariants.

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self, file_path
**Description**: Initialize visitor with file path.

#### visit
**Parameters**: self, node
**Returns**: None
**Description**: Override to track line content.

#### _check_allowlist
**Parameters**: self
**Returns**: bool
**Description**: Check if current line has allowlist comment.

#### visit_Call
**Parameters**: self, node
**Returns**: None
**Description**: Check for shell=True usage in PTC tools.

#### visit_ClassDef
**Parameters**: self, node
**Returns**: None
**Description**: Check ToolSpec args are sorted.



## Function: scan_file_for_ptc_invariants

**Parameters**: file_path
**Returns**: list[tuple[int, str, str]]
**Description**: Scan a single file for PTC invariants violations.

    Args:
        file_path: Path to file to scan

    Returns:
        List of violations as (line, rule_id, description)
    



## Function: scan_repository_for_ptc_invariants

**Parameters**: repo_root
**Returns**: list[tuple[str, int, str, str]]
**Description**: Scan repository for PTC invariants violations.

    Args:
        repo_root: Repository root path

    Returns:
        List of violations as (file_path, line, rule_id, description)
    



## Function: __init__

**Parameters**: self, file_path
**Description**: Initialize visitor with file path.



## Function: visit

**Parameters**: self, node
**Returns**: None
**Description**: Override to track line content.



## Function: _check_allowlist

**Parameters**: self
**Returns**: bool
**Description**: Check if current line has allowlist comment.



## Function: visit_Call

**Parameters**: self, node
**Returns**: None
**Description**: Check for shell=True usage in PTC tools.



## Function: visit_ClassDef

**Parameters**: self, node
**Returns**: None
**Description**: Check ToolSpec args are sorted.



## Usage Examples

### Class Usage

```python
# Using PTCInvariantVisitor
ptcinvariantvisitor = PTCInvariantVisitor()
ptcinvariantvisitor.visit()
ptcinvariantvisitor.visit_Call()
```

### Function Usage

```python
# Using scan_file_for_ptc_invariants
result = scan_file_for_ptc_invariants(file_path)
```

```python
# Using scan_repository_for_ptc_invariants
result = scan_repository_for_ptc_invariants(repo_root)
```

```python
# Using __init__
result = __init__(file_path)
```



---
**Generated**: 2026-03-26T09:39:05.481909
**Type**: api_reference
**Quality**: comprehensive
