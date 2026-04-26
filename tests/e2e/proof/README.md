# E2E Runtime Proof Harness

Implements the `99_End_to_End_Runtime_Proof_and_Acceptance` spec series under
`docs/reference/99_End_to_End_Runtime_Proof_and_Acceptance/`.

This package owns **acceptance proof**, not runtime authority.

## Layout

| Module | Owns | Spec ref |
|---|---|---|
| `proof.contracts` | Contract dataclasses (ValidatedRequest..RuntimeExhaustBundle) + receipts | 99.3, 99.5, 99.6, 99.7 |
| `proof.digests` | Deterministic blake2b hashing + canonical JSON | 99.5 |
| `proof.bundle` | Proof bundle schema + IO + 99.1-compliant artifact filenames | 99.8 |
| `proof.scenarios` | Scenario registry: GP-001 + 9 route-coverage scenarios | 99.1, 99.2 |
| `proof.harness` | Reference deterministic emitter — produces a complete contract chain + OTEL span tree per scenario | 99.1, 99.4, 99.6 |
| `proof.validators` | Per-axis validators (contracts, trace, replay, no-bypass, groundedness, route coverage) | 99.2, 99.3, 99.4, 99.5, 99.6, 99.7 |
| `proof.runner` | Per-scenario aggregator → `ScenarioOutcome` with all receipts | 99.5, 99.6, 99.7 |

## Acceptance Commands (per 99.8)

```bash
# Full E2E proof suite
python -m tests.e2e.run_agentic_runtime_proof --scenario-set all \
    --emit-proof-bundle artifacts/e2e/latest

# Golden path only
python -m tests.e2e.run_agentic_runtime_proof --scenario GP-001 \
    --emit-proof-bundle artifacts/e2e/gp_001

# Route coverage
python -m tests.e2e.run_route_coverage_proof --all-routes \
    --emit-proof-bundle artifacts/e2e/routes

# Per-axis validators (consume an existing bundle)
python -m tests.e2e.validate_trace_tree     --proof-bundle artifacts/e2e/latest --strict
python -m tests.e2e.validate_replay         --proof-bundle artifacts/e2e/latest --strict
python -m tests.e2e.validate_no_bypass      --proof-bundle artifacts/e2e/latest --strict
python -m tests.e2e.validate_grounded_output --proof-bundle artifacts/e2e/latest --strict
```

## Pytest

```bash
python -m pytest tests/e2e/test_runtime_proof_harness.py -v
```

39 tests, < 2 seconds. Covers:
- emitter parametrized over all 10 scenarios
- determinism under same seed
- contract chain completeness
- per-validator failure-mode injection (missing evidence, broken lineage,
  digest tamper, L6-before-disposition, forbidden spans, evidence stripped)
- 99.1 artifact filename mapping
- all 6 CLI runners (subprocess invocation)
- bundle reproducibility across separate runs

## Where this stops being a simulator

The harness is a **reference** emitter. When canonical agentic_core layers
gain the ability to emit these contracts directly (U0 ValidatedRequest, L1
plan, L0 route, C0 evidence, PA prompt envelope, L2 sealed artifact, Exit
disposition, UWG receipt, L6 exhaust), live-emitter outputs should be diff'd
against this reference under the same scenarios. The validators stay the
same; only the emitter is replaced.

## Failure triage (per 99.8 §FAILURE TRIAGE MAP)

The runner prints failures namespaced by axis: `[contracts]`, `[trace]`,
`[replay]`, `[no_bypass]`, `[groundedness]`. Map back to the canonical
owner using 99.8's failure-triage map.
