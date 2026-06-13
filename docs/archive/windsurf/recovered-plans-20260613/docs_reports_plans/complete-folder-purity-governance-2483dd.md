# Complete Folder Purity Governance Plan

This plan extends folder purity governance to ALL folders under agentic_core (excluding __pycache), ensuring every folder has strict naming rules and execute_ssot can heal violations automatically.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State
- **Governed folders**: 10 folders (config, dashboards, enforcement, engines, reasoning, scripts, tools, types, utils, validators)
- **Ungoverned folders**: 20 folders that need rules added
- **Total violations**: 222+ across all folders

## Phase 1: Add Rules for Ungoverned Folders (1 wave)

### Wave 1.1: Define FOLDER_PURITY_RULES for all 20 ungoverned folders
**Target**: Add naming patterns for all currently ungoverned folders

**New folder rules to add:**
```python
# Core infrastructure folders
"agent_configs": [r".*_config\.py$", r".*_spec\.py$"]
"core": [r".*_core\.py$", r".*\.py$"]  # Allow any for core files
"exceptions": [r".*Error\.py$", r".*Exception\.py$"]

# Knowledge and learning folders
"document_loaders": [r".*_loader\.py$", r".*_reader\.py$"]
"static_index": [r".*_index\.py$", r".*_indexer\.py$"]

# Runtime and execution folders
"caching": [r".*_cache\.py$", r".*_cacher\.py$"]
"memory": [r".*_memory\.py$", r".*_store\.py$"]
"engine": [r".*_engine\.py$", r".*_driver\.py$"]
"healers": [r".*_healer\.py$", r".*Healer\.py$"]

# Meta and control folders
"meta_control": [r".*_control\.py$", r".*_controller\.py$", r".*_meta\.py$"]
"policy": [r".*_policy\.py$", r".*Policy\.py$"]

# Prompt governance folders
"meta_prompts": [r".*_prompt\.py$", r".*_template\.py$"]
"templates": [r".*_template\.py$", r".*Template\.py$"]
"optimization": [r".*_optimizer\.py$", r".*Optimizer\.py$"]
"registry": [r".*_registry\.py$", r".*Registry\.py$"]
"validation": [r".*_validator\.py$", r".*Validator\.py$"]

# Security and monitoring
"security": [r".*_security\.py$", r".*Security\.py$"]
"golden_evaluation": [r".*_eval\.py$", r".*_evaluation\.py$"]

# Special global folders
"mixins": [r".*_mixin\.py$", r".*Mixin\.py$"]  # Special case for global mixins
"healing": [r".*_healing\.py$", r".*Healing\.py$"]
```

## Phase 2: Update Test Infrastructure (1 wave)

### Wave 2.1: Extend _find_governed_folders for global folders
**Target**: Update test to find folders at agentic_core root level

**Changes needed:**
- Modify `_find_governed_folders()` to also check `agentic_core/{folder_name}` directly
- This ensures global folders like `mixins/`, `core/`, `runtime/` are included

## Phase 3: Update FileClassificationAgent (1 wave)

### Wave 3.1: Extend _enforce_folder_purity for global folders
**Target**: Ensure agent can compute target paths for global folders

**Changes needed:**
- Update `_enforce_folder_purity()` to handle global folders (not under L*_ layers)
- Add logic to detect when file is in global folder and compute correct target

## Phase 4: Configure Execute_SSOT (1 wave)

### Wave 4.1: Enable full scope healing
**Target**: Remove dry-run restrictions in execute_ssot.py

**Changes needed:**
- Update Phase 2.5 in execute_ssot.py to use `execute=True`
- Remove `validate_only=True, dry_run=True` from healing phase

## Phase 5: Full Remediation Execution (1 wave)

### Wave 5.1: Run execute_ssot and verify all violations fixed
**Target**: Execute the complete pipeline and verify zero violations

**Steps:**
1. Run: `python -m agentic_core.L0_routing.scripts.execute_ssot.py --territory all`
2. Verify: All folder purity violations eliminated
3. Verify: `python -m pytest -q tests/enforcement/test_folder_purity_invariants.py` passes
4. Verify: `pre-commit run --all-files` passes

## Implementation Details

### File Changes Required:
1. **classification.py**: Add 20 new folder rules to FOLDER_PURITY_RULES
2. **test_folder_purity_invariants.py**: Update _find_governed_folders for global folders
3. **FileClassificationAgent.py**: Update _enforce_folder_purity for global folder routing
4. **execute_ssot.py**: Enable actual healing in Phase 2.5

### Special Considerations:
- **mixins folder**: Allow _mixin.py suffix (special global folder)
- **core folder**: Permissive pattern to allow core infrastructure files
- **exceptions folder**: Only Error/Exception suffixes
- **Global folders**: Need special routing logic since they're not under L*_ layers

## Success Criteria
- All 30+ folders under agentic_core have governance rules
- execute_ssot.py automatically fixes all violations
- Zero folder purity violations in test suite
- Full coverage of agentic_core folder structure

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

