# Monolithic Non-Agentic Files - Modularization Report

**Generated:** 2026-01-01  
**Purpose:** Identify all large monolithic files for subatomic architecture compatibility

---

## Summary

**Total Files to Modularize:** 51

| Type | Count | Criteria |
|------|-------|----------|
| Python | 0 | >500 lines + >5 dataclasses/BaseModels/Enums OR >15 classes |
| JSON | 19 | >10KB |
| YAML | 30 | >5KB |
| Markdown | 2 | >20KB |

---

## Python Files (0 found)

✓ **No monolithic Python files remaining** - `core_contracts.py` successfully modularized into 7 packages.

---

## JSON Files (19 files)

| Lines | Size (KB) | File Path |
|------:|----------:|-----------|
| 11,939 | 482 | `agentic_core/config/blueprint_sovereign/active_manifest.json` |
| 1,384 | 95 | `data/processed/semantic_cache/global_report_20251201_224529.json` |
| 1,352 | 94 | `data/processed/semantic_cache/resume_engine_report_20251201_224529.json` |
| 1,049 | 79 | `data/processed/semantic_cache/global_report_20251201_224738.json` |
| 1,017 | 78 | `data/processed/semantic_cache/resume_engine_report_20251201_224738.json` |
| 969 | 62 | `data/processed/semantic_cache/global_report_20251201_224928.json` |
| 937 | 61 | `data/processed/semantic_cache/resume_engine_report_20251201_224928.json` |
| 795 | 39 | `data/freeze_reports/07_observability_freeze_report.json` |
| 668 | 21 | `agent_discovery_report.json` |
| 606 | 17 | `agentic_core/prompt_governance/version_registry/registry.json` |
| 533 | 15 | `data/golden_state/datasets/test_cases.json` |
| 528 | 15 | `ast_redundancy_report_ultra.json` |
| 467 | 25 | `data/freeze_reports/04_prompt_governance_freeze_report.json` |
| 439 | 19 | `tests/10_tests_freeze_report.json` |
| 427 | 21 | `data/freeze_reports/05_config_freeze_report.json` |
| 403 | 12 | `agent_registry_temp.json` |
| 141 | 14 | `agentic_core/L0_maintenance/scripts/schemas/data_assets/master_resume.json` |
| 29 | 27 | `agentic_core/L0_maintenance/scripts/schemas/data_assets/prompts.json` |
| 1 | 371 | `coverage_html/status.json` |

### Modularization Strategy for JSON Files

**High Priority (>100KB or >1000 lines):**
1. `active_manifest.json` (482KB) - Split by agent/layer/domain
2. Semantic cache reports - Archive old reports, keep only recent

**Medium Priority (Config/Registry):**
3. `version_registry/registry.json` - Split by version/component
4. `test_cases.json` - Split by test category
5. `master_resume.json` - Already modular candidate

**Low Priority (Reports/Temp):**
- Freeze reports - Consider archiving
- Temp files - Clean up or archive

---

## YAML Files (30 files)

