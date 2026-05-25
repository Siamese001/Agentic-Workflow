# ADG CI Burndown Report

- **Generated:** 2026-05-25T13:28:42+00:00
- **Gate-results source:** `artifacts\adg\adg_gate_results_20260525_130122.json`
- **Burndown source:** `artifacts\adg\adg_burndown_table.json`
- **Snapshot timestamp:** 2026-05-25T13:01:22.546022+00:00
- **Total gates:** 48
- **Overall verdict:** **BLOCKED** (run halt — exit code)
- **Action:** **FIX**=3 (address for green ADG) · **TRACK**=19 (CI OK, backlog) · **CLEAR**=26

## 1. Burndown by Severity Band

Counts come from the canonical `adg_burndown_table.json` (schema 2.2).
`gross` = raw violations found. `guardian` = guardian-exempted (still counted).
`net` = `gross - guardian`. `diff` = delta vs prior snapshot baseline.

| Band | Label | Gross | Guardian | Net | Diff vs prev |
|------|-------|------:|---------:|----:|-------------:|
| P0 | layer_violations | 38 | 38 | 0 | +38 |
| P1 | anti_patterns_high | 1192 | 1192 | 0 | +1192 |
| P2 | anti_patterns_medium | 671 | 671 | 0 | +671 |
| P3 | style_warnings | 18401 | 74 | 18327 | +74 |

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

