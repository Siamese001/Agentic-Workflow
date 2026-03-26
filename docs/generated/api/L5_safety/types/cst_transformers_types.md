# API Documentation: cst_transformers_types

**Target Audience**: developers, api_users

# cst_transformers_types API Documentation

**File**: `cst_transformers_types.py`
**Classes**: 12
**Functions**: 30

## Classes

- **ImportTarget**
- **DocstringTarget**
- **BareExceptTarget**
- **SurgicalImportRemover** (inherits from <ast.Attribute object at 0x000001CBFB8F1CD0>)
- **SurgicalDocstringInserter** (inherits from <ast.Attribute object at 0x000001CBFCB9DE90>)
- **SurgicalBareExceptFixer** (inherits from <ast.Attribute object at 0x000001CBFCBD3DD0>)
- **SurgicalFutureImportInserter** (inherits from <ast.Attribute object at 0x000001CBFAD83E50>)
- **SurgicalTrailingWhitespaceFixer** (inherits from <ast.Attribute object at 0x000001CBFAE87810>)
- **SurgicalBlankLineNormalizer** (inherits from <ast.Attribute object at 0x000001CBFADAB210>)
- **StructuralTarget**
- **TypeHintTarget**
- **SurgicalTypeHintInserter** (inherits from <ast.Attribute object at 0x000001CBFAD582D0>)

## Functions

- **create_type_hint_inserter** -> SurgicalTypeHintInserter | None
- **create_trailing_whitespace_fixer** -> SurgicalTrailingWhitespaceFixer | None
- **create_blank_line_normalizer** -> SurgicalBlankLineNormalizer | None
- **create_import_remover** -> SurgicalImportRemover | None
- **create_docstring_inserter** -> SurgicalDocstringInserter | None
- **create_bare_except_fixer** -> SurgicalBareExceptFixer | None
- **create_future_import_inserter** -> SurgicalFutureImportInserter | None
- **__init__**
- **on_visit** -> bool
- **leave_Import** -> cst.Import
- **leave_ImportFrom** -> cst.ImportFrom
- **leave_SimpleStatementLine** -> cst.SimpleStatementLine
- **__init__**
- **_has_docstring** -> bool
- **_create_docstring_stmt** -> cst.SimpleStatementLine
- **leave_ClassDef** -> cst.ClassDef
- **leave_FunctionDef** -> cst.FunctionDef
- **__init__**
- **leave_ExceptHandler** -> cst.ExceptHandler
- **_should_fix** -> bool
- **__init__**
- **visit_ImportFrom** -> bool
- **leave_Module** -> cst.Module
- **__init__**
- **leave_TrailingWhitespace** -> cst.TrailingWhitespace
- **leave_EmptyLine** -> cst.EmptyLine
- **__init__**
- **leave_Module** -> cst.Module
- **__init__**
- **leave_FunctionDef** -> cst.FunctionDef


## Class: ImportTarget

**Description**: Target for import removal operations.



## Class: DocstringTarget

**Description**: Target for docstring insertion operations.



## Class: BareExceptTarget

**Description**: Target for bare except fix operations.



## Class: SurgicalImportRemover

**Description**: 
    CST transformer that removes specific imports while preserving formatting.

    Uses a string-based approach to identify and remove imports by name.
    

**Inherits from**: cst.CSTTransformer

### Methods

#### __init__
**Parameters**: self, targets
**Description**: 
        Initialize with import removal targets.

        Args:
            targets: List of imports to remove
        

#### on_visit
**Parameters**: self, node
**Returns**: bool
**Description**: Initialize line tracking.

#### leave_Import
**Parameters**: self, original_node, updated_node
**Returns**: cst.Import
**Description**: Handle Import nodes by checking if they match our targets.

#### leave_ImportFrom
**Parameters**: self, original_node, updated_node
**Returns**: cst.ImportFrom
**Description**: 
        Handle ImportFrom nodes (e.g., `from os import path`, `from x import a, b`).

        Supports both full line removal and partial name removal.
        

