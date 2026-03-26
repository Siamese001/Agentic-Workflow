# API Documentation: location_validator

**Target Audience**: developers, api_users

# location_validator API Documentation

**File**: `location_validator.py`
**Classes**: 1
**Functions**: 33

## Classes

- **LocationValidatorAgent** (inherits from SovereignBaseAgent)

## Functions

- **__post_init__**
- **heal** -> dict[str, Any]
- **heal_repository** -> dict
- **validate_sovereign_roots** -> list[tuple[Path, str]]
- **validate_file_location** -> tuple[bool, str]
- **_validate_forbidden_patterns** -> tuple[bool, str]
- **_validate_root_whitelist** -> tuple[bool, str]
- **_validate_scripts_isolation** -> tuple[bool, str]
- **_validate_depth_requirements** -> tuple[bool, str]
- **_validate_app_specific_files** -> tuple[bool, str]
- **_validate_filename_patterns** -> tuple[bool, str]
- **_validate_final_checks** -> tuple[bool, str]
- **_validate_ast_violations** -> tuple[bool, str]
- **_check_forbidden_imports** -> tuple[bool, str]
- **_scan_imports_for_violations** -> tuple[bool, str | None]
- **_extract_modules_from_node** -> list[str]
- **_is_forbidden_app_import** -> bool
- **_check_layer_import_violation** -> str | None
- **_check_semantic_alignment** -> tuple[bool, str]
- **_calculate_semantic_scores** -> tuple[float, float, dict[str, float]]
- **_check_app_domain_violation** -> tuple[bool, str]
- **_check_territory_alignment** -> tuple[bool, str]
- **_collect_ast_increments** -> list[tuple[str, float]]
- **_aggregate_ast_increments** -> dict[str, float]
- **_recompute_ast_scores** -> tuple[float, float, dict[str, float]]
- **_score_identifier** -> float
- **_score_string** -> float
- **_score_variable** -> float
- **_score_assignments** -> float
- **_score_arguments** -> float
- **enforce_void_compliance** -> tuple[list[Path], list[tuple[Path, str]]]
- **_check_naming_conventions** -> list[str]
- **run** -> dict[str, Any]


## Class: LocationValidatorAgent

**Description**: 
    Pure validation agent for territorial compliance.

    Validates:
    - Root folder whitelist compliance
    - Depth requirements per sovereign root
    - Forbidden patterns and numbered folders
    - AST-based semantic alignment
    - Import layer violations
    - App-specific file placement

    Does NOT perform:
    - File moves or deletions
    - Automated healing
    - Backup operations

    Use LocationHealerAgent for remediation.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Description**: Initialize validator with project root validation.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for location violations.

        Note: LocationValidatorAgent is validation-only and does not perform healing.
        Use LocationHealerAgent for actual remediation.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for LocationValidatorAgent.

#### validate_sovereign_roots
**Parameters**: self
**Returns**: list[tuple[Path, str]]
**Description**: Ensure all required sovereign roots exist and are directories.

#### validate_file_location
**Parameters**: self, file_path
**Returns**: tuple[bool, str]
**Description**: Per-file location validation with correct forbidden-check ordering.

        [CONSTITUTIONAL OVERRIDE 2026-01-22]
        SovereignBaseAgent and Layer Base Agents have 'Semantic Location Immunity'
        from standard rules but MUST reside in 'agentic_core/base_agents/'.
        This check runs BEFORE standard validation to prevent validator logic gaps.
        

#### _validate_forbidden_patterns
**Parameters**: self, parts, root_folder
**Returns**: tuple[bool, str]
**Description**: Validate forbidden folder patterns and numbered roots.

#### _validate_root_whitelist
**Parameters**: self, root_folder, rel_path
**Returns**: tuple[bool, str]
**Description**: Validate path is within an allowed sovereign territory using SSOT helper.

#### _validate_scripts_isolation
**Parameters**: self, file_path
**Returns**: tuple[bool, str]
**Description**: 
        Enforces strict isolation for root scripts.

        Root scripts (`scripts/`) are for standalone utilities/setup only.
        They MUST NOT import from `agentic_core`.

        If a script imports `agentic_core`, it is part of the system
        and belongs in `agentic_core/L0_routing/scripts/`.
        

