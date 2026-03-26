# API Documentation: FileClassificationAgent

**Target Audience**: developers, api_users

# FileClassificationAgent API Documentation

**File**: `FileClassificationAgent.py`
**Classes**: 2
**Functions**: 75

## Classes

- **ClassificationResult**
- **FileClassificationHealerAgent** (inherits from <ast.Starred object at 0x000001CBFCBB8890>)

## Functions

- **get_python_files_fast** -> list[Path]
- **main**
- **__post_init__**
- **enforce_kernel_structure** -> Path | None
- **_get_correct_folder_for_type** -> str | None
- **run** -> dict[str, Any]
- **_orchestrate_audit** -> int
- **classify_file** -> FileType
- **_load_adg_behavioral_profile** -> 'tuple[float, list[str]]'
- **classify_file_with_signals** -> ClassificationResult
- **_detect_enforcer_control_signal** -> bool
- **_detect_orchestrator_patterns** -> bool
- **_validate_orchestrator_invariants** -> str
- **_validate_orchestrator_layer_alignment** -> None
- **_validate_router_invariants** -> None
- **_detect_filename_tag_conflicts** -> set[str]
- **_to_pascal_case** -> str
- **_to_smart_snake_case** -> str
- **_sanitize_filename** -> str
- **normalize_filename** -> str
- **_check_forbidden_patterns** -> list[dict[str, str]]
- **validate_pascal_case_placement** -> dict[str, Any] | None
- **validate_app_prefix_placement** -> dict[str, Any] | None
- **validate_territory_alignment** -> dict[str, Any] | None
- **validate_layer_alignment** -> dict[str, Any] | None
- **suggest_manager_layer** -> str | None
- **suggest_agent_layer** -> dict[str, Any] | None
- **validate_single_suffix** -> dict[str, Any] | None
- **validate_folder_suffix_consistency** -> dict[str, Any] | None
- **_enforce_folder_purity** -> dict[str, Any] | None
- **_detect_cross_domain_violation** -> dict[str, Any] | None
- **_detect_ephemeral_scripts** -> dict[str, Any] | None
- **_detect_cross_layer_naming_violation** -> dict[str, Any] | None
- **_detect_duplicate_files** -> list[dict[str, Any]]
- **_detect_semantic_duplicates** -> list[dict[str, Any]]
- **_compute_layer_affinity** -> dict[str, float]
- **_compute_content_scores** -> dict[str, int]
- **classify_file_with_confidence** -> ClassificationResult
- **_detect_test_patterns** -> dict[str, bool]
- **_detect_script_patterns** -> dict[str, bool]
- **_detect_type_patterns** -> dict[str, bool]
- **_fuzzy_match_name_or_content** -> bool
- **_detect_config_patterns** -> bool
- **_detect_validator_patterns** -> bool
- **_is_true_agent** -> bool
- **_is_service_class** -> bool
- **_is_service_singleton** -> bool
- **_is_factory_class** -> bool
- **_is_async_agent** -> bool
- **_is_adapter_class** -> bool
- **_is_config_class** -> bool
- **_is_model_class** -> bool
- **_is_repository_class** -> bool
- **cleanup_redundant_conflicts**
- **update_file_header**
- **sync_companion_test**
- **refactor_non_python_assets**
- **deep_refactor_name** -> int
- **update_imports** -> int
- **verify_environment** -> bool
- **resolve_collision_and_rename** -> bool
- **check_fake_config** -> dict[str, str] | None
- **check_domain_root_purity** -> dict[str, str] | None
- **check_base_agents_purity** -> dict[str, str] | None
- **check_utils_purity** -> dict[str, str] | None
- **check_layer_purity** -> dict[str, Any] | None
- **check_territory_violation** -> Path | None
- **_calculate_move_target** -> Path
- **get_compliant_name** -> str | None
- **heal** -> dict
- **preflight_safety_gates** -> SafetyGateResult
- **generate_execution_plan** -> dict[str, Any]
- **heal_repository** -> dict[str, int]
- **standard_heal**
- **priority_score** -> int


## Class: ClassificationResult

**Description**: Result of content-weighted file classification with confidence scoring.



## Class: FileClassificationHealerAgent

**Description**: 
    Enforces file classification and naming conventions with architectural integrity.

    This agent provides comprehensive file system governance through intelligent
    categorization and naming enforcement across all architectural layers.
    

**Inherits from**: *BASE_CLASSES

### Methods

#### __post_init__
**Parameters**: self

#### enforce_kernel_structure
**Parameters**: self, file_path, layer_root
**Returns**: Path | None
**Description**: 
        Enforce Standard Kernel structure by detecting and relocating misplaced files.

        LCD+ canonical skeleton (config, types, reasoning, enforcement, validators, utils)
        should exist in all layers. Files matching kernel patterns are routed accordingly.

        GLOBAL OVERRIDES (apply regardless of current location):
        - *_validator.py -> agentic_core/L5_safety/validators/ (all validators go to L5)

        KERNEL ROUTING (within layer):
        - *_util.py -> layer_root/utils/
        - *_config.py -> layer_root/config/
        - *_types.py -> layer_root/types/
        - *_script.py (L0 only) -> layer_root/scripts/
        - *Agent.py (at layer root) -> layer_root/reasoning/

        Args:
            file_path: The file to check
            layer_root: Optional pre-computed layer root

        Returns:
            New target path if file should be moved, None if file is correctly placed.
        

#### _get_correct_folder_for_type
**Parameters**: self, file_path, layer_root
**Returns**: str | None
**Description**: 
        Determine the correct LCD subfolder for a file using AST-based classification.

        Uses classify_file() to parse the file's AST and determine its architectural
        role, then maps that role to the correct LCD folder via FILETYPE_TO_FOLDER.

        NO SUFFIX STRING MATCHING. All routing is based on parsed content.

        Args:
            file_path: Full path to the file (used for AST parsing)
            layer_root: The layer root path (e.g., agentic_core/L5_safety)

        Returns:
            Correct subfolder name (e.g., "config", "types", "reasoning"), or None.
        

#### run
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Entry point for execute_ssot.py orchestration.

#### _orchestrate_audit
**Parameters**: self, root
**Returns**: int
**Description**: Core file classification and audit logic.

#### classify_file
**Parameters**: self, path
**Returns**: FileType
**Description**: 
        Analyze file AST to determine architectural role with STRICT PRIORITY ORDERING.

        WINDSURF IMPLEMENTATION PRIORITY QUEUE (First Match Wins):
        1. STUB     - File contains NOT_AN_AGENT marker (preempts all)
        2. BASE_AGENT - Files in base_agents/ directory (foundational classes)
        2.5 SELF_DETECTION - FileClassificationAgent.py is always an AGENT
        2.7 BLUEPRINT_DETECTION - structure_blueprint.py is always CONFIG
        3. TEST     - Path contains tests/ OR name starts with test_
        4. SCRIPT   - Ops/Maintenance scripts
        5. TYPES    - Collection files & private modules
        6. ORCHESTRATOR - Detect if Orchestrator in class name or path
        7. ADAPTER  - Detect if Strategy or Adapter in class name or file path
        8. CONFIG   - Detect if file name or path contains config, blueprint, settings, or manifest
        9. VALIDATOR - Detect if path contains validators/ or file name ends in _validator
        10. PROTOCOL - Class inherits from typing.Protocol
        11. FACTORY  - Detect if class name ends in Factory
        12. AGENT    - Keep existing inheritance/path logic
        13. MIXIN   - Keep existing logic
        14. CLASS   - Fallback for any other class
        15. UTILITY - Fallback for files with no classes
        

#### _load_adg_behavioral_profile
**Parameters**: self, path
**Returns**: 'tuple[float, list[str]]'
**Description**: Load ADG behavioral profile for a file. Returns (score, signals).

        Always safe to call — returns (0.5, []) when ADG SQLite is unavailable.
        

#### classify_file_with_signals
**Parameters**: self, path
**Returns**: ClassificationResult
**Description**: Classify a file and enrich the result with ADG behavioral signals.

        Returns a ClassificationResult with:
          - file_type from classify_file()
          - adg_behavioral_score and adg_behavioral_signals from ADGBehavioralIndex
          - confidence set to 1.0 (structural classification is deterministic)
          - execution_mode promoted to REASONING when adg_behavioral_score > 0.7
        