#### leave_SimpleStatementLine
**Parameters**: self, original_node, updated_node
**Returns**: cst.SimpleStatementLine
**Description**: 
        Handle SimpleStatementLine to remove empty import statements.

        This catches cases where we removed all names from a multi-line import
        and need to clean up the empty statement.
        



## Class: SurgicalDocstringInserter

**Description**: 
    CST transformer that inserts docstrings while preserving formatting.

    Inserts docstrings at the beginning of class or function bodies.
    Uses name-based matching since CST nodes don't have position metadata.
    

**Inherits from**: cst.CSTTransformer

### Methods

#### __init__
**Parameters**: self, targets
**Description**: 
        Initialize with docstring insertion targets.

        Args:
            targets: List of DocstringTarget objects specifying where to insert
        

#### _has_docstring
**Parameters**: self, body
**Returns**: bool
**Description**: Check if the body already has a docstring.

#### _create_docstring_stmt
**Parameters**: self, docstring
**Returns**: cst.SimpleStatementLine
**Description**: Create a docstring statement line.

#### leave_ClassDef
**Parameters**: self, original_node, updated_node
**Returns**: cst.ClassDef
**Description**: Insert docstring into class if targeted by name.

#### leave_FunctionDef
**Parameters**: self, original_node, updated_node
**Returns**: cst.FunctionDef
**Description**: Insert docstring into function if targeted by name.



## Class: SurgicalBareExceptFixer

**Description**: 
    CST transformer that fixes bare except clauses.

    Converts `except:` to `except Exception:` while preserving formatting.
    Fixes ALL bare except clauses found (no position metadata needed).
    

**Inherits from**: cst.CSTTransformer

### Methods

#### __init__
**Parameters**: self, targets, fix_all
**Description**: 
        Initialize bare except fixer.

        Args:
            targets: Optional list of specific targets (if None, fix all)
            fix_all: If True, fix all bare except clauses found
        

#### leave_ExceptHandler
**Parameters**: self, original_node, updated_node
**Returns**: cst.ExceptHandler
**Description**: Fix bare except clauses.

#### _should_fix
**Parameters**: self, node
**Returns**: bool
**Description**: Check if this node should be fixed based on targets.



## Class: SurgicalFutureImportInserter

**Description**: 
    CST transformer that inserts __future__ imports at the top of modules.

    Handles proper placement after shebang and module docstrings.
    

**Inherits from**: cst.CSTTransformer

### Methods

#### __init__
**Parameters**: self, future_imports
**Description**: 
        Initialize with future imports to add.

        Args:
            future_imports: List of future imports (e.g., ["annotations"])
        

#### visit_ImportFrom
**Parameters**: self, node
**Returns**: bool
**Description**: Check if __future__ import already exists.

#### leave_Module
**Parameters**: self, original_node, updated_node
**Returns**: cst.Module
**Description**: Insert __future__ import at the correct position in the module.



## Class: SurgicalTrailingWhitespaceFixer

**Description**: 
    CST transformer that removes trailing whitespace from lines.

    Preserves all code structure while cleaning up whitespace.
    

**Inherits from**: cst.CSTTransformer

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize the trailing whitespace fixer.

#### leave_TrailingWhitespace
**Parameters**: self, original_node, updated_node
**Returns**: cst.TrailingWhitespace
**Description**: Remove trailing whitespace before newlines.

#### leave_EmptyLine
**Parameters**: self, original_node, updated_node
**Returns**: cst.EmptyLine
**Description**: Remove trailing whitespace from empty lines.



## Class: SurgicalBlankLineNormalizer

**Description**: 
    CST transformer that normalizes excessive blank lines.

    Reduces multiple consecutive blank lines to a maximum of 2.
    

