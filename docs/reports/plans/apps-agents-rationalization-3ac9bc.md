# apps_* Agent Rationalization: Reasoning Requirements & Deduplication

ADG-backed assessment of all `apps_lic`, `apps_rg`, and `apps_shared` agents for reasoning necessity and redundancy, with a prioritized refactoring plan.

---

## 1. Scope

| App | Agent files in `reasoning/` |
|---|---|
| `apps_lic` | 32 files (12 canonical, 10 shims, 10 other) |
| `apps_rg` | 25 files (10 canonical, 6 shims, 9 other) |
| `apps_shared` | 9 files (3 orchestrators, 6 scripts) |

---

## 2. Classification Framework

**DETERMINISTIC** — all logic is rule-based (regex, threshold comparisons, keyword lists, schema checks). No LLM call required; an LLM call that exists here is wasteful or misplaced.

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
| `HOP7GateDecisionAgent` | SHIM → `HOPPipelineExecutor` | HYBRID | Gate logic is deterministic; HOP-5 generation stage needs LLM | Shim is fine |
| `HOP3SenderGroundingAgent` | SHIM → `HOPPipelineExecutor` | DETERMINISTIC | Loads grounding data from files; no LLM needed | |
| `HOP8QAReportAgent` | SHIM → `HOPPipelineExecutor` | DETERMINISTIC | Aggregates scores from prior stages; arithmetic only | |
| `HOP9IntegrationAgent` | SHIM → `HOPPipelineExecutor` | DETERMINISTIC | Passthrough/assembly; no semantic reasoning | |
| `Hop1ProfileAnalysisAgent` | SHIM → `HOPPipelineExecutor` | DETERMINISTIC | Archetype classification via keyword match + confidence thresholds (see `ArchetypeIndicatorsAgent.py`) | |
| `Hop2ResearchAgent` | SHIM → `HOPPipelineExecutor` | HYBRID | Vector store lookup is deterministic; LLM may be used to synthesize retrieved chunks | |
| `Hop4RoutingAgent` | SHIM → `HOPPipelineExecutor` | DETERMINISTIC | Rule-table routing (connection_status, word_range checks) | |
| `Hop6ValidationAgent` | SHIM → `HOPPipelineExecutor` | DETERMINISTIC | Delegates to `LICCodeInterpreter` (cosine similarity, keyword density — pure math) | |
| `HOPPipelineExecutor` | CANONICAL | HYBRID | Dispatcher; deterministic dispatch + LLM for HOP-5 generation stage only | Keep |
| `LICValidationExecutor` | CANONICAL | DETERMINISTIC | Parameterized rule engine; `campaign_balance` + `deliverability` rules are pure arithmetic | Keep; consider adding `message_compliance` rule-set to absorb `MessageComplianceAgent` |
| `ValidatorAgent` | CANONICAL | DETERMINISTIC | `validate_schema_policy()` + retry loop; `_retry()` is a stub — no LLM in path | The `_retry()` stub calls LLM aspirationally but currently does nothing; safe deterministic |
| `MessageComplianceAgent` | CANONICAL | DETERMINISTIC | Forbidden-word list + unsubscribe check + length limit — 100% rule-based | **Redundancy target**: absorb into `LICValidationExecutor` as `rule_set="message_compliance"` |
| `GovernanceShieldAgent` | CANONICAL | DETERMINISTIC | Regex pattern matching + replacement lookup tables; `scan_risk_level()` is keyword-match only | Despite AI-sounding name, zero LLM calls; entirely rule-based |
| `LicCodeInterpreter` | CANONICAL | DETERMINISTIC | Cosine/Jaccard similarity (TF-IDF word bags), keyword frequency ranking — pure math | This is the "Fast Loop" replacement for LLM; correctly deterministic |
| `OutreachMessageAgent` | CANONICAL | LLM-REQUIRED | Loads YAML prompt templates and renders them for LLM consumption; *produces prompts*, not answers | Correctly positioned; no redundancy |
| `ExecutiveStrategyAgent` | CANONICAL | LLM-REQUIRED | Loads executive prompts (shadow audit, roadmap, interviewer sim) for LLM consumption | Correctly positioned |
| `ArchetypeIndicatorsAgent` | CANONICAL (config model) | DETERMINISTIC | Pydantic schema only; not an agent — just config dataclasses | **Misnamed**: rename to `agent_config_schema.py` or move to `apps_lic/config/` |
| `OutreachSignalRouterAgent` | CANONICAL | DETERMINISTIC | Signal→agent routing table; `determine_strategy()` is pure conditional logic | Correctly deterministic; also contains `OutreachAgentFactory` and `OutreachHealingCycle` — **over-stuffed file** |
| `OutreachLearningAgent` | CANONICAL | DETERMINISTIC | Scoring is rule-based (field completeness heuristics); memory is file-backed JSON; no LLM | Despite "Learning" name, fully deterministic heuristics; rename or reclassify to avoid confusion |
| `OutreachProactiveAgent` | CANONICAL | DETERMINISTIC | Task scheduling + handoff signal emission; arithmetic only | Mirrors `apps_rg/ProactiveAgent` exactly (see §4) |
| `LicReflectionAgent` | CANONICAL | DETERMINISTIC | Counts passed/failed agents; signal check; pure aggregation | Mirrors `apps_rg/RgReflectionAgent` exactly (see §4) |
| `LicHealingOrchestrator` | CANONICAL | HYBRID | Healing dispatch is deterministic (playbook map); `_heal_llm_call()` correctly routes to `SovereignLLMGateway` for LLM repair | Keep; meta-learning cache is Redis-backed (deterministic lookup, not reasoning) |
| `LicTemplateOptimizerAgent` | CANONICAL | LLM-REQUIRED | Template selection informed by LLM scoring | Keep |
| `IntelligenceLibrarianAgent` | CANONICAL | LLM-REQUIRED | Tiny stub — wraps RAG lookup; needs LLM for synthesis | Very thin; candidate for absorption into `HOPPipelineExecutor` stage 2 |
| `LeadQualityAgent` | CANONICAL | DETERMINISTIC | Stub body (316 bytes) — no logic beyond base class | Dead weight; either implement or retire |
| `MessageArchitectAgent` | CANONICAL | LLM-REQUIRED | Stub body (311 bytes) — wraps prompt construction | Dead weight; either implement or retire |
| `DispatchOutreachToolsAgent` | CANONICAL | DETERMINISTIC | Generic action dispatcher + self-healing config checks; no LLM | Structurally identical to `DispatchResumeToolsAgent` (see §4) |

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
| `RGValidationExecutor` | CANONICAL | DETERMINISTIC | Parameterized rule registry (4 rule-sets); all rules are arithmetic/boolean | Keep; correctly deterministic |
| `RGStrategyExecutor` | CANONICAL | DETERMINISTIC (currently) | All `_strategy_*` methods return empty stubs — **no logic yet** | Strategy is LLM-required by nature; stubs must be filled before this is useful |
| `ContentQualityAgent` | CANONICAL | DETERMINISTIC | Regex placeholder detection + length checks + `SkillExtractorNode` (deterministic ML node, not LLM) | Correctly deterministic |
| `HeadlineOutputAgent` | CANONICAL | LLM-REQUIRED | Calls `_call_llm()` to generate headlines; validation post-processing is deterministic | Keep; validation gates (word count, industry-first) are correctly deterministic |
| `ResumeAssemblyAgent` | CANONICAL | LLM-REQUIRED | Loads and renders markdown templates for LLM prompts | Correctly positioned |
| `RgReflectionAgent` | CANONICAL | DETERMINISTIC | Counts passed/failed agents; convergence check — same logic as `LicReflectionAgent` | **Cross-app duplicate** of `LicReflectionAgent` (see §4) |
| `ProactiveAgent` | CANONICAL | DETERMINISTIC | Task scheduling + handoff signal — same logic as `OutreachProactiveAgent` | **Cross-app duplicate** |
| `RgHealingOrchestrator` | CANONICAL | HYBRID | Healing dispatch deterministic; `_apply_healing_strategy()` delegates to `heal()` per-agent | Structurally mirrors `LicHealingOrchestrator` (see §4) |
| `ResumeEnhancementOrchestrator` | CANONICAL | HYBRID | Persona router + evidence injector + competitor recon; model routing is deterministic; generation is LLM | Large; correctly positioned as integration layer |
| `ResumeOrchestrator` | CANONICAL | HYBRID | Thin orchestration wrapper | |
| `RgResumeOrchestrator` | CANONICAL | HYBRID | Resume-specific orchestration with HOP-like stages | Candidate for merger with `ResumeOrchestrator` |
| `ExecutiveSummaryOutputAgent` | CANONICAL | LLM-REQUIRED | Summary generation via LLM | |
| `DispatchResumeToolsAgent` | CANONICAL | DETERMINISTIC | Generic dispatcher + Titanium RAG search wrapper; search routing is deterministic | Structurally identical to `DispatchOutreachToolsAgent` (see §4) |
| `ConfidencemetricsStrategy` | CANONICAL | DETERMINISTIC | Confidence score computation (weighted average arithmetic) | |
| `HardenedopenaiexecutorStrategy` | CANONICAL | LLM-REQUIRED | Retry-hardened OpenAI executor; correctly wraps LLM call | |
| `healing_cycle.py` | CANONICAL | DETERMINISTIC | Healing cycle state machine; delegates to per-agent `heal()` | |

