# ADG CI Burndown Report

- **Generated:** 2026-06-10T18:25:17+00:00
- **Gate-results source:** `artifacts\adg\adg_gate_results_20260610_182352.json`
- **Burndown source:** `artifacts\adg\adg_burndown_table.json`
- **Snapshot timestamp:** 2026-06-10T18:23:52.025202+00:00
- **Total gates:** 48
- **Overall verdict:** **BLOCKED** (run halt — exit code)
- **Action:** **FIX**=12 (address for green ADG) · **TRACK**=11 (CI OK, backlog) · **CLEAR**=25

## 1. Burndown by Severity Band

Counts come from the canonical `adg_burndown_table.json` (schema 2.2).
`gross` = raw violations found. `guardian` = guardian-exempted (still counted).
`net` = `gross - guardian`. `diff` = delta vs prior snapshot baseline.

| Band | Label | Gross | Guardian | Net | Diff vs prev |
|------|-------|------:|---------:|----:|-------------:|
| P0 | layer_violations | 42 | 42 | 0 | +42 |
| P1 | anti_patterns_high | 1197 | 1193 | 4 | +1193 |
| P2 | anti_patterns_medium | 734 | 717 | 17 | +717 |
| P3 | style_warnings | 20012 | 93 | 19919 | +93 |

_p0_clean = True • p1_no_ratchet = True • counting_mode = `violations_plus_exempted_edge_inference`_

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

## 3. All CI Gates

One row per registered gate.

- **Verdict** — **FIX** = address now · **TRACK** = backlog, CI OK · **CLEAR** = zero findings.
- **Sub** — detail (block / regr / floor / inventory / …); see glossary.
- **Signal** — what Findings count + short Sub note.
- **Recommended Next Step** — concrete action for this gate (fix / re-baseline / defer / none).

