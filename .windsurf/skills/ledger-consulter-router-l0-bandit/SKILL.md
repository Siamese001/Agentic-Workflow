---
name: ledger-consulter-router-l0-bandit
description: Consult the router_l0_bandit ledger for precedent before changing NamespaceBandit policy, the namespace-to-route admissibility list, or the Thompson sampling logic. Captures every choose() decision and update() outcome with the per-cell Beta posterior. Use when modifying agentic_core/L0_routing/reasoning/namespace_bandit.py.
trigger: model_decision
---

# Ledger Consulter — router_l0_bandit

## Purpose

Captures every routing decision made by `NamespaceBandit.choose()` and its
outcome via `.update()`. Constitutional §29 row #1.

Each row stores:
- `selected` — the chosen route arm
- `cell` — `{namespace, admissible}`
- `predicted_p_success` — posterior mean for chosen arm at decision time
- `eu_score` — Thompson sample value
- `posterior_alpha`, `posterior_beta` — pre-update posterior shape
- After bind: `posterior_alpha_after`, `posterior_beta_after`

## When To Invoke

- Before changing the `BetaPosterior` prior values
- Before adding/removing a route from a namespace's admissibility list
- Before modifying Thompson sampling vs Greedy/UCB switch
- During §29 promotion-gate decisions about which (namespace, route) cells
  have accumulated enough data to deprecate a fallback path
- Cross-router calibration: top-N regret-attributed (namespace, route)
  cells are candidates for L6/promo deprecation

## Minimal Query

```sql
SELECT
    json_extract(prediction_json, '$.cell.namespace') AS ns,
    json_extract(prediction_json, '$.selected')      AS route,
    SUM(CASE WHEN json_extract(outcome_json, '$.success')=1 THEN 1 ELSE 0 END) AS k,
    COUNT(*)                                          AS n,
    AVG(score_numeric)                                AS brier_mean
FROM events
WHERE event_kind='route_decision' AND status='bound'
GROUP BY ns, route
HAVING n >= 30;
```

## Verdict → Action

| `verdict.strength` | Required behavior |
|---|---|
| `strong`       | Bias the parameter change toward precedent. |
| `suggestive`   | Surface in Author-Gate packet body. |
| `none`         | State explicitly: `Precedent: ledger had no match.` |

## Wave / Sunset

- **Wave**: W5.4 (plan `closed-loop-router-fleet-rollout-d8f2a3` follow-on)
- **Writer hook**: `agentic_core/L0_routing/reasoning/namespace_bandit.py`
- **Sunset criterion**: 90 consecutive days zero §29 violations + 4
  consecutive in-band weekly calibration reports

## See Also

- Schema: `.windsurf/schemas/router_l0_bandit_ledger.schema.sql`
- Helper: `tools/ledgers/router_helper.py`
- Sibling routers: router_l1_c0, router_l2_cascade, router_l6_promo, router_l6_regret
