# ADG CI Burndown Report

- **Generated:** 2026-06-28T23:55:12+00:00
- **Gate-results source:** `artifacts\adg\adg_gate_results_20260628_235116.json`
- **Burndown source:** `artifacts\adg\adg_burndown_table.json`
- **Snapshot timestamp:** 2026-06-28T23:51:16.197008+00:00
- **Total gates:** 49
- **Overall verdict:** **BLOCKED** (run halt — exit code)

### BCG Burndown Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **ADG verdict:** BLOCKED
- **Business read:** ADG is BLOCKED: fix the red gates before treating the run as green.
- **Technical evidence:**
  - Snapshot timestamp: 2026-06-28T23:51:16.197008+00:00
  - Total gates: 49
  - FIX gates: 10
  - Burn-down gates: 11
  - KPI/watchlist gates: 2
  - CLEAR gates: 26
  - block_fail=2; ratchet_regressed=8
- **Priority rule:** FIX gates first, then owned burn-down backlog, then KPI/watchlist trends outside the work queue.

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Fix S4_unused_imports_ratchet | This gate is marked FIX, so the ADG run is not decision-grade green until it clears. | P3 ratchet gate; rows=10772; sub=regr. | Regression +22 over baseline 10750: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| 2 | Fix C3_silent_writes_ratchet | This gate is marked FIX, so the ADG run is not decision-grade green until it clears. | P1 ratchet gate; rows=2050; sub=regr. | Regression +16 over baseline 2034: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| 3 | Fix S2_uwg_bypass_ratchet | This gate is marked FIX, so the ADG run is not decision-grade green until it clears. | P0 ratchet gate; rows=1601; sub=regr. | Regression +30 over baseline 1571 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| 4 | Fix Q2_cyclomatic_complexity_ratchet | This gate is marked FIX, so the ADG run is not decision-grade green until it clears. | P3 ratchet gate; rows=1168; sub=regr. | Regression +20 over baseline 1148: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |

Next step: Regression +22 over baseline 10750: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt.
- **Action:** **FIX**=10 (address for green ADG) · **BURN**=11 (owned backlog) · **KPI**=2 (watchlist only) · **CLEAR**=26

## 1. ADG Status By Band

Operator summary from `adg_gate_results_*.json`.
Burn-down rows come from the BCG adapter priority queue; KPI/watchlist rows stay visible but do not imply cleanup work.

