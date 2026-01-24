# 🛡️ RG SOVEREIGN STRUCTURAL AUDIT REPORT

**Version:** 2.5-RG
**Audit Date:** 2026-01-23
**Auditor:** Principal AI Systems Auditor (AST-Enforced)
**Target Directory:** `apps_rg/`

---

## 1. Executive Structural Summary

### 📊 High-Level Health Check

| Metric | Value | Status |
|:-------|:------|:-------|
| **Total .py Files Scanned** | 81 | — |
| **True Sovereign Engines** | 21 | ✅ |
| **Stateless Tools** | 18 | ⚠️ Misplaced |
| **Passive Data Types** | 16 | ⚠️ Misnamed |
| **Legacy/Archive** | 3 | 🗑️ |
| **Unknown (Review Required)** | 23 | ❌ |
| **Parse Errors** | 10 | ❌ Critical |

### 🎯 Sovereign Alignment Score: **25.9%**

> **Critical Assessment:** Only ~26% of files in `apps_rg/engines/` are true Sovereign Agents. The remaining 74% are misclassified tools, types, or legacy code that violates the V2.5 architecture standard.

### 🚨 Critical Risks

1. **Structural Contamination:** 18 stateless tools sitting in `engines/` violate State/Engine separation
2. **Nomenclature Violations:** 16 files named `*Agent.py` are actually passive data types (Enums/BaseModels)
3. **Parse Errors:** 10 files have syntax errors preventing AST analysis - immediate remediation required
4. **No External Namespace Violations:** ✅ No `apps_lic` imports detected (namespace purity maintained)

---

## 2. The "UNKNOWN" Ledger (Gap Analysis)

Files in `engines/` that don't belong there based on AST structural analysis:

| File Path | Detected Class/Logic | Reason for "Unknown" Status | Proposed Action |
|:----------|:---------------------|:---------------------------|:----------------|
| `engines/adjust_section_weights.py` | `AdjustSectionWeights` class | Class without recognized stateful methods | Move to `shared/tools/` |
| `engines/apply_clerk_extraction.py` | `ClerkExtractor` class | Class without recognized stateful methods | Move to `shared/tools/` |
| `engines/apply_data_enrichment.py` | `DataEnricher` class | Class without recognized stateful methods | Move to `shared/tools/` |
| `engines/check_hallucination.py` | `HallucinationDetector` class | Class without recognized stateful methods | Move to `shared/tools/` |
| `engines/enhancement_integration.py` | `ResumeEnhancementOrchestrator` class | Class without recognized stateful methods | Move to `shared/tools/` |
| `engines/EvaluateResumeEffectiveness.py` | `EvaluateResumeEffectiveness` class | Class without recognized stateful methods | Move to `shared/tools/` |
| `engines/fetch_user_preferences.py` | `fetch_user_preferences` class | Class without recognized stateful methods | Move to `shared/tools/` |
| `engines/information_prepare_resume_context.py` | `PrepareResumeContext` class | Class without recognized stateful methods | Move to `shared/tools/` |
| `engines/InspectResumeQuality.py` | `InspectResumeQuality` class | Class without recognized stateful methods | Move to `shared/tools/` |
| `engines/optimize_content_order.py` | `OptimizeContentOrder` class | Class without recognized stateful methods | Move to `shared/tools/` |
| `engines/query_past_generations.py` | `query_past_generations` class | Class without recognized stateful methods | Move to `shared/tools/` |
| `engines/RefineResumeRanking.py` | `RefineResumeRanking` class | Class without recognized stateful methods | Move to `shared/tools/` |
| `engines/request_retrieve_resume_history.py` | `RetrieveResumeHistory` class | Class without recognized stateful methods | Move to `shared/tools/` |

### 🔴 Parse Error Files (Require Immediate Fix)

| File Path | Error | Proposed Action |
|:----------|:------|:----------------|
| `engines/BulletAgent.py` | `unexpected indent (line 7)` | Fix syntax, then reclassify |
| `engines/ConvergenceDetectorAgent.py` | `unexpected indent (line 12)` | Fix syntax, then reclassify |
| `engines/DispatchResumeTools.py` | `unindent does not match (line 20)` | Fix syntax, then reclassify |
| `engines/DraftingAgent.py` | `unexpected indent (line 5)` | Fix syntax, then reclassify |
| `engines/HardenedOrchestrator.py` | `unexpected indent (line 17)` | Fix syntax, then reclassify |
| `engines/k25_research_agent.py` | `unexpected indent (line 3)` | Fix syntax, then reclassify |
| `engines/run_dashboard_pipeline.py` | `unexpected indent (line 24)` | Fix syntax, then reclassify |
| `engines/TestSsotRglobElimination.py` | `unindent does not match (line 57)` | Fix syntax, move to `legacy/` |
| `engines/TitaniumAwareAgent.py` | `unexpected indent (line 10)` | Fix syntax, then reclassify |
| `engines/UtilitiesOrganizeAllFiles.py` | `unexpected indent (line 11)` | Fix syntax, then reclassify |

