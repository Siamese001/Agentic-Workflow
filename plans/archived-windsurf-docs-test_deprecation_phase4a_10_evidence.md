---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\test_deprecation_phase4a_10_evidence.md'
original_relative_path: 'test_deprecation_phase4a_10_evidence.md'
source_sha256: 033c0dcccb2222e10bdbf3b85830c74d2da9516094fdae9f9ef24dbf015cd95e
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Test Deprecation Phases 4a-10 Evidence

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

Phases 4a through 10 of the hardened test deprecation plan:
- Phase 4a: Rewrite 103 B1 imports (namespace moved) + delete 18 unfixable B1
- Phase 5: Repair Cat D — rewrite 14 + delete 54 unfixable
- Phase 6: Fix Cat E runtime target (1 file)
- Phase 7: Add agentic_core/_compat/ shim package (3 files)
- Phase 8: Add 4 CI guards + clean 5 remaining violations
- Phase 9: Backfill introduced_commit + owner_agent into quarantine manifest (75 entries)
- Phase 10: Final cleanup — 8 D escapees + fix stale CI ceilings + document skips

## CODE_COMMIT

0e60b82b2

## EVIDENCE_COMMIT

c338cdf8c

## FILES_CHANGED_CODE

docs/reports/plans/KNOWN_FAILING_TESTS.md
ops_scripts/ci/skip_quarantine_check.py
ops_scripts/general/dep_graph_scan.py
tests/unit/agentic_core/L0_routing/enforcement/test_registry_hard_fail.py
tests/unit/agentic_core/L5_safety/enforcement/test_compliance_audit_manager.py
tests/unit/agentic_core/L5_safety/validators/test_global_routing_rigor.py
tests/unit/agentic_core/test_compliance_audit_manager.py
tests/unit/agentic_core/test_global_routing_rigor.py
tests/unit/agentic_core/test_registry_hard_fail.py
tests/unit/agentic_core/test_route_decision_artifact_contract.py
tests/unit/structure_blueprint/test_allowed_global_territories.py

## FILES_CHANGED_EVIDENCE

PENDING

## INSPECTED_FILES

tests/_quarantine/QUARANTINE_MANIFEST.json
tests/unit_min_deps/test_quarantine_manifest_contract.py
ops_scripts/ci/scan_broken_test_imports.py
ops_scripts/ci/scan_duplicate_tests.py
ops_scripts/ci/skip_quarantine_check.py
agentic_core/_compat/__init__.py
agentic_core/_compat/l5_safety_aliases.py
agentic_core/_compat/apps_engines_aliases.py
tests/unit/test_mixin_consolidation_regression.py

## Collection Count

$ python -m pytest --collect-only -q --color=no
17484 tests collected in 4.49s

Baseline (Phase 0): 18019 tests, 22 errors
Phase 10 final:     17484 tests, 0 errors
Delta:              -535 tests collected, -22 collection errors

## CI Guard 1+3: Broken Import Scanner

$ python ops_scripts/ci/scan_broken_test_imports.py
Broken import scan: fully_orphaned=0  threshold=0
OK: fully_orphaned=0 <= 0
Stale mirror scan: stale_mirrors=0  threshold=0
OK: stale_mirrors=0 <= 0

## CI Guard 4: Duplicate Test Detector

$ python ops_scripts/ci/scan_duplicate_tests.py
Duplicate test scan: found=0  threshold=0
OK: duplicate_tests=0 <= 0

## CI Guard 2: Skip Ratio + Quarantine Gate

$ python ops_scripts/ci/skip_quarantine_check.py
  skip_ratio=0.001  ratio_ceiling=0.05  test_files=2982
Skip/Quarantine Enforcement Gate (non-bypassable):
  skip: count=3  ceiling=25  delta=-22
  quarantine: count=75  ceiling=75  delta=0
  documented_files=11  quarantined_files=75
  files_with_skips=3
PASS: all skips documented, ceilings enforced, critical tests clean

## Quarantine Contract Tests

$ python -m pytest tests/unit_min_deps/test_quarantine_manifest_contract.py -q --color=no
8 passed in 0.03s

## Phase Summary (Commits)

| Phase | Commit | Description |
|-------|--------|-------------|
| 4a | 6bab54715 | Rewrite 103 B1 imports + delete 18 unfixable B1 |
| 5 | 035dbd9c4 | Rewrite 14 D imports + delete 54 unfixable D |
| 6 | a4608e942 | Fix Cat E runtime target _config_compat -> config_compat_mixin |
| 7 | facf8287a | Add _compat shim package (3 shim files) |
| 8 | 2473ac873 | Add 4 CI guards + clean 5 violations |
| 9 | fa7f9a2af | Backfill introduced_commit+owner_agent into manifest (75 entries) |
| 10 | 0e60b82b2 | Final cleanup 8 D escapees + stale ceilings + skip docs |

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

