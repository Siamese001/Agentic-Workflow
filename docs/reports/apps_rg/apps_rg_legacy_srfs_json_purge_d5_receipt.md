# apps_rg legacy SRFS JSON purge — D5 receipt

**Wave:** D5 — Prompt/judge vocabulary purge; remove JSON file envelope from PA/capsule/token-budget paths  
**Status:** PASS  
**Date:** 2026-05-22

## Scope completed

- **PA assembly** ([executive_summary_pa.py](apps_rg/runtime/sections/executive_summary_pa.py)): `build_executive_summary_assembly_input` no longer gates on `srfs_integration`; uses `format_graph_proof_pool_appendix` + graph product hard rules whenever `selected_fact_plan.facts` exist. `compile_executive_summary_prompt` appends forbidden-phrase guardrails when not already present in style oneshot path.
- **Evidence capsule** ([executive_summary_evidence_capsule.py](apps_rg/runtime/sections/executive_summary_evidence_capsule.py)): builds from `proof_pool_metadata` / plan only; drops `artifact_path_resolved`; `graph_proof_pool_used=True`, `selected_role_fact_set_used=False`; receipt adds `input_proof_pool_digest` (alias `input_srfs_digest` retained).
- **Token budget** ([executive_summary_token_budget.py](apps_rg/runtime/sections/executive_summary_token_budget.py)): `graph_product_pool_active()` replaces JSON-envelope detection; `srfs_mode_active` is a deprecated alias; `protected_fact_ids_from_payload` no longer reads `srfs_integration`.
- **Judge packet** ([executive_summary_judge_packet.py](apps_rg/runtime/judges/executive_summary_judge_packet.py)): render prompt labels `allowed_fact_packet` as graph proof pool (GRAPH_ONLY rubric SSOT unchanged from D2).

## Verification

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/test_executive_summary_prompt_dedup_v2.py \
  tests/_apps_contract/test_exec_summary_pa_w4c_guardrails.py \
  tests/_apps_contract/test_executive_summary_evidence_capsule_contract.py \
  tests/_apps_contract/test_executive_summary_token_budget_contract.py \
  tests/_apps_contract/test_executive_summary_judge_packet_srfs_rubric.py \
  tests/unit/apps_rg/runtime/sections/test_executive_summary_evidence_capsule.py \
  tests/unit/apps_rg/runtime/sections/test_executive_summary_token_budget.py \
  tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py::test_compiled_srfs_appendix_contains_pool_and_blocking_rules \
  -p pytest_timeout -q
```

**Result:** 29 passed, 1 skipped (live provider CLI slice in token_budget contract), 0 failed.

## FILES_CHANGED

- [executive_summary_pa.py](apps_rg/runtime/sections/executive_summary_pa.py)
- [executive_summary_evidence_capsule.py](apps_rg/runtime/sections/executive_summary_evidence_capsule.py)
- [executive_summary_token_budget.py](apps_rg/runtime/sections/executive_summary_token_budget.py)
- [executive_summary_judge_packet.py](apps_rg/runtime/judges/executive_summary_judge_packet.py)
- [apps-rg-legacy-srfs-json-purge-a8f3c1.md](.cursor/plans/apps-rg-legacy-srfs-json-purge-a8f3c1.md)
- Test fixtures under [tests/_apps_contract/](tests/_apps_contract/) and [tests/unit/apps_rg/runtime/sections/](tests/unit/apps_rg/runtime/sections/)

## NOTES

- Legacy marker names (`SRFS_*`, `srfs_style_only_oneshot`) retained for grep/tooling continuity; product path text now references augmented_skills_graph.
- Offline JSON write remains gated by `APPS_RG_OFFLINE_SRFS_JSON_WRITE=1` (D4); no runtime path requires `selected_role_fact_set_active.json`.
