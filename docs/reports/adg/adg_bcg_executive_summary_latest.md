## ADG Executive Brief

### BCG Executive Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Decision status:** REPORT_INCONSISTENT
- **Emit status:** PASS
- **Business read:** ADG is REPORT_INCONSISTENT: Repair report consistency first; the executive order of work is not trustworthy until graph and report agree. Repair report consistency before treating blocker order as authoritative.
- **Technical evidence:**
  - ADG source: artifacts/adg/adg_indexed_06282026_1945.sqlite (snapshot 06282026_1945)
  - FIX gates: 10; burn-down gates: 11; KPI/watchlist gates: 2
  - KPI split: foundation blockers 200; P0 audit net 3; P0 live gate drivers 3
  - Runtime proof is present and FAILING — treat as a quality failure to fix.
  - Testing is a control gap where apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py lacks regression coverage; fund tests with the relevant fix slice, not as a generic test campaign.
  - GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.
  - Action rows emitted: 7
- **Priority rule:** Repair report consistency first, then clear blockers, then close testing exposure.

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Repair graph/report consistency | Repair report consistency first; the executive order of work is not trustworthy until graph and report agree. | 6 graph/report mismatch row(s) block decision-grade ordering. | repair_reporting |
| 2 | Remove unused imports | Unused imports add clutter and obscure the live dependency graph. | ADG `06282026_1945`: `S4_unused_imports_ratchet` found 10,772 S4_unused_imports_ratchet, +22 above baseline 10750. Breakout unavailable. | Review the unused import edges evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |
| 3 | Address S2_uwg_bypass_ratchet | This gate still carries decision-grade risk and should be reviewed on its own terms. | ADG `06282026_1945`: `S2_uwg_bypass_ratchet` found 1,601 S2_uwg_bypass_ratchet, +30 above baseline 1571. Breakout unavailable. | Review the Write paths that bypass UWG (overlay on write_sovereignty edges). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |
| 4 | Address Q2_cyclomatic_complexity_ratchet | This gate still carries decision-grade risk and should be reviewed on its own terms. | ADG `06282026_1945`: `Q2_cyclomatic_complexity_ratchet` found 1,168 Q2_cyclomatic_complexity_ratchet, +20 above baseline 1148. Breakout unavailable. | Review the Functions with McCabe cyclomatic complexity above ceiling. evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |

Next step: Repair graph/report consistency first.

### 1. What ADG Is

ADG is the X-ray of the codebase. It maps code connections and lets the system ask health-check questions automatically. It turns 'is this codebase healthy?' from opinion into measured facts.

### 2. Patient Size

This patient has 28891 Python files: 23661 production files and 5230 test files. agentic_core contributes 2891 files; apps_* contributes 1456 files. Current snapshot/run ID: 06282026_1945.

### 3. Executive Decision

ADG is REPORT_INCONSISTENT: Repair report consistency first; the executive order of work is not trustworthy until graph and report agree. This is a material_risk; do not chase Do not rank work by raw MV row count alone., Do not let ordinary FIX gates hide report inconsistency or runtime failure..

### 3A. KPI Scorecard — Decision vs Audit

P0 is split into three ledgers: foundation blockers, audit inventory, and live gate drivers.

Do not add these counts together. A P0 audit finding is not a foundation blocker unless it comes from the foundation-blocker wave plan.

| KPI | Value | Plain-English meaning | Action rule |
|---|---|---|---|
| Foundation blockers | 200 | P0 trust hazards that can make ADG evidence incomplete, unstable, or misleading. | Stop the line if greater than zero; if not loaded, do not claim clean. |
| P0 audit net | 3 | P0 severity audit inventory after guardian exemptions. | Audit-only unless mapped to a failing gate, runtime failure, hotspot, or changed code. |
| P0 live gate drivers | 3 | Current red P0 gates that can drive today's work order. | Can drive priority when the gate is FIX/red and decision-linked. |

Zero foundation blockers can coexist with nonzero P0 audit net because they measure different ledgers: run-trust hazards versus severity audit inventory.

| Band | Audit gross | Guardian / exempted | Audit net | Foundation blockers | Live gate drivers | Action role |
|---|---|---|---|---|---|---|
| P0 | 43 | 40 | 3 | 200 | 3 | Stop-the-line only if foundation blockers are present; otherwise audit net is evidence to map. |
| P1 | 1,150 | 1,144 | 6 | n/a | 3 | Severity inventory to map to a failing gate, hotspot, changed code, or owner. |
| P2 | 743 | 716 | 27 | n/a | 1 | Severity inventory to map to a failing gate, hotspot, changed code, or owner. |
| P3 | 19,151 | 87 | 19,064 | n/a | 3 | Severity inventory to map to a failing gate, hotspot, changed code, or owner. |

