# API Documentation: execute_ssot

**Target Audience**: developers, api_users

# execute_ssot API Documentation

**File**: `execute_ssot.py`
**Classes**: 17
**Functions**: 145

## Classes

- **ConfidenceScore**
- **FailureType** (inherits from <ast.Attribute object at 0x000001CBFAEE6350>)
- **RoutingTier** (inherits from <ast.Attribute object at 0x000001CBFAEE4550>)
- **RoutingInputs**
- **RoutingDecision**
- **ReconciliationViolation**
- **ReconciliationManifest**
- **ASTCodeQualityValidator**
- **HealContext**
- **SovereignDecisionEngine**
- **PreFlightValidator**
- **NonInteractiveGuard**
- **RuntimeStateManager**
- **GracefulExitHandler**
- **tqdm**
- **IHealerProtocol**
- **LegacyAgentAdapter**

## Functions

- **_get_sovereign_excluded_folders**
- **_get_uwg**
- **_get_heal_result_adapter**
- **_get_safe_subprocess_run**
- **_get_write_gateway**
- **_get_execution_context_class**
- **_get_location_validator_agent**
- **_get_location_healer_agent**
- **_fire_meta_learning_intake** -> None
- **_get_l5_agent_roster**
- **_preflight_import_check** -> None
- **_optional_runtime_guard**
- **_safe_print** -> None
- **run_fence_self_check** -> None
- **resolve_repo_root**
- **_apply_v15_enforcement_flag** -> None
- **_configure_logging** -> None
- **_maybe_force_utf8_console** -> None
- **_maybe_force_utf8_logging_handlers** -> None
- **_v15_build_ssot_manifest**
- **_v15_ssot_gateway_audit** -> None
- **compute_routing_decision** -> RoutingDecision
- **_normalize_finding_id** -> str
- **_write_pre_validation_json** -> None
- **_write_post_validation_json** -> None
- **_write_run_manifest_json** -> None
- **_write_decision_summary_json** -> None
- **_write_artifact_integrity_json** -> None
- **with_retry**
- **execute_phase2_reconciliation**
- **validate_territory_input** -> tuple[bool, str]
- **discover_agents_from_registry** -> list[tuple[str, str]]
- **execute_phase3_validation**
- **execute_phase1_discovery**
- **execute_phase1_discovery_impl**
- **execute_phase3_alignment**
- **execute_phase3_alignment_impl**
- **_run_gravity_repair_global**
- **execute_phase4_architectural_validation**
- **execute_phase4_validation_impl**
- **execute_phase5_healing**
- **execute_phase5_healing_impl**
- **execute_phase7_final**
- **execute_phase7_final_impl**
- **save_comprehensive_reports**
- **save_aggregate_report** -> Path | None
- **try_summon_orchestrator**
- **get_execution_plan** -> list[dict]
- **_emit_pipeline_digest** -> str
- **_print_healing_heatmap** -> None
- **_print_meta_learning_summary** -> None
- **_print_run_manifest** -> int
- **_collect_llm_call_trace** -> dict
- **_collect_blocker_scan** -> list
- **_build_coverage_proof** -> dict
- **_build_calibration_proof** -> dict
- **_write_mandatory_json_output** -> None
- **_write_heal_run_complete** -> dict
- **_write_failure_forensics** -> None
- **_print_executive_summary** -> None
- **run_pipeline** -> 'dict[str, object]'
- **print_execution_plan** -> None
- **resolve_agent_subset** -> list[str]
- **list_available_agents**
- **_emit_adg_pre_run_artifact** -> None
- **main** -> int
- **_build_ssot_territory_targets** -> list[str]
- **_compute_pipeline_digest** -> str
- **_legacy_main**
- **load_agents** -> dict[str, Any]
- **_high_threshold** -> float
- **_med_threshold** -> float
- **is_high_confidence** -> bool
- **is_medium_confidence** -> bool
- **is_low_confidence** -> bool
- **as_log_line** -> str
- **_decide** -> RoutingDecision
- **to_dict** -> dict
- **add_modification** -> None
- **add_failure** -> None
- **finalize** -> dict[str, Any]
- **__init__**
- **_read_and_parse_file** -> tuple[ast.AST | None, str | None]
- **check_file_quality** -> dict
- **enable_llm** -> bool
- **dry_run** -> bool
- **from_args** -> 'HealContext'
- **__init__**
- **_calculate_semantic_similarity** -> float
- **_get_bmg_cosine_similarity** -> object
- **_get_bmg_embedding_agent_keys** -> frozenset
- **_get_qwen_14b_routing_config** -> tuple
- **_get_qwen_vllm_arbiter**
- **_calculate_pattern_confidence** -> float
- **_compute_novelty_score** -> int
- **_route_decision** -> 'RoutingDecision'
- **_classify_violation_type** -> str
- **_check_healing_budget** -> tuple[bool, str]
- **calculate_healing_confidence** -> ConfidenceScore
- **should_proceed_with_healing** -> tuple[bool, str]
- **_hitl_gate** -> tuple[bool, str]
- **request_sovereignty_token** -> bool
- **release_sovereignty_token** -> None
- **__init__**
- **run_checks** -> tuple[bool, list[str]]
- **validate_agent_integrity** -> list[str]
- **__init__**
- **__enter__**
- **__exit__**
- **_trap_input**
- **decorator**
- **__init__**
- **start_mission**
- **update_agent**
- **skip_agent**
- **complete_agent**
- **add_event**
- **finish_mission**
- **save**
- **_emergency_cleanup**
- **update_meta_learning**
- **_bar** -> str
- **_sec** -> None
- **_row** -> None
- **_lookup_outcome** -> str
- **_gate_detail** -> list[str]
- **__init__**
- **exit_gracefully**
- **standard_heal**
- **_arbiter** -> dict
- **wrapper**
- **_json_serialise**
- **_agg_json_serialise**
- **__init__**
- **__iter__**
- **__next__**
- **update**
- **set_description**
- **__enter__**
- **__exit__**
- **_noop_guard**
- **__init__**
- **heal**
- **_w6_hitl_archive_gate**
- **_identity**


