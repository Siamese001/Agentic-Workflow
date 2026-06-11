---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\amd-cpu-optimization-waves-8f7d9e.md'
original_relative_path: 'amd-cpu-optimization-waves-8f7d9e.md'
source_sha256: 89f3678bbeeb163c39b9a4003817b21ecc7dba1cb9bc102880fab2e521d94f8a
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-30'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# AMD CPU Optimization Plan - ADG-Informed Waves

**Objective:** Maximize AMD CPU utilization (currently <20%) for CPU-intensive ADG and agentic_core operations.

**ADG Baseline (03302026_0557):**
- 11,063 nodes, 724,922 edges
- 6,290+ modules processed by static_scanner
- Full ADG regeneration: 5+ minutes (single-threaded bottleneck)
- static_scanner.py: 3,011 modules with 7 bootstrap calls per module

---

## Wave Strategy Overview

| Wave | Focus | Target CPU Util | Est. Tokens | Duration |
|------|-------|-----------------|-------------|----------|
| 1 | Infrastructure - ProcessPool + CPU affinity | 40-50% | 8K | 1-2 days |
| 2 | ADG Scanner Parallelization | 60-70% | 12K | 2-3 days |
| 3 | File I/O Optimization | 50-60% | 6K | 1-2 days |
| 4 | Batch Processing Framework | 70-80% | 10K | 2-3 days |
| 5 | ADG Tool Suite Optimization | 80-90% | 15K | 3-4 days |

**Total Estimated Tokens:** ~51K  
**Expected Final CPU Util:** 80-90% on AMD Ryzen/Threadripper

---

## Wave 1: CPU Optimization Infrastructure

**Goal:** Establish foundational CPU optimization modules

### 1.1 CPU Optimizer Core (2.5K tokens)
```python
# agentic_core/L2_execution/optimization/cpu_optimizer.py
- AMDCPUOptimizer class with ProcessPoolExecutor
- CPU affinity tuning for AMD architectures
- Physical core detection (vs logical/SMT)
- Optimal worker calculation (7/8 of cores for Threadripper)
```

**ADG Insight:** `agentic_core/adg/extraction/static_scanner.py` contains 640+ emit calls - CPU-intensive AST analysis. Need ProcessPool to bypass Python GIL.

### 1.2 Parallel File Processor (2K tokens)
```python
# agentic_core/L2_execution/optimization/parallel_file_processor.py
- ParallelFileProcessor with batch execution
- Process directory trees in parallel
- File hashing, JSON parsing, text reading utilities
- Progress callbacks for long operations
```

**ADG Insight:** 6,290 modules scanned individually in `generate_full_adg.py` - parallel file reading can reduce I/O wait time.

### 1.3 Batch Processing Framework (2K tokens)
```python
# agentic_core/L2_execution/optimization/batch_processor.py
- BatchProcessor with error isolation
- StreamingBatchProcessor for large datasets
- JSON and FileHash batch processors
- Metrics collection per batch
```

**ADG Insight:** Redis ingest processes 724,922 edges in batches of 1000 - batch optimization critical.

### 1.4 Integration & Tests (1.5K tokens)
```python
# tests/performance/test_cpu_optimizer.py
- AMD detection tests
- Worker count validation
- CPU affinity tests
- Parallel map verification
```

**Acceptance Criteria:**
- [ ] CPU optimizer detects AMD and uses physical cores
- [ ] ProcessPoolExecutor created with correct worker count
- [ ] Parallel file processing 4x faster on 8+ core AMD
- [ ] All tests pass

---

## Wave 2: ADG Scanner Parallelization

**Goal:** Parallelize static_scanner.py to utilize all CPU cores

### 2.1 Module Scanner Parallelization (4K tokens)
```python
# agentic_core/adg/extraction/static_scanner.py modifications
- Parallel module scanning via ProcessPoolExecutor
- Batch processing for _P3LearningMaturityVisitor
- Parallel edge extraction across modules
- Shared cache for cross-module lookups
```

**ADG Insight:** Current scanner processes 3,011 modules sequentially. With 7 visitors per module and 7 bootstrap calls = 147,539 operations that can be parallelized.

### 2.2 AST Visitor Parallelization (3K tokens)
```python
- _JITContextVisitor parallel execution
- _L5ValidationProofVisitor parallel execution
- _GovernancePlaneVisitor parallel execution
- _DynamicInvocationVisitor parallel execution
- _LearningProvenanceVisitor parallel execution
```

**ADG Insight:** 36 dimensions across P0+P1+P2+P3+P4 all at 100% coverage. Each visitor can run in parallel per-module.

### 2.3 Cache-Aware Scanning (3K tokens)
```python
- Check scan_result_cache.json before re-scan
- Parallel cache validation
- Incremental update for changed modules only
- Cache invalidation on file modification
```

**ADG Insight:** Cache hit rate: 99.95% (6,288 hits / 6,291 total). Parallel cache validation reduces startup time.

