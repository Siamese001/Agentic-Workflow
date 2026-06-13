# ADG CI Burndown Report

- **Generated:** 2026-06-13T21:29:17+00:00
- **Gate-results source:** `artifacts\adg\adg_gate_results_20260613_204942.json`
- **Burndown source:** `artifacts\adg\adg_burndown_table.json`
- **Snapshot timestamp:** 2026-06-13T20:49:42.453429+00:00
- **Total gates:** 48
- **Overall verdict:** **PASS** (run halt — exit code)
- **Action:** **FIX**=0 (address for green ADG) · **TRACK**=21 (CI OK, backlog) · **CLEAR**=27

## 1. ADG Status By Band

Operator summary from `adg_gate_results_*.json`.
Tracked records are gate-specific `violation_count` entries: orphan modules, UWG bypass paths, write-inventory paths, etc.
They are backlog records, not guardian exemptions, test failures, or new failures.

| Band | Status | Fix now | Tracked gate records | Read it as | Next move |
|------|:------:|--------:|----------------------|------------|-----------|
| P0 | PASS | 0 | 5 gates / 5,345 tracked records | green; ratchet burn-down/open work remains | work ranked queue; ratchets first |
| P1 | PASS | 0 | 9 gates / 5,972 tracked records | green; ratchet burn-down/open work remains | work ranked queue; ratchets first |
| P2 | PASS | 0 | 3 gates / 2,277 tracked records | green; ratchet burn-down/open work remains | work ranked queue; ratchets first |
| P3 | PASS | 0 | 4 gates / 12,483 tracked records | green; ratchet burn-down/open work remains | work ranked queue; ratchets first |

`Fix now` counts red gates. `Tracked gate records` are non-blocking open work: burn down ratchet floors first, then close non-ratchet rows.

## 2. ADG CI Gates

One row per registered gate.

- **Action** — **FIX** = address now · **TRACK** = backlog, CI OK · **CLEAR** = zero records.
- **Sub** — detail (block / regr / floor / inventory / …); see glossary.
- **Allowed Floor** — zero-tolerance for block gates, baseline for ratchets, advisory/inventory otherwise.
- **Records** — gate-specific `violation_count`; the Signal cell names what kind of record it is.
- **Signal** — what Records count + short Sub note.
- **Next Best Action** — concrete action for this gate (fix / re-baseline / defer / none).

