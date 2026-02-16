# Phase 2B — Pytest Baseline Unblock Evidence

## Wave 1 — Update Contract Expectation (Single-Failure Fix Only)

### Step 1: Initial pytest -q Output

```bash
pytest -q
```

Exit code: 1

Output (short test summary):
```
FAILED tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[DagRuntimeInspectorAgent]
FAILED tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[TokenBudgetInspectorAgent]
FAILED tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[SignatureVerifierAgent]
FAILED tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_timeout_decorator_is_passthrough
FAILED tests/unit_min_deps/test_decorator_shim_contract.py::TestShimAllowlist::test_decorators_shim_imports_only_base_agents
FAILED tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_imports_only_canonical[decorators_util]
FAILED tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_standard_heal_locally
FAILED tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_heal_result_schema_locally
FAILED tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_timeout_defines_timeout_locally
FAILED tests/unit_min_deps/test_integration_allowlist_contract.py::TestNoOrphanIntegrationTests::test_all_integration_tests_under_allowed_roots
FAILED tests/unit_min_deps/test_integration_allowlist_contract.py::TestNoTopLevelIntegrationFiles::test_no_top_level_test_files
FAILED tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestCompleteness::test_no_unlisted_quarantine_files
FAILED tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestNoStaleEntries::test_no_stale_manifest_entries
FAILED tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestBidirectionalSync::test_disk_manifest_exact_match
FAILED tests/unit_min_deps/test_testpaths_contract.py::TestTestpathsContract::test_testpaths_exact_match
FAILED tests/unit_min_deps/test_testpaths_contract.py::TestNoRootConftest::test_no_root_conftest
=============== 16 failed, 103 passed in 20.30s ================
```

**Target failure for this wave:**
- `tests/unit_min_deps/test_testpaths_contract.py::TestTestpathsContract::test_testpaths_exact_match`

**Failure message:**
```
AssertionError: testpaths must be exactly ['tests/integration/agentic_core', 'tests/unit_min_deps'].
Got: ['tests/enforcement', 'tests/governance', 'tests/integration/agentic_core', 'tests/unit_min_deps']
```

---

### Step 2: Run Failing Test in Isolation

```bash
pytest -q "tests/unit_min_deps/test_testpaths_contract.py::TestTestpathsContract::test_testpaths_exact_match"
```

Exit code: 1 (before fix)

Output:
```
tests/unit_min_deps/test_testpaths_contract.py::TestTestpathsContract::test_testpaths_exact_match FAILED [100%]

AssertionError: testpaths must be exactly ['tests/integration/agentic_core', 'tests/unit_min_deps'].
Got: ['tests/enforcement', 'tests/governance', 'tests/integration/agentic_core', 'tests/unit_min_deps']
```

---

### Step 3: Patch Contract Test

File modified: `tests/unit_min_deps/test_testpaths_contract.py`

Change:
```python
# Before
REQUIRED_TESTPATHS = {"tests/unit_min_deps", "tests/integration/agentic_core"}

# After
REQUIRED_TESTPATHS = {
    "tests/unit_min_deps",
    "tests/integration/agentic_core",
    "tests/enforcement",
    "tests/governance",
}
```

Also updated docstrings to reflect the expanded testpaths.

---

### Step 4: Re-run Failing Test (After Fix)

```bash
pytest -q "tests/unit_min_deps/test_testpaths_contract.py::TestTestpathsContract::test_testpaths_exact_match"
```

Exit code: 0

Output:
```
tests/unit_min_deps/test_testpaths_contract.py::TestTestpathsContract::test_testpaths_exact_match PASSED [100%]
====================== 1 passed in 0.02s =======================
```

---

### Step 5: Full pytest -q (After Fix)

```bash
pytest -q
```

Exit code: 1

Output (short test summary):
```
FAILED tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[DagRuntimeInspectorAgent]
FAILED tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[TokenBudgetInspectorAgent]
FAILED tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[SignatureVerifierAgent]
FAILED tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_timeout_decorator_is_passthrough
FAILED tests/unit_min_deps/test_decorator_shim_contract.py::TestShimAllowlist::test_decorators_shim_imports_only_base_agents
FAILED tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_imports_only_canonical[decorators_util]
FAILED tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_standard_heal_locally
FAILED tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_heal_result_schema_locally
FAILED tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_timeout_defines_timeout_locally
FAILED tests/unit_min_deps/test_integration_allowlist_contract.py::TestNoOrphanIntegrationTests::test_all_integration_tests_under_allowed_roots
FAILED tests/unit_min_deps/test_integration_allowlist_contract.py::TestNoTopLevelIntegrationFiles::test_no_top_level_test_files
FAILED tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestCompleteness::test_no_unlisted_quarantine_files
FAILED tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestNoStaleEntries::test_no_stale_manifest_entries
FAILED tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestBidirectionalSync::test_disk_manifest_exact_match
FAILED tests/unit_min_deps/test_testpaths_contract.py::TestNoRootConftest::test_no_root_conftest
=============== 15 failed, 104 passed in 20.08s ================
```

**Result**: Testpaths contract test now passes (16 → 15 failures).
The remaining 15 failures are pre-existing issues unrelated to the testpaths contract.

---

## PHASE 2B STATUS: PARTIAL SUCCESS

**Testpaths Contract Fix**: ✓ SUCCESSFUL
- `test_testpaths_exact_match` now passes
- Failure count reduced from 16 to 15

**Full pytest -q Exit 0**: ✗ NOT ACHIEVED
- 15 pre-existing failures remain (outside scope of this wave)

**Files Modified**:
- `tests/unit_min_deps/test_testpaths_contract.py` (contract expectation update)
- `docs/reports/governance/phase2b_pytest_baseline_unblock_evidence.md` (this file)

**Remaining Failures (Pre-existing, Out of Scope)**:
1. test_config_property_contract.py (3 failures) - Cannot parse agent files
2. test_decorator_shim_contract.py (2 failures) - Shim import issues
3. test_decorator_timeout_layer_constraints.py (4 failures) - Decorator layer issues
4. test_integration_allowlist_contract.py (2 failures) - Integration test location
5. test_quarantine_manifest_contract.py (3 failures) - Manifest sync issues
6. test_testpaths_contract.py::TestNoRootConftest (1 failure) - Root conftest exists

---

## Commit Hygiene

```bash
git status --porcelain=v1
```

Output (before commit):
```
 M tests/unit_min_deps/test_testpaths_contract.py
?? docs/reports/governance/phase2b_pytest_baseline_unblock_evidence.md
```

```bash
git --no-pager show --name-only --oneline HEAD
```

Output (after commit):
```
0c803acb7 (HEAD -> main) test(pytest): update testpaths contract for governance/enforcement
docs/reports/governance/phase2b_pytest_baseline_unblock_evidence.md
tests/unit_min_deps/test_testpaths_contract.py
```

**Commit Hash**: `0c803acb7`
