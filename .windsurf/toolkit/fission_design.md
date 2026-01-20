# LocationAgent Fission Design Document

**Date:** 2026-01-20  
**Status:** Design Phase - Awaiting Review  
**Current File:** `agentic_core/L5_safety/validators/LocationAgent.py` (2138 lines)

---

## Executive Summary

LocationAgent violates the Single Responsibility Principle by handling:
1. **Validation** - Structural compliance checking
2. **Healing** - Automated file movement and archiving
3. **Gravity Detection** - Cross-boundary dependency analysis

**Proposed Split:** Fission into 3 focused agents following SRP.

---

## Method Inventory (72 total methods)

### Module-Level Functions (3)
1. `_get_python_files(project_root)` - File discovery utility
2. `is_path_compliant(file_path, project_root)` - L5 Sovereign SSOT for path validation
3. `is_excepted_from_key(key_id, file_path, line_content)` - Exception checking

### Class: LocationAgent (69 methods)

#### Initialization & Properties (5)
- `__init__(project_root)` - Constructor
- `naming_agent` - Lazy property for NamingAgent
- `import_agent` - Lazy property for ImportAgent
- `_validate_project_root()` - Root validation
- `safe_create_directory(relative_path)` - Directory creation utility

#### Core Validation Methods (18)
- `validate_sovereign_roots()` - Ensure sovereign roots exist
- `validate_file_location(file_path)` - Main per-file validation
- `_validate_ast_violations(root_folder, file_path, rel_path)` - AST-based checks
- `_check_forbidden_imports(tree, current_l1, rel_path)` - Import validation
- `_scan_imports_for_violations(tree, current_l1)` - Import scanner
- `_extract_modules_from_node(node)` - AST module extraction
- `_is_forbidden_app_import(module)` - App import checker
- `_check_layer_import_violation(module, current_l1)` - Layer violation checker
- `_check_semantic_alignment(tree, current_territory, rel_path)` - Semantic validation
- `_calculate_semantic_scores(tree)` - AST scoring
- `_check_app_domain_violation(app_rg_score, app_lic_score, rel_path)` - Domain checker
- `_check_territory_alignment(current_territory, territory_scores, rel_path)` - Territory checker
- `_validate_final_checks(root_folder, file_path, parts)` - Final validation
- `_validate_forbidden_patterns(parts, root_folder)` - Pattern validation
- `_validate_root_whitelist(root_folder, rel_path)` - Whitelist validation
- `_validate_depth_requirements(parts, root_folder, rel_path)` - Depth validation
- `_validate_app_specific_files(root_folder, file_path)` - App-specific checker
- `_validate_filename_patterns(file_path)` - Filename pattern validation

#### Healing Methods (14)
- `_apply_healing_strategy(file_path, msg, archives_root, dry_run, affected_paths, import_touched_paths)` - Strategy dispatcher
- `_heal_broken_backup(file_path, dry_run, affected_paths)` - Backup file healing
- `_heal_app_specific_violation(file_path, msg, dry_run, affected_paths, import_touched_paths)` - App-specific healing
- `_heal_territory_mismatch(file_path, msg, dry_run, affected_paths, import_touched_paths)` - Territory healing
- `_heal_depth_violation(file_path, msg, dry_run, affected_paths, import_touched_paths)` - Depth healing
- `_heal_via_archiving(file_path, msg, archives_root, dry_run, affected_paths)` - Archive healing
- `safe_move(src_path, dst_path, dry_run)` - Safe file move with backup
- `safe_delete(file_path, dry_run)` - Safe file delete with backup
- `_backup_file(file_path)` - Create backup
- `_init_backup_dir()` - Initialize backup directory
- `fix_imports_after_move(old_path, new_path, dry_run)` - Import fixing
- `post_heal_validation(old_path, new_path, dry_run)` - Post-heal validation
- `post_naming_validation(affected_paths, dry_run)` - Naming validation
- `post_import_validation_and_heal(affected_paths, dry_run)` - Import validation

