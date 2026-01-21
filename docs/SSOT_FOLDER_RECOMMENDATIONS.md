# SSOT Folder Structure Recommendations Report

**Date:** 2026-01-19
**File:** `agentic_core/L5_safety/validators/structure_blueprint.py`
**Scope:** Review of SOVEREIGN_REGISTRY depth definitions and folder structure

---

## Executive Summary

The current SSOT defines a **rigid depth=3** rule for `agentic_core` that does not reflect the actual repository structure. Analysis of 1,306 Python files reveals:

- **97.5%** of files are at depth 3 (compliant)
- **2.5%** of files are at depth 2 (32 files - currently flagged as violations)
- Several L3 subfolders have grown to 100+ files, warranting L4 depth allowance
- Legacy/duplicate folders exist that should be consolidated

---

## Current SSOT Definitions

```python
SOVEREIGN_REGISTRY = {
    'agentic_core': {'depth': 3, 'subfolders': [...]},
    'apps_rg': {'depth': 3, 'subfolders': [...]},
    'apps_lic': {'depth': 3, 'subfolders': [...]},
    'apps_shared': {'depth': 2, 'subfolders': [...]},
    'tests': {'depth': 2, 'subfolders': [...]},
}
```

---

## Findings

### 1. Depth Distribution Analysis

| Root Folder | SSOT Depth | Actual Depth Range | Files | Status |
|-------------|------------|-------------------|-------|--------|
| `agentic_core` | 3 | 2-3 | 1,306 | ⚠️ 32 files at depth 2 |
| `apps_rg` | 3 | 2 | 14 | ⚠️ All files at depth 2 |
| `apps_lic` | 3 | 2 | 17 | ⚠️ All files at depth 2 |
| `apps_shared` | 2 | 2 | 12 | ✅ Compliant |
| `tests` | 2 | 1-3 | 29 | ⚠️ 11 files at root |
| `scripts` | N/A | 1 | 26 | ❌ Not in SSOT |

### 2. Files at Depth 2 (Shallow Violations)

32 files in `agentic_core` are at depth 2 instead of depth 3:

| Folder | Files | Examples |
|--------|-------|----------|
| `observability/` | 16 | `SovereignBaseAgent.py`, `telemetry.py` |
| `prompt_governance/` | 10 | `PromptRegistryAgent.py`, `renderer.py` |
| `L3_orchestration/` | 2 | `unified_orchestrator.py`, `UnifiedOrchestratorAgent.py` |
| `L6_observability/` | 2 | `BenchmarkingAgent.py`, `L6ObservabilityBaseAgent.py` |
| `utils/` | 2 | `sovereign_index.py`, `networking.py` |

### 3. Large L3 Subfolders (Candidates for L4 Depth)

| L3 Folder | Files | Recommendation |
|-----------|-------|----------------|
| `L0_maintenance/scripts` | 444 | ✅ Already in L4_APPROVED_FOLDERS |
| `L1_cognition/thought_engine` | 161 | ✅ Already in L4_APPROVED_FOLDERS |
| `L5_safety/validators` | 135 | ⚠️ **Add to L4_APPROVED_FOLDERS** |
| `L2_execution/ToolRegistry` | 95 | ✅ Already in L4_APPROVED_FOLDERS |
| `utils/core_extensions` | 78 | ✅ Already in L4_APPROVED_FOLDERS |
| `L3_orchestration/workflow_engines` | 57 | ✅ Already in L4_APPROVED_FOLDERS |
| `schemas/models` | 42 | ⚠️ **Consider L4 promotion** |
| `L5_safety/guardrails` | 42 | ✅ Already in L4_APPROVED_FOLDERS |
| `L4_state/ValidationContext` | 41 | ⚠️ **Consider L4 promotion** |
| `L2_execution/mcp` | 26 | ⚠️ **Consider L4 promotion** |
| `L5_safety/gravity` | 22 | ⚠️ **Consider L4 promotion** |

### 4. Non-Standard Folders (Not in SSOT)

| Folder | Files | Issue |
|--------|-------|-------|
| `observability/` | 16 | Duplicate of `L6_observability/` |
| `common/` | 2 | Not in SOVEREIGN_REGISTRY subfolders |
| `L4_resilience/` | 0 | Empty, should be removed |
| `scripts/` (root) | 26 | Not in SOVEREIGN_REGISTRY |