| Band | Status | Fix now | Burn-down backlog | KPI / watchlist | Read it as | Next move |
|------|:------:|--------:|-------------------|-----------------|------------|-----------|
| P0 | BLOCKED | 3 | 3 gates / 2,252 rows | 0 gates / 0 rows | red gates present | fix red gates first |
| P1 | BLOCKED | 3 | 7 gates / 2,834 rows | 0 gates / 0 rows | red gates present | fix red gates first |
| P2 | BLOCKED | 1 | 1 gate / 979 rows | 1 gate / 105 rows | red gates present | fix red gates first |
| P3 | BLOCKED | 3 | 0 gates / 0 rows | 1 gate / 3 rows | red gates present | fix red gates first |

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
| `10_infra_wiring` | P0 | block | FIX | block | 3 | 0 | Counts: Infra wiring defects (canonical pipeline / spine reachability). Sub: Run blocked (exit 1). | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| `13_core_imports_apps` | P0 | block | FIX | block | 35 | 0 | Counts: Core Imports Apps (auto-derived from gate_class) Sub: Run blocked (exit 1). | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | FIX | regr | 1601 | 1571 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: +30 vs baseline 1571. | Regression +30 over baseline 1571 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| `G_REACH_l0_reachability` | P0 | ratchet | BURN | floor | 1495 | 1495 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: 1495 at floor (baseline 1495); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `3_write_sovereignty` | P0 | block | BURN | inventory | 756 | warn inventory | Counts: Non-UWG durable write paths in mv_write_sovereignty_paths (inventory). Sub: 756 warn inventory; not halt-tier. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `J1_canonical_pipeline_wiring` | P0 | block | BURN | inventory | 1 | warn inventory | Counts: Declared canonical_pipelines.yaml steps missing required call wiring. Sub: 1 subprocess warn. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
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
| `8_trace_replay_eval` | P1 | ratchet | FIX | regr | 4 | unseeded | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: Above ratchet baseline. | Regression +N over baseline None: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `C3_silent_writes_ratchet` | P1 | ratchet | FIX | regr | 2050 | 2034 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: +16 vs baseline 2034. | Regression +16 over baseline 2034: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `M_taint_actionable_ratchet` | P1 | ratchet | FIX | regr | 681 | 676 | Counts: Actionable taint surfaces without output schema binding. Sub: +5 vs baseline 676. | Regression +5 over baseline 676: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `B2_layer_skip_ratchet` | P1 | ratchet | BURN | floor | 862 | 862 | Counts: Import edges that skip more than one layer ordinal (layer-hop). Sub: 862 at floor (baseline 862); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C4_policy_without_audit_ratchet` | P1 | ratchet | BURN | floor | 1 | 1 | Counts: controls_flow edges without paired audit/telemetry emission. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `E1_trace_stub_module` | P1 | ratchet | BURN | floor | 982 | 982 | Counts: Modules with high test:production import ratio (trace-theater stub pattern). Sub: 982 at floor (baseline 982); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I1_exit_disposition_ratchet` | P1 | ratchet | BURN | floor | 695 | 695 | Counts: Terminal exit paths not covered in mv_exit_disposition_coverage. Sub: 695 at floor (baseline 695); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `N_guardrail_separation_ratchet` | P1 | ratchet | BURN | floor | 88 | 88 | Counts: L5 guardrail and L3 core-response sharing same write target. Sub: 88 at floor (baseline 88); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `O_tool_call_parity_ratchet` | P1 | ratchet | BURN | floor | 205 | 205 | Counts: Tool invocations missing observability receipt (Anthropic parity pattern). Sub: 205 at floor (baseline 205); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `P_structured_output_ratchet` | P1 | ratchet | BURN | floor | 1 | 1 | Counts: generates_prompt at scale without structured output schema. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `11_architecture_witness` | P1 | block | CLEAR | — | 0 | 0 | Counts: Architecture witness Class A/B absence or live-plane write violations. Sub: No rows. | None — gate clean (zero rows). |
| `12_prompt_assembly_wiring` | P1 | block | CLEAR | — | 0 | 0 | Counts: Prompt-assembly subgraph disconnected from runtime spine. Sub: No rows. | None — gate clean (zero rows). |
| `7_lifecycle_coverage` | P1 | ratchet | CLEAR | — | 0 | unseeded | Counts: Lifecycle gaps: resources opened without matching close/cleanup. Sub: No rows. | None — gate clean (zero rows). |
| `G2_seam_test_export_coherence` | P1 | block | CLEAR | — | 0 | 0 | Counts: Production seam symbols exported in tests but not in package __all__/exports. Sub: No rows. | None — gate clean (zero rows). |
| `G_ISLAND_connected_components` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Non-giant connected components on undirected import graph. Sub: No rows. | None — gate clean (zero rows). |
| `G_WATCHLIST_DELTA_hotspot_regressions` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Graph watchlist items newly FAIL/WARN vs prior run. Sub: No rows. | None — gate clean (zero rows). |
| `H1_new_orphans_delta_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Modules newly fan_in=0 vs prior snapshot (new orphans). Sub: No rows. | None — gate clean (zero rows). |
| `H2_fanin_collapse_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Hotspot modules with >30% fan_in drop vs prior snapshot. Sub: No rows. | None — gate clean (zero rows). |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | FIX | regr | 993 | 989 | Counts: State mutations not consumed by replay surface (gap_flag=1). Sub: +4 vs baseline 989. | Regression +4 over baseline 989: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `F1_untyped_seam_ratchet` | P2 | ratchet | BURN | floor | 979 | 979 | Counts: Cross-layer imports where target has empty type_surface. Sub: 979 at floor (baseline 979); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D2_role_duplication_warn` | P2 | warn | KPI | advis | 105 | advisory | Counts: Role-suffix clusters (_reranker, _planner, …) with fan_in=0 members (advisory). Sub: 105 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `A3_dead_public_symbol_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Public symbols with zero importers (dead surface). Sub: No rows. | None — gate clean (zero rows). |
| `C5_unresolved_callsites_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: resolves_callsite edges with NULL destination (unresolved callee). Sub: No rows. | None — gate clean (zero rows). |
| `F2_broken_contract_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Import targets publishing zero exports edges (contract drift). Sub: No rows. | None — gate clean (zero rows). |
| `H4_mv_staleness_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Total edge count delta >5% vs prior snapshot (graph drift). Sub: No rows. | None — gate clean (zero rows). |
| `M1_module_loc_ratchet` | P3 | ratchet | FIX | regr | 466 | 458 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: +8 vs baseline 458. | Regression +8 over baseline 458: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | FIX | regr | 1168 | 1148 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: +20 vs baseline 1148. | Regression +20 over baseline 1148: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `S4_unused_imports_ratchet` | P3 | ratchet | FIX | regr | 10772 | 10750 | Counts: Unused import edges in production modules. Sub: +22 vs baseline 10750. | Regression +22 over baseline 10750: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `D1_layer_doc_binding` | P3 | warn | KPI | advis | 3 | advisory | Counts: Layer folders missing or mismatched LAYER.md binding (advisory). Sub: 3 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `E3_trace_theater_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Emit-symbol density per layer vs imports (KPI advisory). Sub: No rows. | None — gate clean (zero rows). |
| `F3_missing_adapter_warn` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Protocol/ABC/Interface with zero implements edges (advisory). Sub: No rows. | None — gate clean (zero rows). |
| `H3_ap_velocity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Antipattern edge density per 1k LOC (KPI advisory). Sub: No rows. | None — gate clean (zero rows). |
| `K1_churn_complexity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: High churn×complexity files (KPI advisory, jsonl sink). Sub: No rows. | None — gate clean (zero rows). |

