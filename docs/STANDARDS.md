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

---

## Test Import Discipline

### The Problem: Collection-Time Import Failures

When pytest collects tests, it imports ALL test files simultaneously in a single Python interpreter. Eager (module-level) imports from heavy internal packages cause:

- **Import conflicts** between test files
- **Side-effect accumulation** (registry writes, config loading)
- **Order-sensitive failures** that don't appear in isolated runs
- **Silent collection errors** that block entire test suites

**Real example:** 262 collection errors found in `tests/unit/agentic_core/` that were invisible when running files individually.

### The Rule: No Side-Effectful Module-Level Imports

**FORBIDDEN in test files:**

```python
# ❌ FORBIDDEN - Eager imports at module scope
from agentic_core.L1_cognition.ml_decision_support.config.model_registry import ModelRegistry
from agentic_core.L4_state.memory.l1_exact_cache import L1ExactCache
from agentic_core.runtime.lifecycle_trace_contract import ExecutionTrace

# ❌ FORBIDDEN - Module-scope client/registry creation
registry = ModelRegistry()  # Triggers initialization
client = L1ExactCache()     # Singleton side effects
config = load_policy()      # Config hydration at import time
```

**REQUIRED: Lazy import pattern:**

```python
# ✅ REQUIRED - Fixture-based lazy imports
import pytest

@pytest.fixture
def model_registry():
    from agentic_core.L1_cognition.ml_decision_support.config.model_registry import ModelRegistry
    return ModelRegistry()

def test_something(model_registry):
    registry = model_registry  # Import happens at test runtime, not collection
    # ... test code
```

### Risky Import Roots

The following packages require lazy imports in test files:

- `agentic_core` (all subpackages)
- `apps_exec`, `apps_eval`, `apps_rg`, `apps_lic`, `apps_research`, `apps_rfp`
- `apps_shared.bootstrap`, `apps_shared.runtime`
- `system_learning.runtime`
- `tools.adg`

**Safe imports (no lazy required):**
- Standard library: `typing`, `pathlib`, `dataclasses`, `pytest`, `unittest`
- Common third-party: `numpy`, `pandas`, `pydantic`, `yaml`

### Detection & Enforcement

**1. Pre-Commit Hook (Fast feedback):**
```bash
# Blocks commit if eager imports detected
pre-commit run eager-import-lint
```

**2. CI Collection Gate (Source of truth):**
```bash
# Pytest collection must pass with zero errors
python -m pytest tests/ --collect-only -q
```

**3. AST Linter (Detailed analysis):**
```bash
# Generate detailed report
python tools/lint_eager_imports.py tests --json report.json --fix-report
```

**4. ADG Collection Safety (Secondary signal):**
```bash
# Structural dependency analysis
python tools/adg_test_accelerator.py collection-safety --json out.json
```

### Control Stack Priority

1. **CI collect-only gate** → Hard fail on any collection error
2. **AST eager import lint** → Detect risky patterns pre-commit
3. **ADG risk analysis** → Structural/dependency issues

### Remediation Guide

**If the linter flags your import:**

1. **Move to fixture:**
   ```python
   # Before
   from agentic_core.X import HeavyClass
   
   # After
   @pytest.fixture
   def heavy_class():
       from agentic_core.X import HeavyClass
       return HeavyClass
   ```

2. **Use local import in test function:**
   ```python
   def test_something():
       from agentic_core.X import HeavyClass
       obj = HeavyClass()
   ```

3. **Add to fixture parameters:**
   ```python
   def test_something(model_registry, heavy_class):
       # Fixtures handle lazy imports
       pass
   ```

### Why This Matters

- **Individual test runs pass** → `pytest test_file.py -v` ✅
- **Full collection fails** → `pytest tests/ --collect-only` ❌

The failure mode is invisible until you run full-suite collection. These rules ensure collection safety before code reaches CI.

---

## Enforcement Checklist

- [ ] No side-effectful module-level imports in tests
- [ ] No module-level client creation
- [ ] No module-level registry writes
- [ ] No module-level config or policy hydration
- [ ] Heavy internal imports use fixtures or local imports
- [ ] Full-suite collection passes: `pytest tests/ --collect-only`
- [ ] Pre-commit hook passes: `pre-commit run eager-import-lint`

---
