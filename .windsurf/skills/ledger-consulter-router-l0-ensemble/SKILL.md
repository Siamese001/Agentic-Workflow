---
name: ledger-consulter-router-l0-ensemble
description: Consult the router_l0_ensemble ledger for precedent before changing EnsembleRouter base-model weights, decision_strategy, or MetaLearner architecture. Captures every route() decision and update_outcome() outcome with full ensemble features.
trigger: model_decision
---

# Ledger Consulter — router_l0_ensemble

## Purpose

Provides DURABLE backing for `EnsembleRouter` decisions and outcomes. The
in-memory `MetaLearner` evaporates on restart; this ledger captures the
training stream so model weights and meta-learner posteriors can be
reconstructed across process boundaries.

Each row stores: `selected` (selected_agent), `cell={n_models, decision_strategy}`,
`predicted_p_success` (=decision.confidence), `eu_score` (=mean−std confidence margin),
`decision_strategy`, `confidence`, `uncertainty`, `agent_agreement_score`,
`n_base_models`. Outcome: `success`, `latency_ms`, `meta_learner_target`,
`model_weights_after`.

## When To Invoke

- Before changing the `decision_strategy` (weighted_voting / meta_learning / simple_voting)
- Before adjusting base-model weights or reliability thresholds
- Before changing the MetaLearner architecture (hidden_dim, learning_rate)
- Before adding/removing a `BaseRoutingModel` from the ensemble

## Wave / Sunset

- **Wave**: W5.6 (NEXT_STEP fulfillment)
- **Writer hook**: `agentic_core/L0_routing/reasoning/ensemble_router.py`
- **Sunset criterion**: 90 days zero §29 violations + 4 in-band weekly reports