#### _validate_depth_requirements
**Parameters**: self, parts, root_folder, rel_path
**Returns**: tuple[bool, str]
**Description**: Validate depth requirements from sovereign registry.

        SSOT FIX: Allow variable depth for certain subfolders that legitimately
        have deeper structures (e.g., utils/core_extensions/, config/core/).

        [2026-02-08] FLAT DIRECTORY ENFORCEMENT: Directories in FLAT_DIRECTORIES
        must not contain any subdirectories. This check runs BEFORE depth checks
        to catch violations like mixins/contracts/ that bypass depth validation.
        

#### _validate_app_specific_files
**Parameters**: self, root_folder, file_path
**Returns**: tuple[bool, str]
**Description**: Validate app-specific files are not in core.

#### _validate_filename_patterns
**Parameters**: self, file_path
**Returns**: tuple[bool, str]
**Description**: Validate filename patterns for forbidden prefixes and backup files.

#### _validate_final_checks
**Parameters**: self, root_folder, file_path, parts
**Returns**: tuple[bool, str]
**Description**: Final validation checks for root-level files and gravity leaks.

#### _validate_ast_violations
**Parameters**: self, root_folder, file_path, rel_path
**Returns**: tuple[bool, str]
**Description**: Validate AST-based violations for agentic_core Python files.

#### _check_forbidden_imports
**Parameters**: self, tree, current_l1, rel_path
**Returns**: tuple[bool, str]
**Description**: Check for forbidden app imports and layer violations.

#### _scan_imports_for_violations
**Parameters**: self, tree, current_l1
**Returns**: tuple[bool, str | None]
**Description**: Scan AST for forbidden imports and return violation flags.

#### _extract_modules_from_node
**Parameters**: self, node
**Returns**: list[str]
**Description**: Extract module names from import node.

#### _is_forbidden_app_import
**Parameters**: self, module
**Returns**: bool
**Description**: Check if module is a forbidden app import.

#### _check_layer_import_violation
**Parameters**: self, module, current_l1
**Returns**: str | None
**Description**: Check for layer import violations and return violation description.

        [RECONCILED 2026-01-27] Now enforces:
        1. Core layer gravity (L1-L5 import direction)
        2. App-layer horizontal isolation (apps_shared independence)
        

#### _check_semantic_alignment
**Parameters**: self, tree, current_territory, rel_path
**Returns**: tuple[bool, str]
**Description**: Check semantic alignment between file location and content.

        [DEDUP 2026-02-07] Delegates file classification to FCA for consistent
        territory alignment instead of reimplementing AST scoring locally.
        

#### _calculate_semantic_scores
**Parameters**: self, tree
**Returns**: tuple[float, float, dict[str, float]]
**Description**: Calculate semantic scores for app and territory alignment.

#### _check_app_domain_violation
**Parameters**: self, app_rg_score, app_lic_score, rel_path
**Returns**: tuple[bool, str]
**Description**: 
        [HARDENED] Detects cross-contamination AND Global Candidates for apps_shared.
        [SSOT 2026-01-27] Implements the 'Shared Vacuum' logic.
        

#### _check_territory_alignment
**Parameters**: self, current_territory, territory_scores, rel_path
**Returns**: tuple[bool, str]
**Description**: Check territory alignment between file location and content.

#### _collect_ast_increments
**Parameters**: self, tree, territory_keywords
**Returns**: list[tuple[str, float]]
**Description**: Collect AST-based scoring increments.

#### _aggregate_ast_increments
**Parameters**: self, increments
**Returns**: dict[str, float]
**Description**: Aggregate scoring increments into territory scores.

#### _recompute_ast_scores
**Parameters**: self, tree, territory_keywords
**Returns**: tuple[float, float, dict[str, float]]
**Description**: Recompute AST scores (wrapper for _calculate_semantic_scores).

#### _score_identifier
**Parameters**: self, name, territory_keywords
**Returns**: float
**Description**: Score an identifier name against territory keywords.

#### _score_string
**Parameters**: self, value, territory_keywords
**Returns**: float
**Description**: Score a string value against territory keywords.

