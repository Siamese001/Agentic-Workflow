## ADG Executive Brief

| Question | Answer |
|---|---|
| Can we merge? | No. A live critical gate driver is red and must be treated as a P0 blocker. |
| What blocks merge? | 1 P0 blocker row(s); 3 candidate-blocker row(s): G_REACH_l0_reachability, agentic_core/L1_cognition/bridges/u0_to_l1_planning.py, agentic_core/L1_cognition/c0_context/__init__.py, +1 more. Live blocker drivers=1; top red FIX gate=G_REACH_l0_reachability; rows=1,460. |
| First engineering move | Clear P0 blocker rows. Clear open blockers first; otherwise attach candidate rows to a live blocker gate or move them to tracked debt. |
| What waits? | Non-blocking impact inventory, ratchets, dead-code cleanup, and broad graph ranking. |
| Audit caveat | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the blocker decision. |

Decision gate:

| Gate | Status | Evidence | Required before ranking |
|---|---|---|---|
| Merge decision | No. A live critical gate driver is red and must be treated as a P0 blocker. | Can we merge? | Resolve before lower-severity ranking. |
| Merge decision | 1 P0 blocker row(s); 3 candidate-blocker row(s): G_REACH_l0_reachability, agentic_core/L1_cognition/bridges/u0_to_l1_planning.py, agentic_core/L1_cognition/c0_context/__init__.py, +1 more. Live blocker drivers=1; top red FIX gate=G_REACH_l0_reachability; rows=1,460. | What blocks merge? | Resolve before lower-severity ranking. |
| Merge decision | Clear P0 blocker rows. Clear open blockers first; otherwise attach candidate rows to a live blocker gate or move them to tracked debt. | First engineering move | Resolve before lower-severity ranking. |
| Merge decision | Non-blocking impact inventory, ratchets, dead-code cleanup, and broad graph ranking. | What waits? | Resolve before lower-severity ranking. |
| Merge decision | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the blocker decision. | Audit caveat | Resolve before lower-severity ranking. |

Fix now:

| Rank | Move | Evidence | Exit criterion |
|---:|---|---|---|
| 1 | Clear P0 blocker rows. Clear open blockers first; otherwise attach candidate rows to a live blocker gate or move them to tracked debt. | 1 P0 blocker row(s); 3 candidate-blocker row(s): G_REACH_l0_reachability, agentic_core/L1_cognition/bridges/u0_to_l1_planning.py, agentic_core/L1_cognition/c0_context/__init__.py, +1 more | Rerun ADG and confirm open blocker rows are zero or explicitly waived. |
| 2 | Rerun ADG after the blocker fix; if report consistency still fails, repair the report pipeline before ranking lower-impact work. | Report consistency=FAIL. | Post-blocker ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining critical-impact counts after the rerun: live blocker drivers block merge; foundation-candidate/audit-net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation candidate inventory=200; critical audit net=14; live blocker drivers=1. | Receipt shows open_blocker_fix_count=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the blocker rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=present_failing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Address G_REACH_l0_reachability. Review the Production-layer modules with no import path from any L0 node (orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07132026_0555`: `G_REACH_l0_reachability` found 1,460 G_REACH_l0_reachability, +2 above baseline 1458. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 6 | Fund mapped tests for agentic_core/L5_safety/reasoning/FileClassificationAgent.py. Add mapped tests before touching this surface again. | Add mapped tests/regression coverage for agentic_core. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 7 | After blockers are green and mapped tests are decided, open a scoped refactor/test slice for agentic_core/L0_routing/config/__init__.py only if ADG still flags it or the blocker fix touches it. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 8 | Do not open a separate product/app workstream; validate app-owned wiring only if the blocker fix touches it. | App/product risks were promoted only where hotspot or test evidence changes funding posture. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 9 | Keep deletion/deprecation cleanup after blockers, report consistency, and runtime proof are green unless cleanup blocks the fix. | ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the blocker fix. |

ADG Run Metrics

| Metric | Value |
|---|---|
| Run ID | 07132026_0555 |
| Snapshot | 2026-07-13T10:07:47.561753+00:00 |
| SQLite snapshot | artifacts/adg/adg_indexed_07132026_0555.sqlite |
| Audit caveat | REPORT_INCONSISTENT; report consistency=FAIL |
| FIX gates (all bands) | 1 |
| Open critical gate drivers | 1 |
| Open blocker queue | 1 P0 blocker row(s); 3 candidate-blocker row(s): G_REACH_l0_reachability, agentic_core/L1_cognition/bridges/u0_to_l1_planning.py, agentic_core/L1_cognition/c0_context/__init__.py, +1 more |
| Top FIX gate | G_REACH_l0_reachability; rows=1,460 |
| Action rows | 5 |
| Decision ledgers | foundation candidate inventory=200; critical audit net=14; live blocker drivers=1 |
| Runtime proof | present_failing |
| Testing hotspot | agentic_core/L5_safety/reasoning/FileClassificationAgent.py; risk=CRITICAL |

Impact Inventory

| Band | Impact severity | Gross | Guardian exempted | Net | Foundation candidates | Live blocker drivers |
|---|---|---|---|---|---|---|
| P0 | critical | 46 | 32 | 14 | 200 | 1 |
| P1 | high | 1,149 | 1,143 | 6 | n/a | 0 |
| P2 | medium | 740 | 698 | 42 | n/a | 0 |
| P3 | low | 19,638 | 87 | 19,551 | n/a | 0 |

### Recommended Next Steps

| Priority | Action | Evidence | Exit criterion |
|---|---|---|---|
| 1 | Clear P0 blocker rows. Clear open blockers first; otherwise attach candidate rows to a live blocker gate or move them to tracked debt. | 1 P0 blocker row(s); 3 candidate-blocker row(s): G_REACH_l0_reachability, agentic_core/L1_cognition/bridges/u0_to_l1_planning.py, agentic_core/L1_cognition/c0_context/__init__.py, +1 more | Rerun ADG and confirm open blocker rows are zero or explicitly waived. |
| 2 | Rerun ADG after the blocker fix; if report consistency still fails, repair the report pipeline before ranking lower-impact work. | Report consistency=FAIL. | Post-blocker ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining critical-impact counts after the rerun: live blocker drivers block merge; foundation-candidate/audit-net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation candidate inventory=200; critical audit net=14; live blocker drivers=1. | Receipt shows open_blocker_fix_count=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the blocker rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=present_failing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Address G_REACH_l0_reachability. Review the Production-layer modules with no import path from any L0 node (orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07132026_0555`: `G_REACH_l0_reachability` found 1,460 G_REACH_l0_reachability, +2 above baseline 1458. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 6 | Fund mapped tests for agentic_core/L5_safety/reasoning/FileClassificationAgent.py. Add mapped tests before touching this surface again. | Add mapped tests/regression coverage for agentic_core. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 7 | After blockers are green and mapped tests are decided, open a scoped refactor/test slice for agentic_core/L0_routing/config/__init__.py only if ADG still flags it or the blocker fix touches it. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 8 | Do not open a separate product/app workstream; validate app-owned wiring only if the blocker fix touches it. | App/product risks were promoted only where hotspot or test evidence changes funding posture. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 9 | Keep deletion/deprecation cleanup after blockers, report consistency, and runtime proof are green unless cleanup blocks the fix. | ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the blocker fix. |
