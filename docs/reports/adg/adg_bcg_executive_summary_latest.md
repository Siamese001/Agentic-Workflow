## ADG Executive Brief

### BCG Executive Brief

- **North star:** Maintain SVP engineer-level repo standards: business-first decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Status:** PASS
- **Business read:** ADG is REPORT_INCONSISTENT: Repair report consistency first; the executive order of work is not trustworthy until graph and report agree.. Spend executive time on blockers and test gaps before accepted debt.
- **Technical evidence:**
  - ADG source: artifacts/adg/adg_indexed_06192026_1144.sqlite (snapshot 06192026_1144)
  - FIX gates: 7; TRACK gates: 17
  - Runtime proof is present and FAILING — treat as a quality failure to fix.
  - Testing is a control gap where apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py lacks regression coverage; fund tests with the relevant fix slice, not as a generic test campaign.
  - GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.
  - Action rows emitted: 7
- **Priority rule:** Fix blockers first, then close testing exposure, then reduce accepted debt.
- **Column key:** Business reason = why the item matters to delivery or governance; Technical reason = the measured evidence; Why this order = why this item is ahead of the next row.

| Priority | Move | Scope | Business reason | Technical reason | Why this order | Decision |
|---------:|------|-------|----------------|-----------------|----------------|----------|
| 1 | Clear red gate B2_layer_skip_ratchet | B2_layer_skip_ratchet | Broad architecture drift: layer skipping increases future change cost across the repo and weakens the authority model. | B2_layer_skip_ratchet: 882 finding(s), +4 vs baseline 878, P1; imports are skipping more than one layer ordinal. | Ranks first because a cross-cutting layer-hop pattern will keep generating rework in every later slice. | fix_blocker |
| 2 | Clear red gate C2_l5_bypass_pview | C2_l5_bypass_pview | Zero-tolerance governance breach: a small number of L5 bypasses can invalidate control assurances even when the footprint is small. | C2_l5_bypass_pview: 2 finding(s), P0; provider/tool calls are skipping the L5 gateway. | Ranks second because the control breach is severe, but the affected surface is narrower than the broader layer-skip regression above. | fix_blocker |
| 3 | Clear red gate F1_untyped_seam_ratchet | F1_untyped_seam_ratchet | Contract-seam debt: wide untyped seams slow safe change and increase integration risk across many callers. | F1_untyped_seam_ratchet: 1,013 finding(s), +7 vs baseline 1,006, P2; cross-layer imports land on empty type surfaces. | Ranks third because it is broad technical debt, but not as cross-cutting as the layer-hop problem or as severe as the P0 control bypass. | fix_blocker |
| 4 | Fund mapped tests for apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | Add mapped tests/regression coverage for apps_rg. | This follows the blocker slice because mapped tests reduce repeat-risk after the failing surface is identified. | add_tests |

Why this order:
- Structurally healthy areas are those with CLEAR gates and no promoted GraphDB/testing gaps; do not spend executive time there.
- Actually blocking now: 7 FIX gates; inspect regression delta before declaring a platform crisis.
- Managed debt remains in TRACK ratchets and open non-ratchet rows; schedule it after green unless it overlaps current work.
- Runtime proof gaps are measurement gaps unless runtime artifacts show observed quality failure.

Next step: Clear red gate B2_layer_skip_ratchet

### 1. What ADG Is

ADG is the X-ray of the codebase. It maps code connections and lets the system ask health-check questions automatically. It turns 'is this codebase healthy?' from opinion into measured facts.

### 2. Patient Size

This patient has 12179 Python files: 6995 production files and 5184 test files. agentic_core contributes 2889 files; apps_* contributes 1431 files. Current snapshot/run ID: 06192026_1144.

### 3. Executive Decision

ADG is REPORT_INCONSISTENT: Repair report consistency first; the executive order of work is not trustworthy until graph and report agree. This is a material_risk; do not chase Do not rank work by raw MV row count alone., Do not let ordinary FIX gates hide report inconsistency or runtime failure..

### 4. Lens 0 — P0 Landmines / Foundation Cracks

