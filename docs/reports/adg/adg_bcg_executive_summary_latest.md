## ADG Executive Brief

### 1. What ADG Is

ADG is the X-ray of the codebase. It maps code connections and lets the system ask health-check questions automatically. It turns 'is this codebase healthy?' from opinion into measured facts.

### 2. Patient Size

This patient has 12551 Python files: 7392 production files and 5159 test files. agentic_core contributes 2901 files; apps_* contributes 1500 files. Current snapshot/run ID: 06142026_1721.

### 3. Executive Decision

ADG is BLOCKED: Fund the smallest slice that clears current blockers and attaches tests where hotspot evidence overlaps; keep ratchets after-green. This is a routine_nudge; do not chase Do not rank work by raw MV row count alone., Do not treat guardian inventory as an automatic product failure..

### 4. Gap Analysis — Lens 1: Health Gates

FIX blocks green; TRACK is accepted backlog/ratchet work; CLEAR needs no action. A blocked ADG run is not automatically a platform crisis; regression delta and graph/test linkage determine urgency.

| Bucket | Count | Executive meaning |
|---|---:|---|
| CLEAR | 27 | No action now. |
| TRACK | 18 | Known debt or advisory inventory; burn down after red gates. |
| FIX | 3 | Current blocker or regression requiring action before decision-grade green. |

| Red gate | Total records | Regression / new delta | Executive read | Next action |
|---|---:|---:|---|---|
| M1_module_loc_ratchet | 460 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 459: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| Q2_cyclomatic_complexity_ratchet | 1084 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 1083: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| G_REACH_l0_reachability | 2845 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +2 over baseline 2843 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |

### 5. Gap Analysis — Lens 2: Runtime Proof / Observability

Missing runtime proof is a measurement gap unless an artifact shows runtime failure evidence.

| Runtime proof signal | Status | Executive read | Action |
|---|---|---|---|
| runtime_spine | present | Runtime/structural proof available for interpretation. | Use to confirm runtime path risk. |
| graphdb_queries | present | Runtime/structural proof available for interpretation. | Use to confirm runtime path risk. |
| structural_outputs | present | Runtime/structural proof available for interpretation. | Use to confirm runtime path risk. |

### 6. Gap Analysis — Lens 3: Product / App Risk

No app-specific product gap was promoted in this run; app risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row.

| App / product scope | Risk | Evidence | Executive read | Next action |
|---|---|---|---|---|
| None | No app-specific product gap was promoted in this run |  | App risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row. | Monitor. |

### 7. Gap Analysis — Lens 4: Testing Control Gaps

Testing is a control gap where unknown lacks unit, regression coverage; fund tests with the relevant fix slice, not as a generic test campaign.

| Rank | Production scope | Current tests found | Missing test scope | Risk | Recommended investment | Trigger |
|---:|---|---|---|---|---|---|
| 1 | unknown | none mapped | unit, regression | CRITICAL | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 2 | unknown | none mapped | unit, regression | CRITICAL | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 3 | unknown | none mapped | unit, regression | CRITICAL | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 4 | unknown | none mapped | unit, regression | CRITICAL | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 5 | unknown | none mapped | unit, regression | CRITICAL | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 6 | unknown | none mapped | unit, regression | CRITICAL | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 7 | unknown | none mapped | unit, regression | CRITICAL | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 8 | unknown | none mapped | unit, regression | CRITICAL | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 9 | unknown | none mapped | unit, regression | CRITICAL | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 10 | unknown | none mapped | unit, regression | CRITICAL | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |

### 8. Gap Analysis — Lens 5: GraphDB / MV Decision Impact

GraphDB/MV signals are used as decision drivers only when linked to blockers, testing exposure, ratchets, artifact consistency, or planned slices; raw counts alone stay diagnostic.

