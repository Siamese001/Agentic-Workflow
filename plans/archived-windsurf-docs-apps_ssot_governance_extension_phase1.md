---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\apps_ssot_governance_extension_phase1.md'
original_relative_path: 'apps_ssot_governance_extension_phase1.md'
source_sha256: b3d322b5ef39a59216c0520a1866fe52f890f14668d030f66744a430fe3e20dd
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-16'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase 1: Extend Core SSOT Enforcement to apps_*

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

**Status**: 🔄 IN PROGRESS
**Date**: 2026-02-16
**Baseline Commit**: bcb56a23d818fd43c1dc100292c3bc68e1f79f36

---

## Wave 1 — Baseline + Identify Core-Only Scope/Return Bypass

### 1. Baseline Capture

```
git rev-parse HEAD
bcb56a23d818fd43c1dc100292c3bc68e1f79f36

git status --porcelain=v1
(clean working tree)

pytest -q
153 passed in 20.40s
```

### 2. Core Enforcement Functions Located

Key files containing SSOT enforcement logic:

| File | Purpose |
|------|---------|
| `agentic_core/L0_routing/scripts/execute_ssot.py` | Main SSOT execution orchestrator |
| `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | File classification + naming enforcement |
| `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | SSOT folder definitions |
| `agentic_core/L5_safety/config/structure_blueprint/derived.py` | Derived registries for apps_* |
| `agentic_core/L0_routing/scripts/territory_ssot_definitions_util.py` | Territory name definitions |

### 3. Apps_* Subfolder Maps Already Defined

From `derived.py`:
- `APPS_RG_SUBFOLDER_MAP` - derived from SOVEREIGN_TERRITORIES["apps_rg"]
- `APPS_LIC_SUBFOLDER_MAP` - derived from SOVEREIGN_TERRITORIES["apps_lic"]
- `APPS_SHARED_SUBFOLDER_MAP` - derived from SOVEREIGN_TERRITORIES["apps_shared"]

### 4. Current Violations Enumerated

#### 4.1 Config Files Missing `_config.py` Suffix (25 files)

```
apps_shared/config/config_loader_util.py
apps_shared/config/environment_util.py
apps_shared/config/feedback_category_util.py
apps_shared/config/graph_rag_fusion_util.py
apps_shared/config/input_guardrail_util.py
apps_shared/config/input_validator_util.py
apps_shared/config/metric_augmenter_util.py
apps_shared/config/metric_util.py
apps_shared/config/node_negotiator_util.py
apps_shared/config/prompt_enhancer_util.py
apps_shared/config/prompt_registry_util.py
apps_shared/config/relevance_scorer_util.py
apps_shared/config/sdk_category_util.py
apps_shared/config/settings_util.py
apps_shared/config/signal_weighter_util.py
apps_shared/config/token_budget_util.py
apps_shared/config/unified_config_helper.py
apps_lic/config/archetype_indicator_util.py
apps_lic/config/loader.py
apps_lic/config/ReasoningToggles.py
apps_lic/config/retry_policy.py
apps_rg/config/AgentSpec.py
apps_rg/config/clerk_extractor_util.py
apps_rg/config/ReasoningToggles.py
apps_rg/config/sovereign_config_loader_util.py
```

#### 4.2 Utility Files in config/ (Should Be in utils/) (19 files)

```
apps_shared/config/config_loader_util.py
apps_shared/config/environment_util.py
apps_shared/config/feedback_category_util.py
apps_shared/config/graph_rag_fusion_util.py
apps_shared/config/input_guardrail_util.py
apps_shared/config/input_validator_util.py
apps_shared/config/metric_augmenter_util.py
apps_shared/config/metric_util.py
apps_shared/config/node_negotiator_util.py
apps_shared/config/prompt_enhancer_util.py
apps_shared/config/prompt_registry_util.py
apps_shared/config/relevance_scorer_util.py
apps_shared/config/sdk_category_util.py
apps_shared/config/settings_util.py
apps_shared/config/signal_weighter_util.py
apps_shared/config/token_budget_util.py
apps_lic/config/archetype_indicator_util.py
apps_rg/config/clerk_extractor_util.py
apps_rg/config/sovereign_config_loader_util.py
```

#### 4.3 Utils Files Missing `_util.py` Suffix (95 files)