## Class: ConfidenceScore

**Description**: [HARDENED] Environment-aware confidence score for autonomous healing.

### Methods

#### _high_threshold
**Parameters**: self
**Returns**: float
**Description**: Sourced from .env: SOVEREIGN_HIGH_CONFIDENCE (default: 0.75)

#### _med_threshold
**Parameters**: self
**Returns**: float
**Description**: Sourced from .env: SOVEREIGN_MEDIUM_CONFIDENCE (default: 0.50)

#### is_high_confidence
**Parameters**: self
**Returns**: bool

#### is_medium_confidence
**Parameters**: self
**Returns**: bool

#### is_low_confidence
**Parameters**: self
**Returns**: bool



## Class: FailureType

**Description**: Classifies the failure being routed.  Drives gate selection.

**Inherits from**: _enum.Enum



## Class: RoutingTier

**Inherits from**: _enum.Enum



## Class: RoutingInputs

**Description**: All inputs to compute_routing_decision.  No embeddings allowed.



## Class: RoutingDecision

**Description**: Immutable routing result with full audit trail.

### Methods

#### as_log_line
**Parameters**: self
**Returns**: str



## Class: ReconciliationViolation

**Description**: Structured violation for enhanced telemetry (Ported from FilesystemSSOTReconciler).

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict



## Class: ReconciliationManifest

**Description**: Telemetry manifest for tracking all reconciliation changes.

### Methods

#### add_modification
**Parameters**: self, modification
**Returns**: None

#### add_failure
**Parameters**: self, failure
**Returns**: None

#### finalize
**Parameters**: self
**Returns**: dict[str, Any]



## Class: ASTCodeQualityValidator

**Description**: AST-based code quality validation with memory guards (Ported from TypeMechanic).

### Methods

#### __init__
**Parameters**: self, project_root

#### _read_and_parse_file
**Parameters**: self, fp
**Returns**: tuple[ast.AST | None, str | None]
**Description**: Reads a file and parses it into an AST with strict size limits.

#### check_file_quality
**Parameters**: self, file_path
**Returns**: dict
**Description**: Check file for code quality issues (missing types, etc).



## Class: HealContext

**Description**: Immutable healing configuration passed uniformly to every phase function.

    Single control surface: --heal drives ALL active-mode flags.

      --heal ON  => heal, auto_approve, enable_llm, enable_telemetry,
                    enable_meta_learning all True
      --heal OFF => scan/report only, everything passive

    Per hostile audit Section B1: trace_id must appear in every artifact.
    Per hostile audit Section E1: trace_id threads through all artifacts and HealContext.
    Per hostile audit Section E10: execution_mode distinguishes scan/heal/validate modes.
    

### Methods

#### enable_llm
**Parameters**: self
**Returns**: bool
**Description**: LLM arbitration is always active when healing — not a separate flag.

#### dry_run
**Parameters**: self
**Returns**: bool
**Description**: Convenience alias — inverted heal for legacy call sites.

#### from_args
**Parameters**: cls, args
**Returns**: 'HealContext'
**Description**: Construct from parsed CLI args. Single construction point.

        Canonical flag semantics (--heal is the ONLY active-mode switch):
          --heal ON  => heal, auto_approve, enable_llm, enable_telemetry,
                        enable_meta_learning all True
          --heal OFF => all passive/scan-only

        Deprecated flags (kept for backward-compat, emit warnings):
          --dry-run        => same as omitting --heal
          --manual         => always autonomous now
          --interactive    => auto_approve is always True under --heal
          --apply-proposals => meta-learning always on under --heal
        



## Class: SovereignDecisionEngine

**Description**: 
    [HARDENED] Sovereign Decision Engine with strict token-based access control.
    Synthesizes patterns from FileClassificationAgent for cycle detection and resource protection.
    Unified flat class (formerly AutonomousDecisionEngine -> Enhanced -> Sovereign hierarchy).
    

### Methods

#### __init__
**Parameters**: self, enable_llm, state_mgr, enable_cda, execution_context, healing_memory_retriever, auto_approve

#### _calculate_semantic_similarity
**Parameters**: self, unknown, existing
**Returns**: float
**Description**: Calculate semantic similarity for unknown items against a candidate list.

        Uses BAAI/bge-m3 cosine similarity (GPU-accelerated on RTX 5090).
        Falls back to Jaccard word-overlap only on exception.
        

#### _get_bmg_cosine_similarity
**Returns**: object
**Description**: Lazy seam: load bmg_cosine_similarity from L2 healers without module-level import.

#### _get_bmg_embedding_agent_keys
**Returns**: frozenset
**Description**: Lazy seam: load BMG_EMBEDDING_AGENT_KEYS from L2 healing_tier_config.

#### _get_qwen_14b_routing_config
**Returns**: tuple
**Description**: Lazy seam: load Qwen 14B routing constants from L2 healing_tier_config.

#### _get_qwen_vllm_arbiter
**Description**: Lazy seam: return callable that invokes Qwen 14B via WSL vLLM subprocess.

#### _calculate_pattern_confidence
**Parameters**: self, violation_type
**Returns**: float
**Description**: Regex-based pattern matching for known violation types.