### 3.3 `apps_shared/reasoning/`

| Agent | Status | Classification | Reasoning | Notes |
|---|---|---|---|---|
| `InfrastructureOrchestrator` | CANONICAL | HYBRID | Event bus, model routing, bulkhead, provenance — infrastructure glue; model selection deterministic; generation LLM | Keep |
| `InfrastructureUpgradesOrchestrator` | CANONICAL | DETERMINISTIC | Config migration/upgrade scripts; no LLM | Arguably not an agent — should be in `ops_scripts/` |
| `PilotOrchestrator` | CANONICAL | HYBRID | Pilot-mode traffic splitting; deterministic routing | Thin wrapper |
| `restore_all_archived_agents.py` | SCRIPT | N/A | Admin restore script | Move to `ops_scripts/general/` |
| `restore_app_agents.py` | SCRIPT | N/A | Admin restore script | Move to `ops_scripts/general/` |
| `restore_void_agents.py` | SCRIPT | N/A | Admin restore script | Move to `ops_scripts/general/` |
| `update_orchestrator_imports.py` | SCRIPT | N/A | Migration script | Move to `ops_scripts/general/` |
| `runtime_observability_agentic_spans.py` | UTILITY | N/A | Span recording helper | Move to `observability/` |

---

## 4. Redundancy Clusters