---

## 3. Nomenclature & Type Enforcement (Imposter Agents)

### 🎭 The "Passive Eviction" List

Files named `*Agent.py` that are actually passive data structures (Enums, BaseModels, TypedDicts):

| Current Path | Detected Type | Target Path | Rationale |
|:-------------|:--------------|:------------|:----------|
| `engines/CapabilityMonitorAgent.py` | Enum (`TaskPriority`, `HandoffReason`) | `domain/types/capability_monitor_types.py` | Contains Enum definitions, not active reasoning |
| `engines/ResumeLearningAgent.py` | Enum (`ConfidenceLevel`) | `domain/types/resume_learning_types.py` | Primary structure is Enum-based |
| `engines/SignalRouterAgent.py` | Enum (`HealingStrategy`) | `domain/types/signal_router_types.py` | Contains Enum definitions |
| `engines/StrictDocEnforcerAgent.py` | Enum (`DependencyStatus`, `DocComplianceLevel`, `PromptRisk`) | `domain/types/strict_doc_enforcer_types.py` | Multiple Enum definitions |
| `engines/PersonaRouter.py` | Enum (`ArchetypeBase`) + BaseModel | `domain/types/persona_router_types.py` | Inherits from str, Enum, BaseModel |
| `engines/EvidenceInjector.py` | Enum (`EvidenceType`) + BaseModel | `domain/types/evidence_injector_types.py` | Inherits from str, Enum, BaseModel |
| `engines/SubatomicOrchestrator.py` | Enum (`WorkflowType`) | `domain/types/subatomic_orchestrator_types.py` | Contains Enum definitions |

### 📋 Additional Type Files (Non-Agent Named)

| Current Path | Detected Type | Target Path |
|:-------------|:--------------|:------------|
| `engines/diff_generator.py` | Enum (`DiffFormat`) + BaseModel | `domain/types/diff_types.py` |
| `engines/kx_nodes_outreach_types.py` | Enum (`OutreachKNodeType`, `ReasoningStrategy`) | `domain/types/kx_outreach_types.py` |
| `engines/kx_nodes_resume_types.py` | Enum (`ResumeKNodeType`, `ReasoningStrategy`) | `domain/types/kx_resume_types.py` |
| `engines/orchestrate_workflow.py` | Enum (`HopStatus`, `GateDecision`) | `domain/types/workflow_types.py` |
| `engines/resume_orchestration_config.py` | Enum (`RAGType`, `ClaimVerificationMode`, `ValidationSeverity`) | `domain/types/orchestration_config_types.py` |
| `engines/rg_creative_brief.py` | Enum (`VoiceType`, `ProvenanceStrategy`) | `domain/types/creative_brief_types.py` |
| `engines/rg_provenance_tracker.py` | Enum (`ProvenanceType`, `BulletCategory`) | `domain/types/provenance_types.py` |
| `engines/rg_validation_gates.py` | Enum (`GateDecision`, `GateSeverity`) | `domain/types/validation_gate_types.py` |
| `engines/security_utilities.py` | Enum (`SecurityStatus`) | `domain/types/security_types.py` |

> **Sovereignty Principle:** Anything named "Agent" must be an active, reasoning entity with stateful methods (`execute`, `process`, `run`), not a static type definition.

---

## 4. Dependency & Import Impact Map

### 📈 High-Traffic Modules

Based on AST import analysis, **no files in `apps_rg/engines/` are imported by more than 5 other files within the directory**. This indicates:
- Low internal coupling (good for migration)
- Most dependencies are external to `apps_rg/`

| File | Dependency Count | Imported By |
|:-----|:-----------------|:------------|
| All files | 0 | — |

> **Assessment:** The `apps_rg/engines/` directory has minimal internal cross-dependencies, making Phase 2 migration low-risk.

### 🔒 External Namespace Violations

