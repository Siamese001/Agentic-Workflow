## ADG Executive Brief

### 1. What ADG Is

ADG is the X-ray of the codebase. It maps code connections and lets the system ask health-check questions automatically. It turns 'is this codebase healthy?' from opinion into measured facts.

### 2. Patient Size

This patient has 12374 Python files: 7212 production files and 5162 test files. agentic_core contributes 2910 files; apps_* contributes 1503 files. Current snapshot/run ID: 06152026_0644.

### 3. Executive Decision

ADG is BLOCKED: Fund the smallest slice that clears current blockers and attaches tests where hotspot evidence overlaps; keep ratchets after-green. This is a routine_nudge; do not chase Do not rank work by raw MV row count alone., Do not treat guardian inventory as an automatic product failure..

### 4. Gap Analysis — Lens 1: Health Gates

FIX blocks green; TRACK is accepted backlog/ratchet work; CLEAR needs no action. A blocked ADG run is not automatically a platform crisis; regression delta and graph/test linkage determine urgency.

| Bucket | Count | Executive meaning |
|---|---:|---|
| CLEAR | 25 | No action now. |
| TRACK | 17 | Known debt or advisory inventory; burn down after red gates. |
| FIX | 6 | Current blocker or regression requiring action before decision-grade green. |

| Red gate | Total records | Regression / new delta | Executive read | Next action |
|---|---:|---:|---|---|
| 8_trace_replay_eval | 5 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +N over baseline None: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| L2_lpg_drift_ratchet | 2 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 1 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| M1_module_loc_ratchet | 462 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +3 over baseline 459: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| Q2_cyclomatic_complexity_ratchet | 1086 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +3 over baseline 1083: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| H1_new_orphans_delta_ratchet | 10 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +10 over baseline 0: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| G_REACH_l0_reachability | 2850 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +7 over baseline 2843 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |

### 5. Gap Analysis — Lens 2: Runtime Proof / Observability

Runtime proof is present and FAILING — treat as a quality failure to fix.

| Runtime proof signal | Status | Executive read | Action |
|---|---|---|---|
| runtime_spine | present_failing | Runtime proof present and FAILING: 6 semantic failure(s) — a quality failure, not a measurement gap. | Fix the failing runtime path before relying on the trace. |
| graphdb_queries | present | Runtime/structural proof present and clean for interpretation. | Use to confirm runtime path risk. |
| structural_outputs | present | Runtime/structural proof present and clean for interpretation. | Use to confirm runtime path risk. |
| mv_eval_coverage_by_path | present | replay/eval coverage MV present with 12 rows; gaps here are replay/eval blind spots, not proven failures. | Close replay/eval gaps for critical paths. |

### 6. Gap Analysis — Lens 3: Product / App Risk

App/product risks were promoted only where hotspot or test evidence changes funding posture.

| App / product scope | Risk | Evidence | Executive read | Next action |
|---|---|---|---|---|
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/executive_summary_lane.py | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/headline_lane.py | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/ibm_bullets_lane.py | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/unify_bullets_lane.py | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/executive_summary_judge_remediation.py | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |

### 7. Gap Analysis — Lens 4: Testing Control Gaps

Testing is a control gap where apps_rg/runtime/sections/executive_summary_lane.py lacks regression coverage; fund tests with the relevant fix slice, not as a generic test campaign.

| Rank | Production scope | Current tests found | Missing test scope | Risk | Recommended investment | Trigger |
|---:|---|---|---|---|---|---|
| 1 | apps_rg/runtime/sections/executive_summary_lane.py | none mapped | regression | CRITICAL | Add mapped tests/regression coverage for apps_rg. | current action queue overlap |
| 2 | agentic_core/L5_safety/reasoning/hierarchy_healer.py | none mapped | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 3 | apps_rg/runtime/sections/headline_lane.py | none mapped | regression | CRITICAL | Add mapped tests/regression coverage for apps_rg. | current action queue overlap |
| 4 | agentic_core/L5_safety/reasoning/FileClassificationAgent.py | none mapped | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 5 | apps_rg/runtime/sections/ibm_bullets_lane.py | none mapped | regression | CRITICAL | Add mapped tests/regression coverage for apps_rg. | current action queue overlap |
| 6 | apps_rg/runtime/sections/unify_bullets_lane.py | none mapped | regression | CRITICAL | Add mapped tests/regression coverage for apps_rg. | current action queue overlap |
| 7 | agentic_core/L5_safety/reasoning/root_hygiene_healer.py | none mapped | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 8 | agentic_core/adg/extraction/static_scanner.py | none mapped | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 9 | agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py | none mapped | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 10 | agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py | none mapped | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |

### 8. Gap Analysis — Lens 5: GraphDB / MV Decision Impact

GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.

