# apps_* Agent Rationalization: Reasoning Requirements & Deduplication

ADG-backed assessment of all `apps_lic`, `apps_rg`, and `apps_shared` agents for reasoning necessity and redundancy, with a prioritized refactoring plan.

**ADG verification artifact:** `artifacts/adg/adg_full_20260311T140400Z.json` (regenerated post-implementation, 2026-03-11)

---

## 1. Scope

| App | Agent files in `reasoning/` |
|---|---|
| `apps_lic` | 32 files (12 canonical, 10 shims, 10 other) |
| `apps_rg` | 25 files (10 canonical, 6 shims, 9 other) |
| `apps_shared` | 14 files (3 original orchestrators, 5 new base classes, 6 misplaced scripts) |

---

## 2. Classification Framework

**DETERMINISTIC** — all logic is rule-based (regex, threshold comparisons, keyword lists, schema checks). No LLM call required.

**LLM-REQUIRED** — task involves open-ended generation, semantic judgment, or context synthesis that cannot be reduced to rules without quality loss.

**HYBRID** — deterministic guard-rails + LLM for the generation step only.

**SHIM** — backward-compat stub; re-exports a canonical executor. Zero logic.

---

## 3. Agent-by-Agent Assessment

### 3.1 `apps_lic/reasoning/`

| Agent | Status | Classification | Reasoning | Notes |
|---|---|---|---|---|
| `CampaignBalanceAgent` | SHIM → `LICValidationExecutor` | DETERMINISTIC | Channel ratio threshold check (`ratio > 0.7`) | Shim is fine; canonical logic is correctly deterministic |
| `DeliverabilityAgent` | SHIM → `LICValidationExecutor` | DETERMINISTIC | spam score + DKIM/SPF boolean checks | Same as above |
| `MessageComplianceAgent` | SHIM → `LICValidationExecutor` | DETERMINISTIC | Forbidden-word list + unsubscribe check + length — 100% rule-based | Absorbed as `rule_set="message_compliance"` (P1-A) ✅ |
| `HOP7GateDecisionAgent` | SHIM → `HOPPipelineExecutor` | HYBRID | Gate logic is deterministic; HOP-5 generation stage needs LLM | Shim is fine |
| `HOP3SenderGroundingAgent` | SHIM → `HOPPipelineExecutor` | DETERMINISTIC | Loads grounding data from files; no LLM needed | |
| `HOP8QAReportAgent` | SHIM → `HOPPipelineExecutor` | DETERMINISTIC | Aggregates scores from prior stages; arithmetic only | |
| `HOP9IntegrationAgent` | SHIM → `HOPPipelineExecutor` | DETERMINISTIC | Passthrough/assembly; no semantic reasoning | |
| `Hop1ProfileAnalysisAgent` | SHIM → `HOPPipelineExecutor` | DETERMINISTIC | Archetype classification via keyword match + confidence thresholds | |
| `Hop2ResearchAgent` | SHIM → `HOPPipelineExecutor` | HYBRID | Vector store lookup is deterministic; LLM may synthesize retrieved chunks | |
| `Hop4RoutingAgent` | SHIM → `HOPPipelineExecutor` | DETERMINISTIC | Rule-table routing (connection_status, word_range checks) | |
| `Hop6ValidationAgent` | SHIM → `HOPPipelineExecutor` | DETERMINISTIC | Delegates to `LICCodeInterpreter` (cosine similarity, keyword density — pure math) | |
| `HOPPipelineExecutor` | CANONICAL | HYBRID | Dispatcher; deterministic dispatch + LLM for HOP-5 generation stage only | Keep |
| `LICValidationExecutor` | CANONICAL | DETERMINISTIC | Parameterized rule engine (3 rule-sets); now subclasses `ParameterizedValidator` | Keep ✅ P1-A + P3-A |
| `ValidatorAgent` | CANONICAL | DETERMINISTIC | `validate_schema_policy()` + retry loop; `_retry()` is a stub | Safe deterministic |
| `GovernanceShieldAgent` | CANONICAL | DETERMINISTIC | Regex pattern matching + replacement lookup tables; keyword-match only | Despite AI-sounding name, zero LLM calls |
| `LicCodeInterpreter` | CANONICAL | DETERMINISTIC | Cosine/Jaccard similarity (TF-IDF word bags), keyword frequency — pure math | "Fast Loop" replacement for LLM |
| `OutreachMessageAgent` | CANONICAL | LLM-REQUIRED | Loads YAML prompt templates for LLM consumption | Correctly positioned |
| `ExecutiveStrategyAgent` | CANONICAL | LLM-REQUIRED | Loads executive prompts for LLM consumption | Correctly positioned |
| `ArchetypeIndicatorsAgent` | SHIM → `archetype_indicator_config.py` | DETERMINISTIC | Pydantic schema only; not an agent | Relocated to `apps_lic/config/` (P1-C) ✅ |
| `OutreachSignalRouterAgent` | CANONICAL | DETERMINISTIC | Signal→agent routing table; `determine_strategy()` is pure conditional logic | |
| `OutreachLearningAgent` | CANONICAL | DETERMINISTIC | Scoring is rule-based field completeness heuristics; no LLM | |
| `OutreachProactiveAgent` | CANONICAL | DETERMINISTIC | Task scheduling + handoff signal; now subclasses `BaseProactiveAgent` | P2-B ✅ |
| `LicReflectionAgent` | CANONICAL | DETERMINISTIC | Counts passed/failed agents; now subclasses `BaseReflectionAgent` | P2-A ✅ |
| `LicHealingOrchestrator` | CANONICAL | HYBRID | Healing dispatch (playbook map); `_heal_llm_call()` uses `SovereignLLMGateway`; now subclasses `BaseHealingOrchestrator` | P3-B ✅ |
| `LicTemplateOptimizerAgent` | CANONICAL | LLM-REQUIRED | Template selection informed by LLM scoring | Keep |
| `IntelligenceLibrarianAgent` | RETIRED | LLM-REQUIRED | Tiny stub marked `# RETIRED` | P1-D ✅ |
| `LeadQualityAgent` | RETIRED | DETERMINISTIC | Stub marked `# RETIRED` | P1-D ✅ |
| `MessageArchitectAgent` | RETIRED | LLM-REQUIRED | Stub marked `# RETIRED` | P1-D ✅ |
| `DispatchOutreachToolsAgent` | CANONICAL | DETERMINISTIC | Generic action dispatcher; now subclasses `BaseDispatchAgent` | P2-C ✅ |

