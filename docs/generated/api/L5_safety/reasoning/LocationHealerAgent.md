# API Documentation: LocationHealerAgent

**Target Audience**: developers, api_users

# LocationHealerAgent API Documentation

**File**: `LocationHealerAgent.py`
**Classes**: 1
**Functions**: 56

## Classes

- **LocationHealerAgent** (inherits from SovereignBaseAgent)

## Functions

- **_get_write_gateway**
- **_get_location_healing_strategy**
- **_get_heal_result_types**
- **_evict_blueprint_modules** -> None
- **__post_init__**
- **_validate_project_root** -> None
- **naming_agent**
- **import_agent**
- **heal** -> HealResult
- **heal_violations** -> dict
- **_determine_target_directory** -> Path | None
- **heal_repository** -> dict[str, int]
- **_init_backup_dir** -> Path
- **_backup_file** -> Path
- **safe_create_directory** -> Path
- **safe_move** -> dict[str, Any]
- **safe_delete** -> dict[str, Any]
- **_backup_and_write_file** -> None
- **post_heal_validation** -> dict[str, Any]
- **fix_imports_after_move** -> dict[str, Any]
- **_apply_healing_strategy** -> dict[str, Any]
- **_heal_broken_backup** -> dict[str, Any]
- **_heal_via_archiving** -> dict[str, Any]
- **_heal_app_specific_violation** -> dict[str, Any]
- **_heal_territory_mismatch** -> dict[str, Any]
- **_heal_void_violation** -> dict[str, Any]
- **_relocate_to_existing_subfolder** -> dict[str, Any]
- **_create_new_subfolder_and_update_ssot** -> dict[str, Any]
- **_autonomous_void_violation_resolution** -> dict[str, Any]
- **_calculate_subfolder_confidence** -> float
- **_calculate_semantic_similarity** -> float
- **_find_best_matching_subfolder** -> str | None
- **_autonomous_create_subfolder** -> dict[str, Any]
- **_autonomous_relocate_to_subfolder** -> dict[str, Any]
- **_heal_depth_violation** -> dict[str, Any]
- **_collect_naming_violations** -> tuple[list, list]
- **_apply_naming_heals** -> int
- **_apply_convention_fixes** -> None
- **_set_naming_final_status** -> None
- **_insert_semantic_keywords** -> None
- **_insert_sovereign_marker** -> None
- **_find_docstring_end** -> int
- **_remove_offending_imports** -> tuple[list[str], list[str]]
- **post_naming_validation** -> dict[str, Any]
- **auto_heal_naming_issues** -> dict[str, Any]
- **post_import_validation_and_heal** -> dict[str, Any]
- **_heal_gravity_violations** -> list[dict[str, Any]]
- **post_naming_conventions_validation_and_heal** -> dict[str, Any]
- **deep_import_validation_and_heal** -> dict[str, Any]
- **deep_naming_validation_and_heal** -> dict[str, Any]
- **_determine_target_root_from_metadata** -> str | None
- **enforce_void_compliance** -> tuple[list[Path], list[tuple[Path, str]]]
- **validate_file_location** -> tuple[bool, str]
- **cleanup_violations** -> list[dict[str, Any]]
- **run_with_cleanup** -> dict[str, Any]
- **sort_key** -> Any


## Class: LocationHealerAgent

**Description**: 
    Automated remediation agent for location violations.

    FACADE SHELL: Delegates to UnifiedAgent with LocationHealingStrategy.
    SIGNATURE COMPATIBILITY: 100% preserved - no breaking changes.

    Performs:
    - Safe file moves with collision handling
    - Safe file deletions with backup
    - Backup directory management
    - Import path fixing after moves
    - Post-heal validation (naming, imports)
    - Archive operations

    Does NOT perform:
    - Validation (use LocationValidatorAgent)
    - Gravity detection (use GravityLeakDetector)

    All operations follow ZLM protocol with shadow backups.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Description**: Initialize healer with backup infrastructure.

#### _validate_project_root
**Parameters**: self
**Returns**: None
**Description**: Validate that project_root is the actual project root.

