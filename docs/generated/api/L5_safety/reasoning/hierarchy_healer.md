# API Documentation: hierarchy_healer

**Target Audience**: developers, api_users

# hierarchy_healer API Documentation

**File**: `hierarchy_healer.py`
**Classes**: 1
**Functions**: 35

## Classes

- **HierarchyHealerAgent** (inherits from SovereignBaseAgent)

## Functions

- **get_hierarchy_agent**
- **__init__** -> None
- **heal** -> dict[str, Any]
- **create_missing_structure** -> dict[str, Any]
- **_create_agentic_core_structure** -> None
- **_create_territory_structure** -> None
- **_create_dir_with_init** -> None
- **relocate_misplaced_files** -> dict[str, Any]
- **_block_agent_files_in_tests** -> None
- **_enforce_agentic_core_structure** -> None
- **_enforce_apps_structure** -> None
- **_get_approved_tests_subfolders** -> frozenset[str]
- **_enforce_tests_structure** -> None
- **_relocate_l2_layer_files** -> None
- **_relocate_file_to_l2** -> None
- **_relocate_l3_territory_files** -> None
- **_relocate_file_to_l3** -> None
- **_cleanup_empty_folder** -> None
- **enforce_depth_rules** -> dict[str, Any]
- **_enforce_depth_for_root** -> int
- **_heal_depth_violation** -> int
- **_legacy_archive_depth_violation** -> int
- **_enforce_apps_depth** -> int
- **_enforce_tests_depth** -> int
- **_enforce_universal_depth** -> int
- **_remove_empty_dirs** -> None
- **purge_orphaned_files** -> dict[str, Any]
- **_update_gitignore_for_purge** -> None
- **heal_hierarchy** -> dict[str, Any]
- **heal_repository** -> dict[str, Any]
- **heal** -> dict
- **scan_root_violations** -> dict[str, Any]
- **heal_root_violations** -> dict[str, Any]
- **_merge_root_folder_to_ssot** -> dict[str, Any]
- **_handle_coverage_html** -> dict[str, Any]


## Class: HierarchyHealerAgent

**Description**: 
    Unified Hierarchy Management Agent

    Combines capabilities from HierarchyEnforcerAgent and HierarchyHealerAgent:

    1. Structure Creation:
       - Creates missing L2 (Layer) and L3 (Sub-territory) directories per SSOT Maps.

    2. File Relocation (from Healer):
       - Moves files from non-approved folders to approved locations

    3. Depth Enforcement (from Enforcer):
       - Archives files violating depth rules (apps_*, tests, agentic_core)

    4. Folder Cleanup (from Healer):
       - Removes empty non-approved directories

    5. Orphan Purging (from Healer):
       - Archives orphaned files from forbidden locations
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root, healing_enabled, ctx, auto_approve
**Returns**: None
**Description**: 
        Initialize the unified hierarchy agent.

        Args:
            project_root: Absolute path to the project root
            healing_enabled: Whether healing operations are enabled (dry-run if False)
            ctx: Optional context for reporting
            auto_approve: If True, bypasses interactive user confirmation for moves
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for hierarchy violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        

#### create_missing_structure
**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: 
        Create missing directories across all ENFORCED_TERRITORIES.

        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.

        [EXPANDED SCOPE] Now handles all enforced territories (ops_scripts, system_learning, tools, data, docs, etc.)
        not just agentic_core.

        Args:
            target_territory: If specified, restricts creation to that territory

        Returns:
            Dict with counts of created directories and violations found
        

#### _create_agentic_core_structure
**Parameters**: self, territory_path, target_territory, results
**Returns**: None
**Description**: Create L2/L3 layer structure for agentic_core.

#### _create_territory_structure
**Parameters**: self, territory_name, territory_path, territory_config, results
**Returns**: None
**Description**: Create required subfolders for non-agentic_core territories (ops_scripts, system_learning, tools, data, docs, etc.).

#### _create_dir_with_init
**Parameters**: self, path, results, rel_label
**Returns**: None
**Description**: Helper to create directory and touch __init__.py sentinel.

#### relocate_misplaced_files
**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: 
        Relocate files from Sovereign Roots with optional territory filtering.

        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.

        Args:
            target_territory: If specified, restricts auditing to the relevant root (Strict Targeting).

        Returns:
            Dict with counts of relocated files, removed folders, violations found, and roots processed
        

