# Prompt Reception Hardening — Follow-up Waves

**Plan ID:** prompt-reception-followups-a7b3c4
**Parent plan:** `@c:/Git/Agentic-Workflow/.windsurf/plans/prompt-assembly-reception-hardening-9c4e2b.md` (W0–W8 — COMPLETE)
**Created:** 2026-04-23
**Status:** Todo
**Tier:** T3 (cross-layer, multi-file, >5 files per wave)

## Parent Plan Summary

The 8-wave `prompt-assembly-reception-hardening-9c4e2b` plan landed in commits `f805d63a39`..`4d9bd6f164`, closing the primary prompt-reception gap by introducing reception-audit logging, provider-aware adapters (Anthropic / OpenAI / Gemini), structured slot taxonomy (E0 / M0 / H0), exemplar bank + retrievers (static + embedding), synthesis bridge, and CI gates. This follow-up plan captures the 9 scope items deliberately deferred during that work so the full reception-hardening design lands end-to-end.

## Goal

Complete the prompt-reception hardening story by:

1. Collapsing the `CompiledPromptArtifact` SSOT drift (two parallel dataclasses).
2. Replacing flat `system+user` strings with a structured `PromptMessages` IR so adapters receive slot maps, not joined blobs.
3. Migrating replay-cache keys to digest-over-structured-slots (currently hashes the legacy flat string).
4. Wiring the new adapter-v2 + exemplar eligibility through every app's `AgentSpec`.
5. Adopting the synthesis bridge in the three existing synthesis producers.
6. Shipping the concrete Gemini SDK client (W8 only shipped the adapter, not the client).
7. Adding golden-replay fixtures + wiring the two new CI gates into pre-commit.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W2b** | RH2B.1–3 | IR + SSOT + replay-key | 9 500 | adapter-v2 flag already in production-ready state; no breaking API changes | 🟡 Todo | Single `CompiledPromptArtifact`; `PromptMessages` IR threaded through gateway; replay hits stay ≥ baseline after key rotation |
| **W5b** | RH5B.1–2 | Per-app wiring + golden-replay | 7 000 | 8 apps have AgentSpec configs at canonical paths; fixture recording infra exists | 🟡 Todo | All 8 apps pass `check_exemplar_coverage`; golden-replay suite green against frozen fixtures; both CI gates wired to pre-commit |
| **W6b** | RH6B.1–3 | Synthesis producer adoption | 4 500 | W6 synthesis_bridge stable; no schema changes needed | 🟢 Todo | 3 producers emit governed C0 slots; reception audit shows synthesis_producer provenance |
| **W8b** | RH8B.1 | Gemini SDK client | 3 500 | Vertex AI credentials available in dev; SDK API stable | 🟡 Todo | Real Gemini call succeeds end-to-end through gateway |

**Total estimated tokens: 24 500** (🟢 GREEN — well under 60k per-wave ceiling)

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **RH2B.3** | PromptMessages IR | `agentic_core/L2_execution/reasoning/compiled_artifact.py`, `slot_assembly_engine.py`, `SovereignLLMGateway.py`, 3 adapters | Crosses assembler↔gateway contract; needs passthrough fallback | 4 000 | Todo |
| **RH5B.1** | Per-app AgentSpec wiring | `apps_*/config/agent_spec_config.py` × 8, `config/prompt_governance/exemplar_eligibility.yaml` | 8 parallel edits; each app has subtle config variance | 4 000 | Todo |
| **RH2B.1** | Replay-key migration | `agentic_core/L4_state/cache/`, `gptcache_client.py`, replay key builders | Migration discipline; accept key aliases for warm windows | 3 000 | Todo |
| **RH8B.1** | Gemini SDK client | `infrastructure/sdks_mcps/gemini_client.py` (new), `SovereignLLMGateway` provider wiring, `docs/reference/prompting/gemini_best_practices_2026.md` | Vendor API shape differs from adapter rendering; needs E2E smoke | 3 500 | Todo |
| **RH6B.1** | `KnowledgeSynthesisAgent` adoption | `apps_research/reasoning/KnowledgeSynthesisAgent.py`, tests | Agent currently writes flat text; needs refactor to emit slot | 1 500 | Todo |
| **RH6B.2** | `synthesis_engine_service` adoption | `apps_research/services/synthesis_engine_service.py`, tests | Same shape as 6B.1; can parallelize | 1 500 | Todo |
| **RH6B.3** | `core_synthesis_executor` adoption | `ops_scripts/dev_tools/L0_routing_scripts/core_synthesis_executor.py`, tests | Ops-layer caller; governance slightly different | 1 500 | Todo |
| **RH2B.2** | `CompiledPromptArtifact` SSOT unification | `agentic_core/prompt_governance/contracts/compiled_artifact_types.py` (delete), all importers (~12 files) | Fan-in 12; coordinated import update; deprecation shim for one release | 2 500 | Todo |
| **RH5B.2** | Golden-replay fixtures + pre-commit wiring | `tests/golden/prompt_reception/` (new), `.pre-commit-config.yaml`, `ops_scripts/ci/run_contract_gates.py` | Fixture recording discipline; must not leak secrets; CI runtime budget | 3 000 | Todo |

