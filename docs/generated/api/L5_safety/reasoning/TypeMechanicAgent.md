# API Documentation: TypeMechanicAgent

**Target Audience**: developers, api_users

# TypeMechanicAgent API Documentation

**File**: `TypeMechanicAgent.py`
**Classes**: 1
**Functions**: 14

## Classes

- **TypeMechanicAgent** (inherits from SubAtomicAgent)

## Functions

- **heal_repository** -> dict[str, Any]
- **can_run** -> bool
- **execute** -> None
- **_read_and_parse_file** -> tuple[ast.AST | None, str | None]
- **_get_missing_type_hint_violations_for_tree** -> list[str]
- **check_no_missing_type_hints** -> tuple[bool, list[str]]
- **_check_function_for_unreachable_code** -> list[str]
- **_get_unreachable_code_violations_for_tree** -> list[str]
- **check_no_unreachable_code** -> tuple[bool, list[str]]
- **_collect_variables** -> tuple[set[str], set[str]]
- **_get_function_violations_for_file** -> list[str]
- **_process_file_for_unused_variables** -> list[str]
- **check_no_unused_variables** -> tuple[bool, list[str]]
- **heal**


## Class: TypeMechanicAgent

**Description**: 
    Type Mechanic Agent - Type hints and code quality enforcement.

    Validates:
    - Missing type hints
    - Unreachable code
    - Unused variables

    ROLE: Precision Engineering. Requires AST_VALID signal.
    

**Inherits from**: SubAtomicAgent

### Methods

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        

#### can_run
**Parameters**: self
**Returns**: bool
**Description**: 
        Determines if the agent can run based on the presence of the 'AST_VALID' signal.
        

#### execute
**Parameters**: self
**Returns**: None
**Description**: 
        Executes the TypeMechanic agent, performing checks for type system violations.
        

#### _read_and_parse_file
**Parameters**: self, fp
**Returns**: tuple[ast.AST | None, str | None]
**Description**: 
        Reads a file and parses it into an AST, handling errors.
        Returns (tree, error_message).
        

#### _get_missing_type_hint_violations_for_tree
**Parameters**: self, fp, tree
**Returns**: list[str]
**Description**: 
        Collects formatted Violation strings for Missing type hints in a given AST tree.
        

#### check_no_missing_type_hints
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Checks for functions with Missing type hints (return types).
        Excludes __init__, __str__, __repr__ methods.
        Refactored to reduce nesting depth to meet max 4.
        

#### _check_function_for_unreachable_code
**Parameters**: self, fp, func_node
**Returns**: list[str]
**Description**: 
        Checks a single function node for unreachable code after a return statement.
        

#### _get_unreachable_code_violations_for_tree
**Parameters**: self, fp, tree
**Returns**: list[str]
**Description**: 
        Processes an AST tree to find unreachable code violations within functions.
        

#### check_no_unreachable_code
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Checks for unreachable code, specifically statements after a 'return' statement
        within a function body.
        Refactored to reduce nesting depth to meet max 4.
        

#### _collect_variables
**Parameters**: self, func_node
**Returns**: tuple[set[str], set[str]]
**Description**: 
        Collects assigned and used variable names within a given function AST node.
        

#### _get_function_violations_for_file
**Parameters**: self, fp, tree
**Returns**: list[str]
**Description**: 
        Processes an AST tree to find unused variables within functions.
        

#### _process_file_for_unused_variables
**Parameters**: self, fp
**Returns**: list[str]
**Description**: 
        Opens and parses a single file, then delegates to find unused variables.
        Handles file I/O and parsing errors.
        

#### check_no_unused_variables
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Checks for variables that are assigned but never used within a function.
        Refactored to reduce nesting depth.
        

#### heal
**Parameters**: self, violation



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        



## Function: can_run

**Parameters**: self
**Returns**: bool
**Description**: 
        Determines if the agent can run based on the presence of the 'AST_VALID' signal.
        



## Function: execute

**Parameters**: self
**Returns**: None
**Description**: 
        Executes the TypeMechanic agent, performing checks for type system violations.
        



## Function: _read_and_parse_file

**Parameters**: self, fp
**Returns**: tuple[ast.AST | None, str | None]
**Description**: 
        Reads a file and parses it into an AST, handling errors.
        Returns (tree, error_message).
        



## Function: _get_missing_type_hint_violations_for_tree

**Parameters**: self, fp, tree
**Returns**: list[str]
**Description**: 
        Collects formatted Violation strings for Missing type hints in a given AST tree.
        



## Function: check_no_missing_type_hints

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Checks for functions with Missing type hints (return types).
        Excludes __init__, __str__, __repr__ methods.
        Refactored to reduce nesting depth to meet max 4.
        



## Function: _check_function_for_unreachable_code

**Parameters**: self, fp, func_node
**Returns**: list[str]
**Description**: 
        Checks a single function node for unreachable code after a return statement.
        



## Function: _get_unreachable_code_violations_for_tree

**Parameters**: self, fp, tree
**Returns**: list[str]
**Description**: 
        Processes an AST tree to find unreachable code violations within functions.
        



## Function: check_no_unreachable_code

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Checks for unreachable code, specifically statements after a 'return' statement
        within a function body.
        Refactored to reduce nesting depth to meet max 4.
        



## Function: _collect_variables

**Parameters**: self, func_node
**Returns**: tuple[set[str], set[str]]
**Description**: 
        Collects assigned and used variable names within a given function AST node.
        



## Function: _get_function_violations_for_file

**Parameters**: self, fp, tree
**Returns**: list[str]
**Description**: 
        Processes an AST tree to find unused variables within functions.
        



## Function: _process_file_for_unused_variables

**Parameters**: self, fp
**Returns**: list[str]
**Description**: 
        Opens and parses a single file, then delegates to find unused variables.
        Handles file I/O and parsing errors.
        



## Function: check_no_unused_variables

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Checks for variables that are assigned but never used within a function.
        Refactored to reduce nesting depth.
        



## Function: heal

**Parameters**: self, violation


## Usage Examples

### Class Usage

```python
# Using TypeMechanicAgent
typemechanicagent = TypeMechanicAgent()
typemechanicagent.heal_repository()
typemechanicagent.can_run()
```

### Function Usage

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```

```python
# Using can_run
result = can_run()
```

```python
# Using execute
result = execute()
```



---
**Generated**: 2026-03-26T09:39:05.447792
**Type**: api_reference
**Quality**: comprehensive