#### _block_agent_files_in_tests
**Parameters**: self, results
**Returns**: None
**Description**: Scan tests/ for any *Agent.py files and record violations without moving.

        Agent files must never be relocated into tests/. Human action is required
        to move them back to their correct agentic_core/ territory.
        

#### _enforce_agentic_core_structure
**Parameters**: self, agentic_core_path, results
**Returns**: None
**Description**: Enforce strictly defined L2 structure for agentic_core.

#### _enforce_apps_structure
**Parameters**: self, root_path, results
**Returns**: None
**Description**: Flatten files in apps_*/subfolder/subsubfolder/ to match target depth.

#### _get_approved_tests_subfolders
**Returns**: frozenset[str]
**Description**: Derive the approved tests/ subfolder set directly from SOVEREIGN_TERRITORIES.

        Never hardcoded — always reflects the live SSOT in _constants.py.
        

#### _enforce_tests_structure
**Parameters**: self, root_path, results
**Returns**: None
**Description**: Enforce tests/ structure rules:
        1. All canonical subfolders (derived live from SOVEREIGN_TERRITORIES) are left
           untouched — no phantom relocation.
        2. Every .py file that is not infra MUST have a 'test_' prefix — violations are
           reported as errors, never silently moved.
        

#### _relocate_l2_layer_files
**Parameters**: self, agentic_core_path, bad_layer_l2, approved_layers_l2, results
**Returns**: None
**Description**: Relocate files from non-approved L2 layer.

#### _relocate_file_to_l2
**Parameters**: self, py_file, bad_layer_l2, agentic_core_path, approved_layers_l2, results
**Returns**: None
**Description**: Relocate a single file to approved L2 layer.

        [DEDUP 2026-02-07] Uses FCA classify_file() to determine correct L3 subfolder.
        

#### _relocate_l3_territory_files
**Parameters**: self, agentic_core_path, layer_l2_name, results
**Returns**: None
**Description**: Relocate files from non-approved L3 territories.

#### _relocate_file_to_l3
**Parameters**: self, py_file, layer_l2_name, layer_l2_path, bad_territory_l3, results
**Returns**: None
**Description**: Relocate a single file to approved L3 territory.

        [DEDUP 2026-02-07] Uses FCA classify_file() for L3 routing.
        

#### _cleanup_empty_folder
**Parameters**: self, folder_path, folder_label, results
**Returns**: None
**Description**: Remove empty folder tree after relocation.

#### enforce_depth_rules
**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: 
        Enforce depth rules and archive violations.

        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.

        [HARDENED] Accepts target_territory to skip unrelated roots.

        Returns:
            Dict with counts of archived files by category and violations found
        

#### _enforce_depth_for_root
**Parameters**: self, root_key, root_check, archive_subdir, label
**Returns**: int
**Description**: Generic depth enforcement using dispatch pattern.

#### _heal_depth_violation
**Parameters**: self, file_path, rel, depth, expected
**Returns**: int
**Description**: 
        Smart depth re-alignment instead of archiving.

        Strategy:
        - DEEP Violation (> expected): Flatten by moving up.
        - SHALLOW Violation (< expected): Reported only — no mutation. Creating a
          semantically meaningless folder (e.g. 'depth_aligned') to satisfy a depth
          counter is forbidden. The file must be placed in a semantically named folder.
        

#### _legacy_archive_depth_violation
**Parameters**: self, file_path, rel, depth, expected, subdir, label
**Returns**: int
**Description**: Legacy archive method - only used as fallback when smart healing has collision.

        [PHASE 33j] Gatekeeper is Single Point of Approval - handles user prompts.
        

#### _enforce_apps_depth
**Parameters**: self
**Returns**: int
**Description**: Enforce apps_* depth rule using generic handler for each apps folder.

#### _enforce_tests_depth
**Parameters**: self
**Returns**: int
**Description**: Enforce tests depth rule using generic handler.

#### _enforce_universal_depth
**Parameters**: self
**Returns**: int
**Description**: Enforce universal depth for non-Python files in agentic_core (depth 3). Detection-First.

#### _remove_empty_dirs
**Parameters**: self, path
**Returns**: None
**Description**: 
        Recursively remove empty directories.

        Args:
            path: Directory path to check and potentially remove
        

