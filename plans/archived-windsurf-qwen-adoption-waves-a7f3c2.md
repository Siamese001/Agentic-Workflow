---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\qwen-adoption-waves-a7f3c2.md'
original_relative_path: 'qwen-adoption-waves-a7f3c2.md'
source_sha256: 7bcd4c43d6f918d799ca6c594e6bfcc8d511ca8b5ef1ad87df5c2513929a583e
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Qwen vLLM Adoption — All-Waves Execution Plan

Plan ID: `qwen-adoption-waves-a7f3c2`
Tier: T3 (architectural, cross-layer, multi-file)
ADG snapshot: `artifacts/adg/adg_indexed_04242026_0625.sqlite`
Owner: Cascade (auto-execution approved)
Status: **Complete** (2026-04-24)

## Completion Receipt

| Wave | Commit SHA | Files | Status |
|------|-----------|-------|--------|
| A — Bootstrap | `ede34c389c` | 5 (plan + 4 src) | ✅ pushed to origin/main |
| B — Policy layer | `299e4cbcb3` | 4 src | ✅ pushed to origin/main |
| C — Retrieval factories | `4da45c1867` | 2 (1 new, 1 docstring) | ✅ pushed to origin/main |
| D — Cognition (semantic_enricher) | `b4c9565ae9` | 1 src | ✅ pushed to origin/main |

Verification: `py_compile` + import-smoke passed after every wave. All changes additive; no breaking behavior change for existing cloud-provider callers.

Deferred scope auto-captured to Notion Backlog DB via `.windsurf/scripts/defer.py` — 5 rows, scorer-assigned priority bands (F1/F2=P2, F3/F4/P1=P3).

## Problem

`QwenInferenceGateway` (L3 — `agentic_core/L3_orchestration/inference/qwen_vllm/reasoning/qwen_inference_gateway.py`) is production-ready but has **fan-in = 1** in production code (only `tools/ingestion/qwen_context_gateway.py`). All other LLM consumers hardcode paid cloud providers despite an L0 SSOT (`agentic_core/L0_routing/config/model_registry.py`) that defines `TIER_QWEN_LOCAL`, `QWEN_LOCAL_MODEL_ID`, and `VLLM_BASE_URL`.

## Objective

Thread `QwenInferenceGateway` into the top-impact LLM surfaces ranked by ADG fan-in × layer multiplier. Zero breaking changes (all new paths env-flag-gated or additive).

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| **A** | A1–A4 | Bootstrap: provider impl + judge provider | 40k | vLLM server reachable at `VLLM_BASE_URL`; `QwenInferenceGateway.infer` async contract stable | Todo | `LocalVLLMProvider` + `QwenJudgeProvider` exist; py_compile clean; commit pushed |
| **B** | B1–B3 | Policy layer: tier policy + consensus juror + healing dispatch | 45k | `QWEN_DISALLOWED_FAILURE_TYPES` honored; env flag `USE_QWEN_CONSENSUS_JUROR` gate | Todo | Qwen available as 4th juror; `HealTier.MEDIUM` dispatch wired to gateway; py_compile clean |
| **C** | C1–C4 | Retrieval: cache-control + citation adapter + dual-pass | 60k | Existing Anthropic paths untouched; Qwen fallback is additive | Todo | `QwenCitationAdapter` exists under `agentic_core/knowledge/retrieval/`; dual-pass fallback chain adds Qwen; py_compile clean |
| **D** | D1–D3 | Cognition: summarizer + classifier + enricher | 40k | All gated by env flag; default OFF; A/B under existing eval harness | Todo | Three call-sites accept `provider="qwen"` override; py_compile clean |