### 5. Apps Folder Structure Mismatch

| Folder | SSOT Depth | Actual | Issue |
|--------|------------|--------|-------|
| `apps_rg` | 3 | 2 | All 14 files in `engines/` at depth 2 |
| `apps_lic` | 3 | 2 | All 17 files in `engines/` at depth 2 |

---

## Recommendations

### Priority 1: Update SOVEREIGN_REGISTRY Depths

```python
# BEFORE
'agentic_core': {'depth': 3, ...}
'apps_rg': {'depth': 3, ...}
'apps_lic': {'depth': 3, ...}

# AFTER - Introduce variable depth concept
'agentic_core': {
    'depth': 3,
    'variable_depth_subfolders': [
        'observability',      # depth 2 allowed
        'prompt_governance',  # depth 2 allowed
        'L3_orchestration',   # depth 2 allowed (unified_orchestrator.py)
        'L6_observability',   # depth 2 allowed (base agents)
        'utils',              # depth 2 allowed (sovereign_index.py)
    ],
    ...
}
'apps_rg': {'depth': 2, ...}  # Change from 3 to 2
'apps_lic': {'depth': 2, ...}  # Change from 3 to 2
```

### Priority 2: Add Missing L4 Approved Folders

```python
L4_APPROVED_FOLDERS: Set[str] = {
    # Existing
    'agentic_core/L6_observability/dashboards',
    'agentic_core/L0_maintenance/scripts',
    'agentic_core/L3_orchestration/workflow_engines',
    'agentic_core/L1_cognition/thought_engine',
    'agentic_core/L5_safety/guardrails',
    'agentic_core/L2_execution/ToolRegistry',
    'agentic_core/utils/core_extensions',

    # NEW - Add these
    'agentic_core/L5_safety/validators',      # 135 files
    'agentic_core/schemas/models',            # 42 files
    'agentic_core/L4_state/ValidationContext', # 41 files
    'agentic_core/L2_execution/mcp',          # 26 files
    'agentic_core/L5_safety/gravity',         # 22 files
}
```

### Priority 3: Add `scripts` to SOVEREIGN_REGISTRY

```python
SOVEREIGN_REGISTRY = {
    ...
    'scripts': {
        'depth': 1,  # Files directly in scripts/
        'subfolders': [],
        'purpose': 'Standalone utility scripts'
    },
}
```

### Priority 4: Consolidate Duplicate Folders

| Action | Source | Target | Files |
|--------|--------|--------|-------|
| **MERGE** | `observability/` | `L6_observability/` | 16 files |
| **MERGE** | `common/healing/` | `L5_safety/validators/` | 2 files |
| **DELETE** | `L4_resilience/` | N/A | 0 files (empty) |

### Priority 5: Update VARIABLE_DEPTH_SUBFOLDERS in LocationAgent

The existing `VARIABLE_DEPTH_SUBFOLDERS` in `LocationAgent.py` should be synchronized with SSOT:

```python
VARIABLE_DEPTH_SUBFOLDERS: frozenset = frozenset({
    'utils',              # utils/core_extensions/* has depth 4
    'config',             # config/blueprint_sovereign/* has depth 4
    'common',             # common/healing/* has depth 4
    'observability',      # observability/* can have variable depth
    'L6_observability',   # dashboards have variable depth
    'L3_orchestration',   # unified_orchestrator.py at depth 2
    'L0_maintenance',     # scripts at variable depth
    'L1_cognition',       # thought_engine at variable depth
    'L2_execution',       # mcp at variable depth
    'L4_state',           # ValidationContext at variable depth
    'L5_safety',          # validators/guardrails at variable depth
    'schemas',            # models at variable depth
    'prompt_governance',  # version_registry at variable depth
})
```

---

## Implementation Plan

### Phase 1: SSOT Updates (Low Risk)

1. Update `apps_rg` and `apps_lic` depth from 3 to 2
2. Add `scripts` to SOVEREIGN_REGISTRY
3. Add missing folders to L4_APPROVED_FOLDERS
4. Document VARIABLE_DEPTH_SUBFOLDERS in structure_blueprint.py

**Estimated Impact:** 0 file moves, configuration only

### Phase 2: Folder Consolidation (Medium Risk)

