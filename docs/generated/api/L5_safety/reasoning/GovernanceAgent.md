# API Documentation: GovernanceAgent

**Target Audience**: developers, api_users

# GovernanceAgent API Documentation

**File**: `GovernanceAgent.py`
**Classes**: 4
**Functions**: 38

## Classes

- **DependencyGraph**
- **GovernanceAgent** (inherits from SovereignBaseAgent)
- **Violation**
- **MCPHardenedMixin**

## Functions

- **heal** -> dict[str, Any]
- **create_architecture_governor** -> GovernanceAgent
- **get_GovernanceAgent** -> GovernanceAgent
- **__init__** -> None
- **build** -> Any
- **_build_reverse_index**
- **_calculate_dependencies**
- **get_impact_radius** -> list[str]
- **get_dependency_tree** -> dict[str, list[str]]
- **visualize_graph** -> str
- **__init__** -> None
- **hierarchy_agent** -> Any
- **import_agent** -> Any
- **build_graph** -> Any
- **check_root_hygiene** -> list[str]
- **_check_root_file** -> None
- **_check_root_directory** -> None
- **_check_root_file** -> None
- **_check_root_directory** -> None
- **_sanitize_root_file** -> str
- **check_depth_law** -> str | None
- **check_atomicity_law** -> str | None
- **enforce_depth_law** -> str | None
- **_calculate_mccabe** -> int
- **_check_nesting_depth** -> list[dict[str, Any]]
- **check_complexity** -> list[dict[str, Any]]
- **get_blast_radius** -> dict[str, Any]
- **_create_empty_report** -> dict[str, Any]
- **_validate_single_file** -> None
- **_has_violations** -> bool
- **validate_architecture** -> dict[str, Any]
- **_init_backup_dir** -> Path
- **post_hierarchy_validation** -> dict[str, Any]
- **post_import_validation** -> dict[str, Any]
- **cleanup_violations** -> list[dict[str, Any]]
- **run_with_cleanup** -> dict[str, Any]
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]


## Class: DependencyGraph

**Description**: 
    Builds a directed graph of imports and class hierarchies.

    Used for calculating blast radius when files are modified,
    ensuring comprehensive impact analysis for governance.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the dependency graph.

#### build
**Parameters**: self, files, root_dir
**Returns**: Any
**Description**: 
        Build the dependency graph from a list of Python files.

        Args:
            files: List of Python file paths
            root_dir: Root directory for relative path calculation
        

#### _build_reverse_index
**Parameters**: self
**Description**: Build reverse lookup indices.

#### _calculate_dependencies
**Parameters**: self
**Description**: Calculate transitive dependencies for each file.

#### get_impact_radius
**Parameters**: self, file_path, include_transitive
**Returns**: list[str]
**Description**: 
        Get files impacted by modifications to the given file.

        Args:
            file_path: Path to the modified file
            include_transitive: Whether to include transitive dependencies

        Returns:
            List of file paths that may be impacted
        

#### get_dependency_tree
**Parameters**: self, file_path
**Returns**: dict[str, list[str]]
**Description**: 
        Get the full dependency tree for a file.

        Returns:
            Dictionary with 'direct' and 'transitive' dependencies
        

#### visualize_graph
**Parameters**: self, output_file
**Returns**: str
**Description**: 
        Generate a DOT format visualization of the graph.

        Args:
            output_file: Optional file to save the DOT graph

        Returns:
            DOT format string
        



## Class: GovernanceAgent

**Description**: 
    Enforces architectural governance laws and constraints.

    Implements the Three Laws:
    1. Law of The Void (Root hygiene)
    2. Law of Depth (Depth 3-5)
    3. Law of Impact (Blast radius awareness)

    GOLD STANDARD FEATURES (2026-01-02):
    - Structured Violation dataclass with severity levels
    - HierarchyAgent integration for structure validation
    - ImportAgent integration for gravity compliance
    - Post-heal validation with blast radius analysis
    - Batch post-heal reporting with FULL_SUCCESS/PARTIAL/NEEDS_REVIEW
    - cleanup_violations with multi-stage healing coordination
    - run_with_cleanup returning comprehensive summaries
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, root_dir
**Returns**: None
**Description**: 
        Initialize the ArchitectureGovernor.
        

#### hierarchy_agent
**Parameters**: self
**Returns**: Any
**Description**: Lazy-load HierarchyAgent to avoid circular import.

#### import_agent
**Parameters**: self
**Returns**: Any
**Description**: Lazy-load import healer to avoid circular import.