#### _compute_novelty_score
**Parameters**: self, failure_type, territory, confidence
**Returns**: int
**Description**: Compute the novelty score N (0-3) for RoutingInputs.

        Embeds the current failure signal text and compares against stored
        vectors to produce a true novelty score:
          N=0  max_similarity >= 0.85  (seen before)
          N=1  max_similarity >= 0.70  (similar)
          N=2  max_similarity >= 0.50  (somewhat novel)
          N=3  max_similarity <  0.50  (highly novel)

        Raises VectorSourceMismatchError if stored vectors and the current
        vector have incompatible dimensions.
        

#### _route_decision
**Parameters**: self, confidence, agent_name, territory, failure_type, retry_count, replay_mode, playbook_match, deterministic_coverage, provider_prohibited_gemini, provider_prohibited_qwen, adg_behavioral_score
**Returns**: 'RoutingDecision'
**Description**: Map healing context to a hardened SSOT RoutingDecision.

#### _classify_violation_type
**Parameters**: self, message
**Returns**: str
**Description**: Classify a violation message into a canonical violation type string.

#### _check_healing_budget
**Parameters**: self, agent_name, depth, max_depth
**Returns**: tuple[bool, str]
**Description**: Prevents infinite healing loops and budget exhaustion.

#### calculate_healing_confidence
**Parameters**: self, violations_count, violation_types, territory, historical_success_rate, agent_name, adg_behavioral_score
**Returns**: ConfidenceScore
**Description**: Calculates weighted confidence score.

        Uses GPU-accelerated BAAI/bge-m3 cosine similarity for pattern matching
        when agent_name is in BMG_EMBEDDING_AGENT_KEYS.

        adg_behavioral_score [0.0–1.0] from ADGBehavioralIndex:
          <0.4  script-like: +0.05 confidence boost (deterministic agents are easier to heal)
          >0.7  agent-like:  -0.05 confidence penalty (adaptive agents require more caution)
          0.5   unknown:     no adjustment
        

#### should_proceed_with_healing
**Parameters**: self, confidence, agent_name, territory, failure_type, retry_count, replay_mode, playbook_match, deterministic_coverage, provider_prohibited_gemini, provider_prohibited_qwen, adg_behavioral_score
**Returns**: tuple[bool, str]
**Description**: Determines if healing should proceed using the hardened SSOT routing algorithm.

#### _hitl_gate
**Parameters**: self, agent_name, confidence, tier
**Returns**: tuple[bool, str]
**Description**: 
        HITL terminal gate for medium/low confidence healing decisions.

        Prints a structured prompt showing the agent, confidence score, and
        reasoning, then reads Y/N/D from stdin. Non-interactive environments
        (no tty) default to DEFER (reject).

        Returns:
            (approved: bool, reason: str)
        

#### request_sovereignty_token
**Parameters**: self, agent_name, operation
**Returns**: bool
**Description**: 
        Request permission to perform a state-mutating operation.
        Enforces atomic locking and stack depth limits.
        

#### release_sovereignty_token
**Parameters**: self, agent_name, success
**Returns**: None
**Description**: Release the lock after operation completion.



## Class: PreFlightValidator

**Description**: 
    [ULTRA-HARDENED] Sovereign Contract Enforcer.
    Verifies environmental readiness and enforces strict agent signatures/imports.
    

### Methods

#### __init__
**Parameters**: self, project_root, dry_run

#### run_checks
**Parameters**: self
**Returns**: tuple[bool, list[str]]

#### validate_agent_integrity
**Parameters**: self, agents
**Returns**: list[str]
**Description**: 
        [CONTRACT GUARD] Mandatory validation of all registered agents.
        Catches legacy signatures, broken mixins, and instantiation failures.
        



## Class: NonInteractiveGuard

**Description**: 
    [HARDENED] Global overrides to prevent terminal prompts from hanging CI/CD.
    Now includes Resource Exhaustion Protection against infinite prompt loops.
    

### Methods

#### __init__
**Parameters**: self, active, max_blocked_prompts

#### __enter__
**Parameters**: self

#### __exit__
**Parameters**: self, exc_type, exc_val, exc_tb

#### _trap_input
**Parameters**: self, prompt



## Class: RuntimeStateManager

**Description**: Manages live state for dashboard observability.

### Methods

#### __init__
**Parameters**: self, project_root, execution_context

#### start_mission
**Parameters**: self, mission_type, agents_order

#### update_agent
**Parameters**: self, agent_name, layer

#### skip_agent
**Parameters**: self, agent_name, reason
**Description**: Records agent as skipped — confidence gate or HITL rejected execution.

#### complete_agent
**Parameters**: self, agent_name, success, details
**Description**: 
        [HARDENED] Silent Aggregation.
        Records agent completion but suppresses intermediate JSON console dumps.
        

#### add_event
**Parameters**: self, event_type, message

#### finish_mission
**Parameters**: self, status

#### save
**Parameters**: self
**Description**: 
        [HARDENED] Atomic Write Pattern with Permission Lockdown.
        Writes to temp file, sets 600 permissions, then renames.
        Once L0 mutation prohibition fires, latches _persistence_disabled=True
        and becomes a no-op for the remainder of the run.
        

#### _emergency_cleanup
**Parameters**: self
**Description**: Ensure state is finalized even on unhandled exit.

#### update_meta_learning
**Parameters**: self, experience_data
**Description**: [INTEGRATION] Updates cognitive metrics for dashboard.



## Class: GracefulExitHandler

**Description**: Captures SIGINT/SIGTERM to allow Phase 2 writes to finish safely.

### Methods

#### __init__
**Parameters**: self, state_mgr

#### exit_gracefully
**Parameters**: self, signum, frame
**Description**: Signal handler.



## Class: tqdm

### Methods

#### __init__
**Parameters**: self, iterable, total, desc

#### __iter__
**Parameters**: self

#### __next__
**Parameters**: self

#### update
**Parameters**: self, n

#### set_description
**Parameters**: self, desc

