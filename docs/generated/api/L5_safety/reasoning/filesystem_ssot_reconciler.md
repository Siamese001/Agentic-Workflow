# API Documentation: filesystem_ssot_reconciler

**Target Audience**: developers, api_users

# filesystem_ssot_reconciler API Documentation

**File**: `filesystem_ssot_reconciler.py`
**Classes**: 4
**Functions**: 33

## Classes

- **ReconciliationViolation**
- **FilesystemSSOTReconcilerAgent** (inherits from AutonomyMixin, SelfDiagnosisMixin, L0RoutingBaseAgent)
- **MCPHardenedMixin**
- **SubatomicTestingMixin**

## Functions

- **_evict_blueprint_modules** -> None
- **heal_repository** -> dict[str, int]
- **heal** -> dict
- **__init__** -> None
- **run_ci_verification_sync** -> tuple[bool, dict]
- **_create_no_drift_result** -> dict[str, Any]
- **_create_rejected_result** -> dict[str, Any]
- **_create_applied_result** -> dict[str, Any]
- **_handle_interactive_approval** -> tuple[bool, dict[str, Any] | None]
- **_load_current_blueprint** -> dict[str, Any]
- **_detect_drift** -> list[dict[str, Any]]
- **_check_registry_subfolders** -> None
- **_check_l2_subfolders** -> None
- **_check_canon_signals** -> None
- **_check_registry_subfolders** -> None
- **_check_l2_subfolders** -> None
- **_check_canon_signals** -> None
- **_generate_filesystem_proposals** -> list[dict[str, Any]]
- **_apply_filesystem_alignment** -> list[str]
- **_backup_blueprint** -> Path
- **_apply_proposals** -> None
- **_apply_sovereign_registry_update** -> str
- **_apply_core_map_update** -> str
- **_apply_signals_update** -> str
- **_request_user_approval** -> bool
- **_validate_blueprint_syntax** -> bool
- **_rollback_to_backup** -> None
- **post_heal_validation** -> dict[str, Any]
- **cleanup_violations** -> list[dict[str, Any]]
- **run_with_cleanup** -> dict[str, Any]
- **detect_root_drift** -> dict[str, Any]
- **scan_root_folders** -> dict[str, Any]
- **heal_repository** -> dict[str, int]


## Class: ReconciliationViolation

**Description**: Structured violation for blueprint reconciliation healing.

### Methods

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L0 maintenance agent - operational only.



## Class: FilesystemSSOTReconcilerAgent

**Description**: Filesystem-level SSOT enforcer - treats blueprint as the Gospel.

    Inherits from L0RoutingBaseAgent: HealerMixin, MCPHardenedMixin, L0DelegationTestingMixin

    Enforces the SSOT blueprint by aligning the filesystem:
    - Creation: Ensures all folders in sovereign_registry exist.
    - Archival: Moves unauthorized folders to /.healing_backups/unmapped_drift/.
    - Validation: Post-alignment check with LocationAgent/HierarchyAgent.

    Direction: Blueprint → Filesystem
    SSOT: structure_blueprint.py is the immutable source.

    Safety mechanisms:
    - No-deletion policy (unauthorized folders are MOVED to .healing_backups/).
    - Path validation to prevent root-level accidental modifications.
    - Dry-run mode by default (auto_apply=False)
    

**Inherits from**: AutonomyMixin, SelfDiagnosisMixin, L0RoutingBaseAgent

### Methods

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: 
        [SOVEREIGN CONTRACT] Standardized healing interface for SSOT reconciliation.
        

#### __init__
**Parameters**: self, project_root, enforcement_mode
**Returns**: None
**Description**: Initialize the instance.

#### run_ci_verification_sync
**Parameters**: self
**Returns**: tuple[bool, dict]
**Description**: 
        Synchronous CI verification for pre-commit hooks and CLI tools.

        Phase 5.1 Upgrade: Non-interactive, headless verification mode.
        Returns (is_compliant, results_dict) for easy CI integration.

        Usage:
            is_compliant, results = agent.run_ci_verification_sync()
            sys.exit(0 if is_compliant else 1)
        