| Signal | Decision role | Used now? | Why / why not | Action |
|---|---|---|---|---|
| mv_debt_concentration_hotspots | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_exit_disposition_coverage | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_l2_phase_coverage | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_dependency_cone_risk | used_now | True | Structural MV studied (25 ranked rows on `cone_risk_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_eval_coverage_by_path | used_now | True | Linked to a current FIX/action signal, so it changes immediate work order. | Use in current fix slice. |
| mv_graph_chokepoint_bridges | used_now | True | Structural MV studied (25 ranked rows on `bridge_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_graph_critical_path_blast_radius | used_now | True | Structural MV studied (25 ranked rows on `weighted_blast_radius`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_graph_reverse_dependency_hotspots | used_now | True | Structural MV studied (25 ranked rows on `reverse_dependency_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_hotspot_centrality | used_now | True | Structural MV studied (25 ranked rows on `betweenness_approx`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_hotspot_coverage_risk | used_now | True | Linked to a current FIX/action signal, so it changes immediate work order. | Use in current fix slice. |
| mv_newly_introduced_critical_paths | used_now | True | Structural MV studied (25 ranked rows on `criticality_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| runtime_spine | used_now | True | Runtime spine reports 6 semantic failure(s) — present-and-failing runtime proof, not a measurement gap. | Use for blast-radius / refactor / runtime-path / after-green planning. |

Top structural risks (studied from the graph MVs — centrality / blast radius / reverse deps / cones):

| Rank | Scope | Graph signal | Centrality | Blast radius | Reverse dep | Executive read |
|---:|---|---|---|---|---|---|
| 1 | agentic_core/adg/extraction/static_scanner.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint, newly_introduced | 2.0858 | 84.0 | 84.0 | High structural risk — newly-introduced critical path (modified-area regression); overlaps an under-tested coverage hotspot. |
| 2 | agentic_core/L2_execution/utils/write_gateway.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 0.7624 | 162.78 | 83.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 3 | agentic_core/base_agents/SovereignBaseAgent.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 1.3162 | 288.5 | 150.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 4 | agentic_core/L0_routing/config/__init__.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 2.623 | 185.16 | 116.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 5 | agentic_core/runtime/contracts/lifecycle_trace_contract.py | centrality, reverse_dependency, blast_radius, dependency_cone | 92.1284 | 3390.79 | 1848.0 | High structural risk across 4 graph view(s); monitor unless it overlaps a blocker or hotspot. |

### 9. Next Best Actions

| Rank | Action | Scope | Why now | Evidence used | Testing requirement | Done condition |
|---:|---|---|---|---|---|---|
| 1 | Clear red gate 8_trace_replay_eval | 8_trace_replay_eval | Current FIX gates block decision-grade green; inspect delta before assuming structural crisis. | gate | Add mapped tests when touched scope overlaps a hotspot. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 2 | Clear red gate G_REACH_l0_reachability | G_REACH_l0_reachability | Current FIX gates block decision-grade green; inspect delta before assuming structural crisis. | gate | Add mapped tests when touched scope overlaps a hotspot. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 3 | Clear red gate H1_new_orphans_delta_ratchet | H1_new_orphans_delta_ratchet | Current FIX gates block decision-grade green; inspect delta before assuming structural crisis. | gate | Add mapped tests when touched scope overlaps a hotspot. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 4 | Fund mapped tests for apps_rg/runtime/sections/executive_summary_lane.py | apps_rg/runtime/sections/executive_summary_lane.py | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | testing_hotspot | Add mapped tests/regression coverage for apps_rg. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 5 | Refactor high-blast-radius seam agentic_core/adg/extraction/static_scanner.py | agentic_core/adg/extraction/static_scanner.py | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | graphdb | Add mapped tests before refactoring this seam. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 6 | Burn down ratchet S4_unused_imports_ratchet | S4_unused_imports_ratchet | Accepted baseline debt should fall after red gates are clear. | gate | Add tests only when touched scope overlaps hotspot. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 7 | Refine/deprecate low-value ADG signal mv_capability_and_egress_gaps | mv_capability_and_egress_gaps | Suppress or retire signals that do not affect decisions. | mv | No test required unless generator logic changes. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |

### 10. Defer / Delete / Deprecate

| Item | Current value | Recommendation | Rationale |
|---|---|---|---|
| mv_actionable_surface_without_schema | 790 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_specialization_overlap | 3082 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_tool_ratio | 15 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_authority_boundary_breaches | 7 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_capability_and_egress_gaps | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |
| mv_critical_path_segments | 194 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_cross_cutting_witness_tiers | 56 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_determinism_provenance_drift | 6656 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_digest_reconciliation | 6 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_exemptions_near_critical_paths | 3289 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_gateway_bypass_paths | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |
| mv_graph_scc_clusters | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |

### 11. Honest Bottom Line

- Structurally healthy areas are those with CLEAR gates and no promoted GraphDB/testing gaps; do not spend executive time there.
- Actually blocking now: 6 FIX gates; inspect regression delta before declaring a platform crisis.
- Managed debt remains in TRACK ratchets and open non-ratchet rows; schedule it after green unless it overlaps current work.
- Runtime proof gaps are measurement gaps unless runtime artifacts show observed quality failure.
- Clear red gate 8_trace_replay_eval
- Do not chase raw MV counts, guardian gross counts, or diagnostic reports without a decision role.
