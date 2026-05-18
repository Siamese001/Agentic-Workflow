# apps_rg X2 — remaining lanes active proof pool

## Summary

Extended ledger-primary active proof-pool membership validation to **headline**, **executive_summary**, **unify_narrative**, and **ibm_narrative**, reusing `evaluate_proof_pool_source_fact_gate` and writing `x2_source_fact_pool_receipt.json` on each lane run when the membership gate executes.

## Behavior

| Input class | Result |
|-------------|--------|
| SRFS slice IDs | PASS only when present in active SRFS pool; legacy gate id `x2_{section}_source_fact_ids_within_srfs_slice` |
| Broad skills ledger IDs | PASS only when in active ledger slice; gate id `x2_{section}_active_proof_pool_source_fact_ids` |
| Base resume fallback IDs | PASS only when `proof_pool_type=base_resume_fallback` and ID is in explicit fallback allowlist |
| JD / title / company / briefing surrogate IDs | FAIL (`jd_or_briefing_ids_rejected`) |
| Random / unknown IDs | FAIL (`unsupported_source_fact_ids`) |

Receipt fields align with `section_input_usage_ledger.json` (`proof_source`, `proof_pool_ref`, `proof_pool_digest`).

## Files

- Helper: `apps_rg/runtime/validators/proof_pool_source_fact_validation.py` (+ `proof_pool_x2_gate_id`)
- Validators: `headline_x2.py`, `executive_summary_x2.py`, `unify_narrative_x2.py`, `ibm_narrative_x2.py`
- Lanes: `headline_lane.py`, `executive_summary_lane.py`, `unify_narrative_lane.py`, `ibm_narrative_dispatch.py`
- Tests: `tests/_apps_contract/test_apps_rg_x2_ledger_primary_source_facts.py`

## Proof commands

```powershell
cd C:\Git\Agentic-Workflow-FRESH
$env:PYTHONPATH=(Get-Location).Path
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m compileall apps_rg -q
python -m pytest tests/_apps_contract/test_apps_rg_x2_ledger_primary_source_facts.py -q --tb=short --override-ini="addopts="
```

## Non-claims

- No product ALLOW
- No live Qwen/provider runtime proof in this wave
- X2/X3/judge thresholds not weakened
