# Testing Standards Consolidation Analysis

## Current Fragmented Testing Requirements

###Mapped Requirements Across Sections:

**§1. TESTING & EVIDENCE (Primary)**
- 1.1 Zero-tolerance: every changed line of logic MUST have deterministic tests
- 1.2 Test-first discipline
- 1.3 Deterministic tests only
- 1.4 No mocks for integration seams
- 1.5-1.9 Required test coverage (Edge cases, State transitions, Determinism, Fail-closed, Matrix)
- 1.10 Ingress-path rule
- 1.11 Regression tests
- 1.12 Zero-tolerance for test skipping and xfail drift

**§5.2 Graph-backed test selection**
- Test selection MUST be dependency-graph-backed
- 5.2.1 NodeID-first testing discipline

**§11. TEST QUALITY ENFORCEMENT**
- No silent exception swallowers
- No zero-assert / fake-healthy tests
- No non-strict xfail

**§12. BAN SKIP DRIFT AT COLLECTION TIME**
- Test skips MUST be in allowlist
- Required skip metadata
- Forbidden reasons

**§13. TEST-COUNT AND COLLECTION-COUNT INVARIANTS**
- Test counts are invariants
- Baseline tracking

**§14.4 Test-file edit restriction**
- Test-file edits FORBIDDEN unless cluster root cause is in test infrastructure

**§17. PRE-EXISTING SKIP REGISTRY & CONVERGENCE GATE**
- Skip registry requirements
- Convergence blocking conditions

## Enforcement Scripts Mapping

| Requirement | Enforcement Script(s) |
|-------------|---------------------|
| Test quality gates | check_test_integrity.py, check_no_unconditional_xfail.py, check_utility_silent_swallowers.py |
| Skip management | check_skip_convergence_gate.py, skip_quarantine_check.py |
| Test count invariants | check_test_integrity.py |
| ADG proof artifacts | check_adg_proof_artifact_truthfulness.py |
| ADG schema | check_adg_schema_field_names.py |
| Policy drift | check_policy_drift_classification.py |
| Environment contract | check_environment_contract.py |
| C0 boundary | check_c0_boundary.py |
| Critical infrastructure | check_utility_silent_swallowers.py |
| Timeout progress | validate_timeout_progress.py, validate_timeout_recovery.py |

## Redundancies Identified

1. **Deterministic requirements** appear in §1.3, §1.7, §3.3, §7
2. **Skip management** scattered across §1.12, §12, §17
3. **Test quality** fragmented across §1.1-1.4, §11
4. **Enforcement references** scattered throughout 10+ sections

## Proposed Consolidated Structure

```
§1. TESTING FRAMEWORK
├── 1.1 Coverage Requirements (consolidates 1.5-1.9, 1.11)
├── 1.2 Quality Standards (consolidates 1.1-1.4, 1.10, 11)
├── 1.3 Test Selection & Execution (consolidates 5.2, 5.2.1, 14.4)
├── 1.4 Skip Management (consolidates 1.12, 12, 17)
├── 1.5 Test Count Invariants (consolidates 13)
├── 1.6 Enforcement Registry (centralizes all CI scripts)
└── 1.7 Evidence Requirements (consolidates scattered evidence rules)
```

## Signal Preservation Guarantee

Every existing requirement will be preserved:
- ✅ All edge case requirements (including negative tests)
- ✅ All deterministic testing requirements
- ✅ All skip management rules
- ✅ All enforcement script mappings
- ✅ All evidence requirements
- ✅ All CI gate conditions

Zero signal loss - consolidation only improves organization and clarity.

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