#### _create_no_drift_result
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Create result for no drift detected.

#### _create_rejected_result
**Parameters**: self, proposals, message
**Returns**: dict[str, Any]
**Description**: Create result for rejected/aborted changes.

#### _create_applied_result
**Parameters**: self, proposals, results
**Returns**: dict[str, Any]
**Description**: Create result for successfully applied changes.

#### _handle_interactive_approval
**Parameters**: self, proposals
**Returns**: tuple[bool, dict[str, Any] | None]
**Description**: Handle interactive approval flow. Returns (should_apply, early_return_result).

#### _load_current_blueprint
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Load current blueprint values by dynamically importing it.

        Returns dict with:
        - sovereign_registry
        - core_subfolder_map
        - CANON_SIGNALS
        

#### _detect_drift
**Parameters**: self, current_blueprint
**Returns**: list[dict[str, Any]]
**Description**: 
        Compare actual state vs blueprint, return list of drift items.

        Checks:
        1. sovereign_registry subfolders (L1 depth)
        2. core_subfolder_map (L2 depth for agentic_core)
        3. CANON_SIGNALS (agent-derived signals)
        

#### _check_registry_subfolders
**Parameters**: self, current_blueprint, drift
**Returns**: None
**Description**: 
        Check SOVEREIGN_REGISTRY subfolders.

        Checks:
        - Missing subfolders in actual state
        - Extra subfolders in blueprint
        

#### _check_l2_subfolders
**Parameters**: self, current_blueprint, drift
**Returns**: None
**Description**: 
        Check CORE_SUBFOLDER_MAP (L2 depth).

        Checks:
        - Missing L2 subfolders in actual state
        

#### _check_canon_signals
**Parameters**: self, current_blueprint, drift
**Returns**: None
**Description**: 
        Check CANON_SIGNALS.

        Checks:
        - Missing signals in actual state
        

#### _check_registry_subfolders
**Parameters**: self, current_blueprint, drift
**Returns**: None
**Description**: Check SOVEREIGN_REGISTRY subfolders for drift.

#### _check_l2_subfolders
**Parameters**: self, current_blueprint, drift
**Returns**: None
**Description**: Check CORE_SUBFOLDER_MAP (L2 depth) for drift.

#### _check_canon_signals
**Parameters**: self, current_blueprint, drift
**Returns**: None
**Description**: Check CANON_SIGNALS for drift.

#### _generate_filesystem_proposals
**Parameters**: self, drift
**Returns**: list[dict[str, Any]]
**Description**: Generates OS-level folder actions to match blueprint.

#### _apply_filesystem_alignment
**Parameters**: self, proposals
**Returns**: list[str]
**Description**: Executes the terraforming actions on disk with SurgicalContext logging.

#### _backup_blueprint
**Parameters**: self
**Returns**: Path
**Description**: Create timestamped backup before modifications.

#### _apply_proposals
**Parameters**: self, proposals
**Returns**: None
**Description**: 
        Apply proposals by modifying structure_blueprint.py.

        Uses string-based updates for safe append-style modifications.
        Atomic write at the end via tempfile + rename.
        

#### _apply_sovereign_registry_update
**Parameters**: self, content, root, folders
**Returns**: str
**Description**: 
        Add subfolders to sovereign_registry[root]['subfolders'].

        Strategy: Find the line with the root key and 'subfolders', insert extend() call.
        

#### _apply_core_map_update
**Parameters**: self, content, l1_folder, folders
**Returns**: str
**Description**: 
        Add subfolders to core_subfolder_map[l1_folder].

        Strategy: Find the line with the l1_folder key, insert extend() call.
        