#### Gravity Detection Methods (8)
- `_heal_gravity_violations(file_path, msg, dry_run, affected_paths)` - Gravity healing
- `_insert_gravity_heal_todo(file_path, downstream_roots)` - Insert TODO markers
- `_extract_downstream_roots(tree)` - Extract downstream dependencies
- `_find_todo_insert_position(lines)` - Find TODO insertion point
- `_backup_and_write_file(file_path, new_content)` - Backup and write
- `deep_import_validation_and_heal(affected_paths, dry_run)` - Deep import validation
- `post_naming_conventions_validation_and_heal(affected_paths, dry_run)` - Naming conventions
- `deep_naming_validation_and_heal(affected_paths, dry_run)` - Deep naming validation

#### Naming Integration Methods (11)
- `auto_heal_naming_issues(file_path, dry_run)` - Auto-heal naming
- `_collect_naming_violations(file_path)` - Collect violations
- `_apply_naming_heals(file_path, violations, dry_run)` - Apply naming fixes
- `_check_naming_conventions(file_path)` - Check conventions
- `_apply_convention_fixes(file_path, violations, dry_run)` - Apply fixes
- `_set_naming_final_status(naming_result)` - Set status
- `_insert_semantic_keywords(file_path, keywords)` - Insert keywords
- `_insert_sovereign_marker(file_path)` - Insert marker
- `_check_high_signal_keywords(tree)` - Check keywords
- `_check_sovereign_markers(content)` - Check markers
- `_find_docstring_end(lines)` - Find docstring end

#### AST Scoring Utilities (7)
- `_collect_ast_increments(tree, territory_keywords)` - Collect increments
- `_aggregate_ast_increments(increments)` - Aggregate scores
- `_recompute_ast_scores(tree, territory_keywords)` - Recompute scores
- `_score_identifier(name, territory_keywords)` - Score identifier
- `_score_string(value, territory_keywords)` - Score string
- `_score_variable(name, territory_keywords)` - Score variable
- `_score_assignments(node, territory_keywords)` - Score assignments
- `_score_arguments(node, territory_keywords)` - Score arguments

#### Orchestration Methods (6)
- `run()` - Main execution entry point
- `run_with_cleanup(dry_run)` - Run with cleanup
- `heal_repository(dry_run, execute)` - Repository healing
- `enforce_void_compliance()` - Legacy compliance enforcement
- `cleanup_violations(violations, dry_run)` - Cleanup violations
- `sort_key(violation)` - Sort key for violations

#### Utility Methods (2)
- `_compute_module_path(file_path)` - Compute module path
- `_remove_offending_imports(file_path, forbidden_modules, dry_run)` - Remove imports

---

## Proposed Agent Assignments

### 1. LocationValidatorAgent (Validation Focus)
**Responsibility:** Pure validation - no side effects, no healing

**Methods (28):**
- `validate_sovereign_roots()`
- `validate_file_location(file_path)`
- `_validate_ast_violations()`
- `_check_forbidden_imports()`
- `_scan_imports_for_violations()`
- `_extract_modules_from_node()`
- `_is_forbidden_app_import()`
- `_check_layer_import_violation()`
- `_check_semantic_alignment()`
- `_calculate_semantic_scores()`
- `_check_app_domain_violation()`
- `_check_territory_alignment()`
- `_validate_final_checks()`
- `_validate_forbidden_patterns()`
- `_validate_root_whitelist()`
- `_validate_depth_requirements()`
- `_validate_app_specific_files()`
- `_validate_filename_patterns()`
- `_collect_ast_increments()`
- `_aggregate_ast_increments()`
- `_recompute_ast_scores()`
- `_score_identifier()`
- `_score_string()`
- `_score_variable()`
- `_score_assignments()`
- `_score_arguments()`
- `_check_naming_conventions()`
- `run()` - Validation-only orchestration

**Shared Dependencies:**
- `structure_blueprint` constants (SOVEREIGN_REGISTRY, ROOT_WHITELIST, etc.)
- AST parsing utilities
- Naming/Import agent lazy properties

---

### 2. LocationHealerAgent (Healing Focus)
**Responsibility:** Automated remediation, file operations, import fixing

