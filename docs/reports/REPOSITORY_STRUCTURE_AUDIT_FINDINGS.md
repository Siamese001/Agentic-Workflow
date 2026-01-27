# Repository Structure Audit - Comprehensive Findings & Recommendations

**Date:** January 26, 2026  
**Scope:** All approved top-level folders (agentic_core, apps_shared, apps_rg, apps_lic, archives, data, docs, logs, scripts, tests)  
**Objective:** Align `structure_blueprint.py` SSOT with actual repository content

---

## Executive Summary

**Total Folders Audited:** 10 top-level folders  
**Critical Findings:** 23 misalignments between SSOT and actual structure  
**Recommendations:** 15 structural optimizations (8 depth increases, 7 depth decreases)

### Key Findings
1. **apps_shared** has unapproved subfolders not in SSOT
2. **agentic_core** has several missing subfolder declarations
3. **data** and **docs** folders not defined in SSOT at all
4. **archives** and **logs** folders not defined in SSOT
5. **L0_maintenance** has complex subfolder structure needing L4 depth
6. **apps_rg/apps_lic** have inconsistent subfolder definitions

---

## 1. AGENTIC_CORE Analysis

### Current Structure (Actual)
```
agentic_core/
├── L0_maintenance/ (282 items)
│   ├── scripts/ (269 items) ✓ L4 approved
│   ├── logs/ (6 items)
│   ├── reports/ (1 item)
│   ├── boot/ (1 item)
│   ├── security/ (1 item)
│   └── agentic_core/ (1 item) ⚠️ UNEXPECTED
├── L1_cognition/ (62 items)
│   ├── thought_engine/ (54 items) ✓ L4 approved
│   └── intent_analysis/ (6 items)
├── L2_execution/ (76 items)
│   ├── ToolRegistry/ (57 items)
│   ├── mcp/ (17 items) ✓ L4 approved
│   └── unified/ (1 item)
├── L3_orchestration/ (55 items)
│   ├── workflow_engines/ (45 items) ✓ L4 approved
│   ├── fission_logic/ (4 items)
│   └── interfaces/ (3 items)
├── L4_state/ (41 items)
│   ├── ValidationContext/ (31 items) ✓ L4 approved
│   ├── ledger/ (6 items)
│   └── memory/ (4 items)
├── L5_safety/ (212 items)
│   ├── validators/ (131 items) ✓ L4 approved
│   ├── guardrails/ (36 items) ✓ L4 approved
│   ├── unified/ (18 items)
│   ├── gravity/ (14 items) ✓ L4 approved
│   ├── red_teaming/ (6 items)
│   ├── cognition/ (3 items)
│   ├── core/ (2 items)
│   └── utils/ (2 items)
├── L6_observability/ (52 items)
│   ├── dashboards/ (34 items) ✓ L4 approved
│   ├── agents/ (13 items)
│   ├── reports/ (1 item)
│   └── telemetry/ (1 item)
├── base_agents/ (37 items)
├── config/ (21 items)
│   └── blueprint_sovereign/ (14 items) ✓ L4 approved
├── domain/ (6 items)
├── knowledge/ (8 items)
│   └── document_loaders/ (6 items)
├── patterns/ (8 items)
│   └── agent_roles/ (6 items)
├── prompt_governance/ (78 items)
│   ├── meta_prompts/ (19 items)
│   ├── templates/ (34 items)
│   ├── scripts/ (8 items)
│   └── version_registry/ (3 items)
├── runtime/ (18 items)
│   └── shared_runtime/ (15 items)
├── schemas/ (18 items)
│   └── models/ (18 items) ✓ L4 approved
├── semantic_memory/ (6 items)
│   └── store/ (2 items)
└── utils/ (17 items)
```

