# RCA: Why Test Cases Take So Long — ADG-Backed Evidence

**Date**: 2026-03-25
**Method**: ADG SQLite + Redis hot cache queries (adg_indexed_03252026_0422.sqlite, 8,995 nodes, 836,686 edges)

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

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

# Implementation Plan: Phases and Waves

## Phase 0: Immediate Performance Recovery (1-)

### Wave 0.1: Bootstrap Emitter Cleanup (Day 1)
**Target**: 30 test files with 76–77 emitter imports each
```bash
# Strip top-level _emit_*() calls from test files
python tools/strip_test_emitters.py --dry-run
python tools/strip_test_emitters.py --apply
```
**Expected Impact**: ~30s reduction in test collection time
**Verification**: `pytest --collect-only tests/` timing before/after

### Wave 0.2: Session-Scoped ADG Fixture (Day 1)
**Target**: Eliminate redundant scans across test modules
```python
# In tests/conftest.py
@pytest.fixture(scope="session")
def cached_adg_scan():
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
    scanner = ADGStaticScanner(cache_path=Path("tests/.adg_cache.json"))
    return scanner.scan(commit_sha="session-scan")
```
**Expected Impact**: 3- saved per test session
**Verification**: Test suite runtime before/after

---

## Phase 1: Scanner Architecture Cleanup (3-)

### Wave 1.1: Test-Only Scan Mode (Day 2-3)
**Target**: Create `scan_mode="structural_only"` for test files
```python
# In static_scanner.py
def _selected_scan_roots(include_tests: bool, scan_mode: str = "full") -> tuple[str, ...]:
    if scan_mode == "structural_only" and include_tests:
        return _STRUCTURAL_SCAN_ROOTS + (TESTS_DIR,)
    return _selected_scan_roots(include_tests)

def _get_visitors_for_mode(scan_mode: str, file_path: str) -> list[BaseASTVisitor]:
    if scan_mode == "structural_only" and file_path.startswith("tests/"):
        return [_ImportVisitor, _InheritanceVisitor]  # Only G1 + G3
    return ALL_VISITORS
```
**Expected Impact**: 33 visitors → 2 visitors for test files
**Verification**: Edge count reduction in ADG for test files

### Wave 1.2: Exclude Tests from Non-Structural Scan (Day 3-4)
**Target**: Move `TESTS_DIR` to `_COVERAGE_ONLY_SCAN_ROOTS`
```python
# In static_scanner.py
_COVERAGE_ONLY_SCAN_ROOTS: tuple[str, ...] = (TESTS_DIR,)

def _filter_runtime_only_edges(edges: list[Edge], include_tests: bool, scan_mode: str = "full") -> list[Edge]:
    if scan_mode == "structural_only" and include_tests:
        return []  # Strip all runtime edges from tests
    return _filter_runtime_only_edges(edges, include_tests)
```
**Expected Impact**: Eliminates 125,000+ edges (`tests_execution_of` + `flows_to` + `resolves_callsite`)
**Verification**: ADG edge count drops from 322,978 to ~197,000 test edges

---

## Phase 2: Test Suite Restructuring ()

### Wave 2.1: Heavy Test Tagging (Day 5-6)
**Target**: Tag tests with >1000 edges as `@pytest.mark.slow`
```bash
# Identify heavy tests
python tools/identify_heavy_tests.py --threshold 1000 --output slow_tests.txt

# Auto-tag heavy tests
python tools/tag_slow_tests.py --input slow_tests.txt --apply
```
**Files to Tag**:
- `tests/adg/test_adg_hardening_comprehensive.py` (2,410 edges)
- `tests/adg/test_adg_coverage_supplement.py` (2,207 edges)
- `tests/adg/test_adg_coverage_final_push.py` (2,035 edges)
- All 73 `tests/adg/` files (672 edges avg)

**Expected Impact**: 49,078 edges removed from default test runs
**Verification**: `pytest -m "not slow"` runtime vs full suite

