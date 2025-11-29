# File Reorganization Plan

## Current Issues Identified

### 1. Root Level Files That Need Relocation
- `demo_outreach_engine.py` → `outreach_engine/demo.py`
- `demo_resume_generation.py` → `resume_engine/demo.py`
- `test_*.py` files → `tests/` folder
- Documentation files → `docs/` folder

### 2. Empty Root Level Folders to Remove
- `l1/`, `l2/`, `l3/`, `l4/`, `l5/` (empty at root)
- `config/`, `core/`, `eval/`, `infra/`, `meta/`, `monitoring/`, `orchestration/`, `providers/`, `tools/` (empty)

### 3. Naming Convention Enforcement
**Resume Engine Files (rg_ prefix):**
- ✅ Already properly named: `rg_k1_extract.py`, `rg_k2_clean.py`, etc.
- ✅ `rg_orchestrator.py`, `rg_planner.py`

**Outreach Engine Files (lic_ prefix):**
- ✅ Already properly named in L1-L5: `lic_*_planner.py`
- ❌ Root level files need renaming

### 4. Duplicates to Remove
- Multiple demo files
- Duplicate documentation
- Redundant test files

## Reorganization Steps

### Phase 1: Move Root Level Files
1. Move demo files to appropriate engine folders
2. Move test files to tests/ folder
3. Move documentation to docs/ folder
4. Move configuration files to shared_config/

### Phase 2: Remove Empty Folders
1. Remove empty L1-L5 folders at root
2. Remove other empty utility folders

### Phase 3: Update Imports
1. Update all import statements to reflect new paths
2. Update __init__.py files
3. Update configuration files

### Phase 4: Clean Up Duplicates
1. Identify duplicate files by content comparison
2. Remove redundant copies
3. Update references to remaining files

## Target Structure

```
Agentic_Workflow-10_11/
├── outreach_engine/
│   ├── l1/ (lic_ prefixed files)
│   ├── l2/ (lic_ prefixed files)
│   ├── l3/ (lic_ prefixed files)
│   ├── l4/ (lic_ prefixed files)
│   ├── l5/ (lic_ prefixed files)
│   ├── enhancements/ (already properly organized)
│   ├── demo.py
│   └── ...
├── resume_engine/
│   ├── l1/ (rg_ prefixed files)
│   ├── l2/ (rg_ prefixed files)
│   ├── l3/ (rg_ prefixed files)
│   ├── l4/ (rg_ prefixed files)
│   ├── l5/ (rg_ prefixed files)
│   ├── demo.py
│   └── ...
├── tests/
├── docs/
├── shared_config/
└── [project level files only]
```

## Import Updates Required

### Files That Need Import Updates
- All test files
- Demo files
- Configuration files
- Any files that import from moved locations

### Risk Mitigation
1. Create backup before moving files
2. Update imports systematically
3. Test imports after each phase
4. Keep enhancement system intact (already properly organized)