### 3.2 `apps_rg/reasoning/`

| Agent | Status | Classification | Reasoning | Notes |
|---|---|---|---|---|
| `ATSCompatibilityAgent` | SHIM → `RGValidationExecutor` | DETERMINISTIC | Keyword presence checks | |
| `BrandComplianceAgent` | SHIM → `RGValidationExecutor` | DETERMINISTIC | Tone field check + superlative flag | |
| `FactCheckAgent` | SHIM → `RGValidationExecutor` | DETERMINISTIC | Date overlap detection + source presence check | |
| `SectionBalanceAgent` | SHIM → `RGValidationExecutor` | DETERMINISTIC | Length ratio arithmetic | |
| `ContentStrategyAgent` | SHIM → `RGStrategyExecutor` | DETERMINISTIC | Stub returning empty recommendations | |
| `RgStrategicPlannerAgent` | SHIM → `RGStrategyExecutor` | DETERMINISTIC | Stub returning empty plan | |
| `RgTemplateOptimizerAgent` | SHIM → `RGStrategyExecutor` | DETERMINISTIC | Stub returning empty optimizations | |
| `RGValidationExecutor` | CANONICAL | DETERMINISTIC | Parameterized rule registry (4 rule-sets); now subclasses `ParameterizedValidator` | P3-A ✅ |
| `RGStrategyExecutor` | CANONICAL | DETERMINISTIC (stubs) | All `_strategy_*` return empty stubs — no logic yet | Stubs need LLM implementation |
| `ContentQualityAgent` | CANONICAL | DETERMINISTIC | Regex placeholder detection + length checks + `SkillExtractorNode` | |
| `HeadlineOutputAgent` | CANONICAL | LLM-REQUIRED | Calls `_call_llm()` to generate headlines | Keep |
| `ResumeAssemblyAgent` | CANONICAL | LLM-REQUIRED | Loads and renders markdown templates for LLM prompts | Keep |
| `RgReflectionAgent` | CANONICAL | DETERMINISTIC | Counts passed/failed agents; now subclasses `BaseReflectionAgent` | P2-A ✅ |
| `ProactiveAgent` | CANONICAL | DETERMINISTIC | Task scheduling + handoff signal; now subclasses `BaseProactiveAgent` | P2-B ✅ |
| `RgHealingOrchestrator` | CANONICAL | HYBRID | Healing dispatch; now subclasses `BaseHealingOrchestrator` | P3-B ✅ |
| `ResumeEnhancementOrchestrator` | CANONICAL | HYBRID | Persona router + evidence injector; generation is LLM | Keep |
| `ResumeOrchestrator` | CANONICAL | HYBRID | Thin orchestration wrapper | |
| `RgResumeOrchestrator` | CANONICAL | HYBRID | Resume-specific orchestration with HOP-like stages | Candidate for merger with `ResumeOrchestrator` |
| `ExecutiveSummaryOutputAgent` | CANONICAL | LLM-REQUIRED | Summary generation via LLM | |
| `DispatchResumeToolsAgent` | CANONICAL | DETERMINISTIC | Generic dispatcher + Titanium RAG; now subclasses `BaseDispatchAgent` | P2-C ✅ |
| `ConfidencemetricsStrategy` | CANONICAL | DETERMINISTIC | Confidence score computation (weighted average arithmetic) | |
| `HardenedopenaiexecutorStrategy` | CANONICAL | LLM-REQUIRED | Retry-hardened OpenAI executor | Keep |
| `healing_cycle.py` | CANONICAL | DETERMINISTIC | Healing cycle state machine; delegates to per-agent `heal()` | |

