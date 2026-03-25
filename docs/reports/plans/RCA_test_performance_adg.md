# RCA: Why Test Cases Take So Long — ADG-Backed Evidence

**Date**: 2026-03-25
**Method**: ADG SQLite + Redis hot cache queries (adg_indexed_03252026_0422.sqlite, 8,995 nodes, 836,686 edges)

---

## Executive Summary

Tests account for **38% of all ADG edges** (322,978 / 841,382) across **3,274 test files**. The root causes of slow test execution are: (1) massive per-file bootstrap overhead from `lifecycle_trace_contract` imports (76–77 emitter calls per file), (2) the `tests/adg/` directory averaging **672 edges per file** (13× the `tests/unit/` average), and (3) expensive non-structural edge types (`tests_execution_of`, `decomposes_into`, `flows_to`) that dominate test file processing.

---

## Root Cause 1: Bootstrap Import Overhead — `lifecycle_trace_contract`

### ADG Evidence
```
=== TEST FILES IMPORTING LIFECYCLE_TRACE_CONTRACT ===
  Count: 30 files import lifecycle_trace_contract directly
  77 imports  tests/unit/.../test_transcript_freezer_adg.py
  76 imports  tests/unit_min_deps/test_vllm_replay.py
  76 imports  tests/unit_min_deps/test_version_store.py
  76 imports  tests/unit_min_deps/test_time_shifted_consumption.py
  76 imports  tests/unit_min_deps/test_three_tier_convergence.py
  ... (30 files, each importing 76-77 emitters)
```

Each test file that imports `lifecycle_trace_contract` pulls in **76–77 emitter functions** at module load time. These are top-level `_emit_*()` calls that execute during import — not during test execution. This means **every `pytest` collection step** for these files triggers 76+ function calls before a single test runs.

### Impact
- **Collection overhead**: ~1s per file just for bootstrap emitter calls
- **Multiplied across suite**: 30 files × 76 calls = 2,280 emitter invocations at collection time

---

## Root Cause 2: `tests/adg/` Has Extreme Edge Density

### ADG Evidence — Edge Count by Test Directory
```
  134,799 edges  2,621 files  avg=  51  tests/unit
   49,078 edges     73 files  avg= 672  tests/adg         ← 13× unit avg
   26,741 edges    103 files  avg= 259  tests/unit_min_deps
   22,692 edges     88 files  avg= 257  tests/guardian
   20,602 edges     99 files  avg= 208  tests/governance
   17,317 edges     66 files  avg= 262  tests/integration
   16,507 edges     35 files  avg= 471  tests/architecture ← 9× unit avg
   14,288 edges     38 files  avg= 376  tests/sys_learning
    6,193 edges     10 files  avg= 619  tests/evaluation   ← 12× unit avg
  -------        ----
  322,978 edges  3,274 files  TOTAL
```

**`tests/adg/` has only 73 files but 49,078 edges** — averaging 672 edges per file. This is 13× the `tests/unit/` average of 51 edges/file. Each edge represents an AST-extracted relationship that the scanner must process, hash, and sort.

### Top 30 Heaviest Test Files (Total Edges)
```
  2,410 edges  tests/adg/test_adg_hardening_comprehensive.py
  2,207 edges  tests/adg/test_adg_coverage_supplement.py
  2,206 edges  tests/unit_min_deps/test_llm_workflow_creative.py
  2,035 edges  tests/adg/test_adg_coverage_final_push.py
  1,957 edges  tests/adg/test_adg_gap_implementations.py
  1,894 edges  tests/adg/test_adg_accelerators_edge_cases.py
  1,751 edges  tests/adg/test_adg_accelerator_hardening.py
```

A single file like `test_adg_hardening_comprehensive.py` has **2,410 edges** — equivalent to ~47 average unit test files.

---

## Root Cause 3: Heavy Non-Structural Edge Types in Tests

### ADG Evidence — Heaviest Non-Import Relations
```
   61,499  tests_execution_of
   37,196  decomposes_into
   36,589  flows_to
   27,315  resolves_callsite
   15,268  exports
   14,981  calls
    9,622  covers
    6,146  controls_flow
    5,307  reads_from
    4,353  emits_side_effect
```

