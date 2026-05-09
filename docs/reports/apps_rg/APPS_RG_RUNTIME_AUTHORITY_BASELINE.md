# APPS_RG_RUNTIME_AUTHORITY_BASELINE

**Plan:** `apps-rg-declarative-ingress-only-spinal-governance-c8b3e1`
**Wave:** W1 (ADG + filesystem baseline — no edits)
**Date:** 2026-05-09
**Snapshot:** `artifacts/adg/adg_indexed_05052026_0722.sqlite` (140 743 nodes, 863 353 edges)
**ADG health:** green (sqlite + redis + graph projection all healthy)

---

## Executive Summary

The plan's initial 8 quarantine targets are the **tip of the iceberg**. The ADG reveals
**~43 distinct live-path files** under `apps_rg/` matching §10 forbidden patterns —
roughly **18 % of the 241 live `apps_rg/` modules**. W4 scope MUST expand from 8 named
files to a structured sweep of all 43.

Critical findings:

1. **4 files invoke external LLM providers directly** — bypassing `SovereignLLMGateway` entirely.
2. **`apps_rg/prompt_assembly/`** is a full prompt-assembly subtree owned by `apps_rg`
   (`contracts.py`, `compiler.py`, `slot_mapper.py`, `provider_request.py`) — direct §10 violation.
3. **`apps_rg/l2_recipe/steps.py`** is an apps_rg-owned L2 recipe (fan_in=55, highest hotspot).
4. **One cross-app caller** of `RgResumeOrchestrator` lives in `agentic_core/`:
   `agentic_core/utils/workflow_engines/apps_engines_aliases.py` — must be removed in W4 before quarantine.
5. **`apps_rg/engines/judges/executive_positioning_judge.py`** — judge in apps_rg (fan_in=20).
6. **`apps_rg/cert/fec_producer.py`** — FEC producer in apps_rg (fan_in=10) — see "Open Tension" below.

Repo-wide violation counts (baseline before any W4+ edits): 19 CRITICAL · 19 HIGH ·
32 MEDIUM · 12 749 LOW. Apps_rg-specific antipattern edges: **70 bare `except Exception`**
plus 21 `ImportError`, 13 `OSError`, 4 `RuntimeError`.

---

## §1. ADG Health (W1.1)

| Property | Value |
|---|---|
| Mode | full |
| SQLite | healthy |
| Redis | healthy |
| Cache hit capable | true |
| Schema version | 1.0 |
| Snapshot ID | `05052026_0722` |
| Node count | 140 743 |
| Edge count | 863 353 |
| Graph projection | available, not stale |

**ADG Provenance:** `backend=sqlite`, snapshot `adg_indexed_05052026_0722.sqlite`.

> Note: ADG MCP transport closed mid-batch during W1 fan-in queries. Per constitutional
> §28, fallback to direct SQLite read of the canonical snapshot was used for all
> downstream queries. NO grep was used. Fallback evidence: `tools/analysis/_w1_apps_rg_baseline.py`,
> `tools/analysis/_w1_apps_rg_mv_scan.py`. Raw output:
> `artifacts/_w1_apps_rg_baseline.json`, `artifacts/_w1_apps_rg_mv_scan.json`.

---

## §2. Originally-Named Quarantine Targets (W1.2)

| Target | Module ID | Fan-in (imports) | Cross-app callers | Resolves callsite | Emits side effect | Disposition |
|---|---|---|---|---|---|---|
| `RgResumeOrchestrator` | 3296 | 9 (8 tests + 1 cross-app) | **1** | 41 | 10 | **Quarantine inert (W4.1)** — must remove cross-app caller first |
| `_llm_client` | 3244 | 1 (test only) | 0 | 16 | 15 | **Quarantine inert (W4.5)** — direct provider invoker (5 `invokes_provider` edges) |
| `RGStrategyExecutor` | 3288 | 2 (apps_rg shims only) | 0 | 1 | 0 | **Archive (W4.4)** — only used by 2 sibling shims |
| `RgStrategicPlannerAgent` | 3297 | 1 (test only) | 0 | 0 | 0 | **Archive** — already a shim for RGStrategyExecutor |
| `jd_planner` | 3155 | 0 | 0 | 7 | 4 | **Archive (W4.2)** — orphaned (confirmed 0 importers) |
| `resume_planning_engine` | 3211 | 0 | 0 | 5 | 2 | **Archive (W4.3)** — orphaned + 62 unused_import edges (broken import bug confirmed) |
| `strategic_planning_engine` | 3222 | 0 | 0 | 4 | 5 | **Archive** — orphaned |
| `resume_section_node_types` | 3367 | 0 | 0 | 13 | 4 | **Archive** — orphaned |