Total budget: ≈ 185k tokens (user cap: 1M, comfortable margin).

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| **A1** | `LocalVLLMProvider` adapter | `agentic_core/L2_execution/enforcement/_provider_local_vllm.py` (new) | async→sync bridge for `QwenInferenceGateway.infer` | 10k | Todo |
| **A2** | Wire `SovereignLLMGateway.LOCAL_VLLM` | `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` (patch `_create_default_provider`) | preserve `_PlaceholderProvider` fallback for unknown types | 5k | Todo |
| **A3** | `QwenJudgeProvider` | `agentic_core/evaluation/judges/qwen_judge_provider.py` (new) | mirror `GeminiJudgeProvider` shape; JSON rubric parse | 15k | Todo |
| **A4** | Register QwenJudgeProvider + tests | `agentic_core/evaluation/judges/provider_registry.py` (patch) + new test file | judge auto-discovery from env `JUDGE_PROVIDER` | 10k | Todo |
| **B1** | Qwen tier in `anthropic_model_tier_policy.py` | `agentic_core/knowledge/retrieval/anthropic_model_tier_policy.py` | respect `QWEN_DISALLOWED_FAILURE_TYPES`; ladder ordering | 15k | Todo |
| **B2** | Qwen juror in ConsensusEngine | `agentic_core/L1_cognition/enforcement/consensus_validator.py` | majority threshold auto-raises 2/3 → 3/4; env flag opt-in | 10k | Todo |
| **B3** | `dispatch_to_executor` MEDIUM → Qwen | `agentic_core/L2_execution/healers/healing_router.py` | HIGH/LOW/HITL sentinel paths untouched | 20k | Todo |
| **C1** | Qwen prompt-cache parity | `agentic_core/knowledge/retrieval/anthropic_cache_control.py` (patch) or new `qwen_cache_control.py` | vLLM prefix-cache differs from Anthropic cache-control | 15k | Todo |
| **C2** | Extract `QwenCitationAdapter` | `agentic_core/knowledge/retrieval/qwen_citation_adapter.py` (new; extracted from `tools/ingestion/qwen_context_gateway.py`) | no circular imports | 20k | Todo |
| **C3** | Qwen fallback in dual-pass orchestrator | `agentic_core/knowledge/retrieval/dual_pass_citation_orchestrator.py` (patch) | tier chain: Qwen → Anthropic → heuristic | 15k | Todo |
| **C4** | Qwen in `anthropic_prompt_renderer` | `agentic_core/knowledge/retrieval/anthropic_prompt_renderer.py` (patch) | rendered payload must match vLLM OpenAI wire format | 10k | Todo |
| **D1** | Qwen summarizer in EmbeddingSovereignAgent | `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py` (patch) | env flag `USE_QWEN_SUMMARIZER`; default OFF | 15k | Todo |
| **D2** | Qwen classifier | `agentic_core/L3_orchestration/reasoning/breadth_first_classifier.py` (patch) | deterministic temp=0 | 12k | Todo |
| **D3** | Qwen enricher | `agentic_core/knowledge/enrichment/semantic_enricher.py` (patch) | extractive only; no hallucination | 13k | Todo |

## Commit Cadence

One commit per wave (A, B, C, D). Each commit pushed to `origin/main` before next wave starts. Wave boundaries are rollback checkpoints per constitutional operational-gates policy.

## Gap Register

- **G1** — If `VLLM_BASE_URL` is unreachable at test time, `LocalVLLMProvider.generate()` must raise `ProviderError` cleanly; CircuitBreaker in `SovereignLLMGateway` absorbs.
- **G2** — `QwenInferenceGateway.infer` is `async`; `LLMProvider.generate` is sync. Use `asyncio.run` with existing-loop detection (pattern from `tools/ingestion/qwen_context_gateway.py`).
- **G3** — Do NOT run full ADG regen between waves (expensive; final regen at end only).
- **G4** — Do NOT modify `QWEN_DISALLOWED_FAILURE_TYPES` without a separate ADR — structural-failure disallow-list is a safety invariant.

## ADG Provenance

Backend: direct SQLite (`adg_indexed_04242026_0625.sqlite`). MCP serialization rule §25 enforced — no parallel MCP dispatches.

## Rollback

Each wave is a single commit. `git revert <sha>` reverts the wave. No migrations, no schema changes, no deletions — all changes are additive.

## ADG_HOTSPOT_REPORT

Ranked by impact = fan_in × layer_multiplier × surface_boost. Sourced directly from `artifacts/adg/adg_indexed_04242026_0625.sqlite` (no MCP — per constitutional §25 mitigation).

