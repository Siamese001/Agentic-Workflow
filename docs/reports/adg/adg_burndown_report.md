# ADG CI Burndown Report

- **Generated:** 2026-06-18T12:59:09+00:00
- **Gate-results source:** `artifacts\adg\adg_gate_results_20260618_125756.json`
- **Burndown source:** `artifacts\adg\adg_burndown_table.json`
- **Snapshot timestamp:** 2026-06-18T12:57:56.221731+00:00
- **Total gates:** 48
- **Overall verdict:** **BLOCKED** (run halt — exit code)
- **Action:** **FIX**=6 (address for green ADG) · **TRACK**=18 (CI OK, backlog) · **CLEAR**=24

### BCG Burndown Brief

- **North star:** Maintain SVP engineer-level repo standards: business-first decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Status:** BLOCKED
- **Business read:** Fix 6 blocker(s) first, then burn down 18 backlog item(s) so the run stays green.
- **Technical evidence:**
  - Snapshot timestamp: 2026-06-18T12:57:56.221731+00:00
  - Total gates: 48
  - FIX=6; TRACK=18; CLEAR=24
  - P0 gross/net: 44/3
  - P1 gross/net: 1151/5
- **Priority rule:** Work class first (Fix now > ratchets > open work > severity audit), then P-band (P0 > P1 > P2 > P3), then record count within the same class and band.

| Priority | Move | Scope | Business reason | Technical reason | Why this order | Decision |
|---------:|------|-------|----------------|-----------------|----------------|----------|
| 1 | Fix now | P0: P0 CI blockers | CI blocker; ADG is not green until this clears. | 1,553 records; Fix the blocking gate condition and rerun ADG before burn-down work. | CI blocker; ADG is not green until this clears. | Fix the blocking gate condition and rerun ADG before burn-down work. |
| 2 | Fix now | P1: P1 CI blockers | CI blocker; ADG is not green until this clears. | 2,023 records; Fix the blocking gate condition and rerun ADG before burn-down work. | CI blocker; ADG is not green until this clears. | Fix the blocking gate condition and rerun ADG before burn-down work. |
| 3 | Fix now | P3: P3 CI blockers | CI blocker; ADG is not green until this clears. | 1,087 records; Fix the blocking gate condition and rerun ADG before burn-down work. | CI blocker; ADG is not green until this clears. | Fix the blocking gate condition and rerun ADG before burn-down work. |
| 4 | Burn down ratchets | P0: `G_REACH` 2,785 | Ratchet floor work lowers accepted baseline debt; P-band outranks raw size. | 2,785 records; Use the P0 Action Plan below. | Ratchet floor work lowers accepted baseline debt; P-band outranks raw size. | Use the P0 Action Plan below. |

Why this order:
- Non-exempt severity rows are review context only, not Fix-now work unless a gate is failing.
- Record count breaks ties inside the same work class and P-band; it does not make P3 outrank P0.
- When the top row is P0 ratchets, use the P0 Action Plan for the exact gate order.

Next step: Use the P0 Action Plan for the exact gate order.

## 1. ADG Heuristic Attack Order

Rule: work class first (Fix now > ratchets > open work > severity audit), then P-band (P0 > P1 > P2 > P3), then record count within the same class and band.