## Computed Priority Table

Priorities per constitutional §24 formula: `impact = coverage_gap_pct × layer_multiplier × (1 + log10(1 + fan_in)) × surface_boost`.

Layer multipliers: `L0=2.0, L5=2.0, L3=1.75, L4=1.75, L1=1.0, L2=1.0, L6=0.75`.
Surface boosts: `Security=1.5, Write=1.4, Execution=1.3, State=1.2, Observability=1.1, None=1.0`.

| Phase | Layer | Fan-in | Surface | Gap% | Impact | Band |
|---|---|:-:|---|:-:|:-:|:-:|
| **RH2B.3** PromptMessages IR | L2 | 8 | Execution | 100 | 254 | **P2** |
| **RH5B.1** Per-app AgentSpec | L2 | 8 | Execution | 100 | 254 | **P2** |
| **RH6B.1** KSA adoption | L3 | 4 | Execution | 100 | 251 | **P2** |
| **RH6B.2** synthesis_engine_service adoption | L3 | 3 | Execution | 100 | 237 | **P2** |
| **RH2B.1** Replay-key migration | L2 | 5 | State | 100 | 213 | **P2** |
| **RH8B.1** Gemini SDK client | L2 | 3 | Execution | 100 | 208 | **P2** |
| **RH6B.3** core_synthesis_executor adoption | L2 | 2 | Execution | 100 | 187 | **P2** |
| **RH2B.2** SSOT unification | L2 | 12 | Execution | 50 | 137 | **P3** |
| **RH5B.2** Golden-replay + pre-commit | L6 | 2 | Observability | 100 | 122 | **P3** |

## Recommended Execution Sequence

1. **RH2B.3** — PromptMessages IR (unblocks every downstream wiring step; highest leverage).
2. **RH5B.1** — Per-app AgentSpec once the IR contract is stable.
3. **RH2B.1** — Replay-key migration after IR lands (new keys derive from structured slots).
4. **RH8B.1** — Gemini SDK client (parallelizable with 5B.1; independent surface).
5. **RH6B.1 / RH6B.2 / RH6B.3** — Synthesis producer adoptions (parallelizable; identical shape).
6. **RH2B.2** — SSOT unification cleanup after IR consumers have migrated.
7. **RH5B.2** — Golden-replay fixtures + pre-commit last (captures the final-state behavior).

## ADG_HOTSPOT_REPORT

| File / Module | Fan-in | Layer | Archetype | Surface | Impact | Notes |
|---|:-:|---|---|---|:-:|---|
| `compiled_artifact_types.py` (dup) | 12 | L2 | CENTRAL_DEPENDENCY | Execution | 137 | RH2B.2 retires this |
| `SovereignLLMGateway.py` | 23 | L2 | ORCHESTRATOR | Execution | — | IR threading touches this |
| `slot_assembly_engine.py` | 9 | L2 | ORCHESTRATOR | Execution | — | IR producer |
| `apps_*/config/agent_spec_config.py` | 8 files × ~4 each | L_APP | CENTRAL_DEPENDENCY | Execution | 254 | RH5B.1 fans across |
| `gptcache_client.py` | 5 | L4 | STATE_NODE | State | 213 | Key format owner |
| `KnowledgeSynthesisAgent.py` | 4 | L3 | ORCHESTRATOR | Execution | 251 | RH6B.1 |
| `synthesis_engine_service.py` | 3 | L3 | ORCHESTRATOR | Execution | 237 | RH6B.2 |
| `core_synthesis_executor.py` | 2 | L2 | ORCHESTRATOR | Execution | 187 | RH6B.3 |

