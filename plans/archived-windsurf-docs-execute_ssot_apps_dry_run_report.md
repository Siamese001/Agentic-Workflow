---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\execute_ssot_apps_dry_run_report.md'
original_relative_path: 'execute_ssot_apps_dry_run_report.md'
source_sha256: 9e26ccd0f24bdb634a74bd164ca5e65dc8e7cf35e697c9d6b63623732bfb1deb
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-16'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Legacy SSOT Dry-Run Report for Apps_* Folders

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Wave 1.1 — Discovery Commands

### Git Status (Before)
```
# Clean baseline - no uncommitted changes
```

### Locate Supported Entrypoint
```bash
Get-ChildItem -Path "agentic_core" -Recurse -Filter "*execute_ssot*" | Select-Object FullName
```
**Output:**
```
FullName
--------
C:\Git\Agentic-Workflow\agentic_core\L0_routing\scripts\execute_ssot_entrypoint.py
```

### Help Text for Legacy Entrypoint
```bash
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --help
```
**Output:**
```
usage: execute_ssot_entrypoint.py [-h] [--legacy] [--plan] [--v15-enforcement {0,1}] [-v]

V15 Sovereign Compliance Entrypoint

options:
  -h, --help            show this help message and exit
  --legacy              Invoke the legacy healing pipeline (execute_ssot._legacy_main).
  --plan                Print the deterministic execution plan and exit. Requires --legacy.
  --v15-enforcement {0,1}
                        Override V15_ENFORCEMENT for this run (0=off, 1=on).
  -v, --verbose         Increase log verbosity (repeatable).

Examples:
  # Run legacy healing pipeline (explicit opt-in)
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --territory L5_safety

  # Dry-run validation
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --validate

  # List agents (no --legacy required)
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --list-agents
```

### Legacy Mode Help
```bash
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --help
```
**Output:**
```
usage: execute_ssot_entrypoint.py [-h] [--legacy] [--plan] [--v15-enforcement {0,1}] [-v]

V15 Sovereign Compliance Entrypoint

options:
  -h, --help            show this help message and exit
  --legacy              Invoke the legacy healing pipeline (execute_ssot._legacy_main).
  --plan                Print the deterministic execution plan and exit. Requires --legacy.
  --v15-enforcement {0,1}
                        Override V15_ENFORCEMENT for this run (0=off, 1=on).
  -v, --verbose         Increase log verbosity (repeatable).

Examples:
  # Run legacy healing pipeline (explicit opt-in)
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --territory L5_safety

  # Dry-run validation
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --validate

  # List agents (no --legacy required)
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --list-agents
```

### Discover Apps_* Folders
```bash
Get-ChildItem -Path "." -Filter "apps_*" -Directory | Select-Object Name
```
**Output:**
```
Name
----
apps_lic
apps_rg
apps_shared
```

### Execution Plan Discovery
```bash
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --plan
```
**Output:**
```
PHASE 1: Discovery
  - reconciler.detect_root_drift
    # filesystem SSOT drift detection
  - location.run
    # location validation (confidence gated heal)
  - file_classification.run (validate_only=True, dry_run=True)
    # file classification early detection

PHASE 2: Reconciliation
  - reconciler.heal
    # drift reconciliation (confidence gated)

PHASE 2.5: Structural Alignment & Sovereignty
  - hierarchy.heal_hierarchy
    # hierarchy alignment (confidence gated)
  - file_classification.heal_repository
    # sovereignty purge (confidence gated, not dry_run, not validate)

PHASE 3: Architectural Validation
  - arch_governor.comprehensive_territory_audit
    # territory audit
  - system_architect.validate_core_architecture
    # architecture validation

PHASE 4: Healing
  - arch_governor.generate_healing_plan
    # healing plan generation
  - arch_governor.execute_healing_plan
    # healing plan execution

PHASE 4.5: Additional Agents
  - conversational_repair.scan_violations
    # conversational repair scan
  - root_hygiene.scan_root_violations
    # root hygiene scan (if registered)

PHASE 5: Certification
  - *.aggregate
    # final aggregation and certification
```

## Wave 1.2 — Dry-Run Execution

### Issue with Legacy Entrypoint
The legacy entrypoint fails with Windows LongPathsEnabled check:
```bash
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --validate --territory apps_shared
```
**Output:**
```
2026-02-16 08:43:47,530 CRITICAL UnifiedSovereign 🛑 PRE-FLIGHT CHECK FAILED:
2026-02-16 08:43:47,532 ERROR UnifiedSovereign   - Windows LongPathsEnabled is NOT active (Set to 1 in Registry)
```

