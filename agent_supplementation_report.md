# ULTRA CAPABILITY SUPPLEMENTATION ANALYSIS REPORT

**Generated:** 2025-12-30T15:03:50.291992

---

## Executive Summary

| Metric | Count |
|--------|-------|
| **Live Agents** | 24 |
| **Dead Agents (to mine)** | 35 |
| **Suspect Agents** | 7 |
| **Unique Capabilities in Dead** | 0 |
| **Underrepresented Capabilities** | 4 |

---

## Live Agent Capability Coverage

| Capability | Count in Live Agents |
|------------|---------------------|
| validation | 12 |
| detection | 11 |
| filesystem_introspection | 10 |
| redis_integration | 8 |
| healing | 7 |
| dead_code_analysis | 3 |
| mapping | 3 |
| git_operations | 1 |
| git_integration | 1 |
| pruning | 1 |
| monitoring | 1 |

---

## Unique Capabilities in DEAD Agents

✅ **No completely unique capabilities** — all logic covered by LIVE agents.

---

## Underrepresented Capabilities

Capabilities that appear in fewer than 2 LIVE agents:

| Capability | Live Count | Potential Donors |
|------------|------------|------------------|
| git_integration | 1 | — |
| git_operations | 1 | `OrganicTerritorySeederAgent` |
| monitoring | 1 | — |
| pruning | 1 | `DeadCodePrunerAgent`, `FilesystemAgent`, `RedTeamingSovereignRedTeamAgent` |

---

## Dead Agent Capability Detail

### `AgentRegistryValidatorAgent`

**File:** `agentic_core\L3_orchestration\workflow_engines\AgentRegistryValidatorAgent.py`

**Semantic Tags:** validation
**Patterns:** filesystem_introspection
**Unique Methods:** `_generate_search_paths`, `run_validation`, `validate_agent_exists`, `validate_registry`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `validate_agent_exists` | 37 | Unique method signature |
| `validate_agent_exists` | 37 | Advanced filesystem checks |
| `validate_registry` | 60 | Unique method signature |
| `validate_registry` | 60 | Advanced filesystem checks |
| `_generate_search_paths` | 100 | Unique method signature |
| `run_validation` | 131 | Unique method signature |

### `AuditTrailsSovereignForensicsAgent`

**File:** `agentic_core\L4_state\validation_context\AuditTrailsSovereignForensicsAgent.py`

**Patterns:** redis_integration
**Unique Methods:** `analyze_drift`, `analyze_drift_patterns`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `__init__` | 27 | Redis state access |
| `analyze_drift_patterns` | 31 | Unique method signature |
| `analyze_drift_patterns` | 31 | Redis state access |
| `analyze_drift` | 46 | Unique method signature |
| `analyze_drift` | 46 | Redis state access |

### `BaseAgentsMockCanonAgent`

**File:** `agentic_core\L2_execution\tool_registry\BaseAgentsMockCanonAgent.py`

**Semantic Tags:** validation
**Unique Methods:** `__repr__`, `add_capability`, `get_capabilities`, `set_state_valid`, `validate_state`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `get_capabilities` | 47 | Unique method signature |
| `validate_state` | 56 | Unique method signature |
| `set_state_valid` | 65 | Unique method signature |
| `add_capability` | 74 | Unique method signature |
| `__repr__` | 84 | Unique method signature |

### `BootstrapAgent`

**File:** `agentic_core\L0_maintenance\scripts\BootstrapAgent.py`

**Patterns:** filesystem_introspection, redis_integration
**Unique Methods:** `run_bootstrap`, `verify_neural_link`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `verify_neural_link` | 41 | Unique method signature |
| `verify_neural_link` | 41 | Advanced filesystem checks |
| `verify_neural_link` | 41 | Redis state access |
| `run_bootstrap` | 93 | Unique method signature |
| `run_bootstrap` | 93 | Redis state access |

### `CacheRedisSovereignAgent`

**File:** `agentic_core\L4_state\validation_context\CacheRedisSovereignAgent.py`

**Patterns:** redis_integration
**Unique Methods:** `delete`, `exists`, `get`, `get_client`, `set`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `get_client` | 14 | Unique method signature |
| `get_client` | 14 | Redis state access |
| `get` | 21 | Unique method signature |
| `set` | 25 | Unique method signature |
| `delete` | 29 | Unique method signature |
| `exists` | 33 | Unique method signature |

### `CodeDeduplicationAgent`

**File:** `agentic_core\L2_execution\tool_registry\CodeDeduplicationAgent.py`

