# ADG CI Burndown Report

- **Generated:** 2026-06-15T10:54:39+00:00
- **Gate-results source:** `artifacts\adg\adg_gate_results_20260615_105116.json`
- **Burndown source:** `artifacts\adg\adg_burndown_table.json`
- **Snapshot timestamp:** 2026-06-15T10:51:16.536117+00:00
- **Total gates:** 48
- **Overall verdict:** **BLOCKED** (run halt — exit code)
- **Action:** **FIX**=6 (address for green ADG) · **TRACK**=17 (CI OK, backlog) · **CLEAR**=25

## 1. ADG Heuristic Attack Order

Rule: work class first (Fix now > ratchets > open work > severity audit), then P-band (P0 > P1 > P2 > P3), then record count within the same class and band.

| # | Attack | Band | Records | Why | Next step |
|--:|--------|------|--------:|-----|-----------|
| 1 | Fix now: P0 CI blockers | P0 | 2,852 | CI blocker; ADG is not green until this clears. | Fix the blocking gate condition and rerun ADG before burn-down work. |
| 2 | Fix now: P1 CI blockers | P1 | 15 | CI blocker; ADG is not green until this clears. | Fix the blocking gate condition and rerun ADG before burn-down work. |
| 3 | Fix now: P3 CI blockers | P3 | 1,548 | CI blocker; ADG is not green until this clears. | Fix the blocking gate condition and rerun ADG before burn-down work. |
| 4 | Burn down ratchets: `S2_UWG` 1,541 | P0 | 1,541 | Ratchet floor work lowers accepted baseline debt; P-band outranks raw size. | Use the P0 Action Plan below. |
| 5 | Burn down ratchets: `C3_silent_writes` 1,992; `E1_trace_stub` 1,030; `B2_layer_skip` 951; +6 more = 5,714 total | P1 | 5,714 | Ratchet floor work lowers accepted baseline debt; P-band outranks raw size. | Open a burn-down slice for the listed ratchets, rerun ADG, then absorb the lower baseline. |
| 6 | Burn down ratchets: `F1_untyped_seam` 1,075; `I2_replay_gaps` 993 | P2 | 2,068 | Ratchet floor work lowers accepted baseline debt; P-band outranks raw size. | Open a burn-down slice for the listed ratchets, rerun ADG, then absorb the lower baseline. |
| 7 | Burn down ratchets: `S4_unused_imports` 10,841 | P3 | 10,841 | Ratchet floor work lowers accepted baseline debt; P-band outranks raw size. | Open a burn-down slice for the listed ratchets, rerun ADG, then absorb the lower baseline. |
| 8 | Open non-ratchet work: `write_sovereignty` 933; `pipeline_wiring` 1 | P0 | 934 | Real open work, but it does not lower a ratchet floor or block CI. | Schedule after ratchets unless the item is tiny, already in hand, or high-leverage. |
| 9 | Open non-ratchet work: `D2_role_duplication` 102 | P2 | 102 | Real open work, but it does not lower a ratchet floor or block CI. | Schedule after ratchets unless the item is tiny, already in hand, or high-leverage. |
| 10 | Open non-ratchet work: `D1_layer_doc` 3 | P3 | 3 | Real open work, but it does not lower a ratchet floor or block CI. | Schedule after ratchets unless the item is tiny, already in hand, or high-leverage. |
| 11 | Severity audit: 5 non-exempt from 47 gross | P0 | 5 | Review-only audit signal; not Fix now unless it maps to a failing gate. | Audit or map to a gate; do not treat as a CI blocker by itself. |
| 12 | Severity audit: 4 non-exempt from 1,199 gross | P1 | 4 | Review-only audit signal; not Fix now unless it maps to a failing gate. | Audit or map to a gate; do not treat as a CI blocker by itself. |
| 13 | Severity audit: 22 non-exempt from 745 gross | P2 | 22 | Review-only audit signal; not Fix now unless it maps to a failing gate. | Audit or map to a gate; do not treat as a CI blocker by itself. |
| 14 | Severity audit: 18,878 non-exempt from 18,970 gross | P3 | 18,878 | Review-only audit signal; not Fix now unless it maps to a failing gate. | Audit or map to a gate; do not treat as a CI blocker by itself. |

