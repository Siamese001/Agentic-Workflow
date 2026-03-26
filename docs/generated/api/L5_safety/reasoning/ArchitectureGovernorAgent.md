# API Documentation: ArchitectureGovernorAgent

**Target Audience**: developers, api_users

# ArchitectureGovernorAgent API Documentation

**File**: `ArchitectureGovernorAgent.py`
**Classes**: 1
**Functions**: 34

## Classes

- **ArchitectureGovernorAgent** (inherits from SovereignBaseAgent)

## Functions

- **__post_init__** -> None
- **_get_structure_validator**
- **_get_gravity_repair_agent**
- **_get_archival_gatekeeper**
- **_get_cognitive_agent**
- **heal** -> dict[str, Any]
- **_do_heal** -> dict[str, Any]
- **heal_repository** -> dict[str, Any]
- **run_ci_verification_sync** -> tuple[bool, dict[str, Any]]
- **run_audit** -> dict[str, Any]
- **_orchestrate_guardian_scan** -> dict[str, Any]
- **validate_layer_boundaries** -> tuple[bool, str]
- **_cognitive_triage_validation** -> tuple[bool, str]
- **validate_architectural_patterns** -> dict[str, Any]
- **run_validation** -> dict[str, Any]
- **_heal_violation** -> bool
- **_heal_gravity_violation** -> bool
- **_heal_naming_violation** -> bool
- **_trigger_deduplication_audit** -> dict[str, Any]
- **_resolve_collision** -> int
- **_cleanup_empty_dirs** -> None
- **finalize_sovereign_lockdown** -> tuple[bool, dict]
- **capture_golden_baseline** -> Path
- **_check_baseline_drift** -> list[dict[str, Any]]
- **_persist_audit_report** -> None
- **capture_sovereign_baseline** -> dict[str, Any]
- **_log_categorical_drift** -> dict[str, int]
- **execute_sovereign_convergence** -> dict[str, Any]
- **execute_cognitive_purge** -> dict[str, Any]
- **comprehensive_territory_audit** -> dict[str, Any]
- **check_file_sizes** -> list[dict[str, Any]]
- **generate_healing_plan** -> dict[str, Any]
- **_process_cognitive_disposition** -> bool
- **get_priority** -> int


## Class: ArchitectureGovernorAgent

**Description**: 
    [L5 GOVERNOR] Universal Architecture Pattern Enforcement

    Phase 1 Upgrade: Activated from stub to functioning enforcer.
    Ensures code follows canonical architectural patterns and layer boundaries
    across ALL sovereign territories (not just agentic_core).

    Features:
    - Universal Scope: Scans all SOVEREIGN_TERRITORIES roots
    - Auto-Approve Mode: Headless CI operation without stdin prompts
    - Gravity Detection: L3 importing L5 = violation
    - Naming Enforcement: *Agent.py suffix validation
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the ArchitectureGovernorAgent.

#### _get_structure_validator
**Parameters**: self
**Description**: Lazy-load StructuralValidatorAgent to avoid circular imports.

#### _get_gravity_repair_agent
**Parameters**: self
**Description**: Lazy-load GravityLeakRepairAgent for orchestrated healing.

#### _get_archival_gatekeeper
**Parameters**: self
**Description**: Lazy-load ArchivalGatekeeper for safe file operations.

#### _get_cognitive_agent
**Parameters**: self
**Description**: Lazy-load CognitiveDispositionAgent for AI-powered triage (Phase 11).

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Enhanced healing interface with meta-learning integration.

        Args:
            violation: Violation dict with keys: type, file, message, severity, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        

#### _do_heal
**Parameters**: self, violation
**Returns**: dict[str, Any]

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path, auto_approve, target_territory
**Returns**: dict[str, Any]
**Description**: 
        Universal architecture governance with optional strict scope targeting.

        Phase 1 Upgrade: Now performs actual validation instead of returning stub.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, attempt to fix violations
            depth: Current recursion depth for cycle detection
            max_depth: Maximum recursion depth
            _call_path: Internal call path tracking
            auto_approve: Override instance auto_approve setting
            target_territory: [STRICT SCOPE] If provided, restricts audit to specific territory

        Returns:
            Dictionary with canonical keys: violations_found, violations_fixed, status
        