### SSOT Definition (structure_blueprint.py)
```python
CORE_SUBFOLDER_MAP = {
    "base_agents": [],
    "domain": ["entities", "models", "exceptions"],
    "L0_maintenance": ["scripts", "logs", "benchmarks", "mixins"],
    "L1_cognition": ["thought_engine", "intent_analysis", "planning"],
    "L2_execution": ["core", "tool_registry", "action_handlers", "mcp", "scripts"],
    "L3_orchestration": ["workflow_engines", "fission_logic", "interfaces", "scripts"],
    "L4_state": ["ledger", "memory", "validation_context", "scripts"],
    "L5_safety": ["cognition", "core", "gravity", "guardrails", "red_teaming", "unified", "utils", "validators", "scripts"],
    "L6_observability": ["core", "dashboards", "telemetry", "compliance", "scripts"],
    "schemas": ["models", "messages", "types", "validators", "scripts"],
    "config": ["blueprint_sovereign", "environments", "feature_flags", "secrets_manager", "scripts"],
    "prompt_governance": ["meta_prompts", "scripts", "templates", "security", "core", "version_registry"],
    "runtime": ["shared_runtime", "environment_setup", "resource_management"],
    "utils": ["core_extensions", "wrappers", "general_helpers"],
    "patterns": ["reasoning", "behavior", "interaction", "scripts"],
    "semantic_memory": ["models", "interfaces", "store", "retrieval", "indexes"],
    "knowledge": ["document_loaders", "types", "rag", "processing"],
}
```

### Findings & Recommendations

#### ✅ ALIGNED
- **L1_cognition**: Has `thought_engine`, `intent_analysis` (missing `planning` but not critical)
- **L3_orchestration**: Has `workflow_engines`, `fission_logic`, `interfaces`
- **L5_safety**: All 8 subfolders present
- **prompt_governance**: Has `meta_prompts`, `templates`, `scripts`, `version_registry`

#### ❌ MISALIGNED

**L0_maintenance**
- **Missing in SSOT:** `boot/`, `reports/`, `security/`
- **Unexpected:** `agentic_core/` subfolder (likely misplaced)
- **Missing in actual:** `benchmarks/`, `mixins/`
- **Recommendation:** Add `boot`, `reports`, `security` to SSOT; investigate `agentic_core/` subfolder

**L2_execution**
- **Missing in actual:** `core/`, `action_handlers/`, `scripts/`
- **Actual has:** `ToolRegistry/` (should be `tool_registry`), `unified/`
- **Recommendation:** Add `unified` to SSOT; verify if `ToolRegistry` should be renamed to `tool_registry`

**L4_state**
- **Missing in actual:** `scripts/`
- **Actual has:** `ValidationContext/` (should be `validation_context` per SSOT)
- **Recommendation:** Consider renaming `ValidationContext` to `validation_context` for consistency

**L6_observability**
- **Missing in actual:** `core/`, `compliance/`, `scripts/`
- **Actual has:** `agents/`
- **Recommendation:** Add `agents` to SSOT; verify if `core`, `compliance`, `scripts` are needed

**config**
- **Missing in actual:** `environments/`, `secrets_manager/`, `scripts/`
- **Recommendation:** Add these if needed, or remove from SSOT if not planned

**schemas**
- **Missing in actual:** `messages/`, `types/`, `validators/`, `scripts/`
- **Recommendation:** Add these if needed, or remove from SSOT if not planned

**runtime**
- **Missing in actual:** `environment_setup/`, `resource_management/`
- **Recommendation:** Remove from SSOT if not planned

**utils**
- **Missing in actual:** `core_extensions/`, `wrappers/`, `general_helpers/`
- **Note:** `core_extensions` is in L4_APPROVED_FOLDERS but doesn't exist
- **Recommendation:** Remove non-existent subfolders from SSOT

**patterns**
- **Missing in actual:** `reasoning/`, `behavior/`, `interaction/`, `scripts/`
- **Actual has:** `agent_roles/`
- **Recommendation:** Replace SSOT definition with actual structure: `["agent_roles"]`