#### naming_agent
**Parameters**: self
**Description**: Lazy NamingAgent - created on first access to avoid circular init.

#### import_agent
**Parameters**: self
**Description**: Lazy import healer - created on first access to avoid circular init.

#### heal
**Parameters**: self, violation
**Returns**: HealResult
**Description**: 
        Heal a single location violation.

        Required by execute_ssot.py — provides the interface for autonomous healing.
        Converts violation dict to cleanup_violations format and returns HealResult.

        Args:
            violation: Dict with keys: file, message, type, suggested_action

        Returns:
            HealResult with violations_found, violations_fixed, status, errors, metadata.
        

#### heal_violations
**Parameters**: self, violations, auto_approve
**Returns**: dict
**Description**: 
        Heal multiple location violations.

        Called by execute_ssot.py when LocationAgent has detected violations
        and the decision engine has approved healing.
        

#### _determine_target_directory
**Parameters**: self, src_path, violation
**Returns**: Path | None
**Description**: Determine target directory for file relocation based on violation context.

        [DEDUP 2026-02-07] Uses FCA's classify_file() + _get_correct_folder_for_type()
        for classification-based routing instead of hardcoded defaults.
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path, target_territory
**Returns**: dict[str, int]
**Description**: 
        Autonomous full-repository location law healing.
        Canon Key 51 compliance - fully self-orchestrating.

        Args:
            target_territory: If provided, restricts the location scan to this
                sovereign territory root only (matches LocationValidatorAgent.run
                strict-targeting behaviour). When None, scans all roots.
        

#### _init_backup_dir
**Parameters**: self
**Returns**: Path
**Description**: Initialize backup directory for safe mutations.

#### _backup_file
**Parameters**: self, file_path, backup_dir
**Returns**: Path
**Description**: Create a physical safety copy before mutation.

#### safe_create_directory
**Parameters**: self, relative_path
**Returns**: Path
**Description**: Safely create a directory within the project root.

#### safe_move
**Parameters**: self, src_path, dst_path, dry_run
**Returns**: dict[str, Any]
**Description**: Safely move a file using ArchivalGatekeeper with audit trail.

#### safe_delete
**Parameters**: self, file_path, dry_run
**Returns**: dict[str, Any]
**Description**: Safely delete a file using ArchivalGatekeeper (soft delete to archive).

#### _backup_and_write_file
**Parameters**: self, file_path, new_content
**Returns**: None
**Description**: Backup file and write new content atomically.

#### post_heal_validation
**Parameters**: self, original_path, new_path, dry_run
**Returns**: dict[str, Any]
**Description**: Re-validate after healing to confirm fix effectiveness.

#### fix_imports_after_move
**Parameters**: self, old_path, new_path, dry_run
**Returns**: dict[str, Any]
**Description**: Ultra import healing post-move - scans entire repo for references to old module.

#### _apply_healing_strategy
**Parameters**: self, file_path, msg, archives_root, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: Apply appropriate healing strategy based on violation message.

#### _heal_broken_backup
**Parameters**: self, file_path, dry_run, affected_paths
**Returns**: dict[str, Any]
**Description**: Heal broken backup files by deletion.

#### _heal_via_archiving
**Parameters**: self, file_path, msg, archives_root, dry_run, affected_paths, hitl_approval_fn
**Returns**: dict[str, Any]
**Description**: Heal violations by archiving to appropriate subfolder.

        CRITICAL: Archiving requires explicit user approval via terminal prompt.
        This prevents accidental data loss from aggressive archiving.

        Wave 6: hitl_approval_fn(file_path, msg) -> (approved: bool, decision: str)
        When provided, the function is called before any archive move.  If it
        returns approved=False the archive is skipped and the decision is logged.
        

#### _heal_app_specific_violation
**Parameters**: self, file_path, msg, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: Heal app-specific violations by moving to correct apps folder.

#### _heal_territory_mismatch
**Parameters**: self, file_path, msg, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: Heal territory mismatch violations by moving to correct agentic_core location.

