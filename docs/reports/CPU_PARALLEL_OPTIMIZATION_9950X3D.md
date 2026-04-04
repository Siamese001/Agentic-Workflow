# CPU Parallel Optimization Summary — AMD Ryzen 9950X3D

**Date**: 2025-04-02  
**CPU Target**: AMD Ryzen 9950X3D (16C/32T)  
**Objective**: Maximize CPU utilization across all parallel-enabled tools

---

## Files Updated with 9950X3D-Optimized Defaults

### 1. Pytest Configuration (Primary Test Runner)
**Files**: `pytest.ini`, `pyproject.toml`

**Changes**:
```ini
# pytest.ini
addopts = ... -n 32 --dist=load --timeout=180
```

**Before**: `-n auto --dist=loadfile` (inconsistent between files)  
**After**: `-n 32 --dist=load` (explicit 32 workers, work-stealing)

**Impact**: pytest now uses all 32 threads by default

---

### 2. ADG Test Accelerator
**File**: `tools/adg_test_accelerator.py`

**Change**:
```python
# Line 54
DEFAULT_WORKERS = 32  # Was: 4
```

**Impact**: ADG test selection and gap analysis now uses 32 workers

---

### 3. Batch Embedding Service
**File**: `agentic_core/L2_execution/engines/batch_embedding_service.py`

**Changes**:
```python
# Line 190
def __init__(self, batch_size: int = 32, max_workers: int = 16):
    # Was: max_workers: int = 4

# Line 279
def create_batch_embedding_service(batch_size: int = 32, max_workers: int = 16):
    # Was: max_workers: int = 4
```

**Rationale**: Embedding is I/O-bound; 16 threads balances throughput vs context switching

---

### 4. CPU Benchmark Tool
**File**: `tools/_benchmark_cpu.py`

**Changes**:
```python
# Worker sweep ranges updated
# B3: Parallel AST parse
for nw in [8, 16, 24, 32]:  # Was: [4, 8, 12, 16]

# B5: Parallel full visitor
for nw in [16, 24, 32]:  # Was: [8, 12, 16]

# B6: SHA-256 hashing
with ThreadPoolExecutor(max_workers=32) as ex:  # Was: max_workers=8
```

**Impact**: Benchmark now tests up to 32 workers to find optimal configuration

---

## Already Optimized (No Changes Needed)

### 5. CPU Optimizer (Auto-Detection)
**File**: `agentic_core/L2_execution/optimization/cpu_optimizer.py`

**Status**: ✅ Already uses `psutil.cpu_count()` for auto-detection

**Key Features**:
- Detects AMD vs Intel
- Uses physical cores (16) for compute-bound tasks
- Leaves headroom for >16 core systems
- Windows: ThreadPool (spawn overhead avoidance)
- Unix: ProcessPool (fast fork)

---

### 6. Parallel ADG Scanner
**File**: `agentic_core/adg/extraction/parallel_scanner.py`

**Status**: ✅ Uses `AMDCPUOptimizer` for dynamic worker selection

**Default**: `max_workers=None` → auto-detect via `get_optimal_workers()`

---

### 7. Parallel File Processor
**File**: `agentic_core/L2_execution/optimization/parallel_file_processor.py`

**Status**: ✅ Uses `AMDCPUOptimizer` for dynamic worker selection

**Default**: `max_workers=None` → auto-detect

---

### 8. ADG Generation Tool
**File**: `tools/generate_full_adg.py`

**Status**: ✅ CLI accepts `--workers` argument (defaults to auto)

**Usage**:
```bash
python tools/generate_full_adg.py --parallel --workers 32
```

---

## Parallel Opportunities Identified (Not Yet Optimized)

| File | Current | Recommended | Priority |
|------|---------|-------------|----------|
| `tools/execute_full_migration.py` | Hardcoded workers | Use cpu_optimizer | Medium |
| `tools/batch_fix_swe15.py` | Single-threaded | Add ThreadPool(32) | Low |
| `ops_scripts/dev_tools/l0_scripts/*.py` | Various hardcoded | Standardize to 32 | Low |

---

## Usage Commands (Post-Optimization)

### Run Tests with Max Parallelism
```bash
# Default (32 workers)
pytest tests/

# Serial tests (must run separately)
pytest tests/ -m serial -n0

# Specific worker count
pytest tests/ -n 24 --dist=load
```

### Run ADG Generation with Parallelism
```bash
# Auto-detect workers
python tools/generate_full_adg.py --parallel

# Explicit 32 workers
python tools/generate_full_adg.py --parallel --workers 32 --cpu-affinity
```

### Run ADG Test Accelerator
```bash
# Uses DEFAULT_WORKERS=32
python tools/adg_test_accelerator.py groups --workers 32

# Gap analysis
python tools/adg_test_accelerator.py gap --top 30
```

### CPU Benchmark
```bash
# Tests 8, 16, 24, 32 worker configurations
python tools/_benchmark_cpu.py
```

---

## Validation Checklist

- [x] pytest.ini: `-n 32 --dist=load --timeout=180`
- [x] pyproject.toml: `-n 32 --dist=load --timeout=180`
- [x] adg_test_accelerator.py: `DEFAULT_WORKERS = 32`
- [x] batch_embedding_service.py: `max_workers=16` (I/O bound)
- [x] _benchmark_cpu.py: Worker sweep up to 32
- [x] cpu_optimizer.py: Auto-detects 9950X3D (16P/32T)
- [x] parallel_scanner.py: Uses cpu_optimizer
- [x] parallel_file_processor.py: Uses cpu_optimizer
- [x] Pre-commit hook validates pytest config sync

---

## Expected CPU Utilization

| Scenario | Workers | Expected CPU% |
|----------|---------|---------------|
| pytest full suite | 32 | 85-95% |
| pytest unit only | 32 | 90-100% |
| ADG generation | 32 | 80-90% |
| ADG test accelerator | 32 | 70-80% |
| Embedding batch | 16 | 50-60% (I/O bound) |

---

## Related Files

- `.windsurf/rules/pytest-config-ssot.md` — Pytest config enforcement
- `.windsurf/pytest-optimization.md` — Usage guide
- `ops_scripts/ci/_validate_pytest_config.py` — Config validation
