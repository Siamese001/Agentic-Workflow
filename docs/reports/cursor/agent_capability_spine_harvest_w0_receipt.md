# Agent Capability Spine Harvest — W0 Receipt

**Plan:** [agent-capability-spine-harvest-e8f4a2.md](../../.cursor/plans/agent-capability-spine-harvest-e8f4a2.md)  
**Wave:** W0 — Model publication  
**Date:** 2026-05-25

## STATUS: PASS

## Deliverables

| Artifact | Path |
|----------|------|
| Decision model | [agent_capability_decision_model.md](agent_capability_decision_model.md) |
| Recommendations | [agent_capability_harvest_recommendations.md](agent_capability_harvest_recommendations.md) |
| 118-row matrix | [agent_capability_decision_matrix.json](agent_capability_decision_matrix.json) |
| Index | [agent_capability_decision_model_index.md](agent_capability_decision_model_index.md) |
| Matrix builder | [build_agent_capability_decision_matrix.py](../../tools/governance/build_agent_capability_decision_matrix.py) |
| Plan | [agent-capability-spine-harvest-e8f4a2.md](../../.cursor/plans/agent-capability-spine-harvest-e8f4a2.md) |

## COMMANDS_RUN

```text
python tools/governance/build_agent_capability_decision_matrix.py
  -> PASS (118 rows, summary by_pattern/by_tier emitted)
```

## Matrix summary

- **TIER_A_HARVEST_NOW:** 6 (`SemanticGatekeeper`, `AutonomyGuardian`, `SSOTFolderCleanup`, `EmbeddingSovereign`, `SovereignRAGManager`, `RedisSovereign`)
- **TIER_D_DELETE:** 16
- **P7_CI_OPS:** 66
- **Spine closure agents:** 0

## NOTES

- Notion Plans row: `36b27693-f55c-8175-b7ee-c1042f686bdf` (Not Started).
- Plan hardened v3 (`harvest-hardened-v3`): W0.5 YAML mechanical diff; W1 archive-first; Harvest grep proof set; contract validation checklists; W2-C0 cache stop rule; W3 gen/judge split; W5 strict Completed vs Partial.
- Next wave: **W0.5** — receipt SSOT: [agent_capability_harvest_author_gate_receipt.md](agent_capability_harvest_author_gate_receipt.md).
