# ADG CI Burndown Report

- **Generated:** 2026-07-05T03:17:40+00:00
- **Gate-results source:** `artifacts\adg\adg_gate_results_20260705_031510.json`
- **Burndown source:** `artifacts\adg\adg_burndown_table_07042026_2305.json`
- **Snapshot timestamp:** 2026-07-05T03:15:10.316617+00:00
- **Total gates:** 49
- **Overall verdict:** **PASS** (run halt — exit code)

### BCG Burndown Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Business read:** ADG is PASS with tracked backlog: burn down accepted debt after green.
- **ADG verdict:** PASS
- **Technical evidence:**
  - Snapshot timestamp: 2026-07-05T03:15:10.316617+00:00
  - Total gates: 49
  - FIX gates: 0
  - Burn-down gates: 15
  - KPI/watchlist gates: 5
  - CLEAR gates: 29
  - block_fail=0; ratchet_regressed=0
- **Priority rule:** FIX gates first, then owned burn-down backlog, then KPI/watchlist trends outside the work queue.

Fix now:

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Burn down C3_silent_writes_ratchet | This is accepted or advisory debt; reduce it after FIX rows are clear. | Burn-down gate; rows=2063; sub=floor. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| 2 | Burn down S2_uwg_bypass_ratchet | This is accepted or advisory debt; reduce it after FIX rows are clear. | Burn-down gate; rows=1609; sub=floor. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| 3 | Burn down G_REACH_l0_reachability | This is accepted or advisory debt; reduce it after FIX rows are clear. | Burn-down gate; rows=1453; sub=floor. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| 4 | Burn down I2_replay_surface_gaps_ratchet | This is accepted or advisory debt; reduce it after FIX rows are clear. | Burn-down gate; rows=995; sub=floor. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |

Next step: Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI.
- **Action:** **FIX**=0 (address for green ADG) · **BURN**=15 (owned backlog) · **KPI**=5 (watchlist only) · **CLEAR**=29

## 1. ADG Status By Band

Operator summary from `adg_gate_results_*.json`.
Burn-down rows come from the BCG adapter priority queue; KPI/watchlist rows stay visible but do not imply cleanup work.

