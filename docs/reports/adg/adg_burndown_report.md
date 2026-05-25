# ADG CI Burndown Report

- **Generated:** 2026-05-25T10:29:44+00:00
- **Gate-results source:** `artifacts\adg\adg_gate_results_20260525_102221.json`
- **Burndown source:** `artifacts\adg\adg_burndown_table.json`
- **Snapshot timestamp:** 2026-05-25T10:22:21.832436+00:00
- **Total gates:** 48
- **Overall verdict:** **BLOCKED**

## 1. Burndown by Severity Band

Counts come from the canonical `adg_burndown_table.json` (schema 2.2).
`gross` = raw violations found. `guardian` = guardian-exempted (still counted).
`net` = `gross - guardian`. `diff` = delta vs prior snapshot baseline.

| Band | Label | Gross | Guardian | Net | Diff vs prev |
|------|-------|------:|---------:|----:|-------------:|
| P0 | layer_violations | 38 | 38 | 0 | +38 |
| P1 | anti_patterns_high | 1199 | 1102 | 97 | +1102 |
| P2 | anti_patterns_medium | 669 | 664 | 5 | +664 |
| P3 | style_warnings | 18391 | 69 | 18322 | +69 |

_p0_clean = True • p1_no_ratchet = True • counting_mode = `violations_plus_exempted_edge_inference`_

## 2. All CI Gates

One row per registered gate. `Enf` is the enforcement contract: **block** = any violation fails the run; **ratchet** = only NEW violations beyond the baseline fail; **warn** = advisory only.

| Gate ID | Band | Enf | Status | Violations | Description |
|---------|:----:|:---:|:------:|-----------:|-------------|
| `G_REACH_l0_reachability` | P0 | ratchet | REGR | 2792 | Graph Reach (auto-derived) |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | REGR | 1600 | Uwg Bypass Ratchet (auto-derived) |
| `10_infra_wiring` | P0 | block | PASS | 0 | Infra Wiring (auto-derived) |
| `1_critical_path_integrity` | P0 | block | PASS | 0 | Critical execution paths reach their canonical sinks (no broken chains). |
| `2_authority_boundary` | P0 | block | PASS | 0 | L0/L_PG calls cross only declared authority boundaries (UWG / spine). |
| `3_write_sovereignty` | P0 | block | PASS | 848 | Every state mutation flows through UWG; no direct infra writes from apps_*. |
| `4_capability_egress` | P0 | block | PASS | 0 | Outbound provider/SDK calls leave through sanctioned capability adapters. |
| `5_text_to_action` | P0 | block | PASS | 0 | User text reaches action-class tools only after prompt-governance gating. |
| `6_determinism_provenance` | P0 | block | PASS | 0 | Determinism digest + replay key are emitted on every trace root. |
| `9_executor_theater` | P0 | block | PASS | 0 | Executor Theater (auto-derived) |
| `C1_uwg_bypass_pview` | P0 | block | PASS | 0 | Uwg Bypass PView (auto-derived) |
| `C2_l5_bypass_pview` | P0 | block | PASS | 0 | L5Bypass (auto-derived) |
| `L2_lpg_drift_ratchet` | P0 | ratchet | PASS | 28 | Lpg Drift Ratchet (auto-derived) |
| `W5_waiver_expiry` | P0 | block | PASS | 0 | Waiver Expiry (auto-derived) |
| `J1_canonical_pipeline_wiring` | P0 | block | WARN | 1 | Canonical Pipeline Wiring (auto-derived) |
| `8_trace_replay_eval` | P1 | ratchet | REGR | 78 | Trace Replay Eval (auto-derived) |
| `C3_silent_writes_ratchet` | P1 | ratchet | REGR | 1930 | Silent Writes (auto-derived) |
| `O_tool_call_parity_ratchet` | P1 | ratchet | REGR | 315 | Tool Call Parity (auto-derived) |
| `11_architecture_witness` | P1 | block | PASS | 0 | Architecture Witness (auto-derived) |
| `12_prompt_assembly_wiring` | P1 | block | PASS | 0 | Prompt Assembly Wiring (auto-derived) |
| `7_lifecycle_coverage` | P1 | ratchet | PASS | 0 | Resources opened in apps_*/agentic_core have matching close/cleanup pairs. |
| `B2_layer_skip_ratchet` | P1 | ratchet | PASS | 893 | Layer Skip (auto-derived) |
| `C4_policy_without_audit_ratchet` | P1 | ratchet | PASS | 1 | Policy Without Audit (auto-derived) |
| `E1_trace_stub_module` | P1 | ratchet | PASS | 1036 | Trace Stub Module (auto-derived) |
| `G2_seam_test_export_coherence` | P1 | block | PASS | 0 | Seam Test Export Coherence (auto-derived) |
| `G_ISLAND_connected_components` | P1 | ratchet | PASS | 0 | Graph Island (auto-derived) |
| `G_WATCHLIST_DELTA_hotspot_regressions` | P1 | ratchet | PASS | 0 | Graph Watchlist Delta (auto-derived) |
| `H1_new_orphans_delta_ratchet` | P1 | ratchet | PASS | 0 | New Orphans Delta (auto-derived) |
| `H2_fanin_collapse_ratchet` | P1 | ratchet | PASS | 0 | Fanin Collapse (auto-derived) |
| `I1_exit_disposition_ratchet` | P1 | ratchet | PASS | 726 | Exit Disposition (auto-derived) |
| `M_taint_actionable_ratchet` | P1 | ratchet | PASS | 657 | Taint Actionable (auto-derived) |
| `N_guardrail_separation_ratchet` | P1 | ratchet | PASS | 112 | Guardrail Separation (auto-derived) |
| `P_structured_output_ratchet` | P1 | ratchet | PASS | 1 | Structured Output (auto-derived) |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | REGR | 1054 | Replay Surface Gaps (auto-derived) |
| `A3_dead_public_symbol_ratchet` | P2 | ratchet | PASS | 0 | Dead Symbol Ratchet (auto-derived) |
| `C5_unresolved_callsites_ratchet` | P2 | ratchet | PASS | 0 | Unresolved Callsites (auto-derived) |
| `D2_role_duplication_warn` | P2 | warn | PASS | 99 | Role Dedup (auto-derived) |
| `F1_untyped_seam_ratchet` | P2 | ratchet | PASS | 1015 | Untyped Seam (auto-derived) |
| `F2_broken_contract_ratchet` | P2 | ratchet | PASS | 0 | Broken Contract (auto-derived) |
| `H4_mv_staleness_ratchet` | P2 | ratchet | PASS | 0 | Mv Staleness (auto-derived) |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | REGR | 909 | Cyclomatic Ceiling (auto-derived) |
| `S4_unused_imports_ratchet` | P3 | ratchet | REGR | 10698 | Unused Imports Ratchet (auto-derived) |
| `D1_layer_doc_binding` | P3 | warn | PASS | 3 | Layer Doc Binding (auto-derived) |
| `E3_trace_theater_kpi` | P3 | warn | PASS | 0 | Trace Theater Kpi (auto-derived) |
| `F3_missing_adapter_warn` | P3 | warn | PASS | 0 | Missing Adapter (auto-derived) |
| `H3_ap_velocity_kpi` | P3 | warn | PASS | 0 | Ap Velocity Kpi (auto-derived) |
| `K1_churn_complexity_kpi` | P3 | warn | PASS | 0 | Churn Complexity Kpi (auto-derived) |
| `M1_module_loc_ratchet` | P3 | ratchet | PASS | 442 | Module Loc Ratchet (auto-derived) |