#### _score_variable
**Parameters**: self, name, territory_keywords
**Returns**: float
**Description**: Score a variable name against territory keywords.

#### _score_assignments
**Parameters**: self, node, territory_keywords
**Returns**: float
**Description**: Score assignment nodes.

#### _score_arguments
**Parameters**: self, node, territory_keywords
**Returns**: float
**Description**: Score function arguments.

#### enforce_void_compliance
**Parameters**: self, files
**Returns**: tuple[list[Path], list[tuple[Path, str]]]
**Description**: Filter files and collect all location-based violations.

        Salvaged from LocationAgent.py during LCD+ decommission.
        

#### _check_naming_conventions
**Parameters**: self, file_path
**Returns**: list[str]
**Description**: Check naming conventions for file.

#### run
**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: 
        Execute validation-only scan across sovereign territories.

        Args:
            target_territory: If provided, restricts scan to this domain (Strict Targeting).

        Phase 4.1 Upgrade: Universal root scanning using PROJECT_ROOT_WHITELIST.
        



## Function: __post_init__

**Parameters**: self
**Description**: Initialize validator with project root validation.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for location violations.

        Note: LocationValidatorAgent is validation-only and does not perform healing.
        Use LocationHealerAgent for actual remediation.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        



## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for LocationValidatorAgent.



## Function: validate_sovereign_roots

**Parameters**: self
**Returns**: list[tuple[Path, str]]
**Description**: Ensure all required sovereign roots exist and are directories.



## Function: validate_file_location

**Parameters**: self, file_path
**Returns**: tuple[bool, str]
**Description**: Per-file location validation with correct forbidden-check ordering.

        [CONSTITUTIONAL OVERRIDE 2026-01-22]
        SovereignBaseAgent and Layer Base Agents have 'Semantic Location Immunity'
        from standard rules but MUST reside in 'agentic_core/base_agents/'.
        This check runs BEFORE standard validation to prevent validator logic gaps.
        



## Function: _validate_forbidden_patterns

**Parameters**: self, parts, root_folder
**Returns**: tuple[bool, str]
**Description**: Validate forbidden folder patterns and numbered roots.



## Function: _validate_root_whitelist

**Parameters**: self, root_folder, rel_path
**Returns**: tuple[bool, str]
**Description**: Validate path is within an allowed sovereign territory using SSOT helper.



## Function: _validate_scripts_isolation

**Parameters**: self, file_path
**Returns**: tuple[bool, str]
**Description**: 
        Enforces strict isolation for root scripts.

        Root scripts (`scripts/`) are for standalone utilities/setup only.
        They MUST NOT import from `agentic_core`.

        If a script imports `agentic_core`, it is part of the system
        and belongs in `agentic_core/L0_routing/scripts/`.
        



## Function: _validate_depth_requirements

**Parameters**: self, parts, root_folder, rel_path
**Returns**: tuple[bool, str]
**Description**: Validate depth requirements from sovereign registry.

        SSOT FIX: Allow variable depth for certain subfolders that legitimately
        have deeper structures (e.g., utils/core_extensions/, config/core/).

        [2026-02-08] FLAT DIRECTORY ENFORCEMENT: Directories in FLAT_DIRECTORIES
        must not contain any subdirectories. This check runs BEFORE depth checks
        to catch violations like mixins/contracts/ that bypass depth validation.
        



## Function: _validate_app_specific_files

**Parameters**: self, root_folder, file_path
**Returns**: tuple[bool, str]
**Description**: Validate app-specific files are not in core.



## Function: _validate_filename_patterns

**Parameters**: self, file_path
**Returns**: tuple[bool, str]
**Description**: Validate filename patterns for forbidden prefixes and backup files.



## Function: _validate_final_checks

**Parameters**: self, root_folder, file_path, parts
**Returns**: tuple[bool, str]
**Description**: Final validation checks for root-level files and gravity leaks.



## Function: _validate_ast_violations

**Parameters**: self, root_folder, file_path, rel_path
**Returns**: tuple[bool, str]
**Description**: Validate AST-based violations for agentic_core Python files.



## Function: _check_forbidden_imports

**Parameters**: self, tree, current_l1, rel_path
**Returns**: tuple[bool, str]
**Description**: Check for forbidden app imports and layer violations.



