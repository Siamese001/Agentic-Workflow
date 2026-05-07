# L6 Runtime Exhaust Schema

> Deferred scope item 4. Status: Documented. Date: 2026-05-07.

## Current Schema

The L6 runtime exhaust bundle is emitted by the R4 entrypoint after pipeline
completion. It contains:

```json
{
  "run_id": "string",
  "request_id": "string",
  "trace_root": "string",
  "app_name": "string",
  "disposition": "PASS|DENY|WARN|UNKNOWN",
  "stages": {
    "C0_CONTEXT": {"status": "PASS|BYPASSED|FAIL", "sub_stages": [...]},
    "L2_EXECUTE": {"status": "PASS|FAIL", "sub_stages": [...]},
    "EXIT_EVAL": {"status": "PASS|DENY|WARN", "sub_stages": [...]}
  },
  "timing_ms": {
    "total": 0,
    "c0": 0,
    "l2": 0,
    "exit": 0
  },
  "cache": {
    "r1a_hit": false,
    "r1b_hit": false,
    "d2_learned": false
  }
}
```

## Extension Points (when needed)

1. **Bandit feedback**: Add `bandit_arm`, `reward`, `context_vector` for L6/promo
2. **Regret tracking**: Add `regret_by_layer` for L6/regret router
3. **Cost tracking**: Add `token_usage`, `api_cost_usd` for cost observability
4. **Anomaly flags**: Add `anomalies[]` for runtime anomaly detection

## Integration

- Emitted by: `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py`
- Consumed by: L6/promo router, L6/regret router, L7 HowTrace builder
- Stored at: `artifacts/<app_name>/runs/<ts>/runtime_exhaust_bundle.json`