#### build_graph
**Parameters**: self, file_patterns
**Returns**: Any
**Description**: 
        Build the dependency graph for the project.

        Args:
            file_patterns: Glob patterns for Python files
        

#### check_root_hygiene
**Parameters**: self, auto_sanitize
**Returns**: list[str]
**Description**: 
        Check Law of The Void - root directory hygiene.

        Args:
            auto_sanitize: Whether to automatically move/delete violations

        Returns:
            List of violations
        

#### _check_root_file
**Parameters**: self, file_path, violations, sanitized, auto_sanitize
**Returns**: None

#### _check_root_directory
**Parameters**: self, dir_path, violations
**Returns**: None

#### _check_root_file
**Parameters**: self, item, violations, sanitized, auto_sanitize
**Returns**: None
**Description**: Check if root file is authorized and sanitize if needed.

#### _check_root_directory
**Parameters**: self, item, violations
**Returns**: None
**Description**: Check if root directory is authorized.

#### _sanitize_root_file
**Parameters**: self, file_path
**Returns**: str
**Description**: 
        Sanitize an unauthorized file in the root directory.

        Args:
            file_path: Path to the unauthorized file

        Returns:
            Action taken
        

#### check_depth_law
**Parameters**: self, file_path
**Returns**: str | None
**Description**: 
        Check Law of Depth - ensure proper nesting depth.
        [SSOT] Uses DEPTH_MAP derived from SOVEREIGN_REGISTRY for per-root depth enforcement.

        Args:
            file_path: Path to check
        Returns:
            Violation message or None
        

#### check_atomicity_law
**Parameters**: self, file_path
**Returns**: str | None
**Description**: 
        Check Law of Atomicity - ensure files don't exceed line limit.

        Args:
            file_path: Path to check

        Returns:
            Violation message or None
        

#### enforce_depth_law
**Parameters**: self, file_path
**Returns**: str | None
**Description**: 
        [DEPRECATED - P4 CONSOLIDATION] Use HealerAgent.heal_file_moves() instead.

        This method now only returns the SUGGESTED target path without moving.
        Actual file moves should be performed by HealerAgent.

        Args:
            file_path: Path to check

        Returns:
            Suggested target path if Violation detected, None if compliant
        

#### _calculate_mccabe
**Parameters**: self, node
**Returns**: int
**Description**: 
        Calculate cyclomatic complexity for an AST node.

        CONSOLIDATED: Delegates to shared L4 utility.
        See agentic_core.L4_state.utils.complexity_analyzer

        Args:
            node: AST node to analyze

        Returns:
            Cyclomatic complexity score
        

#### _check_nesting_depth
**Parameters**: self, file_path
**Returns**: list[dict[str, Any]]
**Description**: 
        Check for excessive nesting depth in a file.

        Args:
            file_path: Path to the file to check

        Returns:
            List of nesting violations
        

#### check_complexity
**Parameters**: self, file_path
**Returns**: list[dict[str, Any]]
**Description**: 
        Check complexity violations in a file.

        Args:
            file_path: Path to the file to check

        Returns:
            List of complexity violations
        

#### get_blast_radius
**Parameters**: self, modified_files
**Returns**: dict[str, Any]
**Description**: 
        Calculate the blast radius for modified files.

        Args:
            modified_files: List of modified file paths

        Returns:
            Dictionary with impact analysis
        

#### _create_empty_report
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Create empty validation report structure.

#### _validate_single_file
**Parameters**: self, file_path, report, enforce
**Returns**: None
**Description**: Validate a single file and update report.

#### _has_violations
**Parameters**: self, report
**Returns**: bool
**Description**: Check if report contains any violations.

#### validate_architecture
**Parameters**: self, file_paths, enforce
**Returns**: dict[str, Any]
**Description**: Perform full architecture validation.

#### _init_backup_dir
**Parameters**: self
**Returns**: Path
**Description**: Initialize and return the backup directory for safe operations.

#### post_hierarchy_validation
**Parameters**: self, file_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Run HierarchyAgent validation after governance fixes.

#### post_import_validation
**Parameters**: self, file_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Run ImportAgent validation after governance fixes.

#### cleanup_violations
**Parameters**: self, file_paths, dry_run
**Returns**: list[dict[str, Any]]
**Description**: 
        GOLD STANDARD CLEANUP ENGINE — Multi-stage autonomous governance.

        Healing stages:
        1. Check and fix root hygiene
        2. Check depth violations (suggest moves via HealerAgent)
        3. Check atomicity violations (suggest splits)
        4. Calculate blast radius for all changes
        5. HierarchyAgent integration for structure validation
        6. ImportAgent integration for gravity compliance
        