### 4. Lens 0 — Foundation Blockers

Foundation blockers are P0 trust hazards: they can make the graph incomplete, unstable, or misleading before ordinary gate counts are even interpreted.

Clear dynamic execution, circular imports, protected-surface boundary breaks, and high fan-in wrong-way imports before treating lower-priority cleanup as reliable.

| Foundation signal | Count | Plain-English meaning |
|---|---:|---|
| Layer violations | 0 | Wrong-way dependencies across protected architecture layers. |
| Circular imports | 0 | Modules depend on each other in a loop, making load order brittle. |
| Dynamic execution | 0 | Code is executed dynamically, which can make graph evidence incomplete. |
| Protected surfaces | 200 | Cracks in routing, execution, orchestration, or safety surfaces. |

| Foundation blocker | File | Line | Layer path | Wrong-way? | Protected? | Fan-in | Recommended action |
|---|---|---|---|---|---|---|---|
| l0_reachability_orphan | agentic_core/L1_cognition/__init__.py | 0 | L0 -> L1 | False | True | 0 | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |
| l0_reachability_orphan | agentic_core/L1_cognition/apps_research_c0_binding.py | 0 | L0 -> L1 | False | True | 0 | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |
| l0_reachability_orphan | agentic_core/L1_cognition/apps_research_l1_binding.py | 0 | L0 -> L1 | False | True | 0 | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |
| l0_reachability_orphan | agentic_core/L1_cognition/apps_research_l1_binding_v2.py | 0 | L0 -> L1 | False | True | 0 | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |
| l0_reachability_orphan | agentic_core/L1_cognition/bridges/__init__.py | 0 | L0 -> L1 | False | True | 0 | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |
| l0_reachability_orphan | agentic_core/L1_cognition/bridges/u0_to_l1_plan.py | 0 | L0 -> L1 | False | True | 0 | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |
| l0_reachability_orphan | agentic_core/L1_cognition/bridges/u0_to_l1_planning.py | 0 | L0 -> L1 | False | True | 0 | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |
| l0_reachability_orphan | agentic_core/L1_cognition/c0_context/__init__.py | 0 | L0 -> L1 | False | True | 0 | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| l0_reachability_orphan | Fixing this improves trust in ADG ordering before ordinary gate cleanup. | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |
| l0_reachability_orphan | Fixing this improves trust in ADG ordering before ordinary gate cleanup. | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |
| l0_reachability_orphan | Fixing this improves trust in ADG ordering before ordinary gate cleanup. | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |
| l0_reachability_orphan | Fixing this improves trust in ADG ordering before ordinary gate cleanup. | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |
| l0_reachability_orphan | Fixing this improves trust in ADG ordering before ordinary gate cleanup. | Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety. |

### 5. Gap Analysis — Lens 1: Health Gates

Health gates tell leaders whether the run is green, blocked, carrying owned burn-down debt, or merely showing KPI/watchlist signals.

FIX blocks green; BURN is accepted work; KPI is trend/watchlist; CLEAR needs no action. A blocked ADG run is not automatically a platform crisis; regression delta and graph/test linkage determine urgency.

| Bucket | Count | Executive meaning |
|---|---:|---|
| CLEAR | 26 | No action now. |
| BURN | 11 | Owned backlog; burn down after red gates. |
| KPI | 2 | Watchlist/trend only; no burn-down unless planned. |
| FIX | 10 | Current blocker or regression requiring action before decision-grade green. |

| Red gate | Total records | Regression / new delta | Executive read | Next action |
|---|---:|---:|---|---|
| 13_core_imports_apps | 35 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| 10_infra_wiring | 3 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| S4_unused_imports_ratchet | 10772 | 22 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +22 over baseline 10750: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| C3_silent_writes_ratchet | 2050 | 16 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +16 over baseline 2034: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| S2_uwg_bypass_ratchet | 1601 | 30 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +30 over baseline 1571 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| Q2_cyclomatic_complexity_ratchet | 1168 | 20 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +20 over baseline 1148: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| I2_replay_surface_gaps_ratchet | 993 | 4 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +4 over baseline 989: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| M_taint_actionable_ratchet | 681 | 5 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +5 over baseline 676: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| 13_core_imports_apps | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| 10_infra_wiring | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| S4_unused_imports_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +22 over baseline 10750: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| C3_silent_writes_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +16 over baseline 2034: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| S2_uwg_bypass_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +30 over baseline 1571 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |

KPI / watchlist signals:

| Signal | Rows | Executive read | Recommended action |
|---|---|---|---|
| D2_role_duplication_warn | 105 | Watchlist signal; do not treat as burn-down work without an owner and target. | Advisory KPI: watch the trend; no action required to pass CI. |
| D1_layer_doc_binding | 3 | Watchlist signal; do not treat as burn-down work without an owner and target. | Advisory KPI: watch the trend; no action required to pass CI. |

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

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| apps_rg | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression coverage for apps_rg. |