#### _heal_void_violation
**Parameters**: self, file_path, msg, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: 
        Heal VOID VIOLATION by proper relocation - NOT archiving.

        CRITICAL FLOW (in order of preference):
        1. Relocate to best matching existing subfolder
        2. Propose creating a new subfolder (with user approval)
        3. Update SSOT after successful operation
        4. Archive ONLY as absolute last resort (with explicit user approval)

        This prevents aggressive archiving of files that simply aren't in SSOT yet.
        

#### _relocate_to_existing_subfolder
**Parameters**: self, file_path, root_folder, existing_subfolders, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: Relocate file to an existing approved subfolder.

#### _create_new_subfolder_and_update_ssot
**Parameters**: self, file_path, root_folder, new_subfolder, dry_run, affected_paths
**Returns**: dict[str, Any]
**Description**: Create a new subfolder and update SOVEREIGN_REGISTRY in structure_blueprint.py.

#### _autonomous_void_violation_resolution
**Parameters**: self, file_path, root_folder, unknown_subfolder, msg, existing_subfolders, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: 
        Autonomous resolution of void violations using intelligent decision-making.
        Replaces user prompts with confidence-based autonomous choices.

        Decision Logic:
        1. HIGH CONFIDENCE: If unknown_subfolder matches semantic patterns, create it
        2. MEDIUM CONFIDENCE: If similar subfolder exists, relocate there
        3. LOW CONFIDENCE: Archive to prevent misplacement
        

#### _calculate_subfolder_confidence
**Parameters**: self, unknown_subfolder, existing_subfolders, file_path
**Returns**: float
**Description**: 
        Calculate confidence score for creating a new subfolder.
        Returns 0.0-1.0 based on semantic analysis.

        [AST-PRIMARY] If file_path is provided and AST classification returns AGENT
        or ORCHESTRATOR, confidence is forced to 0.0 — agent files must never be
        autonomously created inside non-source subfolders.  Regex/Jaccard are only
        consulted for non-agent files (secondary role).
        

#### _calculate_semantic_similarity
**Parameters**: self, unknown, existing
**Returns**: float
**Description**: Calculate semantic similarity between unknown subfolder and existing ones.

#### _find_best_matching_subfolder
**Parameters**: self, unknown, existing, file_path
**Returns**: str | None
**Description**: Find the best matching existing subfolder for relocation.

        [PRESERVED-FIRST] Certain subfolder names are semantically self-describing
        and must never be flattened or Jaccard-matched into a different location.
        If `unknown` is in _PRESERVED_SUBDIRS AND already exists in `existing`,
        return it as-is (perfect self-match).  If it is preserved but not yet in
        `existing`, return None so the caller creates it rather than relocating.

        [AST-PRIMARY] If file_path is provided, classify the file first.
        - AGENT / ORCHESTRATOR files: only source-layer subfolders are eligible
          (reasoning/, engines/, enforcement/).  Non-source subfolders such as
          'support', 'test_*', 'fixtures' are unconditionally excluded.
        - All other types: Jaccard word-overlap (secondary) selects the best match.
        

#### _autonomous_create_subfolder
**Parameters**: self, file_path, root_folder, new_subfolder, dry_run, affected_paths
**Returns**: dict[str, Any]
**Description**: Autonomously create new subfolder and update SSOT.

#### _autonomous_relocate_to_subfolder
**Parameters**: self, file_path, root_folder, target_subfolder, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: Autonomously relocate file to target subfolder.

#### _heal_depth_violation
**Parameters**: self, file_path, msg, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: 
        Heal depth violations by realigning file within its Sovereign Territory.
        - DEEP: Flattens path (moves up).
        - SHALLOW: Reported only — no mutation. Creating a semantically meaningless
          folder (e.g. 'depth_aligned') to satisfy a depth counter is forbidden.
          The file must be placed in a folder with real semantic meaning.
        

#### _collect_naming_violations
**Parameters**: self, py_files, affected_paths
**Returns**: tuple[list, list]
**Description**: Phase 1: Scan files for naming violations.

