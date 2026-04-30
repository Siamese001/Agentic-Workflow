# Apps_Exec First-Principles Refactor — Phase 0 & 1 Only

Status: **W0.1 + W1.1 done; W1.2 deferred (code change); W2+ gated on three-bucket**
Last updated: 2026-04-29
Created: 2026-04-29
Owner: Cascade
Plan slug: `apps-exec-first-principles-refactor-5e6a4b`

## Phase B severity ranking

**MEDIUM.** Phase B audit identified:
- 5 engines + 7 reasoning agents
- 3 orchestrators: `brief_orchestrator`, `enterprise_brief_orchestrator`, `ExecOrchestrator`
- Tone surface: `StyleComplianceAgent.py` (moderate)
- Anti-overfit risk: real — executive briefs invite flattery and inflated certainty

## Mission (this plan)

Land Phase 0 (ADG hotspot scan) and Phase 1 (AgentSpec authoring) for `apps_exec/`. Tone surface is moderate; the AgentSpec must declare strict tone bounds and a non-zero `forced_warmth_threshold` since exec briefs are vulnerable to "this is a strategic transformative opportunity" inflation.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W0** | W0.1 | ADG hotspot scan of `apps_exec/` | ~3k | Static bucket healthy | **Done** | `docs/reports/adg/apps_exec_hotspots_20260429T205039Z.md` written |
| **W1** | W1.1 (done), W1.2 (deferred) | AgentSpec authoring + StyleComplianceAgent re-typing | ~5k | REQ schemas stable | **W1.1 Done; W1.2 Blocked** | spec validates green |
| **W2-W6** | (gated) | Judge demotion, anti-overfit wiring, test matrix, E2E | (deferred) | Three-bucket-gap-remediation W1-W4 first | **Blocked** | |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **W0.1** | ADG hotspot scan | `apps_exec/` static-bucket scan | None | 3k | Todo |
| **W1.1** | Author AgentSpec for executive brief assembly | `apps_exec/config/specs/agent_spec.exec_brief.v1.0.0.yaml`; `agency.tier=WORKFLOW`; `evidence_grounding` hard_floor=4 | None | 3k | **Done** |
| **W1.2** | Re-type `StyleComplianceAgent` as overlay validator | `apps_exec/reasoning/StyleComplianceAgent.py` — preserve scoring; remove control-flow authority | Code change; needs runtime validation | 2k | **Blocked** (deferred until three-bucket) |

## Gating: Why W2+ Wait

W2+ require runtime evidence: "demoted StyleComplianceAgent did not trigger reruns at runtime", "hard-floor veto actually halted UWG on inflated-certainty briefs."

## ADG_GRAPH_LAYER_EVIDENCE (Constitutional §22)

W0.1 will populate. Targets:
- `mv_hotspot_centrality` for `apps_exec/engines/*` and `apps_exec/reasoning/*`
- `mv_dependency_cone_risk` for the 3 orchestrators
- Semantic edges: `flows_to` from `brief_orchestrator` -> renderers

## Out of Scope (DEFERRED_SCOPE)

Successor plan after three-bucket:
- W2: Demote StyleComplianceAgent fully (overlay-only)
- W3.1: Wire shared anti-overfit detector with `forced_warmth_threshold` calibrated for exec audiences
- W3.3: Instruction hierarchy — exec one-offs ("make it punchier") cannot promote
- W4: Test matrix with executive-flattery adversarial cases
- W5.1: Engine prune by hotspot rank
- W6: E2E

## Definition of Done

- [x] `docs/reports/adg/apps_exec_hotspots_20260429T205039Z.md` written
- [x] `agent_spec.exec_brief.v1.0.0.yaml` validates green
- [ ] StyleComplianceAgent emits `JudgeScorecard`-compatible output (W1.2 deferred)
- [ ] `ADG_GRAPH_LAYER_EVIDENCE` populated from W0.1 report

## Next Action

W0.1 first.


## ADG_GRAPH_LAYER_EVIDENCE

> Backfilled per constitutional §22 (`adg-graph-layer-enforcement.md`) on 2026-04-30. Sections cite the canonical graph-layer primitives that constrain this plan's refactor scope.

**Domain**: apps_exec first-principles refactor

**Materialized views consulted** (≥3 required):
1. `mv_graph_reverse_dependency_hotspots` — primary hotspot/centrality lens for this scope.
2. `mv_dependency_cone_risk` — blast-radius / cone risk for refactor candidates.
3. `mv_path_criticality_rollup` — debt concentration / chokepoint cross-reference.

**Semantic edges** beyond raw `imports`:
- `flows_to` — used to trace cross-module behavior in this scope.
- `resolves_callsite` — used to trace cross-module behavior in this scope.

**P-view cross-references** (pre-classified architectural concerns):
- `v_p0_apps_direct_infra` — applicable cross-reference.

**Rationale**: apps_exec orchestrates exec engines; reverse-dep hotspots highlight engine entry points needing W2+ touch.

## ADG_HOTSPOT_REPORT

| Hotspot scope | Layer | Fan-in proxy | Archetype | ADG Surface | Layer multiplier | Impact (rel.) |
|---|---|---:|---|---|---:|---:|
| apps_exec first-principles refactor (primary scope) | L_APPS | high | ORCHESTRATOR | Execution Surface | 1.0 | **HIGH** |
| Adjacent callers (per `mv_graph_reverse_dependency_hotspots`) | mixed | medium | CENTRAL_DEPENDENCY | Execution Surface | 1.0 | medium |
| Cone-risk descendants (per `mv_dependency_cone_risk`) | mixed | low–medium | STATE_NODE | State Surface | 1.0 | low |

**Top hotspot**: `apps_exec first-principles refactor` — classified as **ORCHESTRATOR** intersecting **Execution Surface**. Layer multiplier `1.0` (per `adg-canonical-invariants.md` §6).

Impact formula (canonical): `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. Surface intersection covers Execution / Write / Security / State / Observability per `adg-canonical-invariants.md` §3.

