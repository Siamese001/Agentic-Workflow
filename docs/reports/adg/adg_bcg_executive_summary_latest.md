## ADG Executive Brief

| Question | Answer |
|---|---|
| Can we merge? | No. ADG report consistency/runtime proof is not decision-grade. |
| What blocks merge? | Report consistency is FAIL; no red live blocker driver is present. |
| First engineering move | Fund mapped tests for unknown. Add mapped tests before touching this surface again. |
| What waits? | Non-blocking impact inventory, ratchets, dead-code cleanup, and broad graph ranking. |
| Audit caveat | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the blocker decision. |

Decision gate:

| Gate | Status | Evidence | Required before ranking |
|---|---|---|---|
| Merge decision | No. ADG report consistency/runtime proof is not decision-grade. | Can we merge? | Resolve before lower-severity ranking. |
| Merge decision | Report consistency is FAIL; no red live blocker driver is present. | What blocks merge? | Resolve before lower-severity ranking. |
| Merge decision | Fund mapped tests for unknown. Add mapped tests before touching this surface again. | First engineering move | Resolve before lower-severity ranking. |
| Merge decision | Non-blocking impact inventory, ratchets, dead-code cleanup, and broad graph ranking. | What waits? | Resolve before lower-severity ranking. |
| Merge decision | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the blocker decision. | Audit caveat | Resolve before lower-severity ranking. |

Fix now:

| Rank | Move | Evidence | Exit criterion |
|---:|---|---|---|
| 1 | Fund mapped tests for unknown. Add mapped tests before touching this surface again. | Add mapped tests/unit, tests/regression coverage for unknown. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 2 | Rerun ADG after the blocker fix; if report consistency still fails, repair the report pipeline before ranking lower-impact work. | Report consistency=FAIL. | Post-blocker ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining critical-impact counts after the rerun: live blocker drivers block merge; foundation-candidate/audit-net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation candidate inventory=not loaded; critical audit net=0; live blocker drivers=0. | Receipt shows open_blocker_fix_count=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the blocker rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=missing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Do not open a separate product/app workstream; validate app-owned wiring only if the blocker fix touches it. | No app-specific product gap was promoted in this run; app risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 6 | Keep deletion/deprecation cleanup after blockers, report consistency, and runtime proof are green unless cleanup blocks the fix. | No deletions are approved in this run because ADG found 0 confirmed dead-code candidates; reduce uncertainty first, then deprecate noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the blocker fix. |

ADG Run Metrics

| Metric | Value |
|---|---|
| Run ID | 06292026_0101 |
| Snapshot | 2026-07-13T10:50:26.691638+00:00 |
| SQLite snapshot | C:\Users\amita\AppData\Local\Temp\pytest-of-amita\pytest-4115\test_clean_certification_run_r0\snap.sqlite |
| Audit caveat | REPORT_INCONSISTENT; report consistency=FAIL |
| FIX gates (all bands) | 0 |
| Open critical gate drivers | 0 |
| Open blocker queue | no open blocker or candidate-blocker rows |
| Top FIX gate | none |
| Action rows | 1 |
| Decision ledgers | foundation candidate inventory=not loaded; critical audit net=0; live blocker drivers=0 |
| Runtime proof | missing |
| Testing hotspot | unknown; risk=HIGH |

Impact Inventory

| Band | Impact severity | Gross | Guardian exempted | Net | Foundation candidates | Live blocker drivers |
|---|---|---|---|---|---|---|
| P0 | critical | 0 | 0 | 0 | not loaded | 0 |
| P1 | high | 0 | 0 | 0 | n/a | 0 |
| P2 | medium | 0 | 0 | 0 | n/a | 0 |
| P3 | low | 0 | 0 | 0 | n/a | 0 |

### Recommended Next Steps

| Priority | Action | Evidence | Exit criterion |
|---|---|---|---|
| 1 | Fund mapped tests for unknown. Add mapped tests before touching this surface again. | Add mapped tests/unit, tests/regression coverage for unknown. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 2 | Rerun ADG after the blocker fix; if report consistency still fails, repair the report pipeline before ranking lower-impact work. | Report consistency=FAIL. | Post-blocker ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining critical-impact counts after the rerun: live blocker drivers block merge; foundation-candidate/audit-net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation candidate inventory=not loaded; critical audit net=0; live blocker drivers=0. | Receipt shows open_blocker_fix_count=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the blocker rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=missing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Do not open a separate product/app workstream; validate app-owned wiring only if the blocker fix touches it. | No app-specific product gap was promoted in this run; app risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 6 | Keep deletion/deprecation cleanup after blockers, report consistency, and runtime proof are green unless cleanup blocks the fix. | No deletions are approved in this run because ADG found 0 confirmed dead-code candidates; reduce uncertainty first, then deprecate noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the blocker fix. |