#### _apply_naming_heals
**Parameters**: self, heal_actions, affected_paths
**Returns**: int
**Description**: Phase 2: Apply healing actions.

#### _apply_convention_fixes
**Parameters**: self, path, action, affected_paths
**Returns**: None
**Description**: Apply filename/prefix convention fixes.

#### _set_naming_final_status
**Parameters**: self, report, heal_actions, semantic_issues
**Returns**: None
**Description**: Phase 3: Set final status.

#### _insert_semantic_keywords
**Parameters**: self, path, missing_signals
**Returns**: None
**Description**: Insert semantic keyword TODO block.

#### _insert_sovereign_marker
**Parameters**: self, path
**Returns**: None
**Description**: Insert sovereign marker TODO.

#### _find_docstring_end
**Parameters**: self, lines
**Returns**: int
**Description**: Find insertion point after docstring/shebang.

#### _remove_offending_imports
**Parameters**: self, lines, downstream_roots
**Returns**: tuple[list[str], list[str]]
**Description**: Remove import lines containing downstream roots.

#### post_naming_validation
**Parameters**: self, affected_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Post-healing NamingAgent validation on affected paths.

#### auto_heal_naming_issues
**Parameters**: self, naming_report, dry_run
**Returns**: dict[str, Any]
**Description**: Autonomous naming healing triggered when post-naming validation finds issues.

#### post_import_validation_and_heal
**Parameters**: self, affected_paths, import_touched_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Combined ImportAgent validation + auto-healing on affected files.

#### _heal_gravity_violations
**Parameters**: self, gravity_issues
**Returns**: list[dict[str, Any]]
**Description**: Delegate gravity violation healing to GravityLeakDetector.

#### post_naming_conventions_validation_and_heal
**Parameters**: self, affected_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Full NamingAgent convention validation + auto-healing for fixable issues.

#### deep_import_validation_and_heal
**Parameters**: self, affected_paths, import_touched_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Deep ImportAgent integration: full validation + advanced auto-heal.

#### deep_naming_validation_and_heal
**Parameters**: self, affected_paths, import_touched_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Deep naming validation orchestrator — linear phase chain.

#### _determine_target_root_from_metadata
**Parameters**: self, filename
**Returns**: str | None
**Description**: Smart routing using active PROJECT_ROOT_METADATA.

#### enforce_void_compliance
**Parameters**: self, files
**Returns**: tuple[list[Path], list[tuple[Path, str]]]
**Description**: Filter files and collect all location-based violations.

        Delegates to LocationValidatorAgent for validation.
        

#### validate_file_location
**Parameters**: self, file_path
**Returns**: tuple[bool, str]
**Description**: Validate that a file is in the correct location.

        Delegates to LocationValidatorAgent for validation.
        

#### cleanup_violations
**Parameters**: self, violations, dry_run, max_actions
**Returns**: list[dict[str, Any]]
**Description**: ULTRA HEALING ENGINE — Full autonomous healing with batch post-validation.

        Salvaged from LocationAgent.py during LCD+ decommission.
        

#### run_with_cleanup
**Parameters**: self, files, dry_run
**Returns**: dict[str, Any]
**Description**: Full location compliance scan with automatic cleanup.



## Function: _get_write_gateway



## Function: _get_location_healing_strategy



## Function: _get_heal_result_types



## Function: _evict_blueprint_modules

**Returns**: None
**Description**: Evict stale structure_blueprint submodules from sys.modules.

    Called immediately after any on-disk write to a blueprint/constants file so
    that the next import re-executes the module and picks up the new
    SOVEREIGN_TERRITORIES / is_path_allowed definitions.

    REQ-417 blocks importlib.reload() on core modules but does NOT block
    deletion from sys.modules — eviction via pop() is the safe path.
    importlib.invalidate_caches() then tells the import machinery to rescan
    the file-system for new/changed .py files.
    



## Function: __post_init__

**Parameters**: self
**Description**: Initialize healer with backup infrastructure.



## Function: _validate_project_root

**Parameters**: self
**Returns**: None
**Description**: Validate that project_root is the actual project root.



## Function: naming_agent

