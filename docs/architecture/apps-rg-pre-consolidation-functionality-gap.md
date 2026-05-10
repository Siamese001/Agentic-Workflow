---
status: decision-input
type: architecture-decision-input
created: 2026-05-10
related:
  - .windsurf/plans/apps-rg-runtime-wiring-completion-d4e8a1.md  # the consolidation plan
  - .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md  # original re-architecture
  - docs/reference/_notes/Exit Criteria X1-X2-X3.md  # X1/X2/X3 framework spec
  - agentic_core/L3_orchestration/exit_eval/v6/x1_gates.py  # X1A-X1J implementation (orphaned)
  - agentic_core/L5_safety/runtime_gates/  # 29-gate G01-G29 mesh (orphaned)
  - agentic_core/runtime/entrypoints/apps_rg_integrated_pipeline.py  # alt exit path (uninvoked)
supersedes: []
superseded_by: []
---

# apps_rg Pre-Consolidation Functionality Gap Analysis

> **Status: ARCHITECTURE DECISION INPUT** — not yet a decision. This document enumerates 61 categories of functionality that existed in the OLD standalone apps_rg pipeline (pre-`1ffb5150f0`, ~Apr 2026) and were not preserved in the CURRENT agentic_core-routed pipeline (post-plan `apps-rg-runtime-wiring-completion-d4e8a1`, complete 2026-05-09).
>
> **Purpose**: provide the evidence base for a future Author-Gate decision on which capabilities to restore. Not a plan. Not a commitment. The decision and scoping live in a follow-up Author-Gate session.

## Executive Summary

**The consolidation kept the contracts and the file structure but discarded the substance.** The current pipeline is a thin adapter that satisfies the architectural shape while bypassing the safety mesh that justified the architecture.

| Layer | OLD pipeline | Current pipeline |
|---|---|---|
| Ingress (U0) | Schema-validated, transport-allowlisted, replay-keyed via `jd_hash` | Pass-through |
| Plan (L1) | JD planner → IntentPayload → flow router | Hardcoded plan strings |
| Route (L0) | Policy-driven (preconditions, R5 fallback, R1B cache, **C0 bypass**) | Hardcoded route + invokes C0 (architectural divergence) |
| PA | 8 versioned templates × 4 modes + 8-slot BOM (S0/I0/C0/U0/D0/E0/Y0/R0) | Single hardcoded prompt with 2 fields from 1 profile YAML |
| L2 | Multi-provider (OpenAI/Anthropic/Google/Frontier) via SovereignLLMGateway + direct-SDK fallback | Hardcoded Qwen vLLM at localhost:8000 |
| Exit | X1A-X1J gates → X2 aggregation → X3 disposition + L7 audit + 29 runtime gates | JSON write + hardcoded `success` |
| HITL | 6 declarative trigger policies + RuntimeAuthorGate | None |
| Healing | E4 heal modes + max_creative_retries=5 | None |
| Quality | min_quality≥0.75, min_ats≥70, word bounds, ATS keyword density | None enforced |

**Hallucination defect class** (RCA from 2026-05-10): today's defect (DOCX silently dropped at C0) was structurally inevitable because the safety mesh that would have caught it (`X1D` groundedness, `G09` evidence_quality, `G22` output_quality, `verbatim_provenance_gate`, `hallucination_detector`) all exist in agentic_core but are bypassed by the apps_rg dispatch path.

## Document Structure

This document was built in 4 evidence sweeps (4 passes), each adding categories the previous pass missed. The total is 61 categories.

| Pass | Categories | Focus |
|---|---|---|
| Pass 1 | 1–13 | OLD pipeline runtime layer (executors, judges, gates, engines, reasoning agents) |
| Pass 2 | 14–30 | Integrations + types + utils + scripts + chunking + spine + bootstrap |
| Pass 3 | 31–53 | Configuration & policy YAMLs (prompt registry, HITL policy, L0/U0 policies, agent spec, env vars) |
| Pass 4 | 54–61 | **The X1/X2/X3 framework + 29-gate runtime mesh — both implemented in core but bypassed** |

Each category includes: name, file refs, what it provides, current orphan-state. Priority assignments (P0/P1/P2/P3) are aggregated in the Summary by Priority section at the end.

## Decision Surface

A future Author-Gate session must select among:

- **Path A — Intent-only**: extend `AppsRgIngressPayload` with all 61 intent fields. Wire NOTHING. Contract carries everything; runtime stays broken.
- **Path C — Hybrid**: extend ingress with P0 fields (14 items) + wire P0 multi-provider LLM + wire X1D groundedness + G09 evidence_quality + G22 output_quality. ~3-5 day plan.
- **Path D — Restore-the-Mesh**: wire X1A-X1J + 29-gate mesh + AppsRgIntegratedPipeline. ~2-3 weeks across multiple plans.
- **Path B — Full re-wiring**: re-implement all 61 categories. Multi-month effort.

The Restore-the-Mesh path is the architecturally cleanest because the framework already exists in agentic_core; the work is invocation-wiring, not implementation.

## Cross-References

Sibling raw-evidence files (preserved for trace) live in `.windsurf/plans/_orphan_review/`:
- `OLD_apps_rg_main.py`, `OLD_rg_ingress_runner.py`, `OLD_rg_types.py` (OLD pipeline)
- `OLD_reasoning_toggles.py`, `OLD_hop_pipeline.py`, `OLD_agent_spec_config.py` (OLD configs)

---

## Architectural Δ

| Aspect | OLD | CURRENT |
|---|---|---|
| Entrypoint | `python -m apps_rg` → `RgIngressRunner` → `GovernedRgRun.run_governed_e2e()` | `python -m apps_rg` → `AppIngressRunner.run()` → `apps_rg_dispatch(envelope)` |
| Pipeline depth | 7-stage HOP pipeline (`clerk_extraction` → `data_enrichment` → `resume_generation` → `fact_check` → `bullet_diversity_gate` → `content_optimizer` → `generation_diagnostics`) | 7 layer bindings (U0 → L1 → L0 → C0 → PA → L2 → Exit), each a single pure function |
| LLM execution | Multi-provider (OpenAI / Anthropic / Google) via `AgentExecutor` + `SovereignLLMGateway` w/ direct-SDK fallback | Single-provider hardcoded to local Qwen vLLM (`apps_rg_l2_binding._execute_via_qwen_vllm`) |
| Config surface | `RGAgentSpecs` — 8 nested config sections, ~50 knobs | `AppsRgIngressPayload` — 14 fields, mostly identity/refs |
| Engines invoked | ~50 specialized engines (skill scoring, ATS, hallucination, fit, etc.) | None — direct LLM call |
| Judges invoked | 6 ensemble judges (EY, TraderSense, IBM, Unify, Marquee, Headline) + executive_positioning | None — single prompt |
| Runtime gates | 5+ gates (verbatim provenance, bullet diversity, JD enforcement, validation gate, hallucination detector) | None — output goes straight to artifact |
| Output | DOCX + JSON + run summary + provenance | JSON only |

## Functionality Categories Lost

### 1. Multi-Provider LLM Routing — **HIGH IMPACT**

`@apps_rg/utils/agent_executor_util.py` (still on disk, but orphaned from execution path)

Provided:
- `AgentConfig(provider, temperature, max_tokens, model)` per-agent
- `Provider.OPENAI` / `Provider.ANTHROPIC` / `Provider.GOOGLE` enum dispatch
- `SovereignLLMGateway.generate()` — governed pipeline with policy + provenance
- Direct-SDK fallback via `_execute_openai` / `_execute_anthropic` / `_execute_google`
- `AllProvidersDownError` cascade-failure exception
- Reads `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` / `GEMINI_API_KEY` from env

Current state: **all bypassed.** L2 hardcoded to vLLM Qwen at `localhost:8000`. Anthropic/OpenAI/Google env vars are read nowhere in the apps_rg path.

### 2. RGAgentSpecs Master Config — **HIGH IMPACT**

`@apps_rg/config/agent_spec_config.py` — 8 nested Pydantic sections:

