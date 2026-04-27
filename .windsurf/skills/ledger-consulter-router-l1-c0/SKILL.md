---
name: ledger-consulter-router-l1-c0
description: Consult the router_l1_c0 ledger for precedent before acting. RetrievalRouter decisions — intent_class, dim_tier, reranker_mode, SLO outcome (did the implied budget fit). Inherits the contract from `ledger-consulter`. Use when changing _DEFAULT_PLANS, SLO_BUDGETS_MS, intent classification regexes, or downgrade ladders in agentic_core/L1_cognition/reasoning/retrieval_router.py.
trigger: model_decision
---

# Ledger Consulter — router_l1_c0

## Purpose

Captures every routing decision made by `RetrievalRouter.route()` in
`agentic_core/L1_cognition/reasoning/retrieval_router.py`, paired with the
SLO outcome (did the chosen plan fit its latency budget at runtime).
Constitutional §29 closed-loop evidence for matrix row #3 (L1/c0).

Each row stores:

- `selected` — the `dim_tier` chosen (`tier_a` | `tier_b` | `tier_c` …)
- `cell` — `{intent_class, slo, has_filters, compound}` — the routing situation
- `fingerprint` — stable hash of the cell for posterior aggregation
- `predicted_p_success` — prior probability the plan would fit SLO
- `eu_score` — Expected Utility used for tier selection
- `plan` — full RetrievalPlan dict (transform, reranker, reflective, …)
- `score_band` — tp / fp / tn / fn / unbound
- `score_numeric` — Brier component `(predicted_p − actual)²`
- `latency_ms` — end-to-end retrieval latency

## When To Invoke

- Before authoring a new entry in `_DEFAULT_PLANS` or modifying an existing one
- Before tuning `SLO_BUDGETS_MS`, `_STAGE_BUDGETS_MS`, or `_DOWNGRADE_LADDER`
- Before adjusting an intent classifier regex (`_TRACE_RE`, `_INCIDENT_RE`,
  `_QUESTION_WORD_RE`, `_FILEPATH_RE`, `_DOTTED_SYMBOL_RE`, `_CODE_TOKEN_RE`,
  `_WHY_RE`, `_CONJUNCTION_RE`, `_METADATA_LAYER_RE`)
- Before adding a new `IntentClass` enum value
- During promotion-gate evaluation (`L6/promo`): same n≥30 / wilson≥0.60 floors as L2/cascade

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("router_l1_c0").lookup(
    query_text="<intent_class>:<slo>:<dim_tier>",
    filters={"event_kind": "route_decision", "score_band": "fp"},
    limit=10,
)
```

The `fp` filter surfaces over-confident predictions (predicted-fit, actually
missed SLO) — these are the rows that drive plan-table revisions.

## Verdict → Action

| `verdict.strength` | Required behavior |
|---|---|
| `strong`       | Bias the tier choice toward precedent. If 30+ FP rows for the same intent_class and tier, downgrade by one tier in `_DEFAULT_PLANS`. |
| `suggestive`   | Surface in Author-Gate packet body when changing the plan table. |
| `none`         | State explicitly: `Precedent: ledger had no match (novel cell).` Cold-start is normal until n≥30 accrues per cell. |

## Promotion Gate Inputs

```sql
SELECT
    json_extract(prediction_json, '$.cell.intent_class') AS intent,
    json_extract(prediction_json, '$.selected')          AS dim_tier,
    json_extract(prediction_json, '$.fingerprint')       AS cell,
    SUM(CASE WHEN json_extract(outcome_json, '$.success') = 1
              THEN 1 ELSE 0 END)                          AS k,
    COUNT(*)                                              AS n,
    AVG(score_numeric)                                    AS brier_mean,
    AVG(json_extract(outcome_json, '$.latency_ms'))       AS mean_latency
FROM events
WHERE event_kind = 'route_decision' AND status = 'bound'
GROUP BY intent, dim_tier, cell
HAVING n >= 30;
```

## Wave / Sunset

- **Wave**: W5.2 (plan `closed-loop-router-fleet-rollout-d8f2a3`)
- **Writer hook**: `agentic_core/L1_cognition/reasoning/retrieval_router.py`
  via `tools.ledgers.router_helper.RouterClosedLoopHelper`
- **Sunset criterion**: 90 consecutive days zero §29 violations + 4
  consecutive in-band weekly calibration reports

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Helper API: `tools/ledgers/router_helper.py`
- Schema: `.windsurf/schemas/router_l1_c0_ledger.schema.sql`
- Sibling: `.windsurf/skills/ledger-consulter-router-l2-cascade/SKILL.md` (proven pattern, L2/cascade)
- Plan: `.windsurf/plans/closed-loop-router-fleet-rollout-d8f2a3.md`
- Constitutional rule §29 + `closed-loop-router-enforcement.md`
