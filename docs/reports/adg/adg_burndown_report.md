# ADG CI Burndown Report

- **Generated:** 2026-06-13T16:29:21+00:00
- **Gate-results source:** `artifacts\adg\adg_gate_results_20260613_162714.json`
- **Burndown source:** `artifacts\adg\adg_burndown_table.json`
- **Snapshot timestamp:** 2026-06-13T16:27:14.504649+00:00
- **Total gates:** 48
- **Overall verdict:** **PASS** (run halt — exit code)
- **Action:** **FIX**=0 (address for green ADG) · **TRACK**=21 (CI OK, backlog) · **CLEAR**=27

## 1. P0-P3 CI Band Summary

This is the gate/enforcement view from `adg_gate_results_*.json`, not the raw severity inventory.

| CI Band | Gates | FIX | TRACK | CLEAR | Block Fail | Ratchet Regr | Seed Missing | Findings |
|---------|------:|----:|------:|------:|-----------:|-------------:|-------------:|---------:|
| P0 | 15 | 0 | 5 | 10 | 0 | 0 | 0 | 5345 |
| P1 | 18 | 0 | 9 | 9 | 0 | 0 | 0 | 5970 |
| P2 | 7 | 0 | 3 | 4 | 0 | 0 | 0 | 2276 |
| P3 | 8 | 0 | 4 | 4 | 0 | 0 | 0 | 12482 |

`FIX` is the only action class that must be cleared for green ADG. `TRACK` is backlog.

## 2. ADG CI Gates

One row per registered gate.

- **Action** — **FIX** = address now · **TRACK** = backlog, CI OK · **CLEAR** = zero findings.
- **Sub** — detail (block / regr / floor / inventory / …); see glossary.
- **Allowed Floor** — zero-tolerance for block gates, baseline for ratchets, advisory/inventory otherwise.
- **Signal** — what Findings count + short Sub note.
- **Next Best Action** — concrete action for this gate (fix / re-baseline / defer / none).