| # | Attack | Band | Records | Why | Next step |
|--:|--------|------|--------:|-----|-----------|
| 1 | Fix now: P0 CI blockers | P0 | 1,553 | CI blocker; ADG is not green until this clears. | Fix the blocking gate condition and rerun ADG before burn-down work. |
| 2 | Fix now: P1 CI blockers | P1 | 2,023 | CI blocker; ADG is not green until this clears. | Fix the blocking gate condition and rerun ADG before burn-down work. |
| 3 | Fix now: P3 CI blockers | P3 | 1,087 | CI blocker; ADG is not green until this clears. | Fix the blocking gate condition and rerun ADG before burn-down work. |
| 4 | Burn down ratchets: `G_REACH` 2,785 | P0 | 2,785 | Ratchet floor work lowers accepted baseline debt; P-band outranks raw size. | Use the P0 Action Plan below. |
| 5 | Burn down ratchets: `E1_trace_stub` 983; `B2_layer_skip` 878; `I1_exit_disposition` 695; +5 more = 3,522 total | P1 | 3,522 | Ratchet floor work lowers accepted baseline debt; P-band outranks raw size. | Open a burn-down slice for the listed ratchets, rerun ADG, then absorb the lower baseline. |
| 6 | Burn down ratchets: `F1_untyped_seam` 1,006; `I2_replay_gaps` 978 | P2 | 1,984 | Ratchet floor work lowers accepted baseline debt; P-band outranks raw size. | Open a burn-down slice for the listed ratchets, rerun ADG, then absorb the lower baseline. |
| 7 | Burn down ratchets: `S4_unused_imports` 10,735; `M1_module_loc` 446 | P3 | 11,181 | Ratchet floor work lowers accepted baseline debt; P-band outranks raw size. | Open a burn-down slice for the listed ratchets, rerun ADG, then absorb the lower baseline. |
| 8 | Open non-ratchet work: `write_sovereignty` 930; `4_capability_egress` 3; `pipeline_wiring` 1 | P0 | 934 | Real open work, but it does not lower a ratchet floor or block CI. | Schedule after ratchets unless the item is tiny, already in hand, or high-leverage. |
| 9 | Open non-ratchet work: `D2_role_duplication` 105 | P2 | 105 | Real open work, but it does not lower a ratchet floor or block CI. | Schedule after ratchets unless the item is tiny, already in hand, or high-leverage. |
| 10 | Open non-ratchet work: `D1_layer_doc` 3 | P3 | 3 | Real open work, but it does not lower a ratchet floor or block CI. | Schedule after ratchets unless the item is tiny, already in hand, or high-leverage. |
| 11 | Severity audit: 3 non-exempt from 44 gross | P0 | 3 | Review-only audit signal; not Fix now unless it maps to a failing gate. | Audit or map to a gate; do not treat as a CI blocker by itself. |
| 12 | Severity audit: 5 non-exempt from 1,151 gross | P1 | 5 | Review-only audit signal; not Fix now unless it maps to a failing gate. | Audit or map to a gate; do not treat as a CI blocker by itself. |
| 13 | Severity audit: 20 non-exempt from 724 gross | P2 | 20 | Review-only audit signal; not Fix now unless it maps to a failing gate. | Audit or map to a gate; do not treat as a CI blocker by itself. |
| 14 | Severity audit: 18,893 non-exempt from 18,983 gross | P3 | 18,893 | Review-only audit signal; not Fix now unless it maps to a failing gate. | Audit or map to a gate; do not treat as a CI blocker by itself. |

Comments:
- Non-exempt severity rows are included for review, but they do not populate Fix now unless a gate is failing.
- Record count breaks ties inside the same work class and P-band; it does not make P3 outrank P0.
- When the top row is P0 ratchets, use the P0 Action Plan for the exact gate order.

## 2. P0 Action Plan

Read this table top to bottom. It is the action surface; the band table below is status context.