#### run_ci_verification_sync
**Parameters**: self
**Returns**: tuple[bool, dict[str, Any]]
**Description**: 
        Synchronous CI verification for pre-commit hooks and CLI tools.

        Returns (is_compliant, results_dict) for easy CI integration.
        No stdin prompts - fully headless operation.
        

#### run_audit
**Parameters**: self, target_territories
**Returns**: dict[str, Any]
**Description**: 
        Executes a comprehensive structural and naming audit with Phase 8 Drift Detection.
        In CI mode, this returns a non-zero-weighted success status.

        Args:
            target_territories: [STRICT SCOPE] Optional list of specific paths/domains to audit.
        

#### _orchestrate_guardian_scan
**Parameters**: self, target_territories
**Returns**: dict[str, Any]
**Description**: 
        Orchestrate scanning of all L5 Guardians in one pass.
        Internal method for run_audit to consolidate scanning logic.

        Now supports [STRICT SCOPE] targeting via target_territories.
        

#### validate_layer_boundaries
**Parameters**: self, file_path
**Returns**: tuple[bool, str]
**Description**: 
        Validate that file respects layer boundaries using deterministic Guardian test.

        Args:
            file_path: Path to file to validate

        Returns:
            Tuple of (is_valid, reason)
        

#### _cognitive_triage_validation
**Parameters**: self, file_path, violation_type
**Returns**: tuple[bool, str]
**Description**: 
        [PHASE 22] Invoke CognitiveDispositionAgent for intelligent violation analysis.

        Args:
            file_path: Path to the file with potential violation
            violation_type: Type of violation (ORPHAN, GRAVITY, etc.)

        Returns:
            Tuple of (is_valid, reason) with cognitive triage recommendation
        

#### validate_architectural_patterns
**Parameters**: self, file_path
**Returns**: dict[str, Any]
**Description**: 
        Validate architectural patterns in a file.

        Args:
            file_path: Path to file to validate

        Returns:
            Dictionary with validation results
        

#### run_validation
**Parameters**: self, files
**Returns**: dict[str, Any]
**Description**: 
        Run architecture validation on multiple files.

        Args:
            files: List of file paths to validate

        Returns:
            Summary of validation results
        

#### _heal_violation
**Parameters**: self, violation, auto_approve
**Returns**: bool
**Description**: 
        Attempt to heal a single violation.

        Phase 2: Dispatches to appropriate healer based on violation type.

        Args:
            violation: Violation dict with type, file, message, etc.
            auto_approve: If True, skip interactive prompts

        Returns:
            True if violation was fixed, False otherwise
        

#### _heal_gravity_violation
**Parameters**: self, violation, auto_approve
**Returns**: bool
**Description**: 
        Heal a gravity violation by orchestrating GravityLeakRepairAgent.

        Phase 2: Governor acts as executive that decides WHEN to trigger repair.

        Args:
            violation: Gravity violation dict
            auto_approve: If True, skip interactive prompts

        Returns:
            True if fixed, False otherwise
        

#### _heal_naming_violation
**Parameters**: self, violation, auto_approve
**Returns**: bool
**Description**: 
        Heal a naming convention violation via ArchivalGatekeeper safe rename.

        Phase 2: Fixes files missing *Agent.py suffix.

        Args:
            violation: Naming violation dict
            auto_approve: If True, skip interactive prompts

        Returns:
            True if fixed, False otherwise
        

#### _trigger_deduplication_audit
**Parameters**: self, roots, execute
**Returns**: dict[str, Any]
**Description**: 
        [PHASE 4/6] Identify and resolve redundant logic across roots.

        Scans all sovereign roots for duplicate agent definitions and
        redundant code patterns. When execute=True and auto_approve=True,
        resolves collisions via zero-loss merge using ArchivalGatekeeper.

        Args:
            roots: List of root names that were scanned
            execute: If True, attempt to resolve collisions

        Returns:
            Dictionary with audit results including collisions found/fixed
        

#### _resolve_collision
**Parameters**: self, violation
**Returns**: int
**Description**: 
        [PHASE 6] Zero-loss merge: Archives lower-priority duplicates.

        Priority order (highest to lowest):
        - agentic_core (0) - Master source
        - apps_shared (1) - Shared utilities
        - apps_rg (2) - Resume Generator app
        - apps_lic (3) - LinkedIn app
        - tests (4) - Test files
        - scripts (5) - Scripts

        Args:
            violation: StructureViolation with duplicate locations

        Returns:
            Number of files archived (0 if no action taken)
        