**Methods (25):**
- `_apply_healing_strategy()`
- `_heal_broken_backup()`
- `_heal_app_specific_violation()`
- `_heal_territory_mismatch()`
- `_heal_depth_violation()`
- `_heal_via_archiving()`
- `safe_move()`
- `safe_delete()`
- `safe_create_directory()`
- `_backup_file()`
- `_init_backup_dir()`
- `_backup_and_write_file()`
- `fix_imports_after_move()`
- `post_heal_validation()`
- `post_naming_validation()`
- `post_import_validation_and_heal()`
- `auto_heal_naming_issues()`
- `_collect_naming_violations()`
- `_apply_naming_heals()`
- `_apply_convention_fixes()`
- `_set_naming_final_status()`
- `_insert_semantic_keywords()`
- `_insert_sovereign_marker()`
- `_find_docstring_end()`
- `_remove_offending_imports()`
- `heal_repository()` - Main healing orchestration
- `cleanup_violations()`

**Shared Dependencies:**
- Backup directory management
- NamingAgent/ImportAgent integration
- File I/O utilities

---

### 3. GravityLeakDetector (Gravity Focus)
**Responsibility:** Cross-boundary dependency detection and TODO insertion

**Methods (11):**
- `_heal_gravity_violations()`
- `_insert_gravity_heal_todo()`
- `_extract_downstream_roots()`
- `_find_todo_insert_position()`
- `deep_import_validation_and_heal()`
- `post_naming_conventions_validation_and_heal()`
- `deep_naming_validation_and_heal()`
- `_check_high_signal_keywords()`
- `_check_sovereign_markers()`
- `run()` - Gravity detection orchestration
- `enforce_void_compliance()` - Legacy compliance

**Shared Dependencies:**
- AST parsing for dependency extraction
- File content analysis
- TODO marker insertion utilities

---

## Shared Infrastructure Needs

### Constants to Extract (create `location_constants.py`)
- `ARCHIVE_SUBFOLDERS` - Archive mapping
- `HEALING_STRATEGY_MAP` - Strategy dispatcher map
- AST scoring thresholds (AST_DOMAIN_HIT_THRESHOLD, etc.)
- Forbidden patterns and modules

### Utilities to Extract (create `location_utils.py`)
- `_get_python_files()` - File discovery
- `is_path_compliant()` - SSOT path validation
- `is_excepted_from_key()` - Exception checking
- `_compute_module_path()` - Module path computation
- `sort_key()` - Violation sorting

### Base Class Pattern
All three agents should inherit from `SovereignBaseAgent` and share:
- `project_root` initialization
- `_validate_project_root()` logic
- Lazy agent properties (naming_agent, import_agent)

---

## Migration Strategy

### Phase 1: Create Shells (Current Step)
1. Create empty class files with SovereignBaseAgent inheritance
2. Add basic `__init__` and docstrings
3. No code migration yet

### Phase 2: Extract Shared Infrastructure
1. Create `location_constants.py`
2. Create `location_utils.py`
3. Update all three shells to import shared code

### Phase 3: Migrate Methods (ZLM Protocol)
1. **Validator first** - Pure functions, no side effects
2. **Healer second** - File operations, depends on validator
3. **Gravity last** - Depends on both validator and healer

### Phase 4: Integration Testing
1. Update imports in dependent agents
2. Run full test suite (637 tests)
3. Verify no regressions

### Phase 5: Deprecate Original
1. Mark `LocationAgent.py` as deprecated
2. Create facade pattern for backward compatibility
3. Schedule removal after 1 release cycle

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Circular dependencies between agents | High | Use dependency injection, lazy loading |
| Import path updates across codebase | Medium | Automated import fixing via grep/sed |
| Test suite breakage | High | ZLM protocol with shadow backups |
| Performance regression | Low | Shared utilities prevent duplication |
| Naming conflicts | Low | Clear agent naming conventions |

---

## Success Criteria

✅ Each agent has <800 lines  
✅ Single Responsibility Principle enforced  
✅ All 637 tests pass  
✅ No circular dependencies  
✅ Backward compatibility maintained  
✅ Performance neutral or improved  

---

## Next Steps

1. **Review this design** - Verify method assignments are logical
2. **Create shadow shells** - Empty class files ready for migration
3. **Extract shared infrastructure** - Constants and utilities
4. **Begin ZLM migration** - Start with LocationValidatorAgent

**AWAITING APPROVAL TO PROCEED WITH SHELL CREATION**