1. Merge `observability/` → `L6_observability/agents/`
2. Merge `common/healing/` → `L5_safety/validators/`
3. Delete empty `L4_resilience/`
4. Update all imports referencing moved files

**Estimated Impact:** 18 file moves, import updates required

### Phase 3: Depth Normalization (Optional)

1. Move 32 depth-2 files to depth-3 locations OR
2. Formally approve depth-2 for specific subfolders

**Estimated Impact:** 0-32 file moves depending on approach

---

## Risk Assessment

| Change | Risk | Mitigation |
|--------|------|------------|
| Depth changes | LOW | No file moves, config only |
| L4 folder additions | LOW | Expands allowed paths |
| Folder consolidation | MEDIUM | Requires import updates |
| Depth normalization | HIGH | Many file moves, import breaks |

---

## Recommended Approach

**Option A: Flexible Depth (Recommended)**
- Keep files where they are
- Update SSOT to reflect reality
- Use VARIABLE_DEPTH_SUBFOLDERS for exemptions

**Option B: Strict Depth Enforcement**
- Move all 32 depth-2 files to depth-3
- High risk of import breakage
- Not recommended without comprehensive testing

---

## Files to Modify

1. `agentic_core/L5_safety/validators/structure_blueprint.py`
   - Update SOVEREIGN_REGISTRY
   - Add L4_APPROVED_FOLDERS entries
   - Add VARIABLE_DEPTH_SUBFOLDERS constant

2. `agentic_core/L5_safety/validators/LocationAgent.py`
   - Sync VARIABLE_DEPTH_SUBFOLDERS with SSOT

3. `agentic_core/L5_safety/validators/HierarchyAgent.py`
   - Add VARIABLE_DEPTH_SUBFOLDERS exemption check

---

## Appendix: Full File Inventory

### Depth 2 Files (32 total)

```
agentic_core/L3_orchestration/UnifiedOrchestratorAgent.py
agentic_core/L3_orchestration/unified_orchestrator.py
agentic_core/L6_observability/BenchmarkingAgent.py
agentic_core/L6_observability/L6ObservabilityBaseAgent.py
agentic_core/observability/append_windsurf_log.py
agentic_core/observability/cache_metrics.py
agentic_core/observability/DocstringComplianceAgent.py
agentic_core/observability/dspy_optimizer.py
agentic_core/observability/healing_invocation_metrics.py
agentic_core/observability/LoggingObservabilityGuardrail.py
agentic_core/observability/mission_metrics.py
agentic_core/observability/runtime_core_subatomic_swarm.py
agentic_core/observability/runtime_shared_observability_clients.py
agentic_core/observability/secure_logger.py
agentic_core/observability/SovereignBaseAgent.py
agentic_core/observability/telemetry.py
agentic_core/observability/TelemetryManagerAgent.py
agentic_core/observability/test_phase1_phase2_telemetry.py
agentic_core/observability/test_root_ssot_enforcement.py
agentic_core/observability/utilities_fix_print_statements.py
agentic_core/prompt_governance/comprehensive_dashboard_tests.py
agentic_core/prompt_governance/conversational_repair.py
agentic_core/prompt_governance/pitch_generator.py
agentic_core/prompt_governance/PromptRegistryAgent.py
agentic_core/prompt_governance/prompt_assembler.py
agentic_core/prompt_governance/prompt_optimizer.py
agentic_core/prompt_governance/renderer.py
agentic_core/prompt_governance/sovereign_prompt_constitution.py
agentic_core/prompt_governance/sovereign_prompt_renderer.py
agentic_core/prompt_governance/test_red_teaming_agents.py
agentic_core/utils/networking.py
agentic_core/utils/sovereign_index.py
```

### L3 Subfolder File Counts

```
L0_maintenance/scripts: 444 files
L1_cognition/thought_engine: 161 files
L5_safety/validators: 135 files
L2_execution/ToolRegistry: 95 files
utils/core_extensions: 78 files
L3_orchestration/workflow_engines: 57 files
schemas/models: 42 files
L5_safety/guardrails: 42 files
L4_state/ValidationContext: 41 files
L2_execution/mcp: 26 files
L5_safety/gravity: 22 files
config/blueprint_sovereign: 20 files
runtime/shared_runtime: 17 files
prompt_governance/meta_prompts: 12 files
```