#### _detect_enforcer_control_signal
**Parameters**: self, tree, content
**Returns**: bool
**Description**: Detect control outcome signal for ENFORCER AND-gate.

        Returns True if file contains:
        - raise *Error inside validate_* or assert_*_allowed
        - OR function returning (False, "...") pattern
        

#### _detect_orchestrator_patterns
**Parameters**: self, tree, path, content, primary_name
**Returns**: bool
**Description**: 
        Distinguish between L0 routers and L3 orchestrators based on behavioral patterns.

        Phase 2 hardened: inheritance signals, broader tokens, multi-class coordinator,
        relaxed threshold for exact suffix match.

        Returns:
            True if file exhibits orchestrator behavior, False if router or neither.
        

#### _validate_orchestrator_invariants
**Parameters**: self, tree, path, content
**Returns**: str
**Description**: Post-classification invariant validation for ORCHESTRATOR files.

        Checks:
        1. Role coordination evidence (>=2 distinct role buckets)
        2. Mutation indicators (hard fail / soft warn)
        3. Thin wrapper downgrade (<=3 funcs, <=50 LOC, single call path)

        Returns:
            "ORCHESTRATOR" if invariants pass, "ENGINE" if downgraded.
        

#### _validate_orchestrator_layer_alignment
**Parameters**: self, path, file_type
**Returns**: None
**Description**: Report-only: flag ORCHESTRATOR files outside L3_orchestration/.

        Exceptions (no flag):
        - apps_*/ directories
        - agentic_core/L5_safety/runners/ (scripts)
        - knowledge/ (warning-only)
        - *_enforcer.py files
        

#### _validate_router_invariants
**Parameters**: self, tree, path, content
**Returns**: None
**Description**: Report-only invariant validation for router files (ENGINE).

        Checks for anti-patterns that violate router expectations:
        1. mutation — router should not perform file I/O
        2. workflow — router should not have multi-stage execution
        3. inheritance — router should not inherit orchestrator bases
        4. structure — router should not have >5 functions

        Router remains ENGINE regardless of violations.
        

#### _detect_filename_tag_conflicts
**Parameters**: self, path
**Returns**: set[str]
**Description**: 
        Detect conflicting classification tags in a filename.

        Uses COMPOUND_SUFFIX_CONFLICTS from blueprint config to match specific
        compound suffix patterns (e.g., "_agent_types", "_config_script") that
        indicate two classification tags in one filename.

        Returns empty set if clean, or the set of conflicting tags if found.
        Does NOT flag domain words (e.g., "agents" in "find_misnamed_agents_util.py").
        

#### _to_pascal_case
**Parameters**: self, name
**Returns**: str
**Description**: 
        Converts snake_case or mixed case to PascalCase.
        Example: 'pii_sanitizer' -> 'PiiSanitizer', 'PDFLoader' -> 'PdfLoader'
        

#### _to_smart_snake_case
**Parameters**: self, name
**Returns**: str
**Description**: 
        Converts PascalCase to snake_case while preserving acronyms.
        Example: 'PIISanitizer' -> 'pii_sanitizer', 'PDFLoader' -> 'pdf_loader'

        Hardening: Recognizes project-specific atomic words to prevent false positives.
        - "Grounding" stays as "grounding", not "g_r_ounding"
        - "Routing" stays as "routing", not "r_outing"
        

#### _sanitize_filename
**Parameters**: self, stem
**Returns**: str
**Description**: 
        Strip known architectural suffixes from a filename stem to prevent stuttering.

        This prevents "stuttering" (e.g., feature_flags_config_util.py) and
        "hybrid suffixes" (e.g., embedding_config_types_config.py).

        Logic: Iteratively remove known suffixes until none remain.

        IMPORTANT: Only strips TRAILING architectural suffixes, not semantic content.
        For example, "agent_discovery" keeps "agent" because it's semantic, not a suffix.

        Args:
            stem: The filename stem (without .py extension)

        Returns:
            The sanitized core name with trailing architectural suffixes removed.

        Examples:
            - "feature_flags_config_util" -> "feature_flags"
            - "embedding_config_types_config" -> "embedding"
            - "user_profile_types" -> "user_profile"
            - "agent_discovery_util" -> "agent_discovery" (keeps semantic "agent")
        

#### normalize_filename
**Parameters**: self, name
**Returns**: str
**Description**: 
        Smart normalization that fixes root cause naming violations.

        Fixes:
        1. Stuttering acronyms: s_s_o_t_ → ssot_ (naive CamelCase split)
        2. Multiple underscores: ___ → _ (unsanitized concatenation)
        3. Leading underscores: _cc_visitor → cc_visitor (legacy convention)

        Args:
            name: The filename (with or without .py extension)

        Returns:
            Normalized filename with root cause violations corrected.

        Examples:
            - "s_s_o_t_consolidation_analyzer.py" → "ssot_consolidation_analyzer.py"
            - "setup___init___util.py" → "setup_init_util.py"
            - "_cc_visitor.py" → "cc_visitor.py"
        

#### _check_forbidden_patterns
**Parameters**: self, filename
**Returns**: list[dict[str, str]]
**Description**: 
        Check a filename against FORBIDDEN_FILENAME_PATTERNS from the constitution.

        Args:
            filename: The filename to check (without directory path)

        Returns:
            List of violation dicts with 'pattern' and 'reason' for each match.
        

#### validate_pascal_case_placement
**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Validate that PascalCase .py files are only in folders that expect them.

        PascalCase filenames (e.g., EnvelopeFactory.py) are reserved for Agents,
        Adapters, and base classes. Finding them in engine/, types/, utils/, or
        config/ folders indicates misclassification.

        Returns None if compliant, or a violation dict.
        

#### validate_app_prefix_placement
**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Validate that files with app-specific prefixes (rg_, lic_) are inside
        their corresponding apps_* directory, not in ops_scripts/ or agentic_core/.

        Also detects stuttering prefixes like r_g_ (should be rg_).
        

#### validate_territory_alignment
**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Validate that files in ops_scripts/ (or other non-app territories) are not
        functionally bound to a specific apps_* domain.

        Uses the SAME import-based + AST content analysis rigor as agentic_core
        classification. Detects:
        - Direct `from apps_rg.*` or `from apps_lic.*` imports
        - Path string references like `Path("apps_rg/...")`
        - Domain keyword density (resume/cv/linkedin/campaign)

        Returns None if compliant, or a violation dict.
        

#### validate_layer_alignment
**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Layer-level validation using import/content signals + subprocess allowlists.

        Policies enforced:
        - PURPOSE OVER MECHANISM: classify by what the file achieves, not how.
        - L5 subprocess imports flagged UNLESS on L5_SUBPROCESS_ALLOWLIST.
        - L6 subprocess/playwright flagged UNLESS on L6_HYBRID_ALLOWLIST.
        - Agent classes outside reasoning/ flagged as AGENT_OUTSIDE_REASONING.
        - PascalCase / test_* files in scripts/ flagged as SCRIPTS_PURITY_VIOLATION.
        - Nested LCD subtrees under leaf domains flagged.

        Returns None if compliant, or a violation dict.
        

#### suggest_manager_layer
**Parameters**: self, path
**Returns**: str | None
**Description**: 
        Phase 2.5 Manager routing: resolve *Manager classes to the correct layer
        using import/content signals instead of defaulting to a single folder.

        Rules:
        - *Manager with cache/state/persist/store signals → L4_state
        - *Manager with workflow/dag/pipeline/orchestrat signals → L3_orchestration
        - *Manager with tool/api/subprocess/request signals → L2_execution
        - Otherwise → None (use default classification)

        Returns layer name or None if no strong signal.
        

#### suggest_agent_layer
**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Generalized layer-routing for ALL Agent files using AST-based import
        analysis + content signals.  Supersedes suggest_manager_layer() which
        only handled *Manager classes.

        Two-pass detection:
          Pass 1 — Infrastructure imports (high confidence):
            Direct third-party imports (redis, pinecone, subprocess, …) and
            cross-layer agentic_core imports strongly indicate purpose.
          Pass 2 — Content keyword signals (medium confidence):
            Keyword frequency in non-comment code lines.

        Returns None if the agent appears correctly placed, or a dict:
            {"current_layer", "suggested_layer", "confidence", "evidence"}
        