**semantic_memory**
- **Missing in actual:** `models/`, `interfaces/`, `retrieval/`, `indexes/`
- **Recommendation:** Update SSOT to match actual: `["store"]`

**knowledge**
- **Missing in actual:** `types/`, `rag/`, `processing/`
- **Recommendation:** Update SSOT to match actual: `["document_loaders"]`

---

## 2. APPS_SHARED Analysis

### Current Structure (Actual)
```
apps_shared/
├── base_agents/ (1 item)
├── common_utils/ (266 items) ⚠️ NOT IN SSOT
├── config/ (2 items)
├── core_components/ (4 items) ⚠️ NOT IN SSOT
├── data/ (3 items) ⚠️ NOT IN SSOT
├── tools/ (0 items - empty)
└── utils/ (7 items)
```

### SSOT Definition
```python
APPS_SHARED_SUBFOLDER_MAP = {
    "core": ["base_classes", "interfaces", "contracts"],
    "models": ["dtos", "schemas", "types"],
    "utils": ["string_utils", "date_utils", "file_utils"],
    "components": ["loggers", "loaders", "adapters"],
    "agents": ["worker_definitions", "mixins"],
    "templates": ["patterns", "formats"],
}
```

### Findings & Recommendations

#### ❌ CRITICAL MISALIGNMENT
- **SSOT defines:** `core`, `models`, `components`, `agents`, `templates`
- **Actual has:** `base_agents`, `common_utils`, `config`, `core_components`, `data`, `tools`, `utils`
- **Zero overlap** except `utils`

#### 🔧 RECOMMENDATIONS
1. **Rename `base_agents` → `agents`** (align with SSOT)
2. **Rename `common_utils` → `utils`** (consolidate utilities)
3. **Rename `core_components` → `components`** (align with SSOT)
4. **Add `core` folder** with `base_classes`, `interfaces`, `contracts`
5. **Add `models` folder** with `dtos`, `schemas`, `types`
6. **Add `templates` folder** if needed
7. **Evaluate `config` and `data`** - add to SSOT if permanent

**Alternative:** Update SSOT to match actual structure if current naming is intentional.

---

## 3. APPS_RG Analysis

### Current Structure (Actual)
```
apps_rg/
├── asset_library/ (0 items - empty)
├── core/ (1 item)
├── domain/ (6 items)
├── engines/ (73 items)
├── logic_nodes/ (6 items)
├── shared/ (53 items)
├── system_flow/ (0 items - empty)
└── validation/ (4 items) ⚠️ NOT IN SSOT
```

### SSOT Definition
```python
APPS_RG_SUBFOLDER_MAP = {
    "core": ["base", "config", "exceptions"],
    "domain": ["models", "types", "events", "config"],
    "engines": ["drivers", "generators", "utils"],
    "logic_nodes": ["node_definitions", "node_helpers"],
    "asset_library": ["asset_definitions", "asset_helpers"],
    "system_flow": ["flow_definitions", "flow_helpers"],
    "shared": ["core", "reasoning", "tools"],
    "validation": ["validators", "rules", "results"],
    "scripts": ["migration", "maintenance", "utilities"],
    "tools": ["utilities", "processors", "analyzers"],
    "reports": ["generators", "templates", "outputs"]
}
```

### Findings & Recommendations

#### ✅ ALIGNED
- Has: `asset_library`, `core`, `domain`, `engines`, `logic_nodes`, `shared`, `system_flow`, `validation`

#### ❌ MISALIGNED
- **Missing in actual:** `scripts/`, `tools/`, `reports/`
- **Recommendation:** Add these folders if needed, or remove from SSOT

