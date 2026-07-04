## ADG Executive Brief

| Question | Answer |
|---|---|
| Can we merge? | No. ADG is red and P0 foundation/wave work remains before lower-severity lanes. |
| What blocks merge? | 3 P0 wave file row(s): agentic_core/L1_cognition/__init__.py, agentic_core/L1_cognition/apps_research_c0_binding.py, agentic_core/L1_cognition/apps_research_l1_binding.py. Live P0 gate drivers=0; top red FIX gate=H1_new_orphans_delta_ratchet; rows=3. |
| First engineering move | Clear P0 foundation wave. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. |
| What waits? | P1-P3 work, ratchets, dead-code cleanup, and broad graph ranking. |
| Audit caveat | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the P0 decision. |

ADG Run Metrics

| Metric | Value |
|---|---|
| Run ID | 07032026_2302 |
| Snapshot | 2026-07-04T03:17:28.818732+00:00 |
| SQLite snapshot | artifacts/adg/adg_indexed_07032026_2302.sqlite |
| Audit caveat | REPORT_INCONSISTENT; report consistency=FAIL |
| FIX gates (all bands) | 1 |
| Live P0 gate drivers | 0 |
| P0 action queue | 3 P0 wave file row(s): agentic_core/L1_cognition/__init__.py, agentic_core/L1_cognition/apps_research_c0_binding.py, agentic_core/L1_cognition/apps_research_l1_binding.py |
| Top FIX gate | H1_new_orphans_delta_ratchet; rows=3 |
| Action rows | 5 |
| P0 ledgers | foundation risk inventory=201; audit net backlog=4; live merge drivers=0 |
| Runtime proof | present_failing |
| Testing hotspot | agentic_core/L5_safety/reasoning/FileClassificationAgent.py; risk=CRITICAL |

P0-P3 Severity Inventory

| Band | Gross | Guardian exempted | Net | Foundation blockers | Live gate drivers |
|---|---|---|---|---|---|
| P0 | 37 | 33 | 4 | 201 | 0 |
| P1 | 1,146 | 1,143 | 3 | n/a | 1 |
| P2 | 748 | 716 | 32 | n/a | 0 |
| P3 | 19,265 | 87 | 19,178 | n/a | 0 |

### Recommended Next Steps

| Priority | Action | Evidence | Exit criterion |
|---|---|---|---|
| 1 | Clear P0 foundation wave. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. | 3 P0 wave file row(s): agentic_core/L1_cognition/__init__.py, agentic_core/L1_cognition/apps_research_c0_binding.py, agentic_core/L1_cognition/apps_research_l1_binding.py | Rerun ADG and confirm P0 action rows/foundation blockers are zero or explicitly waived. |
| 2 | Rerun ADG after the P0 fix; if report consistency still fails, repair the report pipeline before ranking P1-P3. | Report consistency=FAIL. | Post-P0 ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining P0 counts after the rerun: live merge drivers block merge; foundation/audit net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation risk inventory=201; audit net backlog=4; live merge drivers=0. | Receipt shows P0 FIX=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the P0 rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=present_failing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Address H1_new_orphans_delta_ratchet. Review the Modules newly fan_in=0 vs prior snapshot (new orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. | ADG `07032026_2302`: `H1_new_orphans_delta_ratchet` found 3 H1_new_orphans_delta_ratchet, +3 above baseline 0. Breakout unavailable. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 6 | Fund mapped tests for agentic_core/L5_safety/reasoning/FileClassificationAgent.py. Add mapped tests before touching this surface again. | Add mapped tests/regression coverage for agentic_core. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 7 | After P0 is green and mapped tests are decided, open a scoped refactor/test slice for agentic_core/adg/extraction/static_scanner.py only if ADG still flags it or the P0 fix touches it. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 8 | Do not open a separate product/app workstream; validate app-owned wiring only if the P0 adapter fix touches it. | No app-specific product gap was promoted in this run; app risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 9 | Keep deletion/deprecation cleanup after P0, report consistency, and runtime proof are green unless cleanup blocks the P0 fix. | ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the P0 fix. |