#### purge_orphaned_files
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Purge code and assets in forbidden or root-level locations.

        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.

        Returns:
            Dict with purge count, violations found, and errors
        

#### _update_gitignore_for_purge
**Parameters**: self
**Returns**: None
**Description**: Ensure purge artifacts (*.archived) are permanently ignored by git.

#### heal_hierarchy
**Parameters**: self, create_structure, relocate_files, enforce_depth, purge_orphans, execute, dry_run, auto_approve, target_territory
**Returns**: dict[str, Any]
**Description**: 
        Unified hierarchy healing with granular control.

        Args:
            create_structure: Create missing L2/L3 directories
            relocate_files: Relocate files from non-approved folders
            enforce_depth: Enforce depth rules and archive violations
            purge_orphans: Purge orphaned files
            auto_approve: If True, bypasses interactive user confirmation for moves.
                          USE WITH CAUTION - intended for CI/automated enforcement.
            target_territory: If specified, scope healing to this territory only
                              (e.g., "prompt_governance" -> agentic_core/prompt_governance)

        Returns:
            Comprehensive results dictionary
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: 
        Unified Hierarchy Healing - Enforces structure, relocation, and depth rules.

        WIRED CAPABILITIES:
        - heal_hierarchy(): Standard L2/L3 structure and file relocation.
        - heal_root_violations(): Root-level hygiene (scripts/, logs/, .archived).
        

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: 
        [SOVEREIGN CONTRACT] Standardized healing interface for Hierarchy violations.
        

#### scan_root_violations
**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: 
        [ULTRA-HARDENED] Universal Root Purge.
        Flags EVERY file in the territory root. Nothing is allowed to sit at L3 root.

        Detects:
        1. Forbidden folders at project root (scripts/, logs/, coverage_html/)
        2. .archived files at project root (should be in .healing_backups/)
        3. Files sitting in territory root instead of SSOT subfolders

        Args:
            target_territory: If specified, scans territory root for structural violations

        Returns:
            Dict with violations found and details
        

#### heal_root_violations
**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: 
        Heal root directory SSOT violations.

        Actions:
        1. Move .archived files to .healing_backups/root_archived/
        2. [DEPRECATED] scripts/ and logs/ are now valid roots (no merge)
        3. Add coverage_html/ to .gitignore or move to reports/

        Args:
            dry_run: If True, only preview actions

        Returns:
            Dict with healing results
        

#### _merge_root_folder_to_ssot
**Parameters**: self, folder_name, dry_run
**Returns**: dict[str, Any]
**Description**: 
        Merge a root folder's contents into its SSOT location.

        Args:
            folder_name: Name of folder at root (e.g., 'scripts', 'logs')
            dry_run: If True, only preview actions

        Returns:
            Dict with merge results
        

#### _handle_coverage_html
**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: 
        Handle coverage_html/ folder by adding to .gitignore.

        Args:
            dry_run: If True, only preview actions

        Returns:
            Dict with handling results
        



## Function: get_hierarchy_agent

**Parameters**: project_root
**Description**: Get or create HierarchyHealerAgent singleton.



## Function: __init__

**Parameters**: self, project_root, healing_enabled, ctx, auto_approve
**Returns**: None
**Description**: 
        Initialize the unified hierarchy agent.

        Args:
            project_root: Absolute path to the project root
            healing_enabled: Whether healing operations are enabled (dry-run if False)
            ctx: Optional context for reporting
            auto_approve: If True, bypasses interactive user confirmation for moves
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for hierarchy violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        



## Function: create_missing_structure

**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: 
        Create missing directories across all ENFORCED_TERRITORIES.

        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.

        [EXPANDED SCOPE] Now handles all enforced territories (ops_scripts, system_learning, tools, data, docs, etc.)
        not just agentic_core.

        Args:
            target_territory: If specified, restricts creation to that territory

        Returns:
            Dict with counts of created directories and violations found
        



## Function: _create_agentic_core_structure

**Parameters**: self, territory_path, target_territory, results
**Returns**: None
**Description**: Create L2/L3 layer structure for agentic_core.



## Function: _create_territory_structure