**Parameters**: self
**Description**: Lazy NamingAgent - created on first access to avoid circular init.



## Function: import_agent

**Parameters**: self
**Description**: Lazy import healer - created on first access to avoid circular init.



## Function: heal

**Parameters**: self, violation
**Returns**: HealResult
**Description**: 
        Heal a single location violation.

        Required by execute_ssot.py — provides the interface for autonomous healing.
        Converts violation dict to cleanup_violations format and returns HealResult.

        Args:
            violation: Dict with keys: file, message, type, suggested_action

        Returns:
            HealResult with violations_found, violations_fixed, status, errors, metadata.
        



## Function: heal_violations

**Parameters**: self, violations, auto_approve
**Returns**: dict
**Description**: 
        Heal multiple location violations.

        Called by execute_ssot.py when LocationAgent has detected violations
        and the decision engine has approved healing.
        



## Function: _determine_target_directory

**Parameters**: self, src_path, violation
**Returns**: Path | None
**Description**: Determine target directory for file relocation based on violation context.

        [DEDUP 2026-02-07] Uses FCA's classify_file() + _get_correct_folder_for_type()
        for classification-based routing instead of hardcoded defaults.
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path, target_territory
**Returns**: dict[str, int]
**Description**: 
        Autonomous full-repository location law healing.
        Canon Key 51 compliance - fully self-orchestrating.

        Args:
            target_territory: If provided, restricts the location scan to this
                sovereign territory root only (matches LocationValidatorAgent.run
                strict-targeting behaviour). When None, scans all roots.
        



## Function: _init_backup_dir

**Parameters**: self
**Returns**: Path
**Description**: Initialize backup directory for safe mutations.



## Function: _backup_file

**Parameters**: self, file_path, backup_dir
**Returns**: Path
**Description**: Create a physical safety copy before mutation.



## Function: safe_create_directory

**Parameters**: self, relative_path
**Returns**: Path
**Description**: Safely create a directory within the project root.



## Function: safe_move

**Parameters**: self, src_path, dst_path, dry_run
**Returns**: dict[str, Any]
**Description**: Safely move a file using ArchivalGatekeeper with audit trail.



## Function: safe_delete

**Parameters**: self, file_path, dry_run
**Returns**: dict[str, Any]
**Description**: Safely delete a file using ArchivalGatekeeper (soft delete to archive).



## Function: _backup_and_write_file

**Parameters**: self, file_path, new_content
**Returns**: None
**Description**: Backup file and write new content atomically.



## Function: post_heal_validation

**Parameters**: self, original_path, new_path, dry_run
**Returns**: dict[str, Any]
**Description**: Re-validate after healing to confirm fix effectiveness.



## Function: fix_imports_after_move

**Parameters**: self, old_path, new_path, dry_run
**Returns**: dict[str, Any]
**Description**: Ultra import healing post-move - scans entire repo for references to old module.



## Function: _apply_healing_strategy

**Parameters**: self, file_path, msg, archives_root, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: Apply appropriate healing strategy based on violation message.



## Function: _heal_broken_backup

**Parameters**: self, file_path, dry_run, affected_paths
**Returns**: dict[str, Any]
**Description**: Heal broken backup files by deletion.



## Function: _heal_via_archiving

**Parameters**: self, file_path, msg, archives_root, dry_run, affected_paths, hitl_approval_fn
**Returns**: dict[str, Any]
**Description**: Heal violations by archiving to appropriate subfolder.

        CRITICAL: Archiving requires explicit user approval via terminal prompt.
        This prevents accidental data loss from aggressive archiving.

        Wave 6: hitl_approval_fn(file_path, msg) -> (approved: bool, decision: str)
        When provided, the function is called before any archive move.  If it
        returns approved=False the archive is skipped and the decision is logged.
        



## Function: _heal_app_specific_violation

**Parameters**: self, file_path, msg, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: Heal app-specific violations by moving to correct apps folder.



## Function: _heal_territory_mismatch

**Parameters**: self, file_path, msg, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: Heal territory mismatch violations by moving to correct agentic_core location.