**Semantic Tags:** detection
**Patterns:** filesystem_introspection
**Unique Methods:** `_create_shared_utility`, `_extract_functions_classes`, `_hash_block`, `_normalize_code`, `auto_extract_duplicates`, `scan_for_duplicates`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `_normalize_code` | 32 | Unique method signature |
| `_hash_block` | 45 | Unique method signature |
| `_extract_functions_classes` | 49 | Unique method signature |
| `scan_for_duplicates` | 66 | Unique method signature |
| `scan_for_duplicates` | 66 | Advanced filesystem checks |
| `_create_shared_utility` | 86 | Unique method signature |
| `auto_extract_duplicates` | 100 | Unique method signature |

### `DeadCodeDetectorAgent`

**File:** `agentic_core\utils\core_extensions\DeadCodeDetectorAgent.py`

**Semantic Tags:** detection
**Patterns:** dead_code_analysis, filesystem_introspection
**Unique Methods:** `analyze_file`, `generate_report`, `scan_directory`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `__init__` | 115 | Dead/unused code detection |
| `analyze_file` | 119 | Unique method signature |
| `analyze_file` | 119 | Dead/unused code detection |
| `scan_directory` | 162 | Unique method signature |
| `scan_directory` | 162 | Dead/unused code detection |
| `scan_directory` | 162 | Advanced filesystem checks |
| `generate_report` | 186 | Unique method signature |
| `generate_report` | 186 | Dead/unused code detection |

### `DeadCodePrunerAgent`

**File:** `agentic_core\L3_orchestration\workflow_engines\DeadCodePrunerAgent.py`

**Semantic Tags:** detection, pruning
**Patterns:** dead_code_analysis
**Unique Methods:** `find_dead_code`, `prune`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `find_dead_code` | 16 | Unique method signature |
| `find_dead_code` | 16 | Dead/unused code detection |
| `prune` | 20 | Unique method signature |
| `prune` | 20 | Dead/unused code detection |

### `DebuggerAgent`

**File:** `agentic_core\L2_execution\tool_registry\DebuggerAgent.py`

**Semantic Tags:** detection, healing, validation
**Unique Methods:** `_analyze_error`, `_check_circuit_breaker`, `_debug_specific_trace`, `_find_recent_errors`, `_generate_summary`, `_implement_fix`, `_llm_analyze_error`, `_propose_fix`, `_record_verification`, `_verify_fix`, `run_debugging_cycle`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `run_debugging_cycle` | 29 | Unique method signature |
| `_debug_specific_trace` | 68 | Unique method signature |
| `_find_recent_errors` | 78 | Unique method signature |
| `_analyze_error` | 102 | Unique method signature |
| `_llm_analyze_error` | 115 | Unique method signature |
| `_propose_fix` | 125 | Unique method signature |
| `_implement_fix` | 142 | Unique method signature |
| `_verify_fix` | 163 | Unique method signature |
| `_record_verification` | 186 | Unique method signature |
| `_check_circuit_breaker` | 193 | Unique method signature |
| `_generate_summary` | 209 | Unique method signature |

### `FilesystemAgent`

**File:** `agentic_core\L5_safety\validators\FilesystemAgent.py`

**Semantic Tags:** pruning
**Patterns:** filesystem_introspection
**Unique Methods:** `_backup_file`, `_determine_archive_subpath`, `cleanup_violations`, `run_with_cleanup`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `__init__` | 41 | Advanced filesystem checks |
| `_determine_archive_subpath` | 92 | Unique method signature |
| `_determine_archive_subpath` | 92 | Advanced filesystem checks |
| `_backup_file` | 197 | Unique method signature |
| `cleanup_violations` | 209 | Unique method signature |
| `cleanup_violations` | 209 | Advanced filesystem checks |
| `run_with_cleanup` | 272 | Unique method signature |

### `GeminiPolicyEnforcerAgent`

**File:** `agentic_core\L5_safety\guardrails\GeminiPolicyEnforcerAgent.py`

**Semantic Tags:** validation
**Unique Methods:** `enforce_policy`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `enforce_policy` | 15 | Unique method signature |

### `GlobalComplianceAggregatorAgent`

**File:** `agentic_core\utils\core_extensions\GlobalComplianceAggregatorAgent.py`

**Unique Methods:** `aggregate_results`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `aggregate_results` | 15 | Unique method signature |

### `GravityEnforcerAgent`

**File:** `agentic_core\L5_safety\guardrails\GravityEnforcerAgent.py`

**Semantic Tags:** healing
**Patterns:** filesystem_introspection
**Unique Methods:** `_has_gravity_violations`, `_heal_file`, `get_summary`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `execute` | 30 | Advanced filesystem checks |
| `_has_gravity_violations` | 60 | Unique method signature |
| `_heal_file` | 69 | Unique method signature |
| `get_summary` | 100 | Unique method signature |

### `K25ResearchAgent`

**File:** `agentic_core\L1_cognition\thought_engine\K25ResearchAgent.py`