| # | Work | Gate | Records | Why this priority | Next step |
|--:|------|------|--------:|-------------------|-----------|
| 1 | Fix now | `S2_UWG` | 1,549 | Blocks green ADG; fix before burn-down work. | Fix the gate condition and rerun ADG before treating the run as green. |
| 2 | Fix now | `C2_l5_bypass_pview` | 2 | Blocks green ADG; fix before burn-down work. | Fix the gate condition and rerun ADG before treating the run as green. |
| 3 | Fix now | `L2_LPG` | 2 | Blocks green ADG; fix before burn-down work. | Fix the gate condition and rerun ADG before treating the run as green. |
| 4 | Burn down ratchet | `G_REACH` | 2,785 | Largest P0 ratchet floor; reduces the biggest accepted baseline first. | Open a burn-down slice for this gate, reduce records, rerun ADG, then absorb the lower baseline. |
| 5 | Open non-ratchet work | `write_sovereignty` | 930 | Real open P0 work, but it does not reduce the ratchet floor. | Schedule after P0 ratchets unless the fix is tiny, already in hand, or high-leverage. |
| 6 | Open non-ratchet work | `4_capability_egress` | 3 | Small open P0 work item; bundle if it is already in the same files. | Close when touching nearby code; it is open work but not ratchet burn-down. |
| 7 | Open non-ratchet work | `pipeline_wiring` | 1 | Small open P0 work item; bundle if it is already in the same files. | Close when touching nearby code; it is open work but not ratchet burn-down. |

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
| P0 | BLOCKED | 3 | 1,553 | 2,785 | 934 | red gates present | fix red gates first |
| P1 | BLOCKED | 2 | 2,023 | 3,522 | 0 | red gates present | fix red gates first |
| P2 | PASS | 0 | 0 | 1,984 | 105 | green; ratchet burn-down/open work remains | work ranked queue; ratchets first |
| P3 | BLOCKED | 1 | 1,087 | 11,181 | 3 | red gates present | fix red gates first |

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
| `C2_l5_bypass_pview` | P0 | block | FIX | block | 2 | 0 | Counts: Provider/tool calls skipping L5 gateway (materialized view). Sub: Run blocked (exit 1). | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| `L2_lpg_drift_ratchet` | P0 | ratchet | FIX | regr | 2 | 1 | Counts: Illegal or drifted imports touching L_PG boundary. Sub: +1 vs baseline 1. | Regression +1 over baseline 1 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | FIX | regr | 1549 | 1540 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: +9 vs baseline 1540. | Regression +9 over baseline 1540 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| `G_REACH_l0_reachability` | P0 | ratchet | TRACK | floor | 2785 | 2785 | Counts: Production-layer modules with no import path from any L0 node (orphans). Sub: 2785 at floor (baseline 2785); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `3_write_sovereignty` | P0 | block | TRACK | inventory | 930 | warn inventory | Counts: Non-UWG durable write paths in mv_write_sovereignty_paths (inventory). Sub: 930 warn inventory; not halt-tier. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `4_capability_egress` | P0 | block | TRACK | inventory | 3 | warn inventory | Counts: Outbound provider/SDK calls not leaving through sanctioned adapters. Sub: 3 warn inventory; not halt-tier. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `J1_canonical_pipeline_wiring` | P0 | block | TRACK | inventory | 1 | warn inventory | Counts: Declared canonical_pipelines.yaml steps missing required call wiring. Sub: 1 subprocess warn. | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `10_infra_wiring` | P0 | block | CLEAR | — | 0 | 0 | Counts: Infra wiring defects (canonical pipeline / spine reachability). Sub: No records. | None — gate clean (zero records). |
| `1_critical_path_integrity` | P0 | block | CLEAR | — | 0 | 0 | Counts: Broken or missing links on declared critical execution paths (L0→sink). Sub: No records. | None — gate clean (zero records). |
| `2_authority_boundary` | P0 | block | CLEAR | — | 0 | 0 | Counts: Calls that cross layer authority without UWG/spine sanction. Sub: No records. | None — gate clean (zero records). |
| `5_text_to_action` | P0 | block | CLEAR | — | 0 | 0 | Counts: User text reaching action-class tools without prompt-governance gating. Sub: No records. | None — gate clean (zero records). |
| `6_determinism_provenance` | P0 | block | CLEAR | — | 0 | 0 | Counts: Trace roots missing determinism digest or replay key emission. Sub: No records. | None — gate clean (zero records). |
| `9_executor_theater` | P0 | block | CLEAR | — | 0 | 0 | Counts: Executor-theater signals: import-only or stub execution patterns. Sub: No records. | None — gate clean (zero records). |
| `C1_uwg_bypass_pview` | P0 | block | CLEAR | — | 0 | 0 | Counts: Any row in UWG-bypass materialized view (zero tolerance block). Sub: No records. | None — gate clean (zero records). |
| `W5_waiver_expiry` | P0 | block | CLEAR | — | 0 | 0 | Counts: Expired wiring-CI waiver entries in config. Sub: No records. | None — gate clean (zero records). |
| `8_trace_replay_eval` | P1 | ratchet | FIX | regr | 12 | unseeded | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: Above ratchet baseline. | Regression +N over baseline None: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `C3_silent_writes_ratchet` | P1 | ratchet | FIX | regr | 2011 | 1986 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: +25 vs baseline 1986. | Regression +25 over baseline 1986: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `B2_layer_skip_ratchet` | P1 | ratchet | TRACK | floor | 878 | 878 | Counts: Import edges that skip more than one layer ordinal (layer-hop). Sub: 878 at floor (baseline 878); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C4_policy_without_audit_ratchet` | P1 | ratchet | TRACK | floor | 1 | 1 | Counts: controls_flow edges without paired audit/telemetry emission. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `E1_trace_stub_module` | P1 | ratchet | TRACK | floor | 983 | 983 | Counts: Modules with high test:production import ratio (trace-theater stub pattern). Sub: 983 at floor (baseline 983); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I1_exit_disposition_ratchet` | P1 | ratchet | TRACK | floor | 695 | 695 | Counts: Terminal exit paths not covered in mv_exit_disposition_coverage. Sub: 695 at floor (baseline 695); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `M_taint_actionable_ratchet` | P1 | ratchet | TRACK | floor | 669 | 669 | Counts: Actionable taint surfaces without output schema binding. Sub: 669 at floor (baseline 669); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `N_guardrail_separation_ratchet` | P1 | ratchet | TRACK | floor | 90 | 90 | Counts: L5 guardrail and L3 core-response sharing same write target. Sub: 90 at floor (baseline 90); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `O_tool_call_parity_ratchet` | P1 | ratchet | TRACK | floor | 205 | 205 | Counts: Tool invocations missing observability receipt (Anthropic parity pattern). Sub: 205 at floor (baseline 205); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `P_structured_output_ratchet` | P1 | ratchet | TRACK | floor | 1 | 1 | Counts: generates_prompt at scale without structured output schema. Sub: 1 at floor (baseline 1); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `11_architecture_witness` | P1 | block | CLEAR | — | 0 | 0 | Counts: Architecture witness Class A/B absence or live-plane write violations. Sub: No records. | None — gate clean (zero records). |
| `12_prompt_assembly_wiring` | P1 | block | CLEAR | — | 0 | 0 | Counts: Prompt-assembly subgraph disconnected from runtime spine. Sub: No records. | None — gate clean (zero records). |
| `7_lifecycle_coverage` | P1 | ratchet | CLEAR | — | 0 | unseeded | Counts: Lifecycle gaps: resources opened without matching close/cleanup. Sub: No records. | None — gate clean (zero records). |
| `G2_seam_test_export_coherence` | P1 | block | CLEAR | — | 0 | 0 | Counts: Production seam symbols exported in tests but not in package __all__/exports. Sub: No records. | None — gate clean (zero records). |
| `G_ISLAND_connected_components` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Non-giant connected components on undirected import graph. Sub: No records. | None — gate clean (zero records). |
| `G_WATCHLIST_DELTA_hotspot_regressions` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Graph watchlist items newly FAIL/WARN vs prior run. Sub: No records. | None — gate clean (zero records). |
| `H1_new_orphans_delta_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Modules newly fan_in=0 vs prior snapshot (new orphans). Sub: No records. | None — gate clean (zero records). |
| `H2_fanin_collapse_ratchet` | P1 | ratchet | CLEAR | — | 0 | 0 | Counts: Hotspot modules with >30% fan_in drop vs prior snapshot. Sub: No records. | None — gate clean (zero records). |
| `F1_untyped_seam_ratchet` | P2 | ratchet | TRACK | floor | 1006 | 1006 | Counts: Cross-layer imports where target has empty type_surface. Sub: 1006 at floor (baseline 1006); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | TRACK | floor | 978 | 978 | Counts: State mutations not consumed by replay surface (gap_flag=1). Sub: 978 at floor (baseline 978); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D2_role_duplication_warn` | P2 | warn | TRACK | advis | 105 | advisory | Counts: Role-suffix clusters (_reranker, _planner, …) with fan_in=0 members (advisory). Sub: 105 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `A3_dead_public_symbol_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Public symbols with zero importers (dead surface). Sub: No records. | None — gate clean (zero records). |
| `C5_unresolved_callsites_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: resolves_callsite edges with NULL destination (unresolved callee). Sub: No records. | None — gate clean (zero records). |
| `F2_broken_contract_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Import targets publishing zero exports edges (contract drift). Sub: No records. | None — gate clean (zero records). |
| `H4_mv_staleness_ratchet` | P2 | ratchet | CLEAR | — | 0 | 0 | Counts: Total edge count delta >5% vs prior snapshot (graph drift). Sub: No records. | None — gate clean (zero records). |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | FIX | regr | 1087 | 1083 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: +4 vs baseline 1083. | Regression +4 over baseline 1083: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `M1_module_loc_ratchet` | P3 | ratchet | TRACK | floor | 446 | 446 | Counts: Production modules exceeding LOC ceiling (disk scan). Sub: 446 at floor (baseline 446); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `S4_unused_imports_ratchet` | P3 | ratchet | TRACK | floor | 10735 | 10735 | Counts: Unused import edges in production modules. Sub: 10735 at floor (baseline 10735); no new debt. | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D1_layer_doc_binding` | P3 | warn | TRACK | advis | 3 | advisory | Counts: Layer folders missing or mismatched LAYER.md binding (advisory). Sub: 3 advisory; never blocks. | Advisory KPI: watch the trend; no action required to pass CI. |
| `E3_trace_theater_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Emit-symbol density per layer vs imports (KPI advisory). Sub: No records. | None — gate clean (zero records). |
| `F3_missing_adapter_warn` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Protocol/ABC/Interface with zero implements edges (advisory). Sub: No records. | None — gate clean (zero records). |
| `H3_ap_velocity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: Antipattern edge density per 1k LOC (KPI advisory). Sub: No records. | None — gate clean (zero records). |
| `K1_churn_complexity_kpi` | P3 | warn | CLEAR | — | 0 | advisory | Counts: High churn×complexity files (KPI advisory, jsonl sink). Sub: No records. | None — gate clean (zero records). |

