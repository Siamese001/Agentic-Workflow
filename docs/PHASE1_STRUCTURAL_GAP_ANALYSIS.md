# Phase 1: Structural Gap Analysis

## Current vs Required Directory Structure

### Level 0: Root Directory Analysis

**Current Root Contents**:
```
✅ agentic_core/          (Required)
✅ apps/                  (Required)
✅ prompt_governance/     (Required)
✅ observability/         (Required)
✅ schemas/               (Required)
✅ tests/                 (Required)
✅ runtime/               (Required)
❌ .git/                  (Forbidden - should not exist in validation)
❌ .mypy_cache/           (Forbidden)
❌ .pytest_cache/         (Forbidden)
❌ .ruff_cache/           (Forbidden)
❌ .vscode/               (Forbidden)
❌ *.md files             (Forbidden - should not be in root)
❌ comprehensive_validation.py (Forbidden)
❌ windsurf_rules/        (Forbidden)
❌ Other config files     (Forbidden)
```

**Issues Identified**:
- `root_contains_only_allowed_folders`: ❌ **FAILING** - Multiple forbidden items
- `no_extra_items_in_root`: ❌ **FAILING** - 15+ extra items
- `root_exists`: ✅ **PASSING** - Root directory exists
- `root_name_correct`: ✅ **PASSING** - Assuming correct name

---

### Level 1: Top-Level Directory Analysis

**Required Directories Status**:
```
✅ agentic_core/          (Present - 223 items)
✅ apps/                  (Present - 8 items)
✅ prompt_governance/     (Present - 30 items)
✅ observability/         (Present - 7 items)
✅ schemas/               (Present - 12 items)
✅ tests/                 (Present - 259 items)
✅ runtime/               (Present - 37 items)
❌ deployment/            (Extra - not in allowed list)
❌ evaluation/            (Extra - not in allowed list)
❌ mcp/                   (Extra - not in allowed list)
❌ safety/                (Extra - not in allowed list)
❌ config/                (Extra - not in allowed list)
```

**Issues Identified**:
- `no_extra_level1_directories`: ❌ **FAILING** - 5 extra directories
- All required directories are present ✅

---

### Level 2: Subdirectory Structure Analysis

#### agentic_core/ Structure Requirements
**Required**: Only L1-L5 folders allowed
```
Current agentic_core/ contents:
✅ l1_planning/           (Required)
✅ l2_execution/         (Required)
✅ l3_orchestration/      (Required)
✅ l4_memory_state/       (Required)
✅ l5_safety/             (Required)
❌ [Additional items?]    (Need to verify)
```

#### apps/ Structure Requirements
**Required**: Only engine folders allowed
```
Current apps/ contents:
❓ [Need to examine]      (Should only contain resume/outreach engines)
```

#### prompt_governance/ Structure Requirements
**Required**: Specific subfolders only
```
Current prompt_governance/ contents:
✅ prompts/               (Likely correct)
❓ [Need to examine]      (Check for forbidden subfolders)
```

#### observability/ Structure Requirements
**Required**: trace, metrics, logs, cost only
```
Current observability/ contents:
❓ [Need to examine]      (Should only contain trace/metrics/logs/cost)
```

#### schemas/ Structure Requirements
**Required**: Layer subschemas only
```
Current schemas/ contents:
❓ [Need to examine]      (Should only contain layer-specific schemas)
```

#### tests/ Structure Requirements
**Required**: Layer directories only
```
Current tests/ contents:
❓ [Need to examine]      (Should mirror agentic_core structure)
```

#### runtime/ Structure Requirements
**Required**: cache folder only
```
Current runtime/ contents:
❓ [Need to examine]      (Should primarily contain cache/)
```

---

### Level 3: Engine and Layer-Specific Structure

#### Critical Issues Identified:
1. **agentic_core l2_execution engines** - Need resume/outreach engine structure
2. **agentic_core l3_orchestration engines** - Need engine-specific orchestration
3. **agentic_core l4_memory_providers** - Need provider structure
5. **agentic_core l5_safety** - Need filters/policies/validators structure
6. **apps engines** - Need resume/outreach adapters/pipelines
7. **tests layer structure** - Need comprehensive test tree mirroring

---

### Level 4: File Placement Requirements

**Critical Rules**:
- Only files allowed at level 4 (no directories)
- Specific file locations for each engine/layer
- No cross-layer file placement

---

### Level 5: Depth Restrictions

**Requirements**:
- No level 5 structure should exist
- Maximum depth of 4 levels

---

## 🚨 IMMEDIATE ACTIONS REQUIRED

### 1. Root Directory Cleanup (Priority 1)
**Remove from root**:
- All `.md` files (move to docs/ or remove)
- `comprehensive_validation.py` (move to scripts/)
- `windsurf_rules/` (move to config/)
- All cache directories (`.mypy_cache`, `.pytest_cache`, `.ruff_cache`)
- `.vscode/` (move to config/ or remove)
- Other config files (move to config/)

### 2. Level 1 Directory Restructuring (Priority 2)
**Move/Remove extra directories**:
- `deployment/` → move to `apps/` or remove
- `evaluation/` → move to `apps/` or integrate elsewhere
- `mcp/` → move to `agentic_core/l2_execution/tools/mcp/`
- `safety/` → move to `agentic_core/l5_safety/`
- `config/` → move to root as allowed folder or integrate

### 3. Level 2+ Structure Validation (Priority 3)
**Verify and fix**:
- agentic_core subdirectory compliance
- apps engine structure
- prompt_governance subfolder restrictions
- observability folder restrictions
- schemas layer structure
- tests layer mirroring
- runtime cache structure

---

## 📊 STRUCTURAL COMPLIANCE PROJECTION

**Current Estimated Pass Rate**: 0/30+ keys (0%)
**After Root Cleanup**: ~5/30+ keys (17%)
**After Level 1 Fix**: ~10/30+ keys (33%)
**After Full Restructure**: ~25/30+ keys (83%)

---

## 🎯 IMPLEMENTATION PLAN

### Step 1: Root Directory Cleanup
1. Create `docs/` directory for documentation
2. Create `scripts/` directory for validation scripts
3. Create `config/` directory for configuration
4. Move all forbidden items to appropriate locations
5. Remove unnecessary cache directories

### Step 2: Directory Restructuring
1. Analyze each level 1 directory's contents
2. Move extra directories to appropriate locations
3. Ensure only allowed directories exist at each level

### Step 3: Level 2+ Structure Validation
1. Verify agentic_core L1-L5 structure
2. Implement proper apps engine structure
3. Fix prompt_governance subfolder compliance
4. Ensure observability folder restrictions
5. Validate schemas layer structure
6. Implement tests layer mirroring
7. Fix runtime cache structure

### Step 4: Validation Script Update
1. Update comprehensive_validation.py for new schema
2. Implement tree_levels validation functions
3. Test each structural requirement

---

## 🚀 NEXT STEPS

1. **Immediate**: Start with root directory cleanup
2. **Then**: Level 1 directory restructuring
3. **Finally**: Level 2+ structure validation
4. **Throughout**: Update validation script to measure progress

This analysis provides the foundation for Phase 1 implementation with clear priorities and measurable outcomes.
