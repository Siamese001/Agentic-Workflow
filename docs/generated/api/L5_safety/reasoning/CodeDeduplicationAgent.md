# API Documentation: CodeDeduplicationAgent

**Target Audience**: developers, api_users

# CodeDeduplicationAgent API Documentation

**File**: `CodeDeduplicationAgent.py`
**Classes**: 1
**Functions**: 25

## Classes

- **CodeDeduplicationAgent** (inherits from SovereignBaseAgent)

## Functions

- **get_code_deduplication_agent** -> Any
- **__init__** -> None
- **heal** -> dict[str, Any]
- **_run_self_tests** -> bool
- **_normalize_code** -> str
- **_filter_code_lines** -> list[str]
- **_normalize_ast_tree** -> str
- **_normalize_ts_tree** -> str
- **_block_similarity** -> float
- **_hash_block** -> str
- **_extract_functions_classes** -> list[tuple[str, str, int]]
- **scan_for_duplicates** -> Any
- **_create_shared_utility** -> Path
- **_hash_entire_file** -> str | None
- **scan_file_level_duplicates** -> None
- **scan_filename_duplicates** -> None
- **_suggest_unique_name** -> Path
- **_get_target_dir_from_content** -> Path
- **_get_unique_path** -> Path
- **resolve_duplicates_safely** -> None
- **heal_repository** -> dict[str, int]
- **_collect_ast_symbols** -> tuple
- **detect_dead_code** -> dict[str, Any]
- **scan_dead_code** -> dict[str, Any]
- **prune_dead_code** -> dict[str, Any]


## Class: CodeDeduplicationAgent

**Description**: 
    Batch agent for detecting and optionally refactoring duplicated code.

    HARDENED CONFIGURATION (2026-01-07):
    - Default threshold: 1.0 (100% structural identity required)
    - Aggressive purge mode: Filename duplicates consolidated to SSOT regardless of content divergence
    - Prevents Logic Bleed by enforcing absolute identity

    HARDENED: Redis caching + Pinecone vector support for semantic fingerprinting.

    Responsibilities:
    - Computes perceptual hashes of normalized AST nodes
    - Groups duplicates with 100% structural identity (threshold=THRESHOLD)
    - Reports redundancy to the L4 Ledger for audit tracking
    - [SURGERY] When RUN_SPRAWL_SURGERY=True: Extracts duplicates to shared utils
    - Whole-file duplicate detection and aggressive consolidation
    - Filename uniqueness enforcement (AGGRESSIVE: all duplicates → SSOT, no rename fallback)
    - Dead-code pruning with empty-file auto-deletion

    Consolidates functionality from deprecated FilenameUniquenessGuardianAgent (2025-12-31).
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, similarity_threshold, min_lines
**Returns**: None
**Description**: 
        HARDENED: 100% identity by default to prevent Logic Bleed.
        Enforces absolute structural identity for SSOT compliance.

        Args:
            similarity_threshold: Default 1.0 (100% identity required)
            min_lines: Minimum lines for duplicate detection
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for code deduplication violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L2 compliance.

#### _normalize_code
**Parameters**: code
**Returns**: str
**Description**: Normalize for hashing: dedent, collapse whitespace, strip comments.

#### _filter_code_lines
**Parameters**: code
**Returns**: list[str]
**Description**: Filter code lines by removing comments and empty lines.

#### _normalize_ast_tree
**Parameters**: self, node
**Returns**: str
**Description**: Anonymize variables and constants in AST for structural comparison.

#### _normalize_ts_tree
**Parameters**: self, node
**Returns**: str
**Description**: Normalize tree-sitter node for structural comparison.

#### _block_similarity
**Parameters**: self, norm_a, norm_b
**Returns**: float
**Description**: Conservative structural/text similarity using difflib (built-in, no deps).

#### _hash_block
**Parameters**: self, code
**Returns**: str
**Description**: Generate AST fingerprint for code block.

#### _extract_functions_classes
**Parameters**: self, file_path
**Returns**: list[tuple[str, str, int]]
**Description**: Parse file and extract function/class bodies.

