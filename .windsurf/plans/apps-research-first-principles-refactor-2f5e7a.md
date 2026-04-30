# Apps_Research First-Principles Refactor — Phase 0 & 1 Only

Status: **W0+W1 done; W2+ gated on three-bucket completion**
Last updated: 2026-04-29
Created: 2026-04-29
Owner: Cascade
Plan slug: `apps-research-first-principles-refactor-2f5e7a`

## Phase B severity ranking

**LOW — cleanest non-`apps_underwriting_ai` app in fleet.** Phase B audit identified:
- 3 engines + 7 reasoning agents (lowest engine count in fleet)
- 3 orchestrators: `enterprise_research_orchestrator`, `ResearchOrchestrator`, `research_multi_agent`
- Tone surface: low (research briefs are structured)
- Anti-overfit risk: citation injection, fabricated sources

## Mission (this plan)

Land Phase 0 (ADG hotspot scan) and Phase 1 (AgentSpec authoring) for `apps_research/`. Refactor here is mostly schema work — minimal structural change expected.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W0** | W0.1 | ADG hotspot scan of `apps_research/` | ~3k | Static bucket healthy | **Done** | `docs/reports/adg/apps_research_hotspots_20260429T205039Z.md` written |
| **W1** | W1.1 | AgentSpec authoring | ~4k | REQ schemas stable | **Done** | spec validates green; `agency.tier=SINGLE_AGENT` with retrieval-tool justification |
| **W2-W6** | (gated) | Judge demotion, source-fabrication detector, test matrix, E2E | (deferred) | Three-bucket-gap-remediation W1-W4 first | **Blocked** | |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **W0.1** | ADG hotspot scan | `apps_research/` static-bucket scan | Lean app; expect short report | 3k | Todo |
| **W1.1** | Author AgentSpec for research brief assembly | `apps_research/config/specs/agent_spec.research_brief.v1.0.0.yaml`; `agency.tier=SINGLE_AGENT`; `evidence_grounding` hard_floor=4 | Citation policy is load-bearing | 4k | **Done** |

## Gating: Why W2+ Wait

W2+ require runtime evidence:
- Citation pointers actually present in trace at runtime
- No fabricated sources slip through the judge
- Source-fabrication detector (extension of anti-overfit) needs runtime sealed outputs

## ADG_GRAPH_LAYER_EVIDENCE (Constitutional §22)

W0.1 will populate. Targets:
- `mv_hotspot_centrality` for orchestrators (small set)
- `mv_dependency_cone_risk` for `enterprise_research_orchestrator`
- Semantic edges: `reads_from` for retrieval boundaries

## Out of Scope (DEFERRED_SCOPE)

Successor plan after three-bucket:
- W2: Judge demotion (likely small surface)
- W3.1: Source-fabrication detector — research-specific extension of anti-overfit
- W4: Test matrix with citation-injection attacks, fabricated-source attacks, conflicting-source synthesis
- W6: E2E with research fixture

## Definition of Done

- [x] `docs/reports/adg/apps_research_hotspots_20260429T205039Z.md` written
- [x] `agent_spec.research_brief.v1.0.0.yaml` validates green
- [ ] `ADG_GRAPH_LAYER_EVIDENCE` populated from W0.1 report

## Next Action

W0.1 first. This app will likely close in the smallest scope.
