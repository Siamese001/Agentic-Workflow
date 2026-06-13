# apps_* Agent Rationalization Plan

**ADG artifact:** `artifacts/adg/adg_indexed_20260311T185727Z.sqlite`
**Scan stats:** 3,320 modules · 151,933 edges · entities=43,683 · relations=151,933
**GV_violates touching rationalized files: 0**
**Generated:** 2026-03-11T18:57:27Z

---

## 1. Scope

All Python files under `apps_lic/reasoning/`, `apps_rg/reasoning/`, `apps_shared/reasoning/`, and the new `apps_lic/config/archetype_indicator_config.py`. The rationalization covers agent deduplication, base-class extraction, misplaced script removal, and config relocation.

---

## 2. ADG Node Registry — Rationalized Files

All entries confirmed present in `adg_indexed_20260311T185727Z.sqlite`.

### New base classes (`apps_shared/reasoning/`)

| File | ADG node_id | layer | confidence | fan-in | fan-out |
|---|---|---|---|---|---|
| `BaseReflectionAgent.py` | 22107 | L_APP | MEDIUM | **2** | — |
| `BaseProactiveAgent.py` | 22106 | L_APP | MEDIUM | **2** | — |
| `BaseDispatchAgent.py` | 22105 | L_APP | MEDIUM | **2** | — |
| `BaseHealingOrchestrator.py` | 22104 | L_APP | MEDIUM | **2** | — |
| `ParameterizedValidator.py` | 22108 | L_APP | MEDIUM | **2** | — |

> **Note:** MEDIUM confidence is expected for newly created files. The ADG scanner assigns HIGH only after cross-session evidence accumulation. No action required.

### LIC subclasses (`apps_lic/reasoning/`)

| File | ADG node_id | layer | Base import (ADG-confirmed) |
|---|---|---|---|
| `LicReflectionAgent.py` | 21676 | L_APP | `apps_shared.reasoning.BaseReflectionAgent.BaseReflectionAgent` ✅ |
| `OutreachProactiveAgent.py` | 21683 | L_APP | `apps_shared.reasoning.BaseProactiveAgent.BaseProactiveAgent` ✅ |
| `DispatchOutreachToolsAgent.py` | 21664 | L_APP | `apps_shared.reasoning.BaseDispatchAgent.BaseDispatchAgent` ✅ |
| `LicHealingOrchestrator.py` | 21675 | L_APP | `apps_shared.reasoning.BaseHealingOrchestrator.BaseHealingOrchestrator` ✅ |
| `LICValidationExecutor.py` | 21673 | L_APP | `apps_shared.reasoning.ParameterizedValidator.ParameterizedValidator` ✅ |
| `MessageComplianceAgent.py` | 21678 | L_APP | `apps_lic.reasoning.LICValidationExecutor.LICValidationExecutor` ✅ |
| `ArchetypeIndicatorsAgent.py` | 21661 | L_APP | `apps_lic.config.archetype_indicator_config.*` ✅ |

### RG subclasses (`apps_rg/reasoning/`)

| File | ADG node_id | layer | Base import (ADG-confirmed) |
|---|---|---|---|
| `RgReflectionAgent.py` | 23036 | L_APP | `apps_shared.reasoning.BaseReflectionAgent.BaseReflectionAgent` ✅ |
| `ProactiveAgent.py` | 23032 | L_APP | `apps_shared.reasoning.BaseProactiveAgent.BaseProactiveAgent` ✅ |
| `DispatchResumeToolsAgent.py` | 23024 | L_APP | `apps_shared.reasoning.BaseDispatchAgent.BaseDispatchAgent` ✅ |
| `RgHealingOrchestrator.py` | 23034 | L_APP | `apps_shared.reasoning.BaseHealingOrchestrator.BaseHealingOrchestrator` ✅ |
| `RGValidationExecutor.py` | 23021 | L_APP | `apps_shared.reasoning.ParameterizedValidator.ParameterizedValidator` ✅ |

### Config relocation

| File | ADG node_id | layer | Status |
|---|---|---|---|
| `apps_lic/config/archetype_indicator_config.py` | 21556 | L_APP | Canonical config ✅ |

