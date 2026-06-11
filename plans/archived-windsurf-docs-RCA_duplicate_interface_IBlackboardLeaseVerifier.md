---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_duplicate_interface_IBlackboardLeaseVerifier.md'
original_relative_path: 'RCA_duplicate_interface_IBlackboardLeaseVerifier.md'
source_sha256: 57a93348e800104ba3fe7ccc1a2cb42846816d6fee83487ffe1ce2dd0e63a5e5
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Duplicate Interface Files — IBlackboardLeaseVerifier

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Summary

Two files in `agentic_core/interfaces/` traced back to the same origin but diverged
through conflicting healing passes:

| File | Class Name | Status |
|---|---|---|
| `IBlackboardLeaseVerifierProtocol.py` | `IBlackboardLeaseVerifier` (PascalCase) | **Canonical** — imported by `blackboard_store.py` |
| `IBlackboardLeaseVerifier.py` | `blackboard_lease_verifier` (snake_case) | **Dead** — zero importers, broken class refs |

## Root Cause Chain

1. **Original file**: `Iblackboard_lease_verifierProtocol.py` (mixed case) in `interfaces/`.
2. **Commit `3b2a50d72`** (2026-02-14, "RCA folder structure violations — 5 fixes"):
   **ADDED** a new file `IBlackboardLeaseVerifierProtocol.py` with corrected PascalCase
   classes and updated imports (`tool_args_types`).  The old file was **not deleted**.
3. **Commit `c68243674`** (2026-02-16, "folder-purity refactor"):
   **RENAMED** the still-existing old file `Iblackboard_lease_verifierProtocol.py` to
   `IBlackboardLeaseVerifier.py` (removed "Protocol" suffix, PascalCased filename).
   Inside, class names were **incorrectly snake_cased** (`blackboard_lease_verifier`),
   producing broken runtime references (e.g., `raise SandboxViolationError` where the
   class is defined as `sandbox_violation_error`).

**Result**: Two files from the same origin, with different names, different class-name
styles, and different import paths.

## Why execute_ssot Did Not Catch This

`FileClassificationAgent._detect_duplicate_files()` only matched by **exact filename**.
Since the two files had different names (`IBlackboardLeaseVerifierProtocol.py` vs
`IBlackboardLeaseVerifier.py`), they were invisible to duplicate detection.

Additionally, the FCA `get_compliant_name()` for PROTOCOL type appends "Protocol" suffix
and "I" prefix, while the folder-purity refactor (PascalSovereigntyFixer) strips the
"Protocol" suffix.  Two different naming strategies producing two different target names
from the same source is the structural root cause.

## Fix Applied

### 1. Semantic Duplicate Detection (FileClassificationAgent)

Added `_detect_semantic_duplicates()` to `FileClassificationAgent._detect_duplicate_files()`.
This method:

- Groups files by parent directory
- Extracts the primary (first) AST `ClassDef` per file
- Normalises class names: strips `I` prefix, `Protocol`/`Base` suffixes, lowercases
- Flags files in the same directory whose normalised primary class names collide
- Uses **AST-based import analysis** (not substring matching) to determine which copy
  is canonical (most module-level importers wins; ties broken by shorter filename)

### 2. Dead File Cleanup

- Deleted `agentic_core/interfaces/IBlackboardLeaseVerifier.py` (broken, zero importers)
- Deleted `tests/unit/test_Iblackboard_lease_verifierProtocol.py` (stale test for dead file)

### 3. Tests

Added `TestSemanticDuplicateDetection` class (6 tests) to
`tests/unit/agentic_core/L5_safety/reasoning/test_FileClassificationAgent.py`:

- `test_detects_pascal_vs_snake_same_class` — PascalCase vs snake_case primary class
- `test_no_false_positive_different_classes` — genuinely different classes not flagged
- `test_no_false_positive_different_directories` — same class in different dirs not flagged
- `test_canonical_prefers_more_importers` — AST import count determines canonical
- `test_blackboard_regression` — exact IBlackboardLeaseVerifier scenario
- `test_skips_test_files` — test files excluded from detection

All 9 tests in the file pass.  Canonical tests for `IBlackboardLeaseVerifierProtocol`
(15 passed, 3 skipped) and `blackboard_store` (14 passed) also green.

## Phase 2 Reconciliation Hang Fix

### Symptom

`execute_ssot --heal` stuck at "Phase 2: Reconciling 2 violations across agents..."
after completing 3 territory scans.  Process killed after ~ with no progress.

### Root Causes (3)

1. **No territory scoping** (primary): `execute_phase2_reconciliation` called
   `agent_instance.heal_repository(dry_run=False, execute=True)` at line 1927
   **without** `target_territory=territory`.  Each agent re-scanned the entire repo
   (~3000+ files with AST parsing) instead of just the current territory.

2. **O(n^2) AST parsing in semantic duplicate detection**: `_detect_semantic_duplicates`
   called `_importer_count()` per candidate pair, which re-parsed every file in the
   registry for each candidate.  With 3000+ files and multiple candidates, this was
   extremely slow.

3. **No timeout**: The `heal_repository()` call had no timeout guard.  The `@with_retry`
   decorator only handles exceptions, not hangs.

### Fixes Applied

| Fix | File | Change |
|---|---|---|
| Territory scoping | `execute_ssot.py:1928` | Pass `target_territory=territory` to `heal_repository()` |
| Timeout guard | `execute_ssot.py:1928-1945` | Wrap call in `ThreadPoolExecutor` with 300s timeout (configurable via `HEAL_TIMEOUT_SECONDS` env var) |
| Import index | `FileClassificationAgent.py:3060-3081` | Replace O(n^2) per-candidate AST re-parse with single-pass import index (`module_stem -> count`) |

### Regression Tests

Added `TestPhase2HangFixes` (5 tests) in
`tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_phase2_hang_fix.py`:

- `test_territory_passed_to_heal_repository` — territory flows through to agent
- `test_timeout_catches_hanging_agent` — hanging agent triggers RuntimeError
- `test_timeout_env_var_override` — HEAL_TIMEOUT_SECONDS respected
- `test_normal_agent_completes_within_timeout` — non-hanging agents unaffected
- `test_territory_scoping_reduces_scan_surface` — territory param propagates

All 5 tests pass in <1s.

## Repo-Wide Duplicate Cleanup

In addition to the IBlackboardLeaseVerifier pair, 9 more dead duplicate files and
5 stale test files were identified and deleted across the repo (same-directory,
overlapping primary class, zero importers).

## Files Changed

| Action | File |
|---|---|
| Modified | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` |
| Modified | `agentic_core/L0_routing/scripts/execute_ssot.py` |
| Modified | `tests/unit/agentic_core/L5_safety/reasoning/test_FileClassificationAgent.py` |
| Created  | `tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_phase2_hang_fix.py` |
| Deleted  | `agentic_core/interfaces/IBlackboardLeaseVerifier.py` |
| Deleted  | `tests/unit/test_Iblackboard_lease_verifierProtocol.py` |
| Deleted  | 9 dead duplicate files + 5 stale test files (repo-wide) |

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

