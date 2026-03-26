# API Documentation: HygieneGuardianAgent

**Target Audience**: developers, api_users

# HygieneGuardianAgent API Documentation

**File**: `HygieneGuardianAgent.py`
**Classes**: 2
**Functions**: 14

## Classes

- **HygieneViolation**
- **HygieneGuardianAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__**
- **heal** -> dict[str, Any]
- **_is_empty_file** -> bool
- **_is_orphaned_init** -> bool
- **_has_debug_prints** -> list[int]
- **_has_commented_code** -> tuple[bool, int]
- **_has_repeated_filename_parts** -> tuple[bool, str | None]
- **_is_copy_pattern_filename** -> tuple[bool, str | None]
- **_scan_directory** -> None
- **_fix_violations** -> int
- **heal_repository** -> dict[str, Any]
- **audit_naming_conventions** -> list[dict]
- **_check_filename_length**
- **_generate_concise_suggestion** -> str


## Class: HygieneViolation

**Description**: Structured violation for hygiene issues.



## Class: HygieneGuardianAgent

**Description**: 
    Repository hygiene enforcement agent.

    Detects and optionally fixes:
    - Empty files (0 bytes or only whitespace)
    - Orphaned __init__.py files (in directories with no other Python files)
    - Stale backup files (.bak, .orig, .backup)
    - Temporary files (.tmp, .temp, ~)
    - Debug print statements
    - Large blocks of commented-out code
    - Repeated filename strings (e.g., 'enums_enums_enums') [Merged from FileCleanupAgent]
    - Copy-pattern filenames (e.g., 'Copy of file.py', 'file (1).py')

    Uses ArchivalGatekeeper for all destructive operations (safe deletion).

    Inherits:
        SubatomicTestingMixin: Testing utilities
        HealerMixin: Healing chain support
        MCPHardenedMixin: MCP integration
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root, ctx, dry_run
**Description**: 
        Initialize the hygiene guardian.

        Args:
            project_root: Root directory of the project
            ctx: Execution context (optional)
            dry_run: If True, only report violations without fixing
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for HygieneGuardianAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        

#### _is_empty_file
**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if file is empty or contains only whitespace.

#### _is_orphaned_init
**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if __init__.py is orphaned (no other Python files in directory).

#### _has_debug_prints
**Parameters**: self, file_path
**Returns**: list[int]
**Description**: Detect debug print statements and return line numbers.

#### _has_commented_code
**Parameters**: self, file_path
**Returns**: tuple[bool, int]
**Description**: 
        Detect large blocks of commented-out code.

        Returns:
            (has_commented_code, num_lines)
        

#### _has_repeated_filename_parts
**Parameters**: self, filename
**Returns**: tuple[bool, str | None]
**Description**: 
        Check if filename has repeated consecutive strings (merged from FileCleanupAgent).

        Args:
            filename: Filename to check (without extension)

        Returns:
            Tuple of (has_repeats, repeated_pattern) or (False, None)

        Examples:
            'enums_enums' -> (True, 'enums')
            'impl_impl_impl' -> (True, 'impl')
            'data_models_enums_enums' -> (True, 'enums')
            'test_data' -> (False, None)
        

#### _is_copy_pattern_filename
**Parameters**: self, filename
**Returns**: tuple[bool, str | None]
**Description**: 
        Check if filename matches copy patterns.

        Args:
            filename: Filename to check (without extension)

        Returns:
            Tuple of (is_copy, original_name) or (False, None)

        Examples:
            'Copy of report' -> (True, 'report')
            'report (1)' -> (True, 'report')
            'report_copy2' -> (True, 'report')
        

#### _scan_directory
**Parameters**: self, directory
**Returns**: None
**Description**: Recursively scan directory for hygiene violations.

#### _fix_violations
**Parameters**: self
**Returns**: int
**Description**: 
        Attempt to auto-fix violations where possible.

        Uses ArchivalGatekeeper for all destructive operations (safe deletion).

        Returns:
            Number of violations fixed
        

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method for repository hygiene.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, execute fixes (overrides dry_run)
            **kwargs: Additional arguments

        Returns:
            Dictionary with healing results
        

