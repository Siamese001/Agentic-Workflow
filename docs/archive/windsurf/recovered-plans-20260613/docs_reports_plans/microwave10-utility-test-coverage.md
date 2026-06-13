# Micro-wave 10: Utility Test Coverage Completion

Complete test coverage for L5 safety utility modules created in micro-waves 7-9.

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| 10A | T1-T3 | bootstrap_util tests | 450 | 3 test cases | 🟢 | pytest passes, 100% util coverage |
| 10B | T4-T6 | code_validator_util tests | 680 | 4 validation types | 🟢 | pytest passes, edge cases covered |
| 10C | T7-T9 | credential_scanner_util tests | 620 | regex + patterns | 🟢 | pytest passes, mock file fixtures |
| 10D | T10-T12 | dependency_pruning_util tests | 580 | deptry mocking | 🟢 | pytest passes, dry-run verified |
| 10E | T13-T15 | architecture_governor_validator_util tests | 520 | dry-run mode | 🟢 | pytest passes, shim delegation OK |

**Total: 2,850 tokens across 5 micro-waves, all GREEN**

---

## Gap Register

**GAP-1: Missing unit tests for utility modules**
- 13 utility modules created in waves 7-9 lack dedicated test files
- Risk: utilities may have untested edge cases or regressions
- Impact: MEDIUM - utilities are shimmed but core logic needs validation

**GAP-2: No integration tests for shim→utility delegation**
- Agent shims delegate to utilities but delegation path untested
- Risk: signature mismatches or import errors may go undetected
- Impact: LOW - shims are backward compatibility layer

---

## Execution Plan

### Phase T1 — Bootstrap Utility Tests
**Scope**: Create tests/unit/agentic_core/L5_safety/utils/test_bootstrap_util.py

**Commands**:
```bash
# Create test file with fixtures
python -m pytest tests/unit/agentic_core/L5_safety/utils/test_bootstrap_util.py -v
```

**Acceptance**:
- test_verify_redis_connection_none_returns_false
- test_verify_critical_files_missing_file
- test_verify_critical_files_present
- test_run_bootstrap_healthy_status
- test_heal_bootstrap_issues_no_target_path

### Phase T2 — Code Validator Utility Tests  
**Scope**: Create tests/unit/agentic_core/L5_safety/utils/test_code_validator_util.py

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/utils/test_code_validator_util.py -v
```

**Acceptance**:
- test_validate_syntax_error
- test_validate_canon_wildcard_import
- test_validate_async_no_await
- test_validate_prints_detected
- test_ruleset_configuration

### Phase T3 — Credential Scanner Utility Tests
**Scope**: Create tests/unit/agentic_core/L5_safety/utils/test_credential_scanner_util.py

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/utils/test_credential_scanner_util.py -v
```

**Acceptance**:
- test_credential_scanner_compiles_patterns
- test_false_positive_detection
- test_aws_key_pattern_match
- test_scan_empty_directory
- test_generate_recommendations_high_severity

### Phase T4 — Dependency Pruning Utility Tests
**Scope**: Create tests/unit/agentic_core/L5_safety/utils/test_dependency_pruning_util.py

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/utils/test_dependency_pruning_util.py -v
```

**Acceptance**:
- test_find_unused_deptry_no_deptry_returns_empty
- test_remove_from_requirements_txt_dry_run
- test_pruning_result_dataclass
- test_heal_repository_no_unused

### Phase T5 — Architecture Governor Validator Utility Tests
**Scope**: Create tests/unit/agentic_core/L5_safety/utils/test_architecture_governor_validator_util.py

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/utils/test_architecture_governor_validator_util.py -v
```

**Acceptance**:
- test_validate_dry_run_mode
- test_to_check_dict_structure
- test_governance_validation_result_dataclass

---

## Rules

- One utility = one test file
- Tests must use tmp_path fixture for file operations
- Mock external dependencies (Redis, deptry, ADG)
- Test both happy path and failure paths
- Shim tests not required (backward compatibility only)

---

## Success Criteria

| Metric | Target | Verification |
|---|---|---|
| Test files created | 5 | ls tests/unit/agentic_core/L5_safety/utils/ |
| Tests passing | 100% | pytest --tb=short |
| Code coverage | ≥80% | pytest --cov |
| Mock usage | All external deps mocked | grep -r "Mock\|mock" test_*.py |

---

## Implementation Commands

```bash
# Phase T1: Bootstrap tests
python -c "
# Test content for bootstrap_util
# 5 test functions covering Redis, file verification, healing
"

# Phase T2: Code validator tests
python -c "
# Test content for code_validator_util
# 5 test functions covering syntax, canon, async, prints validation
"

# Phase T3: Credential scanner tests  
python -c "
# Test content for credential_scanner_util
# 5 test functions covering patterns, scanning, recommendations
"

# Phase T4: Dependency pruning tests
python -c "
# Test content for dependency_pruning_util
# 4 test functions covering deptry, pruning, dry-run
"

# Phase T5: Architecture governor tests
python -c "
# Test content for architecture_governor_validator_util
# 3 test functions covering validation, dry-run
"

# Final verification
python -m pytest tests/unit/agentic_core/L5_safety/utils/ -v --tb=short
```

---

## Rollback Strategy

If test creation fails:
1. Skip failing test phases
2. Document untested utilities in README
3. Create manual test checklist for CI
4. Revisit in future maintenance window

---

## Acceptance Criteria

- [ ] 5 test files created in tests/unit/agentic_core/L5_safety/utils/
- [ ] All tests pass with pytest
- [ ] External dependencies properly mocked
- [ ] No new test failures in existing suite
- [ ] Commit with message "Micro-wave 10: Add utility test coverage"
