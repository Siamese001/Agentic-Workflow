# Governance W2 dedupe report

Generated: 2026-06-07T12:01:14.655040+00:00

## Summary

- Duplicate triples before: **8**
- Duplicate triples after: **0**
- AlwaysApply count: **4** (Option A)

## Clusters

### author_gate
- No-loss: Tier-1 003 unchanged; emitter, anti-pattern, calibration, and hook references preserved in author-gate-enforcement.mdc
- Removed duplicates:
  - author-gate-enforcement.mdc: pipeline steps 1-9 (now points to 003)
  - workflows/author-gate-decision-gate.md: full procedural body
  - workflows/antipattern-author-gate.md: scanner walkthrough body

### adg
- No-loss: Full repair/hotspot procedures remain in adg-analysis-procedures.mdc; invariants in adg-canonical-invariants.mdc
- Removed duplicates:
  - workflows/adg-repair-loop.md: step-by-step repair body
  - workflows/adg-test-triage-gate.md: selector walkthrough body

### structured_reasoning
- No-loss: SR packet shape and hard limits preserved in rule + skill templates
- Removed duplicates:
  - workflows/structured-reasoning.md: SR_INTAKE through SR_SUMMARY phase bodies

### tavily
- No-loss: Routing table and §25 sole-MCP discipline remain in mcp-integration §8 and tavily-research skill
- Removed duplicates:
  - All six tavily workflow files: duplicated tool params and hard rules

### notion_plan
- No-loss: Path/format/authorization invariants remain in plan-location and plan-update-enforcement rules
- Removed duplicates:
  - plan-lifecycle-procedures.mdc: full procedural body (moved to plan-governance skill)

## Intentional duplication remaining
- **003 + author-gate-enforcement**: Tier-1 pipeline vs on-demand emitter/anti-pattern/calibration extensions (non-overlapping after W2 trim)
- **adg-canonical-invariants + adg-analysis-procedures**: Invariant vs procedural split by design
- **plan-location + plan-governance skill**: Invariant path/format vs procedural lifecycle
- **mcp-integration §8 + tavily-research skill stub**: Redirect stub until W4 skill split; routing table authoritative in mcp-integration