## Function: _scan_imports_for_violations

**Parameters**: self, tree, current_l1
**Returns**: tuple[bool, str | None]
**Description**: Scan AST for forbidden imports and return violation flags.



## Function: _extract_modules_from_node

**Parameters**: self, node
**Returns**: list[str]
**Description**: Extract module names from import node.



## Function: _is_forbidden_app_import

**Parameters**: self, module
**Returns**: bool
**Description**: Check if module is a forbidden app import.



## Function: _check_layer_import_violation

**Parameters**: self, module, current_l1
**Returns**: str | None
**Description**: Check for layer import violations and return violation description.

        [RECONCILED 2026-01-27] Now enforces:
        1. Core layer gravity (L1-L5 import direction)
        2. App-layer horizontal isolation (apps_shared independence)
        



## Function: _check_semantic_alignment

**Parameters**: self, tree, current_territory, rel_path
**Returns**: tuple[bool, str]
**Description**: Check semantic alignment between file location and content.

        [DEDUP 2026-02-07] Delegates file classification to FCA for consistent
        territory alignment instead of reimplementing AST scoring locally.
        



## Function: _calculate_semantic_scores

**Parameters**: self, tree
**Returns**: tuple[float, float, dict[str, float]]
**Description**: Calculate semantic scores for app and territory alignment.



## Function: _check_app_domain_violation

**Parameters**: self, app_rg_score, app_lic_score, rel_path
**Returns**: tuple[bool, str]
**Description**: 
        [HARDENED] Detects cross-contamination AND Global Candidates for apps_shared.
        [SSOT 2026-01-27] Implements the 'Shared Vacuum' logic.
        



## Function: _check_territory_alignment

**Parameters**: self, current_territory, territory_scores, rel_path
**Returns**: tuple[bool, str]
**Description**: Check territory alignment between file location and content.



## Function: _collect_ast_increments

**Parameters**: self, tree, territory_keywords
**Returns**: list[tuple[str, float]]
**Description**: Collect AST-based scoring increments.



## Function: _aggregate_ast_increments

**Parameters**: self, increments
**Returns**: dict[str, float]
**Description**: Aggregate scoring increments into territory scores.



## Function: _recompute_ast_scores

**Parameters**: self, tree, territory_keywords
**Returns**: tuple[float, float, dict[str, float]]
**Description**: Recompute AST scores (wrapper for _calculate_semantic_scores).



## Function: _score_identifier

**Parameters**: self, name, territory_keywords
**Returns**: float
**Description**: Score an identifier name against territory keywords.



## Function: _score_string

**Parameters**: self, value, territory_keywords
**Returns**: float
**Description**: Score a string value against territory keywords.



## Function: _score_variable

**Parameters**: self, name, territory_keywords
**Returns**: float
**Description**: Score a variable name against territory keywords.



## Function: _score_assignments

**Parameters**: self, node, territory_keywords
**Returns**: float
**Description**: Score assignment nodes.



## Function: _score_arguments

**Parameters**: self, node, territory_keywords
**Returns**: float
**Description**: Score function arguments.



## Function: enforce_void_compliance

**Parameters**: self, files
**Returns**: tuple[list[Path], list[tuple[Path, str]]]
**Description**: Filter files and collect all location-based violations.

        Salvaged from LocationAgent.py during LCD+ decommission.
        



## Function: _check_naming_conventions

**Parameters**: self, file_path
**Returns**: list[str]
**Description**: Check naming conventions for file.



## Function: run

**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: 
        Execute validation-only scan across sovereign territories.

        Args:
            target_territory: If provided, restricts scan to this domain (Strict Targeting).

        Phase 4.1 Upgrade: Universal root scanning using PROJECT_ROOT_WHITELIST.
        



## Usage Examples

### Class Usage

```python
# Using LocationValidatorAgent
locationvalidatoragent = LocationValidatorAgent()
locationvalidatoragent.heal()
locationvalidatoragent.heal_repository()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using heal
result = heal(violation)
```

```python
# Using heal_repository
result = heal_repository()
```



---
**Generated**: 2026-03-26T09:39:05.331489
**Type**: api_reference
**Quality**: comprehensive