## Function: _heal_void_violation

**Parameters**: self, file_path, msg, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: 
        Heal VOID VIOLATION by proper relocation - NOT archiving.

        CRITICAL FLOW (in order of preference):
        1. Relocate to best matching existing subfolder
        2. Propose creating a new subfolder (with user approval)
        3. Update SSOT after successful operation
        4. Archive ONLY as absolute last resort (with explicit user approval)

        This prevents aggressive archiving of files that simply aren't in SSOT yet.
        



## Function: _relocate_to_existing_subfolder

**Parameters**: self, file_path, root_folder, existing_subfolders, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: Relocate file to an existing approved subfolder.



## Function: _create_new_subfolder_and_update_ssot

**Parameters**: self, file_path, root_folder, new_subfolder, dry_run, affected_paths
**Returns**: dict[str, Any]
**Description**: Create a new subfolder and update SOVEREIGN_REGISTRY in structure_blueprint.py.



## Function: _autonomous_void_violation_resolution

**Parameters**: self, file_path, root_folder, unknown_subfolder, msg, existing_subfolders, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: 
        Autonomous resolution of void violations using intelligent decision-making.
        Replaces user prompts with confidence-based autonomous choices.

        Decision Logic:
        1. HIGH CONFIDENCE: If unknown_subfolder matches semantic patterns, create it
        2. MEDIUM CONFIDENCE: If similar subfolder exists, relocate there
        3. LOW CONFIDENCE: Archive to prevent misplacement
        



## Function: _calculate_subfolder_confidence

**Parameters**: self, unknown_subfolder, existing_subfolders, file_path
**Returns**: float
**Description**: 
        Calculate confidence score for creating a new subfolder.
        Returns 0.0-1.0 based on semantic analysis.

        [AST-PRIMARY] If file_path is provided and AST classification returns AGENT
        or ORCHESTRATOR, confidence is forced to 0.0 — agent files must never be
        autonomously created inside non-source subfolders.  Regex/Jaccard are only
        consulted for non-agent files (secondary role).
        



## Function: _calculate_semantic_similarity

**Parameters**: self, unknown, existing
**Returns**: float
**Description**: Calculate semantic similarity between unknown subfolder and existing ones.



## Function: _find_best_matching_subfolder

**Parameters**: self, unknown, existing, file_path
**Returns**: str | None
**Description**: Find the best matching existing subfolder for relocation.

        [PRESERVED-FIRST] Certain subfolder names are semantically self-describing
        and must never be flattened or Jaccard-matched into a different location.
        If `unknown` is in _PRESERVED_SUBDIRS AND already exists in `existing`,
        return it as-is (perfect self-match).  If it is preserved but not yet in
        `existing`, return None so the caller creates it rather than relocating.

        [AST-PRIMARY] If file_path is provided, classify the file first.
        - AGENT / ORCHESTRATOR files: only source-layer subfolders are eligible
          (reasoning/, engines/, enforcement/).  Non-source subfolders such as
          'support', 'test_*', 'fixtures' are unconditionally excluded.
        - All other types: Jaccard word-overlap (secondary) selects the best match.
        



## Function: _autonomous_create_subfolder

**Parameters**: self, file_path, root_folder, new_subfolder, dry_run, affected_paths
**Returns**: dict[str, Any]
**Description**: Autonomously create new subfolder and update SSOT.



## Function: _autonomous_relocate_to_subfolder

**Parameters**: self, file_path, root_folder, target_subfolder, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: Autonomously relocate file to target subfolder.



## Function: _heal_depth_violation

**Parameters**: self, file_path, msg, dry_run, affected_paths, import_touched_paths
**Returns**: dict[str, Any]
**Description**: 
        Heal depth violations by realigning file within its Sovereign Territory.
        - DEEP: Flattens path (moves up).
        - SHALLOW: Reported only — no mutation. Creating a semantically meaningless
          folder (e.g. 'depth_aligned') to satisfy a depth counter is forbidden.
          The file must be placed in a folder with real semantic meaning.
        



## Function: _collect_naming_violations