### 3.3 `apps_shared/reasoning/`

| File | Status | Classification | Notes |
|---|---|---|---|
| `InfrastructureOrchestrator` | CANONICAL | HYBRID | Event bus, model routing, bulkhead — infrastructure glue | Keep |
| `InfrastructureUpgradesOrchestrator` | CANONICAL | DETERMINISTIC | Config migration scripts; no LLM | Should be in `ops_scripts/` |
| `PilotOrchestrator` | CANONICAL | HYBRID | Pilot-mode traffic splitting | Keep |
| `BaseReflectionAgent.py` | NEW BASE | DETERMINISTIC | Shared reflection skeleton (P2-A) ✅ | |
| `BaseProactiveAgent.py` | NEW BASE | DETERMINISTIC | Shared proactive task execution skeleton (P2-B) ✅ | |
| `BaseDispatchAgent.py` | NEW BASE | DETERMINISTIC | Shared action dispatch + heal config/timeout skeleton (P2-C) ✅ | |
| `BaseHealingOrchestrator.py` | NEW BASE | HYBRID | Shared meta-learning heal loop + depth guard + pattern cache (P3-B) ✅ | |
| `ParameterizedValidator.py` | NEW BASE | DETERMINISTIC | Shared rule-registry validator skeleton (P3-A) ✅ | |
| `restore_all_archived_agents.py` | MISPLACED SCRIPT | N/A | `# MISPLACED` header added; move to `ops_scripts/general/` (P1-B) ✅ |
| `restore_app_agents.py` | MISPLACED SCRIPT | N/A | `# MISPLACED` header added; move to `ops_scripts/general/` (P1-B) ✅ |
| `restore_void_agents.py` | MISPLACED SCRIPT | N/A | `# MISPLACED` header added; move to `ops_scripts/general/` (P1-B) ✅ |
| `update_orchestrator_imports.py` | MISPLACED SCRIPT | N/A | `# MISPLACED` header added; move to `ops_scripts/general/` (P1-B) ✅ |
| `runtime_observability_agentic_spans.py` | MISPLACED UTILITY | N/A | `# MISPLACED` header added; move to `observability/` (P1-B) ✅ |

---

## 4. Redundancy Clusters — Resolution Status

| Cluster | Description | Resolution |
|---|---|---|
| **A** | Reflection agents (LIC + RG cross-app duplicate) | ✅ `BaseReflectionAgent` extracted; both subclass it |
| **B** | Proactive agents (LIC + RG cross-app duplicate) | ✅ `BaseProactiveAgent` extracted; both subclass it |
| **C** | Healing orchestrators (near-duplicate pattern) | ✅ `BaseHealingOrchestrator` extracted; both subclass it |
| **D** | Dispatch executors (cross-app duplicate) | ✅ `BaseDispatchAgent` extracted; both subclass it |
| **E** | Validation executors (same registry pattern) | ✅ `ParameterizedValidator` extracted; both executors subclass it |
| **F** | `MessageComplianceAgent` → `LICValidationExecutor` | ✅ Absorbed as `rule_set="message_compliance"`; shim created |
| **G** | Misplaced scripts in `apps_shared/reasoning/` | ✅ `# MISPLACED` headers added; physical move deferred |
| **H** | `ArchetypeIndicatorsAgent` (Pydantic configs in reasoning/) | ✅ Moved to `apps_lic/config/archetype_indicator_config.py`; shim kept |
| **I** | Empty stubs (LeadQuality, MessageArchitect, IntelligenceLibrarian) | ✅ Confirmed already `# RETIRED` |

---

