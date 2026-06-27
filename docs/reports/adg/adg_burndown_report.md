# ADG CI Burndown Report

- **Generated:** 2026-06-27T09:17:32+00:00
- **Gate-results source:** `artifacts\adg\adg_gate_results_20260627_091354.json`
- **Burndown source:** `artifacts\adg\adg_burndown_table.json`
- **Snapshot timestamp:** 2026-06-27T09:13:54.310304+00:00
- **Total gates:** 48
- **Overall verdict:** **BLOCKED** (run halt — exit code)

### BCG Burndown Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **ADG verdict:** BLOCKED
- **Business read:** ADG is BLOCKED: fix the red gates before treating the run as green.
- **Technical evidence:**
  - Snapshot timestamp: 2026-06-27T09:13:54.310304+00:00
  - Total gates: 48
  - FIX gates: 1
  - TRACK gates: 19
  - CLEAR gates: 28
  - block_fail=0; ratchet_regressed=1
- **Priority rule:** FIX gates first, then TRACK ratchets/backlog, then no-action CLEAR gates.

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Fix G_REACH_l0_reachability | This gate is marked FIX, so the ADG run is not decision-grade green until it clears. | P0 ratchet gate; rows=2800; sub=regr. | Regression +14 over baseline 2786 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |

Next step: Regression +14 over baseline 2786 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off.
- **Action:** **FIX**=1 (address for green ADG) · **TRACK**=19 (CI OK, backlog) · **CLEAR**=28

## 1. ADG Status By Band

Operator summary from `adg_gate_results_*.json`.
Backlog rows are summed only from TRACK gate `violation_count`; guardian gross/net math is only in Severity Inventory.

| Band | Status | Fix now | Tracked backlog | Read it as | Next move |
|------|:------:|--------:|-----------------|------------|-----------|
| P0 | BLOCKED | 1 | 3 gates / 2,304 rows | red gates present | fix red gates first |
| P1 | PASS | 0 | 9 gates / 5,558 rows | green; tracked backlog | work ranked queue; do not treat as new failures |
| P2 | PASS | 0 | 3 gates / 2,085 rows | green; tracked backlog | work ranked queue; do not treat as new failures |
| P3 | PASS | 0 | 4 gates / 12,359 rows | green; tracked backlog | work ranked queue; do not treat as new failures |

`Fix now` counts red gates. `Tracked backlog` is old or advisory inventory that does not block this run.

## 2. ADG CI Gates

One row per registered gate.

- **Action** — **FIX** = address now · **TRACK** = backlog, CI OK · **CLEAR** = zero rows.
- **Sub** — detail (block / regr / floor / inventory / …); see glossary.
- **Allowed Floor** — zero-tolerance for block gates, baseline for ratchets, advisory/inventory otherwise.
- **Rows** — gate-specific `violation_count`; meaning depends on Action/Sub.
- **Signal** — what Rows count + short Sub note.
- **Next Best Action** — concrete action for this gate (fix / re-baseline / defer / none).