#### _cleanup_empty_dirs
**Parameters**: self, path
**Returns**: None
**Description**: 
        Recursively remove empty directories after healing operations.

        Phase 3: Post-healing environmental maintenance to purge ghost directories
        left behind after renames or refactors.

        Args:
            path: Root path to start cleanup from
        

#### finalize_sovereign_lockdown
**Parameters**: self
**Returns**: tuple[bool, dict]
**Description**: 
        [PHASE 7] Final CI-ready lockdown verification.

        Performs a non-blocking sync check to ensure the repository state
        perfectly matches the Sovereign SSOT. Designed for CI/CD pipelines
        and pre-commit hooks.

        Returns:
            Tuple of (is_pure: bool, results: dict)
            - is_pure: True if repository has 0 violations
            - results: Full heal_repository results for inspection

        Usage in CI:
            agent = ArchitectureGovernorAgent(project_root=Path.cwd(), auto_approve=True)
            is_pure, results = agent.finalize_sovereign_lockdown()
            sys.exit(0 if is_pure else 1)
        

#### capture_golden_baseline
**Parameters**: self
**Returns**: Path
**Description**: 
        [PHASE 8] Generates a SHA-256 manifest of all files in sovereign territories.
        This represents the 'Gold Master' state of the repository.
        

#### _check_baseline_drift
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: [PHASE 8] Compares live files against the Golden Baseline.

#### _persist_audit_report
**Parameters**: self, structural_results, drift_violations
**Returns**: None
**Description**: [PHASE 8] Saves immutable audit record.

#### capture_sovereign_baseline
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        [PHASE 9] Captures the post-purge state as the new SSOT baseline.

        This establishes the zero-violation benchmark for all future
        CI/CD enforcement gates. Should be called after a successful
        purge execution to lock in the clean state.

        Returns:
            Dictionary containing the baseline state with violation counts
            and root scan results.

        Usage:
            # After purge execution
            agent.heal_repository(execute=True, dry_run=False)

            # Capture the clean state as baseline
            baseline = agent.capture_sovereign_baseline()
            assert baseline.get("violations_found", 0) == 0
        

#### _log_categorical_drift
**Parameters**: self, violations
**Returns**: dict[str, int]
**Description**: 
        [PHASE 10] Generates a diagnostic breakdown of architectural debt.

        Categorizes violations by type for targeted remediation.

        Args:
            violations: List of violation objects or dictionaries

        Returns:
            Dictionary with counts per violation category
        

#### execute_sovereign_convergence
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        [PHASE 10] Final convergence: Purge all drift and seal the baseline.

        This is the terminal command for the L5 safety transition.
        Executes a full purge followed by baseline lockdown verification.

        Returns:
            Dictionary containing:
            - purge_status: Results from heal_repository execution
            - lockdown_status: Tuple of (is_pure, results) from lockdown
            - final_purity: Boolean indicating if repository is clean

        Usage:
            agent = ArchitectureGovernorAgent(project_root=Path.cwd(), auto_approve=True)
            result = agent.execute_sovereign_convergence()
            assert result["final_purity"] is True
        

#### execute_cognitive_purge
**Parameters**: self, checkpoint_file, rate_limit_delay
**Returns**: dict[str, Any]
**Description**: 
        [PHASE 13] Execute AI-driven purge using Cognitive Batch Processor.

        Processes all violations through Gemini LLM with:
        - Rate limiting to respect API quotas
        - Progress checkpointing for resumable execution
        - Exponential backoff for API errors

        Args:
            checkpoint_file: Path to checkpoint file for progress tracking
            rate_limit_delay: Seconds to wait between API calls

        Returns:
            Dictionary with batch processing statistics
        

#### comprehensive_territory_audit
**Parameters**: self, target_territories, check_layer_boundaries, check_naming_conventions
**Returns**: dict[str, Any]
**Description**: 
        [HARDENED] Unified Compliance Audit.
        Aggregates output from Hierarchy, Location, and SystemArchitect agents into a single JSON manifest.
        

