# ADG BCG Gate Adapter

- **Generated:** 2026-06-28T23:55:12+00:00
- **Policy:** `2026-06-28.high_signal_burndown_v1`
- **Source timestamp:** 2026-06-28T23:51:16.197008+00:00
- **Priority queue:** 21 gate(s) / 23,838 row(s)
- **KPI/watchlist:** 2 gate(s) / 108 row(s)

This adapter separates work from watchlist: FIX and burn-down rows can enter the action queue; KPI/watchlist rows stay visible without becoming automatic cleanup work.

## Fix now

Current blockers, regressions, or missing seeds. These are the only rows that should stop green ADG.

| Gate | Materiality | Band | Enforcement | Verdict | Sub | Rows | Next step |
|------|-------------|:----:|-------------|:-------:|:---:|-----:|-----------|
| `13_core_imports_apps` | core_app_boundary | P0 | block | FIX | block | 35 | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| `10_infra_wiring` | runtime_infra_boundary | P0 | block | FIX | block | 3 | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| `S4_unused_imports_ratchet` | architecture_backlog | P3 | ratchet | FIX | regr | 10,772 | Regression +22 over baseline 10750: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `C3_silent_writes_ratchet` | architecture_backlog | P1 | ratchet | FIX | regr | 2,050 | Regression +16 over baseline 2034: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `S2_uwg_bypass_ratchet` | architecture_backlog | P0 | ratchet | FIX | regr | 1,601 | Regression +30 over baseline 1571 (P0): investigate each NEW path; fix the regression — re-baseline only with explicit sign-off. |
| `Q2_cyclomatic_complexity_ratchet` | architecture_backlog | P3 | ratchet | FIX | regr | 1,168 | Regression +20 over baseline 1148: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `I2_replay_surface_gaps_ratchet` | architecture_backlog | P2 | ratchet | FIX | regr | 993 | Regression +4 over baseline 989: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `M_taint_actionable_ratchet` | architecture_backlog | P1 | ratchet | FIX | regr | 681 | Regression +5 over baseline 676: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `M1_module_loc_ratchet` | architecture_backlog | P3 | ratchet | FIX | regr | 466 | Regression +8 over baseline 458: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |
| `8_trace_replay_eval` | architecture_backlog | P1 | ratchet | FIX | regr | 4 | Regression +N over baseline None: fix the new findings, or re-baseline via the gate's `--regenerate-baseline` if intentional/approved debt. |

## Burn down / owned backlog

Accepted debt that is still plausible burn-down work after FIX rows clear.

| Gate | Materiality | Band | Enforcement | Verdict | Sub | Rows | Next step |
|------|-------------|:----:|-------------|:-------:|:---:|-----:|-----------|
| `G_REACH_l0_reachability` | architecture_backlog | P0 | ratchet | TRACK | floor | 1,495 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `E1_trace_stub_module` | architecture_backlog | P1 | ratchet | TRACK | floor | 982 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `F1_untyped_seam_ratchet` | architecture_backlog | P2 | ratchet | TRACK | floor | 979 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `B2_layer_skip_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 862 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I1_exit_disposition_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 695 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `O_tool_call_parity_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 205 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `N_guardrail_separation_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 88 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C4_policy_without_audit_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 1 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `P_structured_output_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 1 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `3_write_sovereignty` | architecture_backlog | P0 | block | TRACK | inventory | 756 | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `J1_canonical_pipeline_wiring` | architecture_backlog | P0 | block | TRACK | inventory | 1 | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |

## KPI / watchlist

Trend and hygiene signals. Report separately; do not treat as burn-down work without an owner and target.

| Gate | Materiality | Band | Enforcement | Verdict | Sub | Rows | Next step |
|------|-------------|:----:|-------------|:-------:|:---:|-----:|-----------|
| `D2_role_duplication_warn` | governance_hygiene | P2 | warn | TRACK | advis | 105 | Advisory KPI: watch the trend; no action required to pass CI. |
| `D1_layer_doc_binding` | governance_hygiene | P3 | warn | TRACK | advis | 3 | Advisory KPI: watch the trend; no action required to pass CI. |

## Clear

Zero-action rows.

| Gate | Materiality | Band | Enforcement | Verdict | Sub | Rows | Next step |
|------|-------------|:----:|-------------|:-------:|:---:|-----:|-----------|
| `11_architecture_witness` | architecture_backlog | P1 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `12_prompt_assembly_wiring` | architecture_backlog | P1 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `1_critical_path_integrity` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `2_authority_boundary` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `4_capability_egress` | provider_model_path | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `5_text_to_action` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `6_determinism_provenance` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `7_lifecycle_coverage` | architecture_backlog | P1 | ratchet | CLEAR | — | 0 | None — gate clean (zero rows). |
| `9_executor_theater` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `A3_dead_public_symbol_ratchet` | architecture_backlog | P2 | ratchet | CLEAR | — | 0 | None — gate clean (zero rows). |
| `C1_uwg_bypass_pview` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `C2_l5_bypass_pview` | provider_model_path | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