#### validate_single_suffix
**Parameters**: self, filename
**Returns**: dict[str, Any] | None
**Description**: 
        Pre-classification gate: reject files with multiple architectural suffixes.

        LCD+ Single-Suffix Rule: every .py file must have AT MOST ONE known
        architectural suffix. Files like *_types_config.py have ambiguous
        classification and must be renamed before processing.

        Args:
            filename: The filename to check (e.g., "model_provider_types_config.py")

        Returns:
            None if compliant, or a violation dict with:
                - found_suffixes: list of detected suffixes
                - primary_suffix: recommended suffix (rightmost match)
                - suggested_name: auto-corrected filename with single suffix
        

#### validate_folder_suffix_consistency
**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Enforce that files in typed LCD folders have matching suffixes.

        Rules:
        - Files in types/   -> must end with _types.py, _protocol.py, or match I*Protocol.py
        - Files in utils/   -> must end with _util.py, _mixin.py, or _helper.py
        - Files in config/  -> must end with _config.py, _settings.py, or _blueprint.py
        - Files in reasoning/ -> must end with Agent.py or other reasoning suffixes

        Args:
            path: Full file path to validate

        Returns:
            None if compliant, or a dict with 'folder', 'expected_suffixes', 'suggested_name'.
        

#### _enforce_folder_purity
**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Bidirectional folder purity enforcement.

        Unlike enforce_kernel_structure() which only routes files INTO correct folders,
        this method EVICTS files from folders they don't belong in.

        Example: reasoning/ should ONLY contain *Agent.py files.
        A file like error_recovery_guardrail.py in reasoning/ is a purity violation.

        Handles both Python AND non-Python files (YAML, JSON, HTML, JS, CSS).

        [GOVERNANCE 2026-02-16] Additional rules:
        - FAIL-CLOSED: Unknown folders fail
        - NO ROOT FILES: Governed folder roots cannot have direct files
        - L0-L6 enforcement/: forbid SCRIPT, SERVICE must end with suffix

        Returns:
            None if file is in a valid folder, or violation dict with eviction target.
        

#### _detect_cross_domain_violation
**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Detect app-domain agents misplaced in agentic_core/.

        Files with app-specific prefixes (Lic*, Campaign*, Outreach*) belong in
        their respective apps_* directories, not in agentic_core/.

        Returns:
            None if no violation, or violation dict with correct app domain.
        

#### _detect_ephemeral_scripts
**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Detect one-off migration/maintenance scripts with numbered phase/wave/sprint patterns.

        These files are ephemeral artifacts that accumulate as tech debt.
        Exempts legitimate domain uses (e.g., TwoPhaseDeduplication, execution_phase_types).

        Returns:
            None if file is clean, or violation dict if ephemeral script detected.
        

#### _detect_cross_layer_naming_violation
**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Detect files with layer indicators in their filename that don't match their
        actual layer location.

        Example: l5_streamer.py in L6_observability/ — the 'l5' in the filename
        implies it belongs to L5_safety, but it's physically in L6.

        Returns:
            None if no violation, or violation dict with details.
        

#### _detect_duplicate_files
**Parameters**: self, file_registry
**Returns**: list[dict[str, Any]]
**Description**: 
        Detect duplicate filenames across the codebase and determine which copy is canonical.

        Uses CANONICAL_LOCATION_PRIORITY to resolve which copy wins. The copy in the
        highest-priority location is kept; others are flagged for deletion.

        Also checks whether any importers reference the duplicate's path — if so,
        the import must be redirected to the canonical location before deletion.

        Args:
            file_registry: List of all file paths being audited.

        Returns:
            List of violation dicts, one per duplicate file (not per group).
        

#### _detect_semantic_duplicates
**Parameters**: self, file_registry
**Returns**: list[dict[str, Any]]
**Description**: Detect same-directory files with overlapping primary class names.

        Two files in the same directory whose primary (first) AST class shares a
        normalised stem are flagged.  The file with more external importers wins;
        ties are broken alphabetically (shorter name first).
        

#### _compute_layer_affinity
**Parameters**: self, path
**Returns**: dict[str, float]
**Description**: 
        Compute semantic layer affinity scores using AST analysis.

        Analyzes:
        1. Module/class docstrings for layer keywords
        2. Class names for domain indicators
        3. Method names for behavioral patterns
        4. Import targets for dependency affinity

        Returns:
            Dict mapping layer names (L0-L6) to affinity scores (0.0-1.0).
        

#### _compute_content_scores
**Parameters**: self, path
**Returns**: dict[str, int]
**Description**: 
        AST-based content scoring to determine true file type by content analysis.

        Walks the AST and assigns weighted scores to each classification category
        based on actual code patterns, NOT filename suffixes.

        Scoring weights:
        - TYPES:     +10 per @dataclass, +10 per BaseModel, +10 per Enum, +15 per Protocol
        - CONFIG:    +5 per UPPER_CASE constant, +3 per settings dict pattern
        - AGENT:     +20 per class ending in 'Agent' or inheriting from *Agent
        - UTILITY:   +3 per standalone function (not a class method)
        - VALIDATOR: +5 per validate_/check_ function

        Args:
            path: File path to analyze

        Returns:
            Dict mapping category names to integer scores.
        

#### classify_file_with_confidence
**Parameters**: self, path
**Returns**: ClassificationResult
**Description**: 
        Content-weighted classification with confidence scoring.

        Uses AST-based content analysis to determine file type and reports
        confidence level. Low-confidence results (<0.6) include ambiguity warnings.

        Args:
            path: File path to classify

        Returns:
            ClassificationResult with file_type, confidence, signals, and warnings.
        

#### _detect_test_patterns
**Parameters**: self, tree, path
**Returns**: dict[str, bool]
**Description**: 
        Enhanced test detection using AST analysis.

        Detects:
        - Classes inheriting from unittest.TestCase
        - pytest fixtures and test functions
        - Test methods (starting with test_)
        - Mock/patch usage
        

#### _detect_script_patterns
**Parameters**: self, tree, path
**Returns**: dict[str, bool]
**Description**: 
        Enhanced script detection using AST analysis.

        Detects:
        - if __name__ == "__main__" patterns
        - argparse or click usage
        - Direct execution patterns
        - Script-like function names (main, run, execute, start)
        

#### _detect_type_patterns
**Parameters**: self, tree, path
**Returns**: dict[str, bool]
**Description**: 
        Enhanced type collection detection using AST analysis.

        Detects:
        - Multiple enum classes
        - TypeVar usage
        - Protocol definitions
        - Abstract base classes
        - Data model patterns
        

#### _fuzzy_match_name_or_content
**Parameters**: self, name, path, content, patterns
**Returns**: bool
**Description**: 
        Fuzzy matching for names and content patterns.

        Uses multiple strategies:
        - Exact name matching
        - Partial name matching
        - Content pattern matching (excluding comments)
        

#### _detect_config_patterns
**Parameters**: self, tree, path, content, indicators, patterns
**Returns**: bool
**Description**: 
        Enhanced config detection using AST analysis.

        Detects:
        - Classes with config-like attributes
        - Constant definitions
        - Configuration loading patterns
        - Settings management
        

#### _detect_validator_patterns
**Parameters**: self, tree, path, content, patterns
**Returns**: bool
**Description**: 
        Enhanced validator detection using AST analysis.

        Detects:
        - Validation methods
        - Check functions
        - Verification patterns
        - Schema validation
        

#### _is_true_agent
**Parameters**: self, node, file_path
**Returns**: bool
**Description**: 
        Enhanced agent detection with multiple criteria.

        Checks:
        1. Naming convention (ends with Agent)
        2. Inheritance from base agents
        3. Decorator-based detection
        4. Method-based detection (execute, act, heal, run)
        

#### _is_service_class
**Parameters**: self, node, file_path
**Returns**: bool
**Description**: 
        Detect service classes with dependency injection patterns.

        Checks:
        1. @service decorator
        2. Constructor with service_container/injector/container parameter
        3. Name ends with Service
        

#### _is_service_singleton
**Parameters**: self, node, class_name
**Returns**: bool
**Description**: 
        Detect singleton service/infrastructure classes (NOT agents).

        These are classes like RagTelemetryCollector, UnifiedAgentMonitor,
        ExecutionTimer — infrastructure singletons that belong in utils/.

        Detection criteria (requires 2+ signals):
        1. Class name ends with a SERVICE_CLASS_INDICATOR (Collector, Monitor, etc.)
        2. Has _instance class attribute (singleton pattern)
        3. Has record_*/emit_*/publish_*/get_metrics methods (telemetry API)
        4. Has __new__ with singleton guard (cls._instance is None)

        Returns True only if the class matches 2+ signals to avoid false positives.
        

