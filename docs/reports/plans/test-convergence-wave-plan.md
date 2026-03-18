# Test Convergence Wave Plan

**Generated**: 2026-03-18
**Baseline commits**: 8f2c23b92a (batch 1), 464eff6175 (batch 2), 566e5fb5c3 (batch 3)

## Current State (post batch 1-3 fixes)

| Suite | Passed | Failed | Skipped | Errors | Notes |
|-------|--------|--------|---------|--------|-------|
| sovereign_hardening | 59 | 0 | 1 | 0 | **CLEAN** |
| guardian | ~1642 | ~32 | 0 | ~22 | Timeouts + assertion + missing fixtures |
| adg | ~4376 | ~64 | 17 | 0 | Assertion + TYPE_CHECKING + integration |
| architecture | ~864 | ~53 | 0 | ~2 | Structural assertions + missing dirs |
| contracts | ? | ? | ? | ? | Hangs during scan — needs individual file runs |

**Estimated totals**: ~6941P / ~149F / ~18S / ~24E

---

## Root Cause Categories

### CAT-A: Missing `import uuid` at module level (~5-10 files causing failures)
- **Pattern**: Lifecycle emitter wiring calls `uuid.uuid4()` but only has function-scoped `import uuid as _uuid`
- **Impact**: NameError at runtime when the module-level emitter call runs
- **Fix**: Add `import uuid` to top of affected files
- **Files known**: `redis_coordination_fabric.py` (FIXED), `SovereignLLMGateway.py` (FIXED)
- **Effort**: Low (1-line per file)

### CAT-B: TYPE_CHECKING-only names used at runtime (~3-5 files)
- **Pattern**: Types imported under `if TYPE_CHECKING:` but used in `isinstance()` or function calls at runtime
- **Impact**: NameError when the function is called
- **Fix**: Use runtime resolver function (e.g. `_get_case_memory_types()`, `_get_determinism_fns()`)
- **Files known**: `case_library.py` (FIXED), `graph_neighborhood_memory.py` (FIXED), `cache_admission_gate.py` (FIXED)
- **Effort**: Low-Medium

### CAT-C: Corrupted files (lifecycle emitter wiring injected into docstrings/code)
- **Pattern**: Batch wiring scripts injected import blocks and emitter calls into wrong locations (inside docstrings, breaking syntax)
- **Impact**: SyntaxError or NameError at import time
- **Fix**: Manually restore corrupted docstrings, move imports to proper location
- **Files known**: `classification_kernel.py` (FIXED)
- **Effort**: Medium (must read each file carefully)

### CAT-D: Missing emitter imports in top-level import block
- **Pattern**: Module uses `_emit_snapshots_state()` etc. at module scope but the import is missing from the top block
- **Impact**: NameError at import time
- **Fix**: Add missing symbol to existing import block
- **Files known**: `classification_kernel.py` (FIXED)
- **Effort**: Low (add to import list)

### CAT-E: Missing infrastructure files/directories
- **Pattern**: Tests assert existence of directories or files that were never created or were removed
- **Impact**: pytest.fail() or FileNotFoundError
- **Known items**:
  - `tests/support/` directory does not exist → 11F in `test_phantom_folder_regression.py`
  - `sovereignty_bootstrap.py` missing → guardian test failures
  - `SSOTFolderCleanupAgent.py` at wrong path (doubled `agentic_core/agentic_core/`)
- **Fix**: Create missing dirs/files OR update tests to skip/adjust
- **Effort**: Medium (need to decide: create infra or update tests)

### CAT-F: Missing pytest fixtures
- **Pattern**: Tests reference fixtures like `adg_query_engine` that are not defined in any conftest
- **Impact**: ERROR at test setup
- **Known items**: 9E in `test_guardian_duplicate_ssot.py`
- **Fix**: Create fixture in conftest OR mark tests as xfail/skip
- **Effort**: Medium-High

### CAT-G: Pre-existing assertion mismatches
- **Pattern**: Tests expect specific values/behaviors that have drifted from current code
- **Impact**: AssertionError
- **Known items**:
  - `test_classification_kernel_hardened.py`: 2F — UTILITY vs IGNORE classification
  - `test_adg_g7_g16_completeness_accuracy.py`: 1F — `emit_replay_key` not in `REPLAY_KEY_METHODS`
  - `test_adg_g7_g16_creative_extensions.py`: 1F — dead relations audit (emits_drift_alert, emits_replay_key)
  - `test_adg_gap_g7_g16.py`: 1F — `ExecutionTrace.__init__()` unexpected kwarg `agent_id`
  - `test_adg_gap_remediation_novel.py`: 1F — `verify_replay` returns False
  - `test_adg_p3_enhancements.py`: 1F — `TypeError: must be real number, not dict`
  - `test_apps_rationalization_verification.py`: F — missing importer paths
  - `test_sovereign_territories_migration_verification.py`: F — `get_territory_metadata` returns wrong type
  - `test_contracts_fixture_placement.py`: 1F — fake_*.py in wrong location
- **Fix**: Update test expectations OR fix source code to match contract
- **Effort**: Medium (each requires individual analysis)

### CAT-H: Timeouts / hanging tests
- **Pattern**: Tests that connect to Redis, run full ADG scans, or do heavy I/O
- **Impact**: pytest timeout or process hang
- **Known items**: ~22E in guardian suite, ~2E in architecture
- **Fix**: Add pytest.mark.skip for integration tests requiring external services, or increase timeout
- **Effort**: Low (mark as skip) or N/A (infrastructure issue)

---

## Wave Plan

### Wave 1: Remaining NameError/ImportError (CAT-A, CAT-B, CAT-C, CAT-D)
**Priority**: HIGH — These are import-time crashes that cascade to many test failures
**Effort**: LOW
**Approach**: 
1. grep for remaining `NameError` in test output (not re-scan — use targeted pytest on known failing files)
2. Fix pattern: add missing imports or use runtime resolvers
3. Verify each fix individually
**Expected gain**: ~10-20F eliminated

### Wave 2: Missing infrastructure (CAT-E)
**Priority**: HIGH — 11F from missing `tests/support/` alone
**Effort**: LOW-MEDIUM
**Approach**:
1. Create `tests/support/` directory (empty is fine if tests just check existence)
2. Determine if `sovereignty_bootstrap.py` needs to be created or tests updated
3. Fix doubled path in `SSOTFolderCleanupAgent.py` reference
**Expected gain**: ~15-20F eliminated

### Wave 3: Missing fixtures (CAT-F) + Timeout management (CAT-H)
**Priority**: MEDIUM — Errors, not failures; won't affect pass count much
**Effort**: MEDIUM
**Approach**:
1. Create `adg_query_engine` fixture stub in appropriate conftest, OR mark tests as `@pytest.mark.skip`
2. Mark integration tests requiring Redis/external services with `@pytest.mark.integration`
3. Skip integration marks in minimal config
**Expected gain**: ~20-30E eliminated

### Wave 4: Assertion mismatches (CAT-G)
**Priority**: LOW — Each is a 1F fix requiring individual analysis
**Effort**: MEDIUM-HIGH
**Approach**:
1. Triage each assertion failure individually
2. Determine if test expectation or source code is wrong
3. Fix the correct side
**Expected gain**: ~10-15F eliminated

---

## Acceptance Criteria

- sovereign_hardening: 59P/0F/1S (ALREADY MET)
- guardian: 0F, 0E (excluding intentional skips)
- adg: 0F, 0E (excluding intentional skips)
- architecture: 0F, 0E (excluding intentional skips)
- All skips have documented justification