| Signal | Decision role | Used now? | Why / why not | Action |
|---|---|---|---|---|
| mv_debt_concentration_hotspots | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_eval_coverage_by_path | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_exit_disposition_coverage | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_graph_reverse_dependency_hotspots | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_hotspot_centrality | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_l2_phase_coverage | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_hotspot_coverage_risk | used_now | True | Linked to a current FIX/action signal, so it changes immediate work order. | Use in current fix slice. |
| mv_capability_and_egress_gaps | deprecate_candidate | False | Empty or stale-looking signal; keep out of inline output until it proves decision value. | Deprecate/delete candidate if still empty next runs. |
| mv_gateway_bypass_paths | deprecate_candidate | False | Empty or stale-looking signal; keep out of inline output until it proves decision value. | Deprecate/delete candidate if still empty next runs. |
| mv_graph_scc_clusters | deprecate_candidate | False | Empty or stale-looking signal; keep out of inline output until it proves decision value. | Deprecate/delete candidate if still empty next runs. |
| mv_live_future_mutation_conflicts | deprecate_candidate | False | Empty or stale-looking signal; keep out of inline output until it proves decision value. | Deprecate/delete candidate if still empty next runs. |
| mv_local_heal_first_breaches | deprecate_candidate | False | Empty or stale-looking signal; keep out of inline output until it proves decision value. | Deprecate/delete candidate if still empty next runs. |

### 9. Next Best Actions

| Rank | Action | Scope | Why now | Evidence used | Testing requirement | Done condition |
|---:|---|---|---|---|---|---|
| 1 | Clear red gate G_REACH_l0_reachability | G_REACH_l0_reachability | Current FIX gates block decision-grade green; inspect delta before assuming structural crisis. | gate | Add mapped tests when touched scope overlaps a hotspot. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 2 | Clear red gate M1_module_loc_ratchet | M1_module_loc_ratchet | Current FIX gates block decision-grade green; inspect delta before assuming structural crisis. | gate | Add mapped tests when touched scope overlaps a hotspot. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 3 | Clear red gate Q2_cyclomatic_complexity_ratchet | Q2_cyclomatic_complexity_ratchet | Current FIX gates block decision-grade green; inspect delta before assuming structural crisis. | gate | Add mapped tests when touched scope overlaps a hotspot. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 4 | Fund mapped tests for unknown | unknown | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | testing_hotspot | Add mapped tests/unit, tests/regression coverage for unknown. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 5 | Burn down ratchet S4_unused_imports_ratchet | S4_unused_imports_ratchet | Accepted baseline debt should fall after red gates are clear. | gate | Add tests only when touched scope overlaps hotspot. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 6 | Refine/deprecate low-value ADG signal mv_capability_and_egress_gaps | mv_capability_and_egress_gaps | Suppress or retire signals that do not affect decisions. | mv | No test required unless generator logic changes. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |

### 10. Defer / Delete / Deprecate

| Item | Current value | Recommendation | Rationale |
|---|---|---|---|
| mv_actionable_surface_without_schema | 814 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_specialization_overlap | 3085 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_tool_ratio | 15 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_authority_boundary_breaches | 7 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_capability_and_egress_gaps | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |
| mv_critical_path_segments | 192 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_cross_cutting_witness_tiers | 56 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_dependency_cone_risk | 11996 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_determinism_provenance_drift | 6838 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_digest_reconciliation | 6 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_exemptions_near_critical_paths | 3467 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_gateway_bypass_paths | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |

### 11. Honest Bottom Line

- Structurally healthy areas are those with CLEAR gates and no promoted GraphDB/testing gaps; do not spend executive time there.
- Actually blocking now: 3 FIX gates; inspect regression delta before declaring a platform crisis.
- Managed debt remains in TRACK ratchets and open non-ratchet rows; schedule it after green unless it overlaps current work.
- Runtime proof gaps are measurement gaps unless runtime artifacts show observed quality failure.
- Clear red gate G_REACH_l0_reachability
- Do not chase raw MV counts, guardian gross counts, or diagnostic reports without a decision role.