#### run_with_cleanup
**Parameters**: self, file_paths, dry_run
**Returns**: dict[str, Any]
**Description**: 
        GOLD STANDARD WORKFLOW — Full governance compliance with autonomous cleanup.
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Enforce architectural governance laws across the repository.

        Checks root hygiene (Law of The Void), depth requirements, and
        atomicity constraints. Governance violations are delegated to
        StructuralHealerAgent for actual fixes.

        Args:
            dry_run: If True, only report violations (default: True).
            execute: If True, delegate fixes to StructuralHealerAgent.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by GovernanceAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Class: Violation

**Description**: Structured violation output for deterministic healing.



## Class: MCPHardenedMixin



## Function: heal

**Parameters**: violation
**Returns**: dict[str, Any]
**Description**: 
    [HEALER PROTOCOL] Standardized healing interface for governance violations.

    Args:
        violation: Violation dict with keys: type, file, message, etc.

    Returns:
        Dict with keys: status, details, artifacts, errors
    



## Function: create_architecture_governor

**Parameters**: root_dir
**Returns**: GovernanceAgent
**Description**: Create an architecture governor instance.



## Function: get_GovernanceAgent

**Parameters**: project_root, enforcement_mode
**Returns**: GovernanceAgent
**Description**: Factory function to get governance agent instance.



## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the dependency graph.



## Function: build

**Parameters**: self, files, root_dir
**Returns**: Any
**Description**: 
        Build the dependency graph from a list of Python files.

        Args:
            files: List of Python file paths
            root_dir: Root directory for relative path calculation
        



## Function: _build_reverse_index

**Parameters**: self
**Description**: Build reverse lookup indices.



## Function: _calculate_dependencies

**Parameters**: self
**Description**: Calculate transitive dependencies for each file.



## Function: get_impact_radius

**Parameters**: self, file_path, include_transitive
**Returns**: list[str]
**Description**: 
        Get files impacted by modifications to the given file.

        Args:
            file_path: Path to the modified file
            include_transitive: Whether to include transitive dependencies

        Returns:
            List of file paths that may be impacted
        



## Function: get_dependency_tree

**Parameters**: self, file_path
**Returns**: dict[str, list[str]]
**Description**: 
        Get the full dependency tree for a file.

        Returns:
            Dictionary with 'direct' and 'transitive' dependencies
        



## Function: visualize_graph

**Parameters**: self, output_file
**Returns**: str
**Description**: 
        Generate a DOT format visualization of the graph.

        Args:
            output_file: Optional file to save the DOT graph

        Returns:
            DOT format string
        



## Function: __init__

**Parameters**: self, root_dir
**Returns**: None
**Description**: 
        Initialize the ArchitectureGovernor.
        



## Function: hierarchy_agent

**Parameters**: self
**Returns**: Any
**Description**: Lazy-load HierarchyAgent to avoid circular import.



## Function: import_agent

**Parameters**: self
**Returns**: Any
**Description**: Lazy-load import healer to avoid circular import.



## Function: build_graph

**Parameters**: self, file_patterns
**Returns**: Any
**Description**: 
        Build the dependency graph for the project.

        Args:
            file_patterns: Glob patterns for Python files
        



## Function: check_root_hygiene

**Parameters**: self, auto_sanitize
**Returns**: list[str]
**Description**: 
        Check Law of The Void - root directory hygiene.

        Args:
            auto_sanitize: Whether to automatically move/delete violations

        Returns:
            List of violations
        



## Function: _check_root_file

**Parameters**: self, file_path, violations, sanitized, auto_sanitize
**Returns**: None


## Function: _check_root_directory

**Parameters**: self, dir_path, violations
**Returns**: None


## Function: _check_root_file

**Parameters**: self, item, violations, sanitized, auto_sanitize
**Returns**: None
**Description**: Check if root file is authorized and sanitize if needed.



## Function: _check_root_directory

**Parameters**: self, item, violations
**Returns**: None
**Description**: Check if root directory is authorized.



## Function: _sanitize_root_file

**Parameters**: self, file_path
**Returns**: str
**Description**: 
        Sanitize an unauthorized file in the root directory.

        Args:
            file_path: Path to the unauthorized file

        Returns:
            Action taken
        



## Function: check_depth_law

**Parameters**: self, file_path
**Returns**: str | None
**Description**: 
        Check Law of Depth - ensure proper nesting depth.
        [SSOT] Uses DEPTH_MAP derived from SOVEREIGN_REGISTRY for per-root depth enforcement.

        Args:
            file_path: Path to check
        Returns:
            Violation message or None
        



