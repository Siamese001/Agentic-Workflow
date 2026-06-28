# apps_rg OTel Trace Reconciliation Consumer

## Fact

INVARIANT: apps_rg OTel traces are consumed post-run through `trace_reconciliation.json`, not as current-run control input.

## Scope

- `apps_rg/runtime/observability/trace_reconciliation.py`
- `apps_rg/runtime/spine/l6_shadow_eval_runner.py`
- `apps_rg/runtime/shadow/l6_handoff_packet.py`
- `apps_rg/runtime/shadow/l6_shadow_learning.py`
- `apps_eval/coverage/apps_rg.py`
- `apps_eval/l6_shadow_bridge.py`

## Canonical Pattern

- Local apps_rg receipts remain proof authority.
- Missing OTel emits `TRACE_UNAVAILABLE` and WARN rows, never an X1-X3/UWG/product failure.
- apps_eval consumes the reconciliation artifact as optional observability evidence.
- L6 receives reconciliation refs in package/handoff/learning outputs and turns trace gaps into future-run-only recommendations.

## Verification

Run:

```powershell
python -m pytest tests/unit/apps_rg/runtime/observability/test_trace_reconciliation.py tests/apps_rg/test_l6_v40_shadow_eval_runner.py apps_eval/tests/test_apps_rg_microstep_scorecards.py apps_eval/tests/test_l6_handoff_shape.py tests/e2e/test_l6_v40_apps_rg_apps_eval.py tests/unit/apps_rg/test_l6_microstep_observability.py -q
```

## Provenance

- plan: `plans/apps-rg-otel-trace-reconciliation-5d4c2b.md`
- discovered: 2026-06-28
- validated: 2026-06-28
