# Apps_LIC First-Principles Refactor — Phase 0 & 1 Only

Status: **Phase 0 done; W1.1 done; W1.2 deferred (code-change phase); downstream gated on three-bucket**
Last updated: 2026-04-29
Created: 2026-04-29
Owner: Cascade
Plan slug: `apps-lic-first-principles-refactor-8a3c2e`
Predecessor concepts:
- `requirements/contracts/REQ-CROSS-APP-AGENTSPEC-001.contract.yaml`
- `.windsurf/plans/three-bucket-gap-remediation-069806.md` (gating dependency)
- Sibling: `.windsurf/plans/apps-rg-first-principles-refactor` (planned)

## Phase B severity ranking

**HIGH — second-heaviest in fleet after `apps_rg`.** Phase B audit identified:
- 20 reasoning agents (highest in fleet)
- 5 orchestrators (highest in fleet): `LicHealingOrchestrator`, `LicReflectionAgent`, `LicTemplateOptimizerAgent`, `enterprise_campaign_orchestrator`, `HOPPipelineExecutor`
- Voice-first design via `voice_profile.json` + `prompts.json` + `LicTemplateOptimizerAgent.py`
- Outreach messaging is the canary surface for forced warmth, fake intimacy, and mimicry
- Mirror of `apps_rg` rerun-loop antipattern (LicReflectionAgent + LicHealingOrchestrator)

## Mission (this plan)

Land Phase 0 (ADG hotspot scan) and Phase 1 (AgentSpec migration scaffold) for `apps_lic/`. Stop at the boundary where runtime validation becomes mandatory. Phases 2–6 (judge demotion, hard-floor veto, anti-overfit wiring, test matrix, E2E) are deferred until three-bucket-gap-remediation W1–W4 land and the runtime bucket lights up.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W0** | W0.1 | ADG hotspot scan of `apps_lic/` | ~3k | Static bucket healthy (verified); snapshot fresh | **Done** | `docs/reports/adg/apps_lic_hotspots_20260429T205039Z.md` written; 75 engines+agents counted, 15 top-fan-in entries surfaced |
| **W1** | W1.1 (done), W1.2 (deferred) | AgentSpec instance authoring; voice profile code migration deferred | ~6k | REQ-CROSS-APP-AGENTSPEC-001 schema stable | **W1.1 Done; W1.2 Blocked** | `apps_lic/config/specs/agent_spec.outreach_messaging.v1.0.0.yaml` validates green |
| **W2-W6** | (gated) | Judge demotion, anti-overfit wiring, test matrix, E2E | (deferred) | Three-bucket-gap-remediation W1-W4 must land first | **Blocked** | Runtime validation possible |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **W0.1** | ADG hotspot scan | ADG SQLite reads against `apps_lic/`; produces `docs/reports/adg/apps_lic_hotspots_<ts>.md` with `mv_hotspot_centrality`, `mv_dependency_cone_risk`, `mv_chokepoint_bridges` rows scoped to `apps_lic/*` | 20 agents may have sprawl beyond ADG visibility (dynamic dispatch); compensate via fan-in counts | 3k | Todo |
| **W1.1** | Author canonical AgentSpec instance for outreach messaging | `apps_lic/config/specs/agent_spec.outreach_messaging.v1.0.0.yaml` — `agency.tier=SINGLE_AGENT` justified, `voice_profile_ref` set, anti_overfit_profile tighter than fleet defaults | None | 4k | **Done** |
| **W1.2** | Migrate `voice_profile.json` to L4 durable form (code change in `LicTemplateOptimizerAgent.py`, `OutreachMessageAgent.py`, `MessageArchitectAgent.py`) | Voice profile is read in ~3-5 places; touch points need ADG fan-in confirm | 2k | **Blocked** (code change requires runtime validation) | `apps_lic/reasoning/*` |

## Gating: Why W2+ Wait for Three-Bucket Completion

The deferred phases (judge demotion, hard-floor veto, anti-overfit wiring, E2E) all assert **runtime claims** — "the demoted reflection agent did NOT trigger a rerun at runtime", "the hard-floor veto actually halted UWG", etc. These cannot be validated from the static bucket. Per `apps_rg-first-principles-refactor` plan and conversation 2026-04-29, three-bucket gap-remediation W1–W4 must land first.

## ADG_GRAPH_LAYER_EVIDENCE (Constitutional §22)

W0.1 will populate this section with citations to:
- `mv_hotspot_centrality` rows for `apps_lic/reasoning/*`
- `mv_dependency_cone_risk` rows showing blast radius of orchestrators
- `mv_chokepoint_bridges` rows for `LicHealingOrchestrator`
- `v_p1_mis_layered_infra` matches if any
- Semantic edges: `flows_to`, `controls_flow`, `emits_side_effect` from each orchestrator

Plan invalid until W0.1 closes and this section is populated.

## Out of Scope (DEFERRED_SCOPE candidates)

Once three-bucket completes, the following will be added in a successor plan:
- W2: Demote `LicReflectionAgent`, `LicHealingOrchestrator` to overlay-only (judge ≠ decider)
- W3.1: Wire shared `anti_overfit_detector_validator` against outreach traffic (canary calibration)
- W3.3: Instruction hierarchy enforcement (one-off "make this email warmer" cannot promote to durable)
- W4: Test matrix with adversarial cases — prompt-injection in outreach replies, over-personalization detection, conflicting voice/style prefs
- W5.1: Engine consolidation per W0.1 hotspot rank (target: 20 → ≤8 reasoning agents)
- W6: E2E with adversarial fixtures (poisoned recipient context)

## Definition of Done (this plan)

- [x] `docs/reports/adg/apps_lic_hotspots_20260429T205039Z.md` written
- [x] `apps_lic/config/specs/agent_spec.outreach_messaging.v1.0.0.yaml` validates green against `check_cross_app_contract_schema.py`
- [ ] Voice profile read sites converted to ref-based loading (W1.2 — deferred until three-bucket)
- [ ] `ADG_GRAPH_LAYER_EVIDENCE` section populated with mv_*/v_p* citations from W0.1 report

## Next Action

Run `python ops_scripts/ci/check_cross_app_contract_schema.py` against the new instance (after authoring) and confirm zero invariant violations. Do NOT execute W2+ until three-bucket-gap-remediation W4 strict-mode flip lands.
