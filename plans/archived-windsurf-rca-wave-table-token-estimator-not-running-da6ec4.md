---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\rca-wave-table-token-estimator-not-running-da6ec4.md'
original_relative_path: 'rca-wave-table-token-estimator-not-running-da6ec4.md'
source_sha256: c2f206acb6da0ec3ff8f3789e6eb8f735698b24ee0bc9f5314bf48465063404d
recovered_status: LOST_RECOVERED
last_commit: '20f413ffbf5'
last_commit_date: '2026-04-01 14:39:03 -0400'
created_date: '2026-03-27'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Wave Table and Token Estimator Not Running at Top of Plan

**Date:** 2026-03-27  
**Severity:** HIGH - Systemic documentation standards violation  
**Status:** 🔍 INVESTIGATION COMPLETE - Root causes identified

## Executive Summary

The "wave table" and "token estimator" are not running at the top of plans because they are not executable components but documentation standards defined in `.windsurfrules §10`. The issue stems from a systemic gap between defined standards and enforcement mechanisms, affecting 862/868 plans with warnings and 6 plans with validation failures.

---

## Root Cause Analysis

### 1. Terminology Misunderstanding

**Issue:** "Wave table" and "token estimator" are not running services but documentation requirements.

- **Wave Table**: A mandatory markdown table at the top of execution plans (per §10.1)
- **Token Estimator**: A workflow using `ContextWindowEstimator` class (per §10.2)
- **Not Running**: These are documentation standards, not executable services

### 2. Standards Enforcement Gap

**Primary Cause:** CI validation deployed without grandfather clause for legacy plans.

**Evidence:**
- 862/868 plans have warnings for missing wave structure
- 6 plans completely invalid
- Legacy plans created before §10 standards (2026-03-01) lack required sections

### 3. Tooling Implementation Status

**Token Estimator Status:**
- ✅ Implemented: `agentic_core/planning/token_estimator.py` (759 lines)
- ✅ Test Coverage: 8 test files with comprehensive coverage
- ✅ Integration: Used by `tools/adg/capability_extractor.py`
- ❌ Not Running: Not invoked automatically during plan creation

**Wave Table Tools:**
- ✅ Implemented: `tools/add_wave_tables_to_legacy_plans.py`
- ✅ Detection Logic: Identifies execution plans needing wave tables
- ❌ Not Running: Bulk migration not executed

### 4. CI Validation State

**Current State:**
- CI gate active and failing on 6 plans
- 862 plans passing but with warnings
- Validation script: `tools/ci_validate_plans.py`
- Enforcement: `.windsurf/rules/.windsurfrules §10`

---

## Why Components Are "Not Running"

### Token Estimator Workflow

**Required Workflow (§10.2):**
```bash
# Run token optimization analysis
python tools/evidence/_run_token_optimizer_plan.py

# Run wave packing optimization  
python tools/adg/wave_packer.py
```

**Status:** Not executed during plan creation - manual step only.

### Wave Table Generation

**Tool Available:** `tools/add_wave_tables_to_legacy_plans.py`
- Supports `--dry-run` and `--execute` modes
- Detects execution plans vs RCA reports
- Generates standard wave table format

**Status:** Created but not executed on repository.

---

## Fix Implementation Plan

### Phase 1: Immediate Remediation (T0)

1. **Execute Wave Table Migration**
```bash
# Add wave tables to all execution plans
python tools/add_wave_tables_to_legacy_plans.py --type execution --dry-run
python tools/add_wave_tables_to_legacy_plans.py --type execution --execute
```

2. **Fix 6 Invalid Plans**
- `convergent_wave_plan_137_150.md` - Add missing Rules/Success Criteria
- `gap-remediation-phased-waves-2026.md` - Add wave table
- `dependency-reclassification-plan-8a2c4d.md` - Add wave table
- `semantic-gap-remediation-wave-plan-6cc20d.md` - Add Gap Register/Execution Plan
- `windsurf-plan-enforcement-rca-solution-8f9a1b.md` - Add Violation/Corrective Actions
- `convergent_wave_plan_101_150.md` - Add Success Criteria

### Phase 2: Token Estimator Integration (T1)

1. **Automate Token Estimation**
```bash
# Run token optimizer on all execution plans
python tools/evidence/_run_token_optimizer_plan.py --batch-mode

# Update wave tables with real token estimates
python tools/adg/wave_packer.py --update-all-plans
```

2. **Integrate with Plan Creation**
- Modify plan templates to include token estimation
- Add pre-commit hook for plan validation
- Update Windsurf skills to auto-generate wave tables

### Phase 3: Standards Hardening (T2)

1. **Plan Type Registry**
```yaml
# .windsurf/config/plan_types.yaml
execution:
  requires_wave_table: true
  requires_token_estimates: true
  required_sections: ["## Wave Structure", "## Rules", "## Success Criteria"]
  
rca:
  requires_wave_table: false
  requires_token_estimates: false
  required_sections: ["## Violation", "## Root Cause", "## Corrective Actions"]
```

2. **Smart Validation**
- Update `tools/validate_plan_format.py` with type awareness
- Add grandfather clause for pre-2026-03-01 plans
- Implement graduated validation (strict for new, lenient for legacy)

---

## Success Criteria

- [ ] 6 invalid plans fixed and passing CI
- [ ] Wave tables added to all execution plans
- [ ] Token estimates populated using ContextWindowEstimator
- [ ] CI validation pass rate ≥ 99%
- [ ] Automated token estimation workflow functional
- [ ] Plan type differentiation implemented

---

## Evidence

**Token Estimator Implementation:**
- File: `agentic_core/planning/token_estimator.py` (759 lines, fully implemented)
- Tests: 8 test files with comprehensive coverage
- Usage: Integrated into `tools/adg/capability_extractor.py`

**Wave Table Tool:**
- File: `tools/add_wave_tables_to_legacy_plans.py` (181 lines, ready to run)
- Logic: Distinguishes execution plans from RCA reports
- Output: Standard wave table format with token estimates

**CI Validation Report:**
- Current: 862/868 valid with warnings, 6 invalid
- Issue: Missing wave structure sections
- Location: `docs/reports/plan_validation_report.md`

---

## Status

🔍 **RCA COMPLETE** - Standards gap identified, not component failure  
⚡ **READY TO EXECUTE** - Tools implemented, need bulk migration  
✅ **PATH TO RESOLUTION** - 3-phase plan with clear success criteria