| Violation Type | Count | Files |
|:---------------|:------|:------|
| `apps_lic` imports | **0** | ✅ None detected |
| `apps_shared` imports | N/A | Expected (shared utilities) |

> **Namespace Purity:** ✅ PASSED - No cross-domain imports detected.

### ⚠️ Hardcoded Path Risks

Files with potential hardcoded paths that may break during migration:

| File | Import Pattern | Risk Level |
|:-----|:---------------|:-----------|
| `DispatchResumeToolsAgent.py` | `titanium_rag_pipeline` | Medium |
| `ResumeGenerator.py` | `runtime.shared.multi_provider_clients` | Medium |
| `SubatomicOrchestrator.py` | `runtime.core.dynamic_dag_manager`, `runtime.core.SubatomicHop` | Medium |
| `RgResumeOrchestratorAgent.py` | `shared.configuration.config` | Low |

---

## 5. The Migration Manifest (JSON Block)

```json
{
  "version": "2.5-RG",
  "audit_date": "2026-01-23",
  "summary": {
    "total_files": 81,
    "engines": 21,
    "tools": 18,
    "types": 16,
    "legacy": 3,
    "unknown": 23,
    "parse_errors": 10,
    "sovereign_alignment_score": 25.9
  },
  "actions": {
    "move_to_engines": [
      "apps_rg/engines/ATSCompatibilityAgent.py",
      "apps_rg/engines/BrandComplianceAgent.py",
      "apps_rg/engines/ContentQualityAgent.py",
      "apps_rg/engines/DispatchResumeToolsAgent.py",
      "apps_rg/engines/FactCheckAgent.py",
      "apps_rg/engines/InvokeGenerationService.py",
      "apps_rg/engines/ProactiveAgent.py",
      "apps_rg/engines/RankResumeSections.py",
      "apps_rg/engines/ResumeAgent.py",
      "apps_rg/engines/ResumeGenerator.py",
      "apps_rg/engines/RgHealingOrchestratorAgent.py",
      "apps_rg/engines/RgReflectionAgent.py",
      "apps_rg/engines/RgResumeOrchestratorAgent.py",
      "apps_rg/engines/RgStrategicPlannerAgent.py",
      "apps_rg/engines/RgTemplateOptimizerAgent.py",
      "apps_rg/engines/SectionBalanceAgent.py",
      "apps_rg/engines/create_experience_bullets.py",
      "apps_rg/engines/execute_message_generation.py",
      "apps_rg/engines/execute_resume_generation.py",
      "apps_rg/engines/orchestrate_resume.py",
      "apps_rg/engines/rg_contact_research_executor.py"
    ],
    "move_to_tools": [
      "apps_rg/engines/GapClosureArchitectAgent.py",
      "apps_rg/engines/achv_models.py",
      "apps_rg/engines/assess_cognition_relevance.py",
      "apps_rg/engines/build_search_filters.py",
      "apps_rg/engines/calibrate_fit_score.py",
      "apps_rg/engines/compute_skill_similarity.py",
      "apps_rg/engines/compute_word_count.py",
      "apps_rg/engines/diagnose_generation_issues.py",
      "apps_rg/engines/evaluate_writing_quality.py",
      "apps_rg/engines/match_job_patterns.py",
      "apps_rg/engines/normalize_skill_scores.py",
      "apps_rg/engines/optimization_strategies.py",
      "apps_rg/engines/order_skills_by_relevance.py",
      "apps_rg/engines/prioritize_achievements.py",
      "apps_rg/engines/resume_planner.py",
      "apps_rg/engines/section_scope_integrator_engine.py",
      "apps_rg/engines/void_compliance.py",
      "apps_rg/engines/weight_experience_match.py"
    ],
    "move_to_domain_types": {
      "apps_rg/engines/CapabilityMonitorAgent.py": "capability_monitor_types.py",
      "apps_rg/engines/diff_generator.py": "diff_types.py",
      "apps_rg/engines/EvidenceInjector.py": "evidence_injector_types.py",
      "apps_rg/engines/kx_nodes_outreach_types.py": "kx_outreach_types.py",
      "apps_rg/engines/kx_nodes_resume_types.py": "kx_resume_types.py",
      "apps_rg/engines/orchestrate_workflow.py": "workflow_types.py",
      "apps_rg/engines/PersonaRouter.py": "persona_router_types.py",
      "apps_rg/engines/ResumeLearningAgent.py": "resume_learning_types.py",
      "apps_rg/engines/resume_orchestration_config.py": "orchestration_config_types.py",
      "apps_rg/engines/rg_creative_brief.py": "creative_brief_types.py",
      "apps_rg/engines/rg_provenance_tracker.py": "provenance_types.py",
      "apps_rg/engines/rg_validation_gates.py": "validation_gate_types.py",
      "apps_rg/engines/security_utilities.py": "security_types.py",
      "apps_rg/engines/SignalRouterAgent.py": "signal_router_types.py",
      "apps_rg/engines/StrictDocEnforcerAgent.py": "strict_doc_enforcer_types.py",
      "apps_rg/engines/SubatomicOrchestrator.py": "subatomic_orchestrator_types.py"
    },
    "archive_legacy": [
      "apps_rg/engines/test_dashboard.py",
      "apps_rg/engines/test_large_node.py",
      "apps_rg/engines/test_ssot_enforcement.py"
    ],
    "fix_syntax_errors": [
      "apps_rg/engines/BulletAgent.py",
      "apps_rg/engines/ConvergenceDetectorAgent.py",
      "apps_rg/engines/DispatchResumeTools.py",
      "apps_rg/engines/DraftingAgent.py",
      "apps_rg/engines/HardenedOrchestrator.py",
      "apps_rg/engines/k25_research_agent.py",
      "apps_rg/engines/run_dashboard_pipeline.py",
      "apps_rg/engines/TestSsotRglobElimination.py",
      "apps_rg/engines/TitaniumAwareAgent.py",
      "apps_rg/engines/UtilitiesOrganizeAllFiles.py"
    ],
    "unknown_require_manual_review": [
      "apps_rg/engines/adjust_section_weights.py",
      "apps_rg/engines/apply_clerk_extraction.py",
      "apps_rg/engines/apply_data_enrichment.py",
      "apps_rg/engines/check_hallucination.py",
      "apps_rg/engines/enhancement_integration.py",
      "apps_rg/engines/EvaluateResumeEffectiveness.py",
      "apps_rg/engines/fetch_user_preferences.py",
      "apps_rg/engines/information_prepare_resume_context.py",
      "apps_rg/engines/InspectResumeQuality.py",
      "apps_rg/engines/optimize_content_order.py",
      "apps_rg/engines/query_past_generations.py",
      "apps_rg/engines/RefineResumeRanking.py",
      "apps_rg/engines/request_retrieve_resume_history.py"
    ]
  }
}
```

