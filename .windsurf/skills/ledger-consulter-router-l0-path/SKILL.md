---
name: ledger-consulter-router-l0-path
description: Consult the router_l0_path ledger for precedent before changing PathRouter abstain logic, DEFAULT_ABSTAIN_THRESHOLD, or A/B/C/D path-selection rules. Captures every route_with_confidence() decision (A/B/C/D/R5).
trigger: model_decision
---

# Ledger Consulter — router_l0_path

## Purpose

Captures `PathRouter.route_with_confidence()` decisions in
`agentic_core/L0_routing/reasoning/path_router.py`. Constitutional §29 non-matrix.

Each row stores: `selected` (A|B|C|D|R5), `cell={threshold, payload_class}`,
`predicted_p_success` (= confidence), `eu_score` (= confidence − threshold),
`abstain` flag, `reason` from plan_abstain.

## When To Invoke

- Before tuning `DEFAULT_ABSTAIN_THRESHOLD`
- Before adding a new Path enum value
- Before changing the R5 abstain branch logic
- During calibration cycles for confidence-scoring upstream

## Wave / Sunset

- **Wave**: W5.5 (NEXT_STEP fulfillment)
- **Writer hook**: `agentic_core/L0_routing/reasoning/path_router.py`
- **Sunset criterion**: 90 days zero §29 violations + 4 in-band weekly reports