| Section | Knobs |
|---|---|
| `ClerkExtractionConfig` | `metrics_patterns`, `min_bullets_per_section=3`, `max_bullets_per_section=8` |
| `EnrichmentConfig` | `forbidden_phrases`, `duplicate_threshold=0.85`, `power_verbs` |
| `GenerationConfig` | `base_temperatures` per role, `max_section_words` per section, `n_candidates=3` |
| `ValidationConfig` | `severity_threshold`, `rule_categories`, `min_quality_score=0.7` |
| `GateConfig` | `factual_failure_rules`, `max_factual_loops=3`, `max_creative_retries=5`, `pass_threshold=0.8` |
| `RefinementConfig` | `optimization_targets`, `max_iterations=3` |
| `QAReportConfig` | `report_sections`, `output_directory`, `scoring_weights` |
| `OrchestratorConfig` | `global_step_limit=20`, `max_retry_iterations=5`, `checkpoint_enabled`, `trace_persistence` |

Current state: **none of these knobs reach the dispatch path.** PA uses hardcoded `temperature=0.4`, `max_tokens=4096`, no per-section budgets, no n_candidates.

### 3. HOP Pipeline Stages — **HIGH IMPACT**

`@apps_rg/config/hop_pipeline.py` — 7 declarative stages:

```
clerk_extraction → data_enrichment → resume_generation → fact_check → 
bullet_diversity_gate(GATE) → content_optimizer → generation_diagnostics
```

Each stage:
- Reads structured inputs from a Buffer
- Writes structured outputs back
- Stage 5 (`bullet_diversity_gate`) was a GATE — could reject and force regeneration

Current state: **collapsed into a single LLM call.** No structured intermediate state, no fact-check stage, no diversity gate, no diagnostics.

### 4. Role-Specific Bullet Ensembles — **MEDIUM IMPACT**

`@apps_rg/integrations/hops/`:
- `competencies_ensemble`, `early_career_compress`, `exec_summary_ensemble`
- `headline_ensemble`, `marquee`
- Per-role ensembles: `ey_judge`, `tradersense_judge`, `ibm_ensemble`, `unify_ensemble`

Each role-ensemble:
- Generated `n_candidates` bullets per role/company in candidate's history
- Used `_role_bullet_runner.run_role_bullets(role_id, jd_facets, company_facets, mirror_terms, tier, n_candidates)`
- Pool-first selection (cached pool of pre-approved bullets per role)
- Tier-aware (`high` / `medium` / `low`) — drove temperature + n_candidates

Current state: **all bypassed.** PA produces a single resume body in one shot.

### 5. Runtime Gates — **HIGH IMPACT**

| Gate | Rejected / mutated when… |
|---|---|
| `VerbatimProvenanceGate` | Per-bullet match score below threshold; metric preservation violated; scope check failed |
| `BulletDiversityGate` | < `MIN_DISTINCT_THEMES=2` distinct bullets across role |
| `JdEnforcementValidator` | JD-required keywords absent from output |
| `ValidationGateValidator` | Composite validation rules fail |
| `HallucinationDetectorValidator` | Claims not traceable to source resume / JD |
| `RegenerationValidator` | After regeneration, drift > tolerance |

Current state: **no gates run at all.** L2 output is written directly to artifact. The hallucination defect we fixed earlier today (DOCX silently dropped) would have been caught immediately by `HallucinationDetectorValidator` if it ran.

### 6. Specialized Scoring Engines — **MEDIUM IMPACT**

`@apps_rg/engines/` (50+ files), notably:

| Engine | Purpose |
|---|---|
| `ats_compatibility_engine` | ATS keyword scoring (0-100) |
| `fit_score_calibrator` | Job-resume fit calibration |
| `job_alignment_scorer` | Per-bullet alignment to JD |
| `skill_score_normalizer` | Cross-role skill normalization |
| `effectiveness_scorer` | Resume effectiveness rating |
| `quality_inspector_engine` | Composite quality verdict |
| `writing_quality_engine` | Style + grammar |
| `hallucination_detector` | Claim traceability |
| `fact_check_engine` | JD/resume cross-reference |
| `duplicate_detector` | Near-duplicate bullet detection |
| `role_archetype_classifier` | Maps title → archetype (IC / Manager / Director / VP / SVP / Exec) |
| `experience_weighting_engine` | Weights by recency × relevance |
| `section_balance_engine` | Section length budgeting |
| `section_ranker_engine` | Ranks sections by JD relevance |

Current state: **all orphaned.** None invoked from current dispatch path.

### 7. Reasoning Toggles — **MEDIUM IMPACT**

`@apps_rg/config/reasoning_toggles_config.py` — `ReasoningToggles`:

| Toggle | Default | Effect |
|---|---|---|
| `use_cot` | True | Chain-of-Thought reasoning |
| `use_reflexion` | False | Self-correction loops |
| `strict_mode` | True | Fail on minor validation errors |
| `use_persistent_tracing` | True | Persistent trace storage |
| `use_cyclic_validation` | True | Cyclic retry validation |
| `tot_branches` | 2 | Tree-of-Thought branches (1-5) |
| `min_tot_depth` | 1 | Minimum tree exploration depth |
| `temperature_cap` | 0.5 | Maximum sampling temperature |

Note: doc says these are defaults-only, OVERRIDDEN at runtime by `ReasoningIntensityProfile` stamped by L0.

Current state: **L0 binding (`apps_rg_l0_binding.py`) does not stamp a ReasoningIntensityProfile.** Toggles are not consulted anywhere in current path.

### 8. ResumeConfig User Knobs — **LOW IMPACT (covered earlier)**

| Field | Default | Purpose |
|---|---|---|
| `target_format` | `standard` | `standard` / `ats_optimized` / `executive` / `creative` |
| `max_length_words` | 500 | 100-2000 |
| `ats_optimization` | True | Enable ATS keyword tuning |
| `highlight_leadership` | False | Emphasize leadership content |
| `min_skill_matches` | 5 | Minimum skill matches to include |
| `target_industry` | `general` | `tech` / `finance` / `healthcare` / `consulting` / `general` |

### 9. Output Formats — **MEDIUM IMPACT**

`@apps_rg/outputs/`:
- `docx_exporter` — DOCX file output
- `resume_renderer` — multi-section JSON renderer with provenance per bullet
- `section_renderer` — per-section formatting
- `envelope_emitter` — RunReport envelope with provenance, gate verdicts, artifact paths

Current state: only JSON output via `apps_rg_exit_binding`. **DOCX export is gone.** Run summary lacks gate verdicts, ATS scores, skill match details.

### 10. Cache Layer — **MEDIUM IMPACT (partially preserved)**

`@apps_rg/cache/`:
- `r1a_adapter.py` (exact-match cache) — present in apps_rg/ but not invoked from current path
- `r1b_adapter.py` (semantic cache) — present, not invoked
- `chunk_commit.py` — present, not invoked
- OLD CLI flag `--skip-r1b-check` had no current equivalent

### 11. Healing Cycle — **LOW IMPACT**

`@apps_rg/reasoning/healing_cycle.py` + `RgHealingOrchestrator`:
- On gate failure → analyzes failure → mutates prompt → regenerates section → re-runs gates
- Bounded by `max_factual_loops=3`, `max_creative_retries=5`

Current state: **no healing.** First L2 response → straight to artifact.

### 12. Validators / Prerequisites — **MEDIUM IMPACT**

`@apps_rg/validators/`:
- `jd_enforcement_validator` — confirms JD requirements addressed
- `validation_gate_validator` — composite validation
- `hallucination_detector_validator`, `regeneration_validator`, `validation_result_validator`

`@apps_rg/prerequisites/briefing_validator.py` — confirms research briefing is well-formed before pipeline starts.

Current state: orphaned.

### 13. Reasoning Agents — **LOW IMPACT**

14 agents in `@apps_rg/reasoning/`:
- ContentQualityAgent, HeadlineOutputAgent, ExecutiveSummaryOutputAgent
- ProactiveAgent, DispatchResumeToolsAgent
- RGStrategyExecutor, RGValidationExecutor
- RgReflectionAgent, RgStrategicPlannerAgent, RgTemplateOptimizerAgent
- RgHealingOrchestrator, RgHopOrchestrator, ResumeOrchestrator, RgResumeOrchestrator

Current state: orphaned.

### 14. Anti-Overfitting Gates — **MEDIUM IMPACT (missed in v1)**

`@apps_rg/integrations/anti_overfitting.py` — `AntiOverfittingConfig` + 4 gates:

- `gate_buzzword_soup` — counts buzzwords vs `DEFAULT_BUZZWORDS` blocklist; rejects when density too high
- `gate_filler_intensifiers` — detects filler words / weak intensifiers
- `gate_mirror_density` — measures % of bullet that mirrors JD terms (overfitting signal — too high = JD-mimicking, not authentic)
- `gate_pipe_format` — enforces pipe-separated bullet format

