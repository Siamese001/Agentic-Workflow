---
name: ledger-consulter-router-l6-regret
description: Consult the router_l6_regret ledger for precedent before changing regret-accounting policy or top-offender attribution. Captures every RegretLedger.record() sample — chosen_reward, best_alternative_reward, decision_layer. Use when modifying any logic in agentic_core/L6_observability/regret_accounting.py or its consumers.
trigger: model_decision
---

# Ledger Consulter — router_l6_regret

## Purpose

Persists every regret sample recorded via
`RegretLedger.record()` in `agentic_core/L6_observability/regret_accounting.py`.
Constitutional §29 row #10.

Each row stores:
- `selected` — `decision_layer` string (e.g. `L0`, `L1`, ...)
- `cell` — `{decision_layer}`
- `predicted_p_success` — `chosen_reward` clamped to [0, 1]
- `eu_score` — `−regret` (negative regret = positive utility)
- `chosen_reward`, `best_alternative_reward`, `regret`

## When To Invoke

- Before adjusting the `top_offenders(k)` aggregation logic
- Before changing how regret is computed for a decision_layer
- During meta-learning cycles that pick "worst-decision-layer-this-week"
- When auditing past decisions for systemic regret patterns

## Minimal Query

```sql
SELECT
    json_extract(prediction_json, '$.cell.decision_layer') AS layer,
    SUM(json_extract(prediction_json, '$.regret'))         AS total_regret,
    COUNT(*)                                                AS n_samples,
    AVG(json_extract(prediction_json, '$.regret'))         AS mean_regret
FROM events
WHERE event_kind = 'route_decision'
GROUP BY layer
ORDER BY total_regret DESC;
```

## Verdict → Action

| `verdict.strength` | Required behavior |
|---|---|
| `strong`       | Bias attribution toward precedent (e.g. layer X is consistent worst offender). |
| `suggestive`   | Surface in Author-Gate packet body. |
| `none`         | State explicitly: `Precedent: ledger had no match.` |

## Wave / Sunset

- **Wave**: W5.3 (plan `closed-loop-l6-promo-regret-wiring-e3c5b9`)
- **Writer hook**: `agentic_core/L6_observability/regret_accounting.py`
- **Sunset criterion**: 90 consecutive days zero §29 violations + 4
  consecutive in-band weekly calibration reports

## See Also

- Schema: `.windsurf/schemas/router_l6_regret_ledger.schema.sql`
- Helper: `tools/ledgers/router_helper.py`
- Plan: `.windsurf/plans/closed-loop-l6-promo-regret-wiring-e3c5b9.md`