| Lines | Size (KB) | File Path |
|------:|----------:|-----------|
| 533 | 16 | `data/prompt_governance/injections/safety.yaml` |
| 512 | 14 | `data/prompt_governance/injections/output_governance.yaml` |
| 470 | 15 | `data/prompt_governance/injections/reasoning.yaml` |
| 469 | 15 | `data/prompt_governance/injections/tool_use.yaml` |
| 466 | 15 | `data/prompt_governance/injections/framing.yaml` |
| 457 | 12 | `data/prompt_governance/injections/context_engineering.yaml` |
| 411 | 12 | `data/prompt_governance/governance/access_control.yaml` |
| 411 | 13 | `data/external/reference_playbooks/access_control.yaml` |
| 409 | 19 | `data/prompt_governance/evaluations/regression_tests.yaml` |
| 402 | 14 | `data/prompt_governance/governance/ownership.yaml` |
| 402 | 14 | `data/external/reference_playbooks/ownership.yaml` |
| 400 | 17 | `data/prompt_governance/evaluations/eval_sets.yaml` |
| 358 | 13 | `data/prompt_governance/governance/compliance_mapping.yaml` |
| 358 | 13 | `data/external/reference_playbooks/compliance_mapping.yaml` |
| 357 | 18 | `data/prompt_governance/evaluations/style_checks.yaml` |
| 357 | 11 | `data/prompt_governance/governance/semantic_versioning.yaml` |
| 357 | 11 | `data/external/reference_playbooks/semantic_versioning.yaml` |
| 353 | 10 | `data/prompt_governance/registry/prompt_manifest.yaml` |
| 340 | 8 | `data/prompt_governance/registry/version_map.yaml` |
| 325 | 8 | `data/prompt_governance/registry/rollback_policies.yaml` |
| 311 | 11 | `data/prompt_governance/governance/approval_workflow.yaml` |
| 311 | 10 | `data/external/reference_playbooks/approval_workflow.yaml` |
| 308 | 12 | `data/prompt_governance/governance/change_history.yaml` |
| 308 | 12 | `data/external/reference_playbooks/change_history.yaml` |
| 305 | 7 | `data/prompt_governance/injections/constraints.yaml` |
| 296 | 11 | `data/prompt_governance/evaluations/rubric.yaml` |
| 261 | 7 | `agentic_core/config/blueprint_sovereign/docker_compose_pipeline.yml` |
| 246 | 6 | `data/prompt_governance/registry/prompt_index.yaml` |
| 197 | 4 | `agentic_core/config/mcp_mappings.yaml` |
| 197 | 4 | `agentic_core/config/blueprint_sovereign/mcp_mappings.yaml` |

### Modularization Strategy for YAML Files

**Prompt Governance Injections (6 files):**
- Split by injection type/category
- Create modular injection registry

**Prompt Governance Governance (8 files):**
- Split by governance domain
- Create policy module structure

**Prompt Governance Evaluations (4 files):**
- Split by evaluation type
- Create test suite modules

**Prompt Governance Registry (4 files):**
- Split by version/component
- Create manifest modules

**External Reference Playbooks (5 files):**
- Consolidate with governance files or archive

**Config Files (3 files):**
- `docker_compose_pipeline.yml` - Split by service
- `mcp_mappings.yaml` - Split by MCP server

---

## Markdown Files (2 files)

| Lines | Size (KB) | File Path |
|------:|----------:|-----------|
| 1,154 | 34 | `agentic_core/MCP_INTEGRATION_GAP_ASSESSMENT.md` |
| 613 | 19 | `agent_supplementation_report.md` |

### Modularization Strategy for Markdown Files

1. **MCP_INTEGRATION_GAP_ASSESSMENT.md** - Split by MCP server/integration
2. **agent_supplementation_report.md** - Archive or split by agent category

---

## Recommended Modularization Priority

### Phase 1: Critical Infrastructure (Immediate)
1. ✅ `core_contracts.py` - **COMPLETED** (modularized into 7 packages)
2. `active_manifest.json` (482KB) - Split by layer/domain
3. `prompt_governance/injections/*.yaml` - Create injection modules

### Phase 2: Configuration & Governance (High Priority)
4. `prompt_governance/governance/*.yaml` - Create policy modules
5. `prompt_governance/registry/*.yaml` - Create registry modules
6. `version_registry/registry.json` - Split by component

### Phase 3: Data & Reports (Medium Priority)
7. Semantic cache reports - Archive old, modularize structure
8. Test cases & evaluation sets - Split by category
9. Freeze reports - Archive or consolidate

### Phase 4: Documentation (Low Priority)
10. Large markdown files - Split by topic
11. External reference playbooks - Consolidate or archive

---

## Subatomic Architecture Compatibility Notes

**Key Requirements:**
- Files should be <500 lines for optimal hop granularity
- Config files should be split by bounded context
- Data files should support lazy loading
- All modules should have clear single responsibility

**Benefits of Modularization:**
- Faster import times (load only what's needed)
- Better hop isolation (smaller context windows)
- Easier testing (focused test suites)
- Improved maintainability (clear boundaries)
- Enhanced sovereignty (modular compliance)

---

**Next Steps:** Review this report and prioritize which files to modularize first based on subatomic architecture requirements.
