## ADG Executive Brief

### BCG Executive Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Decision status:** REPORT_INCONSISTENT
- **Emit status:** PASS
- **Business read:** ADG is REPORT_INCONSISTENT: Repair report consistency first; the executive order of work is not trustworthy until graph and report agree. Repair report consistency before treating blocker order as authoritative.
- **Technical evidence:**
  - ADG source: artifacts/adg/adg_indexed_06262026_0552.sqlite (snapshot 06262026_0552)
  - FIX gates: 9; TRACK gates: 13
  - Runtime proof is present and FAILING — treat as a quality failure to fix.
  - Testing is a control gap where apps_rg/runtime/sections/executive_summary_lane.py lacks mapped_tests_present coverage; fund tests with the relevant fix slice, not as a generic test campaign.
  - GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.
  - Action rows emitted: 7
- **Priority rule:** Repair report consistency first, then clear blockers, then close testing exposure.

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Repair graph/report consistency | Repair report consistency first; the executive order of work is not trustworthy until graph and report agree. | 2 graph/report mismatch row(s) block decision-grade ordering. | repair_reporting |
| 2 | Remove unused imports | Unused imports add clutter and obscure the live dependency graph. | ADG `06262026_0552`: `S4_unused_imports_ratchet` found 10,747 S4_unused_imports_ratchet, +5 above baseline 10742. Breakout unavailable. | Review the unused import edges evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |
| 3 | Address G_REACH_l0_reachability | This gate still carries decision-grade risk and should be reviewed on its own terms. | ADG `06262026_0552`: `G_REACH_l0_reachability` found 2,799 G_REACH_l0_reachability, +13 above baseline 2786. Breakout unavailable. | Review the Production-layer modules with no import path from any L0 node (orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |
| 4 | Address Q2_cyclomatic_complexity_ratchet | This gate still carries decision-grade risk and should be reviewed on its own terms. | ADG `06262026_0552`: `Q2_cyclomatic_complexity_ratchet` found 1,146 Q2_cyclomatic_complexity_ratchet, +7 above baseline 1139. Breakout unavailable. | Review the Functions with McCabe cyclomatic complexity above ceiling. evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |

Next step: Repair graph/report consistency first.

### 1. What ADG Is

ADG is the X-ray of the codebase. It maps code connections and lets the system ask health-check questions automatically. It turns 'is this codebase healthy?' from opinion into measured facts.

### 2. Patient Size

This patient has 28860 Python files: 23646 production files and 5214 test files. agentic_core contributes 2891 files; apps_* contributes 1442 files. Current snapshot/run ID: 06262026_0552.

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
| CLEAR | 26 | No action now. |
| TRACK | 13 | Known debt or advisory inventory; burn down after red gates. |
| FIX | 9 | Current blocker or regression requiring action before decision-grade green. |

| Red gate | Total records | Regression / new delta | Executive read | Next action |
|---|---:|---:|---|---|
| 8_trace_replay_eval | 1 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +N over baseline None: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| S2_uwg_bypass_ratchet | 1571 | 1 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 1570 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| S4_unused_imports_ratchet | 10747 | 5 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +5 over baseline 10742: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| Q2_cyclomatic_complexity_ratchet | 1146 | 7 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +7 over baseline 1139: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| C3_silent_writes_ratchet | 2034 | 1 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 2033: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| I2_replay_surface_gaps_ratchet | 989 | 1 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 988: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| M_taint_actionable_ratchet | 676 | 1 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 675: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| H1_new_orphans_delta_ratchet | 5 | 5 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +5 over baseline 0: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| 8_trace_replay_eval | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +N over baseline None: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| S2_uwg_bypass_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 1570 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| S4_unused_imports_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +5 over baseline 10742: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| Q2_cyclomatic_complexity_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +7 over baseline 1139: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| C3_silent_writes_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 2033: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |

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
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/executive_summary_lane.py | App risk is promoted because product surface and missing test scope overlap. | Maintain mapped tests with the touched slice. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/headline_lane.py | App risk is promoted because product surface and missing test scope overlap. | Maintain mapped tests with the touched slice. |
| apps_rg | Under-tested product hotspot | apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/ibm_bullets_lane.py | App risk is promoted because product surface and missing test scope overlap. | Maintain mapped tests with the touched slice. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/unify_bullets_lane.py | App risk is promoted because product surface and missing test scope overlap. | Maintain mapped tests with the touched slice. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/executive_summary_judge_remediation.py | App risk is promoted because product surface and missing test scope overlap. | Maintain mapped tests with the touched slice. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/unify_narrative_lane.py | App risk is promoted because product surface and missing test scope overlap. | Maintain mapped tests with the touched slice. |
| apps_rg | Under-tested product hotspot | apps_rg/runtime/sections/ibm_narrative_lane_runtime.py | App risk is promoted because product surface and missing test scope overlap. | Maintain mapped tests with the touched slice. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| apps_rg | App risk is promoted because product surface and missing test scope overlap. | Maintain mapped tests with the touched slice. |
| apps_rg | App risk is promoted because product surface and missing test scope overlap. | Maintain mapped tests with the touched slice. |
| apps_rg | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg | App risk is promoted because product surface and missing test scope overlap. | Maintain mapped tests with the touched slice. |
| apps_rg | App risk is promoted because product surface and missing test scope overlap. | Maintain mapped tests with the touched slice. |

### 8. Gap Analysis — Lens 4: Testing Control Gaps

Tests are the control that prove a risky fix actually works; missing mapped tests turn every red-gate fix into a repeat-risk.

Testing is a control gap where apps_rg/runtime/sections/executive_summary_lane.py lacks mapped_tests_present coverage; fund tests with the relevant fix slice, not as a generic test campaign.

| Rank | Production scope | Current tests found | Missing test scope | Risk | Recommended investment | Trigger |
|---:|---|---|---|---|---|---|
| 1 | apps_rg/runtime/sections/executive_summary_lane.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py; unit: tests/unit/apps_rg/fact_inventory/test_p2_graph_skills_accelerated_closeout.py; unit: tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py; unit: tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py; unit: tests/unit/apps_rg/runtime/sections/test_companion_lane_context.py | mapped_tests_present | CRITICAL | Maintain mapped tests with the touched slice. | current action queue overlap |
| 2 | apps_rg/runtime/sections/headline_lane.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py; unit: tests/unit/apps_rg/fact_inventory/test_p2_graph_skills_accelerated_closeout.py; unit: tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py; unit: tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py; unit: tests/unit/apps_rg/runtime/sections/test_companion_lane_context.py | mapped_tests_present | CRITICAL | Maintain mapped tests with the touched slice. | current action queue overlap |
| 3 | apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_arsenal_graph_w4a.py; unit: tests/unit/apps_rg/fact_inventory/test_arsenal_graph_w4a_spec.py; unit: tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py; unit: tests/unit/apps_rg/fact_inventory/test_c03_graph_full_zero_loss_overwrite.py; unit: tests/unit/apps_rg/fact_inventory/test_c03_graph_skill_granularity_hardening.py | regression | CRITICAL | Add mapped tests/regression coverage for apps_rg. | hotspot coverage MV / test inventory |
| 4 | apps_rg/runtime/sections/ibm_bullets_lane.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py; unit: tests/unit/apps_rg/fact_inventory/test_p2_graph_skills_accelerated_closeout.py; unit: tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py; unit: tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py; unit: tests/unit/apps_rg/runtime/sections/test_companion_lane_context.py | mapped_tests_present | CRITICAL | Maintain mapped tests with the touched slice. | current action queue overlap |
| 5 | apps_rg/runtime/sections/unify_bullets_lane.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py; unit: tests/unit/apps_rg/fact_inventory/test_p2_graph_skills_accelerated_closeout.py; unit: tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py; unit: tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py; unit: tests/unit/apps_rg/runtime/sections/test_companion_lane_context.py | mapped_tests_present | CRITICAL | Maintain mapped tests with the touched slice. | current action queue overlap |
| 6 | apps_rg/runtime/sections/executive_summary_judge_remediation.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py; unit: tests/unit/apps_rg/fact_inventory/test_p2_graph_skills_accelerated_closeout.py; unit: tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py; unit: tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py; unit: tests/unit/apps_rg/runtime/sections/test_companion_lane_context.py | mapped_tests_present | CRITICAL | Maintain mapped tests with the touched slice. | current action queue overlap |
| 7 | apps_rg/runtime/sections/unify_narrative_lane.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py; unit: tests/unit/apps_rg/fact_inventory/test_p2_graph_skills_accelerated_closeout.py; unit: tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py; unit: tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py; unit: tests/unit/apps_rg/runtime/sections/test_companion_lane_context.py | mapped_tests_present | CRITICAL | Maintain mapped tests with the touched slice. | current action queue overlap |
| 8 | apps_rg/runtime/sections/ibm_narrative_lane_runtime.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py; unit: tests/unit/apps_rg/fact_inventory/test_p2_graph_skills_accelerated_closeout.py; unit: tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py; unit: tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py; unit: tests/unit/apps_rg/runtime/sections/test_companion_lane_context.py | mapped_tests_present | CRITICAL | Maintain mapped tests with the touched slice. | current action queue overlap |
| 9 | apps_rg/__main__.py | unit: tests/unit/agentic_core/L5_safety/enforcement/test_registry_verification_enforcer_behavior.py; unit: tests/unit/agentic_core/L5_safety/reasoning/test_hierarchy_healer.py; unit: tests/unit/agentic_core/adg/artifact/test_multi_writer_severity.py; unit: tests/unit/agentic_core/adg/contracts/test_schema_util.py; unit: tests/unit/apps_qna/integrations/test_from_apps_envelope_first.py; unit: tests/unit/apps_rg/cache/test_r1b_ingest.py | mapped_tests_present | CRITICAL | Maintain mapped tests with the touched slice. | current action queue overlap |
| 10 | agentic_core/L5_safety/reasoning/hierarchy_healer.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| apps_rg/runtime/sections/executive_summary_lane.py | Fix confidence improves when this scope has mapped tests. | Maintain mapped tests with the touched slice. |
| apps_rg/runtime/sections/headline_lane.py | Fix confidence improves when this scope has mapped tests. | Maintain mapped tests with the touched slice. |
| apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for apps_rg. |
| apps_rg/runtime/sections/ibm_bullets_lane.py | Fix confidence improves when this scope has mapped tests. | Maintain mapped tests with the touched slice. |
| apps_rg/runtime/sections/unify_bullets_lane.py | Fix confidence improves when this scope has mapped tests. | Maintain mapped tests with the touched slice. |

### 9. Gap Analysis — Lens 5: GraphDB / MV Decision Impact

Graph signals show where a change can ripple through the codebase; they should change priorities only when tied to a blocker, hotspot, or planned slice.

GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.

| Signal | Decision role | Used now? | Why / why not | Action |
|---|---|---|---|---|
| p0_wave_plan | used_after_green | True | Planned-slice / watchlist input for after-green burn-down ordering. | Use for blast-radius / refactor / runtime-path / after-green planning. |
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

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| mv_debt_concentration_hotspots | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_dependency_cone_risk | Structural MV studied (25 ranked rows on `cone_risk_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_eval_coverage_by_path | Linked to a current FIX/action signal, so it changes immediate work order. | Use in current fix slice. |
| mv_exit_disposition_coverage | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_graph_chokepoint_bridges | Structural MV studied (25 ranked rows on `bridge_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |

Top structural risks (studied from the graph MVs — centrality / blast radius / reverse deps / cones):

| Rank | Scope | Graph signal | Centrality | Blast radius | Reverse dep | Executive read |
|---:|---|---|---|---|---|---|
| 1 | agentic_core/adg/extraction/static_scanner.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint, newly_introduced | 2.1438 | 84.0 | 84.0 | High structural risk — newly-introduced critical path (modified-area regression); overlaps an under-tested coverage hotspot. |
| 2 | agentic_core/base_agents/SovereignBaseAgent.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 0.8309 | 179.45 | 93.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 3 | agentic_core/L2_execution/utils/write_gateway.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 0.7557 | 162.04 | 82.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 4 | agentic_core/L0_routing/config/__init__.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 2.5349 | 175.43 | 111.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 5 | agentic_core/runtime/contracts/lifecycle_trace_contract.py | centrality, reverse_dependency, blast_radius, dependency_cone | 88.223 | 3243.65 | 1771.0 | High structural risk across 4 graph view(s); monitor unless it overlaps a blocker or hotspot. |

### 10. Next Best Actions

| Priority | Move | Why it matters | Evidence | Next step |
|---|---|---|---|---|
| 1 | Remove unused imports | Unused imports add clutter and obscure the live dependency graph. | ADG `06262026_0552`: `S4_unused_imports_ratchet` found 10,747 S4_unused_imports_ratchet, +5 above baseline 10742. Breakout unavailable. | Review the unused import edges evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |
| 2 | Address G_REACH_l0_reachability | This gate still carries decision-grade risk and should be reviewed on its own terms. | ADG `06262026_0552`: `G_REACH_l0_reachability` found 2,799 G_REACH_l0_reachability, +13 above baseline 2786. Breakout unavailable. | Review the Production-layer modules with no import path from any L0 node (orphans). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |
| 3 | Address Q2_cyclomatic_complexity_ratchet | This gate still carries decision-grade risk and should be reviewed on its own terms. | ADG `06262026_0552`: `Q2_cyclomatic_complexity_ratchet` found 1,146 Q2_cyclomatic_complexity_ratchet, +7 above baseline 1139. Breakout unavailable. | Review the Functions with McCabe cyclomatic complexity above ceiling. evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |
| 4 | Fund mapped tests for apps_rg/runtime/sections/executive_summary_lane.py | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | Maintain mapped tests with the touched slice. | Add mapped tests before touching this surface again. |
| 5 | Refactor high-blast-radius seam agentic_core/adg/extraction/static_scanner.py | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Refactor after the blocker and test exposure are explicit. |
| 6 | Burn down ratchet F1_untyped_seam_ratchet | Accepted baseline debt should fall after red gates are clear. | 991 floor-row(s) remain on the ratchet gate. | Burn down the ratchet after the current red gates clear. |
| 7 | Refine/deprecate low-value ADG signal mv_capability_and_egress_gaps | Suppress or retire signals that do not affect decisions. | Empty or stale-looking signal; keep out of inline output until it proves decision value. | Deprecate only after the higher-risk surfaces are handled. |

### 11. Defer / Delete / Deprecate

### BCG Deletion Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Deletion status:** DELETION_CANDIDATES
- **Source report status:** PASS
- **Business read:** ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics.
- **Technical evidence:**
  - ADG source: artifacts/adg/adg_indexed_06262026_0552.sqlite (snapshot 06262026_0552)
  - Dead code candidates: 965
  - Dead imports: 965
  - Unresolved imports: 483
  - First-party low-confidence ratio: 1.57%
  - Inferred-symbol ratio: 10.15%
  - Cleanup candidates surfaced: 18
- **Priority rule:** Confirmed dead code first, then unresolved imports, then low-confidence noise, then low-value diagnostics.

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 19 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 2 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 14 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 3 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 13 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 4 | Triage unresolved imports | Unresolved imports are the biggest uncertainty and can hide real cleanup opportunities. | 483 unresolved imports; lead hotspot ADG::Module::tests/integration/retrieval_layers/test_bge_embedding_e2e.py (9). | Trace the top unresolved scope before deleting anything else. |
| 5 | Reduce low-confidence noise | Cleaner evidence makes later reviews faster and lowers the risk of deleting the wrong thing. | First-party low-confidence ratio = 1.57% and inferred-symbol ratio = 10.15%. | Lower the noise floor, then rerun the scan. |
| 6 | Deprecate low-value ADG signals | Remove empty or low-value diagnostics to cut review overhead once the evidence layer is stable. | 13 MV candidates and 5 unused artifacts surfaced by the report. | Deprecate only after higher-confidence cleanup is complete. |

Next step: Deprecate first, then delete after the evidence stays clean.

Current low-value cleanup candidates:

| Item | Type | Current value | Recommendation | Rationale |
|---|---|---|---|---|
| mv_actionable_surface_without_schema | mv | 779 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_specialization_overlap | mv | 3036 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_tool_ratio | mv | 15 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_authority_boundary_breaches | mv | 7 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_capability_and_egress_gaps | mv | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |
| mv_critical_path_segments | mv | 196 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_cross_cutting_witness_tiers | mv | 56 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_determinism_provenance_drift | mv | 6579 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_digest_reconciliation | mv | 6 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_exemptions_near_critical_paths | mv | 3150 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_gateway_bypass_paths | mv | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |
| mv_graph_scc_clusters | mv | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |

### 12. Honest Bottom Line

- Structurally healthy areas are those with CLEAR gates and no promoted GraphDB/testing gaps; do not spend executive time there.
- Actually blocking now: 9 FIX gates; inspect regression delta before declaring a platform crisis.
- Managed debt remains in TRACK ratchets and open non-ratchet rows; schedule it after green unless it overlaps current work.
- Runtime proof gaps are measurement gaps unless runtime artifacts show observed quality failure.
- Remove unused imports
- Do not chase raw MV counts, guardian gross counts, or diagnostic reports without a decision role.
