## ADG Executive Brief

### BCG Executive Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Status:** PASS
- **Business read:** ADG is REPORT_INCONSISTENT: Repair report consistency first; the executive order of work is not trustworthy until graph and report agree.. Spend executive time on blockers and test gaps before accepted debt.
- **Technical evidence:**
  - ADG source: artifacts/adg/adg_indexed_06192026_0917.sqlite (snapshot 06192026_0917)
  - FIX gates: 5; TRACK gates: 18
  - Runtime proof is present and FAILING — treat as a quality failure to fix.
  - Testing is a control gap where agentic_core/L5_safety/reasoning/hierarchy_healer.py lacks regression coverage; fund tests with the relevant fix slice, not as a generic test campaign.
  - GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.
  - Action rows emitted: 7
- **Priority rule:** Fix blockers first, then close testing exposure, then reduce accepted debt.

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Clear layer-jump regression | Direct layer jumps increase coupling and make future changes harder to contain. | ADG `06192026_0917`: `B2_layer_skip_ratchet` found 895 direct dependency links, +4 above baseline 891. All +345 are direct dependency links from L5 -> L0, skipping L1/L2/L3/L4. Examples: 46 links from agentic_core/L5_safety/config/structure_blueprint/__init__.py to agentic_core/L0_routing/config/path_constants.py, 14 links from agentic_core/L5_safety/enforcement/mission_utils_enforcer.py to agentic_core/L0_routing/config/path_constants.py, and 12 links from agentic_core/L5_safety/reasoning/location_validator.py to agentic_core/L0_routing/config/path_constants.py. | Review the breakout: All +345 are direct dependency links from L5 -> L0, skipping L1/L2/L3/L4. Fix convenience coupling; introduce an adapter if the cross-layer call is intentional; grant an exemption only with owner, rationale, and retirement condition; re-baseline only with explicit architecture approval. |
| 2 | Stop L5 gateway bypass | Gateway bypass weakens control assurances and makes provider routing harder to defend. | ADG `06192026_0917`: `C2_l5_bypass_pview` found 2 provider/tool calls bypassing the L5 gateway. 2 provider/tool calls from L_APP bypass the L5 gateway. Examples: 2 rows from apps_rg/runtime/providers/external_provider.py:254. | Review the breakout: 2 provider/tool calls from L_APP bypass the L5 gateway. Fix convenience coupling; introduce an adapter if the cross-layer call is intentional; grant an exemption only with owner, rationale, and retirement condition; re-baseline only with explicit architecture approval. |
| 3 | Close untyped cross-layer seams | Untyped seams slow safe change and increase integration risk across callers. | ADG `06192026_0917`: `F1_untyped_seam_ratchet` found 1,026 cross-layer imports with empty type surfaces, +7 above baseline 1019. 345 cross-layer imports land on empty type surfaces from L5 to L0. Examples: 46 links from agentic_core/L5_safety/config/structure_blueprint/__init__.py to agentic_core/L0_routing/config/path_constants.py, 14 links from agentic_core/L5_safety/enforcement/mission_utils_enforcer.py to agentic_core/L0_routing/config/path_constants.py, and 12 links from agentic_core/L5_safety/reasoning/location_validator.py to agentic_core/L0_routing/config/path_constants.py. | Review the breakout: 345 cross-layer imports land on empty type surfaces from L5 to L0. Fix convenience coupling; introduce an adapter if the cross-layer call is intentional; grant an exemption only with owner, rationale, and retirement condition; re-baseline only with explicit architecture approval. |
| 4 | Fund mapped tests for agentic_core/L5_safety/reasoning/hierarchy_healer.py | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | Add mapped tests/regression coverage for agentic_core. | Add mapped tests before touching this surface again. |

Next step: Clear layer-jump regression

### 1. What ADG Is

ADG is the X-ray of the codebase. It maps code connections and lets the system ask health-check questions automatically. It turns 'is this codebase healthy?' from opinion into measured facts.

### 2. Patient Size

This patient has 12310 Python files: 7124 production files and 5186 test files. agentic_core contributes 2892 files; apps_* contributes 1431 files. Current snapshot/run ID: 06192026_0917.

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
| CLEAR | 25 | No action now. |
| TRACK | 18 | Known debt or advisory inventory; burn down after red gates. |
| FIX | 5 | Current blocker or regression requiring action before decision-grade green. |

| Red gate | Total records | Regression / new delta | Executive read | Next action |
|---|---:|---:|---|---|
| L2_lpg_drift_ratchet | 2 | 1 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 1 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| S4_unused_imports_ratchet | 10743 | 16 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +16 over baseline 10727: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| B2_layer_skip_ratchet | 895 | 4 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +4 over baseline 891: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| C2_l5_bypass_pview | 2 | 0 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| F1_untyped_seam_ratchet | 1026 | 7 | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +7 over baseline 1019: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| L2_lpg_drift_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +1 over baseline 1 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| S4_unused_imports_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +16 over baseline 10727: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| B2_layer_skip_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +4 over baseline 891: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| C2_l5_bypass_pview | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| F1_untyped_seam_ratchet | Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure. | Regression +7 over baseline 1019: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |

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

