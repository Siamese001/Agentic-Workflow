---
name: ledger-consulter-router-l3-reroute
description: Consult the router_l3_reroute ledger before changing RerouteCeiling thresholds, max_reroutes default, or per-request ceiling logic. Captures every attempt_reroute() decision (allow|ceiling_exceeded).
trigger: model_decision
---

# Ledger Consulter — router_l3_reroute

Captures `RerouteCeiling.attempt_reroute()` decisions in
`agentic_core/L3_orchestration/exit_control/reroute_governance.py`.
Constitutional §29 row #6.

## When To Invoke

- Before tuning `max_reroutes` default (currently 2 → max 3 dispatches)
- Before changing `RerouteCeilingExceededError` propagation rules
- During calibration cycles when reroute-exceeded rate spikes

## Wave / Sunset

- **Wave**: W5.8
- **Sunset criterion**: 90 days zero §29 violations + 4 in-band weekly reports