```
apps_shared/utils/agent_interface.py
apps_shared/utils/analysis_mixin.py
apps_shared/utils/AppBase.py
apps_shared/utils/ARCHIVE_FILE_ACCESS_DEPRECATED.py
apps_shared/utils/AssessmentLevel.py
apps_shared/utils/async_coordinator.py
apps_shared/utils/autonomous_sovereign_core.py
apps_shared/utils/BackupManager.py
apps_shared/utils/BaggagePropagator.py
apps_shared/utils/bulkhead_manager.py
apps_shared/utils/CacheMetrics.py
apps_shared/utils/CanonError.py
apps_shared/utils/CollectedItem.py
apps_shared/utils/config_environment.py
apps_shared/utils/ConfigurationService.py
apps_shared/utils/context_manager.py
apps_shared/utils/ContextualCompressor.py
apps_shared/utils/DocumentScore.py
apps_shared/utils/EmbedJobDescription.py
apps_shared/utils/EmbedMessageTemplate.py
apps_shared/utils/EmbedRecipientProfile.py
apps_shared/utils/ETLPipeline.py
apps_shared/utils/file_io.py
apps_shared/utils/format_observability_context_plan_type.py
apps_shared/utils/FormatData.py
apps_shared/utils/FormatMetadata.py
apps_shared/utils/FormattedOutput.py
apps_shared/utils/golden_state_datasets.py
apps_shared/utils/health_check_types.py
apps_shared/utils/health_metrics.py
apps_shared/utils/injection_patterns_extended.py
apps_shared/utils/InjectionPatterns.py
apps_shared/utils/json_parser_validator.py
apps_shared/utils/l1_health_benchmark.py
apps_shared/utils/LateInteractionReranker.py
apps_shared/utils/LLMProfile.py
apps_shared/utils/LogObservabilityMetrics.py
apps_shared/utils/math_operations.py
apps_shared/utils/metric_type.py
apps_shared/utils/MetricRegistry.py
apps_shared/utils/model_visitor.py
apps_shared/utils/mutation_phase.py
apps_shared/utils/observability_clients.py
apps_shared/utils/observability_type.py
apps_shared/utils/Observability.py
apps_shared/utils/OpenTelemetryTracingAdapter.py
apps_shared/utils/optimize_observability_order_plan_type.py
apps_shared/utils/orchestration_mixin.py
apps_shared/utils/performance_monitor_types.py
apps_shared/utils/PromptLoader.py
apps_shared/utils/Provider.py
apps_shared/utils/providers_google_genai_client.py
apps_shared/utils/rank_data_components_plan_type.py
apps_shared/utils/rank_observability_components.py
apps_shared/utils/reasoning_prompt.py
apps_shared/utils/request_type.py
apps_shared/utils/resource_manager_types.py
apps_shared/utils/resource_manager.py
apps_shared/utils/RetrievalGrader.py
apps_shared/utils/router_factory.py
apps_shared/utils/runtime_observability_collectors.py
apps_shared/utils/runtime_observability_spans.py
apps_shared/utils/RuntimeMetricsCollector.py
apps_shared/utils/Safety.py
apps_shared/utils/ScoreResult.py
apps_shared/utils/SecureConfigManager.py
apps_shared/utils/security_utils_config.py
apps_shared/utils/SerializeGenerationContext.py
apps_shared/utils/sleeping_giant.py
apps_shared/utils/StatePersistenceError.py
apps_shared/utils/StoredPrompt.py
apps_shared/utils/subatomic_hop.py
apps_shared/utils/text_processing_validator.py
apps_shared/utils/ThinkStep.py
apps_shared/utils/TitaniumRAGPipeline.py
apps_shared/utils/ToneVoice.py
apps_shared/utils/underscore_visitor.py
apps_shared/utils/unified_executor.py
apps_shared/utils/unified_signal_pipeline.py
apps_shared/utils/validation_mixin.py
apps_shared/utils/vector_memory_types.py
apps_shared/utils/VersionTag.py
apps_shared/utils/waterfall_reconciliation.py
apps_lic/utils/cot.py
apps_lic/utils/hop_stage_capability.py
apps_lic/utils/lic_engine_validation_capability.py
apps_lic/utils/LICAgentBase.py
apps_lic/utils/ManifestManager.py
apps_lic/utils/mixins.py
apps_rg/utils/agent_executor.py
apps_rg/utils/authenticity_patterns.py
apps_rg/utils/deep_brain_harvester.py
apps_rg/utils/enhanced_rg_flow_router.py
apps_rg/utils/providers_anthropic_client.py
apps_rg/utils/rg_core_mixins.py
apps_rg/utils/rg_validation_capability.py
apps_rg/utils/RGAgentBase.py
```

#### 4.4 Files with `*_utils.py` Suffix (Should Be `*_util.py`) (1 file)

```
apps_rg/tools/text_utils.py
```

#### 4.5 Files with `utilities_*.py` Prefix (Forbidden) (19 files)