| # | Target file | Fan-in | Layer | Multiplier | Surface | Archetype | Impact |
|---|-------------|-------:|:-----:|:----------:|:-------:|:---------:|------:|
| 1 | `agentic_core/evaluation/judges/llm_judge.py` | 44 | L_SHARED | 1.0 | Observability Surface | CENTRAL_DEPENDENCY | 48.4 |
| 2 | `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | 20 | L2 | 1.0 | Execution Surface | ORCHESTRATOR | 26.0 |
| 3 | `agentic_core/knowledge/retrieval/anthropic_model_tier_policy.py` | 19 | L_PG | 1.0 | Security Surface | SAFETY_GATEKEEPER | 28.5 |
| 4 | `agentic_core/knowledge/retrieval/anthropic_cache_control.py` | 11 | L_PG | 1.0 | State Surface | STATE_NODE | 13.2 |
| 5 | `agentic_core/L3_orchestration/reasoning/breadth_first_classifier.py` | 6 | L3 | 1.75 | Execution Surface | ORCHESTRATOR | 13.7 |
| 6 | `agentic_core/knowledge/retrieval/dual_pass_citation_orchestrator.py` | 9 | L_PG | 1.0 | Execution Surface | ORCHESTRATOR | 11.7 |
| 7 | `agentic_core/L2_execution/healers/healing_router.py` | 9 | L2 | 1.0 | Execution Surface | ORCHESTRATOR | 11.7 |
| 8 | `agentic_core/L1_cognition/enforcement/consensus_validator.py` | 5 | L1 | 1.0 | Security Surface | SAFETY_GATEKEEPER | 7.5 |
| 9 | `agentic_core/knowledge/retrieval/anthropic_citation_adapter.py` | 7 | L_PG | 1.0 | Execution Surface | ORCHESTRATOR | 9.1 |
| 10 | `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py` | 7 | L2 | 1.0 | Execution Surface | CENTRAL_DEPENDENCY | 9.1 |
| 11 | `agentic_core/knowledge/enrichment/semantic_enricher.py` | 5 | L_PG | 1.0 | State Surface | STATE_NODE | 6.0 |
| 12 | `agentic_core/knowledge/retrieval/anthropic_prompt_renderer.py` | 4 | L_PG | 1.0 | Execution Surface | CENTRAL_DEPENDENCY | 5.2 |
| 13 | `agentic_core/evaluation/judges/provider_registry.py` | 2 | L_SHARED | 1.0 | Observability Surface | CENTRAL_DEPENDENCY | 2.2 |

Each target is currently hardcoded to a paid cloud provider (Anthropic / Gemini / OpenAI) despite the L0 `TIER_QWEN_LOCAL` SSOT existing. Waves A–D thread the Qwen gateway into each row in descending impact order (Wave A = rows 1, 2, 13; Wave B = rows 3, 7, 8; Wave C = rows 4, 6, 9, 12; Wave D = rows 5, 10, 11).

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized views consulted

1. **`mv_graph_reverse_dependency_hotspots`** — justifies ranking `llm_judge.py` (fan-in 44) as the top leverage point: judge surface is a `CENTRAL_DEPENDENCY` archetype across evaluation call paths.
2. **`mv_hotspot_centrality`** — confirms `SovereignLLMGateway.py` as an `ORCHESTRATOR` archetype; its `route_generation` method is the single outbound seam for non-judge LLM calls and already enumerates `ProviderType.LOCAL_VLLM` but dispatches to `_PlaceholderProvider` today.
3. **`mv_dependency_cone_risk`** — shows `anthropic_model_tier_policy.py` (fan-in 19) sits on the Security Surface as a `SAFETY_GATEKEEPER`; adding a Qwen tier below Claude-Haiku without modifying `QWEN_DISALLOWED_FAILURE_TYPES` preserves the structural-failure disallow invariant.
4. **`mv_path_criticality_rollup`** — confirms `healing_router.py` MEDIUM tier already targets Qwen in `TIER_CONFIG` but `dispatch_to_executor` returns sentinel results (Wave B / Phase B3 closes this gap).

### Semantic edges exercised

| Edge | Used where in this plan |
|------|-------------------------|
| `imports` | Fan-in counts for all 13 targets (see hotspot report above) |
| `flows_to` | `SovereignLLMGateway.generate` → `_PlaceholderProvider.generate` (current dead-end); Wave A Phase A2 reroutes to `LocalVLLMProvider.generate` |
| `resolves_callsite` | `QwenInferenceGateway.infer` resolved from L2 via local import in `_provider_local_vllm._run` and `qwen_judge_provider.judge` — respects the L2→L3 gravity direction (no inversion) |
| `reads_from` | L0 `model_registry.QWEN_LOCAL_MODEL_ID` and `VLLM_BASE_URL` read by every new Wave A/B component (SSOT compliance) |
| `writes_to` | None — this plan is strictly additive; no state mutation beyond in-memory provider registry |
| `emits_side_effect` | `QwenInferenceGateway` emits lifecycle-trace events (`_emit_records_execution_trace`, `_emit_records_telemetry_event`) — unchanged; new callers inherit them |

### P-view cross-references

* **`v_p0_apps_direct_infra`** — Wave B/C edits avoid apps_* layers entirely, so no new P0 violations.
* **`v_p1_mis_layered_infra`** — `LocalVLLMProvider` (L2) → `QwenInferenceGateway` (L3) via local import mirrors the existing pattern in `SovereignLLMGateway.route_generation` (L2) → `agentic_core.L2_execution.types.gateway_types` (local import at line 812). Verified legal.
* **`v_p2_duplicated_adapters`** — `_provider_local_vllm.py` is a new adapter; `_adapter_registry.py` already maps `LOCAL_VLLM → OpenAIMessageAdapter` for message rendering (separate concern). No duplication.
* **`v_p3_isolated_experimental`** — Wave D gates every cognition-surface change behind env flags (default OFF), so no experimental-code promotion risk.

### ADG Provenance

`backend=sqlite, snapshot=adg_indexed_04242026_0625.sqlite, query_method=direct_sqlite_read_no_mcp`