### Cross-app caller blocking quarantine

```
agentic_core/utils/workflow_engines/apps_engines_aliases.py
  → imports apps_rg/reasoning/RgResumeOrchestrator.py
```

This single edge violates the inverted-gravity invariant (`agentic_core` MUST NOT
import from `apps_rg/`). **Pre-W4 fix required:** remove the import in
`apps_engines_aliases.py` before quarantining `RgResumeOrchestrator`. If the alias
is genuinely needed, it must be re-homed under `agentic_core` with apps_rg-free
implementation.

---

## §3. Newly-Discovered Runtime-Authority Files (W1.3)

The §10 forbidden-pattern scan against the live `apps_rg/` tree (excluding `tests/`,
`docs/`) returned **105 distinct symbol/module nodes across 43 files**. The list
below groups them by archetype. Every file marked **QUARANTINE** or **ARCHIVE** is
in W4 scope; **PROFILE-LOADER** files are eligible to be rewritten as declarative
profile loaders if and only if they read declarative files only and emit no runtime
authority.

### 3.1 Direct Provider Egress (CRITICAL — §10 violation)

These files emit `invokes_provider` edges to `anthropic.Anthropic` / `openai.OpenAI`
WITHOUT going through `SovereignLLMGateway`. **Must be quarantined or archived in
W4.5; provider cascade logic re-homed under the gateway.**

| File | Provider | Edge count |
|---|---|---|
| `apps_rg/integrations/hops/_llm_client.py` | anthropic + openai | 5 |
| `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py` | anthropic | 1 |
| `apps_rg/validators/enforcement/HardenedanthropicexecutorStrategy.py` | anthropic | 1 |
| `apps_rg/engines/hardened_gemini_executor.py` | gemini (per filename) | TBD — name match |
| `apps_rg/reasoning/HardenedopenaiexecutorStrategy.py` | openai (per filename) | TBD — name match |

### 3.2 Orchestrator Pattern (`*Orchestrator*` — §10)

| File | Fan-in | Disposition |
|---|---|---|
| `apps_rg/reasoning/RgResumeOrchestrator.py` | 9 | QUARANTINE (W4.1) |
| `apps_rg/reasoning/ResumeOrchestrator.py` | TBD | QUARANTINE |
| `apps_rg/reasoning/ResumeEnhancementOrchestrator.py` | TBD | QUARANTINE |
| `apps_rg/reasoning/RgHealingOrchestrator.py` | TBD | QUARANTINE |
| `apps_rg/reasoning/RgHopOrchestrator.py` | TBD | QUARANTINE |
| `apps_rg/engines/resume_orchestrator_engine.py` | 6 (fan_out=90) | QUARANTINE — high blast radius |
| `apps_rg/engines/enhancement_orchestrator_engine.py` | TBD | QUARANTINE |

### 3.3 Executor Pattern (`*Executor*` — §10)

| File | Disposition |
|---|---|
| `apps_rg/reasoning/RGStrategyExecutor.py` | ARCHIVE (W4.4) |
| `apps_rg/reasoning/RGValidationExecutor.py` | ARCHIVE |
| `apps_rg/reasoning/HardenedopenaiexecutorStrategy.py` | QUARANTINE — direct OpenAI |
| `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py` | QUARANTINE — direct Anthropic |
| `apps_rg/validators/enforcement/HardenedanthropicexecutorStrategy.py` | QUARANTINE — direct Anthropic |
| `apps_rg/engines/hardened_gemini_executor.py` | QUARANTINE — Gemini path (must fail closed per §3 / §10) |
| `apps_rg/scripts/migration_executor.py` | ARCHIVE (script) |
| `apps_rg/tools/SafetyExecutor.py` | ARCHIVE (utility) |
| `apps_rg/utils/agent_executor_util.py` | ARCHIVE |

