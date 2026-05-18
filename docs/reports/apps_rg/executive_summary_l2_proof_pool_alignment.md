# Executive summary L2 proof-pool alignment

## Summary

`executive_summary` now resolves its **claim-support pool once** at L2 via `load_section_proof_for_lane` / `resolve_section_proof_pool`. The same `SectionProofPool` drives:

- L2 `selected_fact_plan` + `allowed_fact_ids`
- PA compiled prompt (`CLAIM SUPPORT POOL` in `INPUT_AUTHORITY`)
- `runtime_payload.proof_pool_metadata`
- `section_input_usage_ledger.json`
- X2 membership gate + `x2_source_fact_pool_receipt.json`

Legacy duplicate paths (`extract_allowed_facts` + hand-built `base_proof_pool_metadata` / `build_exec_summary_srfs_bundle` at L2) were removed from the lane entrypoint. SRFS integration envelope is still built when `pool.srfs_present` for SRFS-specific X2/PA appendix behavior.

## Resolution paths

| Condition | L2 proof source | PA block |
|-----------|-----------------|----------|
| `--selected-role-fact-set` | SRFS slice | `CLAIM SUPPORT POOL (SRFS)` |
| Default (ledger on disk) | `broad_skills_ledger` | `CLAIM SUPPORT POOL (BROAD SKILLS LEDGER)` |
| Ledger unavailable | `base_resume_fallback` | `CLAIM SUPPORT POOL (BASE RESUME FALLBACK)` |

JD, target title/company, and briefing remain targeting/context only (never valid `source_fact_ids`).

## Proof commands

```powershell
cd C:\Git\Agentic-Workflow-FRESH
$env:PYTHONPATH=(Get-Location).Path
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m compileall apps_rg -q
python -m pytest tests/_apps_contract/test_apps_rg_executive_summary_l2_proof_pool_alignment.py -q --override-ini="addopts="
```

## Non-claims

- No product ALLOW
- No live Qwen/provider runtime proof in this wave
