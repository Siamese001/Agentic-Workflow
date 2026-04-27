# L6 Closed-Loop Wiring — Promotion + Regret (constitutional §29 rows 9 & 10)

Plan ID: `closed-loop-l6-promo-regret-wiring-e3c5b9`
Status: In-progress
Created: 2026-04-26

## Problem

Constitutional §29 matrix rows 9 (`L6/promo`) and 10 (`L6/regret`) are NOT
wired closed-loop:

- `agentic_core/L6_observability/promotion_gates.py` exposes pure functions
  (`promotion_decision`, `auto_rollback_trigger`, `counterfactual_uplift`)
  but every verdict it returns is **lost**: nothing persists the verdict, the
  Wilson interval, or the (k, n) inputs. The Wilson + z + uplift floors
  required by `closed-loop-router-enforcement.md §29` are computed but the
  evidence is volatile.
- `agentic_core/L6_observability/regret_accounting.py` exposes `RegretLedger`
  with `.record(sample)` — but `_samples` is an in-memory list, lost on every
  process restart. Meta-learning that depends on regret accounting (e.g.
  identifying the worst-decision-layer last week) cannot be done.

L6 is the **feedback layer** — its decisions calibrate every other router.
Without durable L6 ledgers, the closed-loop pipeline below L6 (W5.1 L2/cascade
+ W5.2 L1/c0 + future router wirings) accumulates but never gets aggregated
into a promote/rollback or regret-attribution decision.

## Goal

1. Add `router_l6_promo` ledger + wire `promotion_decision()` to emit a
   ROUTER_DECISION marker AND write a durable row carrying the verdict +
   Wilson intervals on every call.
2. Add `router_l6_regret` ledger + wire `RegretLedger.record()` to also
   persist each sample to the durable ledger (in addition to the in-memory list).
3. Use `tools.ledgers.router_helper.RouterClosedLoopHelper` for both — proves
   the helper generalizes to non-route()-style callsites (function-level for
   promo, method-level for regret).

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | 1.1–1.6 | Two L6 ledgers + two router wirings + tests | ~14000 | in-progress |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|----------|-------|-------|-------------|-------------|--------|
| 1.1 | router_l6_promo schema + registry + skill + sqlite | new schema; +1 LedgerSpec; new SKILL.md | additive only | 2000 | pending |
| 1.2 | router_l6_regret schema + registry + skill + sqlite | same | additive only | 2000 | pending |
| 1.3 | Wire `promotion_decision()` | inject helper-based emission alongside the verdict return | preserve existing API + tests | 3000 | pending |
| 1.4 | Wire `RegretLedger.record()` | persist sample to durable ledger | preserve existing API + tests | 3000 | pending |
| 1.5 | Unit tests for both wirings | new test file | full coverage | 3000 | pending |
| 1.6 | Apply schemas, run gates, commit, push | verification | none | 1000 | pending |

## ADG_GRAPH_LAYER_EVIDENCE

This wave is **additive infrastructure** — pure-function `promotion_gates` and
the `RegretLedger` class get NEW telemetry side effects; no public API changes.

- **Materialized views**: `mv_dependency_cone_risk` shows
  `agentic_core/L6_observability/` is a stable hub — adding new ledgers under
  `router_l6_*` matches the existing topology for `router_l1_c0` and
  `router_l2_cascade`.
- **Semantic edges added**: `promotion_gates → router_helper (uses)`,
  `regret_accounting → router_helper (uses)`, `router_helper →
  router_l6_promo.sqlite (writes_to)`, `router_helper →
  router_l6_regret.sqlite (writes_to)`. No new cross-layer violations.
- **P-views**: `v_p1_zero_caller_infra` — every new schema/skill has at least
  one caller from day one (the wiring + tests).

## ADG_HOTSPOT_REPORT

| File | Layer | Fan-in | Archetype | Surface | Impact |
|------|------:|-------:|-----------|---------|-------:|
| `promotion_gates.py` | L6 | medium | SAFETY_GATEKEEPER | Observability | additive wiring; pure functions stay pure-function-callable |
| `regret_accounting.py` | L6 | medium | SAFETY_GATEKEEPER | Observability | additive `record()` side effect |
| `router_helper.py` | tools | growing | CENTRAL_DEPENDENCY (target) | Observability | now reused by 3 callers (HealingRouter wired bespokely; L1/c0 + L6/promo + L6/regret via helper) |

## Test Strategy

`tests/unit/agentic_core/L6_observability/test_l6_closed_loop.py`:

1. `promotion_decision()` returns same `PromotionVerdict` as before
2. After call, ledger has 1 row with verdict in prediction_json
3. `RegretLedger.record()` adds sample to in-memory AND durable
4. Both wirings are fail-soft (helper unavailable → no exception)
5. Multi-call accumulation works correctly

## Verification

- 24 helper tests + 38 L2/cascade + 8 L1/c0 + new L6 tests all pass
- check_ledger_writer_contract OK (14 ledgers conform)
- Live smoke: real `promotion_decision()` writes a row to
  `artifacts/ledgers/router_l6_promo.sqlite`