### Fix now (Verdict FIX)

| Gate ID | Sub | Rows |
|---------|:---:|---------:|
| `S4_unused_imports_ratchet` | regr | 10772 |
| `C3_silent_writes_ratchet` | regr | 2050 |
| `S2_uwg_bypass_ratchet` | regr | 1601 |
| `Q2_cyclomatic_complexity_ratchet` | regr | 1168 |
| `I2_replay_surface_gaps_ratchet` | regr | 993 |
| `M_taint_actionable_ratchet` | regr | 681 |
| `M1_module_loc_ratchet` | regr | 466 |
| `13_core_imports_apps` | block | 35 |
| `8_trace_replay_eval` | regr | 4 |
| `10_infra_wiring` | block | 3 |

### Burn down later (owned backlog — CI OK)

| Gate ID | Sub | Rows |
|---------|:---:|---------:|
| `G_REACH_l0_reachability` | floor | 1495 |
| `E1_trace_stub_module` | floor | 982 |
| `F1_untyped_seam_ratchet` | floor | 979 |
| `B2_layer_skip_ratchet` | floor | 862 |
| `3_write_sovereignty` | inventory | 756 |
| `I1_exit_disposition_ratchet` | floor | 695 |
| `O_tool_call_parity_ratchet` | floor | 205 |
| `N_guardrail_separation_ratchet` | floor | 88 |
| `C4_policy_without_audit_ratchet` | floor | 1 |
| `J1_canonical_pipeline_wiring` | inventory | 1 |
| `P_structured_output_ratchet` | floor | 1 |

## 3. KPI / Watchlist Signals

These rows are visible for trend awareness, but they are not burn-down work unless a plan gives them an owner, target, and retirement condition.