#### check_file_sizes
**Parameters**: self, territory, max_lines
**Returns**: list[dict[str, Any]]
**Description**: Check for Python files exceeding max_lines in the given territory.

        Mirrors the file-size check previously performed by SystemArchitectAgent.
        Returns a list of violation dicts (type FILE_SIZE, file, message, severity).
        

#### generate_healing_plan
**Parameters**: self, gov_report
**Returns**: dict[str, Any]
**Description**: 
        Generates a healing plan based on the governance report.
        Now recognizes STRUCTURE violations (Root Files) and GRAVITY violations.
        

#### _process_cognitive_disposition
**Parameters**: self, file_path, violation_type
**Returns**: bool
**Description**: 
        [PHASE 11] Delegates violation decision to CognitiveDispositionAgent.

        Uses AI-powered heuristics to determine the appropriate action for
        violations that cannot be resolved deterministically.

        Args:
            file_path: Path to the file with the violation
            violation_type: Type of violation (ORPHAN, GRAVITY_FAIL, etc.)

        Returns:
            True if the violation was resolved, False otherwise
        



## Function: __post_init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the ArchitectureGovernorAgent.



## Function: _get_structure_validator

**Parameters**: self
**Description**: Lazy-load StructuralValidatorAgent to avoid circular imports.



## Function: _get_gravity_repair_agent

**Parameters**: self
**Description**: Lazy-load GravityLeakRepairAgent for orchestrated healing.



## Function: _get_archival_gatekeeper

**Parameters**: self
**Description**: Lazy-load ArchivalGatekeeper for safe file operations.



## Function: _get_cognitive_agent

**Parameters**: self
**Description**: Lazy-load CognitiveDispositionAgent for AI-powered triage (Phase 11).



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Enhanced healing interface with meta-learning integration.

        Args:
            violation: Violation dict with keys: type, file, message, severity, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        



## Function: _do_heal

**Parameters**: self, violation
**Returns**: dict[str, Any]


## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path, auto_approve, target_territory
**Returns**: dict[str, Any]
**Description**: 
        Universal architecture governance with optional strict scope targeting.

        Phase 1 Upgrade: Now performs actual validation instead of returning stub.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, attempt to fix violations
            depth: Current recursion depth for cycle detection
            max_depth: Maximum recursion depth
            _call_path: Internal call path tracking
            auto_approve: Override instance auto_approve setting
            target_territory: [STRICT SCOPE] If provided, restricts audit to specific territory

        Returns:
            Dictionary with canonical keys: violations_found, violations_fixed, status
        



## Function: run_ci_verification_sync

**Parameters**: self
**Returns**: tuple[bool, dict[str, Any]]
**Description**: 
        Synchronous CI verification for pre-commit hooks and CLI tools.

        Returns (is_compliant, results_dict) for easy CI integration.
        No stdin prompts - fully headless operation.
        



## Function: run_audit

**Parameters**: self, target_territories
**Returns**: dict[str, Any]
**Description**: 
        Executes a comprehensive structural and naming audit with Phase 8 Drift Detection.
        In CI mode, this returns a non-zero-weighted success status.

        Args:
            target_territories: [STRICT SCOPE] Optional list of specific paths/domains to audit.
        



## Function: _orchestrate_guardian_scan

**Parameters**: self, target_territories
**Returns**: dict[str, Any]
**Description**: 
        Orchestrate scanning of all L5 Guardians in one pass.
        Internal method for run_audit to consolidate scanning logic.

        Now supports [STRICT SCOPE] targeting via target_territories.
        



## Function: validate_layer_boundaries

**Parameters**: self, file_path
**Returns**: tuple[bool, str]
**Description**: 
        Validate that file respects layer boundaries using deterministic Guardian test.

        Args:
            file_path: Path to file to validate

        Returns:
            Tuple of (is_valid, reason)
        



## Function: _cognitive_triage_validation

**Parameters**: self, file_path, violation_type
**Returns**: tuple[bool, str]
**Description**: 
        [PHASE 22] Invoke CognitiveDispositionAgent for intelligent violation analysis.

        Args:
            file_path: Path to the file with potential violation
            violation_type: Type of violation (ORPHAN, GRAVITY, etc.)

        Returns:
            Tuple of (is_valid, reason) with cognitive triage recommendation
        



