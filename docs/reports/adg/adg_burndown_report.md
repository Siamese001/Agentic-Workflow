# ADG CI Burndown Report

- **Generated:** 2026-07-03T08:15:05+00:00
- **Gate-results source:** `artifacts\adg\adg_gate_results_20260703_081235.json`
- **Burndown source:** `artifacts\adg\adg_burndown_table_07032026_0358.json`
- **Snapshot timestamp:** 2026-07-03T08:12:35.117310+00:00
- **Total gates:** 49
- **Overall verdict:** **BLOCKED** (run halt — exit code)

### BCG Burndown Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **ADG verdict:** BLOCKED
- **Business read:** ADG is BLOCKED: fix the red gates before treating the run as green.
- **Technical evidence:**
  - Snapshot timestamp: 2026-07-03T08:12:35.117310+00:00
  - Total gates: 49
  - FIX gates: 1
  - Burn-down gates: 15
  - KPI/watchlist gates: 5
  - CLEAR gates: 28
  - block_fail=1; ratchet_regressed=0
- **Priority rule:** FIX gates first, then owned burn-down backlog, then KPI/watchlist trends outside the work queue.

Fix now:

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Fix 13_core_imports_apps | This gate is marked FIX, so the ADG run is not decision-grade green until it clears. | P0 block gate; rows=5; sub=block. | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |

Next step: BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block.
- **Action:** **FIX**=1 (address for green ADG) · **BURN**=15 (owned backlog) · **KPI**=5 (watchlist only) · **CLEAR**=28

## 1. ADG Status By Band

Operator summary from `adg_gate_results_*.json`.
Burn-down rows come from the BCG adapter priority queue; KPI/watchlist rows stay visible but do not imply cleanup work.

| Band | Status | Fix now | Burn-down backlog | KPI / watchlist | Read it as | Next move |
|------|:------:|--------:|-------------------|-----------------|------------|-----------|
| P0 | BLOCKED | 1 | 4 gates / 3,862 rows | 0 gates / 0 rows | red gates present | fix red gates first |
| P1 | PASS | 0 | 9 gates / 5,573 rows | 0 gates / 0 rows | green; tracked backlog | work ranked queue; do not treat as new failures |
| P2 | PASS | 0 | 2 gates / 1,974 rows | 1 gate / 105 rows | green; tracked backlog | work ranked queue; do not treat as new failures |
| P3 | PASS | 0 | 0 gates / 0 rows | 4 gates / 12,424 rows | green; KPI/watchlist only | watch trend; no burn-down action |

`Fix now` counts red gates. `Burn-down backlog` is accepted work. `KPI / watchlist` is report-only unless a plan gives it an owner and target.

## 2. ADG CI Gates

One row per registered gate.

- **Section** — **FIX** = address now · **BURN** = owned backlog · **KPI** = watchlist only · **CLEAR** = zero rows.
- **Sub** — detail (block / regr / floor / inventory / …); see glossary.
- **Allowed Floor** — zero-tolerance for block gates, baseline for ratchets, advisory/inventory otherwise.
- **Rows** — gate-specific `violation_count`; meaning depends on Action/Sub.
- **Signal** — what Rows count + short Sub note.
- **Next Best Action** — concrete action for this gate (fix / re-baseline / defer / none).