### 2.4 Scanner Performance Tests (2K tokens)
```python
# tests/performance/test_scanner_parallel.py
- Benchmark sequential vs parallel scanning
- Memory usage validation under parallel load
- Cache performance under parallel access
- Regression test for edge count accuracy
```

**Acceptance Criteria:**
- [ ] Scanner uses 70%+ CPU on 8+ core AMD
- [ ] Parallel scan produces identical edge counts
- [ ] Cache hit rate maintained at >99%
- [ ] Full scan completes in <2 minutes (down from 5+)

---

## Wave 3: File I/O Optimization

**Goal:** Eliminate I/O bottlenecks that prevent CPU saturation

### 3.1 Async File Operations (2K tokens)
```python
# agentic_core/L2_execution/optimization/async_file_ops.py
- aiofiles wrapper for async file reading
- Async JSON/yaml parsing
- Concurrent file tree traversal
- Async SQLite operations for ADG
```

**ADG Insight:** `tools/adg/adg_redis_ingest.py` reads 453MB cache file + 724,922 edges from SQLite - all I/O bound.

### 3.2 Memory-Mapped File Access (1.5K tokens)
```python
- mmap for large file processing
- scan_result_cache.json memory mapping
- ADG SQLite read optimization
- Large corpus file handling
```

**ADG Insight:** `artifacts/adg/scan_result_cache.json` is 453MB - memory mapping eliminates read overhead.

### 3.3 Buffered I/O Optimization (1.5K tokens)
```python
- Optimized buffer sizes (8KB, 64KB, 1MB tiers)
- Streaming JSON parser for large files
- Buffered SQLite writes
- Batch file operations
```

**ADG Insight:** Coverage reports, closure validation, layer reports - all JSON files written in tight loops.

### 3.4 I/O Benchmarks (1K tokens)
```python
# tests/performance/test_io_optimization.py
- Sequential vs async file reading
- Memory-mapped vs standard file access
- Buffer size optimization tests
- I/O wait time measurement
```

**Acceptance Criteria:**
- [ ] I/O wait time reduced by 50%
- [ ] Async file operations maintain data integrity
- [ ] Memory-mapped cache access <100ms
- [ ] Large file processing (453MB) under 2 seconds

---

## Wave 4: Batch Processing Framework

**Goal:** Build comprehensive batch processing for all ADG operations

### 4.1 ADG Batch Operations (3K tokens)
```python
# tools/adg/batch_operations.py
- Batch edge insertion to SQLite
- Batch Redis pipeline operations
- Batch violation detection
- Batch report generation
```

**ADG Insight:** 724,922 edges inserted individually in `adg_redis_ingest.py` - batch to 1000 reduces round-trips by 724x.

### 4.2 Parallel Report Generation (2.5K tokens)
```python
- Layer coverage report (parallel per layer)
- Edge density report (parallel edge counting)
- Provenance report (parallel trace analysis)
- Boundary report (parallel validation)
```

**ADG Insight:** `generate_full_adg.py` generates 6+ reports sequentially - each report can be parallelized.

### 4.3 Streaming Data Processor (2.5K tokens)
```python
- Stream processing for large ADG datasets
- Chunked iteration over 724,922 edges
- Backpressure handling for CPU limits
- Progress streaming for long operations
```

**ADG Insight:** P3 learning maturity requires processing 3,011 modules × 7 dimensions = 21,077 operations - streaming prevents memory exhaustion.

### 4.4 Batch Performance Tests (2K tokens)
```python
# tests/performance/test_batch_operations.py
- Batch size optimization (100, 500, 1000, 5000)
- Memory usage under batch load
- Throughput measurement (items/second)
- Latency distribution (p50, p95, p99)
```

**Acceptance Criteria:**
- [ ] Batch edge insertion 10x faster
- [ ] Report generation parallelized 8x on 8-core AMD
- [ ] Streaming processor handles 724K edges without OOM
- [ ] Batch throughput >10,000 items/second

---

## Wave 5: ADG Tool Suite Optimization

**Goal:** Apply CPU optimization to all ADG tools

### 5.1 Coverage Analysis Parallelization (3K tokens)
```python
# tools/adg/coverage_analysis.py optimization
- Parallel source module scanning
- Parallel test coverage calculation
- Parallel ADG vs non-ADG split analysis
- Concurrent uncovered module grouping
```

**ADG Insight:** Coverage analysis iterates 6,290 modules sequentially - parallel by layer (L0-L6).

### 5.2 Layer Boundary Checker Parallelization (2.5K tokens)
```python
# tools/adg/adg_layer_boundary_checker.py optimization
- Parallel file violation checking
- Parallel directory tree traversal
- Concurrent layer summary generation
- Parallel JSON output formatting
```

**ADG Insight:** Layer boundary checker validates imports across all modules - embarrassingly parallel per file.