#### _is_factory_class
**Parameters**: self, node
**Returns**: bool
**Description**: 
        Detect factory classes for object creation.

        Checks:
        1. Name ends with Factory
        2. Has create_* or make_* methods
        3. Has @factory decorator
        

#### _is_async_agent
**Parameters**: self, node, file_path
**Returns**: bool
**Description**: 
        Detect async-based agents.

        Checks:
        1. Has async execute/act/run methods
        2. Has async context manager methods
        

#### _is_adapter_class
**Parameters**: self, node
**Returns**: bool
**Description**: 
        Detect adapter/wrapper classes.

        Checks:
        1. Name ends with Adapter, Wrapper, or Bridge
        2. Has adapt/wrap/bridge methods
        3. Wraps another object (has _wrapped or _adaptee attribute)
        

#### _is_config_class
**Parameters**: self, node, file_path
**Returns**: bool
**Description**: 
        Detect configuration classes.

        Checks:
        1. Path contains config/
        2. Name ends with Config, Settings, or Options
        3. Has @dataclass decorator with config-like attributes
        

#### _is_model_class
**Parameters**: self, node
**Returns**: bool
**Description**: 
        Detect data model classes.

        Checks:
        1. Inherits from pydantic BaseModel
        2. Has @dataclass decorator
        3. Name ends with Model, Schema, DTO
        

#### _is_repository_class
**Parameters**: self, node
**Returns**: bool
**Description**: 
        Detect repository pattern classes.

        Checks:
        1. Name ends with Repository
        2. Has CRUD methods (create, read, update, delete, save, find, get, list)
        3. Name ends with DAO (Data Access Object)
        

#### cleanup_redundant_conflicts
**Parameters**: self, root
**Description**: 
        Scans for .CONFLICT files and removes them ONLY if they are byte-for-byte
        identical to the live file they conflicted with.
        

#### update_file_header
**Parameters**: self, path, old_name, new_name
**Description**: Updates the File: and Path: metadata in docstrings to match reality.

#### sync_companion_test
**Parameters**: self, src_path, new_name
**Description**: Renames the corresponding test file if it exists.

#### refactor_non_python_assets
**Parameters**: self, old_name, new_name
**Description**: Scans JSON/YAML/TOML/TXT files for string references (Config Drift).

#### deep_refactor_name
**Parameters**: self, old_name, new_name
**Returns**: int
**Description**: 
        Performs a Deep Rename of a class symbol across the entire codebase.
        Updates:
        1. Class definitions: 'class OldName:' -> 'class NewName:'
        2. Imports: 'from x import OldName' -> 'from x import NewName'
        3. Init Exports: 'from .OldFile import OldName' -> 'from .NewFile import NewName'
        4. Type Hints / Usages: 'x: OldName' -> 'x: NewName'
        

#### update_imports
**Parameters**: self, old_name, new_name
**Returns**: int
**Description**: Refactors imports using the in-memory registry to avoid O(N²) disk hits.

#### verify_environment
**Parameters**: self
**Returns**: bool
**Description**: Checks for LongPathsEnabled on Windows.

#### resolve_collision_and_rename
**Parameters**: self, src, dest_name, target_dir
**Returns**: bool
**Description**: 
        Handles renaming with intelligent collision resolution.
        Supports optional target_dir for moving files across directories.
        Returns True if the VIOLATION was resolved (either by rename, delete, or move).
        

#### check_fake_config
**Parameters**: self, path, content
**Returns**: dict[str, str] | None
**Description**: 
        Detect files ending in _config.py that contain active logic (classes with methods).

        A genuine config file should only contain constants, dataclasses, or simple assignments.
        If it has class definitions with non-trivial methods (beyond __init__), it's a
        misnamed utility masquerading as config.

        Also classifies Verifier/Guardian/Lock classes as UTILITY unless they inherit
        from SovereignBaseAgent.

        Args:
            path: File path being checked
            content: File content as string

        Returns:
            Violation dict with 'type', 'message', 'suggested_suffix' or None if clean.
        

#### check_domain_root_purity
**Parameters**: self, path
**Returns**: dict[str, str] | None
**Description**: 
        Enforce the Leaf Node Rule: domain roots must NOT contain logic files.

        Domain directories like knowledge/, semantic_memory/ must only contain
        sub-directories. Python files (except __init__.py) at the root level
        are violations that must be moved into appropriate sub-directories.

        Also enforces snake_case naming within knowledge/ domain.

        Args:
            path: File path being checked

        Returns:
            Violation dict or None if clean.
        

#### check_base_agents_purity
**Parameters**: self, path
**Returns**: dict[str, str] | None
**Description**: 
        Enforce STRICT IDENTITY ONLY rule for base_agents/.

        Only SovereignBaseAgent.py, L*Base.py, decorators.py, __init__.py, and
        CanonBaseAgentInterface.py are allowed. Mixins must be in mixins/.
        Everything else (types, utils, exceptions, engines) is a CRITICAL VIOLATION.

        Args:
            path: File path being checked

        Returns:
            Violation dict or None if clean.
        

#### check_utils_purity
**Parameters**: self, path, content
**Returns**: dict[str, str] | None
**Description**: 
        Enforce sanitization rules for agentic_core/ directories.

        Rules:
        1. test_*.py files must NOT exist inside agentic_core/ (except tests/).
        2. utilities_* prefix is banned (redundant naming).
        3. Scripts (if __name__ == '__main__') in utils/ must move to L0_routing/scripts.

        Args:
            path: File path being checked
            content: Optional file content for script detection

        Returns:
            Violation dict or None if clean.
        

#### check_layer_purity
**Parameters**: self, path, content, classification
**Returns**: dict[str, Any] | None
**Description**: 
        Detect cognitive contamination in L0 and passive-agent naming violations.

        Rules:
        1. L0 agents must be reflexive/deterministic — no debate, synthesis, or LLM generation.
        2. Classes named *Agent that are dataclasses/BaseModel with no run/execute/heal method
           are "passive agents" and should be classified as UTILITY or TYPES.

        Args:
            path: File path being checked
            content: File content as string
            classification: Current file type classification

        Returns:
            Violation dict with 'type', 'message', 'suggested_destination' or None if clean.
        

#### check_territory_violation
**Parameters**: self, path, file_type
**Returns**: Path | None
**Description**: 
        Enforces physical-to-logical alignment with Context-Aware Sovereignty.
        Distinguishes between App-Layer (Strict Pattern) and Core-Layer (Domain Semantic).

        [HARDENED] Robust against deep nesting and handles all file types.
        

#### _calculate_move_target
**Parameters**: self, path, root_index, target_folder
**Returns**: Path
**Description**: 
        Robustly calculates the move target relative to the Sovereign Root.
        Fixes the 'parent.parent' fragility by pivoting from the anchor.

        Strategy: Root / Target_Folder / Filename
        (Flattens nesting to enforce standard structure)
        

#### get_compliant_name
**Parameters**: self, path, file_type
**Returns**: str | None
**Description**: Calculates the target filename. Returns None if no change needed.

        Zero-Ambiguity Naming Standard:
        - PROTOCOL: PascalCase, starts with 'I' (e.g., IHealerProtocol.py)
        - CLASS: *Base.py for foundational base agents (e.g., L1CognitionBase.py)
        - STRATEGY: PascalCase with Strategy.py suffix
        - ADAPTER: PascalCase with Adapter.py suffix
        - SCRIPT: snake_case (no _script suffix — scripts/ folder is the signal)
        - UTILITY: snake_case with _util.py suffix
        - TYPES: snake_case with _types.py suffix
        - EXCEPTION: snake_case with _exceptions.py suffix
        - STRATEGY (in strategies/): snake_case with _strategy.py suffix
        - MIXIN: snake_case with _mixin.py suffix
        

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal naming violations using unified classification logic.

        Uses the same classify_file() and get_compliant_name() methods as the
        main audit to ensure consistent detection and healing behavior.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (naming)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format.
        