#### _apply_signals_update
**Parameters**: self, content, signals
**Returns**: str
**Description**: 
        Add signals to CANON_SIGNALS set.

        Strategy: Find CANON_SIGNALS definition, insert update() call.
        

#### _request_user_approval
**Parameters**: self, proposals
**Returns**: bool
**Description**: 
        Interactive approval for blueprint changes (Phase 2).

        Displays proposed changes and requests user confirmation.

        Args:
            proposals: List of reconciliation proposals

        Returns:
            True if user approves, False if rejected

        Raises:
            KeyboardInterrupt: If user chooses to quit
        

#### _validate_blueprint_syntax
**Parameters**: self
**Returns**: bool
**Description**: 
        Ensure blueprint is still valid Python after modifications.

        Returns:
            True if syntax is valid, False otherwise
        

#### _rollback_to_backup
**Parameters**: self, backup_path
**Returns**: None
**Description**: 
        Restore blueprint from backup (Phase 3 safety mechanism).

        Args:
            backup_path: Path to backup file to restore from
        

#### post_heal_validation
**Parameters**: self, affected_paths, dry_run
**Returns**: dict[str, Any]
**Description**: 
        GOLD STANDARD: Post-heal validation confirming blueprint sync.
        Verifies blueprint was successfully updated and syntax is valid.

        Args:
            affected_paths: Paths affected by reconciliation
            dry_run: If True, only preview without applying

        Returns:
            Dict with validation status and details
        

#### cleanup_violations
**Parameters**: self, violations, dry_run, max_actions
**Returns**: list[dict[str, Any]]
**Description**: 
        GOLD STANDARD: Cleanup reconciliation violations with blueprint updates.

        Args:
            violations: List of ReconciliationViolation objects
            dry_run: If True, only preview actions
            max_actions: Maximum cleanup actions per run

        Returns:
            List of action dicts with results and batch summary
        

#### run_with_cleanup
**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: 
        GOLD STANDARD: Full reconciliation with autonomous cleanup.
        Scans filesystem, detects drift, and reconciles blueprint.

        Args:
            dry_run: If True, only preview cleanup actions

        Returns:
            Dict with comprehensive execution and cleanup summaries
        

#### detect_root_drift
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Detect root-level SSOT drift.

        Checks for:
        1. Forbidden folders at project root
        2. .archived files at root (should be in archives/)
        3. Folders that duplicate SSOT locations

        Returns:
            Dict with drift details
        

#### scan_root_folders
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Alias for detect_root_drift for API compatibility.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path, force
**Returns**: dict[str, int]
**Description**: L0 maintenance agent - operational only.

        Wave 3 fix: when force=True, runs detect_root_drift() instead of
        returning skipped immediately.  The skip-gate exists to prevent
        accidental recursive invocations; force=True is the explicit
        caller opt-in (passed by execute_ssot.py).
        



## Class: MCPHardenedMixin



## Class: SubatomicTestingMixin

**Description**: Fallback stub for SubatomicTestingMixin.



## Function: _evict_blueprint_modules

**Returns**: None
**Description**: Evict stale structure_blueprint submodules from sys.modules.

    Called immediately after any on-disk write to a blueprint/constants file so
    that the next import re-executes the module and picks up the new
    SOVEREIGN_TERRITORIES / is_path_allowed definitions.

    REQ-417 blocks importlib.reload() on core modules but does NOT block
    deletion from sys.modules — eviction via pop() is the safe path.
    importlib.invalidate_caches() then tells the import machinery to rescan
    the filesystem for new/changed .py files.
    



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L0 maintenance agent - operational only.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: 
        [SOVEREIGN CONTRACT] Standardized healing interface for SSOT reconciliation.
        



## Function: __init__

**Parameters**: self, project_root, enforcement_mode
**Returns**: None
**Description**: Initialize the instance.



## Function: run_ci_verification_sync