### 3.4 Agent Pattern (`*Agent*` — §10)

| File | Disposition |
|---|---|
| `apps_rg/reasoning/ContentQualityAgent.py` | ARCHIVE |
| `apps_rg/reasoning/DispatchResumeToolsAgent.py` | ARCHIVE |
| `apps_rg/reasoning/ExecutiveSummaryOutputAgent.py` | ARCHIVE |
| `apps_rg/reasoning/HeadlineOutputAgent.py` | ARCHIVE |
| `apps_rg/reasoning/ProactiveAgent.py` | ARCHIVE |
| `apps_rg/reasoning/RgStrategicPlannerAgent.py` | ARCHIVE |
| `apps_rg/config/agent_spec_config.py` | **AMBIGUOUS** — defines `AgentSpec`, `OrchestrationTopology`, `RGAgentSpecs`. If pure dataclasses → could become `apps_rg/profiles/rg_capability_profile.yaml`. Decide in W3. |

### 3.5 Planner / Router Pattern

| File | Disposition |
|---|---|
| `apps_rg/L1_cognition/jd_planner.py` | ARCHIVE (W4.2 — orphaned) |
| `apps_rg/types/rg_flow_router_types.py` | **AMBIGUOUS** — type defs only? If yes, reduce to declarative profile schema. Decide in W3. |
| `apps_rg/utils/enhanced_rg_flow_router_util.py` | ARCHIVE — runtime router util |

### 3.6 Apps_rg-Owned Prompt Assembly (CRITICAL — §10 violation)

`apps_rg/prompt_assembly/` is an entire subtree of prompt-assembly logic owned by
`apps_rg`. **All of it violates §10.** Core Prompt Assembly is the sole owner.

| File | Fan-in | Disposition |
|---|---|---|
| `apps_rg/prompt_assembly/contracts.py` | 37 | QUARANTINE — replaced by `agentic_core/L2_execution/reasoning/compiled_artifact.py` |
| `apps_rg/prompt_assembly/compiler.py` | 19 | QUARANTINE — replaced by core PA |
| `apps_rg/prompt_assembly/slot_mapper.py` | 11 | QUARANTINE — replaced by core PA slot machinery |
| `apps_rg/prompt_assembly/provider_request.py` | 8 | QUARANTINE — replaced by core PA + SovereignLLMGateway |

### 3.7 Apps_rg-Owned L2 Recipe (CRITICAL — §10 violation)

| File | Fan-in | Disposition |
|---|---|---|
| `apps_rg/l2_recipe/steps.py` | **55** (HIGHEST hotspot in apps_rg) | QUARANTINE — agentic_core L2 owns recipes |

### 3.8 Engines (Domain-specific runtime)

`apps_rg/engines/*.py` is a runtime engine subtree. Most violate §10. Specific findings:

| File | Fan-in | Disposition |
|---|---|---|
| `apps_rg/engines/base_rg_engine.py` | 49 (fan_out=81, betweenness=0.406) | QUARANTINE — extreme blast radius |
| `apps_rg/engines/_lifecycle_emits.py` | 45 | QUARANTINE — engine lifecycle = runtime authority |
| `apps_rg/engines/resume_planning_engine.py` | 0 | ARCHIVE (W4.3) — orphaned |
| `apps_rg/engines/strategic_planning_engine.py` | 0 | ARCHIVE — orphaned |
| `apps_rg/engines/judges/executive_positioning_judge.py` | 20 | QUARANTINE — judging in apps_rg = §10 |

### 3.9 Validators / Healing / Hops (runtime)