| Gate ID | CI Band | Enforcement | Action | Sub | Findings | Allowed Floor | Signal | Next Best Action |
|---------|:-------:|-------------|:------:|:---:|---------:|---------------|--------|------------------|
| `G_REACH_l0_reachability` | P0 | ratchet | TRACK | floor | 2843 | 2843 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: 2843 at floor (baseline 2843); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `L2_lpg_drift_ratchet` | P0 | ratchet | TRACK | floor | 1 | 1 | Counts: Illegal or drifted imports touching L_PG boundary. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | TRACK | floor | 1583 | 1583 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: 1583 at floor (baseline 1583); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `3_write_sovereignty` | P0 | block | TRACK | inventory | 917 | warn inventory | Counts: Non-UWG durable write paths in mv_write_sovereignty_paths (inventory). Sub: 917 warn inventory; not halt-tier. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `J1_canonical_pipeline_wiring` | P0 | block | TRACK | inventory | 1 | warn inventory | Counts: Declared canonical_pipelines.yaml steps missing required call wiring. Sub: 1 subprocess warn. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `10_infra_wiring` | P0 | block | CLEAR | — | 0 | 0 | Counts: Infra wiring defects (canonical pipeline / spine reachability). Sub: No findings. | None — gate clean (zero findings). |
| `1_critical_path_integrity` | P0 | block | CLEAR | — | 0 | 0 | Counts: Broken or missing links on declared critical execution paths (L0→sink). Sub: No findings. | None — gate clean (zero findings). |
| `2_authority_boundary` | P0 | block | CLEAR | — | 0 | 0 | Counts: Calls that cross layer authority without UWG/spine sanction. Sub: No findings. | None — gate clean (zero findings). |
| `4_capability_egress` | P0 | block | CLEAR | — | 0 | 0 | Counts: Outbound provider/SDK calls not leaving through sanctioned adapters. Sub: No findings. | None — gate clean (zero findings). |
| `5_text_to_action` | P0 | block | CLEAR | — | 0 | 0 | Counts: User text reaching action-class tools without prompt-governance gating. Sub: No findings. | None — gate clean (zero findings). |
| `6_determinism_provenance` | P0 | block | CLEAR | — | 0 | 0 | Counts: Trace roots missing determinism digest or replay key emission. Sub: No findings. | None — gate clean (zero findings). |
| `9_executor_theater` | P0 | block | CLEAR | — | 0 | 0 | Counts: Executor-theater signals: import-only or stub execution patterns. Sub: No findings. | None — gate clean (zero findings). |
| `C1_uwg_bypass_pview` | P0 | block | CLEAR | — | 0 | 0 | Counts: Any row in UWG-bypass materialized view (zero tolerance block). Sub: No findings. | None — gate clean (zero findings). |
| `C2_l5_bypass_pview` | P0 | block | CLEAR | — | 0 | 0 | Counts: Provider/tool calls skipping L5 gateway (materialized view). Sub: No findings. | None — gate clean (zero findings). |
| `W5_waiver_expiry` | P0 | block | CLEAR | — | 0 | 0 | Counts: Expired wiring-CI waiver entries in config. Sub: No findings. | None — gate clean (zero findings). |
| `B2_layer_skip_ratchet` | P1 | ratchet | TRACK | floor | 951 | 951 | Counts: Import edges that skip more than one layer ordinal (layer-hop). Sub: 951 at floor (baseline 951); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C3_silent_writes_ratchet` | P1 | ratchet | TRACK | floor | 2085 | 2085 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: 2085 at floor (baseline 2085); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C4_policy_without_audit_ratchet` | P1 | ratchet | TRACK | floor | 1 | 1 | Counts: controls_flow edges without paired audit/telemetry emission. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `E1_trace_stub_module` | P1 | ratchet | TRACK | floor | 1030 | 1030 | Counts: Modules with high test:production import ratio (trace-theater stub pattern). Sub: 1030 at floor (baseline 1030); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I1_exit_disposition_ratchet` | P1 | ratchet | TRACK | floor | 742 | 742 | Counts: Terminal exit paths not covered in mv_exit_disposition_coverage. Sub: 742 at floor (baseline 742); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `M_taint_actionable_ratchet` | P1 | ratchet | TRACK | floor | 703 | 703 | Counts: Actionable taint surfaces without output schema binding. Sub: 703 at floor (baseline 703); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `N_guardrail_separation_ratchet` | P1 | ratchet | TRACK | floor | 112 | 112 | Counts: L5 guardrail and L3 core-response sharing same write target. Sub: 112 at floor (baseline 112); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `O_tool_call_parity_ratchet` | P1 | ratchet | TRACK | floor | 345 | 345 | Counts: Tool invocations missing observability receipt (Anthropic parity pattern). Sub: 345 at floor (baseline 345); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `P_structured_output_ratchet` | P1 | ratchet | TRACK | floor | 1 | 1 | Counts: generates_prompt at scale without structured output schema. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `11_architecture_witness` | P1 | block | CLEAR | — | 0 | 0 | Counts: Architecture witness Class A/B absence or live-plane write violations. Sub: No findings. | None — gate clean (zero findings). |
| `12_prompt_assembly_wiring` | P1 | block | CLEAR | — | 0 | 0 | Counts: Prompt-assembly subgraph disconnected from runtime spine. Sub: No findings. | None — gate clean (zero findings). |
| `7_lifecycle_coverage` | P1 | ratchet | CLEAR | — | 0 | unseeded | Counts: Lifecycle gaps: resources opened without matching close/cleanup. Sub: No findings. | None — gate clean (zero findings). |
| `8_trace_replay_eval` | P1 | ratchet | CLEAR | — | 0 | unseeded | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: No findings. | None — gate clean (zero findings). |
| `G2_seam_test_export_coherence` | P1 | block | CLEAR | — | 0 | 0 | Counts: Production seam symbols exported in tests but not in package __all__/exports. Sub: No findings. | None — gate clean (zero findings). |
| `G_ISLAND_connected_components` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Non-giant connected components on undirected import graph. Sub: No findings. | None — gate clean (zero findings). |
| `G_WATCHLIST_DELTA_hotspot_regressions` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Graph watchlist items newly FAIL/WARN vs prior run. Sub: No findings. | None — gate clean (zero findings). |
| `H1_new_orphans_delta_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Modules newly fan_in=0 vs prior snapshot (new orphans). Sub: No findings. | None — gate clean (zero findings). |
| `H2_fanin_collapse_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Hotspot modules with >30% fan_in drop vs prior snapshot. Sub: No findings. | None — gate clean (zero findings). |
| `F1_untyped_seam_ratchet` | P2 | ratchet | TRACK | floor | 1075 | 1075 | Counts: Cross-layer imports where target has empty type_surface. Sub: 1075 at floor (baseline 1075); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | TRACK | floor | 1099 | 1099 | Counts: State mutations not consumed by replay surface (gap_flag=1). Sub: 1099 at floor (baseline 1099); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D2_role_duplication_warn` | P2 | warn | TRACK | advis | 102 | advisory | Counts: Role-suffix clusters (_reranker, _planner, …) with fan_in=0 members (advisory). Sub: 102 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `A3_dead_public_symbol_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Public symbols with zero importers (dead surface). Sub: No findings. | None — gate clean (zero findings). |
| `C5_unresolved_callsites_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: resolves_callsite edges with NULL destination (unresolved callee). Sub: No findings. | None — gate clean (zero findings). |
| `F2_broken_contract_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Import targets publishing zero exports edges (contract drift). Sub: No findings. | None — gate clean (zero findings). |
| `H4_mv_staleness_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Total edge count delta >5% vs prior snapshot (graph drift). Sub: No findings. | None — gate clean (zero findings). |
| `M1_module_loc_ratchet` | P3 | ratchet | TRACK | floor | 459 | 459 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: 459 at floor (baseline 459); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | TRACK | floor | 1083 | 1083 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: 1083 at floor (baseline 1083); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `S4_unused_imports_ratchet` | P3 | ratchet | TRACK | floor | 10937 | 10937 | Counts: Unused import edges in production modules. Sub: 10937 at floor (baseline 10937); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D1_layer_doc_binding` | P3 | warn | TRACK | advis | 3 | advisory | Counts: Layer folders missing or mismatched LAYER.md binding (advisory). Sub: 3 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `E3_trace_theater_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Emit-symbol density per layer vs imports (KPI advisory). Sub: No findings. | None — gate clean (zero findings). |
| `F3_missing_adapter_warn` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Protocol/ABC/Interface with zero implements edges (advisory). Sub: No findings. | None — gate clean (zero findings). |
| `H3_ap_velocity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Antipattern edge density per 1k LOC (KPI advisory). Sub: No findings. | None — gate clean (zero findings). |
| `K1_churn_complexity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: High churn×complexity files (KPI advisory, jsonl sink). Sub: No findings. | None — gate clean (zero findings). |

