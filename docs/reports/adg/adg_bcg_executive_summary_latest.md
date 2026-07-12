## ADG Executive Brief

| Question | Answer |
|---|---|
| Can we merge? | No. A live critical gate driver is red and must be treated as a P0 blocker. |
| What blocks merge? | 3 P0 blocker row(s); 3 candidate-blocker row(s): 10_infra_wiring, G_REACH_l0_reachability, H1_new_orphans_delta_ratchet, +3 more. Live blocker drivers=2; top red FIX gate=10_infra_wiring; rows=3. |
| First engineering move | Clear P0 blocker rows. Clear open blockers first; otherwise attach candidate rows to a live blocker gate or move them to tracked debt. |
| What waits? | Non-blocking impact inventory, ratchets, dead-code cleanup, and broad graph ranking. |
| Audit caveat | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the blocker decision. |

Decision gate:

| Gate | Status | Evidence | Required before ranking |
|---|---|---|---|
| Merge decision | No. A live critical gate driver is red and must be treated as a P0 blocker. | Can we merge? | Resolve before lower-severity ranking. |
| Merge decision | 3 P0 blocker row(s); 3 candidate-blocker row(s): 10_infra_wiring, G_REACH_l0_reachability, H1_new_orphans_delta_ratchet, +3 more. Live blocker drivers=2; top red FIX gate=10_infra_wiring; rows=3. | What blocks merge? | Resolve before lower-severity ranking. |
| Merge decision | Clear P0 blocker rows. Clear open blockers first; otherwise attach candidate rows to a live blocker gate or move them to tracked debt. | First engineering move | Resolve before lower-severity ranking. |
| Merge decision | Non-blocking impact inventory, ratchets, dead-code cleanup, and broad graph ranking. | What waits? | Resolve before lower-severity ranking. |
| Merge decision | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the blocker decision. | Audit caveat | Resolve before lower-severity ranking. |

Fix now:

| Rank | Move | Evidence | Exit criterion |
|---:|---|---|---|
| 1 | Clear P0 blocker rows. Clear open blockers first; otherwise attach candidate rows to a live blocker gate or move them to tracked debt. | 3 P0 blocker row(s); 3 candidate-blocker row(s): 10_infra_wiring, G_REACH_l0_reachability, H1_new_orphans_delta_ratchet, +3 more | Rerun ADG and confirm open blocker rows are zero or explicitly waived. |
| 2 | Rerun ADG after the blocker fix; if report consistency still fails, repair the report pipeline before ranking lower-impact work. | Report consistency=FAIL. | Post-blocker ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining critical-impact counts after the rerun: live blocker drivers block merge; foundation-candidate/audit-net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation candidate inventory=200; critical audit net=11; live blocker drivers=2. | Receipt shows open_blocker_fix_count=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the blocker rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=present_failing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Clear infra wiring P0 block. Inspect the infra-wiring rows and remove or route the invalid pipeline/spine wiring. Do not re-baseline a P0 block. | ADG `07112026_1937`: `10_infra_wiring` found 3 10_infra_wiring. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 6 | Address G_REACH_l0_reachability. Review the Production-layer modules with no import path from any L0 node (orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07112026_1937`: `G_REACH_l0_reachability` found 1,453 G_REACH_l0_reachability, +3 above baseline 1450. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 7 | Address H1_new_orphans_delta_ratchet. Review the Modules newly fan_in=0 vs prior snapshot (new orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07112026_1937`: `H1_new_orphans_delta_ratchet` found 3 H1_new_orphans_delta_ratchet, +3 above baseline 0. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 8 | Do not open a separate product/app workstream; validate app-owned wiring only if the blocker fix touches it. | App/product risks were promoted only where hotspot or test evidence changes funding posture. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 9 | Keep deletion/deprecation cleanup after blockers, report consistency, and runtime proof are green unless cleanup blocks the fix. | ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the blocker fix. |

ADG Run Metrics

| Metric | Value |
|---|---|
| Run ID | 07112026_1937 |
| Snapshot | 2026-07-11T23:50:25.691412+00:00 |
| SQLite snapshot | artifacts/adg/adg_indexed_07112026_1937.sqlite |
| Audit caveat | REPORT_INCONSISTENT; report consistency=FAIL |
| FIX gates (all bands) | 3 |
| Open critical gate drivers | 2 |
| Open blocker queue | 3 P0 blocker row(s); 3 candidate-blocker row(s): 10_infra_wiring, G_REACH_l0_reachability, H1_new_orphans_delta_ratchet, +3 more |
| Top FIX gate | 10_infra_wiring; rows=3 |
| Action rows | 7 |
| Decision ledgers | foundation candidate inventory=200; critical audit net=11; live blocker drivers=2 |
| Runtime proof | present_failing |
| Testing hotspot | agentic_core/L5_safety/reasoning/FileClassificationAgent.py; risk=CRITICAL |

Impact Inventory

| Band | Impact severity | Gross | Guardian exempted | Net | Foundation candidates | Live blocker drivers |
|---|---|---|---|---|---|---|
| P0 | critical | 43 | 32 | 11 | 200 | 2 |
| P1 | high | 1,143 | 1,143 | 0 | n/a | 1 |
| P2 | medium | 733 | 699 | 34 | n/a | 0 |
| P3 | low | 19,539 | 87 | 19,452 | n/a | 0 |

### Recommended Next Steps

| Priority | Action | Evidence | Exit criterion |
|---|---|---|---|
| 1 | Clear P0 blocker rows. Clear open blockers first; otherwise attach candidate rows to a live blocker gate or move them to tracked debt. | 3 P0 blocker row(s); 3 candidate-blocker row(s): 10_infra_wiring, G_REACH_l0_reachability, H1_new_orphans_delta_ratchet, +3 more | Rerun ADG and confirm open blocker rows are zero or explicitly waived. |
| 2 | Rerun ADG after the blocker fix; if report consistency still fails, repair the report pipeline before ranking lower-impact work. | Report consistency=FAIL. | Post-blocker ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining critical-impact counts after the rerun: live blocker drivers block merge; foundation-candidate/audit-net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation candidate inventory=200; critical audit net=11; live blocker drivers=2. | Receipt shows open_blocker_fix_count=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the blocker rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=present_failing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Clear infra wiring P0 block. Inspect the infra-wiring rows and remove or route the invalid pipeline/spine wiring. Do not re-baseline a P0 block. | ADG `07112026_1937`: `10_infra_wiring` found 3 10_infra_wiring. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 6 | Address G_REACH_l0_reachability. Review the Production-layer modules with no import path from any L0 node (orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07112026_1937`: `G_REACH_l0_reachability` found 1,453 G_REACH_l0_reachability, +3 above baseline 1450. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 7 | Address H1_new_orphans_delta_ratchet. Review the Modules newly fan_in=0 vs prior snapshot (new orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07112026_1937`: `H1_new_orphans_delta_ratchet` found 3 H1_new_orphans_delta_ratchet, +3 above baseline 0. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 8 | Do not open a separate product/app workstream; validate app-owned wiring only if the blocker fix touches it. | App/product risks were promoted only where hotspot or test evidence changes funding posture. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 9 | Keep deletion/deprecation cleanup after blockers, report consistency, and runtime proof are green unless cleanup blocks the fix. | ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the blocker fix. |