**Patterns:** filesystem_introspection
**Unique Methods:** `_assemble_research_output`, `_execute_hop_1_financial_strategic`, `_execute_hop_2_technical_product`, `_execute_hop_3_organizational_leadership`, `_get_default_prompt`, `_load_prompt_template`, `execute_research`, `generate_research_prompt`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `_load_prompt_template` | 49 | Unique method signature |
| `_load_prompt_template` | 49 | Advanced filesystem checks |
| `_get_default_prompt` | 55 | Unique method signature |
| `execute_research` | 58 | Unique method signature |
| `_execute_hop_1_financial_strategic` | 79 | Unique method signature |
| `_execute_hop_2_technical_product` | 84 | Unique method signature |
| `_execute_hop_3_organizational_leadership` | 89 | Unique method signature |
| `_assemble_research_output` | 94 | Unique method signature |
| `generate_research_prompt` | 104 | Unique method signature |

### `KeyCoverageAuditorAgent`

**File:** `agentic_core\L4_state\validation_context\KeyCoverageAuditorAgent.py`

**Unique Methods:** `audit_coverage`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `audit_coverage` | 15 | Unique method signature |

### `KeyMappingAgent`

**File:** `agentic_core\L5_safety\validators\KeyMappingAgent.py`

**Unique Methods:** `get_applicable_keys_for_file`, `get_behavioral_keys`, `get_territorial_keys`, `run_on_files`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `get_applicable_keys_for_file` | 35 | Unique method signature |
| `get_territorial_keys` | 78 | Unique method signature |
| `get_behavioral_keys` | 82 | Unique method signature |
| `run_on_files` | 90 | Unique method signature |

### `LayerCapabilityAgent`

**File:** `agentic_core\L5_safety\validators\LayerCapabilityAgent.py`

**Unique Methods:** `analyze_file_ast`, `determine_primary_layer`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `analyze_file_ast` | 58 | Unique method signature |
| `determine_primary_layer` | 100 | Unique method signature |

### `MetaOrchestratorAgent`

**File:** `agentic_core\L3_orchestration\workflow_engines\MetaOrchestratorAgent.py`


### `MissionResumeAgent`

**File:** `agentic_core\L3_orchestration\workflow_engines\MissionResumeAgent.py`

**Patterns:** redis_integration
**Unique Methods:** `get_resume_point`, `resume_mission`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `__init__` | 20 | Redis state access |
| `get_resume_point` | 24 | Unique method signature |
| `resume_mission` | 29 | Unique method signature |

### `NamingLawHealerAgent`

**File:** `agentic_core\utils\core_extensions\NamingLawHealerAgent.py`

**Semantic Tags:** detection
**Patterns:** filesystem_introspection
**Unique Methods:** `_apply_rename`, `_detect_low_signal`, `_determine_new_name`, `_execute_per_file`, `_generate_suggestions`, `_is_protected_file`, `_rank_suggestions`, `_think`, `get_summary`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `execute` | 28 | Advanced filesystem checks |
| `_execute_per_file` | 61 | Unique method signature |
| `_execute_per_file` | 61 | Advanced filesystem checks |
| `_is_protected_file` | 77 | Unique method signature |
| `_determine_new_name` | 88 | Unique method signature |
| `_think` | 110 | Unique method signature |
| `_detect_low_signal` | 117 | Unique method signature |
| `_generate_suggestions` | 127 | Unique method signature |
| `_rank_suggestions` | 139 | Unique method signature |
| `_apply_rename` | 151 | Unique method signature |
| `get_summary` | 155 | Unique method signature |

### `OrganicTerritorySeederAgent`

**File:** `agentic_core\L0_maintenance\scripts\OrganicTerritorySeederAgent.py`

**Patterns:** filesystem_introspection, git_operations

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `execute` | 32 | Git repository interaction |
| `execute` | 32 | Advanced filesystem checks |

### `PolicyNeuralAutoImmuneAgent`

**File:** `agentic_core\L5_safety\guardrails\PolicyNeuralAutoImmuneAgent.py`

**Semantic Tags:** detection
**Patterns:** redis_integration
**Unique Methods:** `detect_breaches`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `__init__` | 22 | Redis state access |
| `detect_breaches` | 26 | Unique method signature |

### `PreCommitGuardianAgent`

**File:** `agentic_core\L5_safety\guardrails\PreCommitGuardianAgent.py`

**Semantic Tags:** validation
**Unique Methods:** `validate_pre_commit`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `validate_pre_commit` | 15 | Unique method signature |

### `PromptValidationAgent`

**File:** `agentic_core\L5_safety\validators\PromptValidationAgent.py`

**Patterns:** filesystem_introspection

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `execute` | 23 | Advanced filesystem checks |