### Fix now (Verdict FIX)

| Gate ID | Sub | Records |
|---------|:---:|---------:|
| `C3_silent_writes_ratchet` | regr | 2011 |
| `S2_uwg_bypass_ratchet` | regr | 1549 |
| `Q2_cyclomatic_complexity_ratchet` | regr | 1087 |
| `8_trace_replay_eval` | regr | 12 |
| `C2_l5_bypass_pview` | block | 2 |
| `L2_lpg_drift_ratchet` | regr | 2 |

### Track later (Verdict TRACK — CI OK, backlog remains)

| Gate ID | Sub | Records |
|---------|:---:|---------:|
| `S4_unused_imports_ratchet` | floor | 10735 |
| `G_REACH_l0_reachability` | floor | 2785 |
| `F1_untyped_seam_ratchet` | floor | 1006 |
| `E1_trace_stub_module` | floor | 983 |
| `I2_replay_surface_gaps_ratchet` | floor | 978 |
| `3_write_sovereignty` | inventory | 930 |
| `B2_layer_skip_ratchet` | floor | 878 |
| `I1_exit_disposition_ratchet` | floor | 695 |
| `M_taint_actionable_ratchet` | floor | 669 |
| `M1_module_loc_ratchet` | floor | 446 |
| `O_tool_call_parity_ratchet` | floor | 205 |
| `D2_role_duplication_warn` | advis | 105 |
| `N_guardrail_separation_ratchet` | floor | 90 |
| `4_capability_egress` | inventory | 3 |
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
| P0 | layer_violations | 44 | 41 | 3 | +41 |
| P1 | anti_patterns_high | 1151 | 1146 | 5 | +1146 |
| P2 | anti_patterns_medium | 724 | 704 | 20 | +704 |
| P3 | style_warnings | 18983 | 90 | 18893 | +90 |

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
| block_pass | 13 | Block-class gates that did not halt the run (exit 0). Records may be non-zero. |
| block_fail | 1 | Block-class gates that halted the run — clear the gate blocking condition. |
| ratchet_pass | 22 | Ratchet-class gates within their baseline ceiling. |
| ratchet_regressed | 5 | Ratchet-class gates with NEW records beyond baseline. |
| ratchet_seed_missing | 0 | Ratchet-class gates without a baseline seed (first run). |
| warn | 6 | Advisory-class gates (do not gate the run). |

