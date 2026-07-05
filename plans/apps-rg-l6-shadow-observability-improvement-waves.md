# apps_rg L6 Shadow Observability Improvement Waves

## Status Tables

### Wave Progress

| Wave | Scope | Status | Evidence |
|---|---|---|---|
| 0 | Branch, evidence, and contract snapshot | Complete | Baseline targeted pytest passed before edits |
| 1 | Contract and schema reconciliation | Complete | `scripts/governance/check_apps_rg_l6_observability_contract.py` |
| 2 | Deterministic L6 artifact closure order | Complete | Trace before microsteps, package before closure receipt |
| 3 | Section-to-apps_eval late binding | Complete | `l6_section_apps_eval_bindings.json` |
| 4 | Actionable RCA, patterns, and proposals | Complete | Expanded core L6 RCA/pattern/proposal payloads |
| 5 | Trace reconciliation monitoring and CI smoke | Complete | `l6_trace_observability_summary.json` and trace tests |
| 6 | Eval ladder coverage | Complete | Micro/lane/suite targeted pytest set |
| 7 | Documentation, receipts, and closeout | Complete | Run receipt and memory writeback captured |

### Phase Progress

| Phase | Status | Notes |
|---|---|---|
| Contract guard | Complete | Fails closed on unknown artifact roles, malformed L6 microsteps, package ambiguity, and trace advisory drift |
| Runtime artifacts | Complete | L6 remains post-run, additive, future-run-only |
| apps_eval binding | Complete | Bound proof is additive and does not rewrite section packages |
| Verification | Complete | Targeted tests and syntax checks passed |

## Wave 1

Contract reconciliation adds explicit evidence classes:

- `CONTRACT_ONLY_ADVISORY`
- `APPS_EVAL_BOUND_PROOF`
- `FAILURE_TERMINAL_ADVISORY`

The governance verifier validates registry roles, L6 microstep shape, package-role semantics, trace advisory behavior, and enum parity with Python constants.

## Wave 2

The section runner now emits trace reconciliation before microstep observations, writes the governed v40 package, then emits `l6_observability_closure_receipt.json`. The closure receipt verifies required post-run refs and repeats the no-current-run-mutation and no-direct-L4-write assertions.

## Wave 3

Post-X3 completion emits `l6_section_apps_eval_bindings.json` as an additive late-binding artifact. It references section packages and apps_eval rows by grain key without rewriting immutable section packages.

## Wave 4

Core L6 microstep outputs now include grouped RCA, recurrence-aware pattern metadata, and inert future-run proposal fields with gauntlet/UWG activation requirements.

## Wave 5

Trace reconciliation now emits `l6_trace_observability_summary.json` with OTel availability, provider mirror, X3 mirror, UWG mirror, warn count, and fail count. OTel unavailability remains advisory.

## Definition of Done

| Check | Status | Evidence |
|---|---|---|
| L6 remains post-run only | Pass | Package, closure, bridge, and proposals carry future-run-only assertions |
| No current-run rescue path | Pass | No X3/Exit mutation fields are introduced |
| No direct L4 write authority | Pass | L6 payloads assert no direct L4/durable write |
| Contract verifier passes | Pass | `python scripts/governance/check_apps_rg_l6_observability_contract.py --json` |
| Targeted eval ladder passes | Pass | 25 targeted pytest tests passed |