#### preflight_safety_gates
**Parameters**: self, scan_root
**Returns**: SafetyGateResult
**Description**: 
        WAVE 1.1–1.3: Run all safety gates on the current file registry.

        Builds a rename_map from proposed renames, then checks:
          1. Rename collisions (dst conflict, casing, existing file)
          2. Import impact / blast radius
          3. Mass action threshold

        Stores result in self.last_safety_gate_result.
        Must be called AFTER _orchestrate_audit populates file_registry,
        or after an explicit scan.
        

#### generate_execution_plan
**Parameters**: self, scan_root
**Returns**: dict[str, Any]
**Description**: 
        WAVE 3.1: Produce a deterministic, machine-readable execution plan.

        Runs preflight_safety_gates if not already run, then builds
        a stable-ordered plan with blocking annotations.

        Stores result in self.last_execution_plan.
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path, target_territory, auto_approve, cached_scan
**Returns**: dict[str, int]
**Description**: 
        Standard healing interface for execute_ssot.py integration.

        This method provides the canonical healing interface that integrates
        with the HealerMixin chain and execute_ssot.py orchestration.

        Args:
            dry_run: If True, only propose changes without applying them
            execute: If True, apply changes (overrides dry_run)
            depth: Current recursion depth for cycle detection
            max_depth: Maximum recursion depth allowed
            _call_path: Set of agent IDs already in call path (cycle detection)
            target_territory: If specified, scope healing to this territory only
                              (e.g., "prompt_governance" -> agentic_core/prompt_governance)
            auto_approve: If True, skip interactive prompts (for CI/automated runs)
        



## Function: get_python_files_fast

**Parameters**: root
**Returns**: list[Path]
**Description**: 
    Scoped repository scanner for territories with enforced structure.

    Scans only sovereign territories with SSOT-defined structure requirements.
    Excludes volatile/output directories (logs, archives) and gitignored paths.
    



## Function: main

**Description**: Standalone execution for testing.



## Function: __post_init__

**Parameters**: self


## Function: enforce_kernel_structure

**Parameters**: self, file_path, layer_root
**Returns**: Path | None
**Description**: 
        Enforce Standard Kernel structure by detecting and relocating misplaced files.

        LCD+ canonical skeleton (config, types, reasoning, enforcement, validators, utils)
        should exist in all layers. Files matching kernel patterns are routed accordingly.

        GLOBAL OVERRIDES (apply regardless of current location):
        - *_validator.py -> agentic_core/L5_safety/validators/ (all validators go to L5)

        KERNEL ROUTING (within layer):
        - *_util.py -> layer_root/utils/
        - *_config.py -> layer_root/config/
        - *_types.py -> layer_root/types/
        - *_script.py (L0 only) -> layer_root/scripts/
        - *Agent.py (at layer root) -> layer_root/reasoning/

        Args:
            file_path: The file to check
            layer_root: Optional pre-computed layer root

        Returns:
            New target path if file should be moved, None if file is correctly placed.
        



## Function: _get_correct_folder_for_type

**Parameters**: self, file_path, layer_root
**Returns**: str | None
**Description**: 
        Determine the correct LCD subfolder for a file using AST-based classification.

        Uses classify_file() to parse the file's AST and determine its architectural
        role, then maps that role to the correct LCD folder via FILETYPE_TO_FOLDER.

        NO SUFFIX STRING MATCHING. All routing is based on parsed content.

        Args:
            file_path: Full path to the file (used for AST parsing)
            layer_root: The layer root path (e.g., agentic_core/L5_safety)

        Returns:
            Correct subfolder name (e.g., "config", "types", "reasoning"), or None.
        



## Function: run

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Entry point for execute_ssot.py orchestration.



## Function: _orchestrate_audit

**Parameters**: self, root
**Returns**: int
**Description**: Core file classification and audit logic.



## Function: classify_file

**Parameters**: self, path
**Returns**: FileType
**Description**: 
        Analyze file AST to determine architectural role with STRICT PRIORITY ORDERING.

        WINDSURF IMPLEMENTATION PRIORITY QUEUE (First Match Wins):
        1. STUB     - File contains NOT_AN_AGENT marker (preempts all)
        2. BASE_AGENT - Files in base_agents/ directory (foundational classes)
        2.5 SELF_DETECTION - FileClassificationAgent.py is always an AGENT
        2.7 BLUEPRINT_DETECTION - structure_blueprint.py is always CONFIG
        3. TEST     - Path contains tests/ OR name starts with test_
        4. SCRIPT   - Ops/Maintenance scripts
        5. TYPES    - Collection files & private modules
        6. ORCHESTRATOR - Detect if Orchestrator in class name or path
        7. ADAPTER  - Detect if Strategy or Adapter in class name or file path
        8. CONFIG   - Detect if file name or path contains config, blueprint, settings, or manifest
        9. VALIDATOR - Detect if path contains validators/ or file name ends in _validator
        10. PROTOCOL - Class inherits from typing.Protocol
        11. FACTORY  - Detect if class name ends in Factory
        12. AGENT    - Keep existing inheritance/path logic
        13. MIXIN   - Keep existing logic
        14. CLASS   - Fallback for any other class
        15. UTILITY - Fallback for files with no classes
        



## Function: _load_adg_behavioral_profile

**Parameters**: self, path
**Returns**: 'tuple[float, list[str]]'
**Description**: Load ADG behavioral profile for a file. Returns (score, signals).

        Always safe to call — returns (0.5, []) when ADG SQLite is unavailable.
        



## Function: classify_file_with_signals

**Parameters**: self, path
**Returns**: ClassificationResult
**Description**: Classify a file and enrich the result with ADG behavioral signals.

        Returns a ClassificationResult with:
          - file_type from classify_file()
          - adg_behavioral_score and adg_behavioral_signals from ADGBehavioralIndex
          - confidence set to 1.0 (structural classification is deterministic)
          - execution_mode promoted to REASONING when adg_behavioral_score > 0.7
        



## Function: _detect_enforcer_control_signal

**Parameters**: self, tree, content
**Returns**: bool
**Description**: Detect control outcome signal for ENFORCER AND-gate.

        Returns True if file contains:
        - raise *Error inside validate_* or assert_*_allowed
        - OR function returning (False, "...") pattern
        



## Function: _detect_orchestrator_patterns

**Parameters**: self, tree, path, content, primary_name
**Returns**: bool
**Description**: 
        Distinguish between L0 routers and L3 orchestrators based on behavioral patterns.

        Phase 2 hardened: inheritance signals, broader tokens, multi-class coordinator,
        relaxed threshold for exact suffix match.

        Returns:
            True if file exhibits orchestrator behavior, False if router or neither.
        



## Function: _validate_orchestrator_invariants

**Parameters**: self, tree, path, content
**Returns**: str
**Description**: Post-classification invariant validation for ORCHESTRATOR files.

        Checks:
        1. Role coordination evidence (>=2 distinct role buckets)
        2. Mutation indicators (hard fail / soft warn)
        3. Thin wrapper downgrade (<=3 funcs, <=50 LOC, single call path)

        Returns:
            "ORCHESTRATOR" if invariants pass, "ENGINE" if downgraded.
        



## Function: _validate_orchestrator_layer_alignment

**Parameters**: self, path, file_type
**Returns**: None
**Description**: Report-only: flag ORCHESTRATOR files outside L3_orchestration/.

        Exceptions (no flag):
        - apps_*/ directories
        - agentic_core/L5_safety/runners/ (scripts)
        - knowledge/ (warning-only)
        - *_enforcer.py files
        



## Function: _validate_router_invariants

**Parameters**: self, tree, path, content
**Returns**: None
**Description**: Report-only invariant validation for router files (ENGINE).

        Checks for anti-patterns that violate router expectations:
        1. mutation — router should not perform file I/O
        2. workflow — router should not have multi-stage execution
        3. inheritance — router should not inherit orchestrator bases
        4. structure — router should not have >5 functions

        Router remains ENGINE regardless of violations.
        



## Function: _detect_filename_tag_conflicts

**Parameters**: self, path
**Returns**: set[str]
**Description**: 
        Detect conflicting classification tags in a filename.

        Uses COMPOUND_SUFFIX_CONFLICTS from blueprint config to match specific
        compound suffix patterns (e.g., "_agent_types", "_config_script") that
        indicate two classification tags in one filename.

        Returns empty set if clean, or the set of conflicting tags if found.
        Does NOT flag domain words (e.g., "agents" in "find_misnamed_agents_util.py").
        



