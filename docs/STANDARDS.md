# Test Execution Standards

## Smoke Tests

### REQUIRED: Use Canonical Runner

Both SWE-1.5 and Opus-4.6 MUST use the canonical smoke test runner:

```bash
# Run ALL smoke tests (RECOMMENDED)
python run_smoke_tests.py

# Run specific phase
python run_smoke_tests.py --phase 1
python run_smoke_tests.py --phase 2
# etc.
```

### FORBIDDEN: Manual Phase Specification

DO NOT run tests with manually specified directories:

```bash
# ❌ FORBIDDEN - These cause discrepancies!
python -m pytest tests/smoke/adg tests/smoke/config tests/smoke/embeddings tests/smoke/health
python -m pytest tests/smoke/alerting tests/smoke/audit tests/smoke/backup tests/smoke/compliance
```

### WHY THIS MATTERS

1. **Missing Directories**: Manual phase runs miss 11 directories not in any phase:
   - `integration`, `logging`, `metrics`, `monitoring`, `observability`
   - `orchestration`, `performance`, `recovery`, `security`, `telemetry`, `workflows`

2. **Inconsistent Execution**: Different AI models may run different test sets

3. **False Confidence**: Tests may appear to pass while critical failures exist

### Phase Definitions

The canonical phase definitions are in `tests/smoke/conftest.py`:

```python
PHASE_DEFINITIONS = {
    'phase1': ['adg', 'config', 'embeddings', 'health'],
    'phase2': ['alerting', 'audit', 'backup', 'compliance'],
    'phase3': ['analytics', 'automation', 'dashboards', 'reporting'],
    'phase4': ['infrastructure', 'interfaces', 'layers', 'runtime', 'tracing', 'visualization'],
    'phase5': ['experimental', 'research', 'development', 'testing', 'deployment',
              'operations', 'maintenance', 'optimization', 'experimental_features',
              'beta_features', 'future_capabilities'],
    'additional': ['integration', 'logging', 'metrics', 'monitoring', 'observability',
                  'orchestration', 'performance', 'recovery', 'security', 'telemetry',
                  'workflows']
}
```

### Test Guidelines

1. **Always use `pytest.skip()` for unimplemented modules**
   ```python
   try:
       from agentic_core.some_module import SomeClass
       assert SomeClass is not None
   except ImportError as e:
       pytest.skip(f"some_module not yet implemented: {e}")
   ```

2. **Never use `pytest.fail()` for missing modules**

3. **All smoke tests must be marked with `@pytest.mark.smoke`**
   - This is automatically applied by `conftest.py`

4. **Tests should be fast and deterministic**
   - No external dependencies
   - No network calls
   - No file system writes

### Verification

To verify both models run the same tests:

```bash
# Run with canonical runner
python run_smoke_tests.py > canonical_output.txt 2>&1

# Extract test list
grep "tests/smoke/" canonical_output.txt | grep -E "(PASSED|SKIPPED|FAILED)" | sort > canonical_tests.txt

# Compare with any other run
diff canonical_tests.txt other_run_tests.txt
# Should produce no output if identical
```

### Enforcement

1. Pre-commit hooks check for `pytest.fail()` usage
2. CI pipelines must use `python run_smoke_tests.py`
3. Manual phase runs are logged as violations

### History

- **Issue**: SWE-1.5 passed individual phases, Opus-4.6 found 48 failures
- **Root Cause**: Phase-based runs missed 11 directories with `pytest.fail()` calls
- **Solution**: Canonical runner ensures identical test execution