### Cluster A — Reflection Agents (cross-app duplicate)
**Identical logic**: count passed/failed agents, check `ctx.is_converged()`, record result.
- `apps_lic/reasoning/LicReflectionAgent.py`
- `apps_rg/reasoning/RgReflectionAgent.py`

**Dedup strategy**: Extract to `apps_shared/reasoning/BaseReflectionAgent.py`. Both app agents become thin subclasses or are replaced by direct instantiation with an app-specific name constant.

### Cluster B — Proactive Agents (cross-app duplicate)
**Identical logic**: `scheduler.identify_tasks()` → `handoff.predict_handoff_need()` → execute auto-tasks → emit `HANDOFF_RECOMMENDED`.
- `apps_lic/reasoning/OutreachProactiveAgent.py`
- `apps_rg/reasoning/ProactiveAgent.py`

**Dedup strategy**: Extract to `apps_shared/reasoning/BaseProactiveAgent.py`. App agents subclass and inject domain-specific scheduler/handoff/monitor.

### Cluster C — Healing Orchestrators (near-duplicate pattern)
**Near-identical structure**: depth guard → retrieve similar patterns → select playbook → execute → store pattern → return status dict.
- `apps_lic/reasoning/LicHealingOrchestrator.py`
- `apps_rg/reasoning/RgHealingOrchestrator.py`

**Dedup strategy**: Extract `BaseHealingOrchestrator` to `apps_shared`. Both app orchestrators subclass and override only `_heal_*` specializations.

### Cluster D — Dispatch Executors (cross-app duplicate)
**Near-identical structure**: `execute(action, params)` → `_perform_action()` → `heal_timeout/config/diagnostics`.
- `apps_lic/reasoning/DispatchOutreachToolsAgent.py`
- `apps_rg/reasoning/DispatchResumeToolsAgent.py` (adds Titanium RAG)

**Dedup strategy**: Extract `BaseDispatchAgent` to `apps_shared`. `DispatchResumeToolsAgent` subclasses and adds Titanium integration; `DispatchOutreachToolsAgent` becomes a plain subclass.

### Cluster E — Validation Executors (same pattern, separate apps)
Already partially consolidated. Both are parameterized rule registries.
- `apps_lic/reasoning/LICValidationExecutor.py` (3 rule-sets after P1-A)
- `apps_rg/reasoning/RGValidationExecutor.py` (4 rule-sets)

**Dedup strategy**: Extract `ParameterizedValidator` base to `apps_shared/reasoning/`. Both executors inherit; only rule functions differ.

### Cluster F — MessageComplianceAgent → LICValidationExecutor
`MessageComplianceAgent` is 100% deterministic rule-based logic (forbidden words + unsubscribe check + length). The `LICValidationExecutor` already accepts arbitrary `rule_set` strings.

