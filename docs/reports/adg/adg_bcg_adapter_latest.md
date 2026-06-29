# ADG BCG Gate Adapter

- **Generated:** 2026-06-29T11:18:55+00:00
- **Policy:** `2026-06-28.high_signal_burndown_v1`
- **Source timestamp:** 2026-06-29T11:16:15.871792+00:00
- **Work sections:** 17 gate(s) / 11,428 row(s)
- **KPI/watchlist:** 5 gate(s) / 12,515 row(s)

This adapter is MECE: FIX, burn-down, KPI/watchlist, and clear rows have one ownership section each. FIX rows can block green; burn-down rows are after-green work; KPI/watchlist rows stay visible without becoming automatic cleanup work.

## Fix now

Current blockers, regressions, or missing seeds. These are the only rows that should stop green ADG.

| Gate | Materiality | Band | Enforcement | Verdict | Sub | Rows | Next step |
|------|-------------|:----:|-------------|:-------:|:---:|-----:|-----------|
| `10_infra_wiring` | runtime_infra_boundary | P0 | block | FIX | block | 3 | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |
| `13_core_imports_apps` | core_app_boundary | P0 | block | FIX | block | 35 | BLOCKER (P0): clear the zero-tolerance condition before merge. Do NOT re-baseline a P0 block. |

## Burn down / owned backlog

Accepted debt that is still plausible burn-down work after FIX rows clear.

| Gate | Materiality | Band | Enforcement | Verdict | Sub | Rows | Next step |
|------|-------------|:----:|-------------|:-------:|:---:|-----:|-----------|
| `S2_uwg_bypass_ratchet` | architecture_backlog | P0 | ratchet | TRACK | floor | 1,601 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `G_REACH_l0_reachability` | architecture_backlog | P0 | ratchet | TRACK | floor | 1,495 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `3_write_sovereignty` | architecture_backlog | P0 | block | TRACK | inventory | 756 | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `J1_canonical_pipeline_wiring` | architecture_backlog | P0 | block | TRACK | inventory | 1 | Advisory inventory: monitor; reduce opportunistically. Does not block CI. |
| `C3_silent_writes_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 2,050 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `E1_trace_stub_module` | architecture_backlog | P1 | ratchet | TRACK | floor | 982 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `B2_layer_skip_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 862 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `I1_exit_disposition_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 695 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `M_taint_actionable_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 681 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `O_tool_call_parity_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 205 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `N_guardrail_separation_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 88 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `C4_policy_without_audit_ratchet` | architecture_backlog | P1 | ratchet | TRACK | floor | 1 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |

## KPI / watchlist

Trend and hygiene signals. Report separately; do not treat as burn-down work without an owner and target.

| Gate | Materiality | Band | Enforcement | Verdict | Sub | Rows | Next step |
|------|-------------|:----:|-------------|:-------:|:---:|-----:|-----------|
| `D2_role_duplication_warn` | governance_hygiene | P2 | warn | TRACK | advis | 105 | Advisory KPI: watch the trend; no action required to pass CI. |
| `S4_unused_imports_ratchet` | governance_hygiene | P3 | ratchet | TRACK | floor | 10,773 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `Q2_cyclomatic_complexity_ratchet` | governance_hygiene | P3 | ratchet | TRACK | floor | 1,168 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `M1_module_loc_ratchet` | governance_hygiene | P3 | ratchet | TRACK | floor | 466 | Backlog (within ratchet ceiling): shrink over time, defer to a plan wave. No action needed to pass CI. |
| `D1_layer_doc_binding` | governance_hygiene | P3 | warn | TRACK | advis | 3 | Advisory KPI: watch the trend; no action required to pass CI. |

## Clear

Zero-action rows.

| Gate | Materiality | Band | Enforcement | Verdict | Sub | Rows | Next step |
|------|-------------|:----:|-------------|:-------:|:---:|-----:|-----------|
| `4_capability_egress` | provider_model_path | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `C2_l5_bypass_pview` | provider_model_path | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `1_critical_path_integrity` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `2_authority_boundary` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `5_text_to_action` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `6_determinism_provenance` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `9_executor_theater` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `C1_uwg_bypass_pview` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `L2_lpg_drift_ratchet` | architecture_backlog | P0 | ratchet | CLEAR | — | 0 | None — gate clean (zero rows). |
| `W5_waiver_expiry` | architecture_backlog | P0 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `11_architecture_witness` | architecture_backlog | P1 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
| `12_prompt_assembly_wiring` | architecture_backlog | P1 | block | CLEAR | — | 0 | None — gate clean (zero rows). |