P0 landmines are foundation cracks: they can make the graph incomplete, unstable, or misleading before ordinary gate counts are even interpreted.

| P0 signal | Count | Plain-English meaning |
|---|---:|---|
| Layer violations | 0 | Wrong-way dependencies across protected architecture layers. |
| Circular imports | 0 | Modules depend on each other in a loop, making load order brittle. |
| Dynamic execution | 0 | Code is executed dynamically, which can make graph evidence incomplete. |
| Protected surfaces | 0 | Cracks in routing, execution, orchestration, or safety surfaces. |

| Landmine | File | Line | Layer path | Wrong-way? | Protected? | Fan-in | Recommended action |
|---|---|---|---|---|---|---|---|
| None |  | 0 |  | False | False | 0 | No P0 landmine action required. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| none | No immediate action impact. | No P0 landmine action required. |

### 5. Gap Analysis — Lens 1: Health Gates

Health gates tell leaders whether the run is green, blocked, or carrying accepted debt; they should not hide report inconsistency or runtime failures.

FIX blocks green; TRACK is accepted backlog/ratchet work; CLEAR needs no action. A blocked ADG run is not automatically a platform crisis; regression delta and graph/test linkage determine urgency.

| Bucket | Count | Executive meaning |
|---|---:|---|
| CLEAR | 24 | No action now. |
| TRACK | 17 | Known debt or advisory inventory; burn down after red gates. |
| FIX | 7 | Current blocker or regression requiring action before decision-grade green. |

| Red gate | Total records | Regression / new delta | Executive read | Next action |
|---|---:|---:|---|---|
| 8_trace_replay_eval | 458 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +N over baseline None: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| L2_lpg_drift_ratchet | 2 | 1 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 1 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| S4_unused_imports_ratchet | 10756 | 16 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +16 over baseline 10740: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| B2_layer_skip_ratchet | 882 | 4 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +4 over baseline 878: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| Q2_cyclomatic_complexity_ratchet | 1095 | 12 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +12 over baseline 1083: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| C2_l5_bypass_pview | 2 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| F1_untyped_seam_ratchet | 1013 | 7 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +7 over baseline 1006: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| 8_trace_replay_eval | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +N over baseline None: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| L2_lpg_drift_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 1 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| S4_unused_imports_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +16 over baseline 10740: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| B2_layer_skip_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +4 over baseline 878: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| Q2_cyclomatic_complexity_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +12 over baseline 1083: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |

### 6. Gap Analysis — Lens 2: Runtime Proof / Observability

Runtime proof separates a real observed failure from a blind spot; leaders should not treat missing traces as proof of health.

Runtime proof is present and FAILING — treat as a quality failure to fix.

| Runtime proof signal | Status | Executive read | Action |
|---|---|---|---|
| runtime_spine | present_failing | Runtime proof present and FAILING: 6 semantic failure(s) — a quality failure, not a measurement gap. | Fix the failing runtime path before relying on the trace. |
| graphdb_queries | present | Runtime/structural proof present and clean for interpretation. | Use to confirm runtime path risk. |
| structural_outputs | present | Runtime/structural proof present and clean for interpretation. | Use to confirm runtime path risk. |
| mv_eval_coverage_by_path | present | replay/eval coverage MV present with 12 rows; gaps here are replay/eval blind spots, not proven failures. | Close replay/eval gaps for critical paths. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| runtime_spine | Runtime proof present and FAILING: 6 semantic failure(s) — a quality failure, not a measurement gap. | Fix the failing runtime path before relying on the trace. |
| graphdb_queries | Runtime/structural proof present and clean for interpretation. | Use to confirm runtime path risk. |
| structural_outputs | Runtime/structural proof present and clean for interpretation. | Use to confirm runtime path risk. |
| mv_eval_coverage_by_path | replay/eval coverage MV present with 12 rows; gaps here are replay/eval blind spots, not proven failures. | Close replay/eval gaps for critical paths. |

### 7. Gap Analysis — Lens 3: Product / App Risk