## ADG_GRAPH_LAYER_EVIDENCE

- **`mv_hotspot_centrality`** — confirms `SovereignLLMGateway.py` as central orchestrator (degree ≫ threshold).
- **`mv_graph_reverse_dependency_hotspots`** — surfaces `compiled_artifact_types.py` dup as a fan-in=12 chokepoint.
- **`mv_exemptions_near_critical_paths`** — no existing guardian exemptions touch the target files (clean slate).
- **`v_p2_duplicated_adapters`** — `CompiledPromptArtifact` appears as a known duplication candidate; RH2B.2 resolves it.
- **Semantic edges used**: `imports` (SSOT unification dependency tracing), `flows_to` (gateway → adapter), `writes_to` (cache key → gptcache).

Snapshot baseline: `artifacts/adg/adg_indexed_04232026_1345.sqlite` (regenerate after each wave).

## Governing ADRs

- `ADR-PROMPT-ASSEMBLY-001` — provider-aware structured prompt rendering (parent plan's ADR; still applicable).

## Deferred Scope Markers (auto-posted to Wave/Phase Convergence DB)

See computed priority table above. The 9 markers are emitted at the bottom of this document so the `post_cascade_deferred_scope_capture` hook can ingest them when Cascade references this plan.

---

DEFERRED_SCOPE: plan=prompt-reception-followups-a7b3c4 wave=W2b phase=RH2B.1 layer=L2 fan_in=5 surface=State coverage_gap_pct=100.0 est_tokens=3000 reason=Replay-key migration from flat-string hash to structured-slot digest

DEFERRED_SCOPE: plan=prompt-reception-followups-a7b3c4 wave=W2b phase=RH2B.2 layer=L2 fan_in=12 surface=Execution coverage_gap_pct=50.0 est_tokens=2500 reason=CompiledPromptArtifact SSOT unification remove duplicate dataclass

DEFERRED_SCOPE: plan=prompt-reception-followups-a7b3c4 wave=W2b phase=RH2B.3 layer=L2 fan_in=8 surface=Execution coverage_gap_pct=100.0 est_tokens=4000 reason=PromptMessages IR replace flat system plus user strings with structured envelope

DEFERRED_SCOPE: plan=prompt-reception-followups-a7b3c4 wave=W5b phase=RH5B.1 layer=L2 fan_in=8 surface=Execution coverage_gap_pct=100.0 est_tokens=4000 reason=Per-app AgentSpec response_schema and exemplar_eligible wiring across 8 apps

DEFERRED_SCOPE: plan=prompt-reception-followups-a7b3c4 wave=W5b phase=RH5B.2 layer=L6 fan_in=2 surface=Observability coverage_gap_pct=100.0 est_tokens=3000 reason=Golden-replay fixture set Anthropic plus OpenAI plus pre-commit hook wiring

DEFERRED_SCOPE: plan=prompt-reception-followups-a7b3c4 wave=W8b phase=RH8B.1 layer=L2 fan_in=3 surface=Execution coverage_gap_pct=100.0 est_tokens=3500 reason=Concrete Gemini SDK client wiring in infrastructure sdks_mcps plus best-practices reference doc

DEFERRED_SCOPE: plan=prompt-reception-followups-a7b3c4 wave=W6b phase=RH6B.1 layer=L3 fan_in=4 surface=Execution coverage_gap_pct=100.0 est_tokens=1500 reason=apps_research KnowledgeSynthesisAgent adoption of synthesis_bridge wrap_synthesis_output

DEFERRED_SCOPE: plan=prompt-reception-followups-a7b3c4 wave=W6b phase=RH6B.2 layer=L3 fan_in=3 surface=Execution coverage_gap_pct=100.0 est_tokens=1500 reason=apps_research synthesis_engine_service adoption of synthesis_bridge wrap_synthesis_output

DEFERRED_SCOPE: plan=prompt-reception-followups-a7b3c4 wave=W6b phase=RH6B.3 layer=L2 fan_in=2 surface=Execution coverage_gap_pct=100.0 est_tokens=1500 reason=ops_scripts core_synthesis_executor adoption of synthesis_bridge wrap_synthesis_output
