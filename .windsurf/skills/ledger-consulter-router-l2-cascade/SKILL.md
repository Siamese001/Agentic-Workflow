---
name: ledger-consulter-router-l2-cascade
description: Consult the router_l2_cascade ledger for precedent before acting. HealingRouter / ConfidenceAwareExecutor decisions — tier (HIGH/MEDIUM/LOW/HITL), provider (deterministic/qwen/gemini_flash/gemini_pro/hitl), EU score, Brier component. Inherits the contract from `ledger-consulter`. Use when constructing or evaluating a routing decision in agentic_core/L2_execution/healers/.
trigger: model_decision
---

# Ledger Consulter — router_l2_cascade

## Purpose

Captures every routing decision made by `HealingRouter.route()` and
`ConfidenceAwareExecutor.execute()`, paired with the dispatch outcome bound on
the same row. The ledger is the §29 closed-loop evidence for the L2/cascade
router (matrix row #4 in `closed-loop-router-enforcement.md`).

Each row stores:

- `tier` — `HIGH` | `MEDIUM` | `LOW` | `HITL`
- `provider` — `deterministic` | `qwen` | `gemini_flash` | `gemini_pro` | `hitl`
- `target_model` — the concrete model id (e.g. `Qwen/Qwen2.5-32B-Instruct-AWQ`)
- `gate_applied` — `NO_OVERRIDE` | `GATE_1_RETRY_OVERRIDE` | `GATE_2_STRUCTURAL_*` | …
- `fingerprint` — stable hash of (failure_class × source_layer × retry_band × error_code)
- `predicted_p_success` — calibrated prior the router used (heuristic today)
- `eu_score` — Expected Utility used for the choice
- `score_band` — `tp` | `fp` | `tn` | `fn` | `unbound`
- `score_numeric` — Brier component `(predicted_p − actual)²`
- `latency_ms` — wall-clock dispatch latency

## When To Invoke

- Before authoring a tier/provider override (e.g., flipping `_PRO_REQUIRED_GATES`)
- Before changing a magic threshold in `confidence_scorer.py` /
  `confidence_aware_executor.py` / `healing_router.py` (`HIGH_THRESHOLD`,
  `MEDIUM_THRESHOLD`, `PRIMARY_*_THRESHOLD`, `COST_DEMOTE_*_USD`)
- Before adding a new entry to `_PRO_REQUIRED_GATES`
- Before adding or removing a value in `QWEN_DISALLOWED_FAILURE_TYPES`
- During promotion-gate evaluation (`L6/promo`): `wilson_lower ≥ 0.60`,
  `z ≥ 1.96`, `uplift > 0`, `n ≥ 30`
- Before any wave that touches `HealingRouter` or `ConfidenceAwareExecutor`

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("router_l2_cascade").lookup(
    query_text="<failure_class>:<source_layer>:<error_code> retry=N",
    filters={"event_kind": "route_decision", "score_band": "tp"},
    limit=10,
)
```

## Verdict → Action

| `verdict.strength` | Required behavior |
|---|---|
| `strong`       | Bias the current decision toward the precedent's tier/provider. Note alignment in any Author-Gate packet (`Precedent informing recommendation: aligned with ledger`). |
| `suggestive`   | Surface in Author-Gate packet body; do not auto-bias. |
| `none`         | State explicitly: `Precedent: ledger had no match (novel cell).` This is normal during cold-start before N≥30 rows accumulate per cell. |

## Promotion Gate Inputs

The `L6/promo` router consumes aggregated rows from this ledger to decide
whether a learned alternative threshold/cascade order beats the current one:

```sql
SELECT
    json_extract(prediction_json, '$.tier')        AS tier,
    json_extract(prediction_json, '$.provider')    AS provider,
    json_extract(prediction_json, '$.fingerprint') AS cell,
    SUM(CASE WHEN json_extract(outcome_json,'$.success')=1 THEN 1 ELSE 0 END) AS k,
    COUNT(*) AS n,
    AVG(score_numeric) AS brier_mean
FROM events
WHERE event_kind='route_decision' AND status='bound'
GROUP BY tier, provider, cell
HAVING n >= 30;
```

## Wave / Sunset

- **Wave**: W5.1 (plan `l2-cascade-router-closed-loop-wiring-c4d8a1`)
- **Writer hook**: `agentic_core/L2_execution/healers/healing_router.py`
  (`_emit_router_decision` + `_bind_router_outcome`)
- **Sunset criterion**: 90 consecutive days with zero §29 router-enforcement
  violations AND 4 consecutive in-band weekly calibration reports

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/router_l2_cascade_ledger.schema.sql`
- Calibration script: `ops_scripts/calibration/router_l2_cascade_calibration.py`
- Plan: `.windsurf/plans/l2-cascade-router-closed-loop-wiring-c4d8a1.md`
- Constitutional rule §29 + `closed-loop-router-enforcement.md`