| Gate ID | CI Band | Enforcement | Section | Sub | Rows | Allowed Floor | Signal | Next Best Action |
|---------|:-------:|-------------|:-------:|:---:|---------:|---------------|--------|------------------|
| `13_core_imports_apps` | P0 | block | FIX | block | 5 | 0 | Counts: Core Imports Apps (auto-derived from gate_class) Sub: Run blocked (exit 1). | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| `G_REACH_l0_reachability` | P0 | ratchet | BURN | floor | 1495 | 1495 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: 1495 at floor (baseline 1495); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | BURN | floor | 1604 | 1604 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: 1604 at floor (baseline 1604); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `3_write_sovereignty` | P0 | block | BURN | inventory | 762 | warn inventory | Counts: Non-UWG durable write paths in mv_write_sovereignty_paths (inventory). Sub: 762 warn inventory; not halt-tier. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `J1_canonical_pipeline_wiring` | P0 | block | BURN | inventory | 1 | warn inventory | Counts: Declared canonical_pipelines.yaml steps missing required call wiring. Sub: 1 subprocess warn. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `10_infra_wiring` | P0 | block | CLEAR | — | 0 | 0 | Counts: Infra wiring defects (canonical pipeline / spine reachability). Sub: No rows. | None — gate clean (zero rows). |
| `1_critical_path_integrity` | P0 | block | CLEAR | — | 0 | 0 | Counts: Broken or missing links on declared critical execution paths (L0→sink). Sub: No rows. | None — gate clean (zero rows). |
| `2_authority_boundary` | P0 | block | CLEAR | — | 0 | 0 | Counts: Calls that cross layer authority without UWG/spine sanction. Sub: No rows. | None — gate clean (zero rows). |
| `4_capability_egress` | P0 | block | CLEAR | — | 0 | 0 | Counts: Outbound provider/SDK calls not leaving through sanctioned adapters. Sub: No rows. | None — gate clean (zero rows). |
| `5_text_to_action` | P0 | block | CLEAR | — | 0 | 0 | Counts: User text reaching action-class tools without prompt-governance gating. Sub: No rows. | None — gate clean (zero rows). |
| `6_determinism_provenance` | P0 | block | CLEAR | — | 0 | 0 | Counts: Trace roots missing determinism digest or replay key emission. Sub: No rows. | None — gate clean (zero rows). |
| `9_executor_theater` | P0 | block | CLEAR | — | 0 | 0 | Counts: Executor-theater signals: import-only or stub execution patterns. Sub: No rows. | None — gate clean (zero rows). |
| `C1_uwg_bypass_pview` | P0 | block | CLEAR | — | 0 | 0 | Counts: Any row in UWG-bypass materialized view (zero tolerance block). Sub: No rows. | None — gate clean (zero rows). |
| `C2_l5_bypass_pview` | P0 | block | CLEAR | — | 0 | 0 | Counts: Provider/tool calls skipping L5 gateway (materialized view). Sub: No rows. | None — gate clean (zero rows). |
| `L2_lpg_drift_ratchet` | P0 | ratchet | CLEAR | — | 0 | 0 | Counts: Illegal or drifted imports touching L_PG boundary. Sub: No rows. | None — gate clean (zero rows). |
| `W5_waiver_expiry` | P0 | block | CLEAR | — | 0 | 0 | Counts: Expired wiring-CI waiver entries in config. Sub: No rows. | None — gate clean (zero rows). |
| `B2_layer_skip_ratchet` | P1 | ratchet | BURN | floor | 862 | 862 | Counts: Import edges that skip more than one layer ordinal (layer-hop). Sub: 862 at floor (baseline 862); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C3_silent_writes_ratchet` | P1 | ratchet | BURN | floor | 2055 | 2055 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: 2055 at floor (baseline 2055); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C4_policy_without_audit_ratchet` | P1 | ratchet | BURN | floor | 1 | 1 | Counts: controls_flow edges without paired audit/telemetry emission. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `E1_trace_stub_module` | P1 | ratchet | BURN | floor | 982 | 982 | Counts: Modules with high test:production import ratio (trace-theater stub pattern). Sub: 982 at floor (baseline 982); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I1_exit_disposition_ratchet` | P1 | ratchet | BURN | floor | 695 | 695 | Counts: Terminal exit paths not covered in mv_exit_disposition_coverage. Sub: 695 at floor (baseline 695); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `M_taint_actionable_ratchet` | P1 | ratchet | BURN | floor | 683 | 683 | Counts: Actionable taint surfaces without output schema binding. Sub: 683 at floor (baseline 683); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `N_guardrail_separation_ratchet` | P1 | ratchet | BURN | floor | 88 | 88 | Counts: L5 guardrail and L3 core-response sharing same write target. Sub: 88 at floor (baseline 88); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `O_tool_call_parity_ratchet` | P1 | ratchet | BURN | floor | 206 | 206 | Counts: Tool invocations missing observability receipt (Anthropic parity pattern). Sub: 206 at floor (baseline 206); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `P_structured_output_ratchet` | P1 | ratchet | BURN | floor | 1 | 1 | Counts: generates_prompt at scale without structured output schema. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `11_architecture_witness` | P1 | block | CLEAR | — | 0 | 0 | Counts: Architecture witness Class A/B absence or live-plane write violations. Sub: No rows. | None — gate clean (zero rows). |
| `12_prompt_assembly_wiring` | P1 | block | CLEAR | — | 0 | 0 | Counts: Prompt-assembly subgraph disconnected from runtime spine. Sub: No rows. | None — gate clean (zero rows). |
| `7_lifecycle_coverage` | P1 | ratchet | CLEAR | — | 0 | unseeded | Counts: Lifecycle gaps: resources opened without matching close/cleanup. Sub: No rows. | None — gate clean (zero rows). |
| `8_trace_replay_eval` | P1 | ratchet | CLEAR | — | 0 | unseeded | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: No rows. | None — gate clean (zero rows). |
| `G2_seam_test_export_coherence` | P1 | block | CLEAR | — | 0 | 0 | Counts: Production seam symbols exported in tests but not in package __all__/exports. Sub: No rows. | None — gate clean (zero rows). |
| `G_ISLAND_connected_components` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Non-giant connected components on undirected import graph. Sub: No rows. | None — gate clean (zero rows). |
| `G_WATCHLIST_DELTA_hotspot_regressions` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Graph watchlist items newly FAIL/WARN vs prior run. Sub: No rows. | None — gate clean (zero rows). |
| `H1_new_orphans_delta_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Modules newly fan_in=0 vs prior snapshot (new orphans). Sub: No rows. | None — gate clean (zero rows). |
| `H2_fanin_collapse_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Hotspot modules with >30% fan_in drop vs prior snapshot. Sub: No rows. | None — gate clean (zero rows). |
| `F1_untyped_seam_ratchet` | P2 | ratchet | BURN | floor | 980 | 980 | Counts: Cross-layer imports where target has empty type_surface. Sub: 980 at floor (baseline 980); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | BURN | floor | 994 | 994 | Counts: State mutations not consumed by replay surface (gap_flag=1). Sub: 994 at floor (baseline 994); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D2_role_duplication_warn` | P2 | warn | KPI | advis | 105 | advisory | Counts: Role-suffix clusters (_reranker, _planner, …) with fan_in=0 members (advisory). Sub: 105 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `A3_dead_public_symbol_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Public symbols with zero importers (dead surface). Sub: No rows. | None — gate clean (zero rows). |
| `C5_unresolved_callsites_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: resolves_callsite edges with NULL destination (unresolved callee). Sub: No rows. | None — gate clean (zero rows). |
| `F2_broken_contract_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Import targets publishing zero exports edges (contract drift). Sub: No rows. | None — gate clean (zero rows). |
| `H4_mv_staleness_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Total edge count delta >5% vs prior snapshot (graph drift). Sub: No rows. | None — gate clean (zero rows). |
| `M1_module_loc_ratchet` | P3 | ratchet | KPI | floor | 467 | 467 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: 467 at floor (baseline 467); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | KPI | floor | 1177 | 1177 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: 1177 at floor (baseline 1177); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `S4_unused_imports_ratchet` | P3 | ratchet | KPI | floor | 10777 | 10777 | Counts: Unused import edges in production modules. Sub: 10777 at floor (baseline 10777); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D1_layer_doc_binding` | P3 | warn | KPI | advis | 3 | advisory | Counts: Layer folders missing or mismatched LAYER.md binding (advisory). Sub: 3 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `E3_trace_theater_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Emit-symbol density per layer vs imports (KPI advisory). Sub: No rows. | None — gate clean (zero rows). |
| `F3_missing_adapter_warn` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Protocol/ABC/Interface with zero implements edges (advisory). Sub: No rows. | None — gate clean (zero rows). |
| `H3_ap_velocity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Antipattern edge density per 1k LOC (KPI advisory). Sub: No rows. | None — gate clean (zero rows). |
| `K1_churn_complexity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: High churn×complexity files (KPI advisory, jsonl sink). Sub: No rows. | None — gate clean (zero rows). |