Testing is a control gap where agentic_core/L5_safety/reasoning/hierarchy_healer.py lacks regression coverage; fund tests with the relevant fix slice, not as a generic test campaign.

| Rank | Production scope | Current tests found | Missing test scope | Risk | Recommended investment | Trigger |
|---:|---|---|---|---|---|---|
| 1 | agentic_core/L5_safety/reasoning/hierarchy_healer.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 2 | agentic_core/L5_safety/reasoning/FileClassificationAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 3 | agentic_core/L5_safety/reasoning/root_hygiene_healer.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 4 | agentic_core/adg/extraction/static_scanner.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 5 | agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 6 | agentic_core/L5_safety/reasoning/location_validator.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 7 | agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 8 | agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 9 | agentic_core/L5_safety/reasoning/SystemArchitectAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |
| 10 | agentic_core/L5_safety/reasoning/CodeHealerAgent.py | unit: tests/system_learning/unit/test_ml_compatibility.py; unit: tests/system_learning/unit/test_ml_end_to_end_envelope.py; unit: tests/system_learning/unit/test_ml_write_envelope.py; unit: tests/system_learning/unit/test_runtime_antipattern_enforcement.py; unit: tests/system_learning/unit/test_runtime_state_digest.py; unit: tests/system_learning/unit/test_runtime_state_digest_advanced.py | regression | CRITICAL | Add mapped tests/regression coverage for agentic_core. | current action queue overlap |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| agentic_core/L5_safety/reasoning/hierarchy_healer.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |
| agentic_core/L5_safety/reasoning/FileClassificationAgent.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |
| agentic_core/L5_safety/reasoning/root_hygiene_healer.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |
| agentic_core/adg/extraction/static_scanner.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |
| agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py | Fix confidence improves when this scope has mapped tests. | Add mapped tests/regression coverage for agentic_core. |

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
| 1 | agentic_core/adg/extraction/static_scanner.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint, newly_introduced | 2.1529 | 84.0 | 84.0 | High structural risk — newly-introduced critical path (modified-area regression); overlaps an under-tested coverage hotspot. |
| 2 | agentic_core/base_agents/SovereignBaseAgent.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 0.8344 | 179.45 | 93.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 3 | agentic_core/L0_routing/config/__init__.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 2.5457 | 175.43 | 111.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 4 | agentic_core/L2_execution/utils/write_gateway.py | centrality, reverse_dependency, blast_radius, dependency_cone, chokepoint | 0.6071 | 125.07 | 64.0 | High structural risk — overlaps an under-tested coverage hotspot. |
| 5 | agentic_core/runtime/contracts/lifecycle_trace_contract.py | centrality, reverse_dependency, blast_radius, dependency_cone | 88.5987 | 3243.84 | 1771.0 | High structural risk across 4 graph view(s); monitor unless it overlaps a blocker or hotspot. |

### 10. Next Best Actions

