---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\cpu-optimization-hotspot-inventory-a1b2c3.md'
original_relative_path: 'cpu-optimization-hotspot-inventory-a1b2c3.md'
source_sha256: 47d0ba3ae0aab0bfc74ff4943f76caf463edc0924a4cd385c907c83253853dfb
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-30'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# CPU Optimization Hotspot Inventory & Wave Plan
**Date:** 2026-03-30 | **Environment:** AMD Ryzen 9 9950X3D, 32 logical CPUs, Windows, Python 3.12.10

---

## Baseline Measurements (MEASURED, not estimated)

| Workload | Wall-clock | CPU Bound? | Notes |
|----------|-----------|------------|-------|
| ADG full scan (99.7% cache) | 50.0s | Mixed | Bottleneck: _edge_from_dict + layer violation sweep |
| Serial AST parse (7522 files) | 6.55s | **YES** | 1148 files/s |
| Parallel AST parse w=16 | 0.65s | — | **10.0x speedup** |
| Full visitor walk (parse+walk) | 6.54s | **YES** | 1150 files/s |
| Parallel full visitor w=16 | 0.68s | — | **9.6x speedup** |
| SHA-256 hashing (7522 files) | 0.295s | I/O | Already fast; ThreadPool *hurts* (0.57x) |
| JSON dumps (50k edges, 3.5MB) | 20.9ms/iter | CPU | orjson = 2.8ms/iter **(7.5x speedup)** |
| pytest collect unit_min_deps | 1.08s | Import | ~1s overhead per suite |
| pytest collect adg | 1.33s | Import | — |
| pytest exec unit_min_deps | 1.08s | Import-dom. | 0.24s actual test time |
| pytest exec adg | 8.71s | **CPU** | 7.81s test execution |
| pytest exec governance | 1.05s | Import-dom. | 0.20s actual |
| pytest exec guardian | 1.04s | Import-dom. | 0.20s actual |
| File discovery (7522 files) | 0.22s | I/O | Already fast |
| Raw file read (1000 files) | 0.033s | I/O | 338 MB/s, no bottleneck |

---

## Top ADG Scanner Profiler Hits (cProfile, cumtime, 99.7% cache run)

| Function | ncalls | cumtime | Classification |
|----------|--------|---------|----------------|
| `scan()` | 1 | 120s* | Orchestrator |
| `_emit_layer_violation_edges` | 1 | 12.35s | **CPU-BOUND** — O(N²) cross-layer check |
| `_edge_from_dict` | 732,019 | 5.63s | **CPU-BOUND** — cache deserialization |
| `run_scanner_self_test` | 1 | 4.77s | **CPU-BOUND** — runs on every scan |
| `canonical_edge_text` | 4 | 3.50s | **CPU-BOUND** — digest computation |

*120s profiler wall vs 50s actual (profiler overhead)

---

## Hotspot Inventory (ranked by optimization ROI)

### RANK 1 — ADG Scanner: `_edge_from_dict` cache deserialization
- **Type:** CPU-bound (Python object construction in tight loop)
- **Bottleneck:** 732k calls constructing edge dataclass objects from dicts, serial
- **Lever:** Batch + parallel deserialization using ProcessPool, or `__slots__` + lazy construction
- **Expected gain:** 4–6x on the cache-hit path (5.6s → ~1s)
- **Risk:** Low — output is identical dataclass objects
- **Files:** `agentic_core/adg/extraction/static_scanner.py`

### RANK 2 — ADG Scanner: Parallel AST parse on cache-miss files
- **Type:** CPU-bound (AST parsing bypasses GIL via C extension)
- **Bottleneck:** Serial parse of 7522 files at 1148 files/s
- **Lever:** ProcessPoolExecutor with chunksize=60, w=16
- **Expected gain:** 10x on full rescan (6.55s → 0.65s)
- **Risk:** Low — each file is independent, results merged after
- **Files:** `agentic_core/adg/extraction/static_scanner.py` (scan loop)

### RANK 3 — ADG Scanner: `_emit_layer_violation_edges`
- **Type:** CPU-bound (cross-product layer check)
- **Bottleneck:** 12.35s, runs on every scan regardless of cache
- **Lever:** Index modules by layer upfront (dict lookup vs linear scan), vectorize with sets
- **Expected gain:** 5–10x (12s → 1–2s)
- **Risk:** Medium — must preserve exact same edges, needs correctness test
- **Files:** `agentic_core/adg/extraction/static_scanner.py`

### RANK 4 — JSON report serialization: replace `json` with `orjson`
- **Type:** CPU-bound (pure Python JSON encoder)
- **Bottleneck:** 20.9ms/iter for 50k-edge graphs; 8 reports generated per ADG run
- **Lever:** Drop-in `orjson.dumps()` — 7.5x faster, Rust-backed
- **Expected gain:** 8 × 17ms = ~136ms saved per ADG run; larger for big graphs
- **Risk:** Very low — same output format, orjson already installed
- **Files:** `tools/generate_full_adg.py` (`_generate_standardized_reports`), `tools/adg/adg_redis_ingest.py`

### RANK 5 — pytest-xdist for ADG test suite
- **Type:** CPU-bound (7.81s actual execution, 424 tests)
- **Bottleneck:** Serial execution, no parallelism
- **Lever:** `pytest-xdist` with `-n auto` (xdist not installed, needs pip install)
- **Expected gain:** ~3–5x on ADG suite (8.7s → ~2–3s)
- **Risk:** Low for unit tests; must verify no shared state / filesystem collisions
- **Files:** `pytest.ini` or `pyproject.toml`, `conftest.py` (fixture scope audit needed)