**Inherits from**: cst.CSTTransformer

### Methods

#### __init__
**Parameters**: self, max_blank_lines
**Description**: 
        Initialize the blank line normalizer.

        Args:
            max_blank_lines: Maximum allowed consecutive blank lines
        

#### leave_Module
**Parameters**: self, original_node, updated_node
**Returns**: cst.Module
**Description**: Normalize blank lines in the module body.



## Class: StructuralTarget

**Description**: Target for structural fix operations.



## Class: TypeHintTarget

**Description**: Target for type hint operations.



## Class: SurgicalTypeHintInserter

**Description**: 
    CST transformer that inserts type hints into function signatures.

    Adds return type hints and parameter type hints while preserving formatting.
    

**Inherits from**: cst.CSTTransformer

### Methods

#### __init__
**Parameters**: self, targets
**Description**: 
        Initialize with type hint targets.

        Args:
            targets: List of TypeHintTarget objects specifying hints to add
        

#### leave_FunctionDef
**Parameters**: self, original_node, updated_node
**Returns**: cst.FunctionDef
**Description**: Add type hints to function if targeted.



## Function: create_type_hint_inserter

**Parameters**: violations
**Returns**: SurgicalTypeHintInserter | None
**Description**: 
    Factory function to create type hint inserter from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalTypeHintInserter instance or None if no type hint violations
    



## Function: create_trailing_whitespace_fixer

**Parameters**: violations
**Returns**: SurgicalTrailingWhitespaceFixer | None
**Description**: 
    Factory function to create trailing whitespace fixer from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalTrailingWhitespaceFixer instance or None if no violations
    



## Function: create_blank_line_normalizer

**Parameters**: violations, max_blank_lines
**Returns**: SurgicalBlankLineNormalizer | None
**Description**: 
    Factory function to create blank line normalizer from violations.

    Args:
        violations: List of ViolationConstraint objects
        max_blank_lines: Maximum allowed consecutive blank lines

    Returns:
        SurgicalBlankLineNormalizer instance or None if no violations
    



## Function: create_import_remover

**Parameters**: violations
**Returns**: SurgicalImportRemover | None
**Description**: 
    Factory function to create import remover from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalImportRemover instance or None if no import violations
    



## Function: create_docstring_inserter

**Parameters**: violations
**Returns**: SurgicalDocstringInserter | None
**Description**: 
    Factory function to create docstring inserter from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalDocstringInserter instance or None if no docstring violations
    



## Function: create_bare_except_fixer

**Parameters**: violations
**Returns**: SurgicalBareExceptFixer | None
**Description**: 
    Factory function to create bare except fixer from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalBareExceptFixer instance or None if no bare except violations
    



## Function: create_future_import_inserter

**Parameters**: violations, future_imports
**Returns**: SurgicalFutureImportInserter | None
**Description**: 
    Factory function to create future import inserter from violations.

    Args:
        violations: List of ViolationConstraint objects
        future_imports: List of future imports to add (default: ["annotations"])

    Returns:
        SurgicalFutureImportInserter instance or None if no future import violations
    



## Function: __init__

**Parameters**: self, targets
**Description**: 
        Initialize with import removal targets.

        Args:
            targets: List of imports to remove
        



## Function: on_visit

**Parameters**: self, node
**Returns**: bool
**Description**: Initialize line tracking.



## Function: leave_Import

**Parameters**: self, original_node, updated_node
**Returns**: cst.Import
**Description**: Handle Import nodes by checking if they match our targets.



## Function: leave_ImportFrom

**Parameters**: self, original_node, updated_node
**Returns**: cst.ImportFrom
**Description**: 
        Handle ImportFrom nodes (e.g., `from os import path`, `from x import a, b`).

        Supports both full line removal and partial name removal.
        



## Function: leave_SimpleStatementLine