### Per-gate verdict rollup (this report)

| Verdict | Gates | Meaning |
|---------|------:|---------|
| FIX | 6 | Address before treating ADG as green (gate blocked or ratchet regressed). |
| TRACK | 18 | CI passed this gate; records are tracked backlog — plan hygiene, not a halt. |
| CLEAR | 24 | Zero records; nothing to do on this gate. |

## 7. Fix now (detail)

| Gate | Band | Enf | Sub | Records | Signal |
|------|:----:|:---:|:---:|---------:|--------|
| `C3_silent_writes_ratchet` | P1 | ratchet | regr | 2011 | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: +25 vs baseline 1986. |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | regr | 1549 | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: +9 vs baseline 1540. |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | regr | 1087 | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: +4 vs baseline 1083. |
| `8_trace_replay_eval` | P1 | ratchet | regr | 12 | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: Above ratchet baseline. |
| `C2_l5_bypass_pview` | P0 | block | block | 2 | Counts: Provider/tool calls skipping L5 gateway (materialized view). Sub: Run blocked (exit 1). |
| `L2_lpg_drift_ratchet` | P0 | ratchet | regr | 2 | Counts: Illegal or drifted imports touching L_PG boundary. Sub: +1 vs baseline 1. |

---
## Next action

- **Queue:** `artifacts\adg\adg_action_queue_06182026_0852.json`
- **emit_status:** `ok`
- **degraded:** `False`
- **summary:** FIX=6 · TRACK=18 · actions_emitted=10

