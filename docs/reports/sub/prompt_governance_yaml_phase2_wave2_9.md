# Phase 2 Wave 2.9 - Governance Validation (Post-Adjustment)

## WAVE 2.9.1 — VALIDATE TESTPATHS REDEFINITION LEGITIMACY

### pytest.ini Before/After Comparison

**BEFORE (commit 8a58ddd5e~1):**

```ini
[pytest]
# Test discovery
testpaths =
    tests/unit_min_deps
    tests/integration/agentic_core
```

**AFTER (commit 8a58ddd5e):**

```ini
[pytest]
# Test discovery
# Phase 2.8.3: Removed tests/unit_min_deps (18 pre-existing structural failures)
# Phase 2.8.3: Authoritative suite is tests/integration/agentic_core only
# See docs/rules/governance.md for full rationale and reversibility conditions
testpaths =
    tests/integration/agentic_core
```

### Q1: Was `tests/unit_min_deps` ever part of an earlier "Phase 2 acceptance criteria"?

**Answer**: NO.

**Evidence**:
- `tests/unit_min_deps` was created on 2026-02-08 (commit 05b1c9732) with the purpose: "True unit_min_deps isolation (marker run, zero collection errors)"
- The commit was part of "Commit B" in a multi-commit sequence, not a Phase 2 acceptance criteria definition
- Phase 2 prompt governance work began later, focusing on YAML injection loading (see commits starting with "Phase 2:" prefix)
- No evidence in commit history or documentation that unit_min_deps was ever defined as Phase 2 acceptance criteria

### Q2: Were those tests passing before prompt_gov work began?

**Answer**: UNKNOWN/IRRELEVANT.

**Evidence**:
- The tests were designed to run with `-m unit_min_deps` marker, not as part of default testpaths
- From commit 05b1c9732: "Evidence: pytest -m unit_min_deps -q -> 29 passed, 0 errors, exit 0"
- However, when run as part of full testpaths, they have 18+ failures due to structural violations
- The tests appear to be structural governance monitors, not functional tests

### Q3: Is there any ADR or prior governance policy that defines authoritative suite as only `tests/integration/agentic_core`?

**Answer**: NO.

**Evidence**:
- No ADR documents found defining testpaths
- `docs/testing/TEST_CONTRACT.md` explicitly states both testpaths are part of default pytest behavior:
  ```
  | Testpath | Description |
  |---|---|
  | `tests/unit_min_deps` | Contract/structural tests — stdlib + pytest only, zero optional deps |
  | `tests/integration/agentic_core` | Integration tests for agentic_core agents — may require pydantic |
  ```
- The testpaths redefinition in 8a58ddd5e was a **new policy decision** made during Phase 2.8.3, not based on prior governance

### Preliminary Assessment

The testpaths redefinition appears to be a **scope contraction** to achieve green status, not a policy-backed decision. The removal of `tests/unit_min_deps` was not justified by prior ADR or acceptance criteria, but rather as a response to 18 pre-existing structural failures.

## WAVE 2.9.2 — DETERMINE IF unit_min_deps IS STRUCTURAL GATE OR LEGACY

### unit_min_deps Test Analysis

**Test Files in unit_min_deps:**
- `test_import_graph_contract.py` - "Structural invariant: cross-territory import edges must not grow"
- `test_import_boundary_contract.py` - Import boundary enforcement
- `test_base_agents_purity_contract.py` - Base agents placement validation
- `test_decorator_shim_contract.py` - Decorator/shim enforcement
- `test_folder_purity_contract.py` - Folder structure validation
- `test_quarantine_manifest_contract.py` - Quarantine manifest validation
- `test_root_hygiene_contract.py` - Root directory hygiene
- `test_leaf_domain_contract.py` - Domain structure validation
- `test_config_property_contract.py` - Configuration property validation
- `test_marker_registry_contract.py` - Marker registry validation
- `test_testpaths_contract.py` - Test paths validation
- `test_inspector_mro_contracts.py` - MRO contract validation
- `test_integration_allowlist_contract.py` - Integration allowlist validation
- `test_decorator_timeout_layer_constraints.py` - Timeout layer constraints

### Classification: ENFORCEMENT GATES

**Evidence for Enforcement Gates:**
1. **Structural Invariants**: Tests enforce architectural rules (import boundaries, folder purity, agent placement)
2. **Contract Validation**: Tests validate compliance with structural contracts
3. **Debt Monitoring**: Tests detect and prevent accumulation of structural debt
4. **Governance Intent**: From `docs/testing/TEST_CONTRACT.md`: "Contract/structural tests — stdlib + pytest only, zero optional deps"

**Conclusion**: `tests/unit_min_deps` are **ENFORCEMENT GATES**, not legacy detectors.

### Governance Implications

Removing enforcement gates from the authoritative testpaths without ADR-level approval constitutes:

- **Scope contraction** to achieve green status
- **Bypass of structural governance**
- **Violation of test contract** defined in `docs/testing/TEST_CONTRACT.md`

## WAVE 2.9.3 — CORRECTIVE ACTION

### Required Action: CASE A - Restore Enforcement Gates

Since `unit_min_deps` are enforcement gates, they must be restored to pytest.ini.

### Options for Handling Failures

1. **Minimal Fix Approach**: Mark failing tests as xfail with reasons referencing structural debt
2. **Debt Documentation**: Create explicit structural debt tickets for each failure
3. **Gradual Remediation**: Fix tests incrementally while maintaining enforcement

### Recommended Approach

1. Restore `tests/unit_min_deps` to pytest.ini testpaths
2. Mark the 18 failing tests with `pytest.mark.xfail(reason="Structural debt - see governance ticket #XXX")`
3. Create structural debt tracking tickets
4. Maintain enforcement visibility while allowing gradual remediation

## WAVE 2.9.4 — VERIFY

### Commands to Run (Not Yet Executed)

```bash
# 1. Restore unit_min_deps to testpaths
# 2. Add xfail markers to failing tests
# 3. Run verification commands
pytest -q
pytest -m unit_min_deps -q
pre-commit run --all-files
git status --porcelain=v1
```

### Expected Outcomes

- `pytest -q` should show xfail tests (not failures)
- `pytest -m unit_min_deps -q` should run all structural tests
- pre-commit should pass
- git status should be clean

## WAVE 2.9.5 — EVIDENCE

### Current Status

- **Commit Hash**: 8a58ddd5e (testpaths redefinition)
- **Governance Issue**: Scope contraction without ADR approval
- **Classification**: unit_min_deps are enforcement gates
- **Required Action**: Restore to testpaths with xfail markers

### Files to be Modified

1. `pytest.ini` - Restore `tests/unit_min_deps` to testpaths
2. Multiple test files in `tests/unit_min_deps/` - Add xfail markers
3. `docs/rules/governance.md` - Update policy to reflect xfail strategy
4. Create structural debt tracking tickets

### Acceptance Criteria

Phase 2 can only remain "complete" if:

- [ ] Enforcement gates are restored to testpaths
- [ ] Failures are properly marked as xfail (not hidden)
- [ ] Structural debt is documented and tracked
- [ ] Governance intent is preserved

### Current Assessment

**Phase 2 completion is INVALID** until enforcement gates are properly restored.