Comments:
- Non-exempt severity rows are included for review, but they do not populate Fix now unless a gate is failing.
- Record count breaks ties inside the same work class and P-band; it does not make P3 outrank P0.
- When the top row is P0 ratchets, use the P0 Action Plan for the exact gate order.

## 2. P0 Action Plan

Read this table top to bottom. It is the action surface; the band table below is status context.

| # | Work | Gate | Records | Why this priority | Next step |
|--:|------|------|--------:|-------------------|-----------|
| 1 | Fix now | `G_REACH` | 2,850 | Blocks green ADG; fix before burn-down work. | Fix the gate condition and rerun ADG before treating the run as green. |
| 2 | Fix now | `L2_LPG` | 2 | Blocks green ADG; fix before burn-down work. | Fix the gate condition and rerun ADG before treating the run as green. |
| 3 | Burn down ratchet | `S2_UWG` | 1,541 | Largest P0 ratchet floor; reduces the biggest accepted baseline first. | Open a burn-down slice for this gate, reduce records, rerun ADG, then absorb the lower baseline. |
| 4 | Open non-ratchet work | `write_sovereignty` | 933 | Real open P0 work, but it does not reduce the ratchet floor. | Schedule after P0 ratchets unless the fix is tiny, already in hand, or high-leverage. |
| 5 | Open non-ratchet work | `pipeline_wiring` | 1 | Small open P0 work item; bundle if it is already in the same files. | Close when touching nearby code; it is open work but not ratchet burn-down. |

Comments:
- If Fix now rows exist, they override ratchets because ADG is not green.
- With Fix now = 0, P0 ratchets are sorted by tracked records so the largest accepted floor burns down first.
- Open non-ratchet work is still real work; it is second because it does not lower the P0 ratchet floor.
- Guardian/non-exempt severity counts are an exception audit and should not reorder this P0 work list.

## 3. ADG Status By Band

Operator summary from `adg_gate_results_*.json`.
Records are gate-specific `violation_count` entries: orphan modules, UWG bypass paths, write-inventory paths, etc.
FIX records are current red-gate work. Ratchet floor and open non-ratchet records are non-blocking backlog context.

| Band | Status | Fix gates | Fix records | Ratchet floor | Open non-ratchet | Read it as | Next move |
|------|:------:|----------:|------------:|--------------:|------------------:|------------|-----------|
| P0 | BLOCKED | 2 | 2,852 | 1,541 | 934 | red gates present | fix red gates first |
| P1 | BLOCKED | 2 | 15 | 5,714 | 0 | red gates present | fix red gates first |
| P2 | PASS | 0 | 0 | 2,068 | 102 | green; ratchet burn-down/open work remains | work ranked queue; ratchets first |
| P3 | BLOCKED | 2 | 1,548 | 10,841 | 3 | red gates present | fix red gates first |

`Fix gates` counts red gates. `Fix records` are current blockers/regressions. `Ratchet floor` is accepted baseline debt; `Open non-ratchet` is non-blocking work.

## 4. ADG CI Gates

One row per registered gate.

- **Action** — **FIX** = address now · **TRACK** = backlog, CI OK · **CLEAR** = zero records.
- **Sub** — detail (block / regr / floor / inventory / …); see glossary.
- **Allowed Floor** — zero-tolerance for block gates, baseline for ratchets, advisory/inventory otherwise.
- **Records** — gate-specific `violation_count`; the Signal cell names what kind of record it is.
- **Signal** — what Records count + short Sub note.
- **Next Best Action** — concrete action for this gate (fix / re-baseline / defer / none).

