---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\execute-ssot-folder-purity-hardening-2483dd.md'
original_relative_path: 'execute-ssot-folder-purity-hardening-2483dd.md'
source_sha256: a80ae5eb778fd5ae35208a867f83290ba3f46706073b124458b067a8456eec68
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Execute_SSOT Folder Purity Hardening Plan

This plan hardens the execute_ssot.py pipeline and FileClassificationAgent to automatically fix all 222 folder purity violations when run, without any manual file changes.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current Architecture
- `execute_ssot.py` → Phase 2.5 calls `FileClassificationAgent.heal_repository()`
- `FileClassificationAgent` uses `_enforce_folder_purity()` to detect and fix violations
- The agent already has logic to move/rename files but needs hardening for apps_* support

## Phase 1: Fix FileClassificationAgent Apps_* Support (1 wave)

### Wave 1.1: Harden _enforce_folder_purity for apps_*
**Target**: Ensure FileClassificationAgent can compute target paths for apps_* folders
- Already fixed in previous commit (f6254a0f2): Added apps_* root detection
- Added fail-loud error when target_path cannot be computed
- This enables the agent to heal apps_* folders automatically

## Phase 2: Update Folder Purity Rules (1 wave)

### Wave 2.1: Remove _mixin.py from utils allowed patterns
**Target**: Fix utils folder rule per user feedback
- Already done: Removed `r".*_mixin\.py$"` from utils patterns
- This ensures mixin files are properly routed

## Phase 3: Configure Execute_SSOT for Full Remediation (1 wave)

### Wave 3.1: Enable full scope healing
**Target**: Configure execute_ssot.py to heal all folders, not just detect
- Update Phase 2.5 execution plan to run `heal_repository` with `execute=True`
- Remove `validate_only=True, dry_run=True` from early detection phase
- Keep early detection in Phase 1 for reporting, but enable actual healing in Phase 2.5

## Phase 4: Test Execution (1 wave)

### Wave 4.1: Run execute_ssot.py and verify results
**Target**: Execute the hardened pipeline and verify all violations are fixed
- Run: `python -m agentic_core.L0_routing.scripts.execute_ssot.py --territory all`
- Verify: All 222 violations are automatically fixed
- Verify: `python -m pytest -q tests/enforcement/test_folder_purity_invariants.py` passes
- Verify: `pre-commit run --all-files` passes

## Key Changes Required

### 1. FileClassificationAgent.py
- ✅ Already fixed: apps_* root detection in `_enforce_folder_purity()`
- ✅ Already fixed: fail-loud when target_path is None

### 2. classification.py
- ✅ Already fixed: removed _mixin.py from utils patterns

### 3. execute_ssot.py
- Update Phase 2.5 to remove `validate_only=True, dry_run=True`
- This will enable actual healing instead of just detection

## Execution Flow
1. **Phase 1** (Discovery): FileClassificationAgent detects violations (dry run)
2. **Phase 2** (Reconciliation): Other agents fix drift
3. **Phase 2.5** (Structural Alignment): FileClassificationAgent heals folder purity
4. **Phase 3+** (Validation): Other agents validate the healed structure

## Benefits
- No manual file changes required
- All 222 violations fixed automatically
- Deterministic, repeatable process
- Uses existing hardened infrastructure

## Success Criteria
- `execute_ssot.py` runs without errors
- All folder purity violations eliminated
- Tests pass with zero failures
- No manual intervention required

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

