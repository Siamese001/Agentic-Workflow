# API Documentation: write_gateway_enforcer

**Target Audience**: developers, api_users

# write_gateway_enforcer API Documentation

**File**: `write_gateway_enforcer.py`
**Classes**: 1
**Functions**: 7

## Classes

- **WriteGatewayVisitor** (inherits from <ast.Attribute object at 0x000001CBFAE78510>)

## Functions

- **scan_file_for_writes** -> list[tuple[int, str, str]]
- **scan_repository_for_writes** -> list[tuple[str, int, str, str]]
- **__init__**
- **visit** -> None
- **_check_allowlist** -> bool
- **visit_Call** -> None
- **visit_With** -> None


## Class: WriteGatewayVisitor

**Description**: AST visitor to detect direct file writes.

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self, file_path

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
**Description**: Check for direct file write calls.

#### visit_With
**Parameters**: self, node
**Returns**: None
**Description**: Check for 'with open(...)' patterns.



## Function: scan_file_for_writes

**Parameters**: file_path
**Returns**: list[tuple[int, str, str]]
**Description**: Scan a single file for direct file writes.

    Args:
        file_path: Path to file to scan

    Returns:
        List of (lineno, rule_id, snippet) tuples
    



## Function: scan_repository_for_writes

**Parameters**: repo_root
**Returns**: list[tuple[str, int, str, str]]
**Description**: Scan governance-critical storage/replay directories for direct file writes.

    Only scans the directories where the UWG write-gateway contract is enforced.
    Legacy script, agent, and reasoning directories are excluded.

    Args:
        repo_root: Repository root path

    Returns:
        List of (file_path, lineno, rule_id, snippet) tuples, sorted deterministically
    



## Function: __init__

**Parameters**: self, file_path


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
**Description**: Check for direct file write calls.



## Function: visit_With

**Parameters**: self, node
**Returns**: None
**Description**: Check for 'with open(...)' patterns.



## Usage Examples

### Class Usage

```python
# Using WriteGatewayVisitor
writegatewayvisitor = WriteGatewayVisitor()
writegatewayvisitor.visit()
writegatewayvisitor.visit_Call()
```

### Function Usage

```python
# Using scan_file_for_writes
result = scan_file_for_writes(file_path)
```

```python
# Using scan_repository_for_writes
result = scan_repository_for_writes(repo_root)
```

```python
# Using __init__
result = __init__(file_path)
```



---
**Generated**: 2026-03-26T09:39:05.487983
**Type**: api_reference
**Quality**: comprehensive
