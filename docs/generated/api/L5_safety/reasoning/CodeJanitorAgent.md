# API Documentation: CodeJanitorAgent

**Target Audience**: developers, api_users

# CodeJanitorAgent API Documentation

**File**: `CodeJanitorAgent.py`
**Classes**: 2
**Functions**: 14

## Classes

- **JanitorViolation**
- **CodeJanitorAgent** (inherits from SubatomicTestingMixin, CanonBaseAgent, MCPHardenedMixin)

## Functions

- **get_validation_keys** -> list[int]
- **check_syntax** -> tuple[bool, list[str]]
- **check_indentation** -> tuple[bool, list[str]]
- **_check_line_indentation** -> None
- **check_trailing_whitespace** -> tuple[bool, list[str]]
- **_check_node_naming_convention** -> Any
- **_process_file_for_naming_conventions** -> Any
- **check_naming_conventions** -> tuple[bool, list[str]]
- **_read_file_content** -> tuple[str | None, str | None]
- **_write_file_content** -> str | None
- **post_heal_validation** -> dict[str, Any]
- **cleanup_violations** -> list[dict[str, Any]]
- **run_with_cleanup** -> dict[str, Any]
- **heal_repository** -> dict[str, int]


## Class: JanitorViolation

**Description**: Structured violation for code janitor healing.



## Class: CodeJanitorAgent

**Description**: 
    Code Janitor validates syntax, style, and formatting.

    Validates:
    - No syntax errors
    - Proper indentation (4 spaces)
    - No trailing whitespace
    - Proper line endings (implicitly handled by editors/git, but can be checked)
    - Naming conventions (snake_case, PascalCase)
    - Other style guide compliance (e.g., line length, blank lines, imports)
    

**Inherits from**: SubatomicTestingMixin, CanonBaseAgent, MCPHardenedMixin

### Methods

#### get_validation_keys
**Parameters**: self
**Returns**: list[int]
**Description**: Return canon keys validated by this agent.

#### check_syntax
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for syntax errors in Python files.

        Returns:
            Tuple of (passed, list of violations)
        

#### check_indentation
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for proper indentation (4 spaces, no tabs).

        Returns:
            Tuple of (passed, list of violations)
        

#### _check_line_indentation
**Parameters**: self, file_path, line_num, line, violations
**Returns**: None
**Description**: Check indentation for a single line.

#### check_trailing_whitespace
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for trailing whitespace at end of lines.

        Returns:
            Tuple of (passed, list of violations)
        

#### _check_node_naming_convention
**Parameters**: self, file_path, node, violations
**Returns**: Any
**Description**: Helper to check naming convention for a single AST node.

#### _process_file_for_naming_conventions
**Parameters**: self, file_path, violations
**Returns**: Any
**Description**: Helper to parse a single file and check all its AST nodes for naming conventions.

#### check_naming_conventions
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for proper naming conventions.

        Returns:
            Tuple of (passed, list of violations)
        

#### _read_file_content
**Parameters**: self, file_path
**Returns**: tuple[str | None, str | None]
**Description**: Helper to read file content, returning content and any error message.

#### _write_file_content
**Parameters**: self, file_path, content
**Returns**: str | None
**Description**: Helper to write content to file, returning any error message.

#### post_heal_validation
**Parameters**: self, file_path, key_id, dry_run
**Returns**: dict[str, Any]
**Description**: GOLD STANDARD: Post-heal validation confirming code quality.

#### cleanup_violations
**Parameters**: self, violations, dry_run, max_actions
**Returns**: list[dict[str, Any]]
**Description**: GOLD STANDARD: Cleanup code violations with auto-fixes.

#### run_with_cleanup
**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: GOLD STANDARD: Full code validation with autonomous cleanup.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L2 execution agent - invoke shared healing chain.



## Function: get_validation_keys

**Parameters**: self
**Returns**: list[int]
**Description**: Return canon keys validated by this agent.



## Function: check_syntax

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for syntax errors in Python files.

        Returns:
            Tuple of (passed, list of violations)
        



## Function: check_indentation

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for proper indentation (4 spaces, no tabs).

        Returns:
            Tuple of (passed, list of violations)
        



## Function: _check_line_indentation

**Parameters**: self, file_path, line_num, line, violations
**Returns**: None
**Description**: Check indentation for a single line.



## Function: check_trailing_whitespace

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for trailing whitespace at end of lines.

        Returns:
            Tuple of (passed, list of violations)
        



## Function: _check_node_naming_convention

**Parameters**: self, file_path, node, violations
**Returns**: Any
**Description**: Helper to check naming convention for a single AST node.



## Function: _process_file_for_naming_conventions

**Parameters**: self, file_path, violations
**Returns**: Any
**Description**: Helper to parse a single file and check all its AST nodes for naming conventions.



## Function: check_naming_conventions

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for proper naming conventions.

        Returns:
            Tuple of (passed, list of violations)
        



## Function: _read_file_content

**Parameters**: self, file_path
**Returns**: tuple[str | None, str | None]
**Description**: Helper to read file content, returning content and any error message.



## Function: _write_file_content

**Parameters**: self, file_path, content
**Returns**: str | None
**Description**: Helper to write content to file, returning any error message.



## Function: post_heal_validation

**Parameters**: self, file_path, key_id, dry_run
**Returns**: dict[str, Any]
**Description**: GOLD STANDARD: Post-heal validation confirming code quality.



## Function: cleanup_violations

**Parameters**: self, violations, dry_run, max_actions
**Returns**: list[dict[str, Any]]
**Description**: GOLD STANDARD: Cleanup code violations with auto-fixes.



## Function: run_with_cleanup

**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: GOLD STANDARD: Full code validation with autonomous cleanup.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L2 execution agent - invoke shared healing chain.



## Usage Examples

### Class Usage

```python
# Using JanitorViolation
janitorviolation = JanitorViolation()
```

```python
# Using CodeJanitorAgent
codejanitoragent = CodeJanitorAgent()
codejanitoragent.get_validation_keys()
codejanitoragent.check_syntax()
```

### Function Usage

```python
# Using get_validation_keys
result = get_validation_keys()
```

```python
# Using check_syntax
result = check_syntax()
```

```python
# Using check_indentation
result = check_indentation()
```



---
**Generated**: 2026-03-26T09:39:05.096233
**Type**: api_reference
**Quality**: comprehensive
