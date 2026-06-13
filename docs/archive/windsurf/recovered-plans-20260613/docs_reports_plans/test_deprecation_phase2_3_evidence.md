# Test Deprecation Phase 2+3 — Delete Cat G Duplicates + Cat F Mirror Tests

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Scope

Phase 2: Delete 42 Cat G `_1` suffix duplicate test files.
Phase 3: Delete 194 Cat F GENERATED_MIRROR_TEST files with broken importlib targets.
Scope N = 236 deletions in `tests/unit/`.

## CODE_COMMIT

2c57a762e2cff9e16e83c479a8bef74c6fae5d56

## EVIDENCE_COMMIT

PENDING

## FILES_CHANGED_CODE

236 files deleted (42 Cat G + 194 Cat F) — see git show 2c57a762e for full list.

## FILES_CHANGED_EVIDENCE

docs/reports/plans/test_deprecation_phase2_3_evidence.md

## INSPECTED_FILES

C:/Users/amita/.windsurf/plans/_scan_results_e92eb2.json

## Phase 2 Delete (Cat G)

### $ batch git rm Cat G (42 files)
G Batch 1: removed 42 files
Errors: 0

## Phase 3 Delete (Cat F)

### $ batch git rm Cat F (194 files)
F Batch 1: removed 100 files
F Batch 2: removed 94 files
Errors: 0

## Collection Verification

### $ python -m pytest --collect-only -q --color=no
Pre-phase: 19073 collected, 33 errors
Post-phase: 18280 collected, 32 errors
Delta: -793 tests, -1 collection error

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