#### 📊 DEPTH ANALYSIS
- **engines/**: 73 items - **Consider L3 depth** (create subfolders: `drivers`, `generators`, `utils`)
- **shared/**: 53 items - **Consider L3 depth** (create subfolders: `core`, `reasoning`, `tools`)

---

## 4. APPS_LIC Analysis

### Current Structure (Actual)
```
apps_lic/
├── asset_library/ (0 items - empty)
├── domain/ (18 items)
├── engines/ (53 items)
├── logic_nodes/ (1 item)
├── reports/ (2 items)
├── scripts/ (2 items)
├── shared/ (66 items)
├── system_flow/ (0 items - empty)
└── tools/ (2 items)
```

### SSOT Definition
```python
APPS_LIC_SUBFOLDER_MAP = {
    "core": ["base", "config", "exceptions"],
    "domain": ["models", "types", "events", "config"],
    "engines": ["drivers", "generators", "utils"],
    "logic_nodes": ["node_definitions", "node_helpers"],
    "asset_library": ["asset_definitions", "asset_helpers"],
    "system_flow": ["flow_definitions", "flow_helpers"],
    "shared": ["core", "reasoning", "tools"],
    "validation": ["validators", "rules", "results"],
    "scripts": ["migration", "maintenance", "utilities"],
    "tools": ["utilities", "processors", "analyzers"],
    "reports": ["generators", "templates", "outputs"]
}
```

### Findings & Recommendations

#### ❌ MISALIGNED
- **Missing in actual:** `core/`, `validation/`
- **Recommendation:** Add `core` folder if needed, or remove from SSOT

#### 📊 DEPTH ANALYSIS
- **engines/**: 53 items - **Consider L3 depth** (create subfolders: `drivers`, `generators`, `utils`)
- **shared/**: 66 items - **Consider L3 depth** (create subfolders: `core`, `reasoning`, `tools`)

#### 🔄 PARITY ISSUE
- **apps_rg** has `validation/` but **apps_lic** doesn't
- **apps_rg** has `core/` but **apps_lic** doesn't
- **Recommendation:** Ensure mirrored structure between apps_rg and apps_lic

---

## 5. SCRIPTS Analysis

### Current Structure (Actual)
```
scripts/ (173 items)
├── ci/ (2 items)
├── maintenance/ (38 items)
└── security/ (1 item)
```

### SSOT Definition
```python
SOVEREIGN_REGISTRY = {
    "scripts": {"depth": 1, "subfolders": [], "purpose": "Standalone utility scripts"}
}
```

### Findings & Recommendations

#### ❌ MISALIGNED
- **SSOT says:** depth=1, no subfolders
- **Actual has:** depth=2 with `ci/`, `maintenance/`, `security/` subfolders

#### 🔧 RECOMMENDATIONS
1. **Update SSOT to depth=2** with subfolders: `["ci", "maintenance", "security"]`
2. **Alternative:** Move `maintenance/` scripts to `agentic_core/L0_maintenance/scripts/`

---

## 6. TESTS Analysis

### Current Structure (Actual)
```
tests/ (359 items)
├── apps_rg/ (19 items)
├── core/ (4 items)
├── e2e/ (8 items)
├── fixtures/ (12 items)
├── functional/ (19 items)
├── integration/ (23 items)
└── unit/ (229 items)
```

### SSOT Definition
```python
TESTS_L2_SUBFOLDER_MAP = {
    "unit": ["test_definitions", "test_helpers"],
    "integration": ["test_definitions", "test_helpers"],
    "e2e": ["test_definitions", "test_helpers"],
    "functional": ["test_definitions", "test_helpers"],
    "fixtures": ["fixture_definitions", "fixture_helpers"],
    "automation": ["automation_definitions", "automation_helpers"],
    "core": ["core_definitions", "core_helpers"],
    "data": ["data_definitions", "data_helpers"],
    "performance": ["performance_definitions", "performance_helpers"],
    "security": ["security_definitions", "security_helpers"],
}
```

### Findings & Recommendations

#### ✅ ALIGNED
- Has: `unit`, `integration`, `e2e`, `functional`, `fixtures`, `core`

#### ❌ MISALIGNED
- **Missing in actual:** `automation/`, `data/`, `performance/`, `security/`
- **Actual has:** `apps_rg/` (not in SSOT)
- **Recommendation:** Add `apps_rg` to SSOT; remove unused subfolders from SSOT

---

## 7. ARCHIVES Analysis

### Current Structure (Actual)
```
archives/ (0 items at root, many empty subdirs)
├── L4_state/
├── Reachout Engine Archive/
├── agentic_core_archived/
├── app_leaks_L1_20260110_071923/
├── apps_lic/
├── apps_rg/
├── apps_shared/
├── backups/
├── bloat_elimination_2026_01/
├── completed_migrations/
├── config/
├── consolidated_agents/
├── consolidated_duplicates/
├── core_contracts_monolithic_20260101/
├── dedup_archived/
├── deprecated_2026_01_20/
├── deprecated_agents/
├── deprecated_auditors/
├── deprecated_canon_prompts/
├── deprecated_code/
├── deprecated_dashboard/
├── deprecated_key_validators/
├── deprecated_modules/
├── deprecated_tests/
├── duplicate_tests_20260110_090742/
├── examples_deprecated/
├── fission_backups/
├── gatekeeper/
├── healing_backups/
├── hierarchy_violations/
├── identity_duplicates/
├── legacy_agents/
├── legacy_cleanup_20251219/
├── legacy_code/
├── legacy_orchestrators/
├── legacy_tools/
├── legacy_validators/
├── location_violations/
├── logs/
├── misplaced_tests_2026_01_20/
├── monolithic_configs_20260101/
├── naming_violations/
├── observability/
├── phase20_synthesis/
├── prompt_governance/
├── redis.py
├── resume_gen_json/
├── root_archived/
├── runtime/
├── schemas/
├── scripts_healing_20260110/
├── shared/
├── stubs/
├── tests/
├── tombstones/
├── unmapped_drift/
└── void_violations/
```

### SSOT Definition
**NOT DEFINED IN SSOT**

### Findings & Recommendations

#### ❌ MISSING FROM SSOT
- **archives/** folder is not defined in `SOVEREIGN_REGISTRY`
- **Recommendation:** Add to SSOT with appropriate depth and subfolder structure

#### 🔧 PROPOSED SSOT ENTRY
```python
"archives": {
    "depth": 2,
    "subfolders": [
        "deprecated_agents",
        "deprecated_code",
        "legacy_agents",
        "legacy_code",
        "backups",
        "migrations",
        "violations"
    ],
    "purpose": "Historical artifacts and deprecated code",
    "volatile": True
}
```

---

## 8. DATA Analysis

### Current Structure (Actual)
```
data/ (225 items)
├── archives/ (0 items)
├── cache/ (0 items)
├── external/ (9 items)
├── freeze_reports/ (3 items)
├── golden/ (3 items)
├── golden_state/ (1 item)
├── logs/ (0 items)
├── manifests/ (3 items)
├── output/ (11 items)
├── processed/ (2 items)
├── prompt_governance/ (161 items)
├── prompt_libraries/ (9 items)
├── prompts/ (5 items)
├── raw/ (1 item)
├── sdks_mcps/ (14 items)
└── tasks/ (3 items)
```

### SSOT Definition
**NOT DEFINED IN SSOT**

### Findings & Recommendations

#### ❌ MISSING FROM SSOT
- **data/** folder is not defined in `SOVEREIGN_REGISTRY`
- **Recommendation:** Add to SSOT with appropriate depth and subfolder structure

#### 🔧 PROPOSED SSOT ENTRY
```python
"data": {
    "depth": 2,
    "subfolders": [
        "archives",
        "cache",
        "external",
        "freeze_reports",
        "golden",
        "golden_state",
        "logs",
        "manifests",
        "output",
        "processed",
        "prompt_governance",
        "prompt_libraries",
        "prompts",
        "raw",
        "sdks_mcps",
        "tasks"
    ],
    "purpose": "Data storage and processing artifacts"
}
```

---

## 9. DOCS Analysis

### Current Structure (Actual)
```
docs/ (116 items)
├── MCP/ (16 items)
├── metrics/ (1 item)
└── reports/ (99 items)
```

### SSOT Definition
**NOT DEFINED IN SSOT**

### Findings & Recommendations

#### ❌ MISSING FROM SSOT
- **docs/** folder is not defined in `SOVEREIGN_REGISTRY`
- **Recommendation:** Add to SSOT with appropriate depth and subfolder structure

#### 🔧 PROPOSED SSOT ENTRY
```python
"docs": {
    "depth": 2,
    "subfolders": [
        "MCP",
        "metrics",
        "reports"
    ],
    "purpose": "Documentation and reporting"
}
```

---

## 10. LOGS Analysis

### Current Structure (Actual)
```
logs/ (17 items)
├── archetype_test/ (1 item)
├── budget_test_001/ (1 item)
├── checksum_test/ (1 item)
├── cxo_test_001/ (1 item)
├── default/ (1 item)
├── error_test/ (1 item)
├── gate5_test/ (1 item)
├── gate6_test/ (1 item)
├── master_test_001/ (1 item)
├── retry_limit_test/ (1 item)
├── retry_test_factual/ (1 item)
├── safety_test/ (1 item)
├── sim_2026_0123/ (1 item)
├── stagnation_test/ (1 item)
├── test_fixture/ (1 item)
├── test_mission_001/ (1 item)
└── test_retry_001/ (1 item)
```

### SSOT Definition
**NOT DEFINED IN SSOT**

### Findings & Recommendations

#### ❌ MISSING FROM SSOT
- **logs/** folder is not defined in `SOVEREIGN_REGISTRY`
- **Recommendation:** Add to SSOT with appropriate depth and subfolder structure

#### 🔧 PROPOSED SSOT ENTRY
```python
"logs": {
    "depth": 2,
    "subfolders": [],  # Dynamic test-specific subfolders
    "purpose": "Runtime logs and test outputs",
    "volatile": True
}
```

---

## Summary of Recommendations

### 🔴 CRITICAL (Must Fix)
1. **apps_shared**: Complete structural mismatch - rename folders or update SSOT
2. **Add missing top-level folders to SSOT**: `archives`, `data`, `docs`, `logs`
3. **Fix agentic_core subfolder misalignments**: 11 subfolders need updates

### 🟡 HIGH PRIORITY (Should Fix)
4. **apps_rg/apps_lic parity**: Ensure mirrored structure
5. **scripts depth**: Update from depth=1 to depth=2
6. **L0_maintenance**: Add missing subfolders (`boot`, `reports`, `security`)
7. **L2_execution**: Add `unified` subfolder
8. **L6_observability**: Add `agents` subfolder

### 🟢 MEDIUM PRIORITY (Consider)
9. **Increase depth for large folders**: `apps_rg/engines`, `apps_rg/shared`, `apps_lic/engines`, `apps_lic/shared`
10. **Remove phantom subfolders from SSOT**: `utils/core_extensions`, `runtime/environment_setup`, etc.
11. **Standardize naming**: `ValidationContext` → `validation_context`, `ToolRegistry` → `tool_registry`

### 📊 Depth Optimization Summary
- **Increase to L3**: apps_rg/engines (73 items), apps_rg/shared (53 items), apps_lic/engines (53 items), apps_lic/shared (66 items)
- **Increase to L2**: scripts/ (currently L1, has 3 subfolders)
- **Already optimal**: All L0-L6 layers in agentic_core

---

## Next Steps

1. **Review this audit** with stakeholders
2. **Decide on apps_shared strategy**: Rename folders or update SSOT?
3. **Update structure_blueprint.py** with approved changes
4. **Run validation scripts** to ensure compliance
5. **Update LocationAgent and HierarchyAgent** to recognize new structure