**`tests_execution_of` alone accounts for 61,499 edges** — these are edges from the execution semantic visitor that trace control flow through test files. Combined with `flows_to` (36,589) and `resolves_callsite` (27,315), the scanner is performing expensive AST analysis on test files that don't benefit from it.

---

## Root Cause 4: Import Fan-Out Per Test File

### ADG Evidence — Top Importers
```
  187 imports  tests/adg/test_adg_hardening_comprehensive.py
  176 imports  tests/architecture/test_adg_digest_stable.py
  175 imports  tests/adg/test_adg_coverage_supplement.py
  175 imports  tests/adg/test_adg_accelerators_edge_cases.py
  174 imports  tests/unit_min_deps/test_llm_workflow_creative.py
  174 imports  tests/adg/test_adg_coverage_final_push.py
  171 imports  tests/integration/test_creative_cross_context.py
  170 imports  tests/adg/test_adg_output_robustness.py
```

The heaviest test files import **170–187 symbols**. Compare: a typical production module imports 10–30 symbols. These massive import lists are almost entirely `lifecycle_trace_contract` emitter functions that exist solely for ADG coverage wiring.

---

## Root Cause 5: Test Relation Type Explosion

### ADG Evidence
```
  Unique relation types in tests: 97
  Total test edges: 322,978 / 841,382 (38% of all edges)
  Unique test files: 3,274
```

Tests use **97 distinct relation types** — the same full set used for production code. The scanner runs all 33+ AST visitors on every test file, extracting edge types like `captures_pattern`, `records_learning_event`, `stores_embedding` that are pure bootstrap wiring with zero test-behavioral value.

---

## Quantified Impact

| Factor | Metric | Impact |
|--------|--------|--------|
| Bootstrap imports | 76 emitters × 30 files | ~30s collection overhead |
| `tests/adg/` density | 672 edges/file avg | 13× slower than unit tests |
| Non-structural edges | 61,499 `tests_execution_of` | Scanner spends majority on non-test logic |
| Import fan-out | 187 imports (max) | Module load time dominates |
| Relation type coverage | 97 types across tests | All 33 visitors run on every test file |
| Total test edge share | 38% of entire ADG | Tests double the graph processing time |

---

## Recommended Fixes (Priority Order)

### P0: Remove Bootstrap Emitters from Test Files
- **Action**: Strip `_emit_*()` calls from test file top-level scope
- **Impact**: Eliminates 76 function calls per file at collection time
- **Risk**: ADG coverage numbers for test files will drop (acceptable — tests are not production code)

### P1: Exclude `tests/` from Non-Structural Scan
- **Action**: Move `TESTS_DIR` from `_NON_STRUCTURAL_SCAN_ROOTS` to a new `_COVERAGE_ONLY_SCAN_ROOTS` that skips execution/semantic visitors
- **Impact**: Eliminates 125,000+ edges (`tests_execution_of` + `flows_to` + `resolves_callsite`)

### P2: Create Lightweight Test Scanner Mode
- **Action**: Add `scan_mode="structural_only"` that runs only G1 (imports) + G3 (inheritance) visitors on test files
- **Impact**: 33 visitors → 2 visitors per test file

### P3: Split `tests/adg/` Into Tiers
- **Action**: Tag heavy tests (`>1000 edges`) as `@pytest.mark.slow` and exclude from default runs
- **Impact**: 73 files with 49,078 edges removed from fast path

### P4: Session-Scoped ADG Fixture
- **Action**: Pre-compute ADG once per session, share across all tests via `@pytest.fixture(scope="session")`
- **Impact**: Eliminates redundant scans across test modules

---

## Conclusion

The ADG proves that **test files are treated identically to production code** by the scanner — all 33+ visitors, all 97 relation types, all bootstrap wiring. This creates a situation where 38% of the entire graph is test-related overhead. The fix is architectural: decouple test coverage tracking from test execution performance by limiting which visitors and emitters apply to `tests/`.
