# apps_rg X2 dead gates — W1 + W2 receipt

**Plan:** [apps-rg-x2-dead-gates-burndown-c4e8f2.md](../../.cursor/plans/apps-rg-x2-dead-gates-burndown-c4e8f2.md)  
**Generated:** 2026-05-22

## W1 — Registry and audit alignment

- Added `RETIRED_EXEC_SUMMARY_X2_GATE_IDS` + `is_retired_exec_summary_x2_gate()` in [section_product_shape_ssot.py](../../apps_rg/runtime/sections/section_product_shape_ssot.py)
- Declarative contract documents live bounds gates: `x2_exec_summary_sentence_count_4_5`, `x2_exec_summary_paragraph_max_words` in [executive_summary_contract.yaml](../../apps_rg/prompt_assembly/section_contracts/executive_summary_contract.yaml)
- `lane_registry` aligned: added `x2_claim_ledger_orphan_zero` to executive_summary critical set
- Complexity audit catalog distinguishes **RETIRED** vs **PASS-skip (W4)**; flags retired IDs in stale proof bundles
- Convergence audit tracks `retired_gate_ids_observed` and recommends refreshing proof when present

## W2 — Retired exec-summary SRFS repair stack

**Deleted (release-disabled, not on product lane path):**

- [exec_summary_srfs_density_repair.py](../../apps_rg/runtime/sections/exec_summary_srfs_density_repair.py)
- [exec_summary_srfs_emergency_finalizer.py](../../apps_rg/runtime/sections/exec_summary_srfs_emergency_finalizer.py)
- [test_exec_summary_srfs_emergency_finalizer.py](../../tests/unit/apps_rg/test_exec_summary_srfs_emergency_finalizer.py)

**Kept (opt-in via `RELEASE_SRFS_JUDGE_SAFE_REPAIR_ENABLED` + env):**

- [exec_summary_srfs_judge_safe.py](../../apps_rg/runtime/sections/exec_summary_srfs_judge_safe.py)

**Tests updated:**

- Removed density micro-repair and legacy density band tests
- Credibility / raw-json tests repointed to `judge_safe` / `graph_only_quality`

**Runtime confirmation:** `run_x2_gates` does not emit any `RETIRED_EXEC_SUMMARY_X2_GATE_IDS` (new unit test).

## Commands

```text
python ops_scripts/apps_rg/section_complexity_reduction_audit.py -> exit 0
python ops_scripts/apps_rg/section_authority_convergence_audit.py -> exit 0
pytest section_rigor + product_shape + x1d_alignment + pa_compiled_prompt + runtime_slice (excl. subprocess mock/qwen) -> 175 passed, 1 skipped
```

## W1/W2 deferred closure (2026-05-22)

- Fixed `test_compile_exec_summary_srfs_includes_style_oneshot_block` for compact SRFS oneshot PA block.
- Aligned runtime_slice contract tests to 4–5 sentence product shape, graph-only prompt markers, and `section_judge_profile` env resolution.
- Retired `test_zz_exec_summary_selected_role_fact_set_cli_smoke` (CLI `--selected-role-fact-set` removed; coverage via SRFS compile test).
- Updated [SIMPLIFICATION_REDESIGN.md](SIMPLIFICATION_REDESIGN.md) and [apps_rg_x2_dead_gates_deletion_plan.md](apps_rg_x2_dead_gates_deletion_plan.md); plan DoD-2/DoD-3 DONE.

## Out of scope (W3/W4)

- Collapse `*_within_srfs_slice` proof-pool gate IDs
- Remove SRFS skip-PASS emission on golden path
- Full `run_cmd()` runtime_slice subprocess tests (mock/qwen dispatch) — require live/stub lane artifacts