## 3. Aggregate Verdicts

| Verdict | Count | Meaning |
|---------|------:|---------|
| block_pass | 14 | Block-class gates with zero violations. |
| block_fail | 0 | Block-class gates currently failing — must reach 0. |
| ratchet_pass | 19 | Ratchet-class gates within their baseline ceiling. |
| ratchet_regressed | 8 | Ratchet-class gates with NEW violations beyond baseline. |
| ratchet_seed_missing | 0 | Ratchet-class gates without a baseline seed (first run). |
| warn | 6 | Advisory-class gates (do not gate the run). |

## 4. Top Blockers (Failing or Regressed)

| Gate | Band | Enf | Violations | Description |
|------|:----:|:---:|-----------:|-------------|
| `S4_unused_imports_ratchet` | P3 | ratchet | 10698 | Unused Imports Ratchet (auto-derived) |
| `G_REACH_l0_reachability` | P0 | ratchet | 2792 | Graph Reach (auto-derived) |
| `C3_silent_writes_ratchet` | P1 | ratchet | 1930 | Silent Writes (auto-derived) |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | 1600 | Uwg Bypass Ratchet (auto-derived) |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | 1054 | Replay Surface Gaps (auto-derived) |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | 909 | Cyclomatic Ceiling (auto-derived) |
| `O_tool_call_parity_ratchet` | P1 | ratchet | 315 | Tool Call Parity (auto-derived) |
| `8_trace_replay_eval` | P1 | ratchet | 78 | Trace Replay Eval (auto-derived) |

---
Report renderer: `tools/reports/adg_burndown_report.py`. Re-run with `python tools/reports/adg_burndown_report.py --out artifacts/adg/adg_burndown_report.md`.
