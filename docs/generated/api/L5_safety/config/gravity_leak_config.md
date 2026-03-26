# API Documentation: gravity_leak_config

**Target Audience**: developers, api_users

# gravity_leak_config API Documentation

**File**: `gravity_leak_config.py`
**Classes**: 1
**Functions**: 14

## Classes

- **GravityLeakDetector**

## Functions

- **__init__**
- **_recompute_ast_scores** -> tuple[float, float, dict[str, float]]
- **_collect_ast_increments** -> dict
- **_score_identifier** -> None
- **_score_arguments** -> None
- **_score_assignments** -> None
- **_score_variable** -> None
- **_score_string** -> None
- **_aggregate_ast_increments** -> dict
- **_heal_gravity_violations** -> list[dict[str, Any]]
- **_extract_downstream_roots** -> list[str]
- **_insert_gravity_heal_todo** -> str
- **_find_todo_insert_position** -> int
- **_backup_and_write_file** -> None


## Class: GravityLeakDetector

**Description**: 
    Cross-boundary dependency detection agent.

    Detects:
    - Gravity leaks (agentic_core importing from apps_*)
    - Downstream dependency chains
    - Semantic alignment violations
    - AST-based semantic scoring

    Performs:
    - TODO marker insertion for manual review
    - Gravity violation healing (import removal)
    - Deep import validation

    Does NOT perform:
    - Validation (use LocationValidatorAgent)
    - File operations (delegates to LocationHealerAgent)

    Gravity leaks require manual review and architectural decisions.
    

### Methods

#### __init__
**Parameters**: self, project_root
**Description**: Initialize gravity detector.

#### _recompute_ast_scores
**Parameters**: self, tree
**Returns**: tuple[float, float, dict[str, float]]
**Description**: AST score recomputation orchestrator — linear walk + aggregation.

#### _collect_ast_increments
**Parameters**: self, tree
**Returns**: dict
**Description**: Phase 1: Pure AST walk — collect raw risk increments.

#### _score_identifier
**Parameters**: self, name, weight, increments
**Returns**: None
**Description**: Score an identifier against app/territory terms.

#### _score_arguments
**Parameters**: self, node, increments
**Returns**: None
**Description**: Score function arguments.

#### _score_assignments
**Parameters**: self, node, increments
**Returns**: None
**Description**: Score assignment targets.

#### _score_variable
**Parameters**: self, name, increments
**Returns**: None
**Description**: Score a variable name.

#### _score_string
**Parameters**: self, text, increments
**Returns**: None
**Description**: Score a string literal.

#### _aggregate_ast_increments
**Parameters**: self, initial_scores, increments
**Returns**: dict
**Description**: Phase 2: Simple aggregation.

#### _heal_gravity_violations
**Parameters**: self, gravity_issues
**Returns**: list[dict[str, Any]]
**Description**: Helper method to heal gravity violations by removing offending imports.

#### _extract_downstream_roots
**Parameters**: self, msg
**Returns**: list[str]
**Description**: Extract downstream roots from gravity violation message.

#### _insert_gravity_heal_todo
**Parameters**: self, lines, msg, removed_modules
**Returns**: str
**Description**: Insert TODO block after shebang/docstring.

#### _find_todo_insert_position
**Parameters**: self, lines
**Returns**: int
**Description**: Find position to insert TODO block after shebang/docstring.

#### _backup_and_write_file
**Parameters**: self, path, content
**Returns**: None
**Description**: Backup file and write new content.



## Function: __init__

**Parameters**: self, project_root
**Description**: Initialize gravity detector.



## Function: _recompute_ast_scores

**Parameters**: self, tree
**Returns**: tuple[float, float, dict[str, float]]
**Description**: AST score recomputation orchestrator — linear walk + aggregation.



## Function: _collect_ast_increments

**Parameters**: self, tree
**Returns**: dict
**Description**: Phase 1: Pure AST walk — collect raw risk increments.



## Function: _score_identifier

**Parameters**: self, name, weight, increments
**Returns**: None
**Description**: Score an identifier against app/territory terms.



## Function: _score_arguments

**Parameters**: self, node, increments
**Returns**: None
**Description**: Score function arguments.



## Function: _score_assignments

**Parameters**: self, node, increments
**Returns**: None
**Description**: Score assignment targets.



## Function: _score_variable

**Parameters**: self, name, increments
**Returns**: None
**Description**: Score a variable name.



## Function: _score_string

**Parameters**: self, text, increments
**Returns**: None
**Description**: Score a string literal.



## Function: _aggregate_ast_increments

**Parameters**: self, initial_scores, increments
**Returns**: dict
**Description**: Phase 2: Simple aggregation.



## Function: _heal_gravity_violations

**Parameters**: self, gravity_issues
**Returns**: list[dict[str, Any]]
**Description**: Helper method to heal gravity violations by removing offending imports.



## Function: _extract_downstream_roots

**Parameters**: self, msg
**Returns**: list[str]
**Description**: Extract downstream roots from gravity violation message.



## Function: _insert_gravity_heal_todo

**Parameters**: self, lines, msg, removed_modules
**Returns**: str
**Description**: Insert TODO block after shebang/docstring.



## Function: _find_todo_insert_position

**Parameters**: self, lines
**Returns**: int
**Description**: Find position to insert TODO block after shebang/docstring.



## Function: _backup_and_write_file

**Parameters**: self, path, content
**Returns**: None
**Description**: Backup file and write new content.



## Usage Examples

### Class Usage

```python
# Using GravityLeakDetector
gravityleakdetector = GravityLeakDetector()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using _recompute_ast_scores
result = _recompute_ast_scores(tree)
```

```python
# Using _collect_ast_increments
result = _collect_ast_increments(tree)
```



---
**Generated**: 2026-03-26T09:39:04.744519
**Type**: api_reference
**Quality**: comprehensive
