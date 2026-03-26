# API Documentation: SSOTFolderCleanupAgent

**Target Audience**: developers, api_users

# SSOTFolderCleanupAgent API Documentation

**File**: `SSOTFolderCleanupAgent.py`
**Classes**: 1
**Functions**: 19

## Classes

- **SSOTFolderCleanupAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__**
- **_detect_project_root** -> Path
- **_load_ssot_config** -> None
- **_build_approved_paths** -> None
- **_get_cognitive_agent**
- **_get_archival_gatekeeper**
- **is_path_ssot_approved** -> bool
- **find_non_approved_files** -> list[Path]
- **triage_file** -> dict[str, Any]
- **move_file_to_ssot** -> bool
- **update_imports_for_moved_file** -> int
- **_path_to_module** -> str | None
- **_update_imports_in_content** -> str
- **delete_empty_folders** -> int
- **cleanup_repository** -> dict[str, Any]
- **preview_cleanup** -> dict[str, Any]
- **execute_cleanup** -> dict[str, Any]
- **heal_repository** -> dict[str, Any]
- **heal** -> dict


## Class: SSOTFolderCleanupAgent

**Description**: 
    [PHASE 24] Automated SSOT Folder Cleanup Agent.

    Responsibilities:
    1. Scan for files in non-SSOT-approved folders
    2. Triage files using CognitiveDispositionAgent
    3. Move files to SSOT-approved locations via ArchivalGatekeeper
    4. Update all imports referencing moved files
    5. Delete empty non-approved folders

    Safety Features:
    - All moves go through ArchivalGatekeeper (audited)
    - Dry-run mode for preview
    - Import updates are AST-based (safe)
    - Empty folder deletion is recursive-safe
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root, dry_run
**Description**: 
        Initialize the SSOT Folder Cleanup Agent.

        Args:
            project_root: Root of the project (auto-detected if None)
            dry_run: If True, only report actions without executing
        

#### _detect_project_root
**Parameters**: self
**Returns**: Path
**Description**: Detect project root by looking for pyproject.toml or .git.

#### _load_ssot_config
**Parameters**: self
**Returns**: None
**Description**: Load SSOT configuration from L0 config.

#### _build_approved_paths
**Parameters**: self
**Returns**: None
**Description**: Build the complete set of SSOT-approved paths.

#### _get_cognitive_agent
**Parameters**: self
**Description**: Lazy-load CognitiveDispositionAgent.

#### _get_archival_gatekeeper
**Parameters**: self
**Description**: Lazy-load ArchivalGatekeeper.

#### is_path_ssot_approved
**Parameters**: self, path
**Returns**: bool
**Description**: 
        Check if a path is in an SSOT-approved location.

        A path is approved if:
        1. It's directly in an approved subfolder (e.g., agentic_core/L5_safety/validators)
        2. It's a file directly in a layer folder (e.g., agentic_core/L5_safety/__init__.py)

        A path is NOT approved if:
        1. It's in a subfolder that's not in CORE_SUBFOLDER_MAP

        Args:
            path: Path to check (relative to project root)

        Returns:
            True if path is in an approved location
        

#### find_non_approved_files
**Parameters**: self
**Returns**: list[Path]
**Description**: 
        Find all Python files in non-SSOT-approved folders.

        Returns:
            List of file paths that need to be moved
        

#### triage_file
**Parameters**: self, file_path
**Returns**: dict[str, Any]
**Description**: 
        Determine where a file should go using FCA classification + CognitiveDispositionAgent.

        [DEDUP 2026-02-07] Uses FCA's classify_file() as primary routing source.
        Falls back to CognitiveDispositionAgent for files FCA can't classify confidently.

        Args:
            file_path: Path to the file to triage

        Returns:
            Dictionary with action, target_path, reason, confidence
        

#### move_file_to_ssot
**Parameters**: self, source_path, target_path
**Returns**: bool
**Description**: 
        Move a file to its SSOT-approved location.

        Args:
            source_path: Current file path
            target_path: Target SSOT path (relative)

        Returns:
            True if move succeeded
        

#### update_imports_for_moved_file
**Parameters**: self, old_path, new_path
**Returns**: int
**Description**: 
        Update all imports referencing a moved file.

        Args:
            old_path: Original file path
            new_path: New file path

        Returns:
            Number of files updated
        

#### _path_to_module
**Parameters**: self, path
**Returns**: str | None
**Description**: Convert a file path to a Python module name.

#### _update_imports_in_content
**Parameters**: self, content, old_module, new_module
**Returns**: str
**Description**: 
        Update import statements using AST-guided Regex.

        Uses AST to identify lines containing imports, then applies Regex
        ONLY to those lines to preserve formatting while ensuring safety.
        

#### delete_empty_folders
**Parameters**: self, start_path
**Returns**: int
**Description**: 
        Delete empty non-SSOT-approved folders.

        Args:
            start_path: Starting path for deletion (default: agentic_core)

        Returns:
            Number of folders deleted
        