Product risk shows whether a structural issue touches user-facing app behavior, not just internal cleanup.

App/product risks were promoted only where hotspot or test evidence changes funding posture.

| App / product scope | Risk | Evidence | Executive read | Next action |
|---|---|---|---|---|
| apps_rg | Under-tested product hotspot | apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/executive_summary_lane.py | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/headline_lane.py | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/ibm_bullets_lane.py | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/unify_bullets_lane.py | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| apps_rg | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |

### 8. Gap Analysis — Lens 4: Testing Control Gaps

Tests are the control that prove a risky fix actually works; missing mapped tests turn every red-gate fix into a repeat-risk.

Testing is a control gap where apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py lacks regression coverage; fund tests with the relevant fix slice, not as a generic test campaign.

| Rank | Production scope | Current tests found | Missing test scope | Risk | Recommended investment | Trigger |
|---:|---|---|---|---|---|---|
| 1 | apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_arsenal_graph_w4a.py; unit: tests/unit/apps_rg/fact_inventory/test_arsenal_graph_w4a_spec.py; unit: tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py; unit: tests/unit/apps_rg/fact_inventory/test_career_track_materialization_p1.py; unit: tests/unit/apps_rg/fact_inventory/test_claim_proof_split_policy.py | regression | CRITICAL | Add mapped tests/regression coverage for apps_rg. | hotspot coverage MV / test inventory |
| 2 | apps_rg/runtime/sections/executive_summary_lane.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py; unit: tests/unit/apps_rg/fact_inventory/test_p2_graph_skills_accelerated_closeout.py; unit: tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py; unit: tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py; unit: tests/unit/apps_rg/runtime/sections/test_companion_lane_context.py | regression | CRITICAL | Add mapped tests/regression coverage for apps_rg. | hotspot coverage MV / test inventory |
| 3 | agentic_core/L5_safety/reasoning/hierarchy_healer.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |
| 4 | apps_rg/runtime/sections/headline_lane.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py; unit: tests/unit/apps_rg/fact_inventory/test_p2_graph_skills_accelerated_closeout.py; unit: tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py; unit: tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py; unit: tests/unit/apps_rg/runtime/sections/test_companion_lane_context.py | regression | CRITICAL | Add mapped tests/regression coverage for apps_rg. | hotspot coverage MV / test inventory |
| 5 | agentic_core/L5_safety/reasoning/FileClassificationAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |
| 6 | apps_rg/runtime/sections/ibm_bullets_lane.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py; unit: tests/unit/apps_rg/fact_inventory/test_p2_graph_skills_accelerated_closeout.py; unit: tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py; unit: tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py; unit: tests/unit/apps_rg/runtime/sections/test_companion_lane_context.py | regression | CRITICAL | Add mapped tests/regression coverage for apps_rg. | hotspot coverage MV / test inventory |
| 7 | apps_rg/runtime/sections/unify_bullets_lane.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py; unit: tests/unit/apps_rg/fact_inventory/test_p2_graph_skills_accelerated_closeout.py; unit: tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py; unit: tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py; unit: tests/unit/apps_rg/runtime/sections/test_companion_lane_context.py | regression | CRITICAL | Add mapped tests/regression coverage for apps_rg. | hotspot coverage MV / test inventory |
| 8 | agentic_core/L5_safety/utils/location_healer_util.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |
| 9 | agentic_core/L5_safety/reasoning/root_hygiene_healer.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |
| 10 | agentic_core/adg/extraction/static_scanner.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg/runtime/sections/executive_summary_lane.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for apps_rg. |
| agentic_core/L5_safety/reasoning/hierarchy_healer.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |
| apps_rg/runtime/sections/headline_lane.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for apps_rg. |
| agentic_core/L5_safety/reasoning/FileClassificationAgent.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |

### 9. Gap Analysis — Lens 5: GraphDB / MV Decision Impact

Graph signals show where a change can ripple through the codebase; they should change priorities only when tied to a blocker, hotspot, or planned slice.

GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.