| Gate ID | Band | Enf | Verdict | Sub | Findings | Signal | Recommended Next Step |
|---------|:----:|:---:|:-------:|:---:|---------:|--------|-----------------------|
| `10_infra_wiring` | P0 | block | FIX | block | 1 | Counts: Infra wiring defects (canonical pipeline / spine reachability). Sub: Run blocked (exit 1). | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| `J1_canonical_pipeline_wiring` | P0 | block | FIX | block | 2 | Counts: Declared canonical_pipelines.yaml steps missing required call wiring. Sub: Run blocked (exit 1). | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| `G_REACH_l0_reachability` | P0 | ratchet | FIX | regr | 2942 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: +32 vs baseline 2910. | Regression +32 over baseline 2910 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | FIX | regr | 1732 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: +128 vs baseline 1604. | Regression +128 over baseline 1604 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| `L2_lpg_drift_ratchet` | P0 | ratchet | TRACK | floor | 1 | Counts: Illegal or drifted imports touching L_PG boundary. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `3_write_sovereignty` | P0 | block | TRACK | inventory | 924 | Counts: Non-UWG durable write paths in mv_write_sovereignty_paths (inventory). Sub: 924 warn inventory; not halt-tier. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `1_critical_path_integrity` | P0 | block | CLEAR | — | 0 | Counts: Broken or missing links on declared critical execution paths (L0→sink). Sub: No findings. | None — gate clean (zero findings). |
| `2_authority_boundary` | P0 | block | CLEAR | — | 0 | Counts: Calls that cross layer authority without UWG/spine sanction. Sub: No findings. | None — gate clean (zero findings). |
| `4_capability_egress` | P0 | block | CLEAR | — | 0 | Counts: Outbound provider/SDK calls not leaving through sanctioned adapters. Sub: No findings. | None — gate clean (zero findings). |
| `5_text_to_action` | P0 | block | CLEAR | — | 0 | Counts: User text reaching action-class tools without prompt-governance gating. Sub: No findings. | None — gate clean (zero findings). |
| `6_determinism_provenance` | P0 | block | CLEAR | — | 0 | Counts: Trace roots missing determinism digest or replay key emission. Sub: No findings. | None — gate clean (zero findings). |
| `9_executor_theater` | P0 | block | CLEAR | — | 0 | Counts: Executor-theater signals: import-only or stub execution patterns. Sub: No findings. | None — gate clean (zero findings). |
| `C1_uwg_bypass_pview` | P0 | block | CLEAR | — | 0 | Counts: Any row in UWG-bypass materialized view (zero tolerance block). Sub: No findings. | None — gate clean (zero findings). |
| `C2_l5_bypass_pview` | P0 | block | CLEAR | — | 0 | Counts: Provider/tool calls skipping L5 gateway (materialized view). Sub: No findings. | None — gate clean (zero findings). |
| `W5_waiver_expiry` | P0 | block | CLEAR | — | 0 | Counts: Expired wiring-CI waiver entries in config. Sub: No findings. | None — gate clean (zero findings). |
| `8_trace_replay_eval` | P1 | ratchet | FIX | regr | 493 | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: Above ratchet baseline. | Regression +N over baseline None: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `C3_silent_writes_ratchet` | P1 | ratchet | FIX | regr | 2070 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: +89 vs baseline 1981. | Regression +89 over baseline 1981: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `M_taint_actionable_ratchet` | P1 | ratchet | FIX | regr | 708 | Counts: Actionable taint surfaces without output schema binding. Sub: +31 vs baseline 677. | Regression +31 over baseline 677: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `O_tool_call_parity_ratchet` | P1 | ratchet | FIX | regr | 344 | Counts: Tool invocations missing observability receipt (Anthropic parity pattern). Sub: +9 vs baseline 335. | Regression +9 over baseline 335: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `B2_layer_skip_ratchet` | P1 | ratchet | TRACK | floor | 951 | Counts: Import edges that skip more than one layer ordinal (layer-hop). Sub: 951 at floor (baseline 951); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C4_policy_without_audit_ratchet` | P1 | ratchet | TRACK | floor | 1 | Counts: controls_flow edges without paired audit/telemetry emission. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `E1_trace_stub_module` | P1 | ratchet | TRACK | floor | 1032 | Counts: Modules with high test:production import ratio (trace-theater stub pattern). Sub: 1032 at floor (baseline 1032); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I1_exit_disposition_ratchet` | P1 | ratchet | TRACK | floor | 742 | Counts: Terminal exit paths not covered in mv_exit_disposition_coverage. Sub: 742 at floor (baseline 742); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `N_guardrail_separation_ratchet` | P1 | ratchet | TRACK | floor | 112 | Counts: L5 guardrail and L3 core-response sharing same write target. Sub: 112 at floor (baseline 112); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `P_structured_output_ratchet` | P1 | ratchet | TRACK | floor | 1 | Counts: generates_prompt at scale without structured output schema. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `11_architecture_witness` | P1 | block | CLEAR | — | 0 | Counts: Architecture witness Class A/B absence or live-plane write violations. Sub: No findings. | None — gate clean (zero findings). |
| `12_prompt_assembly_wiring` | P1 | block | CLEAR | — | 0 | Counts: Prompt-assembly subgraph disconnected from runtime spine. Sub: No findings. | None — gate clean (zero findings). |
| `7_lifecycle_coverage` | P1 | ratchet | CLEAR | — | 0 | Counts: Lifecycle gaps: resources opened without matching close/cleanup. Sub: No findings. | None — gate clean (zero findings). |
| `G2_seam_test_export_coherence` | P1 | block | CLEAR | — | 0 | Counts: Production seam symbols exported in tests but not in package __all__/exports. Sub: No findings. | None — gate clean (zero findings). |
| `G_ISLAND_connected_components` | P1 | ratchet | CLEAR | — | 0 | Counts: Non-giant connected components on undirected import graph. Sub: No findings. | None — gate clean (zero findings). |
| `G_WATCHLIST_DELTA_hotspot_regressions` | P1 | ratchet | CLEAR | — | 0 | Counts: Graph watchlist items newly FAIL/WARN vs prior run. Sub: No findings. | None — gate clean (zero findings). |
| `H1_new_orphans_delta_ratchet` | P1 | ratchet | CLEAR | — | 0 | Counts: Modules newly fan_in=0 vs prior snapshot (new orphans). Sub: No findings. | None — gate clean (zero findings). |
| `H2_fanin_collapse_ratchet` | P1 | ratchet | CLEAR | — | 0 | Counts: Hotspot modules with >30% fan_in drop vs prior snapshot. Sub: No findings. | None — gate clean (zero findings). |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | FIX | regr | 1102 | Counts: State mutations not consumed by replay surface (gap_flag=1). Sub: +78 vs baseline 1024. | Regression +78 over baseline 1024: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `F1_untyped_seam_ratchet` | P2 | ratchet | TRACK | floor | 1075 | Counts: Cross-layer imports where target has empty type_surface. Sub: 1075 at floor (baseline 1075); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D2_role_duplication_warn` | P2 | warn | TRACK | advis | 101 | Counts: Role-suffix clusters (_reranker, _planner, …) with fan_in=0 members (advisory). Sub: 101 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `A3_dead_public_symbol_ratchet` | P2 | ratchet | CLEAR | — | 0 | Counts: Public symbols with zero importers (dead surface). Sub: No findings. | None — gate clean (zero findings). |
| `C5_unresolved_callsites_ratchet` | P2 | ratchet | CLEAR | — | 0 | Counts: resolves_callsite edges with NULL destination (unresolved callee). Sub: No findings. | None — gate clean (zero findings). |
| `F2_broken_contract_ratchet` | P2 | ratchet | CLEAR | — | 0 | Counts: Import targets publishing zero exports edges (contract drift). Sub: No findings. | None — gate clean (zero findings). |
| `H4_mv_staleness_ratchet` | P2 | ratchet | CLEAR | — | 0 | Counts: Total edge count delta >5% vs prior snapshot (graph drift). Sub: No findings. | None — gate clean (zero findings). |
| `M1_module_loc_ratchet` | P3 | ratchet | FIX | regr | 464 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: +14 vs baseline 450. | Regression +14 over baseline 450: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | FIX | regr | 1066 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: +46 vs baseline 1020. | Regression +46 over baseline 1020: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `S4_unused_imports_ratchet` | P3 | ratchet | FIX | regr | 11023 | Counts: Unused import edges in production modules. Sub: +184 vs baseline 10839. | Regression +184 over baseline 10839: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `D1_layer_doc_binding` | P3 | warn | TRACK | advis | 3 | Counts: Layer folders missing or mismatched LAYER.md binding (advisory). Sub: 3 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `E3_trace_theater_kpi` | P3 | warn | CLEAR | — | 0 | Counts: Emit-symbol density per layer vs imports (KPI advisory). Sub: No findings. | None — gate clean (zero findings). |
| `F3_missing_adapter_warn` | P3 | warn | CLEAR | — | 0 | Counts: Protocol/ABC/Interface with zero implements edges (advisory). Sub: No findings. | None — gate clean (zero findings). |
| `H3_ap_velocity_kpi` | P3 | warn | CLEAR | — | 0 | Counts: Antipattern edge density per 1k LOC (KPI advisory). Sub: No findings. | None — gate clean (zero findings). |
| `K1_churn_complexity_kpi` | P3 | warn | CLEAR | — | 0 | Counts: High churn×complexity files (KPI advisory, jsonl sink). Sub: No findings. | None — gate clean (zero findings). |

### Fix now (Verdict FIX)

| Gate ID | Sub | Findings |
|---------|:---:|---------:|
| `S4_unused_imports_ratchet` | regr | 11023 |
| `G_REACH_l0_reachability` | regr | 2942 |
| `C3_silent_writes_ratchet` | regr | 2070 |
| `S2_uwg_bypass_ratchet` | regr | 1732 |
| `I2_replay_surface_gaps_ratchet` | regr | 1102 |
| `Q2_cyclomatic_complexity_ratchet` | regr | 1066 |
| `M_taint_actionable_ratchet` | regr | 708 |
| `8_trace_replay_eval` | regr | 493 |
| `M1_module_loc_ratchet` | regr | 464 |
| `O_tool_call_parity_ratchet` | regr | 344 |
| `J1_canonical_pipeline_wiring` | block | 2 |
| `10_infra_wiring` | block | 1 |

### Track later (Verdict TRACK — CI OK, backlog remains)

| Gate ID | Sub | Findings |
|---------|:---:|---------:|
| `F1_untyped_seam_ratchet` | floor | 1075 |
| `E1_trace_stub_module` | floor | 1032 |
| `B2_layer_skip_ratchet` | floor | 951 |
| `3_write_sovereignty` | inventory | 924 |
| `I1_exit_disposition_ratchet` | floor | 742 |
| `N_guardrail_separation_ratchet` | floor | 112 |
| `D2_role_duplication_warn` | advis | 101 |
| `D1_layer_doc_binding` | advis | 3 |
| `C4_policy_without_audit_ratchet` | floor | 1 |
| `L2_lpg_drift_ratchet` | floor | 1 |
| `P_structured_output_ratchet` | floor | 1 |

## 4. Aggregate Verdicts

| Verdict | Count | Meaning |
|---------|------:|---------|
| block_pass | 13 | Block-class gates that did not halt the run (exit 0). Findings may be non-zero. |
| block_fail | 2 | Block-class gates that halted the run — clear the gate blocking condition. |
| ratchet_pass | 17 | Ratchet-class gates within their baseline ceiling. |
| ratchet_regressed | 10 | Ratchet-class gates with NEW findings beyond baseline. |
| ratchet_seed_missing | 0 | Ratchet-class gates without a baseline seed (first run). |
| warn | 6 | Advisory-class gates (do not gate the run). |

### Per-gate verdict rollup (this report)

| Verdict | Gates | Meaning |
|---------|------:|---------|
| FIX | 12 | Address before treating ADG as green (gate blocked or ratchet regressed). |
| TRACK | 11 | CI passed this gate; findings are backlog — plan hygiene, not a halt. |
| CLEAR | 25 | Zero findings; nothing to do on this gate. |

## 5. Fix now (detail)

| Gate | Band | Enf | Sub | Findings | Signal |
|------|:----:|:---:|:---:|---------:|--------|
| `S4_unused_imports_ratchet` | P3 | ratchet | regr | 11023 | Counts: Unused import edges in production modules. Sub: +184 vs baseline 10839. |
| `G_REACH_l0_reachability` | P0 | ratchet | regr | 2942 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: +32 vs baseline 2910. |
| `C3_silent_writes_ratchet` | P1 | ratchet | regr | 2070 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: +89 vs baseline 1981. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | regr | 1732 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: +128 vs baseline 1604. |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | regr | 1102 | Counts: State mutations not consumed by replay surface (gap_flag=1). Sub: +78 vs baseline 1024. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | regr | 1066 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: +46 vs baseline 1020. |
| `M_taint_actionable_ratchet` | P1 | ratchet | regr | 708 | Counts: Actionable taint surfaces without output schema binding. Sub: +31 vs baseline 677. |
| `8_trace_replay_eval` | P1 | ratchet | regr | 493 | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: Above ratchet baseline. |
| `M1_module_loc_ratchet` | P3 | ratchet | regr | 464 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: +14 vs baseline 450. |
| `O_tool_call_parity_ratchet` | P1 | ratchet | regr | 344 | Counts: Tool invocations missing observability receipt (Anthropic parity pattern). Sub: +9 vs baseline 335. |
| `J1_canonical_pipeline_wiring` | P0 | block | block | 2 | Counts: Declared canonical_pipelines.yaml steps missing required call wiring. Sub: Run blocked (exit 1). |
| `10_infra_wiring` | P0 | block | block | 1 | Counts: Infra wiring defects (canonical pipeline / spine reachability). Sub: Run blocked (exit 1). |

---
## Next action

No `adg_action_queue_*.json` found. Emit with: `python tools/reports/adg_action_queue.py --latest`

Playbook: [adg_action_dispatch_playbook.md](../../docs/reports/cursor/adg_action_dispatch_playbook.md)

---
Report renderer: `tools/reports/adg_burndown_report.py`. Re-run with `python tools/reports/adg_burndown_report.py --out artifacts/adg/adg_burndown_report.md`.