Current state: orphaned. Generated resumes today have no buzzword cap, no mirror-density check.

### 15. Length Budgeting — **MEDIUM IMPACT (missed in v1)**

`@apps_rg/integrations/length_budget.py` — `LengthBudget` class + helpers:

- Per-section word budgets extracted from master resume (`extract_master_resume_budgets`)
- `budget_for_section`, `best_fit` — section-aware sizing
- `count_words`, `count_sentences` — text metrics
- `DEFAULT_TOLERANCE` for budget overflow

Current state: orphaned. Current PA has a single 20K-char evidence budget; no per-section output sizing.

### 16. Pool-First Selection — **MEDIUM IMPACT (missed in v1)**

`@apps_rg/integrations/pool_first_selector.py` — `PoolChoice` + `pool_first_select()`:

Pre-approved bullet pool per role/company. Prefer pool match over LLM generation when match score above threshold. Enables determinism + cost reduction for repeated runs.

Current state: orphaned. Every run is a fresh LLM call.

### 17. HITL Bridge — **HIGH IMPACT (missed in v1)**

`@apps_rg/integrations/hitl_bridge.py` — Human-in-the-Loop:

- `read_run_report` — read the run output
- `build_hitl_context` — package for human review
- `evaluate_hitl` — evaluate human feedback into the next run

Current state: orphaned. No HITL surface in current pipeline.

### 18. Tavily Web Research Supplement — **MEDIUM IMPACT (missed in v1)**

`@apps_rg/integrations/tavily_supplement.py` — `supplement_company_brief(brief: CompanyBrief)`:

When manual brief has missing fields, supplement via Tavily web search. Pairs with `--auto-research-tavily` flag (which IS in current CLI but not wired to anything).

Current state: CLI flag exists, no implementation in current dispatch path.

### 19. Company Research Loading + Facet Extraction — **MEDIUM IMPACT (missed in v1)**

- `@apps_rg/integrations/company_research_loader.py` — load `company_research.json` into `CompanyBrief`
- `@apps_rg/integrations/company_facet_extractor.py` — extract structured facets (industry, size, tech stack, culture signals) for prompt injection
- `@apps_rg/types/company_research.py` — `CompanyBrief` rich type with structured fields

Current state: orphaned. C0 reads `manual_brief_path` as a path-only reference; no structured loading; facets never extracted.

### 20. Cross-App Spine Handoff — **MEDIUM IMPACT (missed in v1)**

`@apps_rg/integrations/spine_handoff.py` — handoff to other apps_* via spine:
- Delegate company research to `apps_research`
- Delegate licensing/credential checks to `apps_lic`
- Pairs with `--research-via apps_research` CLI flag

Current state: CLI flag exists, no spine handoff in dispatch path.

### 21. Two-Phase Generation — **MEDIUM IMPACT (missed in v1)**

`@apps_rg/types/two_phase_generation_node_types.py`:
- Phase 1: structured extraction (bullets, skills, sections) — deterministic
- Phase 2: narrative composition — creative LLM call
- Separation prevented hallucination by anchoring narrative to phase-1 facts

Current state: collapsed into one LLM call. Today's hallucination defect proves this matters — phase-1 anchoring would have caught it.

### 22. Narrative Pass (Post-Generation) — **MEDIUM IMPACT (missed in v1)**

`@apps_rg/scripts/narrative_pass.py` — separate post-generation pass:
- Polishes generated bullets for narrative coherence
- Headline + executive summary generation as separate hops (HOP-4A-HEADLINE)
- Still on disk and currently invokable as `python -m apps_rg.scripts.narrative_pass` (per `apps-rg-post-run-summary.md` rule)

Current state: scripts exist, not chained from current dispatch.

### 23. Provenance Tracking — **HIGH IMPACT (missed in v1)**

`@apps_rg/types/provenance_pattern_types.py` + per-engine emission:
- Per-bullet provenance: source quote, transformation log, confidence
- Per-section provenance roll-up
- Run-level provenance manifest

Current state: dispatch path emits `evidence_anchor` field per bullet (we saw this today) but with hardcoded value pointing at the resume DOCX path — no per-bullet source quote, no transformation log.

### 24. Audit & Live-Fire Scripts — **LOW IMPACT (missed in v1)**

`@apps_rg/scripts/`:
- `rg_final_audit.py` — final audit pass
- `rg_sovereign_auditor.py` — provenance audit
- `rg_live_fire.py` — live-fire test against real LLM stack
- `rg_inject_archives.py` — inject archived bullets back into pool
- `rg_json_miner.py` — mine prior runs for high-quality bullets
- `validate_spine_coverage.py` — validates spine binding completeness

Current state: scripts exist on disk but not chained to main run.

### 25. Specialized Type System — **LOW IMPACT (missed in v1)**

17 rich domain types in `@apps_rg/types/`:
- `IntentPayload`, `PromptTemplate`, `SovereignContext`
- `RunReport` (rich result vs current minimal JSON)
- `RoutingTierTypes` (high/medium/low routing tiers)
- `RgFlowRouterTypes` (flow routing decisions)
- `ResumeAnalysisPlanTypes`, `ResumeSectionNodeTypes`
- `ThematicAnalysisNodeTypes`
- `TraceRegistryTypes`, `StateTransactionTypes`
- `SkillExtractorNodeTypes`, `GapClosureArchitectAgentTypes`

Current state: most replaced by minimal contracts in `agentic_core/runtime/contracts/`. Loss of domain richness — current contracts are generic spine-fitting types, not resume-domain types.

### 26. Utility Layer — **MEDIUM IMPACT (missed in v1)**

`@apps_rg/utils/`:
- `agent_executor_util.py` (covered above)
- `anthropic_rag_entrypoint.py` — direct Anthropic RAG path
- `clerk_extractor_util.py` — clerk extraction helpers
- `deep_brain_harvester_util.py` — harvests deep content from candidate history
- `enhanced_rg_flow_router_util.py` — flow routing logic with tier dispatch
- `intent_builder.py` — builds `IntentPayload` from user input → drives flow router
- `repo_signal_service.py` — pulls structured signals from candidate's GitHub / repo content
- `sovereign_config_loader_util.py` — runtime config loading from `RGAgentSpecs`
- `authenticity_patterns_util.py` — authenticity pattern matching (anti-overfit signal)
- `rg_validation_capability_util.py` — validation capability layer

Current state: orphaned. The intent-builder loss is notable — current path has no `IntentPayload`, just the flat `AppsRgIngressPayload`.

### 27. ~30 Specialized Tools — **LOW-MEDIUM IMPACT (missed in v1)**

`@apps_rg/tools/` (LLM tool definitions for agents):
- `CalibrateFitScore`, `ComputeSkillSimilarity`, `EvaluateResumeEffectiveness`
- `EvaluateWritingQuality`, `InspectResumeQuality`, `DiagnoseGenerationIssues`
- `OrderSkillsByRelevance`, `NormalizeSkillScores`, `RankResumeSections`
- `RefineResumeRanking`, `OptimizeContentOrder`, `WeightExperienceMatch`
- `PrioritizeAchievements`, `PrepareResumeContext`, `BuildSearchFilters`
- `AdjustSectionWeights`, `AssessContentRelevance`, `DataEnricher`
- `ResumeGenerator`, `RetrieveResumeHistory`, `SafetyExecutor`
- `query_past_generations`, `match_job_patterns`, `fetch_user_preferences`
- `create_experience_bullets`, `execute_message_generation`, `invoke_generation_service`

Current state: orphaned. These were tool-call surfaces for agents to use during generation. Without the agent runtime, they don't fire.

### 28. Resume Chunking — **LOW IMPACT (missed in v1)**

`@apps_rg/chunking/resume_chunker.py` — context-budget-aware chunking of long resumes (10+ years experience truncation strategy).

Current state: orphaned. Today's PA truncates to 20K chars by simple `[:budget_remaining]` slicing, no chunk semantics.

### 29. Spine Manifest — **MEDIUM IMPACT (missed in v1)**

`@apps_rg/spine_manifest.yaml` — declarative binding between apps_rg and the agentic spine. Defines what spine routes apps_rg consumes/produces, allowed cross-app delegations.

Current state: file exists in current repo but not loaded by current dispatch path.