| Gate ID | CI Band | Enforcement | Action | Sub | Records | Allowed Floor | Signal | Next Best Action |
|---------|:-------:|-------------|:------:|:---:|---------:|---------------|--------|------------------|
| `G_REACH_l0_reachability` | P0 | ratchet | FIX | regr | 2850 | 2843 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: +7 vs baseline 2843. | Regression +7 over baseline 2843 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| `L2_lpg_drift_ratchet` | P0 | ratchet | FIX | regr | 2 | 1 | Counts: Illegal or drifted imports touching L_PG boundary. Sub: +1 vs baseline 1. | Regression +1 over baseline 1 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | TRACK | floor | 1541 | 1541 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: 1541 at floor (baseline 1541); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `3_write_sovereignty` | P0 | block | TRACK | inventory | 933 | warn inventory | Counts: Non-UWG durable write paths in mv_write_sovereignty_paths (inventory). Sub: 933 warn inventory; not halt-tier. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
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
| `8_trace_replay_eval` | P1 | ratchet | FIX | regr | 5 | unseeded | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: Above ratchet baseline. | Regression +N over baseline None: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `H1_new_orphans_delta_ratchet` | P1 | ratchet | FIX | regr | 10 | 0 | Counts: Modules newly fan_in=0 vs prior snapshot (new orphans). Sub: +10 vs baseline 0. | Regression +10 over baseline 0: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `B2_layer_skip_ratchet` | P1 | ratchet | TRACK | floor | 951 | 951 | Counts: Import edges that skip more than one layer ordinal (layer-hop). Sub: 951 at floor (baseline 951); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C3_silent_writes_ratchet` | P1 | ratchet | TRACK | floor | 1992 | 1992 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: 1992 at floor (baseline 1992); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C4_policy_without_audit_ratchet` | P1 | ratchet | TRACK | floor | 1 | 1 | Counts: controls_flow edges without paired audit/telemetry emission. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `E1_trace_stub_module` | P1 | ratchet | TRACK | floor | 1030 | 1030 | Counts: Modules with high test:production import ratio (trace-theater stub pattern). Sub: 1030 at floor (baseline 1030); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I1_exit_disposition_ratchet` | P1 | ratchet | TRACK | floor | 742 | 742 | Counts: Terminal exit paths not covered in mv_exit_disposition_coverage. Sub: 742 at floor (baseline 742); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `M_taint_actionable_ratchet` | P1 | ratchet | TRACK | floor | 675 | 675 | Counts: Actionable taint surfaces without output schema binding. Sub: 675 at floor (baseline 675); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `N_guardrail_separation_ratchet` | P1 | ratchet | TRACK | floor | 112 | 112 | Counts: L5 guardrail and L3 core-response sharing same write target. Sub: 112 at floor (baseline 112); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `O_tool_call_parity_ratchet` | P1 | ratchet | TRACK | floor | 210 | 210 | Counts: Tool invocations missing observability receipt (Anthropic parity pattern). Sub: 210 at floor (baseline 210); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `P_structured_output_ratchet` | P1 | ratchet | TRACK | floor | 1 | 1 | Counts: generates_prompt at scale without structured output schema. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `11_architecture_witness` | P1 | block | CLEAR | — | 0 | 0 | Counts: Architecture witness Class A/B absence or live-plane write violations. Sub: No records. | None — gate clean (zero records). |
| `12_prompt_assembly_wiring` | P1 | block | CLEAR | — | 0 | 0 | Counts: Prompt-assembly subgraph disconnected from runtime spine. Sub: No records. | None — gate clean (zero records). |
| `7_lifecycle_coverage` | P1 | ratchet | CLEAR | — | 0 | unseeded | Counts: Lifecycle gaps: resources opened without matching close/cleanup. Sub: No records. | None — gate clean (zero records). |
| `G2_seam_test_export_coherence` | P1 | block | CLEAR | — | 0 | 0 | Counts: Production seam symbols exported in tests but not in package __all__/exports. Sub: No records. | None — gate clean (zero records). |
| `G_ISLAND_connected_components` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Non-giant connected components on undirected import graph. Sub: No records. | None — gate clean (zero records). |
| `G_WATCHLIST_DELTA_hotspot_regressions` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Graph watchlist items newly FAIL/WARN vs prior run. Sub: No records. | None — gate clean (zero records). |
| `H2_fanin_collapse_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Hotspot modules with >30% fan_in drop vs prior snapshot. Sub: No records. | None — gate clean (zero records). |
| `F1_untyped_seam_ratchet` | P2 | ratchet | TRACK | floor | 1075 | 1075 | Counts: Cross-layer imports where target has empty type_surface. Sub: 1075 at floor (baseline 1075); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | TRACK | floor | 993 | 993 | Counts: State mutations not consumed by replay surface (gap_flag=1). Sub: 993 at floor (baseline 993); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D2_role_duplication_warn` | P2 | warn | TRACK | advis | 102 | advisory | Counts: Role-suffix clusters (_reranker, _planner, …) with fan_in=0 members (advisory). Sub: 102 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `A3_dead_public_symbol_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Public symbols with zero importers (dead surface). Sub: No records. | None — gate clean (zero records). |
| `C5_unresolved_callsites_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: resolves_callsite edges with NULL destination (unresolved callee). Sub: No records. | None — gate clean (zero records). |
| `F2_broken_contract_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Import targets publishing zero exports edges (contract drift). Sub: No records. | None — gate clean (zero records). |
| `H4_mv_staleness_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Total edge count delta >5% vs prior snapshot (graph drift). Sub: No records. | None — gate clean (zero records). |
| `M1_module_loc_ratchet` | P3 | ratchet | FIX | regr | 462 | 459 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: +3 vs baseline 459. | Regression +3 over baseline 459: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | FIX | regr | 1086 | 1083 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: +3 vs baseline 1083. | Regression +3 over baseline 1083: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `S4_unused_imports_ratchet` | P3 | ratchet | TRACK | floor | 10841 | 10841 | Counts: Unused import edges in production modules. Sub: 10841 at floor (baseline 10841); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D1_layer_doc_binding` | P3 | warn | TRACK | advis | 3 | advisory | Counts: Layer folders missing or mismatched LAYER.md binding (advisory). Sub: 3 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `E3_trace_theater_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Emit-symbol density per layer vs imports (KPI advisory). Sub: No records. | None — gate clean (zero records). |
| `F3_missing_adapter_warn` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Protocol/ABC/Interface with zero implements edges (advisory). Sub: No records. | None — gate clean (zero records). |
| `H3_ap_velocity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Antipattern edge density per 1k LOC (KPI advisory). Sub: No records. | None — gate clean (zero records). |
| `K1_churn_complexity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: High churn×complexity files (KPI advisory, jsonl sink). Sub: No records. | None — gate clean (zero records). |

### Fix now (Verdict FIX)

| Gate ID | Sub | Records |
|---------|:---:|---------:|
| `G_REACH_l0_reachability` | regr | 2850 |
| `Q2_cyclomatic_complexity_ratchet` | regr | 1086 |
| `M1_module_loc_ratchet` | regr | 462 |
| `H1_new_orphans_delta_ratchet` | regr | 10 |
| `8_trace_replay_eval` | regr | 5 |
| `L2_lpg_drift_ratchet` | regr | 2 |

### Track later (Verdict TRACK — CI OK, backlog remains)

| Gate ID | Sub | Records |
|---------|:---:|---------:|
| `S4_unused_imports_ratchet` | floor | 10841 |
| `C3_silent_writes_ratchet` | floor | 1992 |
| `S2_uwg_bypass_ratchet` | floor | 1541 |
| `F1_untyped_seam_ratchet` | floor | 1075 |
| `E1_trace_stub_module` | floor | 1030 |
| `I2_replay_surface_gaps_ratchet` | floor | 993 |
| `B2_layer_skip_ratchet` | floor | 951 |
| `3_write_sovereignty` | inventory | 933 |
| `I1_exit_disposition_ratchet` | floor | 742 |
| `M_taint_actionable_ratchet` | floor | 675 |
| `O_tool_call_parity_ratchet` | floor | 210 |
| `N_guardrail_separation_ratchet` | floor | 112 |
| `D2_role_duplication_warn` | advis | 102 |
| `D1_layer_doc_binding` | advis | 3 |
| `C4_policy_without_audit_ratchet` | floor | 1 |
| `J1_canonical_pipeline_wiring` | inventory | 1 |
| `P_structured_output_ratchet` | floor | 1 |

## 5. Severity Inventory Burndown

Counts come from the canonical `adg_burndown_table.json` (schema 2.2).
This is raw MV defect inventory by severity/source band; it is not one row per CI gate.
Use this section for guardian math, not the status table above.
`gross` = raw violations found. `guardian` = guardian-exempted (still counted).
`net` = `gross - guardian`. `diff` = delta vs prior snapshot baseline.

| Severity Band | Label | Gross | Guardian | Net | Diff vs prev |
|---------------|-------|------:|---------:|----:|-------------:|
| P0 | layer_violations | 47 | 42 | 5 | +42 |
| P1 | anti_patterns_high | 1199 | 1195 | 4 | +1195 |
| P2 | anti_patterns_medium | 745 | 723 | 22 | +723 |
| P3 | style_warnings | 18970 | 92 | 18878 | +92 |

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

## 6. Aggregate Verdicts

| Verdict | Count | Meaning |
|---------|------:|---------|
| block_pass | 14 | Block-class gates that did not halt the run (exit 0). Records may be non-zero. |
| block_fail | 0 | Block-class gates that halted the run — clear the gate blocking condition. |
| ratchet_pass | 21 | Ratchet-class gates within their baseline ceiling. |
| ratchet_regressed | 6 | Ratchet-class gates with NEW records beyond baseline. |
| ratchet_seed_missing | 0 | Ratchet-class gates without a baseline seed (first run). |
| warn | 6 | Advisory-class gates (do not gate the run). |

### Per-gate verdict rollup (this report)

| Verdict | Gates | Meaning |
|---------|------:|---------|
| FIX | 6 | Address before treating ADG as green (gate blocked or ratchet regressed). |
| TRACK | 17 | CI passed this gate; records are tracked backlog — plan hygiene, not a halt. |
| CLEAR | 25 | Zero records; nothing to do on this gate. |

## 7. Fix now (detail)

| Gate | Band | Enf | Sub | Records | Signal |
|------|:----:|:---:|:---:|---------:|--------|
| `G_REACH_l0_reachability` | P0 | ratchet | regr | 2850 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: +7 vs baseline 2843. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | regr | 1086 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: +3 vs baseline 1083. |
| `M1_module_loc_ratchet` | P3 | ratchet | regr | 462 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: +3 vs baseline 459. |
| `H1_new_orphans_delta_ratchet` | P1 | ratchet | regr | 10 | Counts: Modules newly fan_in=0 vs prior snapshot (new orphans). Sub: +10 vs baseline 0. |
| `8_trace_replay_eval` | P1 | ratchet | regr | 5 | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: Above ratchet baseline. |
| `L2_lpg_drift_ratchet` | P0 | ratchet | regr | 2 | Counts: Illegal or drifted imports touching L_PG boundary. Sub: +1 vs baseline 1. |

---
## Next action

- **Queue:** `artifacts\adg\adg_action_queue_06152026_0644.json`
- **emit_status:** `ok`
- **degraded:** `False`
- **summary:** FIX=6 · TRACK=17 · actions_emitted=10

### Testing hotspot overlay

Use these paths to place tests while executing the next burn-down or cleanup slice.

| Rank | Target | How this changes next steps |
|-----:|--------|-----------------------------|
| 7 | `apps_rg/runtime/sections/executive_summary_lane.py` | Add or repair tests here if the current slice touches this path or its callers. |
| 8 | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | Add or repair tests here if the current slice touches this path or its callers. |
| 9 | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` | Add or repair tests here if the current slice touches this path or its callers. |

