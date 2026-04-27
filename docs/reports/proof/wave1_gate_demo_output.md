# Wave 1 Gate Demo — BUG #1 prevention proof

## What this demonstrates

Same T2-tampered tree (mutate `app_id` to `TAMPERED_APP_ID` without
rehashing). Validator called twice:

1. **BUG #1 reverted** — `packet_path=None`, so the validator falls
   back to deriving the packet path from `packet.app_id` / `packet.scenario_id` (the legacy/pre-fix behavior).
2. **Fixed** — caller passes the trusted `packet_path` derived from
   the registered scenario, not from the loaded packet.

## Result table

| Field | BUG #1 reverted | Fixed |
|---|---|---|
| Scenario | `packet_path=None` | trusted `packet_path` |
| `validator.ok` | False | False |
| `caught` (verdict) | ✅ `True` | ✅ `True` |
| `reason_match` (mechanism) | ❌ `False` | ✅ `True` |
| **`fully_caught`** | ❌ **`False`** | ✅ **`True`** |
| `packet.app_id` (post-tamper) | `TAMPERED_APP_ID` | `TAMPERED_APP_ID` |
| Expected fail-reason substring | `hash mismatch` | `hash mismatch` |

## Fail-reason traces

### BUG #1 reverted

```
- packet_hash check failed: missing: C:\Git\Agentic-Workflow\artifacts\runtime\apps_proof\wave1_gate_demo\contracts\TAMPERED_APP_ID\uw_recommendation_only_v1\evidence_packet.json (path_source=trusted_path_unset)
```

### Fixed

```
- packet_hash check failed: hash mismatch: stored=963938975336f268bcad91ba33d225cc6985701e1209402002a972bf7d1fbdb3 recomputed=6ca797881584d4b7e5393ca5da927ff3b7f2a68cc29030d37cd5d951c33ec0ad (path_source=trusted)
```

## Interpretation

Pre-fix audit-pass-1 wave: T2 reported `caught=True` and the harness
marked it green. The new `reason_match` cross-check shows the catch
was via `missing` / wrong-mechanism — `fully_caught=False`. The
harness now gates on `all_fully_caught`, which would have flipped
the build RED the moment BUG #1 was introduced.

Same revert-and-prove pattern works for BUGs #2, #3, #6, #7, #9,
#10, #11, #12, #13 against the property tests + reason-match check.

## Reproduce

```
python docs/reports/proof/wave1_gate_demo.py
```

Inputs read from `artifacts/runtime/apps_proof/latest/` (last full
harness run). Tamper tree staged at
`artifacts/runtime/apps_proof/wave1_gate_demo/`.