---

## 6. Import Update Patterns for Phase 2

Since all files have **0 internal dependencies**, no `sed` or regex patterns are required for internal import updates.

However, for **external consumers** of `apps_rg/engines/`, the following patterns should be applied after migration:

### Tools Migration Pattern
```bash
# For files moving from engines/ to shared/tools/
sed -i 's/from apps_rg\.engines\.\(achv_models\|assess_cognition_relevance\|build_search_filters\|calibrate_fit_score\|compute_skill_similarity\|compute_word_count\|diagnose_generation_issues\|evaluate_writing_quality\|match_job_patterns\|normalize_skill_scores\|optimization_strategies\|order_skills_by_relevance\|prioritize_achievements\|resume_planner\|section_scope_integrator_engine\|void_compliance\|weight_experience_match\)/from apps_rg.shared.tools.\1/g' **/*.py
```

### Types Migration Pattern
```bash
# For files moving from engines/ to domain/types/
sed -i 's/from apps_rg\.engines\.CapabilityMonitorAgent/from apps_rg.domain.types.capability_monitor_types/g' **/*.py
sed -i 's/from apps_rg\.engines\.diff_generator/from apps_rg.domain.types.diff_types/g' **/*.py
sed -i 's/from apps_rg\.engines\.EvidenceInjector/from apps_rg.domain.types.evidence_injector_types/g' **/*.py
sed -i 's/from apps_rg\.engines\.PersonaRouter/from apps_rg.domain.types.persona_router_types/g' **/*.py
sed -i 's/from apps_rg\.engines\.ResumeLearningAgent/from apps_rg.domain.types.resume_learning_types/g' **/*.py
sed -i 's/from apps_rg\.engines\.SignalRouterAgent/from apps_rg.domain.types.signal_router_types/g' **/*.py
sed -i 's/from apps_rg\.engines\.StrictDocEnforcerAgent/from apps_rg.domain.types.strict_doc_enforcer_types/g' **/*.py
sed -i 's/from apps_rg\.engines\.SubatomicOrchestrator/from apps_rg.domain.types.subatomic_orchestrator_types/g' **/*.py
```

