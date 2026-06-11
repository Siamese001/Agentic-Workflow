---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg-repair-scripts-inventory-20260406.md'
original_relative_path: 'adg-repair-scripts-inventory-20260406.md'
source_sha256: 9c247d22338459de070b0576537e64ce13566e4eee5f19caa5a40c5e2be2e460
recovered_status: LOST_RECOVERED
last_commit: '963915cf640'
last_commit_date: '2026-04-06 22:45:14 -0400'
created_date: '2026-04-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Repair Scripts Inventory and Gap Analysis

**Date:** 2026-04-06  
**Scope:** All ADG repair scripts and enhancement needs

---

## Current Repair Scripts Inventory

### 1. Core Repair Framework (`tools/adg/repair/`)

| Script | Purpose | Status |
|--------|---------|--------|
| `repair_orchestrator.py` | Main orchestration class for coordinating repairs | ✅ Active |
| `rule_engine.py` | Rule matching engine | ✅ Active |
| `execution_engine.py` | Fix execution engine | ✅ Active |
| `base_rule.py` | Base class for repair rules | ✅ Active |
| `types.py` | Type definitions (Deficiency, FixResult, etc.) | ✅ Active |
| `git_integration.py` | Git integration for rollback support | ✅ Active |
| `sqlite_analyzer.py` | SQLite analyzer for detecting deficiencies from DB | ✅ Active |

### 2. Repair Rules (`tools/adg/repair/rules/`)

| Rule | Issue Type | Fix Category | Status |
|------|-----------|--------------|--------|
| `fix_layer_assignment.py` | unknown_layer, unknown_layer_inferrable | AUTO_FIX | ✅ Active |
| `fix_guardian_format.py` | guardian_format, non_canonical_guardian | AUTO_FIX | ✅ Active |
| `fix_import_order.py` | import_order | AUTO_FIX | ✅ Active |
| `fix_missing_all.py` | missing_all | AUTO_FIX | ✅ Active |
| `fix_missing_typing.py` | missing_typing_imports | AUTO_FIX | ✅ Active |
| `fix_unused_imports.py` | unused_imports | AUTO_FIX | ✅ Active |
| `fix_docstring_placeholder.py` | docstring_placeholder | AUTO_FIX | ✅ Active |

### 3. Standalone Repair Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| `adg_repair.py` | CLI entry point for repair orchestrator | ✅ Active |
| `adg_antipattern_fixer.py` | Fixes guardian comment format violations | ✅ Active |
| `p1_docstring_repair.py` | Repairs P1 emit calls in docstrings | ✅ Active |
| `p1_fallback_wirer.py` | Adds P1 emit calls to files lacking them | ✅ Active |
| `auto_fix_p1_p2.py` | Auto-fix script for P1/P2 violations | ✅ NEW |

### 4. Historical/Specific Fix Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| `fix_layer_gravity_violations.py` | Creates L_CONTRACTS layer for cross-layer interfaces | ⚠️ Historical |
| `adg_1653_*.py` | Specific historical fixes | ⚠️ Archived |
| `adg_layer_annotation_fix.py` | Layer annotation fixes | ⚠️ Historical |

---

## Gap Analysis

### Critical Gaps

#### Gap 1: P2 Exception Antipattern Auto-Fix Rules
**Current State:** No repair rules for P2 exception antipatterns
- `silent_exception_swallow`
- `broad_exception_catch`
- `log_and_swallow`
- `return_none_swallow`

**Impact:** 3924 P2 antipatterns detected but no automated fixes available

**Needed Enhancement:** Create repair rules for P2 antipatterns:
- `fix_exception_swallow.py` - Add logging to silent swallows
- `fix_broad_exception_catch.py` - Narrow to specific exceptions where possible
- `fix_return_none_swallow.py` - Re-raise or add context instead of returning None

**Priority:** HIGH - P2 is now blocking ADG generation

---

#### Gap 2: P1 Layer Violation Auto-Fix Rules
**Current State:** No repair rules for P1 layer violations
- `violates` edges (layer violations)
- `in_cycle` edges (circular imports)
- `dynamic_exec` edges (dynamic execution)

**Impact:** 1 P1 violation detected, only manual exemption possible

**Needed Enhancement:** Create repair rules for P1 violations:
- `fix_layer_violation.py` - Add guardian exemptions for known-safe patterns
- `fix_circular_import.py` - Refactor to break cycles where possible
- `fix_dynamic_exec.py` - Replace with static imports where possible

**Priority:** HIGH - P1 is blocking ADG generation

**Note:** The `auto_fix_p1_p2.py` script was created but uses a different approach (direct SQLite queries) instead of the repair orchestrator framework.

---

