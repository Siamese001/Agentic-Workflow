# L6 / apps_eval Microstep Alignment Invariant

## Fact

INVARIANT: L6 shadow observability must use the same `microstep_id` join key as `apps_eval` for apps_rg, while remaining post-run, read-only, and future-run-only.

## Scope

- `agentic_core/L6_observability/shadow_eval/microsteps.py`
- `apps_eval/l6_shadow_bridge.py`
- `apps_rg/runtime/shadow/l6_microstep_observability.py`
- `apps_rg/runtime/spine/l6_shadow_eval_runner.py`
- `apps_eval/registries/apps_rg_stage_microstep_contract.json`

## Canonical Pattern

- `apps_eval` grades microsteps and emits scorecard rows.
- L6 emits `L6MicrostepObservation` rows at the same `microstep_id` grain.
- Alignment is recorded in `l6_apps_eval_alignment.json`.
- L6 rows must keep `current_run_mutation_assertion=false`, `l4_write_assertion=false`, and `future_run_only=true`.

## Verification

Run:

```powershell
python -m pytest tests/unit/agentic_core/L6_observability/shadow_eval/test_microsteps.py tests/unit/apps_rg/test_l6_microstep_observability.py tests/e2e/test_l6_v40_apps_rg_apps_eval.py -q
python ops_scripts/ci/check_no_l6_current_run_mutation.py
python ops_scripts/ci/check_no_l6_direct_l4_write.py
```

## Provenance

- discovered: 2026-06-27
- validated: 2026-06-27