| Gate ID | CI Band | Enforcement | Action | Sub | Rows | Allowed Floor | Signal | Next Best Action |
|---------|:-------:|-------------|:------:|:---:|---------:|---------------|--------|------------------|
| `G_REACH_l0_reachability` | P0 | ratchet | FIX | regr | 2800 | 2786 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: +14 vs baseline 2786. | Regression +14 over baseline 2786 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | TRACK | floor | 1571 | 1571 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: 1571 at floor (baseline 1571); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `3_write_sovereignty` | P0 | block | TRACK | inventory | 732 | warn inventory | Counts: Non-UWG durable write paths in mv_write_sovereignty_paths (inventory). Sub: 732 warn inventory; not halt-tier. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `J1_canonical_pipeline_wiring` | P0 | block | TRACK | inventory | 1 | warn inventory | Counts: Declared canonical_pipelines.yaml steps missing required call wiring. Sub: 1 subprocess warn. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
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
| `B2_layer_skip_ratchet` | P1 | ratchet | TRACK | floor | 874 | 874 | Counts: Import edges that skip more than one layer ordinal (layer-hop). Sub: 874 at floor (baseline 874); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C3_silent_writes_ratchet` | P1 | ratchet | TRACK | floor | 2034 | 2034 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: 2034 at floor (baseline 2034); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C4_policy_without_audit_ratchet` | P1 | ratchet | TRACK | floor | 1 | 1 | Counts: controls_flow edges without paired audit/telemetry emission. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `E1_trace_stub_module` | P1 | ratchet | TRACK | floor | 982 | 982 | Counts: Modules with high test:production import ratio (trace-theater stub pattern). Sub: 982 at floor (baseline 982); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I1_exit_disposition_ratchet` | P1 | ratchet | TRACK | floor | 695 | 695 | Counts: Terminal exit paths not covered in mv_exit_disposition_coverage. Sub: 695 at floor (baseline 695); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `M_taint_actionable_ratchet` | P1 | ratchet | TRACK | floor | 676 | 676 | Counts: Actionable taint surfaces without output schema binding. Sub: 676 at floor (baseline 676); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `N_guardrail_separation_ratchet` | P1 | ratchet | TRACK | floor | 90 | 90 | Counts: L5 guardrail and L3 core-response sharing same write target. Sub: 90 at floor (baseline 90); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `O_tool_call_parity_ratchet` | P1 | ratchet | TRACK | floor | 205 | 205 | Counts: Tool invocations missing observability receipt (Anthropic parity pattern). Sub: 205 at floor (baseline 205); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `P_structured_output_ratchet` | P1 | ratchet | TRACK | floor | 1 | 1 | Counts: generates_prompt at scale without structured output schema. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `11_architecture_witness` | P1 | block | CLEAR | — | 0 | 0 | Counts: Architecture witness Class A/B absence or live-plane write violations. Sub: No rows. | None — gate clean (zero rows). |
| `12_prompt_assembly_wiring` | P1 | block | CLEAR | — | 0 | 0 | Counts: Prompt-assembly subgraph disconnected from runtime spine. Sub: No rows. | None — gate clean (zero rows). |
| `7_lifecycle_coverage` | P1 | ratchet | CLEAR | — | 0 | unseeded | Counts: Lifecycle gaps: resources opened without matching close/cleanup. Sub: No rows. | None — gate clean (zero rows). |
| `8_trace_replay_eval` | P1 | ratchet | CLEAR | — | 0 | unseeded | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: No rows. | None — gate clean (zero rows). |
| `G2_seam_test_export_coherence` | P1 | block | CLEAR | — | 0 | 0 | Counts: Production seam symbols exported in tests but not in package __all__/exports. Sub: No rows. | None — gate clean (zero rows). |
| `G_ISLAND_connected_components` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Non-giant connected components on undirected import graph. Sub: No rows. | None — gate clean (zero rows). |
| `G_WATCHLIST_DELTA_hotspot_regressions` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Graph watchlist items newly FAIL/WARN vs prior run. Sub: No rows. | None — gate clean (zero rows). |
| `H1_new_orphans_delta_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Modules newly fan_in=0 vs prior snapshot (new orphans). Sub: No rows. | None — gate clean (zero rows). |
| `H2_fanin_collapse_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Hotspot modules with >30% fan_in drop vs prior snapshot. Sub: No rows. | None — gate clean (zero rows). |
| `F1_untyped_seam_ratchet` | P2 | ratchet | TRACK | floor | 991 | 991 | Counts: Cross-layer imports where target has empty type_surface. Sub: 991 at floor (baseline 991); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | TRACK | floor | 989 | 989 | Counts: State mutations not consumed by replay surface (gap_flag=1). Sub: 989 at floor (baseline 989); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D2_role_duplication_warn` | P2 | warn | TRACK | advis | 105 | advisory | Counts: Role-suffix clusters (_reranker, _planner, …) with fan_in=0 members (advisory). Sub: 105 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `A3_dead_public_symbol_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Public symbols with zero importers (dead surface). Sub: No rows. | None — gate clean (zero rows). |
| `C5_unresolved_callsites_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: resolves_callsite edges with NULL destination (unresolved callee). Sub: No rows. | None — gate clean (zero rows). |
| `F2_broken_contract_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Import targets publishing zero exports edges (contract drift). Sub: No rows. | None — gate clean (zero rows). |
| `H4_mv_staleness_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Total edge count delta >5% vs prior snapshot (graph drift). Sub: No rows. | None — gate clean (zero rows). |
| `M1_module_loc_ratchet` | P3 | ratchet | TRACK | floor | 458 | 458 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: 458 at floor (baseline 458); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | TRACK | floor | 1148 | 1148 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: 1148 at floor (baseline 1148); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `S4_unused_imports_ratchet` | P3 | ratchet | TRACK | floor | 10750 | 10750 | Counts: Unused import edges in production modules. Sub: 10750 at floor (baseline 10750); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D1_layer_doc_binding` | P3 | warn | TRACK | advis | 3 | advisory | Counts: Layer folders missing or mismatched LAYER.md binding (advisory). Sub: 3 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `E3_trace_theater_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Emit-symbol density per layer vs imports (KPI advisory). Sub: No rows. | None — gate clean (zero rows). |
| `F3_missing_adapter_warn` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Protocol/ABC/Interface with zero implements edges (advisory). Sub: No rows. | None — gate clean (zero rows). |
| `H3_ap_velocity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Antipattern edge density per 1k LOC (KPI advisory). Sub: No rows. | None — gate clean (zero rows). |
| `K1_churn_complexity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: High churn×complexity files (KPI advisory, jsonl sink). Sub: No rows. | None — gate clean (zero rows). |