| Gate ID | Band | Rows | Why it is separate | Next step |
|---------|:----:|-----:|--------------------|-----------|
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
| P0 | layer_violations | 43 | 40 | 3 | +40 |
| P1 | anti_patterns_high | 1150 | 1144 | 6 | +1144 |
| P2 | anti_patterns_medium | 743 | 716 | 27 | +716 |
| P3 | style_warnings | 19151 | 87 | 19064 | +87 |

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
| block_pass | 13 | Block-class gates that did not halt the run (exit 0). Rows may be non-zero. |
| block_fail | 2 | Block-class gates that halted the run — clear the gate blocking condition. |
| ratchet_pass | 19 | Ratchet-class gates within their baseline ceiling. |
| ratchet_regressed | 8 | Ratchet-class gates with NEW rows beyond baseline. |
| ratchet_seed_missing | 0 | Ratchet-class gates without a baseline seed (first run). |
| warn | 6 | Advisory-class gates (do not gate the run). |

### Per-gate verdict rollup (this report)

| Verdict | Gates | Meaning |
|---------|------:|---------|
| FIX | 10 | Address before treating ADG as green (gate blocked or ratchet regressed). |
| TRACK | 13 | CI passed this gate; rows are backlog — plan hygiene, not a halt. |
| CLEAR | 26 | Zero rows; nothing to do on this gate. |

## 6. Fix now (detail)

| Gate | Band | Enf | Sub | Rows | Signal |
|------|:----:|:---:|:---:|---------:|--------|
| `S4_unused_imports_ratchet` | P3 | ratchet | regr | 10772 | Counts: Unused import edges in production modules. Sub: +22 vs baseline 10750. |
| `C3_silent_writes_ratchet` | P1 | ratchet | regr | 2050 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: +16 vs baseline 2034. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | regr | 1601 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: +30 vs baseline 1571. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | regr | 1168 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: +20 vs baseline 1148. |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | regr | 993 | Counts: State mutations not consumed by replay surface (gap_flag=1). Sub: +4 vs baseline 989. |
| `M_taint_actionable_ratchet` | P1 | ratchet | regr | 681 | Counts: Actionable taint surfaces without output schema binding. Sub: +5 vs baseline 676. |
| `M1_module_loc_ratchet` | P3 | ratchet | regr | 466 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: +8 vs baseline 458. |
| `13_core_imports_apps` | P0 | block | block | 35 | Counts: Core Imports Apps (auto-derived from gate_class) Sub: Run blocked (exit 1). |
| `8_trace_replay_eval` | P1 | ratchet | regr | 4 | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: Above ratchet baseline. |
| `10_infra_wiring` | P0 | block | block | 3 | Counts: Infra wiring defects (canonical pipeline / spine reachability). Sub: Run blocked (exit 1). |

---
## Next action

- **Queue:** `artifacts\adg\adg_action_queue_06282026_1945.json`
- **emit_status:** `ok`
- **degraded:** `False`
- **summary:** FIX=10 · TRACK=13 · actions_emitted=10

| Rank | Lane | Kind | Target | ordering_reason | Signal |
|-----:|------|------|--------|-----------------|--------|
| 1 | FIX | fix_gate | `10_infra_wiring` | fix_block_p0_violations_asc | Counts: Infra wiring defects (canonical pipeline / spine reachability). Sub: Run blocked (exit 1). |
| 2 | FIX | fix_gate | `13_core_imports_apps` | fix_block_p0_violations_asc | Counts: Core Imports Apps (auto-derived from gate_class) Sub: Run blocked (exit 1). |
| 3 | FIX | fix_gate | `S2_uwg_bypass_ratchet` | fix_regr_p0_delta_asc | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: +30 vs baseline 1571. |
| 4 | FIX | fix_gate | `8_trace_replay_eval` | fix_regr_p1_delta_asc | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: Above ratchet baseline. |
| 5 | FIX | fix_gate | `M_taint_actionable_ratchet` | fix_regr_p1_delta_asc | Counts: Actionable taint surfaces without output schema binding. Sub: +5 vs baseline 676. |

CLI: `python tools/reports/adg_action_queue.py --latest --top 10 --format markdown`

---
Report renderer: `tools/reports/adg_burndown_report.py`. Re-run with `python tools/reports/adg_burndown_report.py --out artifacts/adg/adg_burndown_report.md`.
