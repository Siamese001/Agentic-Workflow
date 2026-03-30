# ADG CPU Optimization Integration Plan

## Executive Summary

**Objective:** Integrate existing CPU optimization infrastructure into ADG generation to achieve 80-90% CPU utilization.

**Current State:**
- Infrastructure exists (commits 93b461be, 55a4ffa2) but NOT integrated
- CPU utilization: ~15-20% (baseline)
- ADG generation: Single-threaded, sequential processing

**Target State:**
- CPU utilization: 80-90%
- Parallel file processing with ProcessPoolExecutor
- Async I/O for SQLite operations
- CPU affinity for AMD processors

---

## Token Budget Summary by Wave

| Wave | Description | Est. Tokens | Status | CPU Target |
|------|-------------|-------------|--------|------------|
| **Wave 1** | Import Wiring & CLI Flags | ~45K | 🟢 Safe | 15-20% |
| **Wave 2** | Parallel Scanner Integration | ~68K | 🟢 Safe | 40-50% |
| **Wave 3** | Async File I/O | ~52K | 🟢 Safe | 50-60% |
| **Wave 4** | Batch Processing | ~75K | 🟡 Watch | 70-80% |
| **Wave 5** | CPU Optimizer & Affinity | ~58K | 🟢 Safe | 80-90% |

**Total Plan Tokens:** ~298K across 5 waves  
**Per-Wave Limit:** 197K (warning threshold)  
**All waves within safe operating bounds** ✅

---

## Wave 1: Import Wiring & CLI Flags

**Objective:** Add imports and command-line options without functional changes.

**Files to Modify:**
- `tools/generate_full_adg.py` (lines 1-50)

**Changes:**
```python
# Add imports after existing imports
from agentic_core.L2_execution.optimization.cpu_optimizer import AMDCPUOptimizer
from agentic_core.L2_execution.optimization.batch_processor import BatchProcessor
from agentic_core.L2_execution.optimization.parallel_file_processor import ParallelFileProcessor

# Add CLI argument
parser.add_argument('--parallel', action='store_true', help='Enable parallel processing')
parser.add_argument('--workers', type=int, default=None, help='Number of worker processes')
parser.add_argument('--cpu-affinity', action='store_true', help='Enable CPU affinity')
```

**Token Estimate:**
- System prompt: 2,500 tokens
- User prompt: 1,800 tokens
- Files: generate_full_adg.py (~300 lines) = ~35K tokens
- Diffs: ~200 lines = ~8K tokens
- **Total: ~47K tokens** 🟢

**Validation:**
- [ ] ADG generation still works (no --parallel flag)
- [ ] --help shows new flags
- [ ] No functional changes yet

**Commit:** `feat(cpu): Wave 1 - Import wiring and CLI flags`

---

## Wave 2: Parallel Scanner Integration

**Objective:** Wire parallel_scanner.py into ADG generation.

**Files to Modify:**
- `tools/generate_full_adg.py` (lines 200-250)
- `agentic_core/adg/extraction/parallel_scanner.py` (verify integration)

**Changes:**
```python
# In generate_full_adg.py scan section
if args.parallel:
    from agentic_core.adg.extraction.parallel_scanner import ParallelScanner
    scanner = ParallelScanner(
        repo_root=ROOT,
        include_tests=True,
        cache_path=cache_path,
        max_workers=args.workers
    )
else:
    scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True, cache_path=cache_path)
```

**Token Estimate:**
- System prompt: 3,000 tokens
- User prompt: 2,500 tokens
- Files: generate_full_adg.py + parallel_scanner.py = ~55K tokens
- Diffs: ~350 lines = ~12K tokens
- Prior step context: ~8K tokens
- **Total: ~80K tokens** 🟢

**Validation:**
- [ ] `--parallel` flag triggers parallel scanning
- [ ] CPU usage increases to 40-50%
- [ ] ADG output identical to sequential mode
- [ ] Determinism preserved

**Commit:** `feat(cpu): Wave 2 - Parallel scanner integration`

---

## Wave 3: Async File I/O

**Objective:** Add async file reading for I/O-bound operations.

**Files to Modify:**
- `agentic_core/adg/extraction/parallel_scanner.py`
- `agentic_core/L2_execution/optimization/async_file_ops.py`

**Changes:**
```python
# Add async file reading
import asyncio
import aiofiles

async def read_file_async(filepath):
    async with aiofiles.open(filepath, 'r') as f:
        return await f.read()

async def process_files_async(file_list):
    tasks = [read_file_async(f) for f in file_list]
    return await asyncio.gather(*tasks)
```

**Token Estimate:**
- System prompt: 2,800 tokens
- User prompt: 2,200 tokens
- Files: parallel_scanner.py + async_file_ops.py = ~42K tokens
- Diffs: ~280 lines = ~10K tokens
- Prior step context: ~12K tokens
- **Total: ~69K tokens** 🟢