**Parameters**: self, py_files, affected_paths
**Returns**: tuple[list, list]
**Description**: Phase 1: Scan files for naming violations.



## Function: _apply_naming_heals

**Parameters**: self, heal_actions, affected_paths
**Returns**: int
**Description**: Phase 2: Apply healing actions.



## Function: _apply_convention_fixes

**Parameters**: self, path, action, affected_paths
**Returns**: None
**Description**: Apply filename/prefix convention fixes.



## Function: _set_naming_final_status

**Parameters**: self, report, heal_actions, semantic_issues
**Returns**: None
**Description**: Phase 3: Set final status.



## Function: _insert_semantic_keywords

**Parameters**: self, path, missing_signals
**Returns**: None
**Description**: Insert semantic keyword TODO block.



## Function: _insert_sovereign_marker

**Parameters**: self, path
**Returns**: None
**Description**: Insert sovereign marker TODO.



## Function: _find_docstring_end

**Parameters**: self, lines
**Returns**: int
**Description**: Find insertion point after docstring/shebang.



## Function: _remove_offending_imports

**Parameters**: self, lines, downstream_roots
**Returns**: tuple[list[str], list[str]]
**Description**: Remove import lines containing downstream roots.



## Function: post_naming_validation

**Parameters**: self, affected_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Post-healing NamingAgent validation on affected paths.



## Function: auto_heal_naming_issues

**Parameters**: self, naming_report, dry_run
**Returns**: dict[str, Any]
**Description**: Autonomous naming healing triggered when post-naming validation finds issues.



## Function: post_import_validation_and_heal

**Parameters**: self, affected_paths, import_touched_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Combined ImportAgent validation + auto-healing on affected files.



## Function: _heal_gravity_violations

**Parameters**: self, gravity_issues
**Returns**: list[dict[str, Any]]
**Description**: Delegate gravity violation healing to GravityLeakDetector.



## Function: post_naming_conventions_validation_and_heal

**Parameters**: self, affected_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Full NamingAgent convention validation + auto-healing for fixable issues.



## Function: deep_import_validation_and_heal

**Parameters**: self, affected_paths, import_touched_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Deep ImportAgent integration: full validation + advanced auto-heal.



## Function: deep_naming_validation_and_heal

**Parameters**: self, affected_paths, import_touched_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Deep naming validation orchestrator — linear phase chain.



## Function: _determine_target_root_from_metadata

**Parameters**: self, filename
**Returns**: str | None
**Description**: Smart routing using active PROJECT_ROOT_METADATA.



## Function: enforce_void_compliance

**Parameters**: self, files
**Returns**: tuple[list[Path], list[tuple[Path, str]]]
**Description**: Filter files and collect all location-based violations.

        Delegates to LocationValidatorAgent for validation.
        



## Function: validate_file_location

**Parameters**: self, file_path
**Returns**: tuple[bool, str]
**Description**: Validate that a file is in the correct location.

        Delegates to LocationValidatorAgent for validation.
        



## Function: cleanup_violations

**Parameters**: self, violations, dry_run, max_actions
**Returns**: list[dict[str, Any]]
**Description**: ULTRA HEALING ENGINE — Full autonomous healing with batch post-validation.

        Salvaged from LocationAgent.py during LCD+ decommission.
        



## Function: run_with_cleanup

**Parameters**: self, files, dry_run
**Returns**: dict[str, Any]
**Description**: Full location compliance scan with automatic cleanup.



## Function: sort_key

**Parameters**: p_str
**Returns**: Any


## Usage Examples

### Class Usage

```python
# Using LocationHealerAgent
locationhealeragent = LocationHealerAgent()
locationhealeragent.naming_agent()
locationhealeragent.import_agent()
```

### Function Usage

```python
# Using _get_write_gateway
result = _get_write_gateway()
```

```python
# Using _get_location_healing_strategy
result = _get_location_healing_strategy()
```

```python
# Using _get_heal_result_types
result = _get_heal_result_types()
```



---
**Generated**: 2026-03-26T09:39:05.323640
**Type**: api_reference
**Quality**: comprehensive
