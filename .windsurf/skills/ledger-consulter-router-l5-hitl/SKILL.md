---
name: ledger-consulter-router-l5-hitl
description: Consult the router_l5_hitl ledger before changing HITLApprovalGate verdict handling, escalation rules, or the modify-then-reclear / reject / return_to_l1 paths. Captures every evaluate() decision.
trigger: model_decision
---

# Ledger Consulter — router_l5_hitl

Captures `HITLApprovalGate.evaluate()` decisions in
`agentic_core/L5_safety/runtime_gates/g06_hitl_approval.py`.
Constitutional §29 row #8.

Each row stores: `selected` (approve|modify|reject|return_to_l1|escalate|pending),
`cell={verdict_class}`, `predicted_p_success`, `eu_score` (negative latency_ms/1000),
`verdict`, `review_requested`, `latency_ms`, `disposition`,
`stop_condition_violated`.

## When To Invoke

- Before changing the `verdict` → `disposition` mapping
- Before adjusting the modify-then-reclear semantics (preserves L5 re-clearance)
- Before tuning escalation packet initialization
- During calibration cycles when HITL_rejection_rate or HITL_modify_rate spikes

## Wave / Sunset

- **Wave**: W5.8
- **Sunset criterion**: 90 days zero §29 violations + 4 in-band weekly reports