#### audit_naming_conventions
**Parameters**: self
**Returns**: list[dict]
**Description**: 
        Performs a deep audit of the repository's naming conventions,
        enforcing word-count limits and semantic density.
        

#### _check_filename_length
**Parameters**: self, path
**Description**: 
        Checks for 'Semantic Bloat' where filenames exceed the word limit.
        Enhanced with CamelCase splitting and mixed delimiter handling.
        Example Violation: logic_synthesis_pick_best_refinement_refine_scripts_ranking.py
        

#### _generate_concise_suggestion
**Parameters**: self, words, ext
**Returns**: str
**Description**: Proposes a concise alternative using semantic anchors and redundant term removal.



## Function: __init__

**Parameters**: self, project_root, ctx, dry_run
**Description**: 
        Initialize the hygiene guardian.

        Args:
            project_root: Root directory of the project
            ctx: Execution context (optional)
            dry_run: If True, only report violations without fixing
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for HygieneGuardianAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        



## Function: _is_empty_file

**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if file is empty or contains only whitespace.



## Function: _is_orphaned_init

**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if __init__.py is orphaned (no other Python files in directory).



## Function: _has_debug_prints

**Parameters**: self, file_path
**Returns**: list[int]
**Description**: Detect debug print statements and return line numbers.



## Function: _has_commented_code

**Parameters**: self, file_path
**Returns**: tuple[bool, int]
**Description**: 
        Detect large blocks of commented-out code.

        Returns:
            (has_commented_code, num_lines)
        



## Function: _has_repeated_filename_parts

**Parameters**: self, filename
**Returns**: tuple[bool, str | None]
**Description**: 
        Check if filename has repeated consecutive strings (merged from FileCleanupAgent).

        Args:
            filename: Filename to check (without extension)

        Returns:
            Tuple of (has_repeats, repeated_pattern) or (False, None)

        Examples:
            'enums_enums' -> (True, 'enums')
            'impl_impl_impl' -> (True, 'impl')
            'data_models_enums_enums' -> (True, 'enums')
            'test_data' -> (False, None)
        



## Function: _is_copy_pattern_filename

**Parameters**: self, filename
**Returns**: tuple[bool, str | None]
**Description**: 
        Check if filename matches copy patterns.

        Args:
            filename: Filename to check (without extension)

        Returns:
            Tuple of (is_copy, original_name) or (False, None)

        Examples:
            'Copy of report' -> (True, 'report')
            'report (1)' -> (True, 'report')
            'report_copy2' -> (True, 'report')
        



## Function: _scan_directory

**Parameters**: self, directory
**Returns**: None
**Description**: Recursively scan directory for hygiene violations.



## Function: _fix_violations

**Parameters**: self
**Returns**: int
**Description**: 
        Attempt to auto-fix violations where possible.

        Uses ArchivalGatekeeper for all destructive operations (safe deletion).

        Returns:
            Number of violations fixed
        



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method for repository hygiene.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, execute fixes (overrides dry_run)
            **kwargs: Additional arguments

        Returns:
            Dictionary with healing results
        



## Function: audit_naming_conventions

**Parameters**: self
**Returns**: list[dict]
**Description**: 
        Performs a deep audit of the repository's naming conventions,
        enforcing word-count limits and semantic density.
        



## Function: _check_filename_length

**Parameters**: self, path
**Description**: 
        Checks for 'Semantic Bloat' where filenames exceed the word limit.
        Enhanced with CamelCase splitting and mixed delimiter handling.
        Example Violation: logic_synthesis_pick_best_refinement_refine_scripts_ranking.py
        



## Function: _generate_concise_suggestion

**Parameters**: self, words, ext
**Returns**: str
**Description**: Proposes a concise alternative using semantic anchors and redundant term removal.



## Usage Examples

### Class Usage

```python
# Using HygieneViolation
hygieneviolation = HygieneViolation()
```

```python
# Using HygieneGuardianAgent
hygieneguardianagent = HygieneGuardianAgent()
hygieneguardianagent.heal()
hygieneguardianagent.heal_repository()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root, ctx)
```

```python
# Using heal
result = heal(violation)
```

```python
# Using _is_empty_file
result = _is_empty_file(file_path)
```



---
**Generated**: 2026-03-26T09:39:05.275029
**Type**: api_reference
**Quality**: comprehensive
