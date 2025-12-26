# OPERATION SOVEREIGN TERRITORY – PHASE 7 APP LAYER AUDIT
**Date:** December 26, 2025  
**Status:** CRITICAL VIOLATIONS DETECTED

---

## EXECUTIVE SUMMARY

### Scope
- **apps_rg/**: Resume Generation Application Layer
- **apps_lic/**: LinkedIn Outreach Application Layer

### Critical Findings

#### 1. ZERO SSOT INTEGRATION ⚠️
**Severity:** CRITICAL  
**Impact:** Complete isolation from purified Core Contracts

- **Finding:** Neither `apps_rg/` nor `apps_lic/` import from `agentic_core.schemas.models.core_contracts`
- **Risk:** Apps are operating with shadow models, creating parallel type systems
- **Evidence:** 0 imports of `RetryPolicy`, `HopSpec`, `GoldenOutput`, or any SSOT models

#### 2. CONTRABAND MODEL PROLIFERATION ⚠️
**Severity:** HIGH  
**Impact:** 50+ local dataclasses with underscore field violations

**apps_rg/ Contraband Models (23 files):**
- `resume_orchestration_config_types_models.py`: WordCountConstraint, CharCountConstraint, ReasoningConfig, ProvenanceRule, ValidationGate (all with `_field` violations)
- `kx_nodes_resume_types.py`: RAGConfig, DecodingParams, ResumeKNode (all with `_field` violations)
- `check_resume_rules_types.py`: ExecutionContext, ProcessingResult
- `resume_planner.py`: resultumeanalysisplan, resultumesectionconfig, resumeprocessessingplan
- `autonomous/context.py`: ResumeEngineContext
- `autonomous/governance.py`: DependencyIssue, DocViolation, PromptIssue, CostPrediction
- `autonomous/intelligence.py`: SecurityIssue, SemanticMatch, RefactorProposal, PhaseResult
- `autonomous/observability.py`: TraceStep, ExecutionTrace, Metric, ValidationIssue, AuditReport
- `autonomous/proactive.py`: ProactiveTask, HandoffRequest, CapabilityProfile
- `autonomous/learning.py`: LearningExample, ConfidenceResult, Instruction, MemoryState
- `autonomous/gitops.py`: FileBackup (truncated)
- `autonomous/healing.py`: CycleResult, HealingResult
- `P1_core/l5_orchestrator/types.py`: OutreachExecutionPhase, OutreachCycleState, OutreachSnapshot
- `P1_core/l5_orchestrator/l5_orchestrator/types.py`: CycleState
- `P1_core/analysis.py`: AnalysisAgent

**apps_lic/ Contraband Models (9 files):**
- `outreach_orchestration_config_models.py`: CharLimitConstraint, WordLimitConstraint, RouteConfig, ArchetypeConfig, ValidationRule (all with `_field` violations)
- `kx_nodes_outreach_types.py`: RAGConfig, DecodingParams, OutreachKNode (all with `_field` violations)
- `check_outreach_rules_types.py`: ExecutionContext, ProcessingResult
- `autonomous/proactive.py`: OutreachProactiveTask, OutreachHandoffRequest, OutreachCapabilityProfile
- `autonomous/observability.py`: OutreachTraceStep, OutreachExecutionTrace, OutreachMetric
- `autonomous/learning.py`: OutreachLearningExample, OutreachInstruction
- `autonomous/healing.py`: OutreachCycleResult, OutreachHealingResult
- `autonomous/context.py`: OutreachBudgetManager
- `P1_core/l5_orchestrator/types.py`: OutreachExecutionPhase, OutreachCycleState, OutreachSnapshot

**Pattern:** Local Runtime DTOs with underscore-prefixed fields (`_min`, `_max`, `_temperature`, `_gate_id`, etc.)

#### 3. CONFIGURATION DECENTRALIZATION ⚠️
**Severity:** MEDIUM  
**Impact:** Hardcoded API keys and environment variable sprawl

**apps_rg/ Configuration Violations (6 files):**
- `P1_core/llm_client_flash.py`: `os.getenv("GOOGLE_API_KEY")` (line 30)
- `P1_core/llm_client.py`: `os.getenv("GOOGLE_API_KEY")`, `os.getenv("LLM_MODEL")` (lines 30, 38)
- `P1_core/connection_manager.py`: Multiple `os.getenv()` calls for Redis, Pinecone, OpenAI (lines 22, 26, 43, 65, 70, 87, 96, 97, 126, 127)
- `engines/resume_engine/autonomous/context.py`: `os.getenv("GEMINI_MODEL")`, `os.getenv("GOOGLE_API_KEY")`, `os.getenv("GEMINI_API_KEY")` (lines 134, 191, 192)
- Hardcoded model pricing: `gpt-4`, `gpt-4o`, `gpt-4o-mini` (lines 36-38)

**apps_lic/ Configuration Violations (1 file):**
- `engines/outreach_engine/autonomous/context.py`: `os.environ.get("GOOGLE_API_KEY")`, `os.environ.get("GEMINI_MODEL")` (lines 104, 107)

#### 4. UNDERSCORE FIELD REFERENCES
**Severity:** LOW (False Positives)  
**Impact:** Mostly legitimate private methods

- **apps_rg/**: 462 matches across 44 files
- **apps_lic/**: 148 matches across 19 files
- **Analysis:** 95%+ are legitimate private methods (`self._perform_analysis`, `self._ctx`, `self.__class__.__name__`)
- **True Violations:** Limited to dataclass field definitions (covered in Finding #2)

---

## REMEDIATION PLAN

### Phase 7A: Contraband Model Triage
**Action:** Tag all local DTOs as `# Local Runtime DTO (Allowed)` or migrate to SSOT

**Decision Matrix:**
1. **App-Specific Models** → Tag as Local DTO, fix underscore fields
   - Resume-specific: `resultumeanalysisplan`, `ResumeEngineContext`
   - Outreach-specific: `OutreachProactiveTask`, `OutreachBudgetManager`
   
2. **Generic Models** → Consider SSOT migration
   - `ExecutionContext`, `ProcessingResult` (duplicated in both apps)
   - `RAGConfig`, `DecodingParams` (duplicated in both apps)
   - `ValidationGate`, `ValidationRule` (duplicated in both apps)

### Phase 7B: Underscore Field Elimination
**Action:** Remove underscore prefixes from all local dataclass fields

**Target Files (Priority):**
1. `apps_rg/engines/resume_engine/resume_orchestration_config_types_models.py`
2. `apps_rg/engines/resume_engine/kx_nodes_resume_types.py`
3. `apps_lic/engines/outreach_engine/outreach_orchestration_config_models.py`
4. `apps_lic/engines/outreach_engine/kx_nodes_outreach_types.py`

### Phase 7C: Configuration Centralization
**Action:** Replace `os.getenv()` with `SovereignConfig` imports

**Target Files:**
1. `apps_rg/P1_core/llm_client.py`
2. `apps_rg/P1_core/llm_client_flash.py`
3. `apps_rg/P1_core/connection_manager.py`
4. `apps_rg/engines/resume_engine/autonomous/context.py`
5. `apps_lic/engines/outreach_engine/autonomous/context.py`

---

## RISK ASSESSMENT

### Immediate Risks
1. **Type Fragmentation:** Apps and Core using incompatible type systems
2. **Drift Acceleration:** No enforcement preventing future underscore field additions
3. **Configuration Sprawl:** API keys scattered across 6+ files

### Long-Term Risks
1. **Maintenance Burden:** Duplicate models require synchronized updates
2. **Testing Complexity:** Cannot use SSOT smoke tests for app layer
3. **Migration Debt:** Growing gap between Core and Apps

---

## NEXT ACTIONS

1. ✅ **Audit Complete** - This document
2. ⏳ **Fix Priority Files** - Eliminate underscore fields in top 4 files
3. ⏳ **Tag Local DTOs** - Mark app-specific models as allowed
4. ⏳ **Centralize Config** - Replace os.getenv with SovereignConfig
5. ⏳ **Smoke Test** - Verify apps_rg/resume_generator.py entry point

**Estimated Effort:** 2-3 hours  
**Blocking Issues:** None  
**Dependencies:** SSOT Phase 6 complete ✅