| Gate ID | Band | Enf | Verdict | Sub | Findings | Signal |
|---------|:----:|:---:|:-------:|:---:|---------:|--------|
| `G_REACH_l0_reachability` | P0 | ratchet | TRACK | floor | 2792 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: 2792 at floor (baseline 2792); no new debt. |
| `L2_lpg_drift_ratchet` | P0 | ratchet | TRACK | floor | 28 | Counts: Illegal or drifted imports touching L_PG boundary. Sub: 28 at floor (baseline 28); no new debt. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | TRACK | floor | 1600 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: 1600 at floor (baseline 1600); no new debt. |
| `3_write_sovereignty` | P0 | block | TRACK | inventory | 848 | Counts: Non-UWG durable write paths in mv_write_sovereignty_paths (inventory). Sub: 848 warn inventory; not halt-tier. |
| `J1_canonical_pipeline_wiring` | P0 | block | TRACK | inventory | 1 | Counts: Declared canonical_pipelines.yaml steps missing required call wiring. Sub: 1 subprocess warn. |
| `10_infra_wiring` | P0 | block | CLEAR | — | 0 | Counts: Infra wiring defects (canonical pipeline / spine reachability). Sub: No findings. |
| `1_critical_path_integrity` | P0 | block | CLEAR | — | 0 | Counts: Broken or missing links on declared critical execution paths (L0→sink). Sub: No findings. |
| `2_authority_boundary` | P0 | block | CLEAR | — | 0 | Counts: Calls that cross layer authority without UWG/spine sanction. Sub: No findings. |
| `4_capability_egress` | P0 | block | CLEAR | — | 0 | Counts: Outbound provider/SDK calls not leaving through sanctioned adapters. Sub: No findings. |
| `5_text_to_action` | P0 | block | CLEAR | — | 0 | Counts: User text reaching action-class tools without prompt-governance gating. Sub: No findings. |
| `6_determinism_provenance` | P0 | block | CLEAR | — | 0 | Counts: Trace roots missing determinism digest or replay key emission. Sub: No findings. |
| `9_executor_theater` | P0 | block | CLEAR | — | 0 | Counts: Executor-theater signals: import-only or stub execution patterns. Sub: No findings. |
| `C1_uwg_bypass_pview` | P0 | block | CLEAR | — | 0 | Counts: Any row in UWG-bypass materialized view (zero tolerance block). Sub: No findings. |
| `C2_l5_bypass_pview` | P0 | block | CLEAR | — | 0 | Counts: Provider/tool calls skipping L5 gateway (materialized view). Sub: No findings. |
| `W5_waiver_expiry` | P0 | block | CLEAR | — | 0 | Counts: Expired wiring-CI waiver entries in config. Sub: No findings. |
| `B2_layer_skip_ratchet` | P1 | ratchet | FIX | regr | 975 | Counts: Import edges that skip more than one layer ordinal (layer-hop). Sub: +21 vs baseline 954. |
| `C3_silent_writes_ratchet` | P1 | ratchet | TRACK | floor | 1932 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: 1932 at floor (baseline 1932); no new debt. |
| `C4_policy_without_audit_ratchet` | P1 | ratchet | TRACK | floor | 1 | Counts: controls_flow edges without paired audit/telemetry emission. Sub: 1 at floor (baseline 1); no new debt. |
| `E1_trace_stub_module` | P1 | ratchet | TRACK | floor | 1036 | Counts: Modules with high test:production import ratio (trace-theater stub pattern). Sub: 1036 at floor (baseline 1036); no new debt. |
| `H1_new_orphans_delta_ratchet` | P1 | ratchet | TRACK | floor | 296 | Counts: Modules newly fan_in=0 vs prior snapshot (new orphans). Sub: 296 at floor (baseline 296); no new debt. |
| `I1_exit_disposition_ratchet` | P1 | ratchet | TRACK | floor | 726 | Counts: Terminal exit paths not covered in mv_exit_disposition_coverage. Sub: 726 at floor (baseline 726); no new debt. |
| `M_taint_actionable_ratchet` | P1 | ratchet | TRACK | floor | 657 | Counts: Actionable taint surfaces without output schema binding. Sub: 657 at floor (baseline 657); no new debt. |
| `N_guardrail_separation_ratchet` | P1 | ratchet | TRACK | floor | 112 | Counts: L5 guardrail and L3 core-response sharing same write target. Sub: 112 at floor (baseline 112); no new debt. |
| `O_tool_call_parity_ratchet` | P1 | ratchet | TRACK | floor | 315 | Counts: Tool invocations missing observability receipt (Anthropic parity pattern). Sub: 315 at floor (baseline 315); no new debt. |
| `P_structured_output_ratchet` | P1 | ratchet | TRACK | floor | 1 | Counts: generates_prompt at scale without structured output schema. Sub: 1 at floor (baseline 1); no new debt. |
| `11_architecture_witness` | P1 | block | CLEAR | — | 0 | Counts: Architecture witness Class A/B absence or live-plane write violations. Sub: No findings. |
| `12_prompt_assembly_wiring` | P1 | block | CLEAR | — | 0 | Counts: Prompt-assembly subgraph disconnected from runtime spine. Sub: No findings. |
| `7_lifecycle_coverage` | P1 | ratchet | CLEAR | — | 0 | Counts: Lifecycle gaps: resources opened without matching close/cleanup. Sub: No findings. |
| `8_trace_replay_eval` | P1 | ratchet | CLEAR | — | 0 | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: No findings. |
| `G2_seam_test_export_coherence` | P1 | block | CLEAR | — | 0 | Counts: Production seam symbols exported in tests but not in package __all__/exports. Sub: No findings. |
| `G_ISLAND_connected_components` | P1 | ratchet | CLEAR | — | 0 | Counts: Non-giant connected components on undirected import graph. Sub: No findings. |
| `G_WATCHLIST_DELTA_hotspot_regressions` | P1 | ratchet | CLEAR | — | 0 | Counts: Graph watchlist items newly FAIL/WARN vs prior run. Sub: No findings. |
| `H2_fanin_collapse_ratchet` | P1 | ratchet | CLEAR | — | 0 | Counts: Hotspot modules with >30% fan_in drop vs prior snapshot. Sub: No findings. |
| `F1_untyped_seam_ratchet` | P2 | ratchet | FIX | regr | 1105 | Counts: Cross-layer imports where target has empty type_surface. Sub: +27 vs baseline 1078. |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | TRACK | floor | 1054 | Counts: State mutations not consumed by replay surface (gap_flag=1). Sub: 1054 at floor (baseline 1054); no new debt. |
| `D2_role_duplication_warn` | P2 | warn | TRACK | advis | 99 | Counts: Role-suffix clusters (_reranker, _planner, …) with fan_in=0 members (advisory). Sub: 99 advisory; never blocks. |
| `A3_dead_public_symbol_ratchet` | P2 | ratchet | CLEAR | — | 0 | Counts: Public symbols with zero importers (dead surface). Sub: No findings. |
| `C5_unresolved_callsites_ratchet` | P2 | ratchet | CLEAR | — | 0 | Counts: resolves_callsite edges with NULL destination (unresolved callee). Sub: No findings. |
| `F2_broken_contract_ratchet` | P2 | ratchet | CLEAR | — | 0 | Counts: Import targets publishing zero exports edges (contract drift). Sub: No findings. |
| `H4_mv_staleness_ratchet` | P2 | ratchet | CLEAR | — | 0 | Counts: Total edge count delta >5% vs prior snapshot (graph drift). Sub: No findings. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | FIX | regr | 911 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: +1 vs baseline 910. |
| `M1_module_loc_ratchet` | P3 | ratchet | TRACK | floor | 442 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: 442 at floor (baseline 442); no new debt. |
| `S4_unused_imports_ratchet` | P3 | ratchet | TRACK | floor | 10699 | Counts: Unused import edges in production modules. Sub: 10699 at floor (baseline 10699); no new debt. |
| `D1_layer_doc_binding` | P3 | warn | TRACK | advis | 3 | Counts: Layer folders missing or mismatched LAYER.md binding (advisory). Sub: 3 advisory; never blocks. |
| `E3_trace_theater_kpi` | P3 | warn | CLEAR | — | 0 | Counts: Emit-symbol density per layer vs imports (KPI advisory). Sub: No findings. |
| `F3_missing_adapter_warn` | P3 | warn | CLEAR | — | 0 | Counts: Protocol/ABC/Interface with zero implements edges (advisory). Sub: No findings. |
| `H3_ap_velocity_kpi` | P3 | warn | CLEAR | — | 0 | Counts: Antipattern edge density per 1k LOC (KPI advisory). Sub: No findings. |
| `K1_churn_complexity_kpi` | P3 | warn | CLEAR | — | 0 | Counts: High churn×complexity files (KPI advisory, jsonl sink). Sub: No findings. |