### 30. Bootstrap Runtime — **LOW IMPACT (missed in v1)**

`@apps_rg/bootstrap_runtime.py` + `@apps_rg/services/runtime/bootstrap.py` — runtime service wiring (registers apps_rg services with the spine, sets up trace registry, initializes governance plane).

Current state: still on disk in apps_rg/ but not invoked from the current `__main__.py`.

---

# Pass 3 — Configuration & Policy Layer (missed in v1 + v2)

The deeper sweep revealed that apps_rg has a **declarative policy layer** of ~30 YAML files that defines everything from prompt assembly slots to HITL triggers. The current pipeline reads ONE file (`rg_prompt_profile.yaml`, only 2 fields). All of this remains on disk in the FRESH repo.

### 31. Versioned Prompt Template Registry — **HIGH IMPACT (missed in v1+v2)**

`@apps_rg/prompt_assembly/`:
- `prompt_registry.yaml` — registry of 8 versioned templates with required slots, output contracts, allowed stages, required modes
- `prompt_bom.yaml` — Bill-of-Materials defining 8 canonical slots with authority levels:
  - **S0** `system_and_governance` (authority: `system_governance`)
  - **I0** `resume_generation_rules` (authority: `app_instruction`)
  - **C0** `verified_resume_context` (authority: `data_only`)
  - **U0** `user_resume_request` (authority: `user_intent_only`)
  - **D0** `origin_and_injection_fences`
  - **E0** evidence
  - **Y0** style
  - **R0** rules
- `templates/` — 8 versioned templates:
  - `strategic_tailor_v1.yaml` (strategic mode generation)
  - `tailor_existing_v1.yaml` (modify existing resume)
  - `generate_scratch_v1.yaml` (from-scratch generation)
  - `enhance_current_v1.yaml` (enhance current bullets)
  - `resume_fact_check_v1.yaml` (E4_HEAL stage)
  - `unsupported_claim_omission_v1.yaml` (E4_HEAL stage)
  - `bullet_diversity_repair_v1.yaml` (repair pass)
  - `docx_manifest_v1.yaml` (DOCX manifest)

Current state: orphaned. Current PA hardcodes a single prompt format with no slot taxonomy, no template selection, no mode-aware composition.

### 32. Generation Modes — **HIGH IMPACT (missed in v1+v2)**

OLD pipeline supported 4 generation modes (selected at runtime):
- `strategic_tailor` — analyze JD, strategically position candidate's strengths
- `tailor_existing` — light-touch modification of candidate's existing resume
- `generate_scratch` — full from-scratch generation
- `enhance_current` — enhance current bullets without restructuring

Plus 2 healing modes (auto-triggered on gate failure):
- `resume_fact_check` — verify claims trace to source
- `unsupported_claim_omission` — strip unsupported claims

Current state: **no mode selection.** Always generates from scratch with a single hardcoded prompt.

### 33. Static L3 DAG — **MEDIUM IMPACT (missed in v1+v2)**

`@apps_rg/config/l3_dag.yaml` — declarative pipeline DAG:
- 8 nodes (`intake` → `plan` → `route` → `l3_bind` → `c0` → `pa` → `l2` → `exit`/`docx_export`)
- Per-node `step_contract_schema` + `allowed_execution_surface`
- L3 authority declarations: `l3_no_execute_policy`, `l3_no_retrieve_policy`, `l3_no_prompt_assembly_policy`, `l3_no_l4_write_policy`
- Bound to capability `apps_rg.resume_generation_v1`
- E2E proof harness verifies DAG invariants: acyclic, has entry+terminal, every node has owner, etc.

Current state: file exists, not loaded by current dispatch.

### 34. Quality Gate Thresholds — **HIGH IMPACT (missed in v1+v2)**

`@apps_rg/config/rg_thresholds.yaml`:
- `min_quality_score: 0.75`
- `min_ats_score: 70`
- `max_words: 1000`, `min_words: 200`
- `keyword_density_target: 3.0`, `max_keyword_density: 8.0`
- `preferred_section_order: [summary, skills, experience, education, certifications]`
- `required_sections: [summary, experience, skills]`

Current state: orphaned. Generated resumes today have no quality threshold check, no word count enforcement, no ATS scoring.

### 35. HITL Trigger Policy — **HIGH IMPACT (missed in v1+v2)**

`@apps_rg/config/hitl_trigger_policy.yaml` — 6 declarative trigger conditions:

| Trigger | Severity | Auto-freeze | When |
|---|---|---|---|
| `MISSING_BRIEF` | HIGH | true | Company brief absent |
| `STALE_BRIEF` | MEDIUM | false | `stale_age_days=30` exceeded |
| `UNSUPPORTED_CLAIM` | HIGH | true | Claim not traceable to master resume |
| `LOW_CONFIDENCE` | MEDIUM | false | Generation confidence below floor |
| `RELEASE_APPROVAL` | HIGH | true | Run is releasable but needs human OK |
| `CACHE_PROMOTION` | LOW | false | Cache row promotable to canonical |

Each trigger has `default_options` (decision choices) with `is_recommended` + `consequence`. `RuntimeAuthorGate` reads this file to freeze runs and surface decisions to humans.

Current state: orphaned. No HITL surface in current dispatch.

### 36. L0 Routing Policy — **MEDIUM IMPACT (missed in v1+v2)**

`@apps_rg/config/l0_policy.yaml`:
- `default_capability: apps_rg.resume_generation_v1`
- 3 preconditions: `jd_file_exists`, `brief_file_exists`, `jd_json_valid`
- Per-precondition `failure_disposition`: `reject` (exit 2, U0 E1 rejection) or `r5_terminal` (R5 fallback packet)
- R1B semantic cache config (`enabled: true`, `cache_adapter: apps_rg.cache.r1b_adapter.AppsRgR1BCacheAdapter`, `--skip-r1b-check` skip flag)
- C0 bypass declaration (`always: true`, `reason: GROUNDING_NOT_REQUIRED`) — **the OLD pipeline did NOT use C0 retrieval; it loaded JD + brief at U0 and passed them through**
- L3 bypass declaration (uses static DAG, `l3_required: false`)
- R5 terminal packet framework — graceful failure to fallback states

Current state: orphaned. **Critically, the OLD pipeline declared `GROUNDING_NOT_REQUIRED` — but the current pipeline DOES invoke C0 retrieval.** This is an architectural divergence the user should know about.

### 37. U0 Intake Policy — **MEDIUM IMPACT (missed in v1+v2)**

`@apps_rg/config/intake_policy.yaml`:
- `accepted_transports: [cli]` (CLI-only; no HTTP, no webhook)
- `required_fields: [transport, source_channel, user_id, jd_payload, jd_hash]`
- `identity_defaults` (tenant_id, user_id, source_channel)
- `jd_schema_path: apps_rg/config/jd_schema.json` (JD schema validation at U0 E4 gate)
- `max_body_text_bytes: 4096`

Current state: orphaned. Current U0 binding doesn't validate transport, doesn't enforce JD schema, doesn't check `jd_hash` for replay determinism.

### 38. Canonical Agent Spec v1 — **HIGH IMPACT (missed in v1+v2)**

`@apps_rg/config/specs/agent_spec.resume_generation.v1.0.0.yaml`:
- `spec_id: agt_rgresume000000000000001` — registry-bound identity
- `spec_version: "0.1.0"`, `signed_by` field for L5 attestation
- `purpose.success_criteria` (5 explicit criteria including ATS≥70, quality≥0.75, "no fabricated companies/dates/credentials beyond master resume", deterministic replay)
- `scope.allowed_tasks` (10): `ingest_master_resume`, `ingest_job_description`, `extract_ats_keywords`, `prioritize_achievements`, `compose_summary`, `compose_experience_bullets`, `compose_skills_section`, `check_ats_compatibility`, `score_quality`, `render_output_bundle`
- `scope.disallowed_tasks` (6): `fabricate_employment_history`, `fabricate_credentials`, `inflate_metrics_beyond_source`, `emit_protected_demographics`, `emit_salary_history`, `mimic_jd_phrasing_as_persona`
- `scope.audience` (tenant, team, role)
- `scope.out_of_scope_behavior: DECLINE`
- `agency.tier: WORKFLOW` (not autonomous; deterministic pipeline)
- `agency.max_tool_calls_per_turn: 0`, `agency.max_turns: 1`
- `agency.parallel_tool_calls: false`