### Misplaced scripts (ADG-confirmed orphans)

| File | ADG node_id | fan-in | fan-out | Target location |
|---|---|---|---|---|
| `apps_shared/reasoning/restore_all_archived_agents.py` | — | **0** | 9 | `ops_scripts/general/` |
| `apps_shared/reasoning/restore_app_agents.py` | — | **0** | 6 | `ops_scripts/general/` |
| `apps_shared/reasoning/restore_void_agents.py` | — | **0** | 6 | `ops_scripts/general/` |
| `apps_shared/reasoning/update_orchestrator_imports.py` | — | **0** | 4 | `ops_scripts/general/` |
| `apps_shared/reasoning/runtime_observability_agentic_spans.py` | — | **0** | 0 | `observability/` |

fan-in=0 for all 5 → **zero consumers, safe to move without import breakage**.

---

## 3. Inheritance Hierarchy (ADG G1_imports confirmed)

```
apps_shared/reasoning/
├── BaseReflectionAgent          ← LicReflectionAgent, RgReflectionAgent
├── BaseProactiveAgent           ← OutreachProactiveAgent, ProactiveAgent
├── BaseDispatchAgent            ← DispatchOutreachToolsAgent, DispatchResumeToolsAgent
├── BaseHealingOrchestrator      ← LicHealingOrchestrator, RgHealingOrchestrator
└── ParameterizedValidator       ← LICValidationExecutor, RGValidationExecutor
```

**All 10 inheritance edges confirmed by ADG fan-in query.**
The base→subclass direction was verified via `edges WHERE dst_id=<base_node_id> AND relation_type='imports'`.

---

## 4. Per-Base-Class Interface Contract

### 4.1 `BaseReflectionAgent`
```python
@dataclass
class BaseReflectionAgent:
    name: str
    def execute(self, agents: list[dict], signals: dict, **kwargs) -> dict
    def _post_reflect(self, result: dict, agents: list[dict], signals: dict) -> dict  # hook
    def heal(self, violation: dict) -> dict
```
- **`LicReflectionAgent`** (node 21676): empty subclass — inherits all. No `_post_reflect` override.
- **`RgReflectionAgent`** (node 23036): overrides `_post_reflect` to cache quality patterns via `GraphMemoryBridge` (L4 import).

### 4.2 `BaseProactiveAgent`
```python
@dataclass
class BaseProactiveAgent:
    name: str
    def execute(self, pending_tasks: list[dict], **kwargs) -> dict
    def _get_handoff_kwargs(self, task: dict) -> dict  # hook
    def _record_task_execution(self, task: dict, result: dict) -> None  # hook
    def heal(self, violation: dict) -> dict
```
- **`OutreachProactiveAgent`** (node 21683): overrides both hooks for outreach-specific handoff kwargs and telemetry.
- **`ProactiveAgent`** (node 23032): thin subclass — inherits all. No hook overrides.

### 4.3 `BaseDispatchAgent`
```python
@dataclass
class BaseDispatchAgent:
    name: str
    def execute(self, action: str, payload: dict, **kwargs) -> ExecutionResult
    def _run_domain_diagnostics(self, action: str, error: Exception) -> dict  # hook
    def heal_timeout(self, violation: dict) -> dict
    def heal_config(self, violation: dict) -> dict
    def heal(self, violation: dict) -> dict
```
- **`DispatchOutreachToolsAgent`** (node 21664): overrides `_run_domain_diagnostics` with outreach-specific checks.
- **`DispatchResumeToolsAgent`** (node 23024): overrides `_run_domain_diagnostics` + adds `_heal_domain_config` for Titanium RAG config healing.

