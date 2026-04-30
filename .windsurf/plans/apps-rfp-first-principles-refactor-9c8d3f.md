# Apps_RFP First-Principles Refactor — Phase 0 & 1 Only

Status: **W0+W1 done; W2+ gated on three-bucket completion**
Last updated: 2026-04-29
Created: 2026-04-29
Owner: Cascade
Plan slug: `apps-rfp-first-principles-refactor-9c8d3f`

## Phase B severity ranking

**MEDIUM-LOW.** Phase B audit identified:
- 4 engines + 7 reasoning agents
- 5 orchestrators: `RfpOrchestrator`, `section_orchestrator`, `enterprise_orchestrator`, `ComplianceMappingAgent`, `RequirementAnalysisAgent`
- Multi-agent decomposition is **defensible**: compliance/requirement/section are genuine RFP-domain stages
- Tone surface: low (RFP responses are structured)
- Anti-overfit risk: low — boilerplate risk exists but isn't intimacy/flattery

## Mission (this plan)

Land Phase 0 (ADG hotspot scan) and Phase 1 (AgentSpec authoring) for `apps_rfp/`. Unlike `apps_lic`/`apps_rg`, the multi-orchestrator topology is likely defensible. The AgentSpec should declare `agency.tier=MULTI_AGENT` with explicit justification — this is the test case for justified multi-agent in the fleet.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W0** | W0.1 | ADG hotspot scan of `apps_rfp/` | ~3k | Static bucket healthy | **Done** | `docs/reports/adg/apps_rfp_hotspots_20260429T205039Z.md` written |
| **W1** | W1.1, W1.2 | AgentSpec authoring + multi-agent justification ADR | ~6k | REQ schemas stable | **Done** | spec validates green with `agency.tier=MULTI_AGENT`; ADR drafted (status: Proposed pending W0.1 ADG verification) |
| **W2-W6** | (gated) | Judge demotion, hard-floor wiring, test matrix, E2E | (deferred) | Three-bucket-gap-remediation W1-W4 first | **Blocked** | |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **W0.1** | ADG hotspot scan | `apps_rfp/` static-bucket scan; rank orchestrators by fan-in/blast-radius | Multi-orchestrator fan-in may be high but defensible | 3k | Todo |
| **W1.1** | Author AgentSpec for RFP response assembly | `apps_rfp/config/specs/agent_spec.rfp_response.v1.0.0.yaml`; `agency.tier=MULTI_AGENT` with justification (3 distinct workflows, typed contracts, parallel) | This is the fleet's test of justified multi-agent | 4k | **Done** |
| **W1.2** | Draft ADR | `docs/architecture/adr/ADR-rfp-multi-agent-justification.md` (Status: Proposed) — verification gated on W0.1 ADG hotspot evidence; will move to Accepted or Rejected based on shared-state check | Per Constitutional §lowest-viable-agency | 2k | **Done (Proposed)** |

## Gating: Why W2+ Wait

W2+ assert runtime claims: "the 5 orchestrators communicate via typed contracts at runtime, not via shared mutable state"; this requires runtime evidence.

## ADG_GRAPH_LAYER_EVIDENCE (Constitutional §22)

W0.1 will populate. Targets:
- `mv_hotspot_centrality` for orchestrators
- `mv_dependency_cone_risk` showing whether orchestrators are cleanly independent or share unsafe state
- `mv_chokepoint_bridges` for `RfpOrchestrator`
- Semantic edges: `flows_to`, `writes_to` between orchestrators (looking for shared-state evidence)

## Out of Scope (DEFERRED_SCOPE)

Successor plan after three-bucket:
- W2: Demote in-run validators to overlay-only
- W3.1: Anti-overfit detector with RFP-specific lexicon (boilerplate, padding)
- W4: Test matrix with adversarial RFP content (poisoned requirements, conflicting compliance demands)
- W5.1: Possible orchestrator consolidation if W0.1 finds genuine sprawl
- W6: E2E with RFP fixture

## Definition of Done

- [x] `docs/reports/adg/apps_rfp_hotspots_20260429T205039Z.md` written
- [x] `agent_spec.rfp_response.v1.0.0.yaml` validates green with `agency.tier=MULTI_AGENT` and non-empty justification
- [x] ADR drafted (Status=Proposed)
- [ ] `ADG_GRAPH_LAYER_EVIDENCE` populated; ADR verification (Accepted vs Rejected) requires reading W0.1 report

## Next Action

W0.1 first. The hotspot scan will validate or invalidate the "multi-agent is defensible" claim — if orchestrators share state, the justification fails and tier should drop to WORKFLOW.