## Function: _to_pascal_case

**Parameters**: self, name
**Returns**: str
**Description**: 
        Converts snake_case or mixed case to PascalCase.
        Example: 'pii_sanitizer' -> 'PiiSanitizer', 'PDFLoader' -> 'PdfLoader'
        



## Function: _to_smart_snake_case

**Parameters**: self, name
**Returns**: str
**Description**: 
        Converts PascalCase to snake_case while preserving acronyms.
        Example: 'PIISanitizer' -> 'pii_sanitizer', 'PDFLoader' -> 'pdf_loader'

        Hardening: Recognizes project-specific atomic words to prevent false positives.
        - "Grounding" stays as "grounding", not "g_r_ounding"
        - "Routing" stays as "routing", not "r_outing"
        



## Function: _sanitize_filename

**Parameters**: self, stem
**Returns**: str
**Description**: 
        Strip known architectural suffixes from a filename stem to prevent stuttering.

        This prevents "stuttering" (e.g., feature_flags_config_util.py) and
        "hybrid suffixes" (e.g., embedding_config_types_config.py).

        Logic: Iteratively remove known suffixes until none remain.

        IMPORTANT: Only strips TRAILING architectural suffixes, not semantic content.
        For example, "agent_discovery" keeps "agent" because it's semantic, not a suffix.

        Args:
            stem: The filename stem (without .py extension)

        Returns:
            The sanitized core name with trailing architectural suffixes removed.

        Examples:
            - "feature_flags_config_util" -> "feature_flags"
            - "embedding_config_types_config" -> "embedding"
            - "user_profile_types" -> "user_profile"
            - "agent_discovery_util" -> "agent_discovery" (keeps semantic "agent")
        



## Function: normalize_filename

**Parameters**: self, name
**Returns**: str
**Description**: 
        Smart normalization that fixes root cause naming violations.

        Fixes:
        1. Stuttering acronyms: s_s_o_t_ → ssot_ (naive CamelCase split)
        2. Multiple underscores: ___ → _ (unsanitized concatenation)
        3. Leading underscores: _cc_visitor → cc_visitor (legacy convention)

        Args:
            name: The filename (with or without .py extension)

        Returns:
            Normalized filename with root cause violations corrected.

        Examples:
            - "s_s_o_t_consolidation_analyzer.py" → "ssot_consolidation_analyzer.py"
            - "setup___init___util.py" → "setup_init_util.py"
            - "_cc_visitor.py" → "cc_visitor.py"
        



## Function: _check_forbidden_patterns

**Parameters**: self, filename
**Returns**: list[dict[str, str]]
**Description**: 
        Check a filename against FORBIDDEN_FILENAME_PATTERNS from the constitution.

        Args:
            filename: The filename to check (without directory path)

        Returns:
            List of violation dicts with 'pattern' and 'reason' for each match.
        



## Function: validate_pascal_case_placement

**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Validate that PascalCase .py files are only in folders that expect them.

        PascalCase filenames (e.g., EnvelopeFactory.py) are reserved for Agents,
        Adapters, and base classes. Finding them in engine/, types/, utils/, or
        config/ folders indicates misclassification.

        Returns None if compliant, or a violation dict.
        



## Function: validate_app_prefix_placement

**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Validate that files with app-specific prefixes (rg_, lic_) are inside
        their corresponding apps_* directory, not in ops_scripts/ or agentic_core/.

        Also detects stuttering prefixes like r_g_ (should be rg_).
        



## Function: validate_territory_alignment

**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Validate that files in ops_scripts/ (or other non-app territories) are not
        functionally bound to a specific apps_* domain.

        Uses the SAME import-based + AST content analysis rigor as agentic_core
        classification. Detects:
        - Direct `from apps_rg.*` or `from apps_lic.*` imports
        - Path string references like `Path("apps_rg/...")`
        - Domain keyword density (resume/cv/linkedin/campaign)

        Returns None if compliant, or a violation dict.
        



## Function: validate_layer_alignment

**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Layer-level validation using import/content signals + subprocess allowlists.

        Policies enforced:
        - PURPOSE OVER MECHANISM: classify by what the file achieves, not how.
        - L5 subprocess imports flagged UNLESS on L5_SUBPROCESS_ALLOWLIST.
        - L6 subprocess/playwright flagged UNLESS on L6_HYBRID_ALLOWLIST.
        - Agent classes outside reasoning/ flagged as AGENT_OUTSIDE_REASONING.
        - PascalCase / test_* files in scripts/ flagged as SCRIPTS_PURITY_VIOLATION.
        - Nested LCD subtrees under leaf domains flagged.

        Returns None if compliant, or a violation dict.
        



## Function: suggest_manager_layer

**Parameters**: self, path
**Returns**: str | None
**Description**: 
        Phase 2.5 Manager routing: resolve *Manager classes to the correct layer
        using import/content signals instead of defaulting to a single folder.

        Rules:
        - *Manager with cache/state/persist/store signals → L4_state
        - *Manager with workflow/dag/pipeline/orchestrat signals → L3_orchestration
        - *Manager with tool/api/subprocess/request signals → L2_execution
        - Otherwise → None (use default classification)

        Returns layer name or None if no strong signal.
        



## Function: suggest_agent_layer

**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Generalized layer-routing for ALL Agent files using AST-based import
        analysis + content signals.  Supersedes suggest_manager_layer() which
        only handled *Manager classes.

        Two-pass detection:
          Pass 1 — Infrastructure imports (high confidence):
            Direct third-party imports (redis, pinecone, subprocess, …) and
            cross-layer agentic_core imports strongly indicate purpose.
          Pass 2 — Content keyword signals (medium confidence):
            Keyword frequency in non-comment code lines.

        Returns None if the agent appears correctly placed, or a dict:
            {"current_layer", "suggested_layer", "confidence", "evidence"}
        



## Function: validate_single_suffix

**Parameters**: self, filename
**Returns**: dict[str, Any] | None
**Description**: 
        Pre-classification gate: reject files with multiple architectural suffixes.

        LCD+ Single-Suffix Rule: every .py file must have AT MOST ONE known
        architectural suffix. Files like *_types_config.py have ambiguous
        classification and must be renamed before processing.

        Args:
            filename: The filename to check (e.g., "model_provider_types_config.py")

        Returns:
            None if compliant, or a violation dict with:
                - found_suffixes: list of detected suffixes
                - primary_suffix: recommended suffix (rightmost match)
                - suggested_name: auto-corrected filename with single suffix
        



## Function: validate_folder_suffix_consistency

**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Enforce that files in typed LCD folders have matching suffixes.

        Rules:
        - Files in types/   -> must end with _types.py, _protocol.py, or match I*Protocol.py
        - Files in utils/   -> must end with _util.py, _mixin.py, or _helper.py
        - Files in config/  -> must end with _config.py, _settings.py, or _blueprint.py
        - Files in reasoning/ -> must end with Agent.py or other reasoning suffixes

        Args:
            path: Full file path to validate

        Returns:
            None if compliant, or a dict with 'folder', 'expected_suffixes', 'suggested_name'.
        



## Function: _enforce_folder_purity

**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Bidirectional folder purity enforcement.

        Unlike enforce_kernel_structure() which only routes files INTO correct folders,
        this method EVICTS files from folders they don't belong in.

        Example: reasoning/ should ONLY contain *Agent.py files.
        A file like error_recovery_guardrail.py in reasoning/ is a purity violation.

        Handles both Python AND non-Python files (YAML, JSON, HTML, JS, CSS).

        [GOVERNANCE 2026-02-16] Additional rules:
        - FAIL-CLOSED: Unknown folders fail
        - NO ROOT FILES: Governed folder roots cannot have direct files
        - L0-L6 enforcement/: forbid SCRIPT, SERVICE must end with suffix

        Returns:
            None if file is in a valid folder, or violation dict with eviction target.
        



## Function: _detect_cross_domain_violation

**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Detect app-domain agents misplaced in agentic_core/.

        Files with app-specific prefixes (Lic*, Campaign*, Outreach*) belong in
        their respective apps_* directories, not in agentic_core/.

        Returns:
            None if no violation, or violation dict with correct app domain.
        



## Function: _detect_ephemeral_scripts