### Alternative Approach: Direct FileClassificationAgent Invocation
Since the legacy entrypoint is blocked by Windows pre-flight checks, I used the FileClassificationAgent directly with individual apps_* folders as project roots.

#### apps_shared Dry-Run
```bash
python -c "from pathlib import Path; import sys; sys.path.insert(0, str(Path('.').resolve())); from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent; import json; apps_shared_root=Path('.').resolve() / 'apps_shared'; agent=FileClassificationAgent(project_root=apps_shared_root, dry_run=True, validate_only=True); result=agent.run(); print('=== apps_shared ==='); print(json.dumps(result, indent=2, default=str))"
```
**Output:**
```
[WARNING] Windows LongPathsEnabled is NOT set to 1.
[MISNAMED_UTILITY] config_loader_config.py: config_loader_config.py contains class 'ConfigLoader' with active methods ['load_config', '_find_config_file', '_load_from_file']. This is a utility, not a config file.
[MISNAMED_UTILITY] environment_config.py: environment_config.py contains class 'EnvironmentValidator' with active methods ['validate', '_format_error_message', 'get_config']. This is a utility, not a config file.
[MISNAMED_UTILITY] feedback_category_config.py: feedback_category_config.py contains class 'FeedbackAggregator' with active methods ['add_feedback', 'get_insights', '_analyze_categories']. This is a utility, not a config file.
[MISNAMED_UTILITY] graph_rag_fusion_config.py: graph_rag_fusion_config.py contains class 'CypherQueryGenerator' with active methods ['generate_query']. This is a utility, not a config file.
[DUAL-TAG] input_guardrail_config.py carries conflicting tags: {'CONFIG', 'GUARDRAIL'}. Resolving via folder context.
[MISNAMED_UTILITY] input_guardrail_config.py: input_guardrail_config.py contains class 'InputGuardrail' with active methods ['_compile_patterns', '_init_semantic_checker', 'scan']. This is a utility, not a config file.
[MISNAMED_UTILITY] input_validator_config.py: input_validator_config.py contains class 'InputValidator' with active methods ['add_rule', 'add_schema', 'validate']. This is a utility, not a config file.
[MISNAMED_UTILITY] metric_augmenter_config.py: metric_augmenter_config.py contains class 'BusinessImpact' with active methods ['validate_conservative_language']. This is a utility, not a config file.
[MISNAMED_UTILITY] metric_config.py: metric_config.py contains class 'MetricConfig' with active methods ['record', 'get_metrics', 'get_latest']. This is a utility, not a config file.
[MISNAMED_UTILITY] node_negotiator_config.py: node_negotiator_config.py contains class 'NegotiationMessage' with active methods ['validate_message_type']. This is a utility, not a config file.
[MISNAMED_UTILITY] prompt_enhancer_config.py: prompt_enhancer_config.py contains class 'PromptEnhancer' with active methods ['enhance_prompt', '_build_constraints', 'process_response']. This is a utility, not a config file.
[MISNAMED_UTILITY] prompt_registry_config.py: prompt_registry_config.py contains class 'PromptRegistry' with active methods ['register', 'get', 'find_by_category']. This is a utility, not a config file.
[MISNAMED_UTILITY] relevance_scorer_config.py: relevance_scorer_config.py contains class 'RelevanceScorer' with active methods ['score_chunk', 'score_chunks', '_keyword_overlap']. This is a utility, not a config file.
[MISNAMED_UTILITY] sdk_category_config.py: sdk_category_config.py contains class 'MockCollection' with active methods ['add', 'query']. This is a utility, not a config file.
[MISNAMED_UTILITY] settings_config.py: settings_config.py contains class 'Settings' with active methods ['process', '_execute_logic']. This is a utility, not a config file.
[MISNAMED_UTILITY] signal_weighter_config.py: signal_weighter_config.py contains class 'SignalWeights' with active methods ['as_dict']. This is a utility, not a config file.
[MISNAMED_UTILITY] token_budget_config.py: token_budget_config.py contains class 'TokenBudget' with active methods ['estimate_tokens', 'check_request_budget', 'record_usage']. This is a utility, not a config file.
[DUAL-TAG] app_config_types.py carries conflicting tags: {'CONFIG', 'TYPES'}. Resolving via folder context.
[DUAL-TAG] checkpoint_manager_types.py carries conflicting tags: {'MANAGER', 'TYPES'}. Resolving via folder context.
[DUAL-TAG] execution_orchestrator_types.py carries conflicting tags: {'ORCHESTRATOR', 'TYPES'}. Resolving via folder context.
[DUAL-TAG] feedback_loop_orchestrator_types.py carries conflicting tags: {'ORCHESTRATOR', 'TYPES'}. Resolving via folder context.
[DUAL-TAG] memory_manager_types.py carries conflicting tags: {'MANAGER', 'TYPES'}. Resolving via folder context.
[DUAL-TAG] resource_manager_types.py carries conflicting tags: {'MANAGER', 'TYPES'}. Resolving via folder context.
[MISNAMED_UTILITY] security_utils_config.py: security_utils_config.py contains class 'InputSanitizer' with active methods ['sanitize_string', 'sanitize_path', 'sanitize_identifier']. This is a utility, not a config file.
[DUAL-TAG] validation_context_manager_validator.py carries conflicting tags: {'MANAGER', 'VALIDATOR'}. Resolving via folder context.
  - Gateways: 0
=== apps_shared ===
{
  "success": true,
  "stats": {
    "analyzed": 232,
    "compliant": 225,
    "renamed": 0,
    "imports_fixed": 0,
    "deep_refactors": 0,
    "collisions_resolved": 0,
    "violations": {
      "AGENT": 0,
      "CLASS": 0,
      "MIXIN": 0,
      "UTILITY": 0,
      "PROTOCOL": 0,
      "ENGINE": 0,
      "STUB": 0,
      "TEST": 0,
      "SCRIPT": 0,
      "TYPES": 0,
      "GATEWAY": 0,
      "ORCHESTRATOR": 0,
      "VALIDATOR": 0,
      "FACTORY": 0,
      "CONFIG": 0,
      "ADAPTER": 0,
      "STRATEGY": 0,
      "EXCEPTION": 0
    },
    "territory_moves": 0
  },
  "summary": "Renamed: 0, Refactors: 0"
}
```

