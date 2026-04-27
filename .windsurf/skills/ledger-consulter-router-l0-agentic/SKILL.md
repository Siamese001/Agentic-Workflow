---
name: ledger-consulter-router-l0-agentic
description: Consult the router_l0_agentic ledger for precedent before changing AgenticRouter dispatch logic, min_confidence threshold, or intent classifier prototypes. Captures every route() decision with handler outcome.
trigger: model_decision
---

# Ledger Consulter — router_l0_agentic

## Purpose

Captures `AgenticRouter.route()` decisions in
`agentic_core/L0_routing/reasoning/agentic_router.py`. Constitutional §29 non-matrix.

Each row stores: `selected` (target_name), `cell={intent, n_targets}`,
`predicted_p_success` (= classifier confidence), `eu_score` (= confidence − min_confidence),
`intent`, `min_confidence`, `had_classifier`, `fallback_to_keywords`. Outcome:
`success` (True iff handler raised no error), `latency_ms`, `error`.

## When To Invoke

- Before tuning `min_confidence` (default 0.2)
- Before adding/removing a `RouteTarget` registration
- Before swapping intent classifier prototypes
- During calibration cycles when handler-error rates spike per (intent, target)

## Wave / Sunset

- **Wave**: W5.5 (NEXT_STEP fulfillment)
- **Writer hook**: `agentic_core/L0_routing/reasoning/agentic_router.py`
- **Sunset criterion**: 90 days zero §29 violations + 4 in-band weekly reports
