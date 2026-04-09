# Pytest Parallel Optimization for Ryzen 9950X3D

## Quick Commands (Windsurf Terminal)

### Full Parallel (32 workers)
```bash
python -m pytest tests/ -n 32 --dist=loadfile --timeout=180 -v
```

### CI/CD Optimized (with coverage)
```bash
python -m pytest tests/ -n auto --dist=load --cov=agentic_core --cov-branch --timeout=180 --reruns=2
```

### Fast Feedback (unit tests only)
```bash
python -m pytest tests/ -m "unit and not serial" -n 32 --dist=load --timeout=60 -x
```

### Debug Mode (serial)
```bash
python -m pytest tests/ -n0 -v --tb=long --capture=no
```

## 9950X3D Tuning Parameters

### 1. Process Distribution Strategy
- `--dist=loadfile` (default): Groups tests by file, sends whole file to worker
- `--dist=load`: Work-stealing, better for uneven test durations
- `--dist=each`: Each test to every worker (for functional testing, slow)
- `--dist=no`: No distribution, forces all to master

### 2. Worker Process Management
- `-n auto`: Detects 32 logical cores on 9950X3D
- `-n 32`: Explicit 32 workers (avoid hyperthreading if thermally constrained)
- `-n 16`: Physical cores only (if memory-bound)
- `--maxprocesses=32`: Prevents fork-bomb on worker crashes

### 3. Memory Optimization
The 9950X3D has large L3 cache (128MB). For cache efficiency:
```bash
# Group related tests to improve cache locality
python -m pytest tests/unit/agentic_core/ -n 8 --dist=loadfile
```

## Serial Test Markers

Tests marked `serial` (Redis state, etc.) are excluded from parallel runs:
```bash
# Run serial tests separately
python -m pytest tests/ -m serial -n0 -v

# Run parallel tests only
python -m pytest tests/ -m "not serial" -n 32
```

## Windsurf-Specific Considerations

1. **Terminal Buffer**: Long parallel output may truncate. Use `--tb=short` or `--tb=no`
2. **Progress Display**: Add `-rN` to suppress summary, or use `pytest-rich` plugin
3. **Memory Pressure**: 32 workers × high memory tests can exhaust RAM. Monitor with:
   ```bash
   python -m pytest tests/ -n 32 --maxprocesses=16  # Cap at 16 if memory-limited
   ```

## Verification Commands

```bash
# Check xdist is active
python -m pytest tests/ --collect-only -q 2>&1 | head -5

# Verify worker count
python -m pytest tests/unit/agentic_core/adg/ -n 32 --dist=load -v --collect-only 2>&1 | grep -i "worker"

# Profile test duration distribution
python -m pytest tests/ --durations=20 -n 32
```