### Track later (Verdict TRACK — CI OK, backlog remains)

| Gate ID | Sub | Findings |
|---------|:---:|---------:|
| `S4_unused_imports_ratchet` | floor | 10937 |
| `G_REACH_l0_reachability` | floor | 2843 |
| `C3_silent_writes_ratchet` | floor | 2085 |
| `S2_uwg_bypass_ratchet` | floor | 1583 |
| `I2_replay_surface_gaps_ratchet` | floor | 1099 |
| `Q2_cyclomatic_complexity_ratchet` | floor | 1083 |
| `F1_untyped_seam_ratchet` | floor | 1075 |
| `E1_trace_stub_module` | floor | 1030 |
| `B2_layer_skip_ratchet` | floor | 951 |
| `3_write_sovereignty` | inventory | 917 |
| `I1_exit_disposition_ratchet` | floor | 742 |
| `M_taint_actionable_ratchet` | floor | 703 |
| `M1_module_loc_ratchet` | floor | 459 |
| `O_tool_call_parity_ratchet` | floor | 345 |
| `N_guardrail_separation_ratchet` | floor | 112 |
| `D2_role_duplication_warn` | advis | 102 |
| `D1_layer_doc_binding` | advis | 3 |
| `C4_policy_without_audit_ratchet` | floor | 1 |
| `J1_canonical_pipeline_wiring` | inventory | 1 |
| `L2_lpg_drift_ratchet` | floor | 1 |
| `P_structured_output_ratchet` | floor | 1 |

