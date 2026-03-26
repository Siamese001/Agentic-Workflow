# API Documentation: DocumentationAgent

**Target Audience**: developers, api_users

# DocumentationAgent API Documentation

**File**: `DocumentationAgent.py`
**Classes**: 1
**Functions**: 6

## Classes

- **DocumentationAgent** (inherits from SubAtomicAgent)

## Functions

- **heal** -> dict[str, Any]
- **execute** -> None
- **_has_missing_docstring** -> bool
- **_find_missing_docstring_violations_in_tree** -> list[str]
- **check_no_missing_docstrings** -> tuple[bool, list[str]]
- **heal_repository** -> dict


## Class: DocumentationAgent

**Description**: 
    Documentation enforcement agent for docstring validation.

    Validates:
        - No missing docstrings in classes and functions.

    Role:
        Pure focus on docstring presence and quality.

    Note:
        Legacy L1 class - true agent is DocEnforcerAgent in L2.

    Attributes:
        agent: Injected CanonBaseAgentInterface implementation.
    

**Inherits from**: SubAtomicAgent

### Methods

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for DocumentationAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        

#### execute
**Parameters**: self
**Returns**: None
**Description**: 
        Execute documentation validation checks.

        Runs missing docstrings check and reports results
        to the validation context.
        

#### _has_missing_docstring
**Parameters**: self, node
**Returns**: bool
**Description**: 
        Check if an AST node is missing a docstring.

        Args:
            node: AST node (FunctionDef or ClassDef) to check.

        Returns:
            True if docstring is missing, False otherwise.
        

#### _find_missing_docstring_violations_in_tree
**Parameters**: self, tree, fp
**Returns**: list[str]
**Description**: 
        Find all missing docstring violations in an AST tree.

        Args:
            tree: Parsed AST tree to analyze.
            fp: File path for violation reporting.

        Returns:
            List of violation strings in 'filepath:line name' format.
        

#### check_no_missing_docstrings
**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for missing docstrings in classes and functions.

        Uses AST parsing to identify FunctionDef and ClassDef nodes
        without docstrings.

        Returns:
            Tuple of (passed: bool, violations: List[str]).
            - passed: True if no violations found.
            - violations: List of 'filepath:line name' strings.
        

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: 
        Execute healing chain via parent class.

        Returns:
            Dict with healing results from parent implementation.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for DocumentationAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        



## Function: execute

**Parameters**: self
**Returns**: None
**Description**: 
        Execute documentation validation checks.

        Runs missing docstrings check and reports results
        to the validation context.
        



## Function: _has_missing_docstring

**Parameters**: self, node
**Returns**: bool
**Description**: 
        Check if an AST node is missing a docstring.

        Args:
            node: AST node (FunctionDef or ClassDef) to check.

        Returns:
            True if docstring is missing, False otherwise.
        



## Function: _find_missing_docstring_violations_in_tree

**Parameters**: self, tree, fp
**Returns**: list[str]
**Description**: 
        Find all missing docstring violations in an AST tree.

        Args:
            tree: Parsed AST tree to analyze.
            fp: File path for violation reporting.

        Returns:
            List of violation strings in 'filepath:line name' format.
        



## Function: check_no_missing_docstrings

**Parameters**: self
**Returns**: tuple[bool, list[str]]
**Description**: 
        Check for missing docstrings in classes and functions.

        Uses AST parsing to identify FunctionDef and ClassDef nodes
        without docstrings.

        Returns:
            Tuple of (passed: bool, violations: List[str]).
            - passed: True if no violations found.
            - violations: List of 'filepath:line name' strings.
        



## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: 
        Execute healing chain via parent class.

        Returns:
            Dict with healing results from parent implementation.
        



## Usage Examples

### Class Usage

```python
# Using DocumentationAgent
documentationagent = DocumentationAgent()
documentationagent.heal()
documentationagent.execute()
```

### Function Usage

```python
# Using heal
result = heal(violation)
```

```python
# Using execute
result = execute()
```

```python
# Using _has_missing_docstring
result = _has_missing_docstring(node)
```



---
**Generated**: 2026-03-26T09:39:05.126703
**Type**: api_reference
**Quality**: comprehensive
