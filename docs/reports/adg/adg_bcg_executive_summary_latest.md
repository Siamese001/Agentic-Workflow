## ADG Executive Brief

| Question | Answer |
|---|---|
| Can we merge? | No. ADG is red and P0 foundation/wave work remains before lower-severity lanes. |
| What blocks merge? | 3 P0 wave file row(s): agentic_core/L1_cognition/__init__.py, agentic_core/L1_cognition/apps_research_c0_binding.py, agentic_core/L1_cognition/apps_research_l1_binding.py. Live P0 gate drivers=0; top red FIX gate=none. |
| First engineering move | Clear P0 foundation wave. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. |
| What waits? | P1-P3 work, ratchets, dead-code cleanup, and broad graph ranking. |
| Audit caveat | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the P0 decision. |

ADG Run Metrics

| Metric | Value |
|---|---|
| Run ID | 06292026_0101 |
| Snapshot | 2026-07-03T10:54:35.390492+00:00 |
| SQLite snapshot | C:\Users\amita\AppData\Local\Temp\pytest-of-amita\pytest-3260\test_clean_certification_run_r0\snap.sqlite |
| Audit caveat | REPORT_INCONSISTENT; report consistency=FAIL |
| FIX gates (all bands) | 0 |
| Live P0 gate drivers | 0 |
| P0 action queue | 3 P0 wave file row(s): agentic_core/L1_cognition/__init__.py, agentic_core/L1_cognition/apps_research_c0_binding.py, agentic_core/L1_cognition/apps_research_l1_binding.py |
| Top FIX gate | none |
| Action rows | 1 |
| P0 ledgers | foundation risk inventory=not loaded; audit net backlog=0; live merge drivers=0 |
| Runtime proof | missing |
| Testing hotspot | unknown; risk=HIGH |

P0-P3 Severity Inventory

| Band | Gross | Guardian exempted | Net | Foundation blockers | Live gate drivers |
|---|---|---|---|---|---|
| P0 | 0 | 0 | 0 | not loaded | 0 |
| P1 | 0 | 0 | 0 | n/a | 0 |
| P2 | 0 | 0 | 0 | n/a | 0 |
| P3 | 0 | 0 | 0 | n/a | 0 |

### Recommended Next Steps

| Priority | Action | Evidence | Exit criterion |
|---|---|---|---|
| 1 | Clear P0 foundation wave. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. | 3 P0 wave file row(s): agentic_core/L1_cognition/__init__.py, agentic_core/L1_cognition/apps_research_c0_binding.py, agentic_core/L1_cognition/apps_research_l1_binding.py | Rerun ADG and confirm P0 action rows/foundation blockers are zero or explicitly waived. |
| 2 | Rerun ADG after the P0 fix; if report consistency still fails, repair the report pipeline before ranking P1-P3. | Report consistency=FAIL. | Post-P0 ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining P0 counts after the rerun: live merge drivers block merge; foundation/audit net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation risk inventory=not loaded; audit net backlog=0; live merge drivers=0. | Receipt shows P0 FIX=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the P0 rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=missing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Fund mapped tests for unknown. Add mapped tests before touching this surface again. | Add mapped tests/unit, tests/regression coverage for unknown. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 6 | Do not open a separate product/app workstream; validate app-owned wiring only if the P0 adapter fix touches it. | No app-specific product gap was promoted in this run; app risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 7 | Keep deletion/deprecation cleanup after P0, report consistency, and runtime proof are green unless cleanup blocks the P0 fix. | No deletions are approved in this run because ADG found 0 confirmed dead-code candidates; reduce uncertainty first, then deprecate noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the P0 fix. |
