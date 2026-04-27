---
name: ledger-consulter-router-l4-uwg
description: Consult the router_l4_uwg ledger for precedent before changing DurableWriteGateway commit policy, validation rules, or anti-bypass enforcement. Captures every commit() decision (commit-allowed/blocked) with stage attribution.
trigger: model_decision
---

# Ledger Consulter — router_l4_uwg

## Purpose

Captures `DurableWriteGateway.commit()` decisions in
`agentic_core/L4_state/uwg/durable_write_gateway.py`. Constitutional §29 row #7.

Each row stores: `selected` ("commit"|"blocked"), `cell={source_surface, blast_radius}`,
`predicted_p_success` (1.0 if validation expected to pass else 0.5),
`eu_score` (1.0=committed, 0.0=blocked), `validation_status`, `block_stage`
("validation"|"lock_contention"|""), `n_state_diffs`, `n_target_surfaces`,
`tenant_id`. Outcome: `success`, `latency_ms`, `commit_receipt_id`,
`blocked_receipt_id`, `n_refresh_receipts`, `snapshot_after`.

## When To Invoke

- Before changing `_validate()` failure rules
- Before adjusting `ALLOWED_OPERATIONS` tuple
- Before modifying `NON_AUTHORIZED_SOURCES` frozenset (anti-bypass enforcement)
- Before changing the lock acquisition timeout or contention semantics
- During calibration cycles when blocked-rate spikes per (source_surface, blast_radius)

## Wave / Sunset

- **Wave**: W5.7 (next-wave fulfillment)
- **Writer hook**: `agentic_core/L4_state/uwg/durable_write_gateway.py`
- **Sunset criterion**: 90 days zero §29 violations + 4 in-band weekly reports