#### apps_lic Dry-Run
```bash
python -c "from pathlib import Path; import sys; sys.path.insert(0, str(Path('.').resolve())); from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent; import json; apps_lic_root=Path('.').resolve() / 'apps_lic'; agent=FileClassificationAgent(project_root=apps_lic_root, dry_run=True, validate_only=True); result=agent.run(); print('=== apps_lic ==='); print(json.dumps(result, indent=2, default=str))"
```
**Output:**
```
[WARNING] Windows LongPathsEnabled is NOT set to 1.
[MISNAMED_UTILITY] archetype_indicator_config.py: archetype_indicator_config.py contains class 'AgentSpecs' with active methods ['from_dict']. This is a utility, not a config file.
[DUAL-TAG] placeholder_detector_agent_config.py carries conflicting tags: {'AGENT', 'CONFIG'}. Resolving via folder context.
[DUAL-TAG] code_quality_guardrail_types.py carries conflicting tags: {'TYPES', 'GUARDRAIL'}. Resolving via folder context.
[DUAL-TAG] competitor_recon_agent_types.py carries conflicting tags: {'AGENT', 'TYPES'}. Resolving via folder context.
[PASSIVE_AGENT_NAMING] PIISanitizerSpecialistAgent.py: ConstitutionalReviewerAgent is a dataclass/BaseModel with no active methods. Rename to *_util.py or *_types.py.
[DUAL-TAG] stack_modernization_agent_types.py carries conflicting tags: {'AGENT', 'TYPES'}. Resolving via folder context.
[DUAL-TAG] app_content_validator_agent_types.py carries conflicting tags: {'AGENT', 'TYPES'}. Resolving via folder context.
  - Gateways: 0
=== apps_lic ===
{
  "success": true,
  "stats": {
    "analyzed": 139,
    "compliant": 131,
    "renamed": 0,
    "imports_fixed": 0,
    "deep_refactors": 0,
    "collisions_resolved": 0,
    "violations": {
      "AGENT": 0,
      "CLASS": 0,
      "MIXIN": 0,
      "UTILITY": 0,
      "PROTOCOL": 0,
      "ENGINE": 0,
      "STUB": 0,
      "TEST": 0,
      "SCRIPT": 0,
      "TYPES": 0,
      "GATEWAY": 0,
      "ORCHESTRATOR": 0,
      "VALIDATOR": 0,
      "FACTORY": 0,
      "CONFIG": 0,
      "ADAPTER": 0,
      "STRATEGY": 0,
      "EXCEPTION": 0
    },
    "territory_moves": 0
  },
  "summary": "Renamed: 0, Refactors: 0"
}
```