Current state: spec exists in canonical location, but **current pipeline does not load it, does not enforce `disallowed_tasks`, does not check `success_criteria`.** The spec essentially documents what the pipeline SHOULD do; the runtime does whatever the LLM decides.

### 39. Domain Contract YAMLs — **MEDIUM IMPACT (missed in v1+v2)**

`@apps_rg/config/domain_contract/` — 18 declarative YAMLs:

| File | Defines |
|---|---|
| `app_domain_manifest.yaml` | Top-level domain manifest |
| `cache_profiles.yaml` | Cache configuration profiles |
| `capability_profiles.yaml` | Capability declarations |
| `eval_rubrics.yaml` | Evaluation rubrics |
| `fixtures.yaml` | Test fixtures |
| `grader_roster.yaml` | Roster of graders / judges |
| `input_contract.yaml` | Input contract schema |
| `learning_profiles.yaml` | Learning profile declarations |
| `negative_controls.yaml` | Negative control set |
| `orchestration_profiles.yaml` | Orchestration profiles |
| `output_schema.yaml` | Output schema |
| `prompt_profiles.yaml` | Prompt profiles |
| `repair_profiles.yaml` | Repair profile (healing strategies) |
| `retrieval_profiles.yaml` | Retrieval profiles |
| `route_profiles.yaml` | Route profiles |
| `rubric_output_map.yaml` | Maps rubric → output dimensions |
| `task_classes.yaml` | Task class declarations |
| `threshold_profiles.yaml` | Threshold profiles |

Current state: declared, not consumed by the dispatch path.

### 40. 6 Profile YAMLs — **HIGH IMPACT (missed in v1+v2)**

`@apps_rg/profiles/`:

| Profile | Purpose | Currently consumed? |
|---|---|---|
| `rg_capability_profile.yaml` | Capability declaration (formats, content domains) | NO |
| `rg_evidence_profile.yaml` | Evidence rules (extraction patterns, quantified achievements taxonomy) | NO |
| `rg_output_schema.json` | Output JSON schema | NO |
| `rg_planning_profile.yaml` | Planning constraints (max_sections=7, required_sections list) | Partial — referenced by L1 binding for digest, content not loaded |
| `rg_prompt_profile.yaml` | Style constraints (forbidden_phrases, power_verbs, duplicate_similarity_target) | Partial — only `forbidden_phrases` + `power_verbs` extracted |
| `rg_style_profile.yaml` | Voice/tone (professional, achievement_oriented, metric_driven, concise, tone_guidance) | NO |

Current PA loses: `preferred_patterns` (passive→active examples), `duplicate_similarity_target=0.85`, voice/tone guidance, evidence extraction patterns, output schema validation, content domain hints.

### 41. JD Schema + JD Plan Rules — **MEDIUM IMPACT (missed in v1+v2)**

- `@apps_rg/config/jd_schema.json` — JSON schema for JD payload validation (the U0 E4 schema gate)
- `@apps_rg/config/jd_plan_rules.yaml` — JD planning rules (how to interpret JD fields for plan emission)
- `@apps_rg/L1_cognition/jd_planner.py` — JD planner module (currently unused by the new L1 binding)

Current state: orphaned. Current U0 doesn't validate JD shape; current L1 doesn't run a JD planner.

### 42. Route Registry + Cert Route Registry — **MEDIUM IMPACT (missed in v1+v2)**

- `@apps_rg/config/route_registry.yaml` — apps_rg route definitions
- `@apps_rg/config/cert_route_registry.yaml` — certified route subset for compliance runs

Current state: orphaned.

### 43. Static DAG (Additional) + Warmup Pairs — **LOW IMPACT (missed in v1+v2)**

- `@apps_rg/config/apps_rg_static_dag.yaml` — additional static DAG (different from `l3_dag.yaml`)
- `@apps_rg/config/warmup_pairs.yaml` — cache warmup pairs (preload semantic cache with high-value queries)

Current state: orphaned.

### 44. Multi-Provider Env Var Surface — **HIGH IMPACT (missed in v1+v2; user-named explicitly)**

`@.env.example` defines but current pipeline does NOT consume:

**Provider keys**:
- `OPENAI_API_KEY`, `OPENAI_MODEL=gpt-5.4-mini`
- `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL=claude-sonnet-4-6`
- `GOOGLE_API_KEY`, `GEMINI_API_KEY`
- `GEMINI_MODEL=gemini-3-flash-preview`, `GEMINI_PRO_MODEL=gemini-3.1-pro-preview`, `GEMINI_FLASH_MODEL`

**Judge / consensus**:
- `JUDGE_PROVIDER` — provider selection for LLM-judge
- `CONSENSUS_JURORS` — list of jurors for consensus scoring
- `USE_QWEN_CONSENSUS_JUROR=` — include Qwen as juror

**Frontier (premium tier)**:
- `FRONTIER_API_BASE_URL`, `FRONTIER_API_KEY` — frontier model gateway

Current state: vars defined, **never read by current dispatch.** L2 binding hardcoded to `localhost:8000` Qwen.

### 45. Narrative Pass Env Vars — **MEDIUM IMPACT (missed in v1+v2)**

apps_rg-specific narrative pass configuration:
- `NARRATIVE_LENIENT_CRITICAL` — narrative tolerance gate
- `NARRATIVE_TEMP_LADDER` — ensemble temperature schedule (low → high re-tries)
- `ANTHROPIC_NARRATIVE_GENERATOR_MODEL`, `ANTHROPIC_NARRATIVE_JUDGE_MODEL`
- `GEMINI_NARRATIVE_GENERATOR_MODEL`
- `OPENAI_NARRATIVE_GENERATOR_MODEL`, `OPENAI_NARRATIVE_JUDGE_MODEL`

Current state: vars defined, never read.

### 46. Cache Env Vars — **MEDIUM IMPACT (missed in v1+v2)**

- `EXACT_CACHE_D1_ENABLED=1` — R1A exact cache writeback + D1 gate
- `SEMANTIC_CACHE_D2_ENABLED=1` — R1B semantic cache
- `SEMANTIC_CACHE_PROMOTE_ENABLED=1` — promote semantic cache hits to canonical
- `SEMANTIC_CACHE_L1_WARMUP_LIMIT=256` — warmup row limit

Current state: env vars exist; the cache infrastructure exists in `apps_rg/cache/` and `agentic_core/L0_routing/c0_retrieval/` (semantic cache) but the apps_rg dispatch path doesn't consult it.

### 47. Embedding / Hive-Mind Env Vars — **MEDIUM IMPACT (missed in v1+v2)**

- `EMBEDDING_ENABLED=true`, `EMBEDDING_DEVICE=cuda`, `AGENTIC_EMBEDDING_PROVIDER=bge-m3`, `EMBEDDING_MODEL_ID=bge-m3-v1`
- `HIVE_MIND_STRICT_MODE`, `HIVE_MIND_MIN_CONFIDENCE=0.98`, `HIVE_MIND_PROMOTION_THRESHOLD=0.8`, `HIVE_MIND_TRACE_SAMPLING_RATE=1.0`, `HIVE_MIND_WORKING_MEMORY_TTL=86400`, `HIVE_MIND_LONG_TERM_TTL=604800`
- `HIVE_MIND_RETRIEVAL_CONFIG_HASH`, `HIVE_MIND_EMBEDDING_MODEL_VERSION`

Current state: vars exist, semantic-cache layer wired in core for some apps, but apps_rg dispatch path doesn't engage it.

### 48. Hugging Face Env Vars — **LOW IMPACT (missed in v1+v2)**

- `HF_TOKEN`, `HUGGINGFACE_HUB_TOKEN` — for model downloads
- `HF_HOME`, `HUGGINGFACE_HUB_CACHE` — cache locations

Current state: needed by vLLM container; not read by apps_rg dispatch.

### 49. Cache-Busting Hashes — **LOW IMPACT (missed in v1+v2)**

- `APPS_RG_BLUEPRINT_HASH` — cache-bust apps_rg blueprint cache
- `APPS_RG_POLICY_HASH` — cache-bust apps_rg policy cache

Current state: vars defined, not read.

### 50. Apps_rg Cert Layer — **MEDIUM IMPACT (missed in v1+v2)**

`@apps_rg/cert/`:
- `__init__.py` — registers FEC producer via side-effect (`register_producer("apps_rg", produce_fec)`)
- `fec_producer.py` — produces `FinalEvidenceContract` with grounded/template/retrieval-source taxonomy