---

## 7. True Sovereign Engines (Validated)

The following 21 files are **confirmed True Sovereign Agents** with proper stateful methods:

| File | Class | Stateful Methods | Inheritance |
|:-----|:------|:-----------------|:------------|
| `ATSCompatibilityAgent.py` | `ATSCompatibilityAgent` | `execute`, `heal_repository` | HealerMixin, MCPHardenedMixin, SubatomicTestingMixin, ResumeAgent |
| `BrandComplianceAgent.py` | `BrandComplianceAgent` | `execute`, `heal_repository` | SubatomicTestingMixin, ResumeAgent, MCPHardenedMixin |
| `ContentQualityAgent.py` | `ContentQualityAgent` | `execute`, `heal_repository` | SubatomicTestingMixin, ResumeAgent, MCPHardenedMixin |
| `DispatchResumeToolsAgent.py` | `DispatchResumeToolsAgent` | `execute`, `heal_repository` | HealerMixin, MCPHardenedMixin |
| `FactCheckAgent.py` | `FactCheckAgent` | `execute`, `heal_repository` | SubatomicTestingMixin, ResumeAgent, MCPHardenedMixin |
| `InvokeGenerationService.py` | `InvokeGenerationService` | `execute` | — |
| `ProactiveAgent.py` | `ProactiveAgent` | `execute`, `heal_repository` | SubatomicTestingMixin, ResumeAgent, MCPHardenedMixin |
| `RankResumeSections.py` | `RankResumeSections` | `process` | — |
| `ResumeAgent.py` | `ResumeAgent` | `execute`, `heal_repository` | MCPHardenedMixin, HealerMixin, SubatomicTestingMixin, ABC |
| `ResumeGenerator.py` | `ResumeGenerator` | `generate` | — |
| `RgHealingOrchestratorAgent.py` | `RgHealingOrchestratorAgent` | `run`, `heal_repository` | MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin |
| `RgReflectionAgent.py` | `RgReflectionAgent` | `execute`, `heal_repository` | SubatomicTestingMixin, ResumeAgent, MCPHardenedMixin |
| `RgResumeOrchestratorAgent.py` | `RgResumeOrchestratorAgent` | `run`, `heal_repository` | MCPHardenedMixin, SubatomicTestingMixin, HealerMixin |
| `RgStrategicPlannerAgent.py` | `RgStrategicPlannerAgent` | `execute`, `heal_repository` | SubatomicTestingMixin, ResumeAgent, MCPHardenedMixin |
| `RgTemplateOptimizerAgent.py` | `RgTemplateOptimizerAgent` | `execute`, `heal_repository` | SubatomicTestingMixin, ResumeAgent, MCPHardenedMixin |
| `SectionBalanceAgent.py` | `SectionBalanceAgent` | `execute`, `heal_repository` | SubatomicTestingMixin, ResumeAgent, MCPHardenedMixin |
| `create_experience_bullets.py` | `CreateExperienceBullets` | `execute` | — |
| `execute_message_generation.py` | `execute_message_generation` | `execute` | — |
| `execute_resume_generation.py` | `execute_resume_generation` | `execute` | — |
| `orchestrate_resume.py` | `ResumeOrchestrator` | `run` | — |
| `rg_contact_research_executor.py` | `SafetyExecutor` | `execute_safety` | — |

---

## 8. Recommended Phase 2 Execution Order

1. **Priority 1 - Fix Syntax Errors** (10 files)
   - These files cannot be properly classified until syntax is fixed

2. **Priority 2 - Archive Legacy** (3 files)
   - Move `test_*.py` files to `apps_rg/legacy/`

3. **Priority 3 - Migrate Types** (16 files)
   - Create `apps_rg/domain/types/` directory
   - Move and rename Enum/BaseModel files

4. **Priority 4 - Migrate Tools** (18 files)
   - Create `apps_rg/shared/tools/` directory
   - Move stateless utility files

5. **Priority 5 - Manual Review** (13 files)
   - Review "unknown" files for proper classification
   - Add stateful methods or reclassify as tools

---

## 9. Appendix: Full File Classification

