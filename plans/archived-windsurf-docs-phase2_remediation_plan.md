---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\phase2_remediation_plan.md'
original_relative_path: 'phase2_remediation_plan.md'
source_sha256: 0307749f0e1b78c636138246c5b01da6260088901af181c0f8fab477f3523843
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-16'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase 2 Remediation Plan - Systemic Naming Drift Remediation

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

Phase 2 addresses 21 systemic naming violations across all app domains, focusing on MISNAMED_UTILITY files that contain active logic but are misclassified as config files.

## Violation Analysis

### Current State
- **apps_shared**: 17 UTILITY violations (MISNAMED_UTILITY)
- **apps_lic**: 2 UTILITY violations (MISNAMED_UTILITY) + 1 PASSIVE_AGENT_NAMING
- **apps_rg**: 2 UTILITY violations (MISNAMED_UTILITY)
- **Total**: 21 violations requiring systematic remediation

### Pattern Analysis
**Primary Pattern**: Files ending in `_config.py` that contain active classes with methods, making them utilities rather than configuration files.

**Secondary Pattern**: DUAL-TAG conflicts in `_types.py` files carrying multiple classification signals.

## Phase 2 Remediation Strategy

### Wave 1: MISNAMED_UTILITY Systematic Remediation
**Target**: All 21 MISNAMED_UTILITY violations
**Approach**: Rename files to reflect their true nature as utilities

**Naming Convention**:
- `_config.py` → `_util.py` for files with active classes
- Preserve existing functionality while correcting classification

### Wave 2: DUAL-TAG Deterministic Resolution
**Target**: Multiple DUAL-TAG conflicts in `_types.py` files
**Approach**: Apply deterministic hierarchy based on folder context

**Resolution Rules**:
- `config/` folder → CONFIG tag takes precedence
- `reasoning/` folder → Higher-level classification takes precedence
- `types/` subfolder → TYPES tag takes precedence

### Wave 3: PASSIVE_AGENT_NAMING Resolution
**Target**: 1 PASSIVE_AGENT_NAMING violation in apps_lic
**Approach**: Rename dataclass/BaseModel files to appropriate suffix

## Detailed Remediation Plan

### apps_shared - 17 Violations

**MISNAMED_UTILITY Files** (rename to `_util.py`):
1. config_loader_config.py → config_loader_util.py
2. environment_config.py → environment_util.py
3. feedback_category_config.py → feedback_category_util.py
4. graph_rag_fusion_config.py → graph_rag_fusion_util.py
5. input_guardrail_config.py → input_guardrail_util.py
6. input_validator_config.py → input_validator_util.py
7. metric_augmenter_config.py → metric_augmenter_util.py
8. metric_config.py → metric_util.py
9. node_negotiator_config.py → node_negotiator_util.py
10. prompt_enhancer_config.py → prompt_enhancer_util.py
11. prompt_registry_config.py → prompt_registry_util.py
12. relevance_scorer_config.py → relevance_scorer_util.py
13. sdk_category_config.py → sdk_category_util.py
14. settings_config.py → settings_util.py
15. signal_weighter_config.py → signal_weighter_util.py
16. token_budget_config.py → token_budget_util.py
17. security_utils_config.py → security_util.py

**DUAL-TAG Files** (deterministic resolution):
- app_config_types.py → TYPES tag (types/ subfolder)
- checkpoint_manager_types.py → MANAGER tag (functionality)
- execution_orchestrator_types.py → ORCHESTRATOR tag (functionality)
- feedback_loop_orchestrator_types.py → ORCHESTRATOR tag (functionality)
- memory_manager_types.py → MANAGER tag (functionality)
- resource_manager_types.py → MANAGER tag (functionality)
- validation_context_manager_validator.py → VALIDATOR tag (functionality)

### apps_lic - 3 Violations

**MISNAMED_UTILITY Files** (rename to `_util.py`):
1. archetype_indicator_config.py → archetype_indicator_util.py

**DUAL-TAG Files** (deterministic resolution):
- placeholder_detector_agent_config.py → AGENT tag (functionality)
- code_quality_guardrail_types.py → GUARDRAIL tag (functionality)
- competitor_recon_agent_types.py → AGENT tag (functionality)
- stack_modernization_agent_types.py → AGENT tag (functionality)
- app_content_validator_agent_types.py → AGENT tag (functionality)

**PASSIVE_AGENT_NAMING**:
- PIISanitizerSpecialistAgent.py → PIISanitizerSpecialistAgent_util.py

### apps_rg - 2 Violations

**MISNAMED_UTILITY Files** (rename to `_util.py`):
1. clerk_extractor_config.py → clerk_extractor_util.py
2. sovereign_config_loader_config.py → sovereign_config_loader_util.py

**DUAL-TAG Files** (deterministic resolution):
- gap_closure_architect_agent_types.py → AGENT tag (functionality)

## Implementation Approach

### Phase 2.1: Automated Renaming
- Use FileClassificationAgent in active mode (not dry-run)
- Apply systematic renaming with collision detection
- Update import statements automatically

### Phase 2.2: Import Resolution
- Scan for imports of renamed files
- Update import statements across codebase
- Validate no broken references remain

### Phase 2.3: Validation
- Re-run classification analysis
- Verify all violations resolved
- Ensure functional integrity maintained

## Risk Mitigation

### Import Impact Assessment
- Map all import dependencies before renaming
- Create rollback plan for each file
- Test critical paths after remediation

### Functional Validation
- Run existing test suites
- Verify no runtime errors introduced
- Confirm all agents still instantiate correctly

## Success Criteria

### Quantitative
- All 21 violations eliminated
- 0 MISNAMED_UTILITY violations remaining
- 0 DUAL-TAG conflicts remaining
- 0 PASSIVE_AGENT_NAMING violations remaining

### Qualitative
- All files accurately classified
- Import dependencies resolved
- No functional regressions
- Clean governance baseline achieved

## Timeline Estimate

- **Wave 1**: 2- (systematic renaming)
- **Wave 2**: 1- (DUAL-TAG resolution)
- **Wave 3**:  (PASSIVE_AGENT_NAMING)
- **Validation**: 1- (testing and verification)

**Total Estimated**: 4.5-

## Next Steps

1. Begin Wave 1 systematic renaming with automated tools
2. Monitor for import impacts and resolve immediately
3. Proceed to Wave 2 and 3 based on Wave 1 results
4. Complete comprehensive validation before Phase 2 certification

---
**Phase 2 Status**: PLANNING COMPLETE
**Ready to Execute**: Systematic naming drift remediation

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