#### __enter__
**Parameters**: self

#### __exit__
**Parameters**: self



## Class: IHealerProtocol



## Class: LegacyAgentAdapter

### Methods

#### __init__
**Parameters**: self, legacy_agent

#### heal
**Parameters**: self, violation



## Function: _get_sovereign_excluded_folders



## Function: _get_uwg

**Description**: Lazy loader — avoids circular import at module level.



## Function: _get_heal_result_adapter

**Description**: Lazy loader for Tier-3 adapter.



## Function: _get_safe_subprocess_run



## Function: _get_write_gateway



## Function: _get_execution_context_class



## Function: _get_location_validator_agent



## Function: _get_location_healer_agent



## Function: _fire_meta_learning_intake

**Parameters**: state_mgr, now_utc
**Returns**: None
**Description**: Wire HealingOutcomeIntakeAdapter and MetaLearningPipeline after each run.

    Both imports are guarded — if archived modules are not yet restored (pre-Wave 0B)
    this is a safe no-op. After Wave 0B restoration the full pipeline activates.
    



## Function: _get_l5_agent_roster



## Function: _preflight_import_check

**Returns**: None
**Description**: Diagnostic-only helper to verify critical imports can be resolved.

    This function checks that the execute_ssot_entrypoint can be imported
    and that _legacy_main symbol exists without invoking any runtime behavior.
    Also validates BGE embedding availability — BGE is a mandatory dependency.
    Raises RuntimeError with detailed message if any check fails.

    NOTE: Called at startup in _legacy_main to fail-fast on missing symbols.
    



## Function: _optional_runtime_guard

**Description**: Lazy import to avoid import-time failure in bootstrap contexts.

    Fail-closed semantics: when V15_ENFORCEMENT=1 and the guard cannot be
    imported, re-raise so the caller sees a hard failure instead of a silent
    no-op.  When enforcement is off (or unset), fall back to a no-op decorator.
    



## Function: _safe_print

**Parameters**: text
**Returns**: None
**Description**: Print text safely on Windows consoles that use charmap encoding.



## Function: run_fence_self_check

**Returns**: None
**Description**: Run deterministic fence self-check (validates policy + wiring; no mutations).

    Validates:
    1. Default ProtectedRootPolicy immutable_roots equals ("agentic_core","tests",".github")
    2. Default ProtectedRootPolicy log_path is outside IMMUTABLE_ROOTS
    3. write_gateway public entrypoints accept allow_override AND call enforce_protected_root
    4. Telemetry emitter path is writable target ONLY outside IMMUTABLE_ROOTS

    Prints single-line JSON summary to stdout:
    - {"status":"ok","checks":4}
    - or {"status":"fail","failed":["check_name",...]}

    Exits with code 0 if all checks pass, nonzero otherwise.
    



## Function: resolve_repo_root

**Parameters**: start
**Description**: Deterministic repo-root resolver.
    Walk upward from this file (or provided start) until we find repo markers.
    



## Function: _apply_v15_enforcement_flag

**Parameters**: args
**Returns**: None
**Description**: CLI overrides env to ensure determinism in CI/smoke paths.



## Function: _configure_logging

**Parameters**: verbosity
**Returns**: None


## Function: _maybe_force_utf8_console

**Returns**: None
**Description**: Unconditional stdout/stderr UTF-8 coercion.  Called at runtime, NOT import time.



## Function: _maybe_force_utf8_logging_handlers

**Returns**: None
**Description**: Reconfigure existing logging handler streams to UTF-8.  Called at runtime, NOT import time.



## Function: _v15_build_ssot_manifest

**Description**: §8.1e — Construct SurgicalManifest for SSOT bootstrap entry.

    Returns None when V15 enforcement is off (zero overhead).
    Bootstrap-safe: lazy imports with fail-closed semantics.
    



## Function: _v15_ssot_gateway_audit

**Parameters**: manifest, trace_id
**Returns**: None
**Description**: §8.1e — Invoke gateway.execute in LOG_ONLY mode for SSOT audit trail.



## Function: compute_routing_decision

**Parameters**: inputs
**Returns**: RoutingDecision
**Description**: Pure SSOT routing function — strict gate order, no side effects.

    ADG behavioral score integration:
      adg_behavioral_score < 0.4 (script-like) overrides deterministic_coverage=True
        when the structural class gate would otherwise require LLM arbitration.
      adg_behavioral_score > 0.7 (agent-like) with low confidence raises N by 1
        to reflect the observed behavioural complexity of the target file.
    



## Function: _normalize_finding_id

**Parameters**: finding, validator, index
**Returns**: str
**Description**: Generate normalized finding ID: {validator}:{path}:{rule}:{index}.

    Per hostile audit Section B3: Finding IDs must be normalized and deterministic.
    Per .windsurfrules §1.7: Identical input → identical output.
    



## Function: _write_pre_validation_json

**Parameters**: violations, trace_id, territory, validators_used, output_dir
**Returns**: None
**Description**: Write pre_validation.json before any healing occurs.

    Per hostile audit Section C2: Pre-heal state must be captured in structured artifact.
    Per hostile audit Section B3: Findings must have normalized IDs and validator provenance.
    Per .windsurfrules §2.2: Evidence must be deterministic, ASCII-only.
    



## Function: _write_post_validation_json

**Parameters**: pre_validation_path, phase3_result, trace_id, territory, output_dir
**Returns**: None
**Description**: Write post_validation.json after Phase 3 revalidation.

    Per hostile audit Section C4: Post-heal proof with resolved/residual/regression breakdown.
    Per hostile audit Section B5: Must show resolved, remaining, and newly introduced findings.
    



## Function: _write_run_manifest_json