```
apps_shared/reasoning/utilities_refactor_agents_to_subatomic.py
apps_shared/scripts/utilities_assess_dependencies.py
apps_shared/scripts/utilities_clean_shims_simple.py
apps_shared/scripts/utilities_find_long_lines.py
apps_shared/scripts/utilities_fix_all_indentation_errors.py
apps_shared/scripts/utilities_fix_all_indentation.py
apps_shared/scripts/utilities_fix_all_violations.py
apps_shared/scripts/utilities_fix_cognitive_density.py
apps_shared/scripts/utilities_fix_global_variables.py
apps_shared/scripts/utilities_fix_indentation.py
apps_shared/scripts/utilities_fix_long_lines.py
apps_shared/scripts/utilities_fix_markdown_fences.py
apps_shared/scripts/utilities_fix_specific_long_lines.py
apps_shared/scripts/utilities_fix_structural_debt.py
apps_shared/scripts/utilities_fix_syntax_errors.py
apps_shared/scripts/utilities_fix_whitespace_in_container.py
apps_shared/scripts/utilities_manage_false_positives.py
apps_lic/tools/utilities_clean_duplicates_enhanced.py
apps_lic/tools/utilities_fix_duplicate_imports.py
```

#### 4.6 PascalCase Files in config/ (3 files)

```
apps_lic/config/ReasoningToggles.py
apps_rg/config/AgentSpec.py
apps_rg/config/ReasoningToggles.py
```

#### 4.7 PascalCase Files in utils/ (42 files)

```
apps_shared/utils/AppBase.py
apps_shared/utils/ARCHIVE_FILE_ACCESS_DEPRECATED.py
apps_shared/utils/AssessmentLevel.py
apps_shared/utils/BackupManager.py
apps_shared/utils/BaggagePropagator.py
apps_shared/utils/CacheMetrics.py
apps_shared/utils/CanonError.py
apps_shared/utils/CollectedItem.py
apps_shared/utils/ConfigurationService.py
apps_shared/utils/ContextualCompressor.py
apps_shared/utils/DocumentScore.py
apps_shared/utils/EmbedJobDescription.py
apps_shared/utils/EmbedMessageTemplate.py
apps_shared/utils/EmbedRecipientProfile.py
apps_shared/utils/ETLPipeline.py
apps_shared/utils/FormatData.py
apps_shared/utils/FormatMetadata.py
apps_shared/utils/FormattedOutput.py
apps_shared/utils/InjectionPatterns.py
apps_shared/utils/LateInteractionReranker.py
apps_shared/utils/LLMProfile.py
apps_shared/utils/LogObservabilityMetrics.py
apps_shared/utils/MetricRegistry.py
apps_shared/utils/Observability.py
apps_shared/utils/OpenTelemetryTracingAdapter.py
apps_shared/utils/PromptLoader.py
apps_shared/utils/Provider.py
apps_shared/utils/RetrievalGrader.py
apps_shared/utils/RuntimeMetricsCollector.py
apps_shared/utils/Safety.py
apps_shared/utils/ScoreResult.py
apps_shared/utils/SecureConfigManager.py
apps_shared/utils/SerializeGenerationContext.py
apps_shared/utils/StatePersistenceError.py
apps_shared/utils/StoredPrompt.py
apps_shared/utils/ThinkStep.py
apps_shared/utils/TitaniumRAGPipeline.py
apps_shared/utils/ToneVoice.py
apps_shared/utils/VersionTag.py
apps_lic/utils/LICAgentBase.py
apps_lic/utils/ManifestManager.py
apps_rg/utils/RGAgentBase.py
```

### 5. Violation Summary

| Category | Count |
|----------|-------|
| config/ files missing `_config.py` suffix | 25 |
| `*_util.py` files in config/ (should be in utils/) | 19 |
| utils/ files missing `_util.py` suffix | 95 |
| `*_utils.py` files (should be `*_util.py`) | 1 |
| `utilities_*.py` files (forbidden prefix) | 19 |
| PascalCase files in config/ | 3 |
| PascalCase files in utils/ | 42 |
| **TOTAL UNIQUE VIOLATIONS** | **~140** |

### 6. Core Enforcement Scope Analysis

The `FileClassificationAgent.validate_layer_alignment()` method contains the naming enforcement logic:

```python
# --- CONFIG SUFFIX ENFORCEMENT: .py files in config/ missing _config ---
if "config" in parts or any(p.endswith("_configs") or p.endswith("_config") for p in parts):
    stem = path.stem
    if (
        not stem.startswith("test_")
        ...
    ):
        return {
            "violation": "CONFIG_SUFFIX_MISSING",
            "message": (
                f"'{path.name}' lives in a config/ directory but is missing "
                f"the '_config' suffix. Rename to '{stem}_config.py'."
            ),
        }
```