## Function: check_atomicity_law

**Parameters**: self, file_path
**Returns**: str | None
**Description**: 
        Check Law of Atomicity - ensure files don't exceed line limit.

        Args:
            file_path: Path to check

        Returns:
            Violation message or None
        



## Function: enforce_depth_law

**Parameters**: self, file_path
**Returns**: str | None
**Description**: 
        [DEPRECATED - P4 CONSOLIDATION] Use HealerAgent.heal_file_moves() instead.

        This method now only returns the SUGGESTED target path without moving.
        Actual file moves should be performed by HealerAgent.

        Args:
            file_path: Path to check

        Returns:
            Suggested target path if Violation detected, None if compliant
        



## Function: _calculate_mccabe

**Parameters**: self, node
**Returns**: int
**Description**: 
        Calculate cyclomatic complexity for an AST node.

        CONSOLIDATED: Delegates to shared L4 utility.
        See agentic_core.L4_state.utils.complexity_analyzer

        Args:
            node: AST node to analyze

        Returns:
            Cyclomatic complexity score
        



## Function: _check_nesting_depth

**Parameters**: self, file_path
**Returns**: list[dict[str, Any]]
**Description**: 
        Check for excessive nesting depth in a file.

        Args:
            file_path: Path to the file to check

        Returns:
            List of nesting violations
        



## Function: check_complexity

**Parameters**: self, file_path
**Returns**: list[dict[str, Any]]
**Description**: 
        Check complexity violations in a file.

        Args:
            file_path: Path to the file to check

        Returns:
            List of complexity violations
        



## Function: get_blast_radius

**Parameters**: self, modified_files
**Returns**: dict[str, Any]
**Description**: 
        Calculate the blast radius for modified files.

        Args:
            modified_files: List of modified file paths

        Returns:
            Dictionary with impact analysis
        



## Function: _create_empty_report

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Create empty validation report structure.



## Function: _validate_single_file

**Parameters**: self, file_path, report, enforce
**Returns**: None
**Description**: Validate a single file and update report.



## Function: _has_violations

**Parameters**: self, report
**Returns**: bool
**Description**: Check if report contains any violations.



## Function: validate_architecture

**Parameters**: self, file_paths, enforce
**Returns**: dict[str, Any]
**Description**: Perform full architecture validation.



## Function: _init_backup_dir

**Parameters**: self
**Returns**: Path
**Description**: Initialize and return the backup directory for safe operations.



## Function: post_hierarchy_validation

**Parameters**: self, file_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Run HierarchyAgent validation after governance fixes.



## Function: post_import_validation

**Parameters**: self, file_paths, dry_run
**Returns**: dict[str, Any]
**Description**: Run ImportAgent validation after governance fixes.



## Function: cleanup_violations

**Parameters**: self, file_paths, dry_run
**Returns**: list[dict[str, Any]]
**Description**: 
        GOLD STANDARD CLEANUP ENGINE — Multi-stage autonomous governance.

        Healing stages:
        1. Check and fix root hygiene
        2. Check depth violations (suggest moves via HealerAgent)
        3. Check atomicity violations (suggest splits)
        4. Calculate blast radius for all changes
        5. HierarchyAgent integration for structure validation
        6. ImportAgent integration for gravity compliance
        



## Function: run_with_cleanup

**Parameters**: self, file_paths, dry_run
**Returns**: dict[str, Any]
**Description**: 
        GOLD STANDARD WORKFLOW — Full governance compliance with autonomous cleanup.
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Enforce architectural governance laws across the repository.

        Checks root hygiene (Law of The Void), depth requirements, and
        atomicity constraints. Governance violations are delegated to
        StructuralHealerAgent for actual fixes.

        Args:
            dry_run: If True, only report violations (default: True).
            execute: If True, delegate fixes to StructuralHealerAgent.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by GovernanceAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Usage Examples

### Class Usage

```python
# Using DependencyGraph
dependencygraph = DependencyGraph()
dependencygraph.build()
dependencygraph.get_impact_radius()
```

```python
# Using GovernanceAgent
governanceagent = GovernanceAgent()
governanceagent.hierarchy_agent()
governanceagent.import_agent()
```

```python
# Using Violation
violation = Violation()
```

### Function Usage

```python
# Using heal
result = heal(violation)
```

```python
# Using create_architecture_governor
result = create_architecture_governor(root_dir)
```

```python
# Using get_GovernanceAgent
result = get_GovernanceAgent(project_root, enforcement_mode)
```



---
**Generated**: 2026-03-26T09:39:05.232840
**Type**: api_reference
**Quality**: comprehensive