### A. Engines (21 files) ✅
```
apps_rg/engines/ATSCompatibilityAgent.py
apps_rg/engines/BrandComplianceAgent.py
apps_rg/engines/ContentQualityAgent.py
apps_rg/engines/DispatchResumeToolsAgent.py
apps_rg/engines/FactCheckAgent.py
apps_rg/engines/InvokeGenerationService.py
apps_rg/engines/ProactiveAgent.py
apps_rg/engines/RankResumeSections.py
apps_rg/engines/ResumeAgent.py
apps_rg/engines/ResumeGenerator.py
apps_rg/engines/RgHealingOrchestratorAgent.py
apps_rg/engines/RgReflectionAgent.py
apps_rg/engines/RgResumeOrchestratorAgent.py
apps_rg/engines/RgStrategicPlannerAgent.py
apps_rg/engines/RgTemplateOptimizerAgent.py
apps_rg/engines/SectionBalanceAgent.py
apps_rg/engines/create_experience_bullets.py
apps_rg/engines/execute_message_generation.py
apps_rg/engines/execute_resume_generation.py
apps_rg/engines/orchestrate_resume.py
apps_rg/engines/rg_contact_research_executor.py
```

### B. Tools (18 files) ⚠️
```
apps_rg/engines/GapClosureArchitectAgent.py
apps_rg/engines/achv_models.py
apps_rg/engines/assess_cognition_relevance.py
apps_rg/engines/build_search_filters.py
apps_rg/engines/calibrate_fit_score.py
apps_rg/engines/compute_skill_similarity.py
apps_rg/engines/compute_word_count.py
apps_rg/engines/diagnose_generation_issues.py
apps_rg/engines/evaluate_writing_quality.py
apps_rg/engines/match_job_patterns.py
apps_rg/engines/normalize_skill_scores.py
apps_rg/engines/optimization_strategies.py
apps_rg/engines/order_skills_by_relevance.py
apps_rg/engines/prioritize_achievements.py
apps_rg/engines/resume_planner.py
apps_rg/engines/section_scope_integrator_engine.py
apps_rg/engines/void_compliance.py
apps_rg/engines/weight_experience_match.py
```

### C. Types (16 files) ⚠️
```
apps_rg/engines/CapabilityMonitorAgent.py
apps_rg/engines/diff_generator.py
apps_rg/engines/EvidenceInjector.py
apps_rg/engines/kx_nodes_outreach_types.py
apps_rg/engines/kx_nodes_resume_types.py
apps_rg/engines/orchestrate_workflow.py
apps_rg/engines/PersonaRouter.py
apps_rg/engines/ResumeLearningAgent.py
apps_rg/engines/resume_orchestration_config.py
apps_rg/engines/rg_creative_brief.py
apps_rg/engines/rg_provenance_tracker.py
apps_rg/engines/rg_validation_gates.py
apps_rg/engines/security_utilities.py
apps_rg/engines/SignalRouterAgent.py
apps_rg/engines/StrictDocEnforcerAgent.py
apps_rg/engines/SubatomicOrchestrator.py
```

### D. Legacy (3 files) 🗑️
```
apps_rg/engines/test_dashboard.py
apps_rg/engines/test_large_node.py
apps_rg/engines/test_ssot_enforcement.py
```

### E. Parse Errors (10 files) ❌
```
apps_rg/engines/BulletAgent.py
apps_rg/engines/ConvergenceDetectorAgent.py
apps_rg/engines/DispatchResumeTools.py
apps_rg/engines/DraftingAgent.py
apps_rg/engines/HardenedOrchestrator.py
apps_rg/engines/k25_research_agent.py
apps_rg/engines/run_dashboard_pipeline.py
apps_rg/engines/TestSsotRglobElimination.py
apps_rg/engines/TitaniumAwareAgent.py
apps_rg/engines/UtilitiesOrganizeAllFiles.py
```

### F. Unknown (13 files) ❓
```
apps_rg/engines/adjust_section_weights.py
apps_rg/engines/apply_clerk_extraction.py
apps_rg/engines/apply_data_enrichment.py
apps_rg/engines/check_hallucination.py
apps_rg/engines/enhancement_integration.py
apps_rg/engines/EvaluateResumeEffectiveness.py
apps_rg/engines/fetch_user_preferences.py
apps_rg/engines/information_prepare_resume_context.py
apps_rg/engines/InspectResumeQuality.py
apps_rg/engines/optimize_content_order.py
apps_rg/engines/query_past_generations.py
apps_rg/engines/RefineResumeRanking.py
apps_rg/engines/request_retrieve_resume_history.py
```

---

**Report Generated:** 2026-01-23
**Next Phase:** Phase 2 - Automated Migration Execution
**Blocking Issues:** 10 files with syntax errors must be fixed before migration
