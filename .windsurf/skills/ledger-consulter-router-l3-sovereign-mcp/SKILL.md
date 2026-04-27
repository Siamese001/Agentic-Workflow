---
name: ledger-consulter-router-l3-sovereign-mcp
description: Consult the router_l3_sovereign_mcp ledger before changing SovereignMcpRouter.resolve_violation key_id branches, MCP tool dispatch logic, or fallback chains. Captures every canon-key dispatch decision with status attribution.
trigger: model_decision
---

# Ledger Consulter — router_l3_sovereign_mcp

Captures `SovereignMcpRouter.resolve_violation()` dispatches in
`agentic_core/L3_orchestration/reasoning/engines/sovereign_mcp_router.py`.
Constitutional §29 non-matrix.

Each row stores: `selected` (l5_redteam|l4_memory_recall|l3_recovery|
l2_deepwiki_qa|l2_figma_truth|l1_sequential|l1_policy_fallback|l0_cleanup|
fallback|error|...), `cell={key_id_band, violation_class}`, `predicted_p_success`,
`eu_score` (1 on success status, 0 on error), `key_id`, `tool`, `authorized`,
`initialized`.

## When To Invoke

- Before changing the canon-key → MCP-tool dispatch table
- Before adding/removing a fallback chain
- Before tuning the key_id ranges (e.g. {19, 50} → l5_redteam)
- During calibration cycles when MCP-tool failure rate spikes

## Wave / Sunset

- **Wave**: W5.9 (final fleet rollout)
- **Sunset criterion**: 90 days zero §29 violations + 4 in-band weekly reports