**Parameters**: self
**Returns**: tuple[bool, dict]
**Description**: 
        Synchronous CI verification for pre-commit hooks and CLI tools.

        Phase 5.1 Upgrade: Non-interactive, headless verification mode.
        Returns (is_compliant, results_dict) for easy CI integration.

        Usage:
            is_compliant, results = agent.run_ci_verification_sync()
            sys.exit(0 if is_compliant else 1)
        



## Function: _create_no_drift_result

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Create result for no drift detected.



## Function: _create_rejected_result

**Parameters**: self, proposals, message
**Returns**: dict[str, Any]
**Description**: Create result for rejected/aborted changes.



## Function: _create_applied_result

**Parameters**: self, proposals, results
**Returns**: dict[str, Any]
**Description**: Create result for successfully applied changes.



## Function: _handle_interactive_approval

**Parameters**: self, proposals
**Returns**: tuple[bool, dict[str, Any] | None]
**Description**: Handle interactive approval flow. Returns (should_apply, early_return_result).



## Function: _load_current_blueprint

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Load current blueprint values by dynamically importing it.

        Returns dict with:
        - sovereign_registry
        - core_subfolder_map
        - CANON_SIGNALS
        



## Function: _detect_drift

**Parameters**: self, current_blueprint
**Returns**: list[dict[str, Any]]
**Description**: 
        Compare actual state vs blueprint, return list of drift items.

        Checks:
        1. sovereign_registry subfolders (L1 depth)
        2. core_subfolder_map (L2 depth for agentic_core)
        3. CANON_SIGNALS (agent-derived signals)
        



## Function: _check_registry_subfolders

**Parameters**: self, current_blueprint, drift
**Returns**: None
**Description**: 
        Check SOVEREIGN_REGISTRY subfolders.

        Checks:
        - Missing subfolders in actual state
        - Extra subfolders in blueprint
        



## Function: _check_l2_subfolders

**Parameters**: self, current_blueprint, drift
**Returns**: None
**Description**: 
        Check CORE_SUBFOLDER_MAP (L2 depth).

        Checks:
        - Missing L2 subfolders in actual state
        



## Function: _check_canon_signals

**Parameters**: self, current_blueprint, drift
**Returns**: None
**Description**: 
        Check CANON_SIGNALS.

        Checks:
        - Missing signals in actual state
        



## Function: _check_registry_subfolders

**Parameters**: self, current_blueprint, drift
**Returns**: None
**Description**: Check SOVEREIGN_REGISTRY subfolders for drift.



## Function: _check_l2_subfolders

**Parameters**: self, current_blueprint, drift
**Returns**: None
**Description**: Check CORE_SUBFOLDER_MAP (L2 depth) for drift.



## Function: _check_canon_signals

**Parameters**: self, current_blueprint, drift
**Returns**: None
**Description**: Check CANON_SIGNALS for drift.



## Function: _generate_filesystem_proposals

**Parameters**: self, drift
**Returns**: list[dict[str, Any]]
**Description**: Generates OS-level folder actions to match blueprint.



## Function: _apply_filesystem_alignment

**Parameters**: self, proposals
**Returns**: list[str]
**Description**: Executes the terraforming actions on disk with SurgicalContext logging.



## Function: _backup_blueprint

**Parameters**: self
**Returns**: Path
**Description**: Create timestamped backup before modifications.



## Function: _apply_proposals

**Parameters**: self, proposals
**Returns**: None
**Description**: 
        Apply proposals by modifying structure_blueprint.py.

        Uses string-based updates for safe append-style modifications.
        Atomic write at the end via tempfile + rename.
        



## Function: _apply_sovereign_registry_update

**Parameters**: self, content, root, folders
**Returns**: str
**Description**: 
        Add subfolders to sovereign_registry[root]['subfolders'].

        Strategy: Find the line with the root key and 'subfolders', insert extend() call.
        



## Function: _apply_core_map_update