**Parameters**: self, original_node, updated_node
**Returns**: cst.SimpleStatementLine
**Description**: 
        Handle SimpleStatementLine to remove empty import statements.

        This catches cases where we removed all names from a multi-line import
        and need to clean up the empty statement.
        



## Function: __init__

**Parameters**: self, targets
**Description**: 
        Initialize with docstring insertion targets.

        Args:
            targets: List of DocstringTarget objects specifying where to insert
        



## Function: _has_docstring

**Parameters**: self, body
**Returns**: bool
**Description**: Check if the body already has a docstring.



## Function: _create_docstring_stmt

**Parameters**: self, docstring
**Returns**: cst.SimpleStatementLine
**Description**: Create a docstring statement line.



## Function: leave_ClassDef

**Parameters**: self, original_node, updated_node
**Returns**: cst.ClassDef
**Description**: Insert docstring into class if targeted by name.



## Function: leave_FunctionDef

**Parameters**: self, original_node, updated_node
**Returns**: cst.FunctionDef
**Description**: Insert docstring into function if targeted by name.



## Function: __init__

**Parameters**: self, targets, fix_all
**Description**: 
        Initialize bare except fixer.

        Args:
            targets: Optional list of specific targets (if None, fix all)
            fix_all: If True, fix all bare except clauses found
        



## Function: leave_ExceptHandler

**Parameters**: self, original_node, updated_node
**Returns**: cst.ExceptHandler
**Description**: Fix bare except clauses.



## Function: _should_fix

**Parameters**: self, node
**Returns**: bool
**Description**: Check if this node should be fixed based on targets.



## Function: __init__

**Parameters**: self, future_imports
**Description**: 
        Initialize with future imports to add.

        Args:
            future_imports: List of future imports (e.g., ["annotations"])
        



## Function: visit_ImportFrom

**Parameters**: self, node
**Returns**: bool
**Description**: Check if __future__ import already exists.



## Function: leave_Module

**Parameters**: self, original_node, updated_node
**Returns**: cst.Module
**Description**: Insert __future__ import at the correct position in the module.



## Function: __init__

**Parameters**: self
**Description**: Initialize the trailing whitespace fixer.



## Function: leave_TrailingWhitespace

**Parameters**: self, original_node, updated_node
**Returns**: cst.TrailingWhitespace
**Description**: Remove trailing whitespace before newlines.



## Function: leave_EmptyLine

**Parameters**: self, original_node, updated_node
**Returns**: cst.EmptyLine
**Description**: Remove trailing whitespace from empty lines.



## Function: __init__

**Parameters**: self, max_blank_lines
**Description**: 
        Initialize the blank line normalizer.

        Args:
            max_blank_lines: Maximum allowed consecutive blank lines
        



## Function: leave_Module

**Parameters**: self, original_node, updated_node
**Returns**: cst.Module
**Description**: Normalize blank lines in the module body.



## Function: __init__

**Parameters**: self, targets
**Description**: 
        Initialize with type hint targets.

        Args:
            targets: List of TypeHintTarget objects specifying hints to add
        



## Function: leave_FunctionDef

**Parameters**: self, original_node, updated_node
**Returns**: cst.FunctionDef
**Description**: Add type hints to function if targeted.



## Usage Examples

### Class Usage

```python
# Using ImportTarget
importtarget = ImportTarget()
```

```python
# Using DocstringTarget
docstringtarget = DocstringTarget()
```

```python
# Using BareExceptTarget
bareexcepttarget = BareExceptTarget()
```

### Function Usage

```python
# Using create_type_hint_inserter
result = create_type_hint_inserter(violations)
```

```python
# Using create_trailing_whitespace_fixer
result = create_trailing_whitespace_fixer(violations)
```

```python
# Using create_blank_line_normalizer
result = create_blank_line_normalizer(violations, max_blank_lines)
```



---
**Generated**: 2026-03-26T09:39:05.502177
**Type**: api_reference
**Quality**: comprehensive
