---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\cot-reflexion-self-consistency-config-7a3f1c.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\cot-reflexion-self-consistency-config-7a3f1c.md'
source_sha256: d1a229ee4a567c47c85f42a8779f7473aae0d1592fe181623823523a744e988c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: CoT/ToT + Reflexion + Self-Consistency Configuration

- **Slug**: `cot-reflexion-self-consistency-config-7a3f1c`
- **Tier**: T3 (cross-layer, apps_* + agentic_core)
- **Status**: Todo — backlog enhancement
- **Parent Plan Summary**: Introduce complexity-adaptive reasoning configuration (Chain-of-Thought, Tree-of-Thought, Reflexion, N self-consistency paths) at every transformer LLM callsite across `apps_*` (and `agentic_core` where needed). Goal: tie reasoning depth/breadth to task complexity, not hard-coded per callsite.

## Goal

Every transformer LLM invocation in `apps_*` and `agentic_core` reads reasoning strategy + `num_self_consistency_paths` from a complexity-aware config resolver, rather than a hard-coded or absent strategy. Provide SSOT defaults, per-app overrides, and recommendations based on task complexity band.

## Scope

| In Scope | Out of Scope |
|---|---|
| Audit of all LLM callsites in `apps_eval/`, `apps_exec/`, `apps_lic/`, `apps_research/`, `apps_rfp/`, `apps_rg/`, `apps_shared/`, `apps_underwriting_ai/` | New LLM providers |
| `agentic_core/L1_cognition/`, `agentic_core/L3_orchestration/` reasoning chokepoints | Model selection policy |
| SSOT config: `config/reasoning_strategy.yaml` with complexity→(strategy, N-paths) mapping | Runtime model swaps |
| Complexity resolver: `agentic_core/L1_cognition/reasoning/complexity_band.py` | Judge/verifier infra beyond self-consistency voting |
| Per-app overrides in `apps_*/config/reasoning_toggles_config.py` | |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | ENH1.1 | ADG audit: enumerate LLM callsites, classify by complexity band | 4000 | Todo | Report in `docs/reports/plans/cot-reflexion-self-consistency-audit.md` with callsite inventory |
| W2 | ENH1.2 | SSOT config + complexity resolver | 5000 | Todo | `config/reasoning_strategy.yaml` + resolver module with unit tests |
| W3 | ENH1.3 | Retrofit callsites to consume resolver | 7000 | Todo | All callsites refactored; no hard-coded `num_paths`; regression tests pass |
| W4 | ENH1.4 | Documentation + recommendation matrix | 2000 | Todo | ADR drafted; recommendation matrix in `docs/reference/03_L0_Routing/Prompt Assembly/` |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| ENH1.1 | LLM callsite audit | All `apps_*/engines/**/*.py`, `agentic_core/L1_cognition/**` | No inventory exists | 4000 | Todo |
| ENH1.2 | SSOT + resolver | `config/`, `agentic_core/L1_cognition/reasoning/` | Complexity banding is subjective | 5000 | Todo |
| ENH1.3 | Callsite retrofit | All apps_* engines | Large diff surface | 7000 | Todo |
| ENH1.4 | Docs + ADR | `docs/reference/` | — | 2000 | Todo |

## Recommendation Matrix (draft)

| Complexity | Strategy | N self-consistency paths |
|---|---|---|
| low | zero-shot | 1 |
| medium | CoT | 3 |
| high | CoT + Reflexion | 5 |
| critical | ToT + Reflexion | 7 |

## ADG_HOTSPOT_REPORT (to be filled in ENH1.1)

| Callsite | Layer | Archetype | Fan-in | Surface | Impact |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD |

## ADG_GRAPH_LAYER_EVIDENCE (to be filled in ENH1.1)

- MVs to query: `mv_hotspot_centrality`, `mv_graph_reverse_dependency_hotspots`, `mv_dependency_cone_risk`
- Semantic edges: `calls`, `flows_to`
- P-views: `v_p0_*` for orchestration chokepoints