**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Detect one-off migration/maintenance scripts with numbered phase/wave/sprint patterns.

        These files are ephemeral artifacts that accumulate as tech debt.
        Exempts legitimate domain uses (e.g., TwoPhaseDeduplication, execution_phase_types).

        Returns:
            None if file is clean, or violation dict if ephemeral script detected.
        



## Function: _detect_cross_layer_naming_violation

**Parameters**: self, path
**Returns**: dict[str, Any] | None
**Description**: 
        Detect files with layer indicators in their filename that don't match their
        actual layer location.

        Example: l5_streamer.py in L6_observability/ — the 'l5' in the filename
        implies it belongs to L5_safety, but it's physically in L6.

        Returns:
            None if no violation, or violation dict with details.
        



## Function: _detect_duplicate_files

**Parameters**: self, file_registry
**Returns**: list[dict[str, Any]]
**Description**: 
        Detect duplicate filenames across the codebase and determine which copy is canonical.

        Uses CANONICAL_LOCATION_PRIORITY to resolve which copy wins. The copy in the
        highest-priority location is kept; others are flagged for deletion.

        Also checks whether any importers reference the duplicate's path — if so,
        the import must be redirected to the canonical location before deletion.

        Args:
            file_registry: List of all file paths being audited.

        Returns:
            List of violation dicts, one per duplicate file (not per group).
        



## Function: _detect_semantic_duplicates

**Parameters**: self, file_registry
**Returns**: list[dict[str, Any]]
**Description**: Detect same-directory files with overlapping primary class names.

        Two files in the same directory whose primary (first) AST class shares a
        normalised stem are flagged.  The file with more external importers wins;
        ties are broken alphabetically (shorter name first).
        



## Function: _compute_layer_affinity

**Parameters**: self, path
**Returns**: dict[str, float]
**Description**: 
        Compute semantic layer affinity scores using AST analysis.

        Analyzes:
        1. Module/class docstrings for layer keywords
        2. Class names for domain indicators
        3. Method names for behavioral patterns
        4. Import targets for dependency affinity

        Returns:
            Dict mapping layer names (L0-L6) to affinity scores (0.0-1.0).
        



## Function: _compute_content_scores

**Parameters**: self, path
**Returns**: dict[str, int]
**Description**: 
        AST-based content scoring to determine true file type by content analysis.

        Walks the AST and assigns weighted scores to each classification category
        based on actual code patterns, NOT filename suffixes.

        Scoring weights:
        - TYPES:     +10 per @dataclass, +10 per BaseModel, +10 per Enum, +15 per Protocol
        - CONFIG:    +5 per UPPER_CASE constant, +3 per settings dict pattern
        - AGENT:     +20 per class ending in 'Agent' or inheriting from *Agent
        - UTILITY:   +3 per standalone function (not a class method)
        - VALIDATOR: +5 per validate_/check_ function

        Args:
            path: File path to analyze

        Returns:
            Dict mapping category names to integer scores.
        



## Function: classify_file_with_confidence

**Parameters**: self, path
**Returns**: ClassificationResult
**Description**: 
        Content-weighted classification with confidence scoring.

        Uses AST-based content analysis to determine file type and reports
        confidence level. Low-confidence results (<0.6) include ambiguity warnings.

        Args:
            path: File path to classify

        Returns:
            ClassificationResult with file_type, confidence, signals, and warnings.
        



## Function: _detect_test_patterns

**Parameters**: self, tree, path
**Returns**: dict[str, bool]
**Description**: 
        Enhanced test detection using AST analysis.

        Detects:
        - Classes inheriting from unittest.TestCase
        - pytest fixtures and test functions
        - Test methods (starting with test_)
        - Mock/patch usage
        



## Function: _detect_script_patterns

**Parameters**: self, tree, path
**Returns**: dict[str, bool]
**Description**: 
        Enhanced script detection using AST analysis.

        Detects:
        - if __name__ == "__main__" patterns
        - argparse or click usage
        - Direct execution patterns
        - Script-like function names (main, run, execute, start)
        



## Function: _detect_type_patterns

**Parameters**: self, tree, path
**Returns**: dict[str, bool]
**Description**: 
        Enhanced type collection detection using AST analysis.

        Detects:
        - Multiple enum classes
        - TypeVar usage
        - Protocol definitions
        - Abstract base classes
        - Data model patterns
        



## Function: _fuzzy_match_name_or_content

**Parameters**: self, name, path, content, patterns
**Returns**: bool
**Description**: 
        Fuzzy matching for names and content patterns.

        Uses multiple strategies:
        - Exact name matching
        - Partial name matching
        - Content pattern matching (excluding comments)
        



## Function: _detect_config_patterns

**Parameters**: self, tree, path, content, indicators, patterns
**Returns**: bool
**Description**: 
        Enhanced config detection using AST analysis.

        Detects:
        - Classes with config-like attributes
        - Constant definitions
        - Configuration loading patterns
        - Settings management
        



## Function: _detect_validator_patterns

**Parameters**: self, tree, path, content, patterns
**Returns**: bool
**Description**: 
        Enhanced validator detection using AST analysis.

        Detects:
        - Validation methods
        - Check functions
        - Verification patterns
        - Schema validation
        



## Function: _is_true_agent

**Parameters**: self, node, file_path
**Returns**: bool
**Description**: 
        Enhanced agent detection with multiple criteria.

        Checks:
        1. Naming convention (ends with Agent)
        2. Inheritance from base agents
        3. Decorator-based detection
        4. Method-based detection (execute, act, heal, run)
        



## Function: _is_service_class

**Parameters**: self, node, file_path
**Returns**: bool
**Description**: 
        Detect service classes with dependency injection patterns.

        Checks:
        1. @service decorator
        2. Constructor with service_container/injector/container parameter
        3. Name ends with Service
        



## Function: _is_service_singleton

**Parameters**: self, node, class_name
**Returns**: bool
**Description**: 
        Detect singleton service/infrastructure classes (NOT agents).

        These are classes like RagTelemetryCollector, UnifiedAgentMonitor,
        ExecutionTimer — infrastructure singletons that belong in utils/.

        Detection criteria (requires 2+ signals):
        1. Class name ends with a SERVICE_CLASS_INDICATOR (Collector, Monitor, etc.)
        2. Has _instance class attribute (singleton pattern)
        3. Has record_*/emit_*/publish_*/get_metrics methods (telemetry API)
        4. Has __new__ with singleton guard (cls._instance is None)

        Returns True only if the class matches 2+ signals to avoid false positives.
        



## Function: _is_factory_class

**Parameters**: self, node
**Returns**: bool
**Description**: 
        Detect factory classes for object creation.

        Checks:
        1. Name ends with Factory
        2. Has create_* or make_* methods
        3. Has @factory decorator
        



## Function: _is_async_agent

**Parameters**: self, node, file_path
**Returns**: bool
**Description**: 
        Detect async-based agents.

        Checks:
        1. Has async execute/act/run methods
        2. Has async context manager methods
        



## Function: _is_adapter_class

**Parameters**: self, node
**Returns**: bool
**Description**: 
        Detect adapter/wrapper classes.

        Checks:
        1. Name ends with Adapter, Wrapper, or Bridge
        2. Has adapt/wrap/bridge methods
        3. Wraps another object (has _wrapped or _adaptee attribute)
        



## Function: _is_config_class

**Parameters**: self, node, file_path
**Returns**: bool
**Description**: 
        Detect configuration classes.

        Checks:
        1. Path contains config/
        2. Name ends with Config, Settings, or Options
        3. Has @dataclass decorator with config-like attributes
        



## Function: _is_model_class

**Parameters**: self, node
**Returns**: bool
**Description**: 
        Detect data model classes.

        Checks:
        1. Inherits from pydantic BaseModel
        2. Has @dataclass decorator
        3. Name ends with Model, Schema, DTO
        



## Function: _is_repository_class

**Parameters**: self, node
**Returns**: bool
**Description**: 
        Detect repository pattern classes.

        Checks:
        1. Name ends with Repository
        2. Has CRUD methods (create, read, update, delete, save, find, get, list)
        3. Name ends with DAO (Data Access Object)
        



## Function: cleanup_redundant_conflicts

**Parameters**: self, root
**Description**: 
        Scans for .CONFLICT files and removes them ONLY if they are byte-for-byte
        identical to the live file they conflicted with.
        



## Function: update_file_header

**Parameters**: self, path, old_name, new_name
**Description**: Updates the File: and Path: metadata in docstrings to match reality.