| Rank | Lane | Kind | Target | ordering_reason | Signal |
|-----:|------|------|--------|-----------------|--------|
| 1 | FIX | fix_gate | `L2_lpg_drift_ratchet` | fix_regr_p0_delta_asc | Counts: Illegal or drifted imports touching L_PG boundary. Sub: +1 vs baseline 1. |
| 2 | FIX | fix_gate | `G_REACH_l0_reachability` | fix_regr_p0_delta_asc | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: +7 vs baseline 2843. |
| 3 | FIX | fix_gate | `8_trace_replay_eval` | fix_regr_p1_delta_asc | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: Above ratchet baseline. |
| 4 | FIX | fix_gate | `H1_new_orphans_delta_ratchet` | fix_regr_p1_delta_asc | Counts: Modules newly fan_in=0 vs prior snapshot (new orphans). Sub: +10 vs baseline 0. |
| 5 | FIX | fix_gate | `M1_module_loc_ratchet` | fix_regr_p3_delta_asc | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: +3 vs baseline 459. |

CLI: `python tools/reports/adg_action_queue.py --latest --top 10 --format markdown`

---
Report renderer: `tools/reports/adg_burndown_report.py`. Re-run with `python tools/reports/adg_burndown_report.py --out artifacts/adg/adg_burndown_report.md`.
