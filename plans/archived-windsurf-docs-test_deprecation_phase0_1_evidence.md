---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\test_deprecation_phase0_1_evidence.md'
original_relative_path: 'test_deprecation_phase0_1_evidence.md'
source_sha256: 2c593d5930c6f0a0a5fb93fc2fcefe1b874f18e27e0bbd683c5fda1ae989f3b2
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Test Deprecation Phase 0+1 — Baseline Capture + Delete Cat C Stubs

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

Phase 0: Deterministic baseline capture (no file changes).
Phase 1: Delete 502 Cat C direct-skip stubs (all tests are `pytest.skip("Implementation pending")`).
Scope N = 502 deletions in `tests/unit/`.

## CODE_COMMIT

ea068e9d86e2d5b00c561b88b5e8ee8adfc2e1c9

## EVIDENCE_COMMIT

PENDING

## FILES_CHANGED_CODE

502 test files deleted — see git show ea068e9d8 for full list.

## FILES_CHANGED_EVIDENCE

docs/reports/plans/test_deprecation_phase0_1_evidence.md

## INSPECTED_FILES

C:/Users/amita/.windsurf/plans/_scan_results_e92eb2.json
tests/unit_min_deps/test_quarantine_manifest_contract.py
ops_scripts/ci/skip_quarantine_check.py
pytest.ini

## Phase 0 Baseline

### $ git branch --show-current
test_deprecation

### $ python -m pytest --collect-only -q --color=no
21586 tests collected, 33 errors in 6.87s
EXIT CODE: 1 (33 pre-existing collection errors — unchanged throughout)

### $ python ops_scripts/ci/skip_quarantine_check.py
Skip/Quarantine Enforcement Gate (non-bypassable):
  skip: count=11  ceiling=25  delta=-14
  quarantine: count=75  ceiling=49  delta=26
  documented_files=9  quarantined_files=75
  files_with_skips=5
FAIL: 6 violation(s) — all pre-existing:
  - Critical test file missing: tests/core/test_executor_smoke.py
  - Critical test file missing: tests/core/test_executor_dispatch_snapshot.py
  - 3 undocumented skips
  - Quarantine entries 75 exceeds gate ceiling 49

## Phase 1 Delete

### $ python batch_git_rm (502 files in 6 batches of 100)
Batch 1: removed 100 files
Batch 2: removed 100 files
Batch 3: removed 100 files
Batch 4: removed 100 files
Batch 5: removed 100 files
Batch 6: removed 2 files
Done. Errors: 0

### $ python -m pytest --collect-only -q --color=no (post-delete)
19073 tests collected, 33 errors in 5.26s
Collection delta: -2513 tests (expected ~502 files x ~5 tests/file avg)
Collection errors: 33 (unchanged)

### $ git diff --cached --name-only | Measure-Object -Line
502 files staged

### $ git commit
ea068e9d8 deprecation: delete 502 Cat C direct-skip stubs (Phase 1)

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