Current state: present per memory `e24c888b` but **the current dispatch path produces its own FEC at C0 stage in `agentic_core/runtime/c0/apps_rg_c0_binding.py`**, not via this hook. The `apps_rg.cert.produce_fec` shape carries:
- `producer`, `grounded`, `retrieval_sources`, `template_ids`, `route_id`, `evidence_sufficiency`

Loss: when C0 retrieval wires to real corpus, this hook flips `grounded=True` and `evidence_sufficiency='grounded'` automatically. Current C0 produces a different shape.

### 51. Apps_rg Airlock Layer — **MEDIUM IMPACT (missed in v1+v2)**

`@apps_rg/airlocks/`:
- `_otel_spans.py` — OTEL span emitters
- `c0_evidence.py` — C0 evidence airlock (validates evidence shape before C0 stage)
- `template_input.py` — template input airlock

Current state: airlock present but not invoked from dispatch path.

### 52. _quarantine — **CONFIRMED REMOVALS (missed in v1+v2)**

`@apps_rg/_quarantine/` — explicitly removed during consolidation:
- `compiler.py` — the OLD prompt/intent compiler (drove generation modes)
- `HardenedanthropicexecutorStrategy.py` — Anthropic-specific hardened executor
- `ResumeAssemblyAgent.py` — the master resume assembly agent

These three files represent **deliberately quarantined capability** — the consolidation explicitly removed them. Restoring functionality requires either un-quarantining or rebuilding.

### 53. CLI Banner / `--skip-r1b-check` Backed by Real Adapter — **LOW IMPACT (missed in v1+v2)**

OLD `--skip-r1b-check` flag was backed by `apps_rg.cache.r1b_adapter.AppsRgR1BCacheAdapter` per `l0_policy.yaml`. The adapter exists in current repo but isn't invoked. So the flag (already missing from current CLI, per v1) AND its underlying cache adapter are both orphaned.

---

# Pass 4 — Exit Criteria + Runtime Gate Mesh + Test Surface

The deepest sweep revealed that **the X1/X2/X3 framework AND a 29-gate runtime safety mesh both exist in `agentic_core/` but are bypassed by the apps_rg dispatch path**. This is the largest architectural gap and the one most directly responsible for today's hallucination defect.

### 54. X1A-X1J Exit Criteria Framework — **CRITICAL P0 (missed in v1+v2+v3)**

`@agentic_core/L3_orchestration/exit_eval/v6/x1_gates.py` (~600 LOC) implements 10 X1 gate evaluators:

| Gate | Function | What it checks |
|---|---|---|
| **X1A** | `eval_x1a` | Today's Rules — policy_hash, blueprint_hash, threshold profile, grader roster fresh |
| **X1B** | `eval_x1b` | Answered It — task completion, format conformance, instruction fit |
| **X1C** | `eval_x1c` | Safe to Leave — sandbox status, mutation authority, egress policy |
| **X1D** | `eval_x1d` | **Answer Good — groundedness, faithfulness, citations** ← would have caught today's hallucination |
| **X1E** | `eval_x1e` | Trajectory OK — tool choice, retry pattern, handoff, process |
| **X1F** | `eval_x1f` | Story Adds Up — internal consistency, cross-step logic |
| **X1G** | `eval_x1g` | Replay Eligible — replay key, idempotency, manifest |
| **X1H** | `eval_x1h` | Observable — OTEL tree completeness, counters, audit trail |
| **X1I** | `eval_x1i` | Consistent Across Runs — pass^k, drift, variance for high-impact runs |
| **X1J** | `eval_x1j` | Write Eligibility — pre-UWG readiness for durable mutation |

Plus orchestrators `run_all_x1_gates(packet)` + `run_all_x1_gates_with_sub_stages(packet)`.

`@agentic_core/L3_orchestration/exit_eval/v6/x2_matrix.py` — X2 aggregation (combines X1A-X1J verdicts with policy weights, applies threshold profile, treats UNKNOWN as not PASS, computes aggregate severity, produces ONE disposition recommendation).

`@agentic_core/L3_orchestration/exit_eval/v6/x3_dispositions.py` — X3 dispositions:
- **X3A** DENY / REROUTE (policy break, safety break, bad route)
- **X3B** ESCALATE_HITL (low confidence, ambiguity, high impact)
- **X3C** COMMIT_REQUEST_TO_UWG (durable mutation requested and cleared)
- **X3D** ALLOW / FINISH (answer-only path, safe to return)
- **X3E** SAFE_ABSTAIN (no safe answer can be returned)

**Constitutional invariant from the spec**: "every run exits exactly one X3 disposition; no silent fallback; no two-faced exit."

**Current state**: `@agentic_core/runtime/exit/apps_rg_exit_binding.py` is **~170 LOC that writes JSON and returns `X3Disposition(exit_status='success')`**. It does NOT:
- Build an `ExitReviewPacket` with the required fields (run_id, route_contract, policy_hash, blueprint_hash, replay_key, terminal_class, capability_token, sandbox_envelope, evidence refs, FEC, PromptAssemblyStatus, CompiledPromptArtifact, ExecTrace, OTEL spans, anomaly flags, HITL packet)
- Run any X1A-X1J gate
- Call `x2_matrix` aggregation
- Apply policy weights or threshold profile
- Select among X3A-X3E based on aggregate verdict

**This is the single largest architectural gap** — the entire exit-review apparatus exists in core but apps_rg's exit binding bypasses it.

### 55. 29-Gate Runtime Safety Mesh (G01-G29) — **CRITICAL P0 (missed in v1+v2+v3)**

`@agentic_core/L5_safety/runtime_gates/` has **29 numbered runtime safety gates**:

| Gate | Concern |
|---|---|
| `g01_request_ingress` | Inbound request validation |
| `g02_identity_session` | Identity / session correctness |
| `g03_intent_ambiguity` | Ambiguous intent detection |
| `g04_safety_policy` | Safety policy compliance |
| `g05_risk_tier` | Risk tier classification |
| `g06_hitl_approval` | HITL approval requirement |
| `g07_route_selection` | Route selection correctness |
| `g08_retrieval_grounding` | Retrieval / grounding required |
| **`g09_evidence_quality`** | **Evidence quality (groundedness)** ← would catch hallucinations |
| `g10_prompt_assembly` | Prompt assembly correctness |
| `g11_tool_model_registry` | Tool / model registry validation |
| `g12_tool_argument` | Tool argument validation |
| `g13_tool_output_trust` | Tool output trust |
| `g14_external_egress` | External egress policy |
| `g15_filesystem_shell` | Filesystem / shell access |
| `g16_memory_access` | Memory access |
| `g17_privacy_cross_context` | Privacy cross-context |
| **`g18_workflow_trajectory`** | **Workflow trajectory consistency** |
| `g19_loop_retry_thrash` | Loop / retry thrash detection |
| `g20_cost_latency_budget` | Cost / latency budget |
| **`g21_output_schema`** | **Output schema validation** ← would catch malformed JSON |
| **`g22_output_quality`** | **Output quality threshold** ← would enforce min_quality≥0.75 |
| `g23_security_leakage` | Security leakage |
| `g24_determinism_replay` | Determinism / replay |
| `g25_runtime_anomaly` | Runtime anomaly |
| `g26_exit_disposition` | Exit disposition correctness |
| `g27_durable_write_sovereignty` | Durable write sovereignty |
| `g28_audit_trace_completeness` | Audit trace completeness |
| **`g29_learning_firewall`** | **Learning firewall (no leakage)** |

Plus a `dispatch.py`, `enforcement.py`, `orchestrator.py`, `mesh_result.py`, `layer_invocation_map.py`, `baseline_registry.py`, `digest.py`, `ctx_builders.py`, `otel_feed.py`, `otel_spans.py`, `structural_na_bundle.py`.

**Current state**: 29 gates implemented; apps_rg dispatch path invokes ZERO. The CI gate `@ops_scripts/ci/check_apps_rg_runtime_gate_hardening.py` validates that the gate MODULES exist and exports are correct — but it doesn't verify the dispatch INVOKES them.

`@agentic_core/L5_safety/runtime_gates/orchestrator.py` provides the dispatcher to run all 29 gates; current apps_rg never calls it.

### 56. AppsRgIntegratedPipeline — **HIGH IMPACT (missed in v1+v2+v3)**