| Signal | Decision role | Used now? | Why / why not | Action |
|---|---|---|---|---|
| p0_wave_plan | used_after_green | True | Planned-slice / watchlist input for after-green burn-down ordering. | Use for blast-radius / refactor / runtime-path / after-green planning. |
| mv_debt_concentration_hotspots | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_eval_coverage_by_path | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_exit_disposition_coverage | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_hotspot_coverage_risk | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_l2_phase_coverage | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_dependency_cone_risk | used_now | True | Structural MV studied (25 ranked rows on `cone_risk_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_graph_chokepoint_bridges | used_now | True | Structural MV studied (25 ranked rows on `bridge_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_graph_critical_path_blast_radius | used_now | True | Structural MV studied (25 ranked rows on `weighted_blast_radius`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_graph_reverse_dependency_hotspots | used_now | True | Structural MV studied (25 ranked rows on `reverse_dependency_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_hotspot_centrality | used_now | True | Structural MV studied (25 ranked rows on `betweenness_approx`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_newly_introduced_critical_paths | used_now | True | Structural MV studied (25 ranked rows on `criticality_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| mv_debt_concentration_hotspots | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_dependency_cone_risk | Structural MV studied (25 ranked rows on `cone_risk_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_eval_coverage_by_path | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_exit_disposition_coverage | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_graph_chokepoint_bridges | Structural MV studied (25 ranked rows on `bridge_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |

Top structural risks (studied from the graph MVs — centrality / blast radius / reverse deps / cones):

| Rank | Scope | Graph signal | Centrality | Blast radius | Reverse dep | Executive read |
|---:|---|---|---|---|---|---|
| 1 | agentic_core/adg/extraction/static_scanner.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint, newly_introduced | 2.1531 | 84.0 | 84.0 | High structural risk — newly-introduced critical path (modified-area regression); overlaps an under-tested coverage hotspot. |
| 2 | agentic_core/base_agents/SovereignBaseAgent.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 0.8345 | 179.39 | 93.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 3 | agentic_core/L0_routing/config/__init__.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 2.5459 | 175.21 | 111.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 4 | agentic_core/L2_execution/utils/write_gateway.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 0.6072 | 125.06 | 64.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 5 | agentic_core/runtime/contracts/lifecycle_trace_contract.py | centrality, reverse_dependency, blast_radius, dependency_cone | 88.6765 | 3244.58 | 1772.0 | High structural risk across 4 graph view(s); monitor unless it overlaps a blocker or hotspot. |

### 10. Next Best Actions

| Rank | Action | Scope | Why now | Evidence used | Testing requirement | Done condition |
|---:|---|---|---|---|---|---|
| 1 | Clear red gate B2_layer_skip_ratchet | B2_layer_skip_ratchet | Broad architecture drift: layer skipping increases future change cost across the repo and weakens the authority model. | gate | Add mapped tests when touched scope overlaps a hotspot. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 2 | Clear red gate C2_l5_bypass_pview | C2_l5_bypass_pview | Zero-tolerance governance breach: a small number of L5 bypasses can invalidate control assurances even when the footprint is small. | gate | Add mapped tests when touched scope overlaps a hotspot. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 3 | Clear red gate F1_untyped_seam_ratchet | F1_untyped_seam_ratchet | Contract-seam debt: wide untyped seams slow safe change and increase integration risk across many callers. | gate | Add mapped tests when touched scope overlaps a hotspot. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 4 | Fund mapped tests for apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | testing_hotspot | Add mapped tests/regression coverage for apps_rg. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 5 | Refactor high-blast-radius seam agentic_core/adg/extraction/static_scanner.py | agentic_core/adg/extraction/static_scanner.py | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | graphdb | Add mapped tests before refactoring this seam. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 6 | Burn down ratchet G_REACH_l0_reachability | G_REACH_l0_reachability | Accepted baseline debt should fall after red gates are clear. | gate | Add tests only when touched scope overlaps hotspot. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 7 | Refine/deprecate low-value ADG signal mv_graph_scc_clusters | mv_graph_scc_clusters | Suppress or retire signals that do not affect decisions. | mv | No test required unless generator logic changes. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |

### 11. Defer / Delete / Deprecate

### BCG Deletion Brief

- **North star:** Maintain SVP engineer-level repo standards: business-first decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Status:** PASS
- **Business read:** No deletions are approved in this run because ADG found 0 confirmed dead-code candidates; reduce uncertainty first, then deprecate noisy diagnostics.
- **Technical evidence:**
  - Dead code candidates: 0
  - Dead imports: 0
  - Unresolved imports: 588
  - First-party low-confidence ratio: 1.92%
  - Inferred-symbol ratio: 10.13%
  - Cleanup candidates surfaced: 20
- **Priority rule:** Confirmed dead code first, then unresolved imports, then low-confidence noise, then low-value diagnostics.
- **Column key:** Business reason = why the item matters to delivery or governance; Technical reason = the measured evidence; Why this order = why this item is ahead of the next row.

| Priority | Move | Scope | Business reason | Technical reason | Why this order | Decision |
|---------:|------|-------|----------------|-----------------|----------------|----------|
| 1 | Hold all deletion | whole codebase | The scan found no confirmed dead code, so deleting anything now would be speculative and could break working paths. | Dead-code candidates = 0 and dead imports = 0. | No proven target means the safest action is to pause deletion. | defer |
| 2 | Triage unresolved imports | ADG::Module::tests/ops_scripts/ci/test_adg_accelerator_compliance_gate.py | Unresolved imports are the biggest uncertainty and can hide real cleanup opportunities. | 588 unresolved imports; lead hotspot ADG::Module::tests/ops_scripts/ci/test_adg_accelerator_compliance_gate.py (62). | We need a cleaner signal before we can trust deletion decisions. | investigate |
| 3 | Reduce low-confidence noise | first-party nodes | Cleaner evidence makes later reviews faster and lowers the risk of deleting the wrong thing. | First-party low-confidence ratio = 1.92% and inferred-symbol ratio = 10.13%. | Noise reduction improves the quality of the next scan and makes future deletions safer. | stabilize |
| 4 | Deprecate low-value ADG signals | materialized views and unused artifacts | Remove empty or low-value diagnostics to cut review overhead once the evidence layer is stable. | 13 MV candidates and 7 unused artifacts surfaced by the report. | This is cheap cleanup, but it should follow the evidence cleanup work above. | deprecate |

Why this order:
- Confirmed dead code is the highest-confidence waste and should be removed first.
- Unresolved imports are the biggest uncertainty and can hide real cleanup work.
- Low-confidence and inferred-symbol noise should be reduced before taking more aggressive action.
- Low-value diagnostics are cheap to deprecate once the evidence layer is cleaner.

Next step: Deprecate first, then delete after the evidence stays clean.

Current low-value cleanup candidates:

| Item | Type | Current value | Recommendation | Rationale |
|---|---|---|---|---|
| mv_actionable_surface_without_schema | mv | 769 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_specialization_overlap | mv | 3034 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_tool_ratio | mv | 15 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_authority_boundary_breaches | mv | 7 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_capability_and_egress_gaps | mv | 1 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_critical_path_segments | mv | 196 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_cross_cutting_witness_tiers | mv | 56 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_determinism_provenance_drift | mv | 6558 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_digest_reconciliation | mv | 6 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_exemptions_near_critical_paths | mv | 3162 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_gateway_bypass_paths | mv | 2 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_graph_scc_clusters | mv | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |

### 12. Honest Bottom Line

- Structurally healthy areas are those with CLEAR gates and no promoted GraphDB/testing gaps; do not spend executive time there.
- Actually blocking now: 7 FIX gates; inspect regression delta before declaring a platform crisis.
- Managed debt remains in TRACK ratchets and open non-ratchet rows; schedule it after green unless it overlaps current work.
- Runtime proof gaps are measurement gaps unless runtime artifacts show observed quality failure.
- Clear red gate B2_layer_skip_ratchet
- Do not chase raw MV counts, guardian gross counts, or diagnostic reports without a decision role.