### Fix now (Verdict FIX)

| Gate ID | Sub | Rows |
|---------|:---:|---------:|
| `13_core_imports_apps` | block | 5 |

### Burn down later (owned backlog — CI OK)

| Gate ID | Sub | Rows |
|---------|:---:|---------:|
| `C3_silent_writes_ratchet` | floor | 2055 |
| `S2_uwg_bypass_ratchet` | floor | 1604 |
| `G_REACH_l0_reachability` | floor | 1495 |
| `I2_replay_surface_gaps_ratchet` | floor | 994 |
| `E1_trace_stub_module` | floor | 982 |
| `F1_untyped_seam_ratchet` | floor | 980 |
| `B2_layer_skip_ratchet` | floor | 862 |
| `3_write_sovereignty` | inventory | 762 |
| `I1_exit_disposition_ratchet` | floor | 695 |
| `M_taint_actionable_ratchet` | floor | 683 |
| `O_tool_call_parity_ratchet` | floor | 206 |
| `N_guardrail_separation_ratchet` | floor | 88 |
| `C4_policy_without_audit_ratchet` | floor | 1 |
| `J1_canonical_pipeline_wiring` | inventory | 1 |
| `P_structured_output_ratchet` | floor | 1 |

## 3. KPI / Watchlist Signals