## Function: sync_companion_test

**Parameters**: self, src_path, new_name
**Description**: Renames the corresponding test file if it exists.



## Function: refactor_non_python_assets

**Parameters**: self, old_name, new_name
**Description**: Scans JSON/YAML/TOML/TXT files for string references (Config Drift).



## Function: deep_refactor_name

**Parameters**: self, old_name, new_name
**Returns**: int
**Description**: 
        Performs a Deep Rename of a class symbol across the entire codebase.
        Updates:
        1. Class definitions: 'class OldName:' -> 'class NewName:'
        2. Imports: 'from x import OldName' -> 'from x import NewName'
        3. Init Exports: 'from .OldFile import OldName' -> 'from .NewFile import NewName'
        4. Type Hints / Usages: 'x: OldName' -> 'x: NewName'
        



## Function: update_imports

**Parameters**: self, old_name, new_name
**Returns**: int
**Description**: Refactors imports using the in-memory registry to avoid O(N²) disk hits.



## Function: verify_environment

**Parameters**: self
**Returns**: bool
**Description**: Checks for LongPathsEnabled on Windows.



## Function: resolve_collision_and_rename

**Parameters**: self, src, dest_name, target_dir
**Returns**: bool
**Description**: 
        Handles renaming with intelligent collision resolution.
        Supports optional target_dir for moving files across directories.
        Returns True if the VIOLATION was resolved (either by rename, delete, or move).
        



## Function: check_fake_config

**Parameters**: self, path, content
**Returns**: dict[str, str] | None
**Description**: 
        Detect files ending in _config.py that contain active logic (classes with methods).

        A genuine config file should only contain constants, dataclasses, or simple assignments.
        If it has class definitions with non-trivial methods (beyond __init__), it's a
        misnamed utility masquerading as config.

        Also classifies Verifier/Guardian/Lock classes as UTILITY unless they inherit
        from SovereignBaseAgent.

        Args:
            path: File path being checked
            content: File content as string

        Returns:
            Violation dict with 'type', 'message', 'suggested_suffix' or None if clean.
        



## Function: check_domain_root_purity

**Parameters**: self, path
**Returns**: dict[str, str] | None
**Description**: 
        Enforce the Leaf Node Rule: domain roots must NOT contain logic files.

        Domain directories like knowledge/, semantic_memory/ must only contain
        sub-directories. Python files (except __init__.py) at the root level
        are violations that must be moved into appropriate sub-directories.

        Also enforces snake_case naming within knowledge/ domain.

        Args:
            path: File path being checked

        Returns:
            Violation dict or None if clean.
        



## Function: check_base_agents_purity

**Parameters**: self, path
**Returns**: dict[str, str] | None
**Description**: 
        Enforce STRICT IDENTITY ONLY rule for base_agents/.

        Only SovereignBaseAgent.py, L*Base.py, decorators.py, __init__.py, and
        CanonBaseAgentInterface.py are allowed. Mixins must be in mixins/.
        Everything else (types, utils, exceptions, engines) is a CRITICAL VIOLATION.

        Args:
            path: File path being checked

        Returns:
            Violation dict or None if clean.
        



## Function: check_utils_purity

**Parameters**: self, path, content
**Returns**: dict[str, str] | None
**Description**: 
        Enforce sanitization rules for agentic_core/ directories.

        Rules:
        1. test_*.py files must NOT exist inside agentic_core/ (except tests/).
        2. utilities_* prefix is banned (redundant naming).
        3. Scripts (if __name__ == '__main__') in utils/ must move to L0_routing/scripts.

        Args:
            path: File path being checked
            content: Optional file content for script detection

        Returns:
            Violation dict or None if clean.
        



## Function: check_layer_purity

**Parameters**: self, path, content, classification
**Returns**: dict[str, Any] | None
**Description**: 
        Detect cognitive contamination in L0 and passive-agent naming violations.

        Rules:
        1. L0 agents must be reflexive/deterministic — no debate, synthesis, or LLM generation.
        2. Classes named *Agent that are dataclasses/BaseModel with no run/execute/heal method
           are "passive agents" and should be classified as UTILITY or TYPES.

        Args:
            path: File path being checked
            content: File content as string
            classification: Current file type classification

        Returns:
            Violation dict with 'type', 'message', 'suggested_destination' or None if clean.
        



## Function: check_territory_violation

**Parameters**: self, path, file_type
**Returns**: Path | None
**Description**: 
        Enforces physical-to-logical alignment with Context-Aware Sovereignty.
        Distinguishes between App-Layer (Strict Pattern) and Core-Layer (Domain Semantic).

        [HARDENED] Robust against deep nesting and handles all file types.
        



## Function: _calculate_move_target

**Parameters**: self, path, root_index, target_folder
**Returns**: Path
**Description**: 
        Robustly calculates the move target relative to the Sovereign Root.
        Fixes the 'parent.parent' fragility by pivoting from the anchor.

        Strategy: Root / Target_Folder / Filename
        (Flattens nesting to enforce standard structure)
        



## Function: get_compliant_name

**Parameters**: self, path, file_type
**Returns**: str | None
**Description**: Calculates the target filename. Returns None if no change needed.

        Zero-Ambiguity Naming Standard:
        - PROTOCOL: PascalCase, starts with 'I' (e.g., IHealerProtocol.py)
        - CLASS: *Base.py for foundational base agents (e.g., L1CognitionBase.py)
        - STRATEGY: PascalCase with Strategy.py suffix
        - ADAPTER: PascalCase with Adapter.py suffix
        - SCRIPT: snake_case (no _script suffix — scripts/ folder is the signal)
        - UTILITY: snake_case with _util.py suffix
        - TYPES: snake_case with _types.py suffix
        - EXCEPTION: snake_case with _exceptions.py suffix
        - STRATEGY (in strategies/): snake_case with _strategy.py suffix
        - MIXIN: snake_case with _mixin.py suffix
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal naming violations using unified classification logic.

        Uses the same classify_file() and get_compliant_name() methods as the
        main audit to ensure consistent detection and healing behavior.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (naming)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: preflight_safety_gates

**Parameters**: self, scan_root
**Returns**: SafetyGateResult
**Description**: 
        WAVE 1.1–1.3: Run all safety gates on the current file registry.

        Builds a rename_map from proposed renames, then checks:
          1. Rename collisions (dst conflict, casing, existing file)
          2. Import impact / blast radius
          3. Mass action threshold

        Stores result in self.last_safety_gate_result.
        Must be called AFTER _orchestrate_audit populates file_registry,
        or after an explicit scan.
        



## Function: generate_execution_plan

**Parameters**: self, scan_root
**Returns**: dict[str, Any]
**Description**: 
        WAVE 3.1: Produce a deterministic, machine-readable execution plan.

        Runs preflight_safety_gates if not already run, then builds
        a stable-ordered plan with blocking annotations.

        Stores result in self.last_execution_plan.
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path, target_territory, auto_approve, cached_scan
**Returns**: dict[str, int]
**Description**: 
        Standard healing interface for execute_ssot.py integration.

        This method provides the canonical healing interface that integrates
        with the HealerMixin chain and execute_ssot.py orchestration.

        Args:
            dry_run: If True, only propose changes without applying them
            execute: If True, apply changes (overrides dry_run)
            depth: Current recursion depth for cycle detection
            max_depth: Maximum recursion depth allowed
            _call_path: Set of agent IDs already in call path (cycle detection)
            target_territory: If specified, scope healing to this territory only
                              (e.g., "prompt_governance" -> agentic_core/prompt_governance)
            auto_approve: If True, skip interactive prompts (for CI/automated runs)
        



## Function: standard_heal

**Parameters**: func
**Description**: Simple fallback that preserves function.



## Function: priority_score

**Parameters**: p
**Returns**: int


## Usage Examples

### Class Usage

```python
# Using ClassificationResult
classificationresult = ClassificationResult()
```

```python
# Using FileClassificationHealerAgent
fileclassificationhealeragent = FileClassificationHealerAgent()
fileclassificationhealeragent.enforce_kernel_structure()
fileclassificationhealeragent.run()
```

### Function Usage

```python
# Using get_python_files_fast
result = get_python_files_fast(root)
```

```python
# Using main
result = main()
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:05.196642
**Type**: api_reference
**Quality**: comprehensive
