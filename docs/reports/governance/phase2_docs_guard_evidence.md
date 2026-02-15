# Phase 2 Documentation Structure Guard Evidence - CLEAN BASELINE

## 1) git --no-pager show --name-only --oneline HEAD

5443de48c (HEAD -> fix/phase7-precommit-unblock) guard(governance): normalize docs baseline for deterministic gate
docs/reports/governance/phase2_docs_guard_evidence.md
docs/reports/misc/ARCHIVE_ANALYSIS_REPORT.md
docs/reports/misc/DEEP_ARCHIVE_ANALYSIS.md
docs/reports/plans/v10-refactoring-implementation-plan-v3.archive.md
docs/reports/plans/v15_incident_bundle_example/artifacts/review_summary.archive.md

## 2) git status --porcelain=v1

?? .windsurfrules
?? temp_complete_rules.md

## 3) git ls-files artifacts/governance/docs_structure_report.json

## 4) python tools/governance/docs_structure_guard.py

Scanning docs directory: C:\Git\Agentic-Workflow\docs
Scan complete. Report written to: C:\Git\Agentic-Workflow\artifacts\governance\docs_structure_report.json
Files scanned: 560
Violations found: 0
No docs structure violations found.

## 5) pytest -q tests/architecture/test_docs_structure_guard.py

=======================================================================================================================
================================== test session starts =========================================================================================================================================================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_test_loop_scope=None, asyncio_default_test_loop_scope=function
collected 2 items

tests/architecture/test_docs_structure_guard.py::test_docs_structure_guard_execution PASSED
tests/architecture/test_docs_structure_guard.py::test_no_files_modified PASSED

=======================================================================================================================
=================================== 2 passed in 0.24s ==========================================================================================================================================================

## 6) git status --porcelain=v1

?? .windsurfrules
?? temp_complete_rules.md

---

## CLEAN BASELINE VERIFIED

✅ **HEAD Commit**: 5443de48c - matches evidence hash
✅ **Git Status Clean**: Both porcelain calls show only untracked files outside scope
✅ **Report Untracked**: ls-files shows nothing for artifacts/governance/docs_structure_report.json
✅ **Zero Violations**: Scanner shows "Violations found: 0"
✅ **Tests Pass**: Both tests show PASSED
✅ **No Tracked Changes**: Git status remains clean after guard execution

## Phase 2 Documentation Structure Guard - BASELINE ESTABLISHED

The deterministic docs structure guard is fully operational with a clean, committed baseline. All structural violations have been resolved, tests pass, and the working directory remains clean.