**Parameters**: self, content, l1_folder, folders
**Returns**: str
**Description**: 
        Add subfolders to core_subfolder_map[l1_folder].

        Strategy: Find the line with the l1_folder key, insert extend() call.
        



## Function: _apply_signals_update

**Parameters**: self, content, signals
**Returns**: str
**Description**: 
        Add signals to CANON_SIGNALS set.

        Strategy: Find CANON_SIGNALS definition, insert update() call.
        



## Function: _request_user_approval

**Parameters**: self, proposals
**Returns**: bool
**Description**: 
        Interactive approval for blueprint changes (Phase 2).

        Displays proposed changes and requests user confirmation.

        Args:
            proposals: List of reconciliation proposals

        Returns:
            True if user approves, False if rejected

        Raises:
            KeyboardInterrupt: If user chooses to quit
        



## Function: _validate_blueprint_syntax

**Parameters**: self
**Returns**: bool
**Description**: 
        Ensure blueprint is still valid Python after modifications.

        Returns:
            True if syntax is valid, False otherwise
        



## Function: _rollback_to_backup

**Parameters**: self, backup_path
**Returns**: None
**Description**: 
        Restore blueprint from backup (Phase 3 safety mechanism).

        Args:
            backup_path: Path to backup file to restore from
        



## Function: post_heal_validation

**Parameters**: self, affected_paths, dry_run
**Returns**: dict[str, Any]
**Description**: 
        GOLD STANDARD: Post-heal validation confirming blueprint sync.
        Verifies blueprint was successfully updated and syntax is valid.

        Args:
            affected_paths: Paths affected by reconciliation
            dry_run: If True, only preview without applying

        Returns:
            Dict with validation status and details
        



## Function: cleanup_violations

**Parameters**: self, violations, dry_run, max_actions
**Returns**: list[dict[str, Any]]
**Description**: 
        GOLD STANDARD: Cleanup reconciliation violations with blueprint updates.

        Args:
            violations: List of ReconciliationViolation objects
            dry_run: If True, only preview actions
            max_actions: Maximum cleanup actions per run

        Returns:
            List of action dicts with results and batch summary
        



## Function: run_with_cleanup

**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: 
        GOLD STANDARD: Full reconciliation with autonomous cleanup.
        Scans filesystem, detects drift, and reconciles blueprint.

        Args:
            dry_run: If True, only preview cleanup actions

        Returns:
            Dict with comprehensive execution and cleanup summaries
        



## Function: detect_root_drift

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Detect root-level SSOT drift.

        Checks for:
        1. Forbidden folders at project root
        2. .archived files at root (should be in archives/)
        3. Folders that duplicate SSOT locations

        Returns:
            Dict with drift details
        



## Function: scan_root_folders

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Alias for detect_root_drift for API compatibility.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path, force
**Returns**: dict[str, int]
**Description**: L0 maintenance agent - operational only.

        Wave 3 fix: when force=True, runs detect_root_drift() instead of
        returning skipped immediately.  The skip-gate exists to prevent
        accidental recursive invocations; force=True is the explicit
        caller opt-in (passed by execute_ssot.py).
        



## Usage Examples

### Class Usage

```python
# Using ReconciliationViolation
reconciliationviolation = ReconciliationViolation()
reconciliationviolation.heal_repository()
```

```python
# Using FilesystemSSOTReconcilerAgent
filesystemssotreconcileragent = FilesystemSSOTReconcilerAgent()
filesystemssotreconcileragent.heal()
filesystemssotreconcileragent.run_ci_verification_sync()
```

```python
# Using MCPHardenedMixin
mcphardenedmixin = MCPHardenedMixin()
```

### Function Usage

```python
# Using _evict_blueprint_modules
result = _evict_blueprint_modules()
```

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```

```python
# Using heal
result = heal(violation)
```



---
**Generated**: 2026-03-26T09:39:05.209467
**Type**: api_reference
**Quality**: comprehensive