### Testing hotspot overlay

Use these paths to place tests while executing the next burn-down or cleanup slice.

| Rank | Target | How this changes next steps |
|-----:|--------|-----------------------------|
| 7 | `apps_rg/runtime/sections/executive_summary_lane.py` | Add or repair tests here if the current slice touches this path or its callers. |
| 8 | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | Add or repair tests here if the current slice touches this path or its callers. |
| 9 | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` | Add or repair tests here if the current slice touches this path or its callers. |

| Rank | Lane | Kind | Target | ordering_reason | Signal |
|-----:|------|------|--------|-----------------|--------|
| 1 | FIX | fix_gate | `C2_l5_bypass_pview` | fix_block_p0_violations_asc | Counts: Provider/tool calls skipping L5 gateway (materialized view). Sub: Run blocked (exit 1). |
| 2 | FIX | fix_gate | `L2_lpg_drift_ratchet` | fix_regr_p0_delta_asc | Counts: Illegal or drifted imports touching L_PG boundary. Sub: +1 vs baseline 1. |
| 3 | FIX | fix_gate | `S2_uwg_bypass_ratchet` | fix_regr_p0_delta_asc | Counts: Write paths that bypass UWG (overlay on write_sovereignty edges). Sub: +9 vs baseline 1540. |
| 4 | FIX | fix_gate | `8_trace_replay_eval` | fix_regr_p1_delta_asc | Counts: Eval/replay coverage regressions vs baseline by layer (mv_eval_coverage_by_path). Sub: Above ratchet baseline. |
| 5 | FIX | fix_gate | `C3_silent_writes_ratchet` | fix_regr_p1_delta_asc | Counts: writes_to edges without sibling emits_side_effect on same source. Sub: +25 vs baseline 1986. |

CLI: `python tools/reports/adg_action_queue.py --latest --top 10 --format markdown`

---
Report renderer: `tools/reports/adg_burndown_report.py`. Re-run with `python tools/reports/adg_burndown_report.py --out artifacts/adg/adg_burndown_report.md`.