| File | Fan-in | Disposition |
|---|---|---|
| `apps_rg/validators/regeneration_validator.py` | 9 (fan_out=74) | QUARANTINE — runtime decide-proceed-or-stop = §10 |
| `apps_rg/integrations/hops/_ensemble_runner.py` | 15 | QUARANTINE — runtime ensemble routing |
| `apps_rg/integrations/hops/_role_bullet_runner.py` | 12 | QUARANTINE — runtime hop runner |
| `apps_rg/integrations/hitl_bridge.py` | 10 | **AMBIGUOUS** — HITL bridge may be allowed if pure ingress/egress |

### 3.10 Open Tension — `apps_rg/cert/fec_producer.py`

Per memory `e24c888b` (plan `apps-qna-c0-fec-producer-wiring-d4f1e8`, completed
2026-05-03), the per-app FEC producer pattern was established and replicated to
five grounded apps. `apps_rg/cert/fec_producer.py` was authored under that pattern.

Plan §4.2 forbids `apps_rg` to "emit `FinalEvidenceContract`". The fec_producer
emits a *partial* `FEC dict` that the core resolver consumes — it is not a full
`FinalEvidenceContract` emission and the core stage seals the contract.

**Decision required (deferred AG):** does the per-app fec_producer pattern survive
the declarative-only governance rule? Two options:

- **Option A (preserve):** `cert/fec_producer.py` is treated as a declarative
  *profile loader* — it returns a dict, not an authority-bearing contract. Pattern
  established by 5 grounded apps; ripping it out would diverge from the BLOCKER #4
  doctrine.
- **Option B (relocate):** move the FEC producer logic into `agentic_core` (e.g.
  per-app entries under `agentic_core/runtime/fec_producers/`), keeping `apps_rg`
  declarative-only. More invasive; affects the other 4 grounded apps.

`AG_QUEUE_SEED:` recorded in §6 below.

---

## §4. Apps_rg Hotspot Centrality (top-25 by degree_centrality)

Source: `mv_hotspot_centrality` filtered on `resolved_path LIKE 'apps_rg/%'`.

| Rank | Path | Fan_in | Fan_out | Degree | Betweenness | §10 Violation? |
|------|------|--------|---------|--------|-------------|----------------|
| 1 | `apps_rg/l2_recipe/steps.py` | 55 | 19 | 74 | 0.107 | **YES — apps_rg-owned L2** |
| 2 | `apps_rg/engines/base_rg_engine.py` | 49 | 81 | 130 | **0.406** | YES — runtime engine base |
| 3 | `apps_rg/engines/_lifecycle_emits.py` | 45 | 63 | 108 | 0.290 | YES — engine lifecycle |
| 4 | `apps_rg/prompt_assembly/contracts.py` | 37 | 7 | 44 | 0.027 | **YES — apps_rg-owned PA** |
| 5 | `apps_rg/hitl/hitl_schemas.py` | 30 | 6 | 36 | 0.018 | AMBIGUOUS |
| 6 | `apps_rg/types/company_research.py` | 25 | 9 | 34 | 0.023 | NO — type defs (allowed) |
| 7 | `apps_rg/__main__.py` | 23 | 11 | 34 | 0.026 | NO — only legitimate live entry |
| 8 | `apps_rg/integrations/length_budget.py` | 21 | 9 | 30 | 0.019 | AMBIGUOUS |
| 9 | `apps_rg/types/__init__.py` | 21 | 11 | 32 | 0.024 | NO — type re-exports |
| 10 | `apps_rg/engines/judges/executive_positioning_judge.py` | 20 | 5 | 25 | 0.010 | **YES — judging** |
| 11 | `apps_rg/__init__.py` | 19 | 1 | 20 | 0.002 | NO |
| 12 | `apps_rg/integrations/anti_overfitting.py` | 19 | 9 | 28 | 0.018 | AMBIGUOUS |
| 13 | `apps_rg/prompt_assembly/compiler.py` | 19 | 14 | 33 | 0.027 | **YES — apps_rg-owned PA** |
| 14 | `apps_rg/config/agent_spec_config.py` | 15 | 77 | 92 | 0.118 | AMBIGUOUS — see §3.4 |
| 15 | `apps_rg/integrations/hops/_ensemble_runner.py` | 15 | 20 | 35 | 0.031 | YES — runtime hop |
| 16 | `apps_rg/types/rg_types.py` | 15 | 6 | 21 | 0.009 | NO — type defs |
| 17 | `apps_rg/integrations/hops/_role_bullet_runner.py` | 12 | 17 | 29 | 0.021 | YES — runtime hop |
| 18 | `apps_rg/utils/authenticity_patterns_util.py` | 12 | 81 | 93 | 0.099 | AMBIGUOUS |
| 19 | `apps_rg/prompt_assembly/slot_mapper.py` | 11 | 5 | 16 | 0.006 | **YES — apps_rg-owned PA** |
| 20 | `apps_rg/cert/fec_producer.py` | 10 | 4 | 14 | 0.004 | **TENSION — see §3.10** |
| 21 | `apps_rg/integrations/hitl_bridge.py` | 10 | 8 | 18 | 0.008 | AMBIGUOUS |
| 22 | `apps_rg/reasoning/RgResumeOrchestrator.py` | 10 | 85 | 95 | 0.087 | YES — quarantine target |
| 23 | `apps_rg/types/SovereignContext.py` | 9 | 67 | 76 | 0.062 | AMBIGUOUS — type or context? |
| 24 | `apps_rg/validators/regeneration_validator.py` | 9 | 74 | 83 | 0.068 | YES — runtime validator |
| 25 | `apps_rg/engines/resume_orchestrator_engine.py` | 6 | 90 | 96 | 0.055 | YES — orchestrator engine |