## 5. Reasoning Classification Summary

| Classification | Count | Key Members |
|---|---|---|
| **DETERMINISTIC** | ~28 agents | All 4 `RGValidationExecutor` rule-sets, `LICValidationExecutor`, `GovernanceShieldAgent`, `LicCodeInterpreter`, `OutreachSignalRouterAgent`, `ContentQualityAgent`, all HOP dispatch stages (1-4, 6-9) |
| **LLM-REQUIRED** | ~8 agents | `HeadlineOutputAgent`, `ResumeAssemblyAgent`, `ExecutiveSummaryOutputAgent`, `OutreachMessageAgent`, `ExecutiveStrategyAgent`, `LicTemplateOptimizerAgent`, `HardenedopenaiexecutorStrategy` |
| **HYBRID** | ~7 agents | `HOPPipelineExecutor` (stage 5 only), `LicHealingOrchestrator`, `RgHealingOrchestrator`, `ResumeEnhancementOrchestrator`, `InfrastructureOrchestrator`, `Hop2ResearchAgent`, `PilotOrchestrator` |
| **SHIM** | ~17 files | All 2026-02-08 consolidation shims + `MessageComplianceAgent` + `ArchetypeIndicatorsAgent` |
| **RETIRED** | 3 files | `LeadQualityAgent`, `MessageArchitectAgent`, `IntelligenceLibrarianAgent` |
| **MISPLACED** | 5 files | 4 restore/migration scripts + `runtime_observability_agentic_spans.py` |

---

## 6. Refactoring Plan — Completed

### Priority 1 — Quick wins ✅ ALL DONE

**P1-A: Absorb `MessageComplianceAgent` into `LICValidationExecutor`**
- Added `rule_set="message_compliance"` handler to `LICValidationExecutor.collect_issues()`
- `MessageComplianceAgent.py` → shim importing `LICValidationExecutor`
- Import path fixed: `apps_lic.reasoning.LICValidationExecutor` (not `engines`)

**P1-B: Mark misplaced scripts in `apps_shared/reasoning/`**
- Added `# MISPLACED` + `# TODO(P1-B)` relocation headers to all 5 files
- Physical moves deferred to avoid breaking direct invocations

**P1-C: Move `ArchetypeIndicatorsAgent.py` to config**
- Created `apps_lic/config/archetype_indicator_config.py` with all Pydantic models
- `ArchetypeIndicatorsAgent.py` → shim re-exporting from canonical location
- Fixed `loader_config.py` broken import

**P1-D: Retire empty stubs**
- `LeadQualityAgent`, `MessageArchitectAgent`, `IntelligenceLibrarianAgent`: confirmed `# RETIRED`

### Priority 2 — Cross-app deduplication ✅ ALL DONE

**P2-A: `BaseReflectionAgent` (Cluster A)**
- `apps_shared/reasoning/BaseReflectionAgent.py`: shared `execute()` + `_post_reflect()` hook
- `LicReflectionAgent` → thin subclass
- `RgReflectionAgent` → subclass with `_post_reflect()` for quality scoring + meta-learning cache

**P2-B: `BaseProactiveAgent` (Cluster B)**
- `apps_shared/reasoning/BaseProactiveAgent.py`: shared proactive task scheduling skeleton
- `OutreachProactiveAgent` → subclass, overrides `_get_handoff_kwargs()` + `_record_task_execution()`
- `ProactiveAgent` → thin subclass

**P2-C: `BaseDispatchAgent` (Cluster D)**
- `apps_shared/reasoning/BaseDispatchAgent.py`: shared `execute()`, `ExecutionResult`, heal config/timeout
- `DispatchOutreachToolsAgent` → thin subclass, overrides `_run_domain_diagnostics()`
- `DispatchResumeToolsAgent` → subclass adding Titanium overrides + `_heal_domain_config()`

### Priority 3 — Pattern extraction ✅ ALL DONE

**P3-A: `ParameterizedValidator` (Cluster E)**
- `apps_shared/reasoning/ParameterizedValidator.py`: `rule_set`, `execute()`, `collect_issues()`, `_RULE_REGISTRY`, `register_rule()`
- `LICValidationExecutor` → subclasses `ParameterizedValidator`; overrides `collect_issues()` with LIC dispatch
- `RGValidationExecutor` → subclasses `ParameterizedValidator`; overrides `collect_issues()` with module-level `_RULE_REGISTRY` dispatch

