---
status: decision-input
type: author-gate-decision-sheet
created: 2026-05-10
related:
  - docs/architecture/apps-rg-pre-consolidation-functionality-gap.md
  - docs/reference/_notes/Exit Criteria X1-X2-X3.md
---

# apps_rg Restoration — Author-Gate Decision Sheet

> 15 Author-Gate decisions across 6 phases. Boundary constraint: **apps_rg owns inputs/prompts/domain; agentic_core owns governance/orchestration/safety**. Per AG-RGGOV-6, apps_rg emits declarative ingress only — no runtime authority fields.

## Phases

| Phase | AGs | Theme |
|---|---|---|
| **A — Boundary contracts** | AG-1, AG-2, AG-3 | What apps_rg owns + how it talks to core |
| **B — Multi-provider LLM** | AG-4, AG-5, AG-6 | Restoring OPENAI/ANTHROPIC/GOOGLE without breaking AG-RGGOV-6 |
| **C — Safety mesh** | AG-7, AG-8, AG-9 | X1A-X1J + 29-gate G01-G29 + apps-specific gates |
| **D — Pipeline arch** | AG-10, AG-11, AG-12 | HOP, two-phase generation, healing |
| **E — Cross-cutting** | AG-13, AG-14 | HITL bridge, output enrichment, spine handoff |
| **F — Strategy** | AG-15 | Restore-vs-rebuild + phasing + backward-compat |

---

## Phase A — Boundary Contracts

### AG-1 — `AppsRgIngressPayload` extension shape