**Parameters**: self, territory_name, territory_path, territory_config, results
**Returns**: None
**Description**: Create required subfolders for non-agentic_core territories (ops_scripts, system_learning, tools, data, docs, etc.).



## Function: _create_dir_with_init

**Parameters**: self, path, results, rel_label
**Returns**: None
**Description**: Helper to create directory and touch __init__.py sentinel.



## Function: relocate_misplaced_files

**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: 
        Relocate files from Sovereign Roots with optional territory filtering.

        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.

        Args:
            target_territory: If specified, restricts auditing to the relevant root (Strict Targeting).

        Returns:
            Dict with counts of relocated files, removed folders, violations found, and roots processed
        



## Function: _block_agent_files_in_tests

**Parameters**: self, results
**Returns**: None
**Description**: Scan tests/ for any *Agent.py files and record violations without moving.

        Agent files must never be relocated into tests/. Human action is required
        to move them back to their correct agentic_core/ territory.
        



## Function: _enforce_agentic_core_structure

**Parameters**: self, agentic_core_path, results
**Returns**: None
**Description**: Enforce strictly defined L2 structure for agentic_core.



## Function: _enforce_apps_structure

**Parameters**: self, root_path, results
**Returns**: None
**Description**: Flatten files in apps_*/subfolder/subsubfolder/ to match target depth.



## Function: _get_approved_tests_subfolders

**Returns**: frozenset[str]
**Description**: Derive the approved tests/ subfolder set directly from SOVEREIGN_TERRITORIES.

        Never hardcoded — always reflects the live SSOT in _constants.py.
        



## Function: _enforce_tests_structure

**Parameters**: self, root_path, results
**Returns**: None
**Description**: Enforce tests/ structure rules:
        1. All canonical subfolders (derived live from SOVEREIGN_TERRITORIES) are left
           untouched — no phantom relocation.
        2. Every .py file that is not infra MUST have a 'test_' prefix — violations are
           reported as errors, never silently moved.
        



## Function: _relocate_l2_layer_files

**Parameters**: self, agentic_core_path, bad_layer_l2, approved_layers_l2, results
**Returns**: None
**Description**: Relocate files from non-approved L2 layer.



## Function: _relocate_file_to_l2

**Parameters**: self, py_file, bad_layer_l2, agentic_core_path, approved_layers_l2, results
**Returns**: None
**Description**: Relocate a single file to approved L2 layer.

        [DEDUP 2026-02-07] Uses FCA classify_file() to determine correct L3 subfolder.
        



## Function: _relocate_l3_territory_files

**Parameters**: self, agentic_core_path, layer_l2_name, results
**Returns**: None
**Description**: Relocate files from non-approved L3 territories.



## Function: _relocate_file_to_l3

**Parameters**: self, py_file, layer_l2_name, layer_l2_path, bad_territory_l3, results
**Returns**: None
**Description**: Relocate a single file to approved L3 territory.

        [DEDUP 2026-02-07] Uses FCA classify_file() for L3 routing.
        



## Function: _cleanup_empty_folder

**Parameters**: self, folder_path, folder_label, results
**Returns**: None
**Description**: Remove empty folder tree after relocation.



## Function: enforce_depth_rules

**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: 
        Enforce depth rules and archive violations.

        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.

        [HARDENED] Accepts target_territory to skip unrelated roots.

        Returns:
            Dict with counts of archived files by category and violations found
        



## Function: _enforce_depth_for_root

**Parameters**: self, root_key, root_check, archive_subdir, label
**Returns**: int
**Description**: Generic depth enforcement using dispatch pattern.



## Function: _heal_depth_violation

**Parameters**: self, file_path, rel, depth, expected
**Returns**: int
**Description**: 
        Smart depth re-alignment instead of archiving.

        Strategy:
        - DEEP Violation (> expected): Flatten by moving up.
        - SHALLOW Violation (< expected): Reported only — no mutation. Creating a
          semantically meaningless folder (e.g. 'depth_aligned') to satisfy a depth
          counter is forbidden. The file must be placed in a semantically named folder.
        



## Function: _legacy_archive_depth_violation

**Parameters**: self, file_path, rel, depth, expected, subdir, label
**Returns**: int
**Description**: Legacy archive method - only used as fallback when smart healing has collision.

        [PHASE 33j] Gatekeeper is Single Point of Approval - handles user prompts.
        