### Fix now (Verdict FIX)

| Gate ID | Sub | Rows |
|---------|:---:|---------:|
| `G_REACH_l0_reachability` | regr | 2800 |

### Track later (Verdict TRACK — CI OK, backlog remains)

| Gate ID | Sub | Rows |
|---------|:---:|---------:|
| `S4_unused_imports_ratchet` | floor | 10750 |
| `C3_silent_writes_ratchet` | floor | 2034 |
| `S2_uwg_bypass_ratchet` | floor | 1571 |
| `Q2_cyclomatic_complexity_ratchet` | floor | 1148 |
| `F1_untyped_seam_ratchet` | floor | 991 |
| `I2_replay_surface_gaps_ratchet` | floor | 989 |
| `E1_trace_stub_module` | floor | 982 |
| `B2_layer_skip_ratchet` | floor | 874 |
| `3_write_sovereignty` | inventory | 732 |
| `I1_exit_disposition_ratchet` | floor | 695 |
| `M_taint_actionable_ratchet` | floor | 676 |
| `M1_module_loc_ratchet` | floor | 458 |
| `O_tool_call_parity_ratchet` | floor | 205 |
| `D2_role_duplication_warn` | advis | 105 |
| `N_guardrail_separation_ratchet` | floor | 90 |
| `D1_layer_doc_binding` | advis | 3 |
| `C4_policy_without_audit_ratchet` | floor | 1 |
| `J1_canonical_pipeline_wiring` | inventory | 1 |
| `P_structured_output_ratchet` | floor | 1 |

## 3. Severity Inventory Burndown

Counts come from the canonical `adg_burndown_table.json` (schema 2.2).
This is raw MV defect inventory by severity/source band; it is not one row per CI gate.
Use this section for guardian math, not the status table above.
`gross` = raw violations found. `guardian` = guardian-exempted (still counted).
`net` = `gross - guardian`. `diff` = delta vs prior snapshot baseline.

| Severity Band | Label | Gross | Guardian | Net | Diff vs prev |
|---------------|-------|------:|---------:|----:|-------------:|
| P0 | layer_violations | 43 | 40 | 3 | +40 |
| P1 | anti_patterns_high | 1151 | 1146 | 5 | +1146 |
| P2 | anti_patterns_medium | 733 | 714 | 19 | +714 |
| P3 | style_warnings | 19065 | 87 | 18978 | +87 |

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
| block_pass | 14 | Block-class gates that did not halt the run (exit 0). Rows may be non-zero. |
| block_fail | 0 | Block-class gates that halted the run — clear the gate blocking condition. |
| ratchet_pass | 26 | Ratchet-class gates within their baseline ceiling. |
| ratchet_regressed | 1 | Ratchet-class gates with NEW rows beyond baseline. |
| ratchet_seed_missing | 0 | Ratchet-class gates without a baseline seed (first run). |
| warn | 6 | Advisory-class gates (do not gate the run). |

### Per-gate verdict rollup (this report)

| Verdict | Gates | Meaning |
|---------|------:|---------|
| FIX | 1 | Address before treating ADG as green (gate blocked or ratchet regressed). |
| TRACK | 19 | CI passed this gate; rows are backlog — plan hygiene, not a halt. |
| CLEAR | 28 | Zero rows; nothing to do on this gate. |

## 5. Fix now (detail)

| Gate | Band | Enf | Sub | Rows | Signal |
|------|:----:|:---:|:---:|---------:|--------|
| `G_REACH_l0_reachability` | P0 | ratchet | regr | 2800 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: +14 vs baseline 2786. |

---
## Next action

- **Queue:** `artifacts\adg\adg_action_queue_06272026_0458.json`
- **emit_status:** `ok`
- **degraded:** `False`
- **summary:** FIX=1 · TRACK=19 · actions_emitted=10

| Rank | Lane | Kind | Target | ordering_reason | Signal |
|-----:|------|------|--------|-----------------|--------|
| 1 | FIX | fix_gate | `G_REACH_l0_reachability` | fix_regr_p0_delta_asc | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: +14 vs baseline 2786. |
| 2 | GRAPHDB | test_hotspot_gap | `apps_rg/runtime/sections/executive_summary_lane.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (absent); critical... |
| 3 | GRAPHDB | test_hotspot_gap | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (0.0%); criticalit... |
| 4 | GRAPHDB | test_hotspot_gap | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (0.0%); criticalit... |
| 5 | REFACTOR | refactor_candidate | `agentic_core/adg/extraction/static_scanner.py` | refactor_accelerator_candidates_desc | Refactor candidate; score=0.1371 |

CLI: `python tools/reports/adg_action_queue.py --latest --top 10 --format markdown`

---
Report renderer: `tools/reports/adg_burndown_report.py`. Re-run with `python tools/reports/adg_burndown_report.py --out artifacts/adg/adg_burndown_report.md`.
