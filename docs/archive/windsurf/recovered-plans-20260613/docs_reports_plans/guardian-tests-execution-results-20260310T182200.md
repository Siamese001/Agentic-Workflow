# Guardian Tests Execution Results

## Execution Summary
**Date:** 2026-03-10T18:22:00
**Environment:** Local Windows development
**V15_TEST_SIGNING:** Enabled

## Tests Successfully Executed

### 1. Sovereignty Interface Tests
- **File:** `tests/unit_min_deps/test_sovereignty_interfaces.py`
- **Result:** ✅ 27 passed in 0.09s
- **Coverage:** Authority blocks, proposal-only interfaces, dual injection requirements, sealed interface checks

### 2. Sovereignty Runtime Contract Tests
- **File:** `tests/guardian/test_sovereignty_runtime_contract.py`
- **Result:** ✅ 15 passed in 0.06s
- **Guardian Shield:** PASS with 0 violations
- **Coverage:** Bootstrap contracts, exception hierarchy, single-use enforcement

### 3. Agent Registry Hardened Tests
- **File:** `tests/guardian/test_agent_registry_hardened.py`
- **Result:** ✅ 28 passed in 0.17s
- **Guardian Shield:** PASS with 0 violations
- **Coverage:** Registry digest, gateway transitive enforcement, LLM API agent validation

### 4. ADG Graph Coverage Guardian Tests (H9)
- **File:** `tests/guardian/test_adg_graph_coverage_guardian.py`
- **Result:** ✅ 18 passed in 10.94s
- **Guardian Shield:** PASS with 0 violations
- **Coverage:** Graph evidence floors, scanner self-test, digest determinism, layer label coverage

### 5. ADG Scanner Governance Tests (S10)
- **File:** `tests/guardian/test_scanner_governance.py`
- **Result:** ✅ 7 passed in 0.19s
- **Guardian Shield:** PASS with 0 violations
- **Coverage:** Scanner self-governance, inheritance detection, dynamic exec detection

## Issues Identified and Fixed

### 1. Missing AGENTIC_CORE_DIR Constant
**Problem:** Multiple files had undefined `AGENTIC_CORE_DIR` references
**Fix Applied:** Added proper import from `agentic_core.L0_routing.config.path_constants`
**Files Fixed:**
- `agentic_core/L0_routing/utils/project_root_util.py`
- `agentic_core/adg/extraction/static_scanner.py`

### 2. V15 Signing Environment
**Problem:** Guardian execution required V15_TEST_SIGNING environment variable
**Fix Applied:** Set `V15_TEST_SIGNING=1` for test execution

## Tests with Import Issues (Currently Blocked)

The following tests have import issues that need similar fixes:
- `test_guardian_c0_sovereignty.py`
- `test_guardian_change_package_activation.py`
- `test_guardian_escalation_determinism.py`
- `test_guardian_gateway_bypass.py`
- `test_registry_completeness.py`
- Various V15 compliance tests missing `REPORTS_DIR` imports

## CI Workflow Alignment

The executed tests align with the GitHub Actions workflow `.github/workflows/guardian-tests.yml`:

1. ✅ Sovereignty interface tests
2. ✅ Core guardian tests (partial - working subset)
3. ✅ ADG graph coverage guardian (H9)
4. ✅ ADG scanner governance (S10)

## Guardian Shield Status

All executed tests show:
```
============================================================
GUARDIAN SHIELD: PASS
============================================================
JSON Report: C:\Git\Agentic-Workflow\agentic_core\L0_routing\logs\guardian_report.json
Violations: 0
============================================================
```

## Recommendations

1. **Complete Import Fixes:** Fix remaining import issues to enable full guardian test suite
2. **Automated Execution:** Integrate into local development workflow
3. **CI Parity:** Ensure local execution matches CI results exactly
4. **Artifact Verification:** Verify guardian artifacts are written to correct locations

## Evidence Location

Guardian reports are generated at:
- `agentic_core/L0_routing/logs/guardian_report.json`
- `docs/reports/verification/guardian/` (when aggregation works)

## Findings

[Document key findings from the investigation]

---

