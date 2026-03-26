# API Documentation: determinism_serialization_check

**Target Audience**: developers, api_users

# determinism_serialization_check API Documentation

**File**: `determinism_serialization_check.py`
**Classes**: 2
**Functions**: 13

## Classes

- **DeterminismVisitor** (inherits from <ast.Attribute object at 0x000001CBFCB877D0>)
- **ExecutionScopeNondeterminismVisitor** (inherits from <ast.Attribute object at 0x000001CBFB8E2210>)

## Functions

- **scan_file_for_determinism** -> list[tuple[int, str, str]]
- **scan_repository_for_determinism** -> list[tuple[str, int, str, str]]
- **scan_file_for_execution_nondeterminism** -> list[tuple[int, str, str]]
- **scan_execution_scope_for_nondeterminism** -> list[tuple[str, int, str, str]]
- **__init__**
- **visit_FunctionDef** -> None
- **visit_Call** -> None
- **visit_Import** -> None
- **visit_ImportFrom** -> None
- **__init__** -> None
- **_is_allowed** -> bool
- **visit_Call** -> None
- **_check_call** -> None


## Class: DeterminismVisitor

**Description**: AST visitor to detect non-deterministic serialization patterns.

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self, file_path

#### visit_FunctionDef
**Parameters**: self, node
**Returns**: None
**Description**: Track function context.

#### visit_Call
**Parameters**: self, node
**Returns**: None
**Description**: Check function calls for non-deterministic patterns.

#### visit_Import
**Parameters**: self, node
**Returns**: None
**Description**: Check for imports of non-deterministic modules.

#### visit_ImportFrom
**Parameters**: self, node
**Returns**: None
**Description**: Check for from-imports of non-deterministic modules.



## Class: ExecutionScopeNondeterminismVisitor

**Description**: AST visitor that detects raw non-deterministic calls in execution-critical code.

    Flags:
    - ``time.time()`` / ``time.monotonic()`` / ``time.sleep()``
    - ``datetime.now()`` / ``datetime.utcnow()``
    - ``random.<any>()`` (except ``random.Random(seed)`` construction)
    - ``uuid.uuid4()``

    Calls on lines annotated with ``# guardian: allow-nondeterminism`` are
    suppressed, as are calls inside functions/methods named with a
    ``_determinism`` prefix (i.e., the infrastructure itself).
    

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self, source_lines
**Returns**: None

#### _is_allowed
**Parameters**: self, lineno
**Returns**: bool
**Description**: True if the source line carries the guardian allowlist comment.

#### visit_Call
**Parameters**: self, node
**Returns**: None

#### _check_call
**Parameters**: self, node
**Returns**: None



## Function: scan_file_for_determinism

**Parameters**: file_path
**Returns**: list[tuple[int, str, str]]
**Description**: Scan a single file for non-deterministic serialization patterns.

    Args:
        file_path: Path to file to scan

    Returns:
        List of (lineno, rule_id, snippet) tuples
    



## Function: scan_repository_for_determinism

**Parameters**: repo_root
**Returns**: list[tuple[str, int, str, str]]
**Description**: Scan repository for non-deterministic serialization in replay/storage modules.

    Args:
        repo_root: Repository root path

    Returns:
        List of (file_path, lineno, rule_id, snippet) tuples, sorted deterministically
    



## Function: scan_file_for_execution_nondeterminism

**Parameters**: file_path
**Returns**: list[tuple[int, str, str]]
**Description**: Scan a single file for raw non-deterministic calls in execution scope.

    Args:
        file_path: Path to file to scan.

    Returns:
        List of (lineno, rule_id, snippet) tuples.
    



## Function: scan_execution_scope_for_nondeterminism

**Parameters**: repo_root
**Returns**: list[tuple[str, int, str, str]]
**Description**: Scan execution-critical layers for raw non-deterministic calls.

    Covers L1_cognition, L2_execution, L3_orchestration, and base_agents.
    Skips determinism-infrastructure modules.

    Args:
        repo_root: Repository root path.

    Returns:
        Sorted list of (file_path, lineno, rule_id, snippet) tuples.
    



## Function: __init__

**Parameters**: self, file_path


## Function: visit_FunctionDef

**Parameters**: self, node
**Returns**: None
**Description**: Track function context.



## Function: visit_Call

**Parameters**: self, node
**Returns**: None
**Description**: Check function calls for non-deterministic patterns.



## Function: visit_Import

**Parameters**: self, node
**Returns**: None
**Description**: Check for imports of non-deterministic modules.



## Function: visit_ImportFrom

**Parameters**: self, node
**Returns**: None
**Description**: Check for from-imports of non-deterministic modules.



## Function: __init__

**Parameters**: self, source_lines
**Returns**: None


## Function: _is_allowed

**Parameters**: self, lineno
**Returns**: bool
**Description**: True if the source line carries the guardian allowlist comment.



## Function: visit_Call

**Parameters**: self, node
**Returns**: None


## Function: _check_call

**Parameters**: self, node
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using DeterminismVisitor
determinismvisitor = DeterminismVisitor()
determinismvisitor.visit_FunctionDef()
determinismvisitor.visit_Call()
```

```python
# Using ExecutionScopeNondeterminismVisitor
executionscopenondeterminismvisitor = ExecutionScopeNondeterminismVisitor()
executionscopenondeterminismvisitor.visit_Call()
```

### Function Usage

```python
# Using scan_file_for_determinism
result = scan_file_for_determinism(file_path)
```

```python
# Using scan_repository_for_determinism
result = scan_repository_for_determinism(repo_root)
```

```python
# Using scan_file_for_execution_nondeterminism
result = scan_file_for_execution_nondeterminism(file_path)
```



---
**Generated**: 2026-03-26T09:39:05.476730
**Type**: api_reference
**Quality**: comprehensive