## Function: validate_architectural_patterns

**Parameters**: self, file_path
**Returns**: dict[str, Any]
**Description**: 
        Validate architectural patterns in a file.

        Args:
            file_path: Path to file to validate

        Returns:
            Dictionary with validation results
        



## Function: run_validation

**Parameters**: self, files
**Returns**: dict[str, Any]
**Description**: 
        Run architecture validation on multiple files.

        Args:
            files: List of file paths to validate

        Returns:
            Summary of validation results
        



## Function: _heal_violation

**Parameters**: self, violation, auto_approve
**Returns**: bool
**Description**: 
        Attempt to heal a single violation.

        Phase 2: Dispatches to appropriate healer based on violation type.

        Args:
            violation: Violation dict with type, file, message, etc.
            auto_approve: If True, skip interactive prompts

        Returns:
            True if violation was fixed, False otherwise
        



## Function: _heal_gravity_violation

**Parameters**: self, violation, auto_approve
**Returns**: bool
**Description**: 
        Heal a gravity violation by orchestrating GravityLeakRepairAgent.

        Phase 2: Governor acts as executive that decides WHEN to trigger repair.

        Args:
            violation: Gravity violation dict
            auto_approve: If True, skip interactive prompts

        Returns:
            True if fixed, False otherwise
        



## Function: _heal_naming_violation

**Parameters**: self, violation, auto_approve
**Returns**: bool
**Description**: 
        Heal a naming convention violation via ArchivalGatekeeper safe rename.

        Phase 2: Fixes files missing *Agent.py suffix.

        Args:
            violation: Naming violation dict
            auto_approve: If True, skip interactive prompts

        Returns:
            True if fixed, False otherwise
        



## Function: _trigger_deduplication_audit

**Parameters**: self, roots, execute
**Returns**: dict[str, Any]
**Description**: 
        [PHASE 4/6] Identify and resolve redundant logic across roots.

        Scans all sovereign roots for duplicate agent definitions and
        redundant code patterns. When execute=True and auto_approve=True,
        resolves collisions via zero-loss merge using ArchivalGatekeeper.

        Args:
            roots: List of root names that were scanned
            execute: If True, attempt to resolve collisions

        Returns:
            Dictionary with audit results including collisions found/fixed
        



## Function: _resolve_collision

**Parameters**: self, violation
**Returns**: int
**Description**: 
        [PHASE 6] Zero-loss merge: Archives lower-priority duplicates.

        Priority order (highest to lowest):
        - agentic_core (0) - Master source
        - apps_shared (1) - Shared utilities
        - apps_rg (2) - Resume Generator app
        - apps_lic (3) - LinkedIn app
        - tests (4) - Test files
        - scripts (5) - Scripts

        Args:
            violation: StructureViolation with duplicate locations

        Returns:
            Number of files archived (0 if no action taken)
        



## Function: _cleanup_empty_dirs

**Parameters**: self, path
**Returns**: None
**Description**: 
        Recursively remove empty directories after healing operations.

        Phase 3: Post-healing environmental maintenance to purge ghost directories
        left behind after renames or refactors.

        Args:
            path: Root path to start cleanup from
        



## Function: finalize_sovereign_lockdown

**Parameters**: self
**Returns**: tuple[bool, dict]
**Description**: 
        [PHASE 7] Final CI-ready lockdown verification.

        Performs a non-blocking sync check to ensure the repository state
        perfectly matches the Sovereign SSOT. Designed for CI/CD pipelines
        and pre-commit hooks.

        Returns:
            Tuple of (is_pure: bool, results: dict)
            - is_pure: True if repository has 0 violations
            - results: Full heal_repository results for inspection

        Usage in CI:
            agent = ArchitectureGovernorAgent(project_root=Path.cwd(), auto_approve=True)
            is_pure, results = agent.finalize_sovereign_lockdown()
            sys.exit(0 if is_pure else 1)
        



## Function: capture_golden_baseline

**Parameters**: self
**Returns**: Path
**Description**: 
        [PHASE 8] Generates a SHA-256 manifest of all files in sovereign territories.
        This represents the 'Gold Master' state of the repository.
        



## Function: _check_baseline_drift

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: [PHASE 8] Compares live files against the Golden Baseline.



## Function: _persist_audit_report