These rows are visible for trend awareness, but they are not burn-down work unless a plan gives them an owner, target, and retirement condition.

| Gate ID | Band | Rows | Why it is separate | Next step |
|---------|:----:|-----:|--------------------|-----------|
| `S4_unused_imports_ratchet` | P3 | 10777 | KPI/watchlist signal, not an owned burn-down item. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | 1177 | KPI/watchlist signal, not an owned burn-down item. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `M1_module_loc_ratchet` | P3 | 467 | KPI/watchlist signal, not an owned burn-down item. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D2_role_duplication_warn` | P2 | 105 | KPI/watchlist signal, not an owned burn-down item. | Advisory KPI: watch the trend; no action required to pass CI. |
| `D1_layer_doc_binding` | P3 | 3 | KPI/watchlist signal, not an owned burn-down item. | Advisory KPI: watch the trend; no action required to pass CI. |

## 4. Severity Inventory Burndown

Counts come from the canonical `adg_burndown_table.json` (schema 2.2).
This is raw MV defect inventory by severity/source band; it is not one row per CI gate.
Use this section for guardian math, not the status table above, and not the BCG foundation-blocker KPI.
`gross` = raw violations found. `guardian` = guardian-exempted (still counted).
`net` = audit net (`gross - guardian`). It is severity inventory, not live gate drivers and not foundation blockers.
A P0 audit net value can be nonzero while BCG foundation blockers are zero; the BCG KPI scorecard reconciles that split.

| Severity Band | Label | Gross | Guardian | Audit net | Diff vs prev |
|---------------|-------|------:|---------:|----:|-------------:|
| P0 | layer_violations | 37 | 33 | 4 | +33 |
| P1 | anti_patterns_high | 1146 | 1143 | 3 | +1143 |
| P2 | anti_patterns_medium | 745 | 716 | 29 | +716 |
| P3 | style_warnings | 19235 | 87 | 19148 | +87 |

_p0_clean = False • p1_no_ratchet = True • counting_mode = `violations_plus_exempted_edge_inference`_

## Verdict glossary

Scan **Verdict** first (3 values). Use **Sub** only when you need detail.

| Verdict | You need to… | Sub (detail) |
|---------|--------------|--------------|
| **FIX** | Fix for green ADG | block, regr, seed |
| **TRACK** | Plan hygiene; CI OK | floor, inventory, advis |
| **CLEAR** | Nothing | — |

| Sub | Parent | Meaning |
|-----|--------|---------|
| block | FIX | Block policy halted the run (exit 1). |
| regr | FIX | Ratchet count rose above baseline (+N new). |
| seed | FIX | Ratchet baseline file missing. |
| floor | TRACK | Ratchet at absorbed floor (≤ baseline); large count OK if no +N. |
| inventory | TRACK | Block warn-tier inventory (e.g. write paths); not baseline math. |
| advis | TRACK | Warn enforcement only; never blocks. |

**floor vs inventory (both TRACK):** floor = ratchet ≤ baseline (e.g. G_REACH 2792). inventory = block warn backlog (e.g. write sovereignty 848). Check **Enf**: ratchet → floor; block → inventory.

## 5. Aggregate Verdicts

| Verdict | Count | Meaning |
|---------|------:|---------|
| block_pass | 14 | Block-class gates that did not halt the run (exit 0). Rows may be non-zero. |
| block_fail | 1 | Block-class gates that halted the run — clear the gate blocking condition. |
| ratchet_pass | 27 | Ratchet-class gates within their baseline ceiling. |
| ratchet_regressed | 0 | Ratchet-class gates with NEW rows beyond baseline. |
| ratchet_seed_missing | 0 | Ratchet-class gates without a baseline seed (first run). |
| warn | 6 | Advisory-class gates (do not gate the run). |

### Per-gate verdict rollup (this report)

| Verdict | Gates | Meaning |
|---------|------:|---------|
| FIX | 1 | Address before treating ADG as green (gate blocked or ratchet regressed). |
| TRACK | 20 | CI passed this gate; rows are backlog — plan hygiene, not a halt. |
| CLEAR | 28 | Zero rows; nothing to do on this gate. |

## 6. Fix now (detail)

| Gate | Band | Enf | Sub | Rows | Signal |
|------|:----:|:---:|:---:|---------:|--------|
| `13_core_imports_apps` | P0 | block | block | 5 | Counts: Core Imports Apps (auto-derived from gate_class) Sub: Run blocked (exit 1). |

---
## Next action

- **Queue:** `artifacts\adg\adg_action_queue_07032026_0358.json`
- **emit_status:** `ok`
- **degraded:** `False`
- **summary:** FIX=1 · TRACK=20 · actions_emitted=10

| Rank | Lane | Kind | Target | ordering_reason | Signal |
|-----:|------|------|--------|-----------------|--------|
| 1 | FIX | fix_gate | `13_core_imports_apps` | fix_block_p0_violations_asc | Counts: Core Imports Apps (auto-derived from gate_class) Sub: Run blocked (exit 1). |
| 2 | P0_WAVE | p0_wave_file | `agentic_core/L1_cognition/__init__.py` | p0_wave_top_files_priority | P0 wave file; issues=1 |
| 3 | P0_WAVE | p0_wave_file | `agentic_core/L1_cognition/apps_research_c0_binding.py` | p0_wave_top_files_priority | P0 wave file; issues=1 |
| 4 | P0_WAVE | p0_wave_file | `agentic_core/L1_cognition/apps_research_l1_binding.py` | p0_wave_top_files_priority | P0 wave file; issues=1 |
| 5 | GRAPHDB | test_hotspot_gap | `agentic_core/L5_safety/contracts/registry.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (absent); critical... |

CLI: `python tools/reports/adg_action_queue.py --latest --top 10 --format markdown`

---
Report renderer: `tools/reports/adg_burndown_report.py`. Re-run with `python tools/reports/adg_burndown_report.py --out artifacts/adg/adg_burndown_report.md`.