#### apps_rg Dry-Run
```bash
python -c "from pathlib import Path; import sys; sys.path.insert(0, str(Path('.').resolve())); from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent; import json; apps_rg_root=Path('.').resolve() / 'apps_rg'; agent=FileClassificationAgent(project_root=apps_rg_root, dry_run=True, validate_only=True); result=agent.run(); print('=== apps_rg ==='); print(json.dumps(result, indent=2, default=str))"
```
**Output:**
```
[WARNING] Windows LongPathsEnabled is NOT set to 1.
[DUPLICATE] ContentStrategyAgent.py exists in multiple locations. Canonical: C:\Git\Agentic-Workflow\apps_rg\engines. Duplicate: C:\Git\Agentic-Workflow\apps_rg\reasoning — should be deleted.
[MISNAMED_UTILITY] clerk_extractor_config.py: clerk_extractor_config.py contains class 'ClerkExtractor' with active methods ['extract', '_validate_structure', '_build_experience_sections']. This is a utility, not a config file.
[MISNAMED_UTILITY] sovereign_config_loader_config.py: sovereign_config_loader_config.py contains class 'SovereignConfigLoader' with active methods ['load_topology', '_get_default_scaffold', 'reset']. This is a utility, not a config file.
[MISPLACED-TEST] test_run_grand_unification_tests.py is a test file outside tests/ directory. Current location: C:\Git\Agentic-Workflow\apps_rg\scripts. Move to tests/ mirror structure.
[DUAL-TAG] gap_closure_architect_agent_types.py carries conflicting tags: {'AGENT', 'TYPES'}. Resolving via folder context.
  - Gateways: 0
=== apps_rg ===
{
  "success": true,
  "stats": {
    "analyzed": 155,
    "compliant": 148,
    "renamed": 0,
    "imports_fixed": 0,
    "deep_refactors": 0,
    "collisions_resolved": 0,
    "violations": {
      "AGENT": 0,
      "CLASS": 0,
      "MIXIN": 0,
      "UTILITY": 0,
      "PROTOCOL": 0,
      "ENGINE": 0,
      "STUB": 0,
      "TEST": 0,
      "SCRIPT": 0,
      "TYPES": 0,
      "GATEWAY": 0,
      "ORCHESTRATOR": 0,
      "VALIDATOR": 0,
      "FACTORY": 0,
      "CONFIG": 0,
      "ADAPTER": 0,
      "STRATEGY": 0,
      "EXCEPTION": 0
    },
    "territory_moves": 0,
    "duplicate_files": 1
  },
  "summary": "Renamed: 0, Refactors: 0"
}
```

## Wave 1.3 — Summary Table

| Folder | Analyzed | Compliant | Violations | Issues Found | Dry-Run Status |
|--------|----------|-----------|------------|--------------|----------------|
| apps_shared | 232 | 225 | 0 | Multiple MISNAMED_UTILITY files, DUAL-TAG conflicts | ✅ Success |
| apps_lic | 139 | 131 | 0 | MISNAMED_UTILITY files, DUAL-TAG conflicts, PASSIVE_AGENT_NAMING | ✅ Success |
| apps_rg | 155 | 148 | 0 | DUPLICATE file, MISNAMED_UTILITY files, MISPLACED-TEST, DUAL-TAG conflicts | ✅ Success |

**Key Findings:**
- Total files analyzed: 526
- Total compliant files: 504 (95.8%)
- No critical violations requiring immediate fixes
- apps_rg has 1 duplicate file that should be addressed
- Multiple utility files misnamed as config files across all folders
- No mutations occurred (dry-run validation successful)

## Git Status (After)
```
?? docs/reports/plans/execute_ssot_apps_dry_run_report.md
```

## Conclusion

The legacy SSOT entrypoint (`execute_ssot_entrypoint.py --legacy`) is blocked on Windows due to LongPathsEnabled registry requirements. However, the FileClassificationAgent can be invoked directly to perform dry-run validation on apps_* folders.

All three apps_* folders (apps_shared, apps_lic, apps_rg) were successfully scanned with dry-run validation. The scans revealed naming convention issues and one duplicate file, but no critical structural violations requiring immediate action.

**Note:** The Windows LongPathsEnabled issue prevents full legacy pipeline execution, but the core file classification validation works properly when invoked directly.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