| Gate ID | CI Band | Enforcement | Action | Sub | Records | Allowed Floor | Signal | Next Best Action |
|---------|:-------:|-------------|:------:|:---:|---------:|---------------|--------|------------------|
| `G_REACH_l0_reachability` | P0 | ratchet | TRACK | floor | 2843 | 2843 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: 2843 at floor (baseline 2843); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `L2_lpg_drift_ratchet` | P0 | ratchet | TRACK | floor | 1 | 1 | Counts: Illegal or drifted imports touching L_PG boundary. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | TRACK | floor | 1583 | 1583 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: 1583 at floor (baseline 1583); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `3_write_sovereignty` | P0 | block | TRACK | inventory | 917 | warn inventory | Counts: Non-UWG durable write paths in mv_write_sovereignty_paths (inventory). Sub: 917 warn inventory; not halt-tier. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `J1_canonical_pipeline_wiring` | P0 | block | TRACK | inventory | 1 | warn inventory | Counts: Declared canonical_pipelines.yaml steps missing required call wiring. Sub: 1 subprocess warn. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `10_infra_wiring` | P0 | block | CLEAR | — | 0 | 0 | Counts: Infra wiring defects (canonical pipeline / spine reachability). Sub: No records. | None — gate clean (zero records). |
| `1_critical_path_integrity` | P0 | block | CLEAR | — | 0 | 0 | Counts: Broken or missing links on declared critical execution paths (L0→sink). Sub: No records. | None — gate clean (zero records). |
| `2_authority_boundary` | P0 | block | CLEAR | — | 0 | 0 | Counts: Calls that cross layer authority without UWG/spine sanction. Sub: No records. | None — gate clean (zero records). |
| `4_capability_egress` | P0 | block | CLEAR | — | 0 | 0 | Counts: Outbound provider/SDK calls not leaving through sanctioned adapters. Sub: No records. | None — gate clean (zero records). |
| `5_text_to_action` | P0 | block | CLEAR | — | 0 | 0 | Counts: User text reaching action-class tools without prompt-governance gating. Sub: No records. | None — gate clean (zero records). |
| `6_determinism_provenance` | P0 | block | CLEAR | — | 0 | 0 | Counts: Trace roots missing determinism digest or replay key emission. Sub: No records. | None — gate clean (zero records). |
| `9_executor_theater` | P0 | block | CLEAR | — | 0 | 0 | Counts: Executor-theater signals: import-only or stub execution patterns. Sub: No records. | None — gate clean (zero records). |
| `C1_uwg_bypass_pview` | P0 | block | CLEAR | — | 0 | 0 | Counts: Any row in UWG-bypass materialized view (zero tolerance block). Sub: No records. | None — gate clean (zero records). |
| `C2_l5_bypass_pview` | P0 | block | CLEAR | — | 0 | 0 | Counts: Provider/tool calls skipping L5 gateway (materialized view). Sub: No records. | None — gate clean (zero records). |
| `W5_waiver_expiry` | P0 | block | CLEAR | — | 0 | 0 | Counts: Expired wiring-CI waiver entries in config. Sub: No records. | None — gate clean (zero records). |
| `B2_layer_skip_ratchet` | P1 | ratchet | TRACK | floor | 951 | 951 | Counts: Import edges that skip more than one layer ordinal (layer-hop). Sub: 951 at floor (baseline 951); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C3_silent_writes_ratchet` | P1 | ratchet | TRACK | floor | 2087 | 2087 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: 2087 at floor (baseline 2087); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C4_policy_without_audit_ratchet` | P1 | ratchet | TRACK | floor | 1 | 1 | Counts: controls_flow edges without paired audit/telemetry emission. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `E1_trace_stub_module` | P1 | ratchet | TRACK | floor | 1030 | 1030 | Counts: Modules with high test:production import ratio (trace-theater stub pattern). Sub: 1030 at floor (baseline 1030); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I1_exit_disposition_ratchet` | P1 | ratchet | TRACK | floor | 742 | 742 | Counts: Terminal exit paths not covered in mv_exit_disposition_coverage. Sub: 742 at floor (baseline 742); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `M_taint_actionable_ratchet` | P1 | ratchet | TRACK | floor | 703 | 703 | Counts: Actionable taint surfaces without output schema binding. Sub: 703 at floor (baseline 703); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `N_guardrail_separation_ratchet` | P1 | ratchet | TRACK | floor | 112 | 112 | Counts: L5 guardrail and L3 core-response sharing same write target. Sub: 112 at floor (baseline 112); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `O_tool_call_parity_ratchet` | P1 | ratchet | TRACK | floor | 345 | 345 | Counts: Tool invocations missing observability receipt (Anthropic parity pattern). Sub: 345 at floor (baseline 345); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `P_structured_output_ratchet` | P1 | ratchet | TRACK | floor | 1 | 1 | Counts: generates_prompt at scale without structured output schema. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `11_architecture_witness` | P1 | block | CLEAR | — | 0 | 0 | Counts: Architecture witness Class A/B absence or live-plane write violations. Sub: No records. | None — gate clean (zero records). |
| `12_prompt_assembly_wiring` | P1 | block | CLEAR | — | 0 | 0 | Counts: Prompt-assembly subgraph disconnected from runtime spine. Sub: No records. | None — gate clean (zero records). |
| `7_lifecycle_coverage` | P1 | ratchet | CLEAR | — | 0 | unseeded | Counts: Lifecycle gaps: resources opened without matching close/cleanup. Sub: No records. | None — gate clean (zero records). |
| `8_trace_replay_eval` | P1 | ratchet | CLEAR | — | 0 | unseeded | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: No records. | None — gate clean (zero records). |
| `G2_seam_test_export_coherence` | P1 | block | CLEAR | — | 0 | 0 | Counts: Production seam symbols exported in tests but not in package __all__/exports. Sub: No records. | None — gate clean (zero records). |
| `G_ISLAND_connected_components` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Non-giant connected components on undirected import graph. Sub: No records. | None — gate clean (zero records). |
| `G_WATCHLIST_DELTA_hotspot_regressions` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Graph watchlist items newly FAIL/WARN vs prior run. Sub: No records. | None — gate clean (zero records). |
| `H1_new_orphans_delta_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Modules newly fan_in=0 vs prior snapshot (new orphans). Sub: No records. | None — gate clean (zero records). |
| `H2_fanin_collapse_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Hotspot modules with >30% fan_in drop vs prior snapshot. Sub: No records. | None — gate clean (zero records). |
| `F1_untyped_seam_ratchet` | P2 | ratchet | TRACK | floor | 1075 | 1075 | Counts: Cross-layer imports where target has empty type_surface. Sub: 1075 at floor (baseline 1075); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | TRACK | floor | 1100 | 1100 | Counts: State mutations not consumed by replay surface (gap_flag=1). Sub: 1100 at floor (baseline 1100); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D2_role_duplication_warn` | P2 | warn | TRACK | advis | 102 | advisory | Counts: Role-suffix clusters (_reranker, _planner, …) with fan_in=0 members (advisory). Sub: 102 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `A3_dead_public_symbol_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Public symbols with zero importers (dead surface). Sub: No records. | None — gate clean (zero records). |
| `C5_unresolved_callsites_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: resolves_callsite edges with NULL destination (unresolved callee). Sub: No records. | None — gate clean (zero records). |
| `F2_broken_contract_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Import targets publishing zero exports edges (contract drift). Sub: No records. | None — gate clean (zero records). |
| `H4_mv_staleness_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Total edge count delta >5% vs prior snapshot (graph drift). Sub: No records. | None — gate clean (zero records). |
| `M1_module_loc_ratchet` | P3 | ratchet | TRACK | floor | 459 | 459 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: 459 at floor (baseline 459); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | TRACK | floor | 1083 | 1083 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: 1083 at floor (baseline 1083); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `S4_unused_imports_ratchet` | P3 | ratchet | TRACK | floor | 10938 | 10938 | Counts: Unused import edges in production modules. Sub: 10938 at floor (baseline 10938); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D1_layer_doc_binding` | P3 | warn | TRACK | advis | 3 | advisory | Counts: Layer folders missing or mismatched LAYER.md binding (advisory). Sub: 3 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `E3_trace_theater_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Emit-symbol density per layer vs imports (KPI advisory). Sub: No records. | None — gate clean (zero records). |
| `F3_missing_adapter_warn` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Protocol/ABC/Interface with zero implements edges (advisory). Sub: No records. | None — gate clean (zero records). |
| `H3_ap_velocity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Antipattern edge density per 1k LOC (KPI advisory). Sub: No records. | None — gate clean (zero records). |
| `K1_churn_complexity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: High churn×complexity files (KPI advisory, jsonl sink). Sub: No records. | None — gate clean (zero records). |