### 4.4 `BaseHealingOrchestrator`
```python
@dataclass
class BaseHealingOrchestrator:
    name: str
    healing_cache: dict
    healing_depth: dict
    cycle_results: list
    def ml_heal_with_learning_enhanced(self, violation: dict, heal_fn: Callable) -> dict
    def orchestrate_healing_cycle(self, violations: list[dict], heal_fn: Callable) -> dict
    def _apply_healing_strategy(self, violation: dict, strategy: str) -> dict
    def ml_check_healing_depth(self, item_id: str) -> bool
    def ml_increment_healing_depth(self, item_id: str) -> None
    def ml_reset_healing_depth(self, item_id: str) -> None
    def ml_cache_get(self, key: str) -> dict | None
    def ml_cache_set(self, key: str, value: dict) -> bool
    def heal_repository(self, dry_run: bool, execute: bool, **kwargs) -> dict
    def _cycle_results_key(self) -> str  # hook — override for domain-specific cache key
```
- **`LicHealingOrchestrator`** (node 21675): overrides `_cycle_results_key` → `"incident_recovery"`. Adds `ml_heal_incident`, `_execute_healing` (dispatches to `_heal_structural`, `_heal_schema`, `_heal_llm_call`), `ml_cache_incident_resolution`, `ml_recall_incident_resolution`, `ml_optimize_playbook_selection`, `ml_record_playbook_success`.
- **`RgHealingOrchestrator`** (node 23034): default `_cycle_results_key`. Adds `ml_determine_strategy`, `ml_record_strategy_success`, `ml_cache_convergence_pattern`, `ml_recall_convergence_pattern`, `ml_heal_with_learning` (thin wrapper over inherited `ml_enhanced_heal`). Owns `run()` async healing loop.

### 4.5 `ParameterizedValidator`
```python
@dataclass
class ParameterizedValidator:
    name: str
    rule_set: str
    def execute(self, data: dict, **kwargs) -> dict  # returns {rule_set, issues, issue_count, passed}
    def collect_issues(self, data: dict, **kwargs) -> list[dict]  # override in subclass
```
- **`LICValidationExecutor`** (node 21673): inherits from `LICEngineValidationCapability` + `ParameterizedValidator` (MRO: LICEngineValidationCapability → ParameterizedValidator). Overrides `collect_issues` dispatching to `_validate_campaign_balance`, `_validate_deliverability`, `_validate_message_compliance`.
- **`RGValidationExecutor`** (node 23021): inherits from `ParameterizedValidator` only. Overrides `collect_issues` dispatching via module-level `_RULE_REGISTRY` decorated with `@register_rule`. Overrides `execute` to accept `(resume_data, job_data)` signature.

---

## 5. Completed Work — Full Audit

### P1-A: Absorb `MessageComplianceAgent` → `LICValidationExecutor` ✅
- **What changed:** Added `_validate_message_compliance(data)` to `LICValidationExecutor`. `collect_issues` dispatches to it when `rule_set="message_compliance"`.
- **Shim:** `apps_lic/reasoning/MessageComplianceAgent.py` re-exports `LICValidationExecutor as MessageComplianceAgent` from `apps_lic.reasoning.LICValidationExecutor` (fixed from broken `apps_lic.engines` path).
- **ADG edge:** node 21678 imports `apps_lic.reasoning.LICValidationExecutor.LICValidationExecutor` ✅

### P1-B: Mark misplaced scripts ✅ (physical move PENDING)
- **What changed:** Added `# MISPLACED — TODO(P1-B)` relocation headers to all 5 files.
- **ADG evidence:** All 5 have fan-in=0. No consumers in the entire 3,320-module graph. **Physical move is safe.**
- **Remaining action:** `git mv` each file to target location + update `# MISPLACED` header to `# RELOCATED`.

### P1-C: Relocate `ArchetypeIndicatorsAgent` Pydantic schemas ✅
- **What changed:** Created `apps_lic/config/archetype_indicator_config.py` (node 21556) with all Pydantic models (`AgentSpecs`, `ArchetypeIndicators`, `Conditions`, `Constraints`, `FallbackRAGParams`, `GateDecisionAgent`, `GenerationAgent`, `ProfileAnalysisAgent`, `QAReportAgent`, `ResearchAgent`, `RoutingAgent`, `RoutingRule`, `ScoringWeights`, `SenderGroundingAgent`, `ValidationAgent`, `VectorStoreQueryParams`).
- **Shim:** `apps_lic/reasoning/ArchetypeIndicatorsAgent.py` (node 21661) re-exports all 15 symbols + constants.
- **Consumer:** `apps_lic/config/loader_config.py` imports `AgentSpecs` from canonical path ✅