`@agentic_core/runtime/entrypoints/apps_rg_integrated_pipeline.py`:
```python
class AppsRgIntegratedPipeline:
    def execute(self, ...) -> X3Disposition:
        ...
        x3_disposition = self.exit_emitter.emit(l2_artifact)
        return x3_disposition
    
    def execute_with_audit(self, ...) -> tuple[X3Disposition, L7RuntimeAuditTrace]:
        ...
        x3_disposition = self.exit_emitter.emit(l2_artifact)
        return x3_disposition, audit_trace
```

This pipeline exists, integrates L2 → Exit (X3Disposition) → L7 (Audit Trace) via `ExitDispositionEmitter`. **But the current `apps_rg/__main__.py` does NOT invoke `AppsRgIntegratedPipeline`** — it goes through `AppIngressRunner.run() → apps_rg_dispatch()` which uses the thin `apps_rg_exit_binding`.

**Two parallel exit paths exist in core:**
- `agentic_core/runtime/entrypoints/apps_rg_integrated_pipeline.py` (with X3 emitter + L7 audit)
- `agentic_core/runtime/exit/apps_rg_exit_binding.py` (thin JSON write)

The thin one is the one actually wired to apps_rg today.

### 57. Provider Util Status — **CONFIRMED P0 (refines v3 #44)**

`@apps_shared/utils/provider_util.py` EXISTS and exports:
- `Provider` enum (`OPENAI`, `ANTHROPIC`, `GOOGLE`)
- `MultiProviderClient` class with async `completion(prompt, provider)`
- `get_client(provider)` — returns a client per provider
- `get_instructor_client(provider)` — returns instructor-wrapped client
- `get_litellm_completion(provider, messages)` — LiteLLM unified completion
- `get_default_model(provider)` — returns canonical model per provider:
  - OPENAI: `"gpt-4o"` ⚠️ stale (.env says `gpt-5.4-mini`)
  - ANTHROPIC: `"claude-sonnet-4-6"` ✓ matches .env
  - GOOGLE: `"gemini-pro"` ⚠️ stale (.env says `gemini-3-flash-preview`)

**HOWEVER**: `@apps_shared/types/multi_provider_clients.py` is **stubbed**:
```python
class _StubClient:
    def interactions(self, *args, **kwargs): ...
def get_client(provider) -> _StubClient: ...
```

So there are two `Provider`/`get_client` definitions — one in `utils/provider_util.py` (real, with LiteLLM) and one in `types/multi_provider_clients.py` (stub). Resolving which is canonical and verifying live API calls work is part of the rewire.

Also `@apps_shared/types/multi_provider_clients.py` reference confirms multi-provider was a documented apps_shared capability.

### 58. 21 Test Fixtures — **DOCUMENT THE INTENT (missed in v1+v2+v3)**

`@tests/_apps_contract/test_apps_rg_*.py` — 21 test files exercising apps_rg behaviors. The tests are governance-shape tests (assert forbidden patterns ABSENT) more than capability-presence tests:

| Test file | What it asserts |
|---|---|
| `test_apps_rg_acceptance_checks.py` | Run-time acceptance checks |
| `test_apps_rg_artifact_completeness.py` | Artifact completeness |
| `test_apps_rg_cannot_inject_l2_callable.py` | apps_rg cannot inject L2 callable (governance) |
| `test_apps_rg_core_resolves_l2_recipe.py` | Core resolves L2 recipe (governance) |
| `test_apps_rg_cross_company_contamination_guard.py` | Cross-company contamination guard |
| **`test_apps_rg_e4_heal_steps.py`** | **E4 heal steps (resume_fact_check, unsupported_claim_omission)** |
| **`test_apps_rg_e5_seal_step.py`** | **E5 seal step** |
| `test_apps_rg_generate_step_requires_compiled_prompt_artifact.py` | Generate requires CompiledPromptArtifact |
| `test_apps_rg_generate_step_uses_compiled_artifact_only.py` | Generate uses compiled artifact only |
| `test_apps_rg_l2_steps_only_via_core_recipe.py` | L2 only via core recipe |
| `test_apps_rg_llm_step_requires_pa_artifact.py` | LLM requires PA artifact |
| `test_apps_rg_missing_recipe_fails_closed.py` | Missing recipe fails closed |
| `test_apps_rg_no_ad_hoc_prompt_model_call.py` | No ad-hoc LLM calls outside PA |
| `test_apps_rg_pa_compiles_prompt_artifact.py` | PA compiles artifact |
| `test_apps_rg_pa_failure_blocks_model_call.py` | PA failure blocks model |
| `test_apps_rg_pa_governance.py` | PA governance enforcement |
| `test_apps_rg_pipeline_capability.py` | Pipeline capability declaration |
| `test_apps_rg_prompt_artifact_in_sealed_l2_output.py` | Prompt artifact in sealed L2 |
| `test_apps_rg_prompt_bom_exists.py` | Prompt BOM file exists |
| **`test_apps_rg_prompt_slots_fence_untrusted_data.py`** | **S0/I0/C0/U0/D0 slot fencing — proves the slot taxonomy is enforced** |
| `test_apps_rg_runtime_artifact_threading.py` | Runtime artifact threading |

Memory `bf13593c` calls these "test theater" — they assert forbidden patterns absent, not capability present. So the tests pass even though the runtime doesn't fire E4 heal, E5 seal, or actual slot-fenced prompt assembly.

### 59. CI Gates for apps_rg — **CONFIRMED 4 GATES (missed in v1+v2+v3)**

`@ops_scripts/ci/`:

| Gate | Validates |
|---|---|
| `check_apps_rg_import.py` | `python -m apps_rg --help` exit 0 |
| `check_apps_rg_dryrun.py` | `python -m apps_rg --dry-run` exit 0 with DRY RUN marker |
| `check_apps_rg_pa_boundary.py` | apps_rg/ contains NO prompt-assembly code (governance — must be in core) |
| `check_apps_rg_runtime_gate_hardening.py` | Required gate modules exist + export `provenance_required_gate` etc |

**None of these gates verify capability — they verify boundary/import/governance.** A pipeline that imports cleanly, has no PA code in apps_rg/, and has the gate modules registered will pass all 4 gates while still being an empty hallucinating shell.

### 60. Apps_rg-Specific L5 Validators — **MEDIUM IMPACT (missed in v1+v2+v3)**

`@agentic_core/L5_safety/validators/`:
- `ats_validator.py` — ATS compatibility validator (referenced in grep)
- And likely more apps_rg-specific validators in this directory

Current state: validators exist; not invoked from apps_rg dispatch.

### 61. Engine Sub-Categorization Refinement — **REFINES v1 #6 + v2 #15 (Pass 1+2 understated)**

Pass 1 categorized 50 engines as P3 polish. **Pass 4 reclassifies the safety-critical subset as P0:**

| Engine | Original P-tier | Refined P-tier | Why |
|---|---|---|---|
| `hallucination_detector.py` | P3 | **P0** | Direct catch for today's defect |
| `fact_check_engine.py` | P3 | **P0** | Cross-references claims to source |
| `verbatim_provenance_gate.py` | P1 | **P0** | Per-bullet provenance verification |
| `bullet_diversity_gate.py` | P1 | **P0** (gate) | Prevents single-theme overfitting |
| `quality_inspector_engine.py` | P3 | P1 | Composite quality verdict |
| `ats_compatibility_engine.py` | P2 | P1 | Drives ATS≥70 threshold |
| `fit_score_calibrator.py` | P2 | P1 | Drives quality≥0.75 threshold |
| `effectiveness_scorer.py` | P3 | P2 | Effectiveness rating |
| `writing_quality_engine.py` | P3 | P2 | Style + grammar |
| `duplicate_detector.py` | P3 | P2 | `duplicate_threshold=0.85` enforcement |

The 4 promoted-to-P0 engines + the 4 anti-overfit gates (P1) + the 5 validators (P3 in v2) + the X1A-X1J framework (P0 newly) + the 29 runtime gates (P0 newly) collectively form the **safety mesh** that the OLD apps_rg pipeline ran on every output. The current pipeline runs ZERO of them.

## Summary by Priority