#### scan_for_duplicates
**Parameters**: self, python_files
**Returns**: Any
**Description**: Phase 2 entry point - cross-file territory sweep.

#### _create_shared_utility
**Parameters**: self, code, func_name, project_root
**Returns**: Path
**Description**: Create deduplicated utility in sovereign shared location.

#### _hash_entire_file
**Parameters**: self, file_path
**Returns**: str | None
**Description**: SHA256 of normalized entire file (dedent, strip comments, collapse whitespace).

#### scan_file_level_duplicates
**Parameters**: self, python_files
**Returns**: None
**Description**: Detect exact whole-file duplicates (identical content).

#### scan_filename_duplicates
**Parameters**: self, python_files, project_root
**Returns**: None
**Description**: Detect duplicate basenames with safety check (identical vs divergent content).

        Enhanced with intelligent suffix pattern detection to catch all common duplicate
        suffixes: _flat, _1, _2, _from_utils, _copy, etc.
        

#### _suggest_unique_name
**Parameters**: self, file_path, project_root
**Returns**: Path
**Description**: Primary: NamingAgent if available; Fallback: content heuristics.

#### _get_target_dir_from_content
**Parameters**: self, preview, project_root
**Returns**: Path
**Description**: Determine target directory from content keywords using lookup table.

#### _get_unique_path
**Parameters**: self, target_dir, file_path
**Returns**: Path
**Description**: Generate unique path with collision handling.

#### resolve_duplicates_safely
**Parameters**: self, project_root, dry_run
**Returns**: None
**Description**: Central resolution: identical files → consolidate; divergent filenames → rename.

        [BATCH 1 REMEDIATION] Respects SOVEREIGN_AUTO_APPROVE for automated healing.
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Scan repository for code duplication and report findings.

        Detects duplicated code blocks, whole-file duplicates, and filename
        collisions. Deduplication requires batch processing and manual review.

        Args:
            dry_run: If True, only report duplicates (default: True).
            execute: If True, generate deduplication report.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        

#### _collect_ast_symbols
**Parameters**: self, tree
**Returns**: tuple
**Description**: Collect imports, definitions, and usages from AST.

#### detect_dead_code
**Parameters**: self, file_path
**Returns**: dict[str, Any]
**Description**: Analyze a single Python file for dead code.

#### scan_dead_code
**Parameters**: self, directory, recursive
**Returns**: dict[str, Any]
**Description**: 
        SUPPLEMENTED FROM DeadCodeDetectorAgent — merged 2025-12-30

        Scan an entire directory for dead code.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively

        Returns:
            Dict with scan results and summary
        

#### prune_dead_code
**Parameters**: self, file_path, dry_run
**Returns**: dict[str, Any]
**Description**: 
        SUPPLEMENTED FROM DeadCodePrunerAgent — merged 2025-12-30

        Remove detected dead code from a file.

        Args:
            file_path: Path to the file to prune
            dry_run: If True, only report what would be removed

        Returns:
            Dict with pruning results
        



## Function: get_code_deduplication_agent

**Returns**: Any
**Description**: Brief description of functionality and purpose.



## Function: __init__

**Parameters**: self, similarity_threshold, min_lines
**Returns**: None
**Description**: 
        HARDENED: 100% identity by default to prevent Logic Bleed.
        Enforces absolute structural identity for SSOT compliance.

        Args:
            similarity_threshold: Default 1.0 (100% identity required)
            min_lines: Minimum lines for duplicate detection
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for code deduplication violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L2 compliance.



## Function: _normalize_code

**Parameters**: code
**Returns**: str
**Description**: Normalize for hashing: dedent, collapse whitespace, strip comments.



## Function: _filter_code_lines

**Parameters**: code
**Returns**: list[str]
**Description**: Filter code lines by removing comments and empty lines.



## Function: _normalize_ast_tree

**Parameters**: self, node
**Returns**: str
**Description**: Anonymize variables and constants in AST for structural comparison.



## Function: _normalize_ts_tree

**Parameters**: self, node
**Returns**: str
**Description**: Normalize tree-sitter node for structural comparison.