## Function: _enforce_apps_depth

**Parameters**: self
**Returns**: int
**Description**: Enforce apps_* depth rule using generic handler for each apps folder.



## Function: _enforce_tests_depth

**Parameters**: self
**Returns**: int
**Description**: Enforce tests depth rule using generic handler.



## Function: _enforce_universal_depth

**Parameters**: self
**Returns**: int
**Description**: Enforce universal depth for non-Python files in agentic_core (depth 3). Detection-First.



## Function: _remove_empty_dirs

**Parameters**: self, path
**Returns**: None
**Description**: 
        Recursively remove empty directories.

        Args:
            path: Directory path to check and potentially remove
        



## Function: purge_orphaned_files

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Purge code and assets in forbidden or root-level locations.

        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.

        Returns:
            Dict with purge count, violations found, and errors
        



## Function: _update_gitignore_for_purge

**Parameters**: self
**Returns**: None
**Description**: Ensure purge artifacts (*.archived) are permanently ignored by git.



## Function: heal_hierarchy

**Parameters**: self, create_structure, relocate_files, enforce_depth, purge_orphans, execute, dry_run, auto_approve, target_territory
**Returns**: dict[str, Any]
**Description**: 
        Unified hierarchy healing with granular control.

        Args:
            create_structure: Create missing L2/L3 directories
            relocate_files: Relocate files from non-approved folders
            enforce_depth: Enforce depth rules and archive violations
            purge_orphans: Purge orphaned files
            auto_approve: If True, bypasses interactive user confirmation for moves.
                          USE WITH CAUTION - intended for CI/automated enforcement.
            target_territory: If specified, scope healing to this territory only
                              (e.g., "prompt_governance" -> agentic_core/prompt_governance)

        Returns:
            Comprehensive results dictionary
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: 
        Unified Hierarchy Healing - Enforces structure, relocation, and depth rules.

        WIRED CAPABILITIES:
        - heal_hierarchy(): Standard L2/L3 structure and file relocation.
        - heal_root_violations(): Root-level hygiene (scripts/, logs/, .archived).
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: 
        [SOVEREIGN CONTRACT] Standardized healing interface for Hierarchy violations.
        



## Function: scan_root_violations

**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: 
        [ULTRA-HARDENED] Universal Root Purge.
        Flags EVERY file in the territory root. Nothing is allowed to sit at L3 root.

        Detects:
        1. Forbidden folders at project root (scripts/, logs/, coverage_html/)
        2. .archived files at project root (should be in .healing_backups/)
        3. Files sitting in territory root instead of SSOT subfolders

        Args:
            target_territory: If specified, scans territory root for structural violations

        Returns:
            Dict with violations found and details
        



## Function: heal_root_violations

**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: 
        Heal root directory SSOT violations.

        Actions:
        1. Move .archived files to .healing_backups/root_archived/
        2. [DEPRECATED] scripts/ and logs/ are now valid roots (no merge)
        3. Add coverage_html/ to .gitignore or move to reports/

        Args:
            dry_run: If True, only preview actions

        Returns:
            Dict with healing results
        



## Function: _merge_root_folder_to_ssot

**Parameters**: self, folder_name, dry_run
**Returns**: dict[str, Any]
**Description**: 
        Merge a root folder's contents into its SSOT location.

        Args:
            folder_name: Name of folder at root (e.g., 'scripts', 'logs')
            dry_run: If True, only preview actions

        Returns:
            Dict with merge results
        



## Function: _handle_coverage_html

**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: 
        Handle coverage_html/ folder by adding to .gitignore.

        Args:
            dry_run: If True, only preview actions

        Returns:
            Dict with handling results
        



## Usage Examples

### Class Usage

```python
# Using HierarchyHealerAgent
hierarchyhealeragent = HierarchyHealerAgent()
hierarchyhealeragent.heal()
hierarchyhealeragent.create_missing_structure()
```

### Function Usage

```python
# Using get_hierarchy_agent
result = get_hierarchy_agent(project_root)
```

```python
# Using __init__
result = __init__(project_root, healing_enabled)
```

```python
# Using heal
result = heal(violation)
```



---
**Generated**: 2026-03-26T09:39:05.268351
**Type**: api_reference
**Quality**: comprehensive
