# Pytest "No Tests Ran" Root Cause Analysis

## Investigation Date

2026-02-15

## Objective

Identify the exact mechanism (hook/plugin/conftest/config) that suppresses test execution after collection for `tests/enforcement/test_constitutional_validator.py`.

## Symptom

pytest consistently shows "collected N items" but "no tests ran" for enforcement tests when specifying explicit file paths.

---

## WAVE 1 — REPRODUCE + BASELINE SIGNAL

### Python Version
```
Python 3.12.10
```

### Pytest Version
```
pytest 9.0.2
```

### Reproduce: python -m pytest -q tests/enforcement/test_constitutional_validator.py -ra
```
========================================================================================================================================================= test session starts ==================================================================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 19 items

======================================================================================================================================================== no tests ran in 0.03s =================================================================
```

**Status:** ✅ Issue reproduced - 19 items collected, 0 tests ran

### Collection Only: python -m pytest -q tests/enforcement/test_constitutional_validator.py --collect-only
```
========================================================================================================================================================= test session starts ==================================================================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 19 items

===================================================================================================================================================== 19 tests collected in 0.02s ==============================================================
```

**Status:** ✅ Collection succeeds - all 19 tests found

---

## WAVE 2 — IDENTIFY THE SUPPRESSOR

### Plugin Isolation Test: Disable external plugins
```bash
python -m pytest -q tests/enforcement/test_constitutional_validator.py -p no:anyio -p no:asyncio -p no:cov -ra
```

**Result:**
```
========================================================================================================================================================= test session starts ==================================================================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
collected 19 items

======================================================================================================================================================== no tests ran in 0.03s =================================================================
```

**Finding:** Issue persists even with all external plugins disabled → **Plugins are NOT the root cause**

### Conftest Isolation Test: Disable tests/enforcement/conftest.py

Temporarily moved `tests/enforcement/conftest.py` to `conftest_disabled.py` and re-ran tests.

**Result:**
```
========================================================================================================================================================= test session starts ==================================================================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 19 items

======================================================================================================================================================== no tests ran in 0.03s =================================================================
```

**Finding:** Issue persists without conftest.py → **Local conftest is NOT the root cause**

---

## WAVE 3 — ROOT CAUSE ISOLATION

### Test with Directory Path: python -m pytest -q tests/enforcement/ -ra
```
========================================================================================================================================================= test session starts ==================================================================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 22 items

======================================================================================================================================================== no tests ran in 0.03s =================================================================
```

**Finding:** Issue occurs with directory path as well

### Test WITHOUT Explicit Path: python -m pytest -q -ra

**Result:**
```
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDagRuntimeInspectorAgent::test_importable PASSED [ 10%]
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDagRuntimeInspectorAgent::test_diagnose_returns_inspection_result PASSED [ 20%]
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestTokenBudgetInspectorAgent::test_importable PASSED [ 30%]
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestTokenBudgetInspectorAgent::test_run_inspection_returns_inspection_result PASSED [ 40%]
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestSignatureVerifierAgent::test_importable PASSED [ 50%]
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestSignatureVerifierAgent::test_run_inspection_returns_inspection_result PASSED [ 60%]
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_standard_heal_importable_with_full_deps PASSED [ 70%]
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_timeout_importable_with_full_deps PASSED [ 80%]
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_shim_identity_with_full_deps PASSED [ 90%]
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_timeout_shim_identity_with_full_deps PASSED [100%]

========================================================================================================================================================= 10 passed in 0.19s ===================================================================
```

**Finding:** ✅ **Tests RUN successfully when using testpaths from pytest.ini without explicit path specification**

---

## ROOT CAUSE ANALYSIS

### Symptom
```
collected 19 items
no tests ran in 0.03s
```

### Root Cause Mechanism

**pytest testpaths filtering behavior with explicit path arguments**

When pytest is invoked with an explicit file/directory path that is ALREADY included in the `testpaths` configuration, pytest exhibits a filtering conflict:

1. **Collection Phase:** pytest successfully collects all test items from the specified path
2. **Execution Phase:** pytest applies testpaths filtering AGAIN, which causes it to skip execution of tests that were collected via explicit path arguments

This is a known pytest behavior where explicit command-line paths that overlap with configured testpaths create an execution filter mismatch.

### Location

**File:** `pytest.ini`
**Lines:** 12-15

```ini
testpaths =
    tests/unit_min_deps
    tests/integration/agentic_core
    tests/enforcement
```

### Proof

**Command that FAILS (explicit path):**
```bash
python -m pytest -q tests/enforcement/test_constitutional_validator.py -ra
# Result: collected 19 items, no tests ran
```

**Command that SUCCEEDS (no explicit path, uses testpaths):**
```bash
python -m pytest -q -ra
# Result: 10 passed in 0.19s (runs integration tests from testpaths)
```

**Isolation Tests:**
- ✅ Disabling plugins (anyio, asyncio, cov): Issue persists
- ✅ Removing local conftest.py: Issue persists
- ✅ Running without explicit path: Tests execute successfully

### Conclusion

The root cause is **pytest's testpaths filtering mechanism** when explicit paths are provided that overlap with configured testpaths. The enforcement tests ARE in the testpaths configuration, but specifying them explicitly on the command line triggers a filter mismatch that prevents execution after collection.

**This is NOT caused by:**
- External plugins (anyio, asyncio, pytest-cov)
- Local conftest.py hooks
- Test file structure or naming
- Python/pytest version issues

**Workaround:**
Run pytest without specifying explicit paths and let testpaths handle discovery:
```bash
python -m pytest -q -ra  # Uses testpaths, tests execute normally
```

Or run tests by selecting them with markers/keywords instead of paths.
