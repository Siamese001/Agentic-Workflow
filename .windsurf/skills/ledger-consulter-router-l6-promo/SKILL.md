---
name: ledger-consulter-router-l6-promo
description: Consult the router_l6_promo ledger for precedent before changing promotion-gate parameters or thresholds. Captures every promotion_decision() verdict — Wilson CI bounds for candidate vs baseline, promote/reject outcome. Use when modifying min_n_each_arm, z (CI level), or any logic in agentic_core/L6_observability/promotion_gates.py.
trigger: model_decision
---

# Ledger Consulter — router_l6_promo

## Purpose

Captures every verdict from `promotion_decision()` in
`agentic_core/L6_observability/promotion_gates.py`. Constitutional §29 row #9.

Each row stores:
- `selected` — `"promote"` | `"reject"`
- `cell` — `{min_n_each_arm, z}`
- `predicted_p_success` — candidate's Wilson lower bound
- `eu_score` — `candidate.lower − baseline.upper` (positive when promoted)
- `candidate_successes`, `candidate_n`, `baseline_successes`, `baseline_n`
- Full Wilson intervals (lower/upper for both arms)
- `promote` flag + `verdict_reason` string

## When To Invoke

- Before tuning `min_n_each_arm` (default likely 30)
- Before changing the z-value (95% vs 99% CI)
- Before authoring auto-rollback policy that consumes promotion verdicts
- During §29 promotion-gate calibration cycles
- When deciding whether to require uplift > 0 in addition to Wilson dominance

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("router_l6_promo").lookup(
    query_text="recent promote decisions",
    filters={"event_kind": "route_decision"},
    limit=20,
)
```

## Verdict → Action

| `verdict.strength` | Required behavior |
|---|---|
| `strong`       | Bias the parameter change toward precedent. |
| `suggestive`   | Surface in Author-Gate packet body. |
| `none`         | State explicitly: `Precedent: ledger had no match.` |

## Wave / Sunset

- **Wave**: W5.3 (plan `closed-loop-l6-promo-regret-wiring-e3c5b9`)
- **Writer hook**: `agentic_core/L6_observability/promotion_gates.py`
- **Sunset criterion**: 90 consecutive days zero §29 violations + 4
  consecutive in-band weekly calibration reports

## See Also

- Schema: `.windsurf/schemas/router_l6_promo_ledger.schema.sql`
- Helper: `tools/ledgers/router_helper.py`
- Plan: `.windsurf/plans/closed-loop-l6-promo-regret-wiring-e3c5b9.md`