#### cleanup_repository
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Execute full SSOT folder cleanup.

        Returns:
            Summary of cleanup operations
        

#### preview_cleanup
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Preview cleanup without making changes.

        Returns:
            Preview of what would be changed
        

#### execute_cleanup
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Execute cleanup with actual file changes.

        Returns:
            Summary of changes made
        

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal SSOT folder violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (orphan, misplaced)
                - path: Path to the violating file
                - target_path: Suggested target path

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: __init__

**Parameters**: self, project_root, dry_run
**Description**: 
        Initialize the SSOT Folder Cleanup Agent.

        Args:
            project_root: Root of the project (auto-detected if None)
            dry_run: If True, only report actions without executing
        



## Function: _detect_project_root

**Parameters**: self
**Returns**: Path
**Description**: Detect project root by looking for pyproject.toml or .git.



## Function: _load_ssot_config

**Parameters**: self
**Returns**: None
**Description**: Load SSOT configuration from L0 config.



## Function: _build_approved_paths

**Parameters**: self
**Returns**: None
**Description**: Build the complete set of SSOT-approved paths.



## Function: _get_cognitive_agent

**Parameters**: self
**Description**: Lazy-load CognitiveDispositionAgent.



## Function: _get_archival_gatekeeper

**Parameters**: self
**Description**: Lazy-load ArchivalGatekeeper.



## Function: is_path_ssot_approved

**Parameters**: self, path
**Returns**: bool
**Description**: 
        Check if a path is in an SSOT-approved location.

        A path is approved if:
        1. It's directly in an approved subfolder (e.g., agentic_core/L5_safety/validators)
        2. It's a file directly in a layer folder (e.g., agentic_core/L5_safety/__init__.py)

        A path is NOT approved if:
        1. It's in a subfolder that's not in CORE_SUBFOLDER_MAP

        Args:
            path: Path to check (relative to project root)

        Returns:
            True if path is in an approved location
        



## Function: find_non_approved_files

**Parameters**: self
**Returns**: list[Path]
**Description**: 
        Find all Python files in non-SSOT-approved folders.

        Returns:
            List of file paths that need to be moved
        



## Function: triage_file

**Parameters**: self, file_path
**Returns**: dict[str, Any]
**Description**: 
        Determine where a file should go using FCA classification + CognitiveDispositionAgent.

        [DEDUP 2026-02-07] Uses FCA's classify_file() as primary routing source.
        Falls back to CognitiveDispositionAgent for files FCA can't classify confidently.

        Args:
            file_path: Path to the file to triage

        Returns:
            Dictionary with action, target_path, reason, confidence
        



## Function: move_file_to_ssot

**Parameters**: self, source_path, target_path
**Returns**: bool
**Description**: 
        Move a file to its SSOT-approved location.

        Args:
            source_path: Current file path
            target_path: Target SSOT path (relative)

        Returns:
            True if move succeeded
        



## Function: update_imports_for_moved_file

**Parameters**: self, old_path, new_path
**Returns**: int
**Description**: 
        Update all imports referencing a moved file.

        Args:
            old_path: Original file path
            new_path: New file path

        Returns:
            Number of files updated
        



## Function: _path_to_module

**Parameters**: self, path
**Returns**: str | None
**Description**: Convert a file path to a Python module name.



## Function: _update_imports_in_content

**Parameters**: self, content, old_module, new_module
**Returns**: str
**Description**: 
        Update import statements using AST-guided Regex.

        Uses AST to identify lines containing imports, then applies Regex
        ONLY to those lines to preserve formatting while ensuring safety.
        



## Function: delete_empty_folders

**Parameters**: self, start_path
**Returns**: int
**Description**: 
        Delete empty non-SSOT-approved folders.

        Args:
            start_path: Starting path for deletion (default: agentic_core)

        Returns:
            Number of folders deleted
        



## Function: cleanup_repository

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Execute full SSOT folder cleanup.

        Returns:
            Summary of cleanup operations
        



## Function: preview_cleanup

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Preview cleanup without making changes.

        Returns:
            Preview of what would be changed
        



## Function: execute_cleanup

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Execute cleanup with actual file changes.

        Returns:
            Summary of changes made
        



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal SSOT folder violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (orphan, misplaced)
                - path: Path to the violating file
                - target_path: Suggested target path

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using SSOTFolderCleanupAgent
ssotfoldercleanupagent = SSOTFolderCleanupAgent()
ssotfoldercleanupagent.is_path_ssot_approved()
ssotfoldercleanupagent.find_non_approved_files()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root, dry_run)
```

```python
# Using _detect_project_root
result = _detect_project_root()
```

```python
# Using _load_ssot_config
result = _load_ssot_config()
```



---
**Generated**: 2026-03-26T09:39:02.721384
**Type**: api_reference
**Quality**: comprehensive
