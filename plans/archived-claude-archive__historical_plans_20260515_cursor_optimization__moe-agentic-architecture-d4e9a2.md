---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\moe-agentic-architecture-d4e9a2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\moe-agentic-architecture-d4e9a2.md'
source_sha256: 1a978e6b27bc269e752b842915fc7405039b28e30d30837c999bcfd611009427
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Mixture-of-Experts (MoE) in Agentic Architecture

- **Slug**: `moe-agentic-architecture-d4e9a2`
- **Tier**: T3 (cross-layer, L0 routing + L1 cognition + L3 orchestration + system_learning/arbitration)
- **Status**: Todo — backlog enhancement (do NOT implement yet)
- **Parent Plan Summary**: Formalize the existing agentic architecture as a first-class Mixture-of-Experts (MoE) system. Each `apps_*` is already a domain expert; this plan adds a **learned gating network**, **top-k sparse expert activation**, **load balancing**, **expert capacity**, and **auxiliary-loss-style telemetry** to turn ad-hoc routing into an SSOT MoE control plane at L0.

## Motivation

MoE (Shazeer 2017, Switch Transformer 2021, GShard 2020, Mixtral 2024) is the dominant architectural pattern for scaling specialized capability without scaling inference cost per query. The agentic system already has the structural pieces — domain apps, an arbitration engine, a routing chokepoint — but lacks the **formal gating + capacity + load-balancing contract** that makes MoE performant and auditable.

## Mapping: MoE Primitive → Existing Repo Asset

| MoE Primitive | Existing Asset | Gap |
|---|---|---|
| **Experts** | `apps_eval`, `apps_exec`, `apps_lic`, `apps_research`, `apps_rfp`, `apps_rg`, `apps_underwriting_ai` | Not declared as experts; no expert manifest |
| **Gating network (router)** | `agentic_core/L0_routing/` + `apps_shared/enforcement/Decomposedqueryagent*` | Rule-based, not learned/confidence-scored |
| **Top-k activation** | `system_learning/arbitration/engine.py` | Single-expert selection; no k>1 |
| **Load balancing** | — | Missing |
| **Expert capacity** | — | Missing (no per-expert token budget) |
| **Auxiliary loss / telemetry** | `system_learning/confidence/engine.py`, OTel spans | Not framed as MoE load-balance signal |
| **Expert dropout / fallback** | `L5_safety` guardrails | Not integrated with expert health |

## Goal

Ship an SSOT MoE control plane with:

1. Expert manifest (`config/moe/experts.yaml`) — declarative registry of each `apps_*` as an expert with capabilities, cost profile, capacity.
2. Gating network (`agentic_core/L0_routing/moe/gating.py`) — takes user prompt + context, emits top-k expert distribution with confidence scores.
3. Top-k dispatcher — invokes k experts in parallel, aggregates via arbitration engine.
4. Load-balance telemetry (OTel) — per-expert utilization, capacity saturation, gate entropy.
5. ADR documenting the MoE contract and deferred items (learned router training, gradient-free routing, etc.).

## Scope

| In Scope | Out of Scope |
|---|---|
| L0 gating network (rule + confidence-scored, not learned-by-gradient in this plan) | Training a neural router (deferred) |
| Top-k expert selection across all `apps_*` | New experts |
| Arbitration for aggregating k expert outputs | Model-level MoE (e.g., deploying Mixtral locally) |
| Expert capacity + load-balance telemetry | Full reinforcement-learning loop for router |
| Integration with runtime-HITL (ADR-023) for expert disagreement | — |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | ENH4.1 | ADG audit + MoE primitive↔asset mapping report | 4000 | Todo | Evidence report in `docs/reports/plans/moe-audit.md` with gap register |
| W2 | ENH4.2 | Expert manifest SSOT + gating contract design | 5000 | Todo | `config/moe/experts.yaml` schema + `docs/contracts/moe_gating.md` |
| W3 | ENH4.3 | Gating network (rule + confidence) + top-k dispatcher | 7000 | Todo | `agentic_core/L0_routing/moe/` module, unit-tested; top-k=2 end-to-end demo |
| W4 | ENH4.4 | Load-balance telemetry + capacity gating | 4000 | Todo | OTel spans emit expert utilization; capacity breach triggers fallback |
| W5 | ENH4.5 | ADR + deferred-items register (learned router, RL loop) | 2000 | Todo | `docs/architecture/adr/ADR-NNN-moe-control-plane.md` |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| ENH4.1 | MoE audit | `agentic_core/L0_routing/**`, `apps_*/`, `system_learning/arbitration/**`, `system_learning/confidence/**` | Existing router is rule-based; no expert manifest | 4000 | Todo |
| ENH4.2 | Expert manifest + gating contract | `config/moe/`, `docs/contracts/` | Capability taxonomy must match `Agentic Prompt Categories.txt` | 5000 | Todo |
| ENH4.3 | Gating network + top-k dispatcher | `agentic_core/L0_routing/moe/`, `system_learning/arbitration/` | Arbitration must reconcile disagreeing top-k outputs | 7000 | Todo |
| ENH4.4 | Load-balance telemetry + capacity | `agentic_core/L6_observability/`, `agentic_core/L5_safety/` | Capacity breach policy: fallback, queue, or reject | 4000 | Todo |
| ENH4.5 | ADR + deferred register | `docs/architecture/adr/` | — | 2000 | Todo |