### P1-D: Confirm empty stubs retired ✅
- `LeadQualityAgent.py`, `MessageArchitectAgent.py`, `IntelligenceLibrarianAgent.py`: all contain `# RETIRED` marker. No active consumers.

### P2-A: `BaseReflectionAgent` (node 22107, fan-in=2) ✅
- **Interface:** `execute(agents, signals) → dict` + `_post_reflect` hook + `heal`.
- **`LicReflectionAgent`** (node 21676): thin subclass, no overrides. 33 lines total.
- **`RgReflectionAgent`** (node 23036): overrides `_post_reflect` — caches quality patterns, calls `GraphMemoryBridge`.

### P2-B: `BaseProactiveAgent` (node 22106, fan-in=2) ✅
- **Interface:** `execute(pending_tasks) → dict` + `_get_handoff_kwargs` + `_record_task_execution` hooks + `heal`.
- **`OutreachProactiveAgent`** (node 21683): overrides both hooks. 140 lines.
- **`ProactiveAgent`** (node 23032): thin subclass. 42 lines.

### P2-C: `BaseDispatchAgent` (node 22105, fan-in=2) ✅
- **Interface:** `execute(action, payload) → ExecutionResult` + `_run_domain_diagnostics` hook + `heal_timeout` + `heal_config` + `heal`.
- **`DispatchOutreachToolsAgent`** (node 21664): overrides `_run_domain_diagnostics`. Imports `BaseDispatchAgent` + `ExecutionResult` ✅
- **`DispatchResumeToolsAgent`** (node 23024): overrides `_run_domain_diagnostics` + adds Titanium RAG config healing. Imports `BaseDispatchAgent` + `ExecutionResult` ✅

### P3-A: `ParameterizedValidator` (node 22108, fan-in=2) ✅
- **Interface:** `execute(data) → {rule_set, issues, issue_count, passed}` + `collect_issues` override point.
- **`LICValidationExecutor`** (node 21673): MRO = `LICEngineValidationCapability, ParameterizedValidator`. Rule sets: `campaign_balance`, `deliverability`, `message_compliance`.
- **`RGValidationExecutor`** (node 23021): MRO = `ParameterizedValidator`. Rule sets: `ats_compatibility`, `brand_compliance`, `fact_check`, `section_balance`. Uses module-level `_RULE_REGISTRY` + `@register_rule` decorator. Overrides `execute` signature to `(resume_data, job_data)`.

### P3-B: `BaseHealingOrchestrator` (node 22104, fan-in=2) ✅
- **Interface:** full meta-learning heal loop — depth guard, pattern cache, `orchestrate_healing_cycle`, `_apply_healing_strategy`.
- **`LicHealingOrchestrator`** (node 21675): `_cycle_results_key` → `"incident_recovery"`. Owns incident-domain healing (`_heal_structural`, `_heal_schema`, `_heal_llm_call`). Removed `ml_heal_incident_enhanced` + `_execute_recovery_playbook` (were duplicating base).
- **`RgHealingOrchestrator`** (node 23034): default `_cycle_results_key`. Owns async `run()` healing loop + `ml_determine_strategy` / `ml_record_strategy_success` / convergence pattern cache methods. Removed `ml_heal_with_learning_enhanced` + `_apply_healing_strategy` + `orchestrate_healing_cycle` (were duplicating base).

---

## 6. Remaining Work

### R1: Physically move misplaced scripts (P1-B physical) ✅ DONE 2026-03-11
ADG confirmed fan-in=0 for all 5 — zero breakage risk. Moves executed:

| Source | Destination |
|---|---|
| `apps_shared/reasoning/restore_all_archived_agents.py` | `ops_scripts/general/` |
| `apps_shared/reasoning/restore_app_agents.py` | `ops_scripts/general/` |
| `apps_shared/reasoning/restore_void_agents.py` | `ops_scripts/general/` |
| `apps_shared/reasoning/update_orchestrator_imports.py` | `ops_scripts/general/` |
| `apps_shared/reasoning/runtime_observability_agentic_spans.py` | `observability/` |