### `RecursiveAgent`

**File:** `agentic_core\L3_orchestration\workflow_engines\RecursiveAgent.py`


### `RecursiveSpanHealerAgent`

**File:** `agentic_core\L3_orchestration\workflow_engines\RecursiveSpanHealerAgent.py`

**Semantic Tags:** detection, healing
**Unique Methods:** `detect_span_violations`, `run_healing`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `detect_span_violations` | 20 | Unique method signature |
| `run_healing` | 44 | Unique method signature |

### `RedTeamingSovereignRedTeamAgent`

**File:** `agentic_core\L5_safety\guardrails\RedTeamingSovereignRedTeamAgent.py`

**Semantic Tags:** pruning
**Patterns:** redis_integration
**Unique Methods:** `_inject_depth_violation`, `_inject_gravity_violation`, `cleanup`, `run_tests`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `__init__` | 23 | Redis state access |
| `_inject_depth_violation` | 35 | Unique method signature |
| `_inject_gravity_violation` | 41 | Unique method signature |
| `run_tests` | 48 | Unique method signature |
| `run_tests` | 48 | Redis state access |
| `cleanup` | 69 | Unique method signature |

### `RuntimeSharedCulturalDecoderAgent`

**File:** `agentic_core\L0_maintenance\scripts\RuntimeSharedCulturalDecoderAgent.py`

**Unique Methods:** `decode`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `decode` | 14 | Unique method signature |

### `RuntimeSharedK3MessageBodyAgent`

**File:** `agentic_core\L0_maintenance\scripts\RuntimeSharedK3MessageBodyAgent.py`

**Unique Methods:** `generate_body`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `generate_body` | 47 | Unique method signature |

### `RuntimeSharedK7AssemblyAgent`

**File:** `agentic_core\L0_maintenance\scripts\RuntimeSharedK7AssemblyAgent.py`

**Unique Methods:** `assemble`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `assemble` | 45 | Unique method signature |

### `ScriptsConsolidatorAgent`

**File:** `agentic_core\L3_orchestration\workflow_engines\ScriptsConsolidatorAgent.py`

**Semantic Tags:** detection
**Unique Methods:** `consolidate`, `find_scattered_scripts`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `find_scattered_scripts` | 16 | Unique method signature |
| `consolidate` | 20 | Unique method signature |

### `SemanticTerritoryMapperAgent`

**File:** `agentic_core\L3_orchestration\workflow_engines\SemanticTerritoryMapperAgent.py`

**Semantic Tags:** mapping
**Patterns:** redis_integration
**Unique Methods:** `_seed_territory_examples`, `analyze_territory_coverage`, `get_embedding`, `map_file_to_territory`, `suggest_territory_move`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `__init__` | 22 | Redis state access |
| `_seed_territory_examples` | 30 | Unique method signature |
| `get_embedding` | 42 | Unique method signature |
| `get_embedding` | 42 | Redis state access |
| `map_file_to_territory` | 55 | Unique method signature |
| `suggest_territory_move` | 81 | Unique method signature |
| `analyze_territory_coverage` | 96 | Unique method signature |

### `SovereignAlertingAgent`

**File:** `agentic_core\L5_safety\guardrails\SovereignAlertingAgent.py`

**Patterns:** redis_integration
**Unique Methods:** `trigger_alert`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `__init__` | 22 | Redis state access |
| `trigger_alert` | 27 | Unique method signature |
| `trigger_alert` | 27 | Redis state access |

### `SovereignWatchdogAgent`

**File:** `agentic_core\L0_maintenance\scripts\SovereignWatchdogAgent.py`


### `TestGeneratorAgent`

**File:** `agentic_core\L2_execution\tool_registry\TestGeneratorAgent.py`

**Patterns:** filesystem_introspection, redis_integration
**Unique Methods:** `_scaffold_unit_test`, `get_validation_keys`

**Valuable Methods:**

| Method | Line | Description |
|--------|------|-------------|
| `get_validation_keys` | 26 | Unique method signature |
| `_scaffold_unit_test` | 51 | Unique method signature |
| `_scaffold_unit_test` | 51 | Advanced filesystem checks |
| `_scaffold_unit_test` | 51 | Redis state access |

---

## Recommended Supplementation Merges

✅ **No high-confidence supplementation opportunities detected.**

The LIVE agents already cover all semantic capabilities found in DEAD agents.

---

## Next Steps

1. Review underrepresented capabilities for potential consolidation
2. For each recommended merge:
   - Open source and target files side-by-side
   - Copy valuable methods with full context
   - Update docstrings and add tests
   - Delete original DEAD file after verification
3. Re-run `agent_discovery_audit.py` to verify changes

---

*Report generated by `agent_capability_supplement.py`*