## Design Decisions (for Author-Gate during W2)

1. **Routing granularity**: request-level (each user prompt routed once) vs. step-level (each orchestration step re-routed). Initial recommendation: request-level for W3; step-level deferred.
2. **Top-k**: k=1 (switch) vs. k=2 (classic MoE) vs. k>2. Initial recommendation: k=2 with weighted aggregation.
3. **Gating signal**: prompt embedding similarity to expert capability descriptor vs. classifier over hand-crafted features vs. LLM-as-router. Initial recommendation: hybrid — embedding similarity + LLM-as-router tiebreak.
4. **Aggregation**: weighted voting (current arbitration) vs. hierarchical (one expert critiques others) vs. consensus. Initial recommendation: weighted voting via existing arbitration engine.
5. **Capacity policy on breach**: fallback to next-ranked expert, queue, or reject. Initial recommendation: fallback + OTel anomaly emission.

Each decision above will emit a Author-Gate packet during W2 — not pre-committed.

## Dependencies

- **ENH1** (`cot-reflexion-self-consistency-config-7a3f1c`) — MoE gate output consumes complexity band for N-paths; intersection but not blocking
- **ENH3** (`prompt-categories-coverage-audit-b8f5d3`) — expert capability taxonomy shares vocabulary with the 9 prompt categories
- **ADR-023** (runtime HITL exit control) — expert disagreement above threshold triggers runtime-HITL escalation

## ADG_HOTSPOT_REPORT (to be filled in ENH4.1)

| Callsite | Layer | Archetype | Fan-in | Surface | Impact |
|---|---|---|---|---|---|
| TBD — current L0 router chokepoint | L0 | CENTRAL_DEPENDENCY | TBD | Execution | TBD |
| TBD — arbitration engine | L3 | ORCHESTRATOR | TBD | Execution | TBD |
| TBD — confidence engine | L1 | STATE_NODE | TBD | State | TBD |

## ADG_GRAPH_LAYER_EVIDENCE (to be filled in ENH4.1)

- **MVs**: `mv_hotspot_centrality`, `mv_graph_chokepoint_bridges`, `mv_graph_critical_path_blast_radius`, `mv_dependency_cone_risk`
- **Semantic edges**: `calls`, `flows_to`, `resolves_callsite`, `controls_flow`
- **P-views**: `v_p0_*` for L0 routing chokepoints; L3 orchestration P-views

## Risks

| Risk | Mitigation |
|---|---|
| Top-k increases inference cost k× | Capacity + caching; start with k=2 on high-confidence-gap queries only |
| Gate entropy collapse (always routes to one expert) | Auxiliary load-balance telemetry + alert threshold |
| Arbitration disagrees → HITL storm | Tie to ADR-023 escalation thresholds |
| Expert manifest drift from apps_* reality | CI gate `check_moe_expert_manifest.py` validates manifest ↔ apps_* code |

## Non-Goals

- Training a learned (neural) router with gradient updates — deferred, needs dedicated plan
- Replacing the existing arbitration engine — this plan EXTENDS it
- Token-level MoE inside a single LLM call — that is a model-architecture concern, not an agent-architecture concern

## Deferred Items (for ENH4.5 register)

1. Learned router with RL from HITL feedback
2. Step-level (not request-level) expert re-routing
3. Hierarchical MoE (experts of experts)
4. Cross-tenant expert sharing policies
5. Cost-aware routing (token-cost model per expert)