**Validation:**
- [ ] File I/O is non-blocking
- [ ] CPU usage: 50-60%
- [ ] Memory usage stable
- [ ] ADG generation faster than Wave 2

**Commit:** `feat(cpu): Wave 3 - Async file I/O integration`

---

## Wave 4: Batch Processing Framework

**Objective:** Implement batch processing for large file sets.

**Files to Modify:**
- `agentic_core/adg/extraction/parallel_scanner.py`
- `agentic_core/L2_execution/optimization/batch_processor.py`

**Changes:**
```python
# Batch processing for large repos
from agentic_core.L2_execution.optimization.batch_processor import BatchProcessor

batch_size = 100  # files per batch
processor = BatchProcessor(batch_size=batch_size, max_workers=workers)

for batch in processor.create_batches(all_files):
    results = processor.process_batch(batch, process_func)
    # Aggregate results
```

**Token Estimate:**
- System prompt: 3,500 tokens
- User prompt: 2,800 tokens
- Files: parallel_scanner.py + batch_processor.py = ~68K tokens
- Diffs: ~420 lines = ~15K tokens
- Prior step context: ~15K tokens
- **Total: ~105K tokens** 🟡

**Validation:**
- [ ] Files processed in batches
- [ ] CPU usage: 70-80%
- [ ] No memory spikes
- [ ] Progress reporting per batch

**Commit:** `feat(cpu): Wave 4 - Batch processing framework`

---

## Wave 5: CPU Optimizer & Affinity

**Objective:** Enable AMD-specific CPU optimization and affinity.

**Files to Modify:**
- `tools/generate_full_adg.py` (main execution)
- `agentic_core/L2_execution/optimization/cpu_optimizer.py`

**Changes:**
```python
# CPU affinity and optimization
if args.cpu_affinity:
    from agentic_core.L2_execution.optimization.cpu_optimizer import AMDCPUOptimizer
    optimizer = AMDCPUOptimizer()
    optimizer.set_affinity()
    optimizer.optimize_for_parallel_workload()
    workers = optimizer.recommended_workers
```

**Token Estimate:**
- System prompt: 2,500 tokens
- User prompt: 2,000 tokens
- Files: generate_full_adg.py + cpu_optimizer.py = ~48K tokens
- Diffs: ~320 lines = ~12K tokens
- Prior step context: ~12K tokens
- **Total: ~76K tokens** 🟢

**Validation:**
- [ ] CPU affinity set on AMD processors
- [ ] CPU usage: 80-90%
- [ ] Workers match CPU core count
- [ ] Thermal throttling monitored

**Commit:** `feat(cpu): Wave 5 - CPU optimizer and affinity`

---

## Testing & Validation Strategy

### Per-Wave Testing
1. Unit tests for new functions
2. Integration test: `python tools/generate_full_adg.py --parallel --force`
3. CPU monitoring: `python tools/test_cpu_usage_adg.py`
4. Determinism check: Compare digests sequential vs parallel

### Regression Testing
- Scanner tests: 19/19 must pass
- Edge counts: Must match baseline
- Node counts: Must match baseline
- ADG digests: Must be deterministic

### Performance Benchmarks
```python
# Benchmark script
baseline_time = measure_sequential()
for wave in [1, 2, 3, 4, 5]:
    wave_time = measure_wave(wave)
    speedup = baseline_time / wave_time
    cpu_percent = measure_cpu()
    print(f"Wave {wave}: {speedup:.2f}x speedup, CPU: {cpu_percent:.1f}%")
```

---

## Rollback Plan

If any wave causes issues:
1. Revert commit for that wave
2. Verify ADG generation works without --parallel flag
3. Investigate in isolated environment
4. Retry with fixes

---

## CI/CD Integration

Add to `.github/workflows/adg.yml`:
```yaml
- name: CPU Optimization Test
  run: |
    python tools/generate_full_adg.py --parallel --force
    python tools/test_cpu_usage_adg.py
    python tools/verify_adg_determinism.py
```

---

## Success Metrics

| Metric | Baseline | Wave 5 Target | Measurement |
|--------|----------|---------------|-------------|
| CPU Utilization | 15-20% | 80-90% | psutil.cpu_percent() |
| ADG Generation Time | ~300s | ~60s | time command |
| Memory Usage | ~2GB | ~4GB | psutil.virtual_memory() |
| Determinism | ✅ | ✅ | SHA256 digests |
| Scanner Tests | 19/19 | 19/19 | pytest |

---

## Plan Approval

**Estimated Total Time:** 2-3 days  
**Risk Level:** Medium (parallel processing complexity)  
**Rollback Complexity:** Low (feature flag via --parallel)  
**Dependencies:** None (all infrastructure exists)  

**Prepared by:** Cascade  
**Date:** 2026-03-30  
**Plan ID:** `adg-cpu-integration-waves-8f7d9e`  
