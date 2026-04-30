---
name: ledger-consulter-apps-qna-pack-lifecycle
description: Consult the apps_qna_pack_lifecycle ledger for precedent before acting. apps_qna pack build / lint / self-eval / route-select / paste-set / promotion decisions — durable record surface that W4 NamespaceBandit + Wilson CI promotion gates + W5 system_learning consume for cross-interview transfer per constitutional §29. Inherits the contract from `ledger-consulter`. Use when emitting any apps_qna pack-lifecycle event, choosing a likely_questions route, composing a paste-set, or evaluating a promotion verdict.
trigger: model_decision
---

# Ledger Consulter — apps_qna_pack_lifecycle

## Purpose

apps_qna pack build / lint / self-eval / route-select / paste-set /
promotion decisions — durable record surface that W4 NamespaceBandit +
Wilson CI promotion gates + W5 system_learning consume for
cross-interview transfer.

Every row in `artifacts/ledgers/apps_qna_pack_lifecycle.sqlite` captures
a prediction paired with a later-bound outcome. Before committing to a
new decision of this class, look up precedent and bias the current
choice accordingly.

## When To Invoke

- Emitting an apps_qna pack-lifecycle event from
  `apps_qna/builder/card_pack_builder.py` (`event_kind="pack_build"`)
- Choosing a `likely_questions` route via the W4 NamespaceBandit
  (`event_kind="route_select"`)
- Composing a paste-set via the W4 paste-set bandit
  (`event_kind="paste_set_select"`)
- Evaluating a Wilson CI promotion verdict
  (`event_kind="promote_decision"`) — promote requires
  `wilson_lower ≥ 0.60`, `z_score ≥ 1.96`, `uplift > 0`, `n ≥ 30`
- Capturing a post-rehearsal interview outcome
  (`event_kind="interview_outcome"`) for cross-interview transfer in W5

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("apps_qna_pack_lifecycle").lookup(
    query_text="<current intent summary, e.g. 'route_select for Searce VP Americas'>",
    filters={"event_kind": "route_select"},
    limit=5,
)
```

## Verdict → Action

| `verdict.strength` | Required behavior |
|---|---|
| `strong`       | Bias current decision toward precedent; note alignment in packet/plan. |
| `suggestive`   | Surface precedent in Author-Gate packet or plan body; do not auto-bias. |
| `none`         | State explicitly: `Precedent: ledger had no match (novel case).` |

## Wave / Sunset

- **Wave**: W1.4 (apps-qna-spine-integration-e8f3a1 plan)
- **Writer hook**: `apps_qna/builder/card_pack_builder.py` — emits
  `pack_build` events on every successful build via
  `apps_qna.integrations.spine_adapter.emit_pack_lifecycle_event`. W4
  routers extend this surface for `route_select` / `paste_set_select`.
- **Sunset criterion**: apps_qna spine integration plan W5 closes AND
  4 consecutive interview-outcome calibration reports stable

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/apps_qna_pack_lifecycle_ledger.schema.sql`
- Plan: `.windsurf/plans/apps-qna-spine-integration-e8f3a1.md`
- Constitutional §29: closed-loop router enforcement (paired marker +
  `emit_ledger_event` contract)
