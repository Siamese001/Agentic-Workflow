# API Documentation: powershell_ban

**Target Audience**: developers, api_users

# powershell_ban API Documentation

**File**: `powershell_ban.py`
**Classes**: 1
**Functions**: 5

## Classes

- **PowerShellBanVisitor** (inherits from <ast.Attribute object at 0x000001CBFAD87BD0>)

## Functions

- **scan_file_for_powershell** -> list[tuple[int, str, str]]
- **scan_repository_for_powershell** -> list[tuple[str, int, str, str]]
- **__init__**
- **visit_Constant** -> None
- **visit_Call** -> None


## Class: PowerShellBanVisitor

**Description**: AST visitor to detect PowerShell usage patterns.

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self, file_path

#### visit_Constant
**Parameters**: self, node
**Returns**: None
**Description**: Check string literals for PowerShell command invocations in docs/evidence.

        Only flags strings that START WITH 'pwsh' or 'powershell' AND contain a space,
        indicating a full command invocation (e.g. "powershell -Command ...").
        Short guard-check strings like 'powershell' or 'pwsh' used in comparisons
        are NOT flagged because they lack a following argument.
        

#### visit_Call
**Parameters**: self, node
**Returns**: None
**Description**: Check for subprocess calls with PowerShell - semantic callsite enforcement only.



## Function: scan_file_for_powershell

**Parameters**: file_path
**Returns**: list[tuple[int, str, str]]
**Description**: Scan a single file for PowerShell usage.

    For docs/evidence files: also scans raw comment lines for PS references.
    For other files: uses AST-based detection only (subprocess calls).

    Args:
        file_path: Path to file to scan

    Returns:
        List of (lineno, rule_id, snippet) tuples
    



## Function: scan_repository_for_powershell

**Parameters**: repo_root
**Returns**: list[tuple[str, int, str, str]]
**Description**: Scan repository for PowerShell usage.

    Args:
        repo_root: Repository root path

    Returns:
        List of (file_path, lineno, rule_id, snippet) tuples, sorted deterministically
    



## Function: __init__

**Parameters**: self, file_path


## Function: visit_Constant

**Parameters**: self, node
**Returns**: None
**Description**: Check string literals for PowerShell command invocations in docs/evidence.

        Only flags strings that START WITH 'pwsh' or 'powershell' AND contain a space,
        indicating a full command invocation (e.g. "powershell -Command ...").
        Short guard-check strings like 'powershell' or 'pwsh' used in comparisons
        are NOT flagged because they lack a following argument.
        



## Function: visit_Call

**Parameters**: self, node
**Returns**: None
**Description**: Check for subprocess calls with PowerShell - semantic callsite enforcement only.



## Usage Examples

### Class Usage

```python
# Using PowerShellBanVisitor
powershellbanvisitor = PowerShellBanVisitor()
powershellbanvisitor.visit_Constant()
powershellbanvisitor.visit_Call()
```

### Function Usage

```python
# Using scan_file_for_powershell
result = scan_file_for_powershell(file_path)
```

```python
# Using scan_repository_for_powershell
result = scan_repository_for_powershell(repo_root)
```

```python
# Using __init__
result = __init__(file_path)
```



---
**Generated**: 2026-03-26T09:39:05.479852
**Type**: api_reference
**Quality**: comprehensive
