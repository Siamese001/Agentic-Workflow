## ADG Executive Brief

| Question | Answer |
|---|---|
| Can we merge? | No. A live P0 gate driver is red. |
| What blocks merge? | 1 P0 FIX row(s); 3 P0 wave row(s): G_REACH_l0_reachability, agentic_core/L1_cognition/apps_research_l1_binding_v2.py, agentic_core/L1_cognition/bridges/__init__.py, +1 more. Live P0 gate drivers=1; top red FIX gate=G_REACH_l0_reachability; rows=1,454. |
| First engineering move | Clear P0 FIX rows. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. |
| What waits? | P1-P3 work, ratchets, dead-code cleanup, and broad graph ranking. |
| Audit caveat | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the P0 decision. |

Decision gate:

| Gate | Status | Evidence | Required before ranking |
|---|---|---|---|
| Merge decision | No. A live P0 gate driver is red. | Can we merge? | Resolve before lower-severity ranking. |
| Merge decision | 1 P0 FIX row(s); 3 P0 wave row(s): G_REACH_l0_reachability, agentic_core/L1_cognition/apps_research_l1_binding_v2.py, agentic_core/L1_cognition/bridges/__init__.py, +1 more. Live P0 gate drivers=1; top red FIX gate=G_REACH_l0_reachability; rows=1,454. | What blocks merge? | Resolve before lower-severity ranking. |
| Merge decision | Clear P0 FIX rows. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. | First engineering move | Resolve before lower-severity ranking. |
| Merge decision | P1-P3 work, ratchets, dead-code cleanup, and broad graph ranking. | What waits? | Resolve before lower-severity ranking. |
| Merge decision | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the P0 decision. | Audit caveat | Resolve before lower-severity ranking. |

Fix now:

| Rank | Move | Evidence | Exit criterion |
|---:|---|---|---|
| 1 | Clear P0 FIX rows. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. | 1 P0 FIX row(s); 3 P0 wave row(s): G_REACH_l0_reachability, agentic_core/L1_cognition/apps_research_l1_binding_v2.py, agentic_core/L1_cognition/bridges/__init__.py, +1 more | Rerun ADG and confirm P0 action rows/foundation blockers are zero or explicitly waived. |
| 2 | Rerun ADG after the P0 fix; if report consistency still fails, repair the report pipeline before ranking P1-P3. | Report consistency=FAIL. | Post-P0 ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining P0 counts after the rerun: live merge drivers block merge; foundation/audit net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation risk inventory=200; audit net backlog=6; live merge drivers=1. | Receipt shows P0 FIX=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the P0 rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=present_failing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Address G_REACH_l0_reachability. Review the Production-layer modules with no import path from any L0 node (orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07082026_2035`: `G_REACH_l0_reachability` found 1,454 G_REACH_l0_reachability, +1 above baseline 1453. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 6 | Fund mapped tests for agentic_core/L5_safety/reasoning/FileClassificationAgent.py. Add mapped tests before touching this surface again. | Add mapped tests/regression coverage for agentic_core. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 7 | After P0 is green and mapped tests are decided, open a scoped refactor/test slice for agentic_core/adg/extraction/static_scanner.py only if ADG still flags it or the P0 fix touches it. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 8 | Do not open a separate product/app workstream; validate app-owned wiring only if the P0 adapter fix touches it. | App/product risks were promoted only where hotspot or test evidence changes funding posture. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 9 | Keep deletion/deprecation cleanup after P0, report consistency, and runtime proof are green unless cleanup blocks the P0 fix. | ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the P0 fix. |

ADG Run Metrics

| Metric | Value |
|---|---|
| Run ID | 07082026_2035 |
| Snapshot | 2026-07-09T00:48:37.356191+00:00 |
| SQLite snapshot | artifacts/adg/adg_indexed_07082026_2035.sqlite |
| Audit caveat | REPORT_INCONSISTENT; report consistency=FAIL |
| FIX gates (all bands) | 1 |
| Live P0 gate drivers | 1 |
| P0 action queue | 1 P0 FIX row(s); 3 P0 wave row(s): G_REACH_l0_reachability, agentic_core/L1_cognition/apps_research_l1_binding_v2.py, agentic_core/L1_cognition/bridges/__init__.py, +1 more |
| Top FIX gate | G_REACH_l0_reachability; rows=1,454 |
| Action rows | 5 |
| P0 ledgers | foundation risk inventory=200; audit net backlog=6; live merge drivers=1 |
| Runtime proof | present_failing |
| Testing hotspot | agentic_core/L5_safety/reasoning/FileClassificationAgent.py; risk=CRITICAL |

P0-P3 Severity Inventory

| Band | Gross | Guardian exempted | Net | Foundation blockers | Live gate drivers |
|---|---|---|---|---|---|
| P0 | 38 | 32 | 6 | 200 | 1 |
| P1 | 1,143 | 1,143 | 0 | n/a | 0 |
| P2 | 726 | 698 | 28 | n/a | 0 |
| P3 | 19,413 | 87 | 19,326 | n/a | 0 |

### Recommended Next Steps

| Priority | Action | Evidence | Exit criterion |
|---|---|---|---|
| 1 | Clear P0 FIX rows. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. | 1 P0 FIX row(s); 3 P0 wave row(s): G_REACH_l0_reachability, agentic_core/L1_cognition/apps_research_l1_binding_v2.py, agentic_core/L1_cognition/bridges/__init__.py, +1 more | Rerun ADG and confirm P0 action rows/foundation blockers are zero or explicitly waived. |
| 2 | Rerun ADG after the P0 fix; if report consistency still fails, repair the report pipeline before ranking P1-P3. | Report consistency=FAIL. | Post-P0 ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining P0 counts after the rerun: live merge drivers block merge; foundation/audit net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation risk inventory=200; audit net backlog=6; live merge drivers=1. | Receipt shows P0 FIX=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the P0 rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=present_failing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Address G_REACH_l0_reachability. Review the Production-layer modules with no import path from any L0 node (orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07082026_2035`: `G_REACH_l0_reachability` found 1,454 G_REACH_l0_reachability, +1 above baseline 1453. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 6 | Fund mapped tests for agentic_core/L5_safety/reasoning/FileClassificationAgent.py. Add mapped tests before touching this surface again. | Add mapped tests/regression coverage for agentic_core. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 7 | After P0 is green and mapped tests are decided, open a scoped refactor/test slice for agentic_core/adg/extraction/static_scanner.py only if ADG still flags it or the P0 fix touches it. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 8 | Do not open a separate product/app workstream; validate app-owned wiring only if the P0 adapter fix touches it. | App/product risks were promoted only where hotspot or test evidence changes funding posture. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 9 | Keep deletion/deprecation cleanup after P0, report consistency, and runtime proof are green unless cleanup blocks the P0 fix. | ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the P0 fix. |