---

## §5. Antipattern Baseline (apps_rg-anchored edges)

Source: `edges` table where `relation_type = 'antipattern'` and `src.resolved_path LIKE 'apps_rg/%'`.

| Antipattern kind | Count |
|---|---|
| `Exception` (bare `except Exception`) | **70** |
| `SELF` (self-reference smell) | 24 |
| `ImportError` | 21 |
| `OSError` | 13 |
| `RuntimeError` | 4 |
| `AttributeError` | 4 |
| `ValueError` | 3 |
| `TypeError` | 3 |
| `KeyError` | 2 |
| `subprocess.run` | 2 |

**Implication:** the 70 `except Exception` edges in apps_rg are independent of the
declarative-ingress refactor but represent technical debt that will be **eliminated
naturally** as the runtime files are quarantined or archived.

---

## §6. Open Author-Gate Decisions (AG_QUEUE_SEED)

```
AG_QUEUE_SEED: plan=apps-rg-declarative-ingress-only-spinal-governance-c8b3e1 id=AG-RGGOV-5 depends_on=AG-RGGOV-1 title=Per-app FEC producer pattern survival — does apps_rg/cert/fec_producer.py remain (Option A: declarative loader) or relocate to agentic_core (Option B: re-home with 4 sibling apps)? Affects established BLOCKER #4 doctrine. Cross-references plan apps-qna-c0-fec-producer-wiring-d4f1e8.
AG_QUEUE_SEED: plan=apps-rg-declarative-ingress-only-spinal-governance-c8b3e1 id=AG-RGGOV-6 depends_on= title=apps_rg/config/agent_spec_config.py reduction — pure dataclasses? If yes, target W3 conversion to apps_rg/profiles/rg_capability_profile.yaml. If contains runtime logic, archive in W4.
AG_QUEUE_SEED: plan=apps-rg-declarative-ingress-only-spinal-governance-c8b3e1 id=AG-RGGOV-7 depends_on= title=apps_rg/hitl/* and apps_rg/integrations/hitl_bridge.py — HITL is at the runtime boundary. Does the wizard/hitl machinery count as ingress (allowed) or runtime authority (forbidden)? Per apps-rg-interactive-discipline.md the wizard is ingress; HITL re-entry mid-run is core territory.
AG_QUEUE_SEED: plan=apps-rg-declarative-ingress-only-spinal-governance-c8b3e1 id=AG-RGGOV-8 depends_on= title=apps_rg/integrations/hops/* removal scope — all 5+ hop runners need quarantine. Confirm none are live-imported by agentic_core (likely zero per §2 cross-app analysis but must enumerate). 
AG_QUEUE_SEED: plan=apps-rg-declarative-ingress-only-spinal-governance-c8b3e1 id=AG-RGGOV-9 depends_on= title=Cross-app cleanup of agentic_core/utils/workflow_engines/apps_engines_aliases.py — remove the apps_rg import, or refactor the alias machinery? This must land BEFORE W4.1 quarantine of RgResumeOrchestrator.
```