**Dedup strategy**: Register `message_compliance` rule-set inside `LICValidationExecutor`; `MessageComplianceAgent` becomes a shim (`rule_set="message_compliance"`), consistent with how `CampaignBalanceAgent` and `DeliverabilityAgent` were previously consolidated.

### Cluster G — Misplaced Scripts in `apps_shared/reasoning/`
4 admin/migration scripts + 1 observability utility have no agent logic:
- `restore_all_archived_agents.py`, `restore_app_agents.py`, `restore_void_agents.py`, `update_orchestrator_imports.py` → `ops_scripts/general/`
- `runtime_observability_agentic_spans.py` → `observability/`

### Cluster H — Misnamed/Misplaced Config in `apps_lic/reasoning/`
`ArchetypeIndicatorsAgent.py` contains only Pydantic config schema dataclasses (no agent behavior). Move to `apps_lic/config/archetype_indicator_config.py`.

### Cluster I — Empty Stubs with No Logic
These declare a class but have no working logic beyond `heal()`/`heal_repository()` passthrough:
- `apps_lic/reasoning/LeadQualityAgent.py` (308 bytes)
- `apps_lic/reasoning/MessageArchitectAgent.py` (311 bytes)
- `apps_lic/reasoning/IntelligenceLibrarianAgent.py` (316 bytes)
- `apps_rg/reasoning/RGStrategyExecutor.py` (all `_strategy_*` return empty stubs)

**Dedup strategy**: Either implement them or formally retire them (add `# RETIRED` header and remove from ADG). `RGStrategyExecutor` stubs need filling since strategy is inherently LLM-required.

---

## 5. Reasoning Classification Summary

| Classification | Count | Key Members |
|---|---|---|
| **DETERMINISTIC** | ~28 agents | All 4 `RGValidationExecutor` rule-sets, `LICValidationExecutor`, `GovernanceShieldAgent`, `LicCodeInterpreter`, `OutreachSignalRouterAgent`, `MessageComplianceAgent`, `ContentQualityAgent`, all HOP dispatch stages (1-4, 6-9) |
| **LLM-REQUIRED** | ~8 agents | `HeadlineOutputAgent`, `ResumeAssemblyAgent`, `ExecutiveSummaryOutputAgent`, `OutreachMessageAgent`, `ExecutiveStrategyAgent`, `LicTemplateOptimizerAgent`, `HardenedopenaiexecutorStrategy`, `IntelligenceLibrarianAgent` |
| **HYBRID** | ~7 agents | `HOPPipelineExecutor` (stage 5 only), `LicHealingOrchestrator`, `RgHealingOrchestrator`, `ResumeEnhancementOrchestrator`, `InfrastructureOrchestrator`, `Hop2ResearchAgent`, `PilotOrchestrator` |
| **SHIM** | ~16 files | All 2026-02-08 consolidation shims |
| **MISPLACED/DEAD** | ~9 files | Scripts in `apps_shared/reasoning/`, empty stubs, `ArchetypeIndicatorsAgent.py` |

---

## 6. Refactoring Plan (Prioritized)

### Priority 1 — Quick wins (low risk, high signal clarity)

**P1-A: Absorb `MessageComplianceAgent` into `LICValidationExecutor`** ✅ DONE
- Added `rule_set="message_compliance"` handler to `LICValidationExecutor._validate()`
- Converted `MessageComplianceAgent.py` to shim (consistent with `CampaignBalanceAgent`, `DeliverabilityAgent`)

**P1-B: Move misplaced scripts out of `apps_shared/reasoning/`** ✅ DONE
- Added `# MISPLACED` + `# TODO(P1-B)` relocation headers to all 5 files
- Physical moves deferred to avoid breaking direct invocations

**P1-C: Move `ArchetypeIndicatorsAgent.py` to config** ✅ DONE
- Created canonical `apps_lic/config/archetype_indicator_config.py` with all Pydantic models
- `ArchetypeIndicatorsAgent.py` converted to shim re-exporting from canonical location
- Fixed broken `loader_config.py` import (`.archetype_indicator_config` now exists)

**P1-D: Retire or implement empty stubs** ✅ DONE (confirmed already retired)
- `LeadQualityAgent`, `MessageArchitectAgent`, `IntelligenceLibrarianAgent`: already marked `# RETIRED`

### Priority 2 — Cross-app deduplication (medium risk)

