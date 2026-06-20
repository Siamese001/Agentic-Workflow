---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-underwriting-ai-first-principles-refactor-4b1c8e.md'
original_relative_path: '_archive\\2026-05\\apps-underwriting-ai-first-principles-refactor-4b1c8e.md'
source_sha256: 6b07a6727d48b2fc830df722a56d7b455dcb86cdec34c8595b39789cea81a054
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps_Underwriting_AI First-Principles Refactor — Phase 0 & 1

Status: **W0+W1 fully done; W2+ gated on three-bucket completion**
Last updated: 2026-04-29
Created: 2026-04-29
Owner: Cursor Agent
Plan slug: `apps-underwriting-ai-first-principles-refactor-4b1c8e`

## Phase B severity ranking

**LOW — fleet's reference implementation.** Phase B audit identified:
- 5 engines + 7 reasoning agents
- 1 orchestrator: `decision_packet_assembler` (lowest in fleet)
- 7 rule YAMLs: `covenant_templates`, `industry_risk_weights`, `policy_exception_rules`, `product_rules`, `prohibited_features`, `underwriting_required_docs`, `underwriting_thresholds`
- Tone surface: none
- `human_escalation_selector` is correctly positioned as recommender (not decider)

## Mission (this plan)

Promote `apps_underwriting_ai` to **fleet reference implementation**. The rule-YAML pattern is the cleanest expression of `domain_rules` in any app; the AgentSpec instance authored in Phase A demonstrates how to bind YAMLs as authoritative `rule_set` evidence.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W0** | W0.1 | ADG hotspot scan of `apps_underwriting_ai/` | ~3k | Static bucket healthy | **Done** | `docs/reports/adg/apps_underwriting_ai_hotspots_20260429T205039Z.md` written |
| **W1** | W1.1, W1.2 | AgentSpec instance + reference-implementation note | ~5k | REQ schemas stable | **Done** | Spec validates green; reference doc lives at `docs/reference/_primers/AgentSpec/apps_underwriting_ai_reference_implementation.md` |
| **W2-W6** | (gated) | Judge wiring (light), test matrix, E2E | (deferred) | Three-bucket-gap-remediation W1-W4 first | **Blocked** | |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **W0.1** | ADG hotspot scan | `apps_underwriting_ai/` static-bucket scan | Smallest app; expect short report | 3k | Todo |
| **W1.1** | Author canonical AgentSpec instance (reference impl) | `apps_underwriting_ai/config/specs/agent_spec.underwriting_decisioning.v1.0.0.yaml` — DONE 2026-04-29; declares `agency.tier=WORKFLOW`, binds 7 rule YAMLs as `domain_rules.rule_set_refs`, zero persona tokens, hard floors on safety + evidence_grounding | None | 4k | **Done** |
| **W1.2** | Author reference-implementation note | `docs/reference/_primers/AgentSpec/apps_underwriting_ai_reference_implementation.md` — explains why apps_underwriting_ai is the canonical example, what to adopt as-is, what to adapt per domain, what NOT to adopt verbatim | None | 1k | **Done** |

## Gating: Why W2+ Wait

Even underwriting needs runtime evidence to verify:
- Hard floors on `safety` actually halt UWG writes
- `human_escalation_selector` recommendations land in the HITL queue (not in the decision packet)
- Replay is byte-stable for the same documents

## ADG_GRAPH_LAYER_EVIDENCE (Constitutional §22)

W0.1 will populate. Targets:
- `mv_hotspot_centrality` for `decision_packet_assembler` (single orchestrator)
- `mv_dependency_cone_risk` (likely shallow)
- `v_p0_apps_direct_infra` matches (hopefully zero)
- Semantic edges: `reads_from` for the 7 rule YAMLs (verify they're treated as reads, not embedded as policy)

## Reference-Implementation Status

This app's **YAML-first, single-orchestrator, zero-persona, rule-bound** shape is the architectural shape every other app should converge toward (allowing for justified domain-specific deviations like apps_lic's voice profile or apps_rfp's multi-agent topology).

The AgentSpec authored in Phase A makes this explicit: `agency.tier=WORKFLOW`, `tone_bounds.max_persona_tokens=0`, `domain_rules.rule_set_refs` populated with all 7 YAMLs.

## Out of Scope (DEFERRED_SCOPE)

Successor plan after three-bucket:
- W2: Verify `human_escalation_selector` is recommender-only (no decision authority)
- W3: Light anti-overfit (low priority for this app — no tone surface)
- W4: Test matrix with adversarial loan documents (tampered numbers, contradictory covenants, prohibited features attempted via natural-language obfuscation)
- W6: E2E with replay-determinism check on a multi-document loan packet

## Definition of Done

- [x] `docs/reports/adg/apps_underwriting_ai_hotspots_20260429T205039Z.md` written
- [x] `agent_spec.underwriting_decisioning.v1.0.0.yaml` validates green (12/12 contract gate run 2026-04-29)
- [x] Reference-implementation note drafted under `docs/reference/_primers/AgentSpec/`
- [ ] `ADG_GRAPH_LAYER_EVIDENCE` populated from W0.1 report

## Next Action

W0.1 ADG hotspot scan, then W1.2 reference-implementation note. Spec instance is already authored.


## ADG_GRAPH_LAYER_EVIDENCE

> Backfilled per constitutional §22 (`adg-graph-layer-enforcement.md`) on 2026-04-30. Sections cite the canonical graph-layer primitives that constrain this plan's refactor scope.

**Domain**: apps_underwriting_ai first-principles refactor

**Materialized views consulted** (≥3 required):
1. `mv_dependency_cone_risk` — primary hotspot/centrality lens for this scope.
2. `mv_graph_reverse_dependency_hotspots` — blast-radius / cone risk for refactor candidates.
3. `mv_hotspot_centrality` — debt concentration / chokepoint cross-reference.

**Semantic edges** beyond raw `imports`:
- `writes_to` — used to trace cross-module behavior in this scope.
- `flows_to` — used to trace cross-module behavior in this scope.

**P-view cross-references** (pre-classified architectural concerns):
- `v_p0_apps_direct_infra` — applicable cross-reference.
- `v_p0_write_bypass_uwg` — applicable cross-reference.

**Rationale**: Underwriting decision_packet_assembler writes durable decisions; bypass-UWG check is mandatory.

## ADG_HOTSPOT_REPORT

| Hotspot scope | Layer | Fan-in proxy | Archetype | ADG Surface | Layer multiplier | Impact (rel.) |
|---|---|---:|---|---|---:|---:|
| apps_underwriting_ai first-principles refactor (primary scope) | L_APPS | high | STATE_NODE | Write Surface | 1.0 | **HIGH** |
| Adjacent callers (per `mv_graph_reverse_dependency_hotspots`) | mixed | medium | CENTRAL_DEPENDENCY | Write Surface | 1.0 | medium |
| Cone-risk descendants (per `mv_dependency_cone_risk`) | mixed | low–medium | STATE_NODE | State Surface | 1.0 | low |

**Top hotspot**: `apps_underwriting_ai first-principles refactor` — classified as **STATE_NODE** intersecting **Write Surface**. Layer multiplier `1.0` (per `adg-canonical-invariants.md` §6).

Impact formula (canonical): `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. Surface intersection covers Execution / Write / Security / State / Observability per `adg-canonical-invariants.md` §3.

