## ADG Executive Brief

### BCG Executive Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Decision status:** REPORT_INCONSISTENT
- **Emit status:** PASS
- **Business read:** ADG is REPORT_INCONSISTENT: Repair report consistency first; the executive order of work is not trustworthy until graph and report agree. Repair report consistency before treating blocker order as authoritative.
- **Technical evidence:**
  - ADG source: artifacts/adg/adg_indexed_07032026_0358.sqlite (snapshot 07032026_0358)
  - FIX gates: 1; burn-down gates: 15; KPI/watchlist gates: 5
  - KPI split: foundation blockers 201; P0 audit net 4; P0 live gate drivers 1
  - Runtime proof is present and FAILING — treat as a quality failure to fix.
  - Testing is a control gap where agentic_core/L5_safety/reasoning/FileClassificationAgent.py lacks regression coverage; fund tests with the relevant fix slice, not as a generic test campaign.
  - GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.
  - Action rows emitted: 5
- **Priority rule:** Decision queue: repair consistency, then remove concrete P0 hard stops/regressions; do not let high-volume P3 hygiene outrank P0 safety/governance gates.

Decision gate:

| Gate | Why it matters | Evidence | Required before ranking |
|------|----------------|----------|-------------------------|
| Repair graph/report consistency | The executive order is not decision-grade until graph and report agree. | 6 graph/report mismatch row(s) block decision-grade ordering. | Repair report consistency, then rerun ADG before treating the ranked work queue as authoritative. |

Fix now:

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Stop core importing apps | Core importing apps breaks the core/app boundary and directly weakens provider-agnostic core. | ADG `07032026_0358`: `13_core_imports_apps` found 5 13_core_imports_apps. Breakout unavailable. | Move app-specific bindings behind an adapter or app-owned wiring surface; core should keep only generic contracts. |
| 2 | Fund mapped tests for agentic_core/L5_safety/reasoning/FileClassificationAgent.py | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | Add mapped tests/regression coverage for agentic_core. | Add mapped tests before touching this surface again. |
| 3 | Refactor high-blast-radius seam agentic_core/adg/extraction/static_scanner.py | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Refactor after the blocker and test exposure are explicit. |
| 4 | Burn down ratchet C3_silent_writes_ratchet | Accepted baseline debt should fall after red gates are clear. | 2,055 floor-row(s) remain on the ratchet gate. | Burn down the ratchet after the current red gates clear. |

Next step: Repair graph/report consistency first.

### 1. What ADG Is

ADG is the X-ray of the codebase. It maps code connections and lets the system ask health-check questions automatically. It turns 'is this codebase healthy?' from opinion into measured facts.

### 2. Patient Size

This patient has 12310 Python files: 7069 production files and 5241 test files. agentic_core contributes 2889 files; apps_* contributes 1468 files. Current snapshot/run ID: 07032026_0358.

### 3. Executive Decision

ADG is REPORT_INCONSISTENT: Repair report consistency first; the executive order of work is not trustworthy until graph and report agree. This is a material_risk; do not chase Do not rank work by raw MV row count alone., Do not let ordinary FIX gates hide report inconsistency or runtime failure..

### 3A. KPI Scorecard — Decision vs Audit

P0 is split into three ledgers: foundation blockers, audit inventory, and live gate drivers.

Do not add these counts together. A P0 audit finding is not a foundation blocker unless it comes from the foundation-blocker wave plan.

| KPI | Value | Plain-English meaning | Action rule |
|---|---|---|---|
| Foundation blockers | 201 | P0 trust hazards that can make ADG evidence incomplete, unstable, or misleading. | Stop the line if greater than zero; if not loaded, do not claim clean. |
| P0 audit net | 4 | P0 severity audit inventory after guardian exemptions. | Audit-only unless mapped to a failing gate, runtime failure, hotspot, or changed code. |
| P0 live gate drivers | 1 | Current red P0 gates that can drive today's work order. | Can drive priority when the gate is FIX/red and decision-linked. |

Zero foundation blockers can coexist with nonzero P0 audit net because they measure different ledgers: run-trust hazards versus severity audit inventory.

| Band | Audit gross | Guardian / exempted | Audit net | Foundation blockers | Live gate drivers | Action role |
|---|---|---|---|---|---|---|
| P0 | 37 | 33 | 4 | 201 | 1 | Stop-the-line only if foundation blockers are present; otherwise audit net is evidence to map. |
| P1 | 1,146 | 1,143 | 3 | n/a | 0 | Severity inventory to map to a failing gate, hotspot, changed code, or owner. |
| P2 | 745 | 716 | 29 | n/a | 0 | Severity inventory to map to a failing gate, hotspot, changed code, or owner. |
| P3 | 19,235 | 87 | 19,148 | n/a | 0 | Severity inventory to map to a failing gate, hotspot, changed code, or owner. |