### 8. Gap Analysis — Lens 4: Testing Control Gaps

Tests are the control that prove a risky fix actually works; missing mapped tests turn every red-gate fix into a repeat-risk.

Testing is a control gap where apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py lacks regression coverage; fund tests with the relevant fix slice, not as a generic test campaign.

| Rank | Production scope | Current tests found | Missing test scope | Risk | Recommended investment | Trigger |
|---:|---|---|---|---|---|---|
| 1 | apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | unit: tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py; unit: tests/unit/apps_rg/fact_inventory/test_arsenal_graph_w4a.py; unit: tests/unit/apps_rg/fact_inventory/test_arsenal_graph_w4a_spec.py; unit: tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py; unit: tests/unit/apps_rg/fact_inventory/test_c03_graph_full_zero_loss_overwrite.py; unit: tests/unit/apps_rg/fact_inventory/test_c03_graph_skill_granularity_hardening.py | regression | CRITICAL | Add mapped tests/regression coverage for apps_rg. | hotspot coverage MV / test inventory |
| 2 | agentic_core/L5_safety/reasoning/FileClassificationAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |
| 3 | agentic_core/L5_safety/utils/location_healer_util.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |
| 4 | agentic_core/L5_safety/reasoning/root_hygiene_healer.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |
| 5 | agentic_core/adg/extraction/static_scanner.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |
| 6 | agentic_core/L6_system_learning/engines/semantic_index_registry.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |
| 7 | agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |
| 8 | agentic_core/L2_execution/utils/write_gateway.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |
| 9 | agentic_core/L5_safety/reasoning/location_validator.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |
| 10 | agentic_core/L5_safety/types/heal_llm_seam_types.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | hotspot coverage MV / test inventory |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for apps_rg. |
| agentic_core/L5_safety/reasoning/FileClassificationAgent.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |
| agentic_core/L5_safety/utils/location_healer_util.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |
| agentic_core/L5_safety/reasoning/root_hygiene_healer.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |
| agentic_core/adg/extraction/static_scanner.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |

### 9. Gap Analysis — Lens 5: GraphDB / MV Decision Impact

Graph signals show where a change can ripple through the codebase; they should change priorities only when tied to a blocker, hotspot, or planned slice.

GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.

