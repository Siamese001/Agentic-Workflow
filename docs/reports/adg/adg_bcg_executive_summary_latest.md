## ADG Executive Brief

| Question | Answer |
|---|---|
| Can we merge? | No. A live P0 gate driver is red. |
| What blocks merge? | 3 P0 FIX row(s): 10_infra_wiring, C1_uwg_bypass_pview, 3_write_sovereignty. Live P0 gate drivers=3; top red FIX gate=10_infra_wiring; rows=2. |
| First engineering move | Clear P0 FIX rows. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. |
| What waits? | P1-P3 work, ratchets, dead-code cleanup, and broad graph ranking. |
| Audit caveat | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the P0 decision. |

Decision gate:

| Gate | Status | Evidence | Required before ranking |
|---|---|---|---|
| Merge decision | No. A live P0 gate driver is red. | Can we merge? | Resolve before lower-severity ranking. |
| Merge decision | 3 P0 FIX row(s): 10_infra_wiring, C1_uwg_bypass_pview, 3_write_sovereignty. Live P0 gate drivers=3; top red FIX gate=10_infra_wiring; rows=2. | What blocks merge? | Resolve before lower-severity ranking. |
| Merge decision | Clear P0 FIX rows. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. | First engineering move | Resolve before lower-severity ranking. |
| Merge decision | P1-P3 work, ratchets, dead-code cleanup, and broad graph ranking. | What waits? | Resolve before lower-severity ranking. |
| Merge decision | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the P0 decision. | Audit caveat | Resolve before lower-severity ranking. |

Fix now:

| Rank | Move | Evidence | Exit criterion |
|---:|---|---|---|
| 1 | Clear P0 FIX rows. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. | 3 P0 FIX row(s): 10_infra_wiring, C1_uwg_bypass_pview, 3_write_sovereignty | Rerun ADG and confirm P0 action rows/foundation blockers are zero or explicitly waived. |
| 2 | Rerun ADG after the P0 fix; if report consistency still fails, repair the report pipeline before ranking P1-P3. | Report consistency=FAIL. | Post-P0 ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining P0 counts after the rerun: live merge drivers block merge; foundation/audit net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation risk inventory=200; audit net backlog=3; live merge drivers=3. | Receipt shows P0 FIX=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the P0 rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=present_failing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Clear infra wiring P0 block. Inspect the infra-wiring rows and remove or route the invalid pipeline/spine wiring. Do not re-baseline a P0 block. | ADG `07052026_2301`: `10_infra_wiring` found 2 10_infra_wiring. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 6 | Address C1_uwg_bypass_pview. Review the Any row in UWG-bypass materialized view (zero tolerance block). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07052026_2301`: `C1_uwg_bypass_pview` found 7 C1_uwg_bypass_pview. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 7 | Address 3_write_sovereignty. Review the Non-UWG durable write paths in mv_write_sovereignty_paths (inventory). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07052026_2301`: `3_write_sovereignty` found 766 3_write_sovereignty. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 8 | Do not open a separate product/app workstream; validate app-owned wiring only if the P0 adapter fix touches it. | No app-specific product gap was promoted in this run; app risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 9 | Keep deletion/deprecation cleanup after P0, report consistency, and runtime proof are green unless cleanup blocks the P0 fix. | ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the P0 fix. |

ADG Run Metrics

| Metric | Value |
|---|---|
| Run ID | 07052026_2301 |
| Snapshot | 2026-07-06T03:23:16.794189+00:00 |
| SQLite snapshot | artifacts/adg/adg_indexed_07052026_2301.sqlite |
| Audit caveat | REPORT_INCONSISTENT; report consistency=FAIL |
| FIX gates (all bands) | 4 |
| Live P0 gate drivers | 3 |
| P0 action queue | 3 P0 FIX row(s): 10_infra_wiring, C1_uwg_bypass_pview, 3_write_sovereignty |
| Top FIX gate | 10_infra_wiring; rows=2 |
| Action rows | 7 |
| P0 ledgers | foundation risk inventory=200; audit net backlog=3; live merge drivers=3 |
| Runtime proof | present_failing |
| Testing hotspot | agentic_core/L5_safety/reasoning/FileClassificationAgent.py; risk=CRITICAL |

P0-P3 Severity Inventory

| Band | Gross | Guardian exempted | Net | Foundation blockers | Live gate drivers |
|---|---|---|---|---|---|
| P0 | 35 | 32 | 3 | 200 | 3 |
| P1 | 1,146 | 1,143 | 3 | n/a | 1 |
| P2 | 722 | 698 | 24 | n/a | 0 |
| P3 | 19,321 | 87 | 19,234 | n/a | 0 |

### Recommended Next Steps

| Priority | Action | Evidence | Exit criterion |
|---|---|---|---|
| 1 | Clear P0 FIX rows. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. | 3 P0 FIX row(s): 10_infra_wiring, C1_uwg_bypass_pview, 3_write_sovereignty | Rerun ADG and confirm P0 action rows/foundation blockers are zero or explicitly waived. |
| 2 | Rerun ADG after the P0 fix; if report consistency still fails, repair the report pipeline before ranking P1-P3. | Report consistency=FAIL. | Post-P0 ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining P0 counts after the rerun: live merge drivers block merge; foundation/audit net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation risk inventory=200; audit net backlog=3; live merge drivers=3. | Receipt shows P0 FIX=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the P0 rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=present_failing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Clear infra wiring P0 block. Inspect the infra-wiring rows and remove or route the invalid pipeline/spine wiring. Do not re-baseline a P0 block. | ADG `07052026_2301`: `10_infra_wiring` found 2 10_infra_wiring. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 6 | Address C1_uwg_bypass_pview. Review the Any row in UWG-bypass materialized view (zero tolerance block). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07052026_2301`: `C1_uwg_bypass_pview` found 7 C1_uwg_bypass_pview. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 7 | Address 3_write_sovereignty. Review the Non-UWG durable write paths in mv_write_sovereignty_paths (inventory). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07052026_2301`: `3_write_sovereignty` found 766 3_write_sovereignty. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 8 | Do not open a separate product/app workstream; validate app-owned wiring only if the P0 adapter fix touches it. | No app-specific product gap was promoted in this run; app risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 9 | Keep deletion/deprecation cleanup after P0, report consistency, and runtime proof are green unless cleanup blocks the P0 fix. | ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the P0 fix. |