| Band | Status | Fix now | Burn-down backlog | KPI / watchlist | Read it as | Next move |
|------|:------:|--------:|-------------------|-----------------|------------|-----------|
| P0 | PASS | 0 | 4 gates / 3,827 rows | 0 gates / 0 rows | green; tracked backlog | work ranked queue; do not treat as new failures |
| P1 | PASS | 0 | 9 gates / 5,583 rows | 0 gates / 0 rows | green; tracked backlog | work ranked queue; do not treat as new failures |
| P2 | PASS | 0 | 2 gates / 1,977 rows | 1 gate / 105 rows | green; tracked backlog | work ranked queue; do not treat as new failures |
| P3 | PASS | 0 | 0 gates / 0 rows | 4 gates / 12,454 rows | green; KPI/watchlist only | watch trend; no burn-down action |

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
| `G_REACH_l0_reachability` | P0 | ratchet | BURN | floor | 1453 | 1453 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: 1453 at floor (baseline 1453); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | BURN | floor | 1609 | 1609 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: 1609 at floor (baseline 1609); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `3_write_sovereignty` | P0 | block | BURN | inventory | 764 | warn inventory | Counts: Non-UWG durable write paths in mv_write_sovereignty_paths (inventory). Sub: 764 warn inventory; not halt-tier. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `J1_canonical_pipeline_wiring` | P0 | block | BURN | inventory | 1 | warn inventory | Counts: Declared canonical_pipelines.yaml steps missing required call wiring. Sub: 1 subprocess warn. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `10_infra_wiring` | P0 | block | CLEAR | — | 0 | 0 | Counts: Infra wiring defects (canonical pipeline / spine reachability). Sub: No rows. | None — gate clean (zero rows). |
| `13_core_imports_apps` | P0 | block | CLEAR | — | 0 | 0 | Counts: Core Imports Apps (auto-derived from gate_class) Sub: No rows. | None — gate clean (zero rows). |
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
| `C3_silent_writes_ratchet` | P1 | ratchet | BURN | floor | 2063 | 2063 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: 2063 at floor (baseline 2063); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C4_policy_without_audit_ratchet` | P1 | ratchet | BURN | floor | 1 | 1 | Counts: controls_flow edges without paired audit/telemetry emission. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `E1_trace_stub_module` | P1 | ratchet | BURN | floor | 982 | 982 | Counts: Modules with high test:production import ratio (trace-theater stub pattern). Sub: 982 at floor (baseline 982); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I1_exit_disposition_ratchet` | P1 | ratchet | BURN | floor | 695 | 695 | Counts: Terminal exit paths not covered in mv_exit_disposition_coverage. Sub: 695 at floor (baseline 695); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `M_taint_actionable_ratchet` | P1 | ratchet | BURN | floor | 685 | 685 | Counts: Actionable taint surfaces without output schema binding. Sub: 685 at floor (baseline 685); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
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
| `F1_untyped_seam_ratchet` | P2 | ratchet | BURN | floor | 982 | 982 | Counts: Cross-layer imports where target has empty type_surface. Sub: 982 at floor (baseline 982); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | BURN | floor | 995 | 995 | Counts: State mutations not consumed by replay surface (gap_flag=1). Sub: 995 at floor (baseline 995); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D2_role_duplication_warn` | P2 | warn | KPI | advis | 105 | advisory | Counts: Role-suffix clusters (_reranker, _planner, …) with fan_in=0 members (advisory). Sub: 105 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `A3_dead_public_symbol_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Public symbols with zero importers (dead surface). Sub: No rows. | None — gate clean (zero rows). |
| `C5_unresolved_callsites_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: resolves_callsite edges with NULL destination (unresolved callee). Sub: No rows. | None — gate clean (zero rows). |
| `F2_broken_contract_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Import targets publishing zero exports edges (contract drift). Sub: No rows. | None — gate clean (zero rows). |
| `H4_mv_staleness_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Total edge count delta >5% vs prior snapshot (graph drift). Sub: No rows. | None — gate clean (zero rows). |
| `M1_module_loc_ratchet` | P3 | ratchet | KPI | floor | 468 | 468 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: 468 at floor (baseline 468); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | KPI | floor | 1188 | 1188 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: 1188 at floor (baseline 1188); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `S4_unused_imports_ratchet` | P3 | ratchet | KPI | floor | 10795 | 10795 | Counts: Unused import edges in production modules. Sub: 10795 at floor (baseline 10795); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D1_layer_doc_binding` | P3 | warn | KPI | advis | 3 | advisory | Counts: Layer folders missing or mismatched LAYER.md binding (advisory). Sub: 3 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `E3_trace_theater_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Emit-symbol density per layer vs imports (KPI advisory). Sub: No rows. | None — gate clean (zero rows). |
| `F3_missing_adapter_warn` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Protocol/ABC/Interface with zero implements edges (advisory). Sub: No rows. | None — gate clean (zero rows). |
| `H3_ap_velocity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Antipattern edge density per 1k LOC (KPI advisory). Sub: No rows. | None — gate clean (zero rows). |
| `K1_churn_complexity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: High churn×complexity files (KPI advisory, jsonl sink). Sub: No rows. | None — gate clean (zero rows). |

### Burn down later (owned backlog — CI OK)

| Gate ID | Sub | Rows |
|---------|:---:|---------:|
| `C3_silent_writes_ratchet` | floor | 2063 |
| `S2_uwg_bypass_ratchet` | floor | 1609 |
| `G_REACH_l0_reachability` | floor | 1453 |
| `I2_replay_surface_gaps_ratchet` | floor | 995 |
| `E1_trace_stub_module` | floor | 982 |
| `F1_untyped_seam_ratchet` | floor | 982 |
| `B2_layer_skip_ratchet` | floor | 862 |
| `3_write_sovereignty` | inventory | 764 |
| `I1_exit_disposition_ratchet` | floor | 695 |
| `M_taint_actionable_ratchet` | floor | 685 |
| `O_tool_call_parity_ratchet` | floor | 206 |
| `N_guardrail_separation_ratchet` | floor | 88 |
| `C4_policy_without_audit_ratchet` | floor | 1 |
| `J1_canonical_pipeline_wiring` | inventory | 1 |
| `P_structured_output_ratchet` | floor | 1 |

## 3. KPI / Watchlist Signals

These rows are visible for trend awareness, but they are not burn-down work unless a plan gives them an owner, target, and retirement condition.

| Gate ID | Band | Rows | Why it is separate | Next step |
|---------|:----:|-----:|--------------------|-----------|
| `S4_unused_imports_ratchet` | P3 | 10795 | KPI/watchlist signal, not an owned burn-down item. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | 1188 | KPI/watchlist signal, not an owned burn-down item. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `M1_module_loc_ratchet` | P3 | 468 | KPI/watchlist signal, not an owned burn-down item. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
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
| P0 | layer_violations | 35 | 32 | 3 | +32 |
| P1 | anti_patterns_high | 1147 | 1143 | 4 | +1143 |
| P2 | anti_patterns_medium | 747 | 716 | 31 | +716 |
| P3 | style_warnings | 19279 | 87 | 19192 | +87 |

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
| block_pass | 15 | Block-class gates that did not halt the run (exit 0). Rows may be non-zero. |
| block_fail | 0 | Block-class gates that halted the run — clear the gate blocking condition. |
| ratchet_pass | 27 | Ratchet-class gates within their baseline ceiling. |
| ratchet_regressed | 0 | Ratchet-class gates with NEW rows beyond baseline. |
| ratchet_seed_missing | 0 | Ratchet-class gates without a baseline seed (first run). |
| warn | 6 | Advisory-class gates (do not gate the run). |

### Per-gate verdict rollup (this report)

| Verdict | Gates | Meaning |
|---------|------:|---------|
| TRACK | 20 | CI passed this gate; rows are backlog — plan hygiene, not a halt. |
| CLEAR | 29 | Zero rows; nothing to do on this gate. |

## 6. Fix now (detail)

_No FIX gates._

---
## Next action

- **Queue:** `artifacts\adg\adg_action_queue_07042026_2305.json`
- **emit_status:** `ok`
- **degraded:** `False`
- **summary:** FIX=0 · TRACK=20 · actions_emitted=9

| Rank | Lane | Kind | Target | ordering_reason | Signal |
|-----:|------|------|--------|-----------------|--------|
| 1 | GRAPHDB | test_hotspot_gap | `agentic_core/L5_safety/contracts/registry.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (absent); critical... |
| 2 | GRAPHDB | test_hotspot_gap | `apps_rg/runtime/sections/executive_summary_lane.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (absent); critical... |
| 3 | GRAPHDB | test_hotspot_gap | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | mv_hotspot_coverage_risk_priority | Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT; risk=CRITICAL; coverage=ABSENT (absent); critical... |
| 4 | REFACTOR | refactor_candidate | `apps_rg/runtime/validators/executive_summary_x2.py` | refactor_accelerator_candidates_desc | Refactor candidate; score=0.0858 |
| 5 | REFACTOR | refactor_candidate | `agentic_core/L0_routing/config/path_constants.py` | refactor_accelerator_candidates_desc | Refactor candidate; score=0.0666 |

CLI: `python tools/reports/adg_action_queue.py --latest --top 10 --format markdown`

---
Report renderer: `tools/reports/adg_burndown_report.py`. Re-run with `python tools/reports/adg_burndown_report.py --out artifacts/adg/adg_burndown_report.md`.