**P3-B: `BaseHealingOrchestrator` (Cluster C)**
- `apps_shared/reasoning/BaseHealingOrchestrator.py`: `ml_heal_with_learning_enhanced()`, `orchestrate_healing_cycle()`, `_apply_healing_strategy()`, depth guard, pattern cache
- `LicHealingOrchestrator` → subclasses it; `ml_heal_incident_enhanced()` + `_execute_recovery_playbook()` duplicates removed; `_cycle_results_key()` override retained
- `RgHealingOrchestrator` → subclasses it; `ml_heal_with_learning_enhanced()`, `_apply_healing_strategy()`, `orchestrate_healing_cycle()` duplicates removed; `cycle_results` field removed (inherited from base)

---

## 7. Agents That Should NEVER Use LLM

- `GovernanceShieldAgent` — regex only
- `OutreachSignalRouterAgent` — routing table
- `LICValidationExecutor` / `RGValidationExecutor` — rule registry; LLM breaks determinism guarantees
- `LicCodeInterpreter` — "Fast Loop" replacement for LLM; must stay pure math
- `MessageComplianceAgent` (post-consolidation) — rule-set inside `LICValidationExecutor`
- All HOP shims (1, 3, 4, 6, 7, 8, 9) — deterministic stages; only HOP-5 needs LLM

---

## 8. New Shared Base Classes Created

| File | Purpose | Consumers |
|---|---|---|
| `apps_shared/reasoning/BaseReflectionAgent.py` | Shared `execute()` + `_post_reflect()` hook | `LicReflectionAgent`, `RgReflectionAgent` |
| `apps_shared/reasoning/BaseProactiveAgent.py` | Shared proactive task scheduling skeleton | `OutreachProactiveAgent`, `ProactiveAgent` |
| `apps_shared/reasoning/BaseDispatchAgent.py` | Shared dispatch + `ExecutionResult` + heal config/timeout | `DispatchOutreachToolsAgent`, `DispatchResumeToolsAgent` |
| `apps_shared/reasoning/BaseHealingOrchestrator.py` | Shared meta-learning heal loop + depth guard + pattern cache | `LicHealingOrchestrator`, `RgHealingOrchestrator` |
| `apps_shared/reasoning/ParameterizedValidator.py` | Shared rule-registry validator skeleton | `LICValidationExecutor`, `RGValidationExecutor` |
| `apps_lic/config/archetype_indicator_config.py` | Canonical Pydantic config schemas (relocated from `reasoning/`) | `loader_config.py`, `ArchetypeIndicatorsAgent` shim |

---

## 9. ADG Verification — 2026-03-11

**Artifact:** `artifacts/adg/adg_full_20260311T140400Z.json`
**Stats:** 3,283 modules · 83,306 edges · entities=41,167 · relations=69,527
**E7 drift:** +34,704 edges, −2,910 edges, **risk_delta=−25 [IMPROVED]**

### Inheritance edge audit (ADG G1_imports confirmed)

| Subclass | Base | ADG Edge |
|---|---|---|
| `LicReflectionAgent` | `BaseReflectionAgent` | ✅ imports |
| `RgReflectionAgent` | `BaseReflectionAgent` | ✅ imports |
| `OutreachProactiveAgent` | `BaseProactiveAgent` | ✅ imports |
| `ProactiveAgent` | `BaseProactiveAgent` | ✅ imports |
| `DispatchOutreachToolsAgent` | `BaseDispatchAgent` | ✅ imports + `ExecutionResult` |
| `DispatchResumeToolsAgent` | `BaseDispatchAgent` | ✅ imports + `ExecutionResult` |
| `LicHealingOrchestrator` | `BaseHealingOrchestrator` | ✅ imports |
| `RgHealingOrchestrator` | `BaseHealingOrchestrator` | ✅ imports |
| `LICValidationExecutor` | `ParameterizedValidator` | ✅ imports |
| `RGValidationExecutor` | `ParameterizedValidator` | ✅ imports |

**GV_violates edges touching rationalized files: 0**

`MessageComplianceAgent` import resolves to `ADG::Symbol::apps_lic.reasoning.LICValidationExecutor.LICValidationExecutor` ✅

---

## 10. ADG Impact Actions Required (Post-Completion)

1. ✅ ADG regenerated — `artifacts/adg/adg_full_20260311T140400Z.json`
2. ⬜ Update `SOVEREIGN_TERRITORIES` to formally register `apps_shared/reasoning/` as a base-class territory
3. ⬜ Physically move 5 misplaced scripts (deferred — headers only)
4. ⬜ Update `artifacts/consolidation/active_set_snapshot.json` for retired agents
5. ⬜ Run `ops_scripts/ci/_audit_scan.py` after any physical file moves
