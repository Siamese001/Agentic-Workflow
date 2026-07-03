## ADG Executive Brief

| Question | Answer |
|---|---|
| Can we merge? | No. A live P0 gate driver is red. |
| What blocks merge? | 1 P0 FIX row(s); 3 P0 wave row(s): 13_core_imports_apps, agentic_core/L1_cognition/__init__.py, agentic_core/L1_cognition/apps_research_c0_binding.py, +1 more. Live P0 gate drivers=1; top red FIX gate=13_core_imports_apps; rows=5. |
| First engineering move | Clear P0 FIX rows. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. |
| What waits? | P1-P3 work, ratchets, dead-code cleanup, and broad graph ranking. |
| Audit caveat | Report consistency is FAIL; this makes lower-priority ranking provisional, but does not change the P0 decision. |

ADG Run Metrics

| Metric | Value |
|---|---|
| Run ID | 07032026_0812 |
| Snapshot | 2026-07-03T12:25:29.907040+00:00 |
| SQLite snapshot | artifacts/adg/adg_indexed_07032026_0812.sqlite |
| Audit caveat | REPORT_INCONSISTENT; report consistency=FAIL |
| FIX gates (all bands) | 1 |
| Live P0 gate drivers | 1 |
| P0 action queue | 1 P0 FIX row(s); 3 P0 wave row(s): 13_core_imports_apps, agentic_core/L1_cognition/__init__.py, agentic_core/L1_cognition/apps_research_c0_binding.py, +1 more |
| Top FIX gate | 13_core_imports_apps; rows=5 |
| Action rows | 5 |
| P0 ledgers | foundation risk inventory=201; audit net backlog=4; live merge drivers=1 |
| Runtime proof | present_failing |
| Testing hotspot | agentic_core/L5_safety/reasoning/FileClassificationAgent.py; risk=CRITICAL |

P0-P3 Severity Inventory

| Band | Gross | Guardian exempted | Net | Foundation blockers | Live gate drivers |
|---|---|---|---|---|---|
| P0 | 37 | 33 | 4 | 201 | 1 |
| P1 | 1,146 | 1,143 | 3 | n/a | 0 |
| P2 | 747 | 716 | 31 | n/a | 0 |
| P3 | 19,262 | 87 | 19,175 | n/a | 0 |

### Recommended Next Steps

| Priority | Action | Evidence | Exit criterion |
|---|---|---|---|
| 1 | Clear P0 FIX rows. Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3. | 1 P0 FIX row(s); 3 P0 wave row(s): 13_core_imports_apps, agentic_core/L1_cognition/__init__.py, agentic_core/L1_cognition/apps_research_c0_binding.py, +1 more | Rerun ADG and confirm P0 action rows/foundation blockers are zero or explicitly waived. |
| 2 | Rerun ADG after the P0 fix; if report consistency still fails, repair the report pipeline before ranking P1-P3. | Report consistency=FAIL. | Post-P0 ADG has report consistency PASS or an explicit waiver. |
| 3 | Classify remaining P0 counts after the rerun: live merge drivers block merge; foundation/audit net rows become follow-up backlog unless they still appear as live FIX gates. | Foundation risk inventory=201; audit net backlog=4; live merge drivers=1. | Receipt shows P0 FIX=0, or any remaining foundation/audit row is attached to an explicit live FIX gate. |
| 4 | Repair runtime proof if it is still missing or failing after the P0 rerun; do not rely on runtime evidence until it is present and passing. | runtime_spine=present_failing. | Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision. |
| 5 | Stop core importing apps. Move app-specific bindings behind an adapter or app-owned wiring surface; core should keep only generic contracts. | ADG `07032026_0812` found 5 core-to-app import row(s): `agentic_core` imports `apps_*`. | Rerun ADG and confirm the gate returns to green or is explicitly waived. |
| 6 | Fund mapped tests for agentic_core/L5_safety/reasoning/FileClassificationAgent.py. Add mapped tests before touching this surface again. | Add mapped tests/regression coverage for agentic_core. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 7 | After P0 is green and mapped tests are decided, open a scoped refactor/test slice for agentic_core/adg/extraction/static_scanner.py only if ADG still flags it or the P0 fix touches it. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 8 | Do not open a separate product/app workstream; validate app-owned wiring only if the P0 adapter fix touches it. | No app-specific product gap was promoted in this run; app risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row. | Touched app wiring has targeted validation, or no app-owned surface was touched. |
| 9 | Keep deletion/deprecation cleanup after P0, report consistency, and runtime proof are green unless cleanup blocks the P0 fix. | ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics. | Cleanup is scheduled as a separate after-green wave or explicitly tied to the P0 fix. |