### Fix now (Verdict FIX)

| Gate ID | Sub | Findings |
|---------|:---:|---------:|
| `F1_untyped_seam_ratchet` | regr | 1105 |
| `B2_layer_skip_ratchet` | regr | 975 |
| `Q2_cyclomatic_complexity_ratchet` | regr | 911 |

### Track later (Verdict TRACK — CI OK, backlog remains)

| Gate ID | Sub | Findings |
|---------|:---:|---------:|
| `S4_unused_imports_ratchet` | floor | 10699 |
| `G_REACH_l0_reachability` | floor | 2792 |
| `C3_silent_writes_ratchet` | floor | 1932 |
| `S2_uwg_bypass_ratchet` | floor | 1600 |
| `I2_replay_surface_gaps_ratchet` | floor | 1054 |
| `E1_trace_stub_module` | floor | 1036 |
| `3_write_sovereignty` | inventory | 848 |
| `I1_exit_disposition_ratchet` | floor | 726 |
| `M_taint_actionable_ratchet` | floor | 657 |
| `M1_module_loc_ratchet` | floor | 442 |
| `O_tool_call_parity_ratchet` | floor | 315 |
| `H1_new_orphans_delta_ratchet` | floor | 296 |
| `N_guardrail_separation_ratchet` | floor | 112 |
| `D2_role_duplication_warn` | advis | 99 |
| `L2_lpg_drift_ratchet` | floor | 28 |
| `D1_layer_doc_binding` | advis | 3 |
| `C4_policy_without_audit_ratchet` | floor | 1 |
| `J1_canonical_pipeline_wiring` | inventory | 1 |
| `P_structured_output_ratchet` | floor | 1 |

## 4. Aggregate Verdicts

| Verdict | Count | Meaning |
|---------|------:|---------|
| block_pass | 14 | Block-class gates that did not halt the run (exit 0). Findings may be non-zero. |
| block_fail | 0 | Block-class gates that halted the run — clear the gate blocking condition. |
| ratchet_pass | 24 | Ratchet-class gates within their baseline ceiling. |
| ratchet_regressed | 3 | Ratchet-class gates with NEW findings beyond baseline. |
| ratchet_seed_missing | 0 | Ratchet-class gates without a baseline seed (first run). |
| warn | 6 | Advisory-class gates (do not gate the run). |

### Per-gate verdict rollup (this report)

| Verdict | Gates | Meaning |
|---------|------:|---------|
| FIX | 3 | Address before treating ADG as green (gate blocked or ratchet regressed). |
| TRACK | 19 | CI passed this gate; findings are backlog — plan hygiene, not a halt. |
| CLEAR | 26 | Zero findings; nothing to do on this gate. |

## 5. Fix now (detail)

| Gate | Band | Enf | Sub | Findings | Signal |
|------|:----:|:---:|:---:|---------:|--------|
| `F1_untyped_seam_ratchet` | P2 | ratchet | regr | 1105 | Counts: Cross-layer imports where target has empty type_surface. Sub: +27 vs baseline 1078. |
| `B2_layer_skip_ratchet` | P1 | ratchet | regr | 975 | Counts: Import edges that skip more than one layer ordinal (layer-hop). Sub: +21 vs baseline 954. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | regr | 911 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: +1 vs baseline 910. |

---
## Next action

- **Queue:** `artifacts\adg\adg_action_queue_20260525_130122.json`
- **emit_status:** `ok`
- **degraded:** `False`
- **summary:** FIX=3 · TRACK=19 · actions_emitted=5

| Rank | Verdict | Target | ordering_reason |
|-----:|---------|--------|-----------------|
| 1 | FIX | `B2_layer_skip_ratchet` | fix_regr_p1_delta_asc |
| 2 | FIX | `F1_untyped_seam_ratchet` | fix_regr_p2_delta_asc |
| 3 | FIX | `Q2_cyclomatic_complexity_ratchet` | fix_regr_p3_delta_asc |
| 4 | P0_WAVE | `apps_shared/integrations/governed_app_runner.py` | p0_wave_top_files_priority |
| 5 | P0_WAVE | `apps_research/integrations/execution_adapter.py` | p0_wave_top_files_priority |

CLI: `python tools/reports/adg_action_queue.py --latest --top 10 --format markdown`

---
Report renderer: `tools/reports/adg_burndown_report.py`. Re-run with `python tools/reports/adg_burndown_report.py --out artifacts/adg/adg_burndown_report.md`.