**Parameters**: trace_id, execution_mode, territories, agents_executed, output_dir
**Returns**: None
**Description**: E6: Write run_manifest.json with run metadata and execution summary.

    Per hostile audit Section E6: run_manifest.json provides high-level run metadata.
    



## Function: _write_decision_summary_json

**Parameters**: trace_id, decisions_made, output_dir
**Returns**: None
**Description**: E6: Write decision_summary.json with routing decision audit trail.

    Per hostile audit Section E6: decision_summary.json provides routing decision audit.
    



## Function: _write_artifact_integrity_json

**Parameters**: trace_id, output_dir
**Returns**: None
**Description**: E7: Write artifact_integrity.json as final step with SHA256 hashes of all artifacts.

    Per hostile audit Section E7: artifact_integrity.json provides cryptographic proof of artifact set.
    



## Function: with_retry

**Parameters**: max_retries, delay
**Description**: 
    [HARDENED] Decorator for transient failure resilience with exponential backoff.
    



## Function: execute_phase2_reconciliation

**Parameters**: agents, territory, decision_engine, state_mgr, plan, ctx
**Description**: 
    PHASE 2: EXECUTE HEALING (HARDENED)
    Critical Path: Modifications occur here. Must strictly adhere to decision engine.
    Enhanced with atomic operations and sovereignty patterns from FileClassificationAgent.
    Returns: Dict conforming to HEAL_RESULT_SCHEMA
    



## Function: validate_territory_input

**Parameters**: territory
**Returns**: tuple[bool, str]
**Description**: Validate territory input with comprehensive security checks.



## Function: discover_agents_from_registry

**Parameters**: project_root, dedupe
**Returns**: list[tuple[str, str]]
**Description**: Hybrid agent discovery: prefer cached JSON, fallback to live scan.



## Function: execute_phase3_validation

**Parameters**: agents, territory, original_violations, dry_run
**Description**: 
    PHASE 3: POST-MORTEM VALIDATION

    Verifies that 'fixed' files now pass AST and SSOT checks.
    Does NOT blindly trust the agent's 'success' return value.
    



## Function: execute_phase1_discovery

**Parameters**: agents, territory, decision_engine, state_mgr, ctx
**Description**: PHASE 1: TERRITORIAL DISCOVERY (Retriable)



## Function: execute_phase1_discovery_impl

**Parameters**: agents, territory, decision_engine, state_mgr, ctx
**Description**: PHASE 1: TERRITORIAL DISCOVERY - Implementation with CognitiveDispositionAgent integration



## Function: execute_phase3_alignment

**Parameters**: agents, territory, decision_engine, state_mgr, ctx
**Description**: PHASE 3: STRUCTURAL ALIGNMENT (Retriable)



## Function: execute_phase3_alignment_impl

**Parameters**: agents, territory, decision_engine, state_mgr, ctx
**Description**: PHASE 3: STRUCTURAL ALIGNMENT - Implementation



## Function: _run_gravity_repair_global

**Parameters**: agents, state_mgr, ctx
**Description**: Run GravityLeakRepairAgent once globally — gravity (layer inversions) is repo-wide.



## Function: execute_phase4_architectural_validation

**Parameters**: agents, territory, state_mgr, ctx
**Description**: PHASE 4: ARCHITECTURAL VALIDATION (Retriable)



## Function: execute_phase4_validation_impl

**Parameters**: agents, territory, state_mgr, ctx
**Description**: PHASE 4: ARCHITECTURAL VALIDATION - Implementation



## Function: execute_phase5_healing

**Parameters**: agents, territory, gov_report, decision_engine, state_mgr, ctx
**Description**: PHASE 5: HEALING (Retriable)



## Function: execute_phase5_healing_impl

**Parameters**: agents, territory, gov_report, decision_engine, state_mgr, ctx
**Description**: PHASE 5: HEALING - Implementation



## Function: execute_phase7_final

**Parameters**: agents, territory, state_mgr, decision_engine
**Description**: PHASE 7: CERTIFICATION (Retriable)



## Function: execute_phase7_final_impl

**Parameters**: agents, territory, state_mgr, decision_engine
**Description**: PHASE 7: CERTIFICATION - Implementation with Silent Aggregation



## Function: save_comprehensive_reports

**Parameters**: territory, detailed_cert, markdown_summary, files_affected, project_root
**Description**: 
    [COMPREHENSIVE REPORTS] Save detailed JSON manifest and Markdown summary to persistent files.
    Creates timestamped reports in logs/compliance_reports/ directory.
    



## Function: save_aggregate_report

**Parameters**: targets, project_root
**Returns**: Path | None
**Description**: 
    [AGGREGATE REPORT] Merge all per-territory compliance_report_<t>.json into a single
    compliance_report_AGGREGATE.json in logs/compliance_reports/.

    Deduplicates violations by (type, file, message) so cross-territory duplicates
    (e.g. GRAVITY, ILLEGAL_CACHE_DIR) are counted once.

    Returns the Path to the written file, or None on failure.
    



## Function: try_summon_orchestrator

**Parameters**: project_root, targets, execute
**Description**: Attempts to load L3 Orchestrator for smart execution. Delegates to _ssot_pipeline.



## Function: get_execution_plan

**Returns**: list[dict]
**Description**: Return the deterministic, ordered execution plan.

    Pure introspection — no side effects, no file mutations.
    



## Function: _emit_pipeline_digest

**Parameters**: adapters, territory, ctx
**Returns**: str
**Description**: Compute and print the deterministic pipeline digest (once per run).

    Returns the 64-char hex digest string.
    When SSOT_ORCH_NEGCTRL_TAMPER=1 the digest payload is perturbed so the
    output differs from a clean run — used by the negative-control test.
    



## Function: _print_healing_heatmap