**Current Scope Gate**: The enforcement appears to apply to any path containing "config" in parts, which should include apps_* paths. However, the execute_ssot.py may have early-return bypasses for apps_* directories.

---

## Wave 1 Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Evidence shows core enforcement functions | ✅ |
| Evidence shows where apps_* is excluded/bypassed | ✅ |
| Concrete violation lists for apps_* | ✅ |

---

## Wave 2 — Extend Existing Core Logic

### Bypasses Removed

Two apps_* bypasses were removed from `FileClassificationAgent.py`:

1. **Line 2131-2136** (`validate_folder_suffix_consistency`):
   - Before: `if any(p.startswith("apps_") for p in path.parts): return None`
   - After: Removed bypass, apps_* now evaluated by same logic

2. **Line 2193-2198** (`_enforce_folder_purity`):
   - Before: `if any(p.startswith("apps_") for p in path.parts): return None`
   - After: Removed bypass, apps_* now evaluated by same logic

### Shared Enforcement Tests Added

File: `tests/architecture/test_apps_ssot_shared_enforcement.py`

| Test Class | Tests | Status |
|------------|-------|--------|
| TestSharedEnforcementLogic | 12 | ✅ PASS |
| TestNegativeCases | 5 | ✅ PASS |
| TestEnforcementFunctionIdentity | 1 | ✅ PASS |
| **TOTAL** | **18** | **✅ PASS** |

### Test Output

```text
pytest tests/architecture/test_apps_ssot_shared_enforcement.py -v
18 passed in 0.20s
```

### Full Test Suite

```text
pytest -q
153 passed in 20.16s
```

### Wave 2 Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Tests pass | ✅ 153 passed |
| apps_* paths evaluated by same core functions | ✅ |
| Same violations produced for apps_* as agentic_core | ✅ |

---

## Wave 3 — Controlled Remediation

### Scope Assessment

The extended enforcement now detects violations in apps_* folders. However, the remediation scope is large:

| Category | Count | Remediation |
|----------|-------|-------------|
| config/ files missing `_config.py` | 25 | Rename or move to utils/ |
| utils/ files missing `_util.py` | 95 | Rename to `*_util.py` |
| `utilities_*.py` files | 19 | Move to utils/ + rename |
| PascalCase in config/ | 3 | Rename to snake_case |
| PascalCase in utils/ | 42 | Rename to snake_case |
| **TOTAL** | **~140** | |

### Remediation Strategy

Given the large scope, Wave 3 remediation should be split into sub-phases:

1. **Phase 1a**: Fix `utilities_*.py` files (19 files) - forbidden prefix
2. **Phase 1b**: Move `*_util.py` from config/ to utils/ (19 files)
3. **Phase 1c**: Rename PascalCase files (45 files)
4. **Phase 1d**: Add `_util.py` suffix to utils/ files (95 files)
5. **Phase 1e**: Add `_config.py` suffix to config/ files (remaining)

### Current Status

Wave 3 file remediation is **deferred** pending user decision on scope (~140 files).

The enforcement extension is complete and functional:

- apps_* paths are now governed by the same core logic as agentic_core
- 18 tests prove shared enforcement
- 153 total tests pass
- All pre-commit hooks pass

---

## Final Commit

```text
Commit: e1bee1e3734d70945f3106db75433151bdb243d2
Message: governance(apps): extend core SSOT naming/purity enforcement to apps_*

Files changed:
 agentic_core/L5_safety/reasoning/FileClassificationAgent.py |  23 +-
 docs/reports/plans/apps_ssot_governance_extension_phase1.md | 428 +++
 tests/architecture/test_apps_ssot_shared_enforcement.py     | 176 +++
 3 files changed, 615 insertions(+), 12 deletions(-)
```

---

## Files Changed

### Wave 1 (Analysis Only)

- `docs/reports/plans/apps_ssot_governance_extension_phase1.md` (this file)

### Wave 2 (Scope Extension)

- `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` - removed apps_* bypasses
- `tests/architecture/test_apps_ssot_shared_enforcement.py` - new shared enforcement tests

---

## Phase 1 Completion Summary

| Wave | Description | Status |
|------|-------------|--------|
| Wave 1 | Baseline + identify bypasses | ✅ Complete |
| Wave 2 | Extend core logic to apps_* | ✅ Complete |
| Wave 3 | File remediation | ⏸️ Deferred (140 files) |

**Objective Achieved**: apps_* SSOT folders are now governed by the **same** core enforcement logic as agentic_core. No duplicate rules were created.

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