## 3. Severity Inventory Burndown

Counts come from the canonical `adg_burndown_table.json` (schema 2.2).
This is raw MV defect inventory by severity/source band; it is not one row per CI gate.
`gross` = raw violations found. `guardian` = guardian-exempted (still counted).
`net` = `gross - guardian`. `diff` = delta vs prior snapshot baseline.

| Severity Band | Label | Gross | Guardian | Net | Diff vs prev |
|---------------|-------|------:|---------:|----:|-------------:|
| P0 | layer_violations | 46 | 41 | 5 | +41 |
| P1 | anti_patterns_high | 1197 | 1193 | 4 | +1193 |
| P2 | anti_patterns_medium | 751 | 730 | 21 | +730 |
| P3 | style_warnings | 20131 | 92 | 20039 | +92 |

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

## 4. Aggregate Verdicts

| Verdict | Count | Meaning |
|---------|------:|---------|
| block_pass | 14 | Block-class gates that did not halt the run (exit 0). Findings may be non-zero. |
| block_fail | 0 | Block-class gates that halted the run — clear the gate blocking condition. |
| ratchet_pass | 27 | Ratchet-class gates within their baseline ceiling. |
| ratchet_regressed | 0 | Ratchet-class gates with NEW findings beyond baseline. |
| ratchet_seed_missing | 0 | Ratchet-class gates without a baseline seed (first run). |
| warn | 6 | Advisory-class gates (do not gate the run). |

### Per-gate verdict rollup (this report)

| Verdict | Gates | Meaning |
|---------|------:|---------|
| TRACK | 21 | CI passed this gate; findings are backlog — plan hygiene, not a halt. |
| CLEAR | 27 | Zero findings; nothing to do on this gate. |

## 5. Fix now (detail)

_No FIX gates._

---
## Next action

- **Queue:** `artifacts\adg\adg_action_queue_06132026_1222.json`
- **emit_status:** `ok`
- **degraded:** `False`
- **summary:** FIX=0 · TRACK=21 · actions_emitted=9

| Rank | Lane | Kind | Target | ordering_reason | Signal |
|-----:|------|------|--------|-----------------|--------|
| 1 | GRAPHDB | test_hotspot_gap | `apps_rg/runtime/sections/executive_summary_lane.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (absent); critical... |
| 2 | GRAPHDB | test_hotspot_gap | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (0.0%); criticalit... |
| 3 | GRAPHDB | test_hotspot_gap | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (0.0%); criticalit... |
| 4 | REFACTOR | refactor_candidate | `agentic_core/adg/extraction/static_scanner.py` | refactor_accelerator_candidates_desc | Refactor candidate; score=0.2521 |
| 5 | REFACTOR | refactor_candidate | `agentic_core/base_agents/SovereignBaseAgent.py` | refactor_accelerator_candidates_desc | Refactor candidate; score=0.1234 |

CLI: `python tools/reports/adg_action_queue.py --latest --top 10 --format markdown`

---
Report renderer: `tools/reports/adg_burndown_report.py`. Re-run with `python tools/reports/adg_burndown_report.py --out artifacts/adg/adg_burndown_report.md`.
