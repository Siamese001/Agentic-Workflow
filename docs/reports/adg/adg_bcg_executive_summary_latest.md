## ADG Executive Brief

| Question | Answer |
|---|---|
| Can we merge? | No. ADG is red and P0 foundation/wave work remains before lower-severity lanes. |
| What blocks merge? | `H1_new_orphans_delta_ratchet` has 1 blocking row(s). |
| First engineering move | Address H1_new_orphans_delta_ratchet. Review the Modules newly fan_in=0 vs prior snapshot (new orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |
| What waits? | P1-P3 work, ratchets, dead-code cleanup, and broad graph ranking. |
| Audit caveat | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the P0 decision. |

Decision gate:

| Gate | Status | Evidence | Required before ranking |
|---|---|---|---|
| Merge decision | No. ADG is red and P0 foundation/wave work remains before lower-severity lanes. | Can we merge? | Resolve before lower-severity ranking. |
| Merge decision | `H1_new_orphans_delta_ratchet` has 1 blocking row(s). | What blocks merge? | Resolve before lower-severity ranking. |
| Merge decision | Address H1_new_orphans_delta_ratchet. Review the Modules newly fan_in=0 vs prior snapshot (new orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | First engineering move | Resolve before lower-severity ranking. |
| Merge decision | P1-P3 work, ratchets, dead-code cleanup, and broad graph ranking. | What waits? | Resolve before lower-severity ranking. |
| Merge decision | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the P0 decision. | Audit caveat | Resolve before lower-severity ranking. |

Fix now:

| Rank | Move | Evidence | Exit criterion |
|---:|---|---|---|
| 1 | Address H1_new_orphans_delta_ratchet. Review the Modules newly fan_in=0 vs prior snapshot (new orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07082026_2156`: `H1_new_orphans_delta_ratchet` found 1 H1_new_orphans_delta_ratchet, +1 above baseline 0. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 2 | Rerun ADG after the P0 fix; if report consistency still fails, repair the report pipeline before ranking P1-P3. | Report consistency=FAIL. | Post-P0 ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining P0 counts after the rerun: live merge drivers block merge; foundation/audit net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation risk inventory=200; audit net backlog=6; live merge drivers=0. | Receipt shows P0 FIX=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the P0 rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=present_failing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Fund mapped tests for agentic_core/L5_safety/reasoning/FileClassificationAgent.py. Add mapped tests before touching this surface again. | Add mapped tests/regression coverage for agentic_core. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 6 | After P0 is green and mapped tests are decided, open a scoped refactor/test slice for agentic_core/adg/extraction/static_scanner.py only if ADG still flags it or the P0 fix touches it. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 7 | Burn down ratchet G_REACH_l0_reachability. Burn down the ratchet after the current red gates clear. | 1,450 floor-row(s) remain on the ratchet gate. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 8 | Do not open a separate product/app workstream; validate app-owned wiring only if the P0 adapter fix touches it. | App/product risks were promoted only where hotspot or test evidence changes funding posture. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 9 | Keep deletion/deprecation cleanup after P0, report consistency, and runtime proof are green unless cleanup blocks the P0 fix. | ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the P0 fix. |

ADG Run Metrics

| Metric | Value |
|---|---|
| Run ID | 07082026_2156 |
| Snapshot | 2026-07-09T02:02:35.916900+00:00 |
| SQLite snapshot | artifacts/adg/adg_indexed_07082026_2156.sqlite |
| Audit caveat | REPORT_INCONSISTENT; report consistency=FAIL |
| FIX gates (all bands) | 1 |
| Live P0 gate drivers | 0 |
| P0 action queue | no P0 action-queue rows |
| Top FIX gate | H1_new_orphans_delta_ratchet; rows=1 |
| Action rows | 5 |
| P0 ledgers | foundation risk inventory=200; audit net backlog=6; live merge drivers=0 |
| Runtime proof | present_failing |
| Testing hotspot | agentic_core/L5_safety/reasoning/FileClassificationAgent.py; risk=CRITICAL |

P0-P3 Severity Inventory

| Band | Gross | Guardian exempted | Net | Foundation blockers | Live gate drivers |
|---|---|---|---|---|---|
| P0 | 38 | 32 | 6 | 200 | 0 |
| P1 | 1,143 | 1,143 | 0 | n/a | 1 |
| P2 | 727 | 698 | 29 | n/a | 0 |
| P3 | 19,433 | 87 | 19,346 | n/a | 0 |

### Recommended Next Steps

| Priority | Action | Evidence | Exit criterion |
|---|---|---|---|
| 1 | Address H1_new_orphans_delta_ratchet. Review the Modules newly fan_in=0 vs prior snapshot (new orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07082026_2156`: `H1_new_orphans_delta_ratchet` found 1 H1_new_orphans_delta_ratchet, +1 above baseline 0. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 2 | Rerun ADG after the P0 fix; if report consistency still fails, repair the report pipeline before ranking P1-P3. | Report consistency=FAIL. | Post-P0 ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining P0 counts after the rerun: live merge drivers block merge; foundation/audit net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation risk inventory=200; audit net backlog=6; live merge drivers=0. | Receipt shows P0 FIX=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the P0 rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=present_failing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Fund mapped tests for agentic_core/L5_safety/reasoning/FileClassificationAgent.py. Add mapped tests before touching this surface again. | Add mapped tests/regression coverage for agentic_core. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 6 | After P0 is green and mapped tests are decided, open a scoped refactor/test slice for agentic_core/adg/extraction/static_scanner.py only if ADG still flags it or the P0 fix touches it. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 7 | Burn down ratchet G_REACH_l0_reachability. Burn down the ratchet after the current red gates clear. | 1,450 floor-row(s) remain on the ratchet gate. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 8 | Do not open a separate product/app workstream; validate app-owned wiring only if the P0 adapter fix touches it. | App/product risks were promoted only where hotspot or test evidence changes funding posture. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 9 | Keep deletion/deprecation cleanup after P0, report consistency, and runtime proof are green unless cleanup blocks the P0 fix. | ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the P0 fix. |
