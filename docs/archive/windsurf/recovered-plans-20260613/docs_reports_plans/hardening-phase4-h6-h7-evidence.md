# Hardening Phase 4: H6 + H7 Evidence

**Phase:** 4 / Wave 3 (FINAL)
**Date:** 2026-02-18
**Branch:** adaptive_control
**Baseline:** 8d88d2e0c

---

## Objective

Implement H6 (AST-based learning seam compliance test) and H7 (formal tier lattice with property-based tests).

## Scope Declaration

| File | Intent |
|---|---|
| `tests/governance/test_learning_seam_compliance.py` | New: H6 AST compliance test (6 tests) |
| `agentic_core/L5_safety/types/tier_lattice_types.py` | New: H7 TierLattice, BackpressurePolicy, LearningTier |
| `tests/governance/test_tier_lattice.py` | New: H7 property-based tests (279 parametrized) |
| `docs/reports/plans/hardening-phase4-h6-h7-evidence.md` | This evidence file |

Planned impacted files: N=4

## H6: AST-Based Learning Seam Compliance

- AST scanner (not inspect.stack) verifies agent files
- No non-L2/L4 agent imports persistence modules (redis, pinecone, sqlite3, sqlalchemy, pymongo)
- No non-L2/L4 agent calls durable write functions (pickle.dump, shelve.open)
- L0 learning seam file exists and exports LearningArtifactIntent + LearningPersistenceService
- Scanner is deterministic and produces results
- L2 (execution) and L4 (state) excluded from scan — they are authorized persistence layers

### H6 Tests: 6 passed

```
TestNoDirectPersistenceImport::test_no_persistence_imports_in_agents PASSED
TestNoForbiddenWriteCalls::test_no_direct_write_calls_in_agents PASSED
TestLearningSeamExists::test_learning_seam_file_exists PASSED
TestLearningSeamExists::test_learning_seam_exports_intent PASSED
TestASTScannerDeterminism::test_agent_file_collection_deterministic PASSED
TestASTScannerDeterminism::test_scanner_produces_results PASSED
```

## H7: Formal Tier Lattice

- `LearningTier` IntEnum: L0–L6
- `TierLattice` frozen dataclass with `dominates(a, b)` strict partial order
- `DropPolicy` enum: SAFE, UNDER_PRESSURE, NEVER
- `BackpressurePolicy` delegates to lattice for drop decisions
- `validate_escalation_sequence()` enforces monotonicity

### H7 Lattice Invariants (all verified exhaustively)

1. **Irreflexivity**: 7 tests (all tiers) — no self-dominance
2. **Antisymmetry**: 42 tests (all ordered pairs) — if a > b then not b > a
3. **Transitivity**: 210 tests (all ordered triples) — if a > b > c then a > c
4. **Escalation monotonicity**: 5 tests — ascending/flat valid, descending rejected

### H7 Additional Tests

- Drop policy: 7 tests (L0 safe, L1 under pressure, L2+ never)
- can_drop: 4 tests (pressure flag respected)
- BackpressurePolicy: 3 tests (delegation to lattice)
- Completeness: 1 test (21 distinct pairs verified)

### H7 Total: 279 parametrized tests passed

## Full Governance Suite

```
python -m pytest tests/governance/ -q --tb=short

546 passed in 49.86s
```

Previous: 261 passed. Current: 546 passed (+285: 6 H6 + 279 H7).

## Acceptance

- [x] H6: 6/6 AST compliance tests pass
- [x] H7: 279/279 property-based lattice tests pass
- [x] Full governance suite: 546/546 pass
- [x] No regressions
- [x] Scope matches declaration (4 files)

---

## Hardening Roadmap Complete

All 8 hardening items (H0–H7) implemented across 4 phases:

| Phase | Items | Commit | Tests Added |
|---|---|---|---|
| 1 | H0 + H5 | 0c4c68468 | +14 (5 fixed + 9 new) |
| 2 | H1 + H2 | ffbb3c860 | +29 (11 + 18) |
| 3 | H3 + H4 | 8d88d2e0c | +29 (15 + 14) |
| 4 | H6 + H7 | (this commit) | +285 (6 + 279) |

**Total governance tests: 546 (was 189 pre-hardening)**

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