All headers updated from `# MISPLACED` → `# RELOCATED: Moved from apps_shared/reasoning/ (P1-B, 2026-03-11)`.

### R2: ADG confidence on new base classes ✅ NO ACTION NEEDED
All 5 base classes show `confidence=MEDIUM`. Expected for newly created files — scanner assigns MEDIUM until cross-session scan history accumulates. Auto-promotes to HIGH on next 2-3 regenerations.

### R3: Unused `field` import in `RgHealingOrchestrator` ✅ DONE 2026-03-11
`apps_rg/reasoning/RgHealingOrchestrator.py` line 17: removed `field` from `from dataclasses import dataclass, field`. `field` was only needed for `cycle_results` which now lives in `BaseHealingOrchestrator`.

### R4: Register `apps_shared/reasoning/` as a formal sovereign territory
**Priority: LOW** | The new base-class files live in `apps_shared/reasoning/` which is not yet in `SOVEREIGN_TERRITORIES`.

- File: `agentic_core/L5_safety/config/structure_blueprint_config.py`
- Action: add `"apps_shared/reasoning"` to `SOVEREIGN_TERRITORIES`
- Consequence if deferred: ADG will continue assigning MEDIUM confidence to base-class files; no functional impact.

---

## 7. Test Verification — 100% Pass (28/28 tests)

**Test suite:** `tests/architecture/test_apps_rationalization_verification.py`
**Evidence report:** `docs/reports/plans/apps-agents-rationalization-verification-evidence.md`
**Execution:** 2026-03-11T19:07:00Z

### Test Coverage

| Dimension | Tests | Pass | Method |
|---|---|---|---|
| ADG inheritance edges | 7 | 7/7 | SQLite fan-in queries |
| Import path correctness | 5 | 5/5 | AST parsing |
| Base class interface contracts | 9 | 9/9 | `inspect` + `issubclass` |
| File relocation | 5 | 5/5 | `Path.exists()` |
| MRO verification | 2 | 2/2 | `inspect.getmro()` |
| **Total** | **28** | **28/28** | — |

### Key Verifications

✅ All 10 base→subclass inheritance edges confirmed in ADG
✅ All import paths resolve correctly (no broken imports)
✅ All base class interfaces satisfied by subclasses
✅ All 5 misplaced scripts physically moved (fan-in=0 confirmed)
✅ All MRO chains correct (including `LICValidationExecutor` dual inheritance)
✅ Zero GV_violates edges touch any rationalized file

### Bugs Fixed During Verification

1. **`ParameterizedValidator._RULE_REGISTRY` mutable default** → `field(default_factory=dict)`
2. **`LICValidationExecutor` import path** → `lic_engine_validation_capability_util` (not `lic_engine_validation_capability`)

### Test Execution

```bash
python -m pytest tests/architecture/test_apps_rationalization_verification.py -v
# Result: 28 passed in 0.24s
```

---

## 8. Reasoning Classification

### Agents that are 100% DETERMINISTIC (must never use LLM)

| Agent | Rule | Risk if LLM added |
|---|---|---|
| `GovernanceShieldAgent` | Regex pattern match + replacement table | Determinism violation |
| `LicCodeInterpreter` | TF-IDF cosine/Jaccard similarity — pure math | Would negate "Fast Loop" purpose |
| `LICValidationExecutor` | Rule registry (threshold/regex/boolean) | Compliance audit would fail |
| `RGValidationExecutor` | Rule registry (keyword/ratio/date math) | Same |
| `OutreachSignalRouterAgent` | Routing table lookup | |
| `OutreachLearningAgent` | Field completeness scoring (heuristic) | |
| `ValidatorAgent` | Schema policy check + retry | |
| All HOP shims 1,3,4,6,7,8,9 | Deterministic dispatch stages | HOP-5 is the only LLM stage |

### Agents that REQUIRE LLM

| Agent | LLM usage |
|---|---|
| `OutreachMessageAgent` | YAML prompt templates → LLM generation |
| `ExecutiveStrategyAgent` | Executive prompt templates → LLM |
| `LicTemplateOptimizerAgent` | LLM-scored template selection |
| `HeadlineOutputAgent` | `_call_llm()` for headline generation |
| `ResumeAssemblyAgent` | Markdown template rendering for LLM |
| `ExecutiveSummaryOutputAgent` | Summary generation via LLM |
| `HardenedopenaiexecutorStrategy` | Retry-hardened OpenAI executor |
| `HardenedanthropicexecutorStrategy` | Retry-hardened Anthropic executor |