#### Gap 3: SQLite Analyzer Not Integrated with Repair Orchestrator
**Current State:** `sqlite_analyzer.py` exists but is not used by `repair_orchestrator.py`

**Impact:** Repair orchestrator only parses JSON reports, missing SQLite-only deficiencies (P1/P2 violations)

**Needed Enhancement:** Integrate `sqlite_analyzer.py` into `repair_orchestrator.py`:
- Call SQLite analyzer during deficiency detection
- Convert SQLite query results to `Deficiency` objects
- Enable P1/P2 repair through orchestrator framework

**Priority:** HIGH - Unifies repair infrastructure

---

### Medium Gaps

#### Gap 4: Missing Code Quality Repair Rules
**Current State:** No rules for:
- Dead code removal
- Duplicate code detection
- Long function refactoring
- Complex cyclomatic complexity

**Needed Enhancement:** Create repair rules:
- `fix_dead_code.py` - Remove unused functions/classes
- `fix_duplicate_code.py` - Extract common patterns
- `fix_long_function.py` - Split large functions
- `fix_complexity.py` - Simplify complex logic

**Priority:** MEDIUM - Improves maintainability

---

#### Gap 5: No Test-Related Repair Rules
**Current State:** No rules for:
- Missing test coverage
- Broken test imports
- Outdated test fixtures

**Needed Enhancement:** Create repair rules:
- `fix_missing_tests.py` - Generate skeleton tests
- `fix_test_imports.py` - Update test imports after refactors
- `fix_test_fixtures.py` - Update fixtures after schema changes

**Priority:** MEDIUM - Improves test health

---

### Low Gaps

#### Gap 6: Documentation Repair Rules
**Current State:** No rules for:
- Missing docstrings
- Outdated docstrings
- Inconsistent docstring format

**Needed Enhancement:** Create repair rules:
- `fix_missing_docstrings.py` - Generate docstring stubs
- `fix_docstring_format.py` - Standardize docstring format
- `fix_outdated_docstrings.py` - Update after signature changes

**Priority:** LOW - Documentation quality

---

## Recommended Enhancement Plan

### Phase 1: Critical P1/P2 Integration (HIGH Priority)

1. **Integrate SQLite Analyzer into Repair Orchestrator**
   - Modify `repair_orchestrator.py` to call `sqlite_analyzer.py`
   - Convert P1/P2 violations to `Deficiency` objects
   - Enable repair orchestrator to handle P1/P2

2. **Create P2 Exception Antipattern Repair Rules**
   - `fix_exception_swallow.py` - Add logging
   - `fix_broad_exception_catch.py` - Narrow exceptions
   - `fix_return_none_swallow.py` - Re-raise with context

3. **Create P1 Layer Violation Repair Rule**
   - `fix_layer_violation.py` - Add guardian exemptions for known-safe patterns
   - Integrate with repair orchestrator

4. **Unify Auto-Fix Script**
   - Either integrate `auto_fix_p1_p2.py` into repair orchestrator
   - Or update repair orchestrator to call it as a fallback

### Phase 2: Code Quality Enhancements (MEDIUM Priority)

5. **Create Dead Code Removal Rule**
   - `fix_dead_code.py` - Remove unused functions/classes

6. **Create Duplicate Code Detection Rule**
   - `fix_duplicate_code.py` - Extract common patterns

7. **Create Test-Related Repair Rules**
   - `fix_test_imports.py` - Update test imports

### Phase 3: Documentation Enhancements (LOW Priority)

8. **Create Docstring Repair Rules**
   - `fix_missing_docstrings.py` - Generate stubs
   - `fix_docstring_format.py` - Standardize format

---

## Integration Recommendations

### Option A: Full Repair Orchestrator Integration
**Pros:**
- Unified repair infrastructure
- Consistent logging and rollback
- All repairs go through same pipeline

**Cons:**
- Requires significant refactoring
- More complex to maintain

### Option B: Hybrid Approach
**Pros:**
- Quick wins with standalone scripts
- Gradual migration to orchestrator
- Flexibility for one-off fixes

**Cons:**
- Fragmented repair infrastructure
- Inconsistent logging

**Recommendation:** Start with Option B (Hybrid) for Phase 1, migrate to Option A for Phase 2+

---

## Summary

**Total Repair Rules:** 7 active rules  
**Total Standalone Scripts:** 5 active scripts  
**Critical Gaps:** 3 (P1/P2 rules, SQLite integration)  
**Medium Gaps:** 3 (code quality, tests)  
**Low Gaps:** 1 (documentation)

**Immediate Action Items:**
1. Integrate `sqlite_analyzer.py` into `repair_orchestrator.py`
2. Create P2 exception antipattern repair rules
3. Create P1 layer violation repair rule
4. Unify `auto_fix_p1_p2.py` with repair orchestrator framework