**Q**: how does apps_rg communicate 30+ pieces of domain config to core via U0?
**Blast**: 23+ categories (#1, #2, #16, #17, #25, #31, #34–43)

| | Option | Trade-off |
|---|---|---|
| | **a** Status quo (14 fields) | Cheapest; couples core to apps_rg paths |
| | **b** Path-refs only | Lightweight; brittle if files move |
| | **c** Structured-rich (~50KB) | Self-contained; bloats payload |
| ⭐ | **d** Manifest-bundled | apps_rg loads → `AppsRgProfileManifest` + digest → payload. Already a forward-ref in current contract. Survives AG-RGGOV-6 |

### AG-2 — Profile/config loading authority

**Q**: when do apps_rg's ~30 config files get read?
**Blast**: 6 profiles (#40), 18 domain_contract YAMLs (#39), 12 root configs

| | Option | Trade-off |
|---|---|---|
| | **a** Core eager-loads at L1 | Centralizes; redundant per request; couples core to apps_rg paths |
| ⭐ | **b** apps_rg eager-loads, manifest-bundles | One load per run; pairs with AG-1.d |
| | **c** Lazy-load on first reference | Minimal up-front cost; race conditions |

**Depends on**: AG-1

### AG-3 — Prompt mode selection authority

**Q**: who picks generation mode (`strategic_tailor` / `tailor_existing` / `generate_scratch` / `enhance_current` + healing/repair)?
**Blast**: #31, #32

| | Option | Trade-off |
|---|---|---|
| ⭐ | **a** Explicit user choice (CLI/wizard) | User authoritative; matches OLD pipeline |
| | **b** L1 derives from JD/resume signals | More autonomous; harder to audit |
| | **c** L0 route policy decides | Declarative; less flexible per-request |

---

## Phase B — Multi-Provider LLM

### AG-4 — AG-RGGOV-6 reconciliation

**Q**: AG-RGGOV-6 forbids "model/provider authority" in apps_rg, but P0 needs multi-provider. How?
**Blast**: #1, #44, #45 — user explicitly named this regression

| | Option | Trade-off |
|---|---|---|
| | **a** Strict AG-RGGOV-6 | Cleanest boundary; loses multi-provider |
| ⭐ | **b** Capability-requirement clause | apps_rg declares semantic requirements (`needs_strong_narrative`, `needs_long_context`); core L0 maps requirements → provider. Preserves "no provider authority" while enabling diversity |
| | **c** Modify AG-RGGOV-6 | Allow provider preference list. Simpler but explicit boundary breach |

### AG-5 — `provider_util` canonicalization

**Q**: `apps_shared/utils/provider_util.py` (real) vs `apps_shared/types/multi_provider_clients.py` (stub) — pick one?
**Blast**: #57

| | Option | Trade-off |
|---|---|---|
| ⭐ | **a** `utils/` canonical, retire `types/` stub | utils/ has real LiteLLM integration |
| | **b** `types/` canonical | Requires reimplementing LiteLLM |
| | **c** Hybrid (types/ for type, utils/ for impl) | Stable split; double-source-of-truth risk |

### AG-6 — Multi-provider env consumption point

**Q**: where do `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GOOGLE_API_KEY` get read?
**Blast**: #44, #45

| | Option | Trade-off |
|---|---|---|
| | **a** Core L2 reads at dispatch | Late binding; harder to audit |
| | **b** apps_shared at module load | Fastest; stale on env change |
| ⭐ | **c** `model_registry.py` resolves at L0 | Single resolution point; testable; matches existing location |

**Depends on**: AG-4, AG-5

---

## Phase C — Safety Mesh Wiring

### AG-7 — X1A-X1J invocation strategy

**Q**: how do the 10 X1 gates in `agentic_core/L3_orchestration/exit_eval/v6/x1_gates.py` fire?
**Blast**: #54, #61

| | Option | Trade-off |
|---|---|---|
| | **a** Thin binding inlines `run_all_x1_gates` | Smallest change; binding becomes 500+ LOC |
| | **b** Replace with `AppsRgIntegratedPipeline` | Removes parallel exit path #56; contract mismatch risk |
| ⭐ | **c** New `ExitReviewPacket` builder stage | New core stage between L2 and Exit; runs gates; passes verdicts to exit binding for X3 selection. Clean separation |

### AG-8 — 29-gate G01-G29 phasing

**Q**: how many of 29 runtime gates fire per dispatch?
**Blast**: #55

| | Option | Trade-off |
|---|---|---|
| | **a** Full 29 always | Max safety; high latency; many irrelevant |
| | **b** Critical subset (G09/G21/G22/G26/G28) | Addresses today's hallucination; misses ingress/policy/egress |
| ⭐ | **c** Rolling restoration | W1: G09+G21+G22 (output safety). W2: +G04+G06+G14. W3: +G01–03+G07–10. W4: full 29. Incremental; ships value early |
| | **d** Capability-driven | Apps_rg declares enabled gates. Violates "core owns runtime authority" |

**Depends on**: AG-7

### AG-9 — Apps-specific gate placement

**Q**: where do `verbatim_provenance`, `bullet_diversity`, `anti_overfitting` (4), `hallucination_detector`, `fact_check` live?
**Blast**: #5, #14, #61

| | Option | Trade-off |
|---|---|---|
| | **a** Move to core L5 validators | Centralizes; couples core to apps_rg domain |
| ⭐ | **b** Exit-stage callbacks via core registry | apps_rg owns gates; registers via `gate_registry`; core invokes per `app_id`. Mirrors `apps_rg.cert.fec_producer` pattern |
| | **c** Forge core equivalents, leave OLD orphaned | Wasted prior work |

**Depends on**: AG-7

---

## Phase D — Pipeline Architecture

### AG-10 — HOP pipeline restoration model

**Q**: 7-stage HOP (`clerk_extraction` → `data_enrichment` → `resume_generation` → `fact_check` → `bullet_diversity_gate` → `content_optimizer` → `generation_diagnostics`) — how does it map to L1-L0-C0-PA-L2-Exit?
**Blast**: #3, #4, #33

| | Option | Trade-off |
|---|---|---|
| ⭐ | **a** L3 reads HOP from apps_rg config, orchestrates | apps_rg authoritative on stages; core L3 owns dispatch. `l3_dag.yaml` already declares it (`l3_required: false` flips to `true`) |
| | **b** Collapse HOP into L2 sub-stages | Simpler L3; harder to inject gates between stages |
| | **c** Abandon HOP for atomic dispatch | Cheapest; loses determinism |

**Depends on**: AG-1, AG-2

### AG-11 — Two-phase generation wiring

**Q**: how to restore extract-then-narrate (prevents today's hallucination class)?
**Blast**: #21

| | Option | Trade-off |
|---|---|---|
| ⭐ | **a** PA template chaining | Phase-1 prompt + phase-2 prompt compiled into chained `CompiledPromptArtifact`. Leverages existing 8-template registry |
| | **b** L2 sub-stages (two LLM calls) | More plumbing in L2; observable per-phase |
| | **c** Separate dispatch loop (re-enter at C0) | Cleanest; doubles cost |

**Depends on**: AG-3, AG-10

### AG-12 — Healing cycle wiring

**Q**: how do `max_factual_loops=3`, `max_creative_retries=5` get restored?
**Blast**: #11, #32 (heal modes)

| | Option | Trade-off |
|---|---|---|
| | **a** L3 retry loop | L3 owns retry; couples L3 to apps_rg quality model |
| ⭐ | **b** Exit X3B → re-dispatch via L3 | X1D fails → X3B disposition → L3 reinvokes with healing-mode prompt. Bounded by L3 budget. Uses canonical X3 flow |
| | **c** Apps_rg `__main__` orchestrates retry | Apps_rg owns retry; violates "core owns orchestration" |

**Depends on**: AG-7, AG-8, AG-10

---

## Phase E — Cross-Cutting

### AG-13 — HITL bridge wiring

**Q**: 6 HITL triggers (`MISSING_BRIEF`, `STALE_BRIEF`, `UNSUPPORTED_CLAIM`, `LOW_CONFIDENCE`, `RELEASE_APPROVAL`, `CACHE_PROMOTION`) — how do they fire?
**Blast**: #17, #35

| | Option | Trade-off |
|---|---|---|
| | **a** Core L5 RuntimeAuthorGate reads apps_rg policy directly | Couples core to apps_rg paths |
| ⭐ | **b** Apps_rg-owned HITL emitter, core consumes via registry | Mirrors gate registry. apps_rg authoritative; core mediates per app_id |
| | **c** Direct payload field | Per-request triggers; payload bloat |

**Depends on**: AG-9

### AG-14 — Output enrichment + DOCX + spine handoff

**Q**: combine `RunReport` rich result, per-bullet provenance, DOCX export, cross-app delegation (`apps_research`, `apps_lic`).
**Blast**: #9, #18, #19, #20, #22, #23

| | Option | Trade-off |
|---|---|---|
| ⭐ | **a** Apps_rg-owned Exit-stage callbacks via registry | apps_rg owns output formats (domain-specific); core stays generic; same registry pattern. Spine handoff via `spine_manifest.yaml` |
| | **b** Move all to core Exit binding | Doesn't scale to N apps |
| | **c** Separate post-Exit script | Loses provenance threading |

**Depends on**: AG-9, AG-1

---

## Phase F — Strategy

### AG-15 — Restore-vs-rebuild + phasing + backward-compat

**Blast**: governs all phases

#### F-15.1 Restore-vs-rebuild

| | Option | Trade-off |
|---|---|---|
| | **a** Restore everywhere (un-quarantine + thread through new contracts) | Preserves prior work; high friction |
| | **b** Rebuild everywhere clean | Cleanest; loses domain knowledge |
| ⭐ | **c** Per-category | Restore: `agent_executor_util`, HOP definitions, anti-overfit gates, healing prompts, profile YAMLs. Rebuild: HOP orchestrator (now in core L3), Exit emitter, AppsRgIngressPayload extensions |

#### F-15.2 Phasing

| | Option | Trade-off |
|---|---|---|
| | **a** Big-bang multi-wave plan | Most coherent; high risk; long time-to-value |
| ⭐ | **b** Incremental rolling | W1: multi-provider LLM (P0). W2: safety mesh (X1A-X1J + critical G-gates). W3: HOP. W4: HITL + healing. W5: enrichment (DOCX, RunReport, spine handoff). W6: P3 polish |
| | **c** Parallel tracks | Compresses calendar; high merge risk |

#### F-15.3 Backward-compat

| | Option | Trade-off |
|---|---|---|
| | **a** Zero-breakage (additive) | Safest; double-code-path |
| ⭐ | **b** Feature-flag gated (`APPS_RG_RESTORATION_MODE=v2`) | Safe rollout; explicit cutover; clear A/B; flip default after W6 |
| | **c** Accept breakage windows per wave | Faster; user-facing breakage risk |

---

## Dependency Graph

```
AG-1 (payload) ──┬── AG-2 (config load) ── AG-3 (mode)
                 │                              │
                 │                              └── AG-10 (HOP) ── AG-11 (two-phase) ── AG-12 (healing)
                 │
                 ├── AG-7 (X1 invocation) ── AG-8 (29-gate) ── AG-9 (apps gates) ── AG-13 (HITL) ── AG-14 (output)
                 │
                 └── AG-4 (capability) ── AG-5 (provider_util) ── AG-6 (model_registry)
                                                                       │
                                                                       └── AG-15 (strategy)
```

## First Author-Gate Session — 4 Highest-Leverage Decisions

If you take ONE session, decide these 4:

1. **AG-1** — payload shape (gates Phases A, B, C, D, E)
2. **AG-4** — capability-requirement clause (unblocks multi-provider Wave 1)
3. **AG-7** — X1 invocation strategy (unblocks Phases C and D)
4. **AG-15.2** — phasing strategy (sets calendar expectation)

The remaining 11 cascade from these 4.

## Status

**Not yet decided.** Each AG above is an option-set, not a commitment. Open a future Author-Gate session and walk through the decisions in dependency order.