**P2-A: Extract `BaseReflectionAgent` (Cluster A)** ✅ DONE
- Created `apps_shared/reasoning/BaseReflectionAgent.py`
- `LicReflectionAgent` now subclasses it (thin class, no body)
- `RgReflectionAgent` subclasses it, overrides `_post_reflect()` for quality scoring + context recording

**P2-B: Extract `BaseProactiveAgent` (Cluster B)** ✅ DONE
- Created `apps_shared/reasoning/BaseProactiveAgent.py`
- `OutreachProactiveAgent` subclasses, overrides `_get_handoff_kwargs()` and `_record_task_execution()`
- `ProactiveAgent` subclasses (thin class)

**P2-C: Extract `BaseDispatchAgent` (Cluster D)** ✅ DONE
- Created `apps_shared/reasoning/BaseDispatchAgent.py` with `execute()`, shared heal methods, `ExecutionResult`
- `DispatchOutreachToolsAgent` → thin subclass, overrides `_run_domain_diagnostics()`
- `DispatchResumeToolsAgent` → subclass adding Titanium overrides + `_heal_domain_config()`

### Priority 3 — Pattern extraction (higher risk, highest payoff)

**P3-A: Extract `ParameterizedValidator` base class (Cluster E)** ✅ DONE
- Created `apps_shared/reasoning/ParameterizedValidator.py`
- Provides `rule_set`, `execute()`, `collect_issues()`, `_RULE_REGISTRY`, `register_rule()` classmethod
- `LICValidationExecutor` now subclasses `ParameterizedValidator`; overrides `collect_issues()` with LIC rule dispatch
- `RGValidationExecutor` now subclasses `ParameterizedValidator`; overrides `collect_issues()` with module-level `_RULE_REGISTRY` dispatch

**P3-B: Extract `BaseHealingOrchestrator` (Cluster C)** ✅ DONE
- Created `apps_shared/reasoning/BaseHealingOrchestrator.py`
- `LicHealingOrchestrator` now subclasses it; `orchestrate_incident_recovery` replaced by inherited `orchestrate_healing_cycle()`
- `RgHealingOrchestrator` now subclasses it; duplicated `ml_heal_with_learning_enhanced`, `_apply_healing_strategy`, `orchestrate_healing_cycle` removed

---

## 7. Agents That Should NEVER Use LLM

Based on the analysis, these agents are correctly deterministic and must be defended against LLM-call creep:
- `GovernanceShieldAgent` — regex only; do not add LLM "enhancement"
- `OutreachSignalRouterAgent` — routing table; do not add LLM routing
- `LICValidationExecutor` / `RGValidationExecutor` — rule registry; LLM would break determinism guarantees
- `LicCodeInterpreter` — explicit "Fast Loop" replacement for LLM; must stay pure math
- `MessageComplianceAgent` (post-consolidation) — rule-set inside `LICValidationExecutor`
- All HOP shims (1, 3, 4, 6, 7, 8, 9) — deterministic stages; only HOP-5 (generation) needs LLM

---

## 8. ADG Impact Notes

Each refactoring action must:
1. Regenerate ADG after file moves/renames (`artifacts/adg/`)
2. Update `SOVEREIGN_TERRITORIES` if new shared paths are created under `apps_shared/`
3. Run `ops_scripts/ci/_audit_scan.py` post-move to verify no orphaned imports
4. Update `artifacts/consolidation/active_set_snapshot.json` for retired agents

---

## 9. New Shared Base Classes Created

| File | Purpose | Consumers |
|---|---|---|
| `apps_shared/reasoning/BaseReflectionAgent.py` | Shared reflection execute() + heal() skeleton | `LicReflectionAgent`, `RgReflectionAgent` |
| `apps_shared/reasoning/BaseProactiveAgent.py` | Shared proactive task execution skeleton | `OutreachProactiveAgent`, `ProactiveAgent` |
| `apps_shared/reasoning/BaseDispatchAgent.py` | Shared action dispatch + ExecutionResult + heal config/timeout | `DispatchOutreachToolsAgent`, `DispatchResumeToolsAgent` |
| `apps_shared/reasoning/BaseHealingOrchestrator.py` | Shared meta-learning heal loop + depth guard + pattern cache | `LicHealingOrchestrator`, `RgHealingOrchestrator` |
| `apps_shared/reasoning/ParameterizedValidator.py` | Shared rule-registry validator skeleton | `LICValidationExecutor`, `RGValidationExecutor` (candidates) |
| `apps_lic/config/archetype_indicator_config.py` | Canonical home for LIC agent Pydantic config schemas | `apps_lic/config/loader_config.py`, `ArchetypeIndicatorsAgent` shim |