| Priority | Category | Capability | Reason |
|---|---|---|---|
| P0 | LLM | Multi-provider LLM (Anthropic/OpenAI/Google) via env keys | User explicitly named this; current Qwen-only is a regression |
| P0 | Gates | Hallucination + provenance gates | Today's RCA showed a hallucination defect that gates would have caught |
| P0 | Gates | Two-phase generation (extract → narrate) | Phase-1 anchoring prevents the hallucination class we just hit |
| P0 | Config | Generation knobs (temperature, max_tokens, n_candidates) | User config intent — already on `GenerationConfig` |
| P0 | HITL | HITL bridge (read run report → human review → re-run) | Quality control loop |
| P1 | Pipeline | HOP 7-stage pipeline | Whole orchestration model lost; current is single-shot |
| P1 | Pipeline | Role-specific ensembles + judges (EY/TS/IBM/Unify/Marquee/Headline) | Multi-role bullet generation lost |
| P1 | Gates | Output gates (VerbatimProvenance, BulletDiversity, JdEnforcement) | Quality control lost |
| P1 | Gates | Anti-overfitting gates (buzzword soup, mirror density, filler) | Authenticity protection |
| P1 | Routing | Cross-app spine handoff (apps_research / apps_lic delegation) | `--research-via` flag exists but does nothing |
| P1 | Research | Tavily web research supplement | `--auto-research-tavily` exists but does nothing |
| P1 | Research | Company research loader + facet extractor (`CompanyBrief`) | C0 reads brief as path-only; never structured |
| P1 | Provenance | Per-bullet provenance tracking (source quote, transformation log) | Today's `evidence_anchor` is hardcoded; real provenance lost |
| P1 | Output | Length budgeting (per-section word budgets from master resume) | Section sizing |
| P2 | Config | ResumeConfig knobs (target_format, max_length_words, ats_optimization, highlight_leadership, min_skill_matches, target_industry) | User intent surface |
| P2 | Cache | Cache layer (R1A exact + R1B semantic + pool-first selection) | Performance + determinism + cost |
| P2 | Output | DOCX output (`docx_exporter`) | UX regression — JSON only today |
| P2 | Output | Rich `RunReport` (gate verdicts, ATS scores, skill matches, provenance) vs current minimal JSON | Reporting depth |
| P2 | Reasoning | Reasoning toggles (CoT, reflexion, ToT, temperature_cap) + ReasoningIntensityProfile from L0 | Reasoning intensity per task |
| P2 | Engines | ATS compatibility, fit score calibrator, hallucination detector, fact check engine | User-facing scoring |
| P2 | Pipeline | Narrative pass (post-generation polish, headline/exec-summary hops) | Output quality |
| P2 | Config | RGAgentSpecs nested config (8 sections, ~50 knobs) | Fine-tuned per-stage behavior |
| P2 | Spine | Spine manifest binding | Cross-app contract |
| P3 | Engines | ~50 other specialized scoring engines (writing quality, section ranker, etc.) | Polish |
| P3 | Healing | Healing cycle (`max_factual_loops=3`, `max_creative_retries=5`) | Quality recovery |
| P3 | Reasoning | 14 reasoning agents (ContentQualityAgent, etc.) | Most superseded by single LLM call |
| P3 | Tools | 30 specialized tool surfaces (CalibrateFitScore, ResumeGenerator, etc.) | Agent tool calls |
| P3 | Utils | Intent builder (`IntentPayload` → flow router) | Domain richness in ingress |
| P3 | Utils | Repo signal service (GitHub signals → bullets) | Optional enrichment |
| P3 | Utils | Deep brain harvester (history mining) | Optional enrichment |
| P3 | Validators | 5 validators (jd_enforcement, validation_gate, hallucination_detector, regeneration, validation_result) | Composite validation rules |
| P3 | Prerequisites | Briefing validator (well-formedness pre-check) | Input sanity |
| P3 | Audit | Audit & live-fire scripts (rg_final_audit, rg_sovereign_auditor, rg_live_fire) | Optional |
| P3 | Chunking | Resume chunker (context-budget-aware chunking) | Output quality on long resumes |
| P3 | Bootstrap | Runtime bootstrap service wiring | Spine integration |
| P0 | Prompt | Versioned prompt template registry (8 templates, 4 modes + healing/repair) | Single hardcoded prompt today |
| P0 | Modes | 4 generation modes (strategic_tailor / tailor_existing / generate_scratch / enhance_current) | No mode selection today |
| P0 | Quality | Quality gate thresholds (min_quality≥0.75, min_ats≥70, word bounds) | No quality enforcement |
| P0 | HITL | 6 HITL trigger policies (MISSING_BRIEF, STALE_BRIEF, UNSUPPORTED_CLAIM, LOW_CONFIDENCE, RELEASE_APPROVAL, CACHE_PROMOTION) | No HITL surface today |
| P0 | Spec | Canonical agent spec v1 (allowed/disallowed tasks, success_criteria, agency tier, signed_by L5) | Runtime ignores spec |
| P0 | LLM Env | Multi-provider env vars (OPENAI/ANTHROPIC/GOOGLE/GEMINI keys + models) | All defined, none read |
| P0 | Multi-Judge | Narrative pass env vars (per-provider generator + judge models) | All defined, none read |
| P1 | Policy | L0 routing policy (preconditions, R5 fallback, R1B cache, C0 bypass) | Architectural divergence: OLD declared GROUNDING_NOT_REQUIRED |
| P1 | Policy | U0 intake policy (transports, required fields, JD schema, replay determinism via jd_hash) | Current U0 doesn't validate |
| P1 | Slots | 8-slot prompt BOM (S0/I0/C0/U0/D0/E0/Y0/R0 with authority levels) | No slot taxonomy today |
| P1 | Profiles | 6 profile YAMLs (capability, evidence, output_schema, planning, prompt, style) | Only 2 fields from 1 file loaded |
| P1 | Schema | JD schema validation (U0 E4 gate) + JD plan rules | No schema enforcement |
| P2 | DAG | Static L3 DAG (8 nodes, authority declarations) | DAG file exists, not validated |
| P2 | Spec | 18 domain contract YAMLs (rubrics, fixtures, profiles, etc.) | Declared, not consumed |
| P2 | Cert | apps_rg cert FEC producer hook (`apps_rg.cert.produce_fec`) | Bypassed by core C0 |
| P2 | Airlock | C0 evidence airlock | Not invoked |
| P2 | Cache Env | EXACT_CACHE_D1, SEMANTIC_CACHE_D2/PROMOTE/L1_WARMUP env vars | Defined, not consulted |
| P3 | Routes | route_registry.yaml + cert_route_registry.yaml | Not loaded |
| P3 | Embedding | EMBEDDING_*, HIVE_MIND_*, HF_*, AGENTIC_EMBEDDING_* env vars | Not engaged for apps_rg |
| P3 | Cache-bust | APPS_RG_BLUEPRINT_HASH, APPS_RG_POLICY_HASH | Not read |
| P3 | Bootstrap | Static DAG (apps_rg_static_dag.yaml) + warmup pairs | Not loaded |
| ⚠️ | Quarantine | `_quarantine/` (compiler.py, ResumeAssemblyAgent.py, HardenedanthropicexecutorStrategy.py) | **Deliberately removed** during consolidation |

## Two-Path Decision

The user said "preserve in U0 input." That can mean two things:

**Path A — Carry intent only**: extend `AppsRgIngressPayload` with all the config flags (provider preference, knobs, toggles). Downstream layers ignore them today, but the ingress contract preserves the user's intent. Future plans wire downstream layers to honor them. **Risk**: contract bloat without runtime benefit; the user might think the configs work when they don't.

**Path B — Carry intent + wire executions**: extend the payload AND re-wire L0/L1/L2 to honor the new fields. **Risk**: scope explosion — re-implementing 50 engines + multi-provider routing + HOP pipeline + gates is a multi-month rewrite, not a single plan.

Recommended hybrid:
1. Extend payload with **P0 + P1 + P2** intent fields (model_provider, model_name, temperature_override, max_tokens_override, target_format, max_length_words, ats_optimization, highlight_leadership, min_skill_matches, target_industry, skip_r1a_cache, skip_r1b_cache, require_briefing, n_candidates, enable_hop_pipeline, enable_gates, enable_healing, reasoning_intensity).
2. Wire the **P0 multi-provider routing** in L2 (Anthropic/OpenAI/Google + Qwen) — single highest-value rewire, ~1 day of work.
3. Wire **P0 hallucination gate** at Exit — second-highest-value rewire, ~1 day.
4. Defer P1/P2/P3 wiring to follow-up plans.

This keeps the ingress contract honest (it carries everything) while delivering the two highest-value re-wires.