### 4. Lens 0 — Foundation Blockers

Foundation blockers are P0 trust hazards: they can make the graph incomplete, unstable, or misleading before ordinary gate counts are even interpreted.

Clear dynamic execution, circular imports, protected-surface boundary breaks, and high fan-in wrong-way imports before treating lower-priority cleanup as reliable.

| Foundation signal | Count | Plain-English meaning |
|---|---:|---|
| Layer violations | 1 | Wrong-way dependencies across protected architecture layers. |
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
| CLEAR | 28 | No action now. |
| BURN | 15 | Owned backlog; burn down after red gates. |
| KPI | 5 | Watchlist/trend only; no burn-down unless planned. |
| FIX | 1 | Current blocker or regression requiring action before decision-grade green. |

| Red gate | Total records | Regression / new delta | Executive read | Next action |
|---|---:|---:|---|---|
| 13_core_imports_apps | 5 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| 13_core_imports_apps | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |

KPI / watchlist signals:

| Signal | Rows | Executive read | Recommended action |
|---|---|---|---|
| S4_unused_imports_ratchet | 10777 | Watchlist signal; do not treat as burn-down work without an owner and target. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| Q2_cyclomatic_complexity_ratchet | 1177 | Watchlist signal; do not treat as burn-down work without an owner and target. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| M1_module_loc_ratchet | 467 | Watchlist signal; do not treat as burn-down work without an owner and target. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
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

No app-specific product gap was promoted in this run; app risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row.

| App / product scope | Risk | Evidence | Executive read | Next action |
|---|---|---|---|---|
| None | No app-specific product gap was promoted in this run |  | App risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row. | Monitor. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| none | No immediate action impact. | No product-scope action promoted. |

### 8. Gap Analysis — Lens 4: Testing Control Gaps

Tests are the control that prove a risky fix actually works; missing mapped tests turn every red-gate fix into a repeat-risk.

Testing is a control gap where agentic_core/L5_safety/reasoning/FileClassificationAgent.py lacks regression coverage; fund tests with the relevant fix slice, not as a generic test campaign.

| Rank | Production scope | Current tests found | Missing test scope | Risk | Recommended investment | Trigger |
|---:|---|---|---|---|---|---|
| 1 | agentic_core/L5_safety/reasoning/FileClassificationAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 2 | agentic_core/L5_safety/reasoning/root_hygiene_healer.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 3 | agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 4 | agentic_core/L5_safety/reasoning/location_validator.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 5 | agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 6 | agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 7 | agentic_core/L5_safety/reasoning/SystemArchitectAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 8 | agentic_core/L0_routing/__init__.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 9 | agentic_core/L5_safety/reasoning/CodeHealerAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 10 | agentic_core/L5_safety/reasoning/PascalSovereigntyAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| agentic_core/L5_safety/reasoning/FileClassificationAgent.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |
| agentic_core/L5_safety/reasoning/root_hygiene_healer.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |
| agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |
| agentic_core/L5_safety/reasoning/location_validator.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |
| agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |

### 9. Gap Analysis — Lens 5: GraphDB / MV Decision Impact

Graph signals show where a change can ripple through the codebase; they should change priorities only when tied to a blocker, hotspot, or planned slice.

GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.