## Function: _block_similarity

**Parameters**: self, norm_a, norm_b
**Returns**: float
**Description**: Conservative structural/text similarity using difflib (built-in, no deps).



## Function: _hash_block

**Parameters**: self, code
**Returns**: str
**Description**: Generate AST fingerprint for code block.



## Function: _extract_functions_classes

**Parameters**: self, file_path
**Returns**: list[tuple[str, str, int]]
**Description**: Parse file and extract function/class bodies.



## Function: scan_for_duplicates

**Parameters**: self, python_files
**Returns**: Any
**Description**: Phase 2 entry point - cross-file territory sweep.



## Function: _create_shared_utility

**Parameters**: self, code, func_name, project_root
**Returns**: Path
**Description**: Create deduplicated utility in sovereign shared location.



## Function: _hash_entire_file

**Parameters**: self, file_path
**Returns**: str | None
**Description**: SHA256 of normalized entire file (dedent, strip comments, collapse whitespace).



## Function: scan_file_level_duplicates

**Parameters**: self, python_files
**Returns**: None
**Description**: Detect exact whole-file duplicates (identical content).



## Function: scan_filename_duplicates

**Parameters**: self, python_files, project_root
**Returns**: None
**Description**: Detect duplicate basenames with safety check (identical vs divergent content).

        Enhanced with intelligent suffix pattern detection to catch all common duplicate
        suffixes: _flat, _1, _2, _from_utils, _copy, etc.
        



## Function: _suggest_unique_name

**Parameters**: self, file_path, project_root
**Returns**: Path
**Description**: Primary: NamingAgent if available; Fallback: content heuristics.



## Function: _get_target_dir_from_content

**Parameters**: self, preview, project_root
**Returns**: Path
**Description**: Determine target directory from content keywords using lookup table.



## Function: _get_unique_path

**Parameters**: self, target_dir, file_path
**Returns**: Path
**Description**: Generate unique path with collision handling.



## Function: resolve_duplicates_safely

**Parameters**: self, project_root, dry_run
**Returns**: None
**Description**: Central resolution: identical files → consolidate; divergent filenames → rename.

        [BATCH 1 REMEDIATION] Respects SOVEREIGN_AUTO_APPROVE for automated healing.
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Scan repository for code duplication and report findings.

        Detects duplicated code blocks, whole-file duplicates, and filename
        collisions. Deduplication requires batch processing and manual review.

        Args:
            dry_run: If True, only report duplicates (default: True).
            execute: If True, generate deduplication report.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        



## Function: _collect_ast_symbols

**Parameters**: self, tree
**Returns**: tuple
**Description**: Collect imports, definitions, and usages from AST.



## Function: detect_dead_code

**Parameters**: self, file_path
**Returns**: dict[str, Any]
**Description**: Analyze a single Python file for dead code.



## Function: scan_dead_code

**Parameters**: self, directory, recursive
**Returns**: dict[str, Any]
**Description**: 
        SUPPLEMENTED FROM DeadCodeDetectorAgent — merged 2025-12-30

        Scan an entire directory for dead code.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively

        Returns:
            Dict with scan results and summary
        



## Function: prune_dead_code

**Parameters**: self, file_path, dry_run
**Returns**: dict[str, Any]
**Description**: 
        SUPPLEMENTED FROM DeadCodePrunerAgent — merged 2025-12-30

        Remove detected dead code from a file.

        Args:
            file_path: Path to the file to prune
            dry_run: If True, only report what would be removed

        Returns:
            Dict with pruning results
        



## Usage Examples

### Class Usage

```python
# Using CodeDeduplicationAgent
codededuplicationagent = CodeDeduplicationAgent()
codededuplicationagent.heal()
codededuplicationagent.scan_for_duplicates()
```

### Function Usage

```python
# Using get_code_deduplication_agent
result = get_code_deduplication_agent()
```

```python
# Using __init__
result = __init__(similarity_threshold, min_lines)
```

```python
# Using heal
result = heal(violation)
```



---
**Generated**: 2026-03-26T09:39:05.073095
**Type**: api_reference
**Quality**: comprehensive