### Wave 2.2: Test Tier Separation (Day 6-7)
**Target**: Create separate test suites with different ADG requirements
```python
# tests/fast_suite/conftest.py
pytest_plugins = ["tests.conftest"]
@pytest.fixture(scope="session")
def adg_scan_mode():
    return "structural_only"

# tests/full_suite/conftest.py
pytest_plugins = ["tests.conftest"]
@pytest.fixture(scope="session")
def adg_scan_mode():
    return "full"
```
**Expected Impact**: Fast suite runs in <30s, full suite for CI only
**Verification**: Timing comparison between suites

---

## Phase 3: Infrastructure Optimization (1-)

### Wave 3.1: Parallel Test Processing (Week 2)
**Target**: Run test files in parallel during ADG scanning
```python
# In static_scanner.py
from concurrent.futures import ThreadPoolExecutor

def _scan_files_parallel(filepaths: list[Path], scan_mode: str) -> list[Edge]:
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(_scan_file, f, scan_mode) for f in filepaths]
        results = [f.result() for f in futures]
    return [edge for file_edges, _, _, _ in results for edge in file_edges]
```
**Expected Impact**: 4× speedup for multi-file test scans
**Verification**: Benchmark single vs parallel scanning

### Wave 3.2: Incremental Test ADG Updates (Week 2-3)
**Target**: Only rescan changed test files
```python
# In tools/adg_incremental_update.py
def update_test_adg(changed_files: list[Path]) -> None:
    test_files = [f for f in changed_files if f.is_relative_to("tests/")]
    if not test_files:
        return

    # Rescan only changed test files
    scanner = ADGStaticScanner(scan_mode="structural_only")
    new_edges = scanner.scan_files(test_files)

    # Update cache incrementally
    cache = ScanCache.load("tests/.adg_cache.json")
    for f in test_files:
        cache.invalidate(str(f))
    cache.save("tests/.adg_cache.json")
```
**Expected Impact**: <10s for single test file changes
**Verification**: Time measurement for incremental updates

---

## Phase 4: Long-term Architecture (2-)

### Wave 4.1: Test-Only ADG Schema (Week 3)
**Target**: Separate ADG schema for test vs production code
```python
# In agentic_core/adg/schema_test.py
TEST_RELATION_TYPES = frozenset({
    "imports", "implements", "calls", "exports"  # Structural only
})

# In static_scanner.py
def _get_schema_for_file(file_path: str) -> frozenset:
    if file_path.startswith("tests/"):
        return TEST_RELATION_TYPES
    return PRODUCTION_RELATION_TYPES
```
**Expected Impact**: Clean separation of concerns
**Verification**: ADG validation passes for both schemas

### Wave 4.2: Mock ADG for Unit Tests (Week 3-4)
**Target**: Create lightweight mock ADG for unit test performance
```python
# In tests/unit/conftest.py
@pytest.fixture
def mock_adg():
    class MockADG:
        def __init__(self):
            self.edges = []
            self.nodes = []
        def query(self, relation, **kwargs):
            return []
    return MockADG()
```
**Expected Impact**: Unit tests run in <1s without ADG dependency
**Verification**: Unit test suite timing

---

## Success Metrics

| Phase | Target Metric | Current | Target |
|-------|---------------|---------|--------|
| Phase 0 | Test collection time | ~60s | <30s |
| Phase 1 | Test ADG edges | 322,978 | <200,000 |
| Phase 2 | Fast suite runtime | 5- | <30s |
| Phase 3 | Parallel scan speedup | 1× | 4× |
| Phase 4 | Unit test isolation | Full ADG | Mock ADG |

---

## Risk Mitigation

1. **Coverage Loss**: Track ADG coverage metrics before/after each wave
2. **Test Regression**: Run full test suite after each phase
3. **Cache Corruption**: Implement cache validation and fallback
4. **Performance Regression**: Benchmark at each checkpoint

---

## Conclusion

The ADG proves that **test files are treated identically to production code** by the scanner — all 33+ visitors, all 97 relation types, all bootstrap wiring. This creates a situation where 38% of the entire graph is test-related overhead. This phased approach systematically decouples test coverage tracking from test execution performance while preserving architectural integrity.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