### 5.3 Redis Ingest Parallelization (3K tokens)
```python
# tools/adg/adg_redis_ingest.py optimization
- Parallel node insertion to Redis
- Pipeline batching (currently 1000, optimize to 5000)
- Parallel edge adjacency set building
- Concurrent module context calculation
```

**ADG Insight:** Redis ingest processes 724,922 edges, 11,063 nodes, module context for 6,290 modules - all parallelizable.

### 5.4 Incremental Update Engine Optimization (2.5K tokens)
```python
# tools/adg/accelerators/incremental/generate_full_adg.py
- Parallel impacted closure calculation
- Concurrent neighbor detection
- Parallel rescan of changed modules
- Batch SQLite update operations
```

**ADG Insight:** Incremental update (12 files → 129 impacted → 16.4s) can be sub-10s with parallel processing.

### 5.5 ADG Tool Performance Suite (2K tokens)
```python
# tests/performance/test_adg_tools.py
- End-to-end ADG generation benchmark
- Tool-by-tool performance comparison
- CPU utilization measurement per tool
- Regression detection for performance
```

**Acceptance Criteria:**
- [ ] Coverage analysis 5x faster
- [ ] Layer boundary checker uses 80%+ CPU
- [ ] Redis ingest completes in <30 seconds
- [ ] Incremental update <10 seconds
- [ ] Full ADG generation <90 seconds

---

## Token Budget Summary

| Wave | Component | Tokens | Cumulative |
|------|-----------|--------|------------|
| **Wave 1** | Infrastructure | 8,000 | 8,000 |
| **Wave 2** | ADG Scanner | 12,000 | 20,000 |
| **Wave 3** | File I/O | 6,000 | 26,000 |
| **Wave 4** | Batch Framework | 10,000 | 36,000 |
| **Wave 5** | ADG Tools | 15,000 | 51,000 |
| **Buffer** | Testing/Integration | 9,000 | **60,000** |

**Total Token Budget:** 60,000 tokens (51K implementation + 9K buffer)

---

## Expected Performance Outcomes

### AMD CPU Utilization Targets

| Phase | Current | Wave 1 | Wave 2 | Wave 3 | Wave 4 | Wave 5 |
|-------|---------|--------|--------|--------|--------|--------|
| **Full ADG Scan** | 15-20% | 40% | 70% | 75% | 80% | 85-90% |
| **Redis Ingest** | 10-15% | 30% | 50% | 60% | 75% | 85% |
| **Coverage Analysis** | 20% | 40% | 60% | 65% | 75% | 85% |
| **Layer Check** | 15% | 35% | 55% | 65% | 75% | 85% |

### Time Reduction Targets

| Operation | Current | Target | Speedup |
|-----------|---------|--------|---------|
| Full ADG generation | 5+ min | <90 sec | 3.3x |
| Redis ingest | 60+ sec | <30 sec | 2x |
| Coverage analysis | 30+ sec | <6 sec | 5x |
| Incremental update | 16.4 sec | <10 sec | 1.6x |
| Layer boundary check | 20+ sec | <4 sec | 5x |

---

## Implementation Dependencies

```
Wave 1 (Infrastructure)
  ├── cpu_optimizer.py
  ├── parallel_file_processor.py
  └── batch_processor.py
      │
      ▼
Wave 2 (ADG Scanner)
  ├── static_scanner.py modifications
  ├── Parallel AST visitors
  └── Cache-aware scanning
      │
      ▼
Wave 3 (File I/O)
  ├── async_file_ops.py
  ├── memory-mapped access
  └── buffered I/O
      │
      ▼
Wave 4 (Batch Framework)
  ├── ADG batch operations
  ├── Parallel report generation
  └── Streaming processor
      │
      ▼
Wave 5 (ADG Tools)
  ├── coverage_analysis.py
  ├── adg_layer_boundary_checker.py
  ├── adg_redis_ingest.py
  └── incremental update engine
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Parallel scan produces different results | Regression tests comparing edge counts before/after |
| Memory exhaustion on Threadripper | Streaming processors with backpressure |
| Cache corruption in parallel access | File locking for scan_result_cache.json |
| GIL contention in Python | ProcessPoolExecutor for CPU-bound tasks only |
| Windows process spawn overhead | Use 'spawn' context, optimize batch sizes |

---

## Success Metrics

1. **CPU Utilization:** 80-90% sustained on AMD during ADG operations
2. **Performance:** 3x+ speedup on full ADG generation
3. **Correctness:** 100% edge count accuracy maintained
4. **Memory:** No OOM errors on 32GB+ systems
5. **Tests:** All 19 scanner tests pass + new performance tests

---

## Plan Location
**Canonical Path:** `docs/reports/plans/amd-cpu-optimization-waves-8f7d9e.md`

**Related Documents:**
- `docs/reports/QWEN_VLLM_OPTIMIZATION_SUMMARY.md`
- `docs/reports/QWEN_VLLM_PERFORMANCE_HARDENING.md`
- `agentic_core/L2_execution/optimization/` (implementation directory)