**Parameters**: state_mgr, decision_engine
**Returns**: None
**Description**: Print a per-agent healing count heatmap at end of every run.



## Function: _print_meta_learning_summary

**Parameters**: state_mgr, decision_engine
**Returns**: None
**Description**: Print meta-learning bus additions summary — what this run teaches the next run.



## Function: _print_run_manifest

**Parameters**: state_mgr, targets
**Returns**: int
**Description**: Print a complete agent/phase execution manifest and return the number of gaps.

    Every expected agent must appear in completed_agents. Every territory must have
    executed Phase 1 (discovery). Any gap is printed as an explicit ERROR line.
    Returns the count of gaps so the caller can decide exit behavior.
    Zero tolerance: if it didn't run, it appears here.
    



## Function: _collect_llm_call_trace

**Parameters**: state_mgr, decision_engine
**Returns**: dict
**Description**: Extract LLM invocation proof from healing_actions and decision records.

    Returns a dict with keys:
      - call_trace   : list of proven calls (tier, request_id, hash, latency, status)
      - blocked_calls: list of expected-but-blocked invocations with blocker reason
      - stats        : expected / actual / blocked_by_flags / blocked_by_errors counts
    



## Function: _collect_blocker_scan

**Parameters**: state_mgr
**Returns**: list
**Description**: Extract blocked agent records with timestamps and blocker taxonomy.

    Returns a list of dicts, one per blocked agent:
      agent, blocker_type, flag/dep name, check_timestamp, code_location,
      stack_trace_hash, last_successful_run, remediation
    



## Function: _build_coverage_proof

**Parameters**: state_mgr, decision_engine
**Returns**: dict
**Description**: Build agent coverage proof: expected vs executed vs skipped.

    Returns a dict with:
      expected_agents, executed_agents, skipped_agents,
      coverage_ratio, proof hashes
    



## Function: _build_calibration_proof

**Parameters**: state_mgr, decision_engine
**Returns**: dict
**Description**: Compute per-tier confidence calibration error.

    calibration_error = abs(predicted_success_rate - actual_success_rate)

    Returns dict keyed by canonical tier name with:
      predicted_success, actual_success, calibration_error, sample_size
    



## Function: _write_mandatory_json_output

**Parameters**: state_mgr, decision_engine
**Returns**: None
**Description**: Write mandatory heal-run JSON output to logs/compliance_reports/heal_run_output.json.

    This is always written at the end of every --heal run. It is the authoritative
    machine-readable record of what the run did, what the meta-learning system learned,
    and what the routing engine decided. No querying required after the run.
    



## Function: _write_heal_run_complete

**Parameters**: state_mgr, decision_engine
**Returns**: dict
**Description**: Write authoritative heal_run_complete.json with prove-it evidence for all 6 concerns.

    Sections:
      meta, coverage, routing (llm_call_trace + calibration), learning,
      healing_actions, blockers, executive_summary gate criteria.
    Always written; exceptions are logged and swallowed (fail-safe).
    



## Function: _write_failure_forensics

**Parameters**: state_mgr, decision_engine
**Returns**: None
**Description**: Write failure_forensics.json — detailed drill-down for failed/blocked/misrouted agents.

    Only written when there are failures, blockers, or misrouted agents.
    If all agents succeed and nothing is blocked, the file is not written.
    



## Function: _print_executive_summary

**Parameters**: complete_output
**Returns**: None
**Description**: Print the mandatory high-signal pass/fail executive summary table.

    Accepts the dict returned by _write_heal_run_complete so no recomputation needed.
    12 gate criteria rows, VERDICT line, critical blockers, remediation commands,
    proof integrity check, healing effectiveness breakdown, next-run prediction.
    



## Function: run_pipeline

**Parameters**: adapters, territory, decision_engine, state_mgr, ctx
**Returns**: 'dict[str, object]'
**Description**: Unified pipeline loop. Delegates to _ssot_pipeline.run_pipeline.



## Function: print_execution_plan

**Parameters**: arbitrate_plan, ptc_plan
**Returns**: None
**Description**: Print stable, sorted execution plan to stdout. Delegates to _ssot_pipeline.



## Function: resolve_agent_subset

**Parameters**: requested
**Returns**: list[str]
**Description**: Resolve requested agent keys to a closed set including dependencies. Delegates to _ssot_pipeline.



## Function: list_available_agents

**Parameters**: project_root, dedupe
**Description**: Alias for discover_agents_from_registry (backward compat). Delegates to _ssot_pipeline.



## Function: _emit_adg_pre_run_artifact

**Parameters**: repo_root
**Returns**: None
**Description**: Emit artifacts/adg/execution_impact_<timestamp>.json. Delegates to _ssot_pipeline.



## Function: main

**Returns**: int
**Description**: Deterministic wrapper: logging, V15 enforcement, console, then legacy body.



## Function: _build_ssot_territory_targets

**Parameters**: project_root
**Returns**: list[str]
**Description**: Derive the canonical territory target list from SOVEREIGN_TERRITORIES SSOT. Delegates to _ssot_pipeline.



## Function: _compute_pipeline_digest

**Parameters**: targets
**Returns**: str
**Description**: Compute a stable determinism digest for the pipeline run. Delegates to _ssot_pipeline.



## Function: _legacy_main

**Parameters**: args


## Function: load_agents

**Parameters**: project_root
**Returns**: dict[str, Any]
**Description**: 
    Dynamically discovers and loads compliant Healer Agents.
    Wraps non-compliant agents in LegacyAgentAdapter.

    Scans 'agentic_core' and 'apps_*' for classes that:
    1. Have 'Agent' or 'Validator' in their name.
    2. Implement the 'heal' method (Standard Heal Interface) OR can be adapted.

    Returns:
        Dict[str, Any]: Map of agent_name -> initialized_instance (or adapter)
    