| Signal | Decision role | Used now? | Why / why not | Action |
|---|---|---|---|---|
| p0_wave_plan | used_after_green | True | Planned-slice / watchlist input for after-green burn-down ordering. | Use for blast-radius / refactor / runtime-path / after-green planning. |
| mv_debt_concentration_hotspots | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_eval_coverage_by_path | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_exit_disposition_coverage | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_l2_phase_coverage | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_dependency_cone_risk | used_now | True | Structural MV studied (25 ranked rows on `cone_risk_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |
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
| mv_eval_coverage_by_path | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_exit_disposition_coverage | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_graph_chokepoint_bridges | Structural MV studied (25 ranked rows on `bridge_score`); a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now. | Use in current fix slice. |

Top structural risks (studied from the graph MVs — centrality / blast radius / reverse deps / cones):

| Rank | Scope | Graph signal | Centrality | Blast radius | Reverse dep | Executive read |
|---:|---|---|---|---|---|---|
| 1 | agentic_core/adg/extraction/static_scanner.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint, newly_introduced | 2.1882 | 84.0 | 84.0 | High structural risk — newly-introduced critical path (modified-area regression); overlaps an under-tested coverage hotspot. |
| 2 | agentic_core/base_agents/SovereignBaseAgent.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 0.81 | 175.93 | 91.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 3 | agentic_core/L2_execution/utils/write_gateway.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 0.7438 | 160.06 | 81.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 4 | agentic_core/L0_routing/config/__init__.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 2.5127 | 173.4 | 110.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 5 | agentic_core/runtime/contracts/lifecycle_trace_contract.py | centrality, reverse_dependency, blast_radius, dependency_cone | 87.7419 | 3239.46 | 1770.0 | High structural risk across 4 graph view(s); monitor unless it overlaps a blocker or hotspot. |

### 10. MECE Decision Gate and Work Queue

Decision gate — fixes report/runtime trust before ranking becomes authoritative:

| Gate | Why it matters | Evidence | Required before ranking |
|---|---|---|---|
| Repair graph/report consistency | The executive order is not decision-grade until graph and report agree. | 6 graph/report mismatch row(s) block decision-grade ordering. | Repair report consistency, then rerun ADG before treating the ranked work queue as authoritative. |

Fix now — ranked work items only:

| Priority | Move | Why it matters | Evidence | Next step |
|---|---|---|---|---|
| 1 | Stop core importing apps | Core importing apps breaks the core/app boundary and directly weakens provider-agnostic core. | ADG `07032026_0358`: `13_core_imports_apps` found 5 13_core_imports_apps. Breakout unavailable. | Move app-specific bindings behind an adapter or app-owned wiring surface; core should keep only generic contracts. |
| 2 | Fund mapped tests for agentic_core/L5_safety/reasoning/FileClassificationAgent.py | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | Add mapped tests/regression coverage for agentic_core. | Add mapped tests before touching this surface again. |
| 3 | Refactor high-blast-radius seam agentic_core/adg/extraction/static_scanner.py | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Refactor after the blocker and test exposure are explicit. |
| 4 | Burn down ratchet C3_silent_writes_ratchet | Accepted baseline debt should fall after red gates are clear. | 2,055 floor-row(s) remain on the ratchet gate. | Burn down the ratchet after the current red gates clear. |
| 5 | Refine/deprecate low-value ADG signal mv_capability_and_egress_gaps | Suppress or retire signals that do not affect decisions. | Empty or stale-looking signal; keep out of inline output until it proves decision value. | Deprecate only after the higher-risk surfaces are handled. |

### 11. Defer / Delete / Deprecate

### BCG Deletion Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Deletion status:** DELETION_CANDIDATES
- **Source report status:** PASS
- **Business read:** ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics.
- **Technical evidence:**
  - ADG source: artifacts/adg/adg_indexed_07032026_0358.sqlite (snapshot 07032026_0358)
  - Dead code candidates: 913
  - Dead imports: 913
  - Unresolved imports: 483
  - First-party low-confidence ratio: 1.56%
  - Inferred-symbol ratio: 10.15%
  - Cleanup candidates surfaced: 19
- **Priority rule:** Confirmed dead code first, then unresolved imports, then low-confidence noise, then low-value diagnostics.

Fix now:

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 13 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 2 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 12 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 3 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 11 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 4 | Triage unresolved imports | Unresolved imports are the biggest uncertainty and can hide real cleanup opportunities. | 483 unresolved imports; lead hotspot ADG::Module::tests/integration/retrieval_layers/test_bge_embedding_e2e.py (9). | Trace the top unresolved scope before deleting anything else. |
| 5 | Reduce low-confidence noise | Cleaner evidence makes later reviews faster and lowers the risk of deleting the wrong thing. | First-party low-confidence ratio = 1.56% and inferred-symbol ratio = 10.15%. | Lower the noise floor, then rerun the scan. |
| 6 | Deprecate low-value ADG signals | Remove empty or low-value diagnostics to cut review overhead once the evidence layer is stable. | 13 MV candidates and 6 unused artifacts surfaced by the report. | Deprecate only after higher-confidence cleanup is complete. |

Next step: Deprecate first, then delete after the evidence stays clean.

Current low-value cleanup candidates:

| Item | Type | Current value | Recommendation | Rationale |
|---|---|---|---|---|
| mv_actionable_surface_without_schema | mv | 785 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_specialization_overlap | mv | 3034 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_tool_ratio | mv | 15 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_authority_boundary_breaches | mv | 7 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_capability_and_egress_gaps | mv | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |
| mv_critical_path_segments | mv | 191 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_cross_cutting_witness_tiers | mv | 56 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_determinism_provenance_drift | mv | 6607 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_digest_reconciliation | mv | 6 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_exemptions_near_critical_paths | mv | 3175 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_gateway_bypass_paths | mv | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |
| mv_graph_scc_clusters | mv | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |

### 12. Honest Bottom Line

- Structurally healthy areas are those with CLEAR gates and no promoted GraphDB/testing gaps; do not spend executive time there.
- Actually blocking now: 1 FIX gates; inspect regression delta before declaring a platform crisis.
- Managed debt remains in TRACK ratchets and open non-ratchet rows; schedule it after green unless it overlaps current work.
- Runtime proof gaps are measurement gaps unless runtime artifacts show observed quality failure.
- Stop core importing apps
- Do not chase raw MV counts, guardian gross counts, or diagnostic reports without a decision role.