### Track later (Verdict TRACK — CI OK, backlog remains)

| Gate ID | Sub | Records |
|---------|:---:|---------:|
| `S4_unused_imports_ratchet` | floor | 10938 |
| `G_REACH_l0_reachability` | floor | 2843 |
| `C3_silent_writes_ratchet` | floor | 2087 |
| `S2_uwg_bypass_ratchet` | floor | 1583 |
| `I2_replay_surface_gaps_ratchet` | floor | 1100 |
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
Use this section for guardian math, not the status table above.
`gross` = raw violations found. `guardian` = guardian-exempted (still counted).
`net` = `gross - guardian`. `diff` = delta vs prior snapshot baseline.

| Severity Band | Label | Gross | Guardian | Net | Diff vs prev |
|---------------|-------|------:|---------:|----:|-------------:|
| P0 | layer_violations | 46 | 41 | 5 | +41 |
| P1 | anti_patterns_high | 1197 | 1193 | 4 | +1193 |
| P2 | anti_patterns_medium | 752 | 731 | 21 | +731 |
| P3 | style_warnings | 20160 | 92 | 20068 | +92 |

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
| block_pass | 14 | Block-class gates that did not halt the run (exit 0). Records may be non-zero. |
| block_fail | 0 | Block-class gates that halted the run — clear the gate blocking condition. |
| ratchet_pass | 27 | Ratchet-class gates within their baseline ceiling. |
| ratchet_regressed | 0 | Ratchet-class gates with NEW records beyond baseline. |
| ratchet_seed_missing | 0 | Ratchet-class gates without a baseline seed (first run). |
| warn | 6 | Advisory-class gates (do not gate the run). |

### Per-gate verdict rollup (this report)

| Verdict | Gates | Meaning |
|---------|------:|---------|
| TRACK | 21 | CI passed this gate; records are tracked backlog — plan hygiene, not a halt. |
| CLEAR | 27 | Zero records; nothing to do on this gate. |

## 5. Fix now (detail)

_No FIX gates._

---
## Next action

- **Queue:** `artifacts\adg\adg_action_queue_06132026_1643.json`
- **emit_status:** `ok`
- **degraded:** `False`
- **summary:** FIX=0 · TRACK=21 · actions_emitted=9

| Rank | Lane | Kind | Target | ordering_reason | Signal |
|-----:|------|------|--------|-----------------|--------|
| 1 | GRAPHDB | test_hotspot_gap | `apps_rg/runtime/sections/executive_summary_lane.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (absent); critical... |
| 2 | GRAPHDB | test_hotspot_gap | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (0.0%); criticalit... |
| 3 | GRAPHDB | test_hotspot_gap | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (0.0%); criticalit... |
| 4 | REFACTOR | refactor_candidate | `agentic_core/adg/extraction/static_scanner.py` | refactor_accelerator_candidates_desc | Refactor candidate; score=0.2521 |
| 5 | REFACTOR | refactor_candidate | `agentic_core/base_agents/SovereignBaseAgent.py` | refactor_accelerator_candidates_desc | Refactor candidate; score=0.1245 |

CLI: `python tools/reports/adg_action_queue.py --latest --top 10 --format markdown`

---
Report renderer: `tools/reports/adg_burndown_report.py`. Re-run with `python tools/reports/adg_burndown_report.py --out artifacts/adg/adg_burndown_report.md`.