## Function: _high_threshold

**Parameters**: self
**Returns**: float
**Description**: Sourced from .env: SOVEREIGN_HIGH_CONFIDENCE (default: 0.75)



## Function: _med_threshold

**Parameters**: self
**Returns**: float
**Description**: Sourced from .env: SOVEREIGN_MEDIUM_CONFIDENCE (default: 0.50)



## Function: is_high_confidence

**Parameters**: self
**Returns**: bool


## Function: is_medium_confidence

**Parameters**: self
**Returns**: bool


## Function: is_low_confidence

**Parameters**: self
**Returns**: bool


## Function: as_log_line

**Parameters**: self
**Returns**: str


## Function: _decide

**Parameters**: tier, gate, score
**Returns**: RoutingDecision


## Function: to_dict

**Parameters**: self
**Returns**: dict


## Function: add_modification

**Parameters**: self, modification
**Returns**: None


## Function: add_failure

**Parameters**: self, failure
**Returns**: None


## Function: finalize

**Parameters**: self
**Returns**: dict[str, Any]


## Function: __init__

**Parameters**: self, project_root


## Function: _read_and_parse_file

**Parameters**: self, fp
**Returns**: tuple[ast.AST | None, str | None]
**Description**: Reads a file and parses it into an AST with strict size limits.



## Function: check_file_quality

**Parameters**: self, file_path
**Returns**: dict
**Description**: Check file for code quality issues (missing types, etc).



## Function: enable_llm

**Parameters**: self
**Returns**: bool
**Description**: LLM arbitration is always active when healing — not a separate flag.



## Function: dry_run

**Parameters**: self
**Returns**: bool
**Description**: Convenience alias — inverted heal for legacy call sites.



## Function: from_args

**Parameters**: cls, args
**Returns**: 'HealContext'
**Description**: Construct from parsed CLI args. Single construction point.

        Canonical flag semantics (--heal is the ONLY active-mode switch):
          --heal ON  => heal, auto_approve, enable_llm, enable_telemetry,
                        enable_meta_learning all True
          --heal OFF => all passive/scan-only

        Deprecated flags (kept for backward-compat, emit warnings):
          --dry-run        => same as omitting --heal
          --manual         => always autonomous now
          --interactive    => auto_approve is always True under --heal
          --apply-proposals => meta-learning always on under --heal
        



## Function: __init__

**Parameters**: self, enable_llm, state_mgr, enable_cda, execution_context, healing_memory_retriever, auto_approve


## Function: _calculate_semantic_similarity

**Parameters**: self, unknown, existing
**Returns**: float
**Description**: Calculate semantic similarity for unknown items against a candidate list.

        Uses BAAI/bge-m3 cosine similarity (GPU-accelerated on RTX 5090).
        Falls back to Jaccard word-overlap only on exception.
        



## Function: _get_bmg_cosine_similarity

**Returns**: object
**Description**: Lazy seam: load bmg_cosine_similarity from L2 healers without module-level import.



## Function: _get_bmg_embedding_agent_keys

**Returns**: frozenset
**Description**: Lazy seam: load BMG_EMBEDDING_AGENT_KEYS from L2 healing_tier_config.



## Function: _get_qwen_14b_routing_config

**Returns**: tuple
**Description**: Lazy seam: load Qwen 14B routing constants from L2 healing_tier_config.



## Function: _get_qwen_vllm_arbiter

**Description**: Lazy seam: return callable that invokes Qwen 14B via WSL vLLM subprocess.



## Function: _calculate_pattern_confidence

**Parameters**: self, violation_type
**Returns**: float
**Description**: Regex-based pattern matching for known violation types.



## Function: _compute_novelty_score

**Parameters**: self, failure_type, territory, confidence
**Returns**: int
**Description**: Compute the novelty score N (0-3) for RoutingInputs.

        Embeds the current failure signal text and compares against stored
        vectors to produce a true novelty score:
          N=0  max_similarity >= 0.85  (seen before)
          N=1  max_similarity >= 0.70  (similar)
          N=2  max_similarity >= 0.50  (somewhat novel)
          N=3  max_similarity <  0.50  (highly novel)

        Raises VectorSourceMismatchError if stored vectors and the current
        vector have incompatible dimensions.
        



## Function: _route_decision

**Parameters**: self, confidence, agent_name, territory, failure_type, retry_count, replay_mode, playbook_match, deterministic_coverage, provider_prohibited_gemini, provider_prohibited_qwen, adg_behavioral_score
**Returns**: 'RoutingDecision'
**Description**: Map healing context to a hardened SSOT RoutingDecision.



## Function: _classify_violation_type

**Parameters**: self, message
**Returns**: str
**Description**: Classify a violation message into a canonical violation type string.



## Function: _check_healing_budget

**Parameters**: self, agent_name, depth, max_depth
**Returns**: tuple[bool, str]
**Description**: Prevents infinite healing loops and budget exhaustion.



## Function: calculate_healing_confidence

**Parameters**: self, violations_count, violation_types, territory, historical_success_rate, agent_name, adg_behavioral_score
**Returns**: ConfidenceScore
**Description**: Calculates weighted confidence score.

        Uses GPU-accelerated BAAI/bge-m3 cosine similarity for pattern matching
        when agent_name is in BMG_EMBEDDING_AGENT_KEYS.

        adg_behavioral_score [0.0–1.0] from ADGBehavioralIndex:
          <0.4  script-like: +0.05 confidence boost (deterministic agents are easier to heal)
          >0.7  agent-like:  -0.05 confidence penalty (adaptive agents require more caution)
          0.5   unknown:     no adjustment
        



## Function: should_proceed_with_healing