**Parameters**: self, structural_results, drift_violations
**Returns**: None
**Description**: [PHASE 8] Saves immutable audit record.



## Function: capture_sovereign_baseline

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        [PHASE 9] Captures the post-purge state as the new SSOT baseline.

        This establishes the zero-violation benchmark for all future
        CI/CD enforcement gates. Should be called after a successful
        purge execution to lock in the clean state.

        Returns:
            Dictionary containing the baseline state with violation counts
            and root scan results.

        Usage:
            # After purge execution
            agent.heal_repository(execute=True, dry_run=False)

            # Capture the clean state as baseline
            baseline = agent.capture_sovereign_baseline()
            assert baseline.get("violations_found", 0) == 0
        



## Function: _log_categorical_drift

**Parameters**: self, violations
**Returns**: dict[str, int]
**Description**: 
        [PHASE 10] Generates a diagnostic breakdown of architectural debt.

        Categorizes violations by type for targeted remediation.

        Args:
            violations: List of violation objects or dictionaries

        Returns:
            Dictionary with counts per violation category
        



## Function: execute_sovereign_convergence

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        [PHASE 10] Final convergence: Purge all drift and seal the baseline.

        This is the terminal command for the L5 safety transition.
        Executes a full purge followed by baseline lockdown verification.

        Returns:
            Dictionary containing:
            - purge_status: Results from heal_repository execution
            - lockdown_status: Tuple of (is_pure, results) from lockdown
            - final_purity: Boolean indicating if repository is clean

        Usage:
            agent = ArchitectureGovernorAgent(project_root=Path.cwd(), auto_approve=True)
            result = agent.execute_sovereign_convergence()
            assert result["final_purity"] is True
        



## Function: execute_cognitive_purge

**Parameters**: self, checkpoint_file, rate_limit_delay
**Returns**: dict[str, Any]
**Description**: 
        [PHASE 13] Execute AI-driven purge using Cognitive Batch Processor.

        Processes all violations through Gemini LLM with:
        - Rate limiting to respect API quotas
        - Progress checkpointing for resumable execution
        - Exponential backoff for API errors

        Args:
            checkpoint_file: Path to checkpoint file for progress tracking
            rate_limit_delay: Seconds to wait between API calls

        Returns:
            Dictionary with batch processing statistics
        



## Function: comprehensive_territory_audit

**Parameters**: self, target_territories, check_layer_boundaries, check_naming_conventions
**Returns**: dict[str, Any]
**Description**: 
        [HARDENED] Unified Compliance Audit.
        Aggregates output from Hierarchy, Location, and SystemArchitect agents into a single JSON manifest.
        



## Function: check_file_sizes

**Parameters**: self, territory, max_lines
**Returns**: list[dict[str, Any]]
**Description**: Check for Python files exceeding max_lines in the given territory.

        Mirrors the file-size check previously performed by SystemArchitectAgent.
        Returns a list of violation dicts (type FILE_SIZE, file, message, severity).
        



## Function: generate_healing_plan

**Parameters**: self, gov_report
**Returns**: dict[str, Any]
**Description**: 
        Generates a healing plan based on the governance report.
        Now recognizes STRUCTURE violations (Root Files) and GRAVITY violations.
        



## Function: _process_cognitive_disposition

**Parameters**: self, file_path, violation_type
**Returns**: bool
**Description**: 
        [PHASE 11] Delegates violation decision to CognitiveDispositionAgent.

        Uses AI-powered heuristics to determine the appropriate action for
        violations that cannot be resolved deterministically.

        Args:
            file_path: Path to the file with the violation
            violation_type: Type of violation (ORPHAN, GRAVITY_FAIL, etc.)

        Returns:
            True if the violation was resolved, False otherwise
        



## Function: get_priority

**Parameters**: p
**Returns**: int


## Usage Examples

### Class Usage

```python
# Using ArchitectureGovernorAgent
architecturegovernoragent = ArchitectureGovernorAgent()
architecturegovernoragent.heal()
architecturegovernoragent.heal_repository()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _get_structure_validator
result = _get_structure_validator()
```

```python
# Using _get_gravity_repair_agent
result = _get_gravity_repair_agent()
```



---
**Generated**: 2026-03-26T09:39:05.041174
**Type**: api_reference
**Quality**: comprehensive