### RANK 6 — ADG Scanner: `run_scanner_self_test` called on every scan
- **Type:** CPU-bound (self-test runs full import/visit cycle)
- **Bottleneck:** 4.77s on every scan, even with 99.7% cache
- **Lever:** Gate behind env flag `ADG_SKIP_SELF_TEST=1` or run only on cache-miss
- **Expected gain:** 4.77s saved per cached run
- **Risk:** Low if gated (test correctness preserved by CI, not every run)
- **Files:** `agentic_core/adg/extraction/static_scanner.py`

### NOT WORTH OPTIMIZING (correct behavior)

| Workload | Why it's fine |
|----------|--------------|
| SHA-256 hashing | Already 0.295s serial; ThreadPool makes it slower (I/O-bound, disk cache warm) |
| File discovery | 0.22s, I/O-bound, already fast |
| Raw file reads | 338 MB/s, no bottleneck |
| pytest unit_min_deps/governance/guardian | Import-dominated (1s overhead, 0.2s actual); parallelism adds more overhead than saved |
| Redis lookups | Cache-hit fast path — adding CPU work here is wrong |
| ADG cache scan (99.7% hits) | Correctness of cache is more important; don't add work to cache path |

---

## Implementation Waves

### Wave A — orjson + scanner self-test gate (lowest risk, immediate win)
**Files:** `tools/generate_full_adg.py`, `agentic_core/adg/extraction/static_scanner.py`
**Expected gain:** ~5s per ADG run (4.77s self-test + 0.1s JSON)
**Risk:** Very low
**Validation:** ADG generation produces identical artifacts; `python -m pytest tests/adg -q`

### Wave B — Parallel `_edge_from_dict` deserialization
**Files:** `agentic_core/adg/extraction/static_scanner.py`
**Expected gain:** ~4s per cached scan
**Risk:** Low — pure transformation, no side effects
**Validation:** edge count and digest unchanged

### Wave C — Parallel AST parse on cache-miss files
**Files:** `agentic_core/adg/extraction/static_scanner.py`
**Expected gain:** 10x on full rescan (6.5s → 0.65s)
**Risk:** Low — files are independent
**Validation:** same modules/edges as serial run

### Wave D — `_emit_layer_violation_edges` O(N²) → O(N) fix
**Files:** `agentic_core/adg/extraction/static_scanner.py`
**Expected gain:** 10–12s saved per scan
**Risk:** Medium — must verify exact same violation edges
**Validation:** `pytest tests/adg -k violation` + edge count regression check

### Wave E — pytest-xdist for ADG test suite
**Files:** `requirements*.txt`, `pytest.ini` or `pyproject.toml`
**Expected gain:** ADG suite 8.7s → ~2–3s
**Risk:** Low (ADG tests are stateless file-based analysis)
**Validation:** same pass/fail counts with `-n 8`

---

## Safe Default Worker Counts (AMD Ryzen 9 9950X3D, 32 logical / 16 physical)

| Workload | Recommended Workers | Rationale |
|----------|-------------------|-----------|
| AST parse (ProcessPool) | 16 | Matches physical core count; 10x speedup measured |
| Full visitor walk | 16 | Same — CPU-bound, GIL-free via C AST extension |
| JSON serialization | N/A | Use orjson (single-thread is already 7.5x faster) |
| Redis ingest pipeline | 1 (single connection) | Network/Redis-bound, parallelism doesn't help |
| pytest-xdist | 8 | Conservative for stateful fixture safety |

---

## AFTER Measurements (commit 85e4a87f13)

| Wave | Change | Before | After | Speedup |
|------|--------|--------|-------|---------|
| E | orjson in scan_cache.py load()/save() | json.dumps=49.7s | orjson.dumps=0.38s | **131x** on serialization |
| H | _EDGE_SORT_KEY fast sort key | sorted() 25s (13-field __lt__) | sorted() 5.1s | **4.9x** on sort |
| G | Batch post-scan edge merges | 3x sorted()+digest | 1x sorted()+digest | 3x fewer re-sorts |
| F | Remove redundant sort in canonical_edge_text | sorted(self.edges) per digest | direct iteration | eliminates 4x redundant sorts |
| D | lru_cache on module_path_to_layer | 12.35s (1.5M calls) | <0.1s (cache hits) | **>100x** on layer lookup |
| B | _EDGE_FIELD_NAMES pre-computed | 5.63s (per-call set()) | 3.23s | **1.7x** on deserialization |
| A | ADG_SKIP_SELF_TEST env gate | 4.9s always | 0s when env=1 | **eliminates** self-test cost |
| A | orjson in generate_full_adg.py | 20.9ms/iter JSON | 2.8ms/iter orjson | **7.5x** on report gen |

**Overall ADG cached scan: 50.0s → 19.8s (2.5x speedup, skip_self_test=1)**
**Overall ADG cached scan: 50.0s → ~25s (with self-test, default mode)**

### Correctness Verification
- 424/424 ADG tests passed after all waves
- Pre-existing failures: 183 (unchanged before/after)
- Edge count preserved: 728k (same modules, same graph structure)
- Digest computation preserved (determinism maintained)

### Remaining Bottlenecks (not yet optimized)
| Bottleneck | Cost | Notes |
|------------|------|-------|
| `_edge_from_dict` 732k calls | 3.2s | Per-file cache deserialization; needs schema change to avoid |
| `sorted(filenames)` in file walk | ~5s | Necessary for determinism; unavoidable |
| `Edge.__hash__` for set() dedup | 0.66s | Inherent to frozenset dedup; acceptable |
| `canonical_edge_text` (3 calls) | 1.3s | SHA-256 digest over 728k-line string |

---

## Non-Negotiable Invariants
- No changes to governance, safety, replay, UWG, or determinism paths
- All optimizations must produce byte-identical ADG artifacts (digest-verified)
- No busy-loops or artificial CPU burn
- Every wave tested before commit