**Parameters**: self, confidence, agent_name, territory, failure_type, retry_count, replay_mode, playbook_match, deterministic_coverage, provider_prohibited_gemini, provider_prohibited_qwen, adg_behavioral_score
**Returns**: tuple[bool, str]
**Description**: Determines if healing should proceed using the hardened SSOT routing algorithm.



## Function: _hitl_gate

**Parameters**: self, agent_name, confidence, tier
**Returns**: tuple[bool, str]
**Description**: 
        HITL terminal gate for medium/low confidence healing decisions.

        Prints a structured prompt showing the agent, confidence score, and
        reasoning, then reads Y/N/D from stdin. Non-interactive environments
        (no tty) default to DEFER (reject).

        Returns:
            (approved: bool, reason: str)
        



## Function: request_sovereignty_token

**Parameters**: self, agent_name, operation
**Returns**: bool
**Description**: 
        Request permission to perform a state-mutating operation.
        Enforces atomic locking and stack depth limits.
        



## Function: release_sovereignty_token

**Parameters**: self, agent_name, success
**Returns**: None
**Description**: Release the lock after operation completion.



## Function: __init__

**Parameters**: self, project_root, dry_run


## Function: run_checks

**Parameters**: self
**Returns**: tuple[bool, list[str]]


## Function: validate_agent_integrity

**Parameters**: self, agents
**Returns**: list[str]
**Description**: 
        [CONTRACT GUARD] Mandatory validation of all registered agents.
        Catches legacy signatures, broken mixins, and instantiation failures.
        



## Function: __init__

**Parameters**: self, active, max_blocked_prompts


## Function: __enter__

**Parameters**: self


## Function: __exit__

**Parameters**: self, exc_type, exc_val, exc_tb


## Function: _trap_input

**Parameters**: self, prompt


## Function: decorator

**Parameters**: func


## Function: __init__

**Parameters**: self, project_root, execution_context


## Function: start_mission

**Parameters**: self, mission_type, agents_order


## Function: update_agent

**Parameters**: self, agent_name, layer


## Function: skip_agent

**Parameters**: self, agent_name, reason
**Description**: Records agent as skipped — confidence gate or HITL rejected execution.



## Function: complete_agent

**Parameters**: self, agent_name, success, details
**Description**: 
        [HARDENED] Silent Aggregation.
        Records agent completion but suppresses intermediate JSON console dumps.
        



## Function: add_event

**Parameters**: self, event_type, message


## Function: finish_mission

**Parameters**: self, status


## Function: save

**Parameters**: self
**Description**: 
        [HARDENED] Atomic Write Pattern with Permission Lockdown.
        Writes to temp file, sets 600 permissions, then renames.
        Once L0 mutation prohibition fires, latches _persistence_disabled=True
        and becomes a no-op for the remainder of the run.
        



## Function: _emergency_cleanup

**Parameters**: self
**Description**: Ensure state is finalized even on unhandled exit.



## Function: update_meta_learning

**Parameters**: self, experience_data
**Description**: [INTEGRATION] Updates cognitive metrics for dashboard.



## Function: _bar

**Parameters**: n
**Returns**: str


## Function: _sec

**Parameters**: title
**Returns**: None


## Function: _row

**Parameters**: label, value
**Returns**: None


## Function: _lookup_outcome

**Parameters**: agent_key
**Returns**: str
**Description**: Resolve a decision agent key to its healing outcome.

        Decision keys are short roster names (e.g. 'location', 'reconciler').
        Healing-action keys are full class names (e.g. 'LocationHealerAgent').
        Resolution order:
          1. Exact match
          2. Case-insensitive exact match
          3. Any healing-action agent whose lower-case name starts with the key
          4. Any healing-action agent whose lower-case name contains the key
          5. Default → empty string (no outcome recorded → not SUCCESS)
        



## Function: _gate_detail

**Parameters**: criterion
**Returns**: list[str]
**Description**: Return 0-N inline detail lines for a gate criterion.



## Function: __init__

**Parameters**: self, state_mgr


## Function: exit_gracefully

**Parameters**: self, signum, frame
**Description**: Signal handler.



## Function: standard_heal

**Parameters**: func


## Function: _arbiter

**Parameters**: agent_name, violation_types, territory, score, gate
**Returns**: dict


## Function: wrapper



## Function: _json_serialise

**Parameters**: obj


## Function: _agg_json_serialise

**Parameters**: obj


## Function: __init__

**Parameters**: self, iterable, total, desc


## Function: __iter__

**Parameters**: self


## Function: __next__

**Parameters**: self


## Function: update

**Parameters**: self, n


## Function: set_description

**Parameters**: self, desc


## Function: __enter__

**Parameters**: self


## Function: __exit__

**Parameters**: self


## Function: _noop_guard

**Parameters**: _entry_point_id
**Description**: No-op: accepts an ID string and returns an identity decorator.



## Function: __init__

**Parameters**: self, legacy_agent


## Function: heal

**Parameters**: self, violation


## Function: _w6_hitl_archive_gate

**Parameters**: file_path, msg


## Function: _identity

**Parameters**: func


## Usage Examples

### Class Usage

```python
# Using ConfidenceScore
confidencescore = ConfidenceScore()
confidencescore.is_high_confidence()
confidencescore.is_medium_confidence()
```

```python
# Using FailureType
failuretype = FailureType()
```

```python
# Using RoutingTier
routingtier = RoutingTier()
```

### Function Usage

```python
# Using _get_sovereign_excluded_folders
result = _get_sovereign_excluded_folders()
```

```python
# Using _get_uwg
result = _get_uwg()
```

```python
# Using _get_heal_result_adapter
result = _get_heal_result_adapter()
```



---
**Generated**: 2026-03-26T09:39:03.081075
**Type**: api_reference
**Quality**: comprehensive
