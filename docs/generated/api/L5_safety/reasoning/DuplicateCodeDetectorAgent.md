# API Documentation: DuplicateCodeDetectorAgent

**Target Audience**: developers, api_users

# DuplicateCodeDetectorAgent API Documentation

**File**: `DuplicateCodeDetectorAgent.py`
**Classes**: 5
**Functions**: 16

## Classes

- **DuplicateFile**
- **DuplicateCodeDetectorAgent** (inherits from AtomicExecutionMixin, SubatomicTestingMixin, HealerMixin, MCPHardenedMixin)
- **SubatomicTestingMixin**
- **HealerMixin**
- **MCPHardenedMixin**

## Functions

- **__post_init__**
- **__init__** -> None
- **_scan_whole_files** -> list[DuplicateFile]
- **_iter_files** -> Any
- **_generate_deletion_plan** -> list[dict]
- **_choose_canonical_path** -> Path
- **_generate_rationale** -> str
- **archive_duplicates** -> dict
- **delete_duplicates** -> dict
- **_hash_block_ast** -> str
- **_normalize_ast_tree** -> str
- **_normalize_ts_tree** -> str
- **heal_repository** -> dict[str, int]
- **heal**
- **timeout**
- **decorator**


## Class: DuplicateFile

**Description**: Represents a duplicate file with metadata.



## Class: DuplicateCodeDetectorAgent

**Description**: L5 Safety agent that detects duplicate files and code blocks.

    This batch agent detects exact duplicate files and code blocks across the
    entire territory using content hashing and AST fingerprinting.

    Attributes:
        project_root: Root directory of the project.
        ctx: Execution context.
        min_lines: Minimum block size to flag as duplicate.
        max_report: Maximum number of duplicates to report.

    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
        MCPHardenedMixin: Provides MCP hardening and telemetry.
    

**Inherits from**: AtomicExecutionMixin, SubatomicTestingMixin, HealerMixin, MCPHardenedMixin

### Methods

#### __post_init__
**Parameters**: self
**Description**: Initialize mixins after dataclass initialization.

#### __init__
**Parameters**: self, project_root, ctx
**Returns**: None
**Description**: 
        Initialize duplicate code detector.

        Args:
            project_root: Optional project root directory
            ctx: Optional validation context
        

#### _scan_whole_files
**Parameters**: self, file_types
**Returns**: list[DuplicateFile]
**Description**: Scan for exact duplicate files by content hash.

#### _iter_files
**Parameters**: self, file_types
**Returns**: Any
**Description**: Iterate over files matching the given extensions.

#### _generate_deletion_plan
**Parameters**: self, duplicates
**Returns**: list[dict]
**Description**: Generate deletion recommendations with rationale.

#### _choose_canonical_path
**Parameters**: self, paths
**Returns**: Path
**Description**: Choose the canonical path to keep based on location priority.

#### _generate_rationale
**Parameters**: self, keep_path, delete_paths, dup
**Returns**: str
**Description**: Generate human-readable rationale for deletion.

#### archive_duplicates
**Parameters**: self, recommendations, dry_run
**Returns**: dict
**Description**: Archive duplicate files to archives/ directory (Phase 2.2).

        Args:
            recommendations: List of deletion recommendations from execute()
            dry_run: If True, only simulate archiving

        Returns:
            Dict with archiving results
        

#### delete_duplicates
**Parameters**: self, recommendations, dry_run
**Returns**: dict
**Description**: Delete duplicate files based on recommendations.

        Args:
            recommendations: List of deletion recommendations from execute()
            dry_run: If True, only simulate deletion

        Returns:
            Dict with deletion results
        

#### _hash_block_ast
**Parameters**: self, code
**Returns**: str
**Description**: Generate AST fingerprint for code block.

#### _normalize_ast_tree
**Parameters**: self, node
**Returns**: str
**Description**: Anonymize variables and constants in AST for structural comparison.

#### _normalize_ts_tree
**Parameters**: self, node
**Returns**: str
**Description**: Normalize tree-sitter node for structural comparison.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        

#### heal
**Parameters**: self, violation



## Class: SubatomicTestingMixin



## Class: HealerMixin



## Class: MCPHardenedMixin



## Function: __post_init__

**Parameters**: self
**Description**: Initialize mixins after dataclass initialization.



## Function: __init__

**Parameters**: self, project_root, ctx
**Returns**: None
**Description**: 
        Initialize duplicate code detector.

        Args:
            project_root: Optional project root directory
            ctx: Optional validation context
        



## Function: _scan_whole_files

**Parameters**: self, file_types
**Returns**: list[DuplicateFile]
**Description**: Scan for exact duplicate files by content hash.



## Function: _iter_files

**Parameters**: self, file_types
**Returns**: Any
**Description**: Iterate over files matching the given extensions.



## Function: _generate_deletion_plan

**Parameters**: self, duplicates
**Returns**: list[dict]
**Description**: Generate deletion recommendations with rationale.



## Function: _choose_canonical_path

**Parameters**: self, paths
**Returns**: Path
**Description**: Choose the canonical path to keep based on location priority.



## Function: _generate_rationale

**Parameters**: self, keep_path, delete_paths, dup
**Returns**: str
**Description**: Generate human-readable rationale for deletion.



## Function: archive_duplicates

**Parameters**: self, recommendations, dry_run
**Returns**: dict
**Description**: Archive duplicate files to archives/ directory (Phase 2.2).

        Args:
            recommendations: List of deletion recommendations from execute()
            dry_run: If True, only simulate archiving

        Returns:
            Dict with archiving results
        



## Function: delete_duplicates

**Parameters**: self, recommendations, dry_run
**Returns**: dict
**Description**: Delete duplicate files based on recommendations.

        Args:
            recommendations: List of deletion recommendations from execute()
            dry_run: If True, only simulate deletion

        Returns:
            Dict with deletion results
        



## Function: _hash_block_ast

**Parameters**: self, code
**Returns**: str
**Description**: Generate AST fingerprint for code block.



## Function: _normalize_ast_tree

**Parameters**: self, node
**Returns**: str
**Description**: Anonymize variables and constants in AST for structural comparison.



## Function: _normalize_ts_tree

**Parameters**: self, node
**Returns**: str
**Description**: Normalize tree-sitter node for structural comparison.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        



## Function: heal

**Parameters**: self, violation


## Function: timeout

**Parameters**: seconds


## Function: decorator

**Parameters**: func


## Usage Examples

### Class Usage

```python
# Using DuplicateFile
duplicatefile = DuplicateFile()
```

```python
# Using DuplicateCodeDetectorAgent
duplicatecodedetectoragent = DuplicateCodeDetectorAgent()
duplicatecodedetectoragent.archive_duplicates()
duplicatecodedetectoragent.delete_duplicates()
```

```python
# Using SubatomicTestingMixin
subatomictestingmixin = SubatomicTestingMixin()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __init__
result = __init__(project_root, ctx)
```

```python
# Using _scan_whole_files
result = _scan_whole_files(file_types)
```



---
**Generated**: 2026-03-26T09:39:05.131862
**Type**: api_reference
**Quality**: comprehensive