| Priority | Move | Why it matters | Evidence | Next step |
|---|---|---|---|---|
| 1 | Clear layer-jump regression | Direct layer jumps increase coupling and make future changes harder to contain. | ADG `06192026_0917`: `B2_layer_skip_ratchet` found 895 direct dependency links, +4 above baseline 891. All +345 are direct dependency links from L5 -> L0, skipping L1/L2/L3/L4. Examples: 46 links from agentic_core/L5_safety/config/structure_blueprint/__init__.py to agentic_core/L0_routing/config/path_constants.py, 14 links from agentic_core/L5_safety/enforcement/mission_utils_enforcer.py to agentic_core/L0_routing/config/path_constants.py, and 12 links from agentic_core/L5_safety/reasoning/location_validator.py to agentic_core/L0_routing/config/path_constants.py. | Review the breakout: All +345 are direct dependency links from L5 -> L0, skipping L1/L2/L3/L4. Fix convenience coupling; introduce an adapter if the cross-layer call is intentional; grant an exemption only with owner, rationale, and retirement condition; re-baseline only with explicit architecture approval. |
| 2 | Stop L5 gateway bypass | Gateway bypass weakens control assurances and makes provider routing harder to defend. | ADG `06192026_0917`: `C2_l5_bypass_pview` found 2 provider/tool calls bypassing the L5 gateway. 2 provider/tool calls from L_APP bypass the L5 gateway. Examples: 2 rows from apps_rg/runtime/providers/external_provider.py:254. | Review the breakout: 2 provider/tool calls from L_APP bypass the L5 gateway. Fix convenience coupling; introduce an adapter if the cross-layer call is intentional; grant an exemption only with owner, rationale, and retirement condition; re-baseline only with explicit architecture approval. |
| 3 | Close untyped cross-layer seams | Untyped seams slow safe change and increase integration risk across callers. | ADG `06192026_0917`: `F1_untyped_seam_ratchet` found 1,026 cross-layer imports with empty type surfaces, +7 above baseline 1019. 345 cross-layer imports land on empty type surfaces from L5 to L0. Examples: 46 links from agentic_core/L5_safety/config/structure_blueprint/__init__.py to agentic_core/L0_routing/config/path_constants.py, 14 links from agentic_core/L5_safety/enforcement/mission_utils_enforcer.py to agentic_core/L0_routing/config/path_constants.py, and 12 links from agentic_core/L5_safety/reasoning/location_validator.py to agentic_core/L0_routing/config/path_constants.py. | Review the breakout: 345 cross-layer imports land on empty type surfaces from L5 to L0. Fix convenience coupling; introduce an adapter if the cross-layer call is intentional; grant an exemption only with owner, rationale, and retirement condition; re-baseline only with explicit architecture approval. |
| 4 | Fund mapped tests for agentic_core/L5_safety/reasoning/hierarchy_healer.py | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | Add mapped tests/regression coverage for agentic_core. | Add mapped tests before touching this surface again. |
| 5 | Refactor high-blast-radius seam agentic_core/adg/extraction/static_scanner.py | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path. | Refactor after the blocker and test exposure are explicit. |
| 6 | Burn down ratchet G_REACH_l0_reachability | Accepted baseline debt should fall after red gates are clear. | 2,788 floor-row(s) remain on the ratchet gate. | Burn down the ratchet after the current red gates clear. |
| 7 | Refine/deprecate low-value ADG signal mv_graph_scc_clusters | Suppress or retire signals that do not affect decisions. | Empty or stale-looking signal; keep out of inline output until it proves decision value. | Deprecate only after the higher-risk surfaces are handled. |

### 11. Defer / Delete / Deprecate

### BCG Deletion Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Status:** PASS
- **Business read:** ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics.
- **Technical evidence:**
  - ADG source: artifacts/adg/adg_indexed_06192026_0917.sqlite (snapshot 06192026_0917)
  - Dead code candidates: 0
  - Dead imports: 971
  - Unresolved imports: 486
  - First-party low-confidence ratio: 1.59%
  - Inferred-symbol ratio: 10.16%
  - Cleanup candidates surfaced: 18
- **Priority rule:** Confirmed dead code first, then unresolved imports, then low-confidence noise, then low-value diagnostics.

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 19 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 2 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 14 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 3 | Remove confirmed dead imports | This is high-confidence cleanup because the completed ADG resolved it as dead import traffic. | 13 resolved dead-import overlay row(s) point at this file. | Remove the imports, then rerun ADG to confirm the dead-import signal clears. |
| 4 | Triage unresolved imports | Unresolved imports are the biggest uncertainty and can hide real cleanup opportunities. | 486 unresolved imports; lead hotspot ADG::Module::tests/integration/retrieval_layers/test_bge_embedding_e2e.py (9). | Trace the top unresolved scope before deleting anything else. |
| 5 | Reduce low-confidence noise | Cleaner evidence makes later reviews faster and lowers the risk of deleting the wrong thing. | First-party low-confidence ratio = 1.59% and inferred-symbol ratio = 10.16%. | Lower the noise floor, then rerun the scan. |
| 6 | Deprecate low-value ADG signals | Remove empty or low-value diagnostics to cut review overhead once the evidence layer is stable. | 13 MV candidates and 5 unused artifacts surfaced by the report. | Deprecate only after higher-confidence cleanup is complete. |

Next step: Deprecate first, then delete after the evidence stays clean.

Current low-value cleanup candidates:

| Item | Type | Current value | Recommendation | Rationale |
|---|---|---|---|---|
| mv_actionable_surface_without_schema | mv | 768 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_specialization_overlap | mv | 3036 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_agent_tool_ratio | mv | 15 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_authority_boundary_breaches | mv | 7 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_capability_and_egress_gaps | mv | 1 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_critical_path_segments | mv | 196 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_cross_cutting_witness_tiers | mv | 56 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_determinism_provenance_drift | mv | 6559 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_digest_reconciliation | mv | 6 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_exemptions_near_critical_paths | mv | 3142 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_gateway_bypass_paths | mv | 2 rows; diagnostic_monitor | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_graph_scc_clusters | mv | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |

### 12. Honest Bottom Line

- Structurally healthy areas are those with CLEAR gates and no promoted GraphDB/testing gaps; do not spend executive time there.
- Actually blocking now: 5 FIX gates; inspect regression delta before declaring a platform crisis.
- Managed debt remains in TRACK ratchets and open non-ratchet rows; schedule it after green unless it overlaps current work.
- Runtime proof gaps are measurement gaps unless runtime artifacts show observed quality failure.
- Clear layer-jump regression
- Do not chase raw MV counts, guardian gross counts, or diagnostic reports without a decision role.