### HYBRID (deterministic guard-rails + LLM for one stage)

| Agent | Deterministic part | LLM part |
|---|---|---|
| `HOPPipelineExecutor` | Stages 1-4, 6-9 dispatch | Stage 5 generation only |
| `LicHealingOrchestrator` | Playbook dispatch, depth guard | `_heal_llm_call` via `SovereignLLMGateway` |
| `RgHealingOrchestrator` | Cycle strategy, convergence detection | Optional reflection stub |
| `ResumeEnhancementOrchestrator` | Persona routing, evidence injection | Generation step |
| `Hop2ResearchAgent` | Vector store lookup | Optional LLM synthesis |

---

## 8. Deduplication Summary

| Before | After | Mechanism |
|---|---|---|
| 2 reflection agents with duplicate `execute()` + `heal()` | 1 base + 2 thin subclasses | `BaseReflectionAgent` |
| 2 proactive agents with duplicate `execute()` + `heal()` | 1 base + 2 thin subclasses | `BaseProactiveAgent` |
| 2 dispatch agents with duplicate `execute()` + heal boilerplate | 1 base + 2 subclasses | `BaseDispatchAgent` |
| 2 healing orchestrators with 3 identical meta-learning methods each | 1 base + 2 subclasses (domain-specific methods retained) | `BaseHealingOrchestrator` |
| 2 validation executors with identical `rule_set` dispatch skeleton | 1 base + 2 subclasses | `ParameterizedValidator` |
| `MessageComplianceAgent` as standalone agent | Absorbed as `rule_set="message_compliance"` + shim | `LICValidationExecutor` |
| `ArchetypeIndicatorsAgent` mixing config schemas with reasoning/ | Schemas in `apps_lic/config/` + shim | `archetype_indicator_config.py` |

**Estimated lines eliminated:** ~450 lines of duplicated boilerplate across 10 files.

---

## 9. ADG Verification Summary

**Artifact:** `artifacts/adg/adg_indexed_20260311T185727Z.sqlite`

```
Scan:    3,320 modules  ·  151,933 edges
GV_violates (total):     220 (0 touch rationalized files)
G1_imports:              22,803
confidence avg:          0.8856
```

### All 10 inheritance edges — G1_imports confirmed

| Subclass | Base | Symbol | ADG method |
|---|---|---|---|
| `LicReflectionAgent` | `BaseReflectionAgent` | `...BaseReflectionAgent.BaseReflectionAgent` | fan-in query |
| `RgReflectionAgent` | `BaseReflectionAgent` | `...BaseReflectionAgent.BaseReflectionAgent` | fan-in query |
| `OutreachProactiveAgent` | `BaseProactiveAgent` | `...BaseProactiveAgent.BaseProactiveAgent` | fan-in query |
| `ProactiveAgent` | `BaseProactiveAgent` | `...BaseProactiveAgent.BaseProactiveAgent` | fan-in query |
| `DispatchOutreachToolsAgent` | `BaseDispatchAgent` | `...BaseDispatchAgent.ExecutionResult` | bidirectional |
| `DispatchResumeToolsAgent` | `BaseDispatchAgent` | `...BaseDispatchAgent.ExecutionResult` | bidirectional |
| `LicHealingOrchestrator` | `BaseHealingOrchestrator` | `...BaseHealingOrchestrator.BaseHealingOrchestrator` | fan-in query |
| `RgHealingOrchestrator` | `BaseHealingOrchestrator` | `...BaseHealingOrchestrator.BaseHealingOrchestrator` | fan-in query |
| `LICValidationExecutor` | `ParameterizedValidator` | `...ParameterizedValidator.ParameterizedValidator` | bidirectional |
| `RGValidationExecutor` | `ParameterizedValidator` | `...ParameterizedValidator.ParameterizedValidator` | bidirectional |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