---

## §7. Implications for W4 Scope

The plan's W4 wave originally listed **8 quarantine targets**. W1 evidence shows
the actual scope is **~43 files across 7 archetypes**, plus **1 cross-app caller
in `agentic_core/`**. W4 must expand into structured sub-phases:

- **W4.0 (NEW):** Pre-quarantine — remove cross-app caller in
  `agentic_core/utils/workflow_engines/apps_engines_aliases.py`. Blocker for W4.1.
- **W4.1:** Quarantine all 6 `Orchestrator` files (not just `RgResumeOrchestrator`).
- **W4.2:** Archive all orphaned planners (`jd_planner`, `strategic_planning_engine`,
  `resume_planning_engine`, `RgStrategicPlannerAgent`, `RGStrategyExecutor`,
  `RGValidationExecutor`).
- **W4.3:** Quarantine all 5 direct-provider executors (`HardenedanthropicexecutorStrategy.py`
  ×2, `hardened_gemini_executor.py`, `HardenedopenaiexecutorStrategy.py`,
  `_llm_client.py`).
- **W4.4:** Quarantine the entire `apps_rg/prompt_assembly/` subtree (4 files).
- **W4.5:** Quarantine `apps_rg/l2_recipe/steps.py`.
- **W4.6:** Quarantine `apps_rg/engines/*` runtime (judges, lifecycle, base engine,
  orchestrator engines, hardened executors).
- **W4.7:** Quarantine `apps_rg/integrations/hops/*` runtime hops (~5 files).
- **W4.8:** Quarantine `apps_rg/validators/regeneration_validator.py`.
- **W4.9:** Resolve AG-RGGOV-5/6/7 ambiguities (cert, agent_spec, hitl).
- **W4.10:** Verify quarantine inert — every quarantined module raises `RuntimeError`
  on import; live `apps_rg` import scan returns zero §10 hits.

W4 token estimate revises from ~5 k to **~10 k**. Plan §12 wave structure should be
amended after AG approval; this baseline is the authoritative scope evidence.

---

## §8. W1 Acceptance

| Sub-phase | Status |
|---|---|
| W1.1 — ADG health green | ✅ |
| W1.2 — fan-in / fan-out for 8 named targets | ✅ |
| W1.2 — cross-app caller enumeration | ✅ (1 found) |
| W1.2 — provider egress edges enumerated | ✅ (4 files, 7 edges) |
| W1.2 — antipattern baseline | ✅ |
| W1.2 — hotspot centrality top-25 | ✅ |
| W1.3 — runtime authority smell inventory | ✅ (43 files, 105 symbol matches) |
| W1.3 — `APPS_RG_RUNTIME_AUTHORITY_BASELINE.md` authored | ✅ (this file) |

**No edits performed in W1.** All evidence is read-only ADG / SQLite queries.

---

## §9. Artifacts

| Artifact | Path |
|---|---|
| Raw fan-in/fan-out + smell inventory | `artifacts/_w1_apps_rg_baseline.json` |
| MV / violations / provider-egress slice | `artifacts/_w1_apps_rg_mv_scan.json` |
| Baseline-script SSOT | `tools/analysis/_w1_apps_rg_baseline.py` |
| MV-scan-script SSOT | `tools/analysis/_w1_apps_rg_mv_scan.py` |
| Schema probe | `tools/analysis/_w1_schema_probe.py` |
| ADG snapshot used | `artifacts/adg/adg_indexed_05052026_0722.sqlite` |