| Signal | Decision role | Used now? | Why / why not | Action |
|---|---|---|---|---|
| p0_wave_plan | used_after_green | True | Planned-slice / watchlist input for after-green burn-down ordering. | Use for blast-radius / refactor / runtime-path / after-green planning. |
| mv_debt_concentration_hotspots | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_exit_disposition_coverage | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_hotspot_coverage_risk | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_l2_phase_coverage | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_dependency_cone_risk | used_now | True | Structural MV studied (25 ranked rows on `cone_risk_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
| mv_eval_coverage_by_path | used_now | True | Linked to a current FIX/action signal, so it changes immediate work order. | Use in current fix slice. |
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
| mv_eval_coverage_by_path | Linked to a current FIX/action signal, so it changes immediate work order. | Use in current fix slice. |
| mv_exit_disposition_coverage | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_graph_chokepoint_bridges | Structural MV studied (25 ranked rows on `bridge_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |

Top structural risks (studied from the graph MVs — centrality / blast radius / reverse deps / cones):

| Rank | Scope | Graph signal | Centrality | Blast radius | Reverse dep | Executive read |
|---:|---|---|---|---|---|---|
| 1 | agentic_core/adg/extraction/static_scanner.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint, newly_introduced | 2.1926 | 84.0 | 84.0 | High structural risk — newly-introduced critical path (modified-area regression); overlaps an under-tested coverage hotspot. |
| 2 | agentic_core/base_agents/SovereignBaseAgent.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 0.8116 | 175.93 | 91.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 3 | agentic_core/L2_execution/utils/write_gateway.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 0.7453 | 160.06 | 81.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 4 | agentic_core/L0_routing/config/__init__.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 2.5178 | 173.4 | 110.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 5 | agentic_core/runtime/contracts/lifecycle_trace_contract.py | centrality, reverse_dependency, blast_radius, dependency_cone | 87.92 | 3240.29 | 1770.0 | High structural risk across 4 graph view(s); monitor unless it overlaps a blocker or hotspot. |

### 10. Next Best Actions

| Priority | Move | Why it matters | Evidence | Next step |
|---|---|---|---|---|
| 1 | Remove unused imports | Unused imports add clutter and obscure the live dependency graph. | ADG `06282026_1945`: `S4_unused_imports_ratchet` found 10,772 S4_unused_imports_ratchet, +22 above baseline 10750. Breakout unavailable. | Review the unused import edges evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |
| 2 | Address S2_uwg_bypass_ratchet | This gate still carries decision-grade risk and should be reviewed on its own terms. | ADG `06282026_1945`: `S2_uwg_bypass_ratchet` found 1,601 S2_uwg_bypass_ratchet, +30 above baseline 1571. Breakout unavailable. | Review the Write paths that bypass UWG (overlay on write_sovereignty edges). evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |
| 3 | Address Q2_cyclomatic_complexity_ratchet | This gate still carries decision-grade risk and should be reviewed on its own terms. | ADG `06282026_1945`: `Q2_cyclomatic_complexity_ratchet` found 1,168 Q2_cyclomatic_complexity_ratchet, +20 above baseline 1148. Breakout unavailable. | Review the Functions with McCabe cyclomatic complexity above ceiling. evidence. Investigate evidence before changing code; the current choices are Investigate evidence, Fix, Adapter/interface, Guardian exemption. |
| 4 | Fund mapped tests for apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | Add mapped tests/regression coverage for apps_rg. | Add mapped tests before touching this surface again. |
| 5 | Refactor high-blast-radius seam agentic_core/adg/extraction/static_scanner.py | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Refactor after the blocker and test exposure are explicit. |
| 6 | Burn down ratchet G_REACH_l0_reachability | Accepted baseline debt should fall after red gates are clear. | 1,495 floor-row(s) remain on the ratchet gate. | Burn down the ratchet after the current red gates clear. |
| 7 | Refine/deprecate low-value ADG signal mv_capability_and_egress_gaps | Suppress or retire signals that do not affect decisions. | Empty or stale-looking signal; keep out of inline output until it proves decision value. | Deprecate only after the higher-risk surfaces are handled. |

### 11. Defer / Delete / Deprecate

### BCG Deletion Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Deletion status:** DELETION_CANDIDATES
- **Source report status:** PASS
- **Business read:** ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics.
- **Technical evidence:**
  - ADG source: artifacts/adg/adg_indexed_06282026_1945.sqlite (snapshot 06282026_1945)
  - Dead code candidates: 964
  - Dead imports: 964
  - Unresolved imports: 483
  - First-party low-confidence ratio: 1.57%
  - Inferred-symbol ratio: 10.16%
  - Cleanup candidates surfaced: 19
- **Priority rule:** Confirmed dead code first, then unresolved imports, then low-confidence noise, then low-value diagnostics.

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 19 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 2 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 14 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 3 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 13 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 4 | Triage unresolved imports | Unresolved imports are the biggest uncertainty and can hide real cleanup opportunities. | 483 unresolved imports; lead hotspot ADG::Module::tests/integration/retrieval_layers/test_bge_embedding_e2e.py (9). | Trace the top unresolved scope before deleting anything else. |
| 5 | Reduce low-confidence noise | Cleaner evidence makes later reviews faster and lowers the risk of deleting the wrong thing. | First-party low-confidence ratio = 1.57% and inferred-symbol ratio = 10.16%. | Lower the noise floor, then rerun the scan. |
| 6 | Deprecate low-value ADG signals | Remove empty or low-value diagnostics to cut review overhead once the evidence layer is stable. | 13 MV candidates and 6 unused artifacts surfaced by the report. | Deprecate only after higher-confidence cleanup is complete. |

Next step: Deprecate first, then delete after the evidence stays clean.

Current low-value cleanup candidates:

| Item | Type | Current value | Recommendation | Rationale |
|---|---|---|---|---|
| mv_actionable_surface_without_schema | mv | 783 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_specialization_overlap | mv | 3036 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_tool_ratio | mv | 15 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_authority_boundary_breaches | mv | 7 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_capability_and_egress_gaps | mv | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |
| mv_critical_path_segments | mv | 196 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_cross_cutting_witness_tiers | mv | 56 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_determinism_provenance_drift | mv | 6594 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_digest_reconciliation | mv | 6 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_exemptions_near_critical_paths | mv | 3162 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_gateway_bypass_paths | mv | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |
| mv_graph_scc_clusters | mv | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |

### 12. Honest Bottom Line

- Structurally healthy areas are those with CLEAR gates and no promoted GraphDB/testing gaps; do not spend executive time there.
- Actually blocking now: 10 FIX gates; inspect regression delta before declaring a platform crisis.
- Managed debt remains in TRACK ratchets and open non-ratchet rows; schedule it after green unless it overlaps current work.
- Runtime proof gaps are measurement gaps unless runtime artifacts show observed quality failure.
- Remove unused imports
- Do not chase raw MV counts, guardian gross counts, or diagnostic reports without a decision role.
