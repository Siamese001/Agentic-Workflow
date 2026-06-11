---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\ssot-detailed-implementation-18dfc6.md'
original_relative_path: 'ssot-detailed-implementation-18dfc6.md'
source_sha256: e83dadfe14b125915e989fdba4e322eb3cf8eee0c954192b2b92302dd6480128
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# SSOT Compliance Detailed Implementation Plan

This plan provides specific target files for each sub-phase, breaking down the 1,949 violations into manageable batches with clear refactoring goals.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Phase 0: Discovery & Preparation ()

### 0.1: Baseline Establishment (Day 0 - )
**Target Files**: None (preparation phase)
**Actions**:
- Create git tag `ssot-baseline-{timestamp}`
- Run full test suite and capture results
- Generate dependency map for all violation files

### 0.2: Risk Assessment (Day 0 - )
**Target Files**: Top 50 most imported violation files
**Sample High-Risk Files**:
- `agentic_core/config/SovereignConfigManager.py` (CONFIG)
- `agentic_core/L5_safety/validators/FileClassificationAgent.py` (VALIDATOR)
- `agentic_core/L3_orchestration/OrchestratorAgent.py` (SCRIPT)

### 0.3: Tooling Preparation (Day 1 - )
**Target Files**: Create new tools
- `tools/rename_validator.py` - Batch rename validators
- `tools/rename_config.py` - Batch rename configs
- `tools/validate_imports.py` - Check for broken imports

### 0.4: Stakeholder Alignment (Day 2 - )
**Target Files**: Review plan documents
- Get approval for Phase 1 start

## Phase 1: Critical Infrastructure ()

### 1.1: VALIDATOR - Safety Layer (Day 3)
**Target Files** (20 files):
```
agentic_core/L5_safety/validators/
├── security_controls.py → security_controls_validator.py
├── security_security_controls.py → security_security_controls_validator.py
├── BlueprintSovereign.py → blueprint_sovereign_validator.py
├── chaos_healing_validator.py (already compliant)
├── FileClassificationAgent.py → file_classification_validator.py
├── LocationAgent.py → location_validator.py
├── HierarchyAgent.py → hierarchy_validator.py
├── NamingAgent.py → naming_validator.py
├── StructureAgent.py → structure_validator.py
├── BlueprintSovereignValidator.py → blueprint_sovereign_validator.py
└── ... (10 more validators in L5_safety)
```
**Special Handling**: Update FileClassificationAgent self-references

### 1.2: VALIDATOR - Domain Pilots (Day 4)
**Target Files** (15-20 files, 2-3 per layer):
```
L0_maintenance/
├── deterministic/ATSValidationDeterministic.py → ats_validation_validator.py
L1_cognition/
├── intent_analysis/IntentValidator.py → intent_validator.py
├── meta_learning/MetaLearningValidator.py → meta_learning_validator.py
L2_execution/
├── execution_bridge/ExecutionValidator.py → execution_validator.py
L3_orchestration/
├── workflow_engines/WorkflowValidator.py → workflow_validator.py
L4_state/
├── validation_context/StateValidatorAgent.py → state_validator.py
L5_safety/
├── guardrails/GuardrailValidator.py → guardrail_validator.py
L6_observability/
├── logging/LogValidator.py → log_validator.py
```

### 1.3: VALIDATOR - Batch Processing (Days 5-6)
**Target Files** (Remaining ~300 validators in batches of 30):
```
Batch 1 (Day 5 AM):
- apps_lic/engines/*Validator.py (10 files)
- apps_rg/engines/*Validator.py (10 files)
- apps_shared/common_utils/*Validator.py (10 files)

Batch 2 (Day 5 PM):
- ops_scripts/maintenance/*Validator.py (10 files)
- scripts/maintenance/*Validator.py (5 files)
- tests/*Validator.py (15 files)

Batch 3-6 (Day 6):
- Remaining validators by directory
```

### 1.4: CONFIG - Core Configuration (Day 7)
**Target Files** (50 files):
```
agentic_core/config/
├── config_mixin.py → config_mixin_config.py
├── feature_flags.py → feature_flags_config.py
├── settings.py → settings_config.py
├── SovereignConfigManager.py → sovereign_config_manager_config.py
├── blueprint_sovereign/config_impl.py → config_impl_config.py
├── blueprint_sovereign/Neo4jGraphStore.py → neo4j_graph_store_config.py
├── blueprint_sovereign/RescueReviewer.py → rescue_reviewer_config.py
└── ... (43 more config files)
```

### 1.5: CONFIG - Layer Configuration (Day 8)
**Target Files** (78 files by layer):
```
L0_maintenance/config/ (10 files)
├── BootConfig.py → boot_config.py
├── MaintenanceConfig.py → maintenance_config.py
└── ...

L1_cognition/config/ (12 files)
├── CognitionConfig.py → cognition_config.py
└── ...

L2_execution/config/ (15 files)
├── ExecutionConfig.py → execution_config.py
└── ...

L3_orchestration/config/ (13 files)
├── OrchestrationConfig.py → orchestration_config.py
└── ...

L4_state/config/ (10 files)
├── StateConfig.py → state_config.py
└── ...

L5_safety/config/ (10 files)
├── SafetyConfig.py → safety_config.py
└── ...

L6_observability/config/ (8 files)
├── ObservabilityConfig.py → observability_config.py
└── ...
```

## Phase 2: Type System Foundation ()

### 2.1: Core Types (Day 9)
**Target Files** (50 most imported types):
```
agentic_core/config/
├── EmbeddingConfig.py → embedding_types.py
├── ModelConfig.py → model_types.py
├── ProviderConfig.py → provider_types.py

agentic_core/domain/
├── BaseEntity.py → base_entity_types.py
├── DomainEntity.py → domain_entity_types.py
├── EntityTypes.py → entity_types.py

agentic_core/L1_cognition/thought_engine/
├── CognitiveCapability.py → cognitive_capability_types.py
├── ExecutionStatus.py → execution_status_types.py
├── IdentityType.py → identity_types.py
├── MissionStatus.py → mission_status_types.py
└── ... (40 more)
```

### 2.2: Domain Types (Day 10)
**Target Files** (200 types by domain):
```
L0_maintenance/ (30 types)
├── BootSequence.py → boot_sequence_types.py
├── Colors.py → colors_types.py
└── ...

L1_cognition/ (40 types)
├── BudgetAgent.py → budget_agent_types.py
├── OrchestratorConfig.py → orchestrator_config_types.py
└── ...

L2_execution/ (50 types)
├── ActionCapability.py → action_capability_types.py
├── BaseToolAgent.py → base_tool_agent_types.py
├── BulletFormat.py → bullet_format_types.py
└── ...

L3_orchestration/ (30 types)
├── HopStatus.py → hop_status_types.py
├── PermissionScope.py → permission_scope_types.py
└── ...

L4_state/ (25 types)
├── ContextPriority.py → context_priority_types.py
├── GravityViolation.py → gravity_violation_types.py
└── ...

L5_safety/ (25 types)
├── AgentInfo.py → agent_info_types.py
└── ...
```

### 2.3: Remaining Types (Day 11)
**Target Files** (179 remaining types):
```
apps_lic/ (50 types)
apps_rg/ (50 types)
apps_shared/ (30 types)
ops_scripts/ (20 types)
tests/ (29 types)
```

## Phase 3: Test Organization ()

### 3.1: Critical Tests (Day 12)
**Target Files** (100 critical test files):
```
Root level tests:
├── simple_verify_patch.py → test_simple_verify_patch.py
├── test_execute_ssot_e2e.py (already compliant)
├── test_heal_implementations.py → test_heal_implementations.py (already compliant)
└── ...

Critical test directories:
├── tests/test_audit_pipeline.py → test_audit_pipeline.py (already compliant)
├── tests/test_discovery_compliance.py → test_discovery_compliance.py (already compliant)
├── tests/test_meta_learning.py → test_meta_learning.py (already compliant)
└── ...
```

### 3.2: Remaining Tests (Day 13)
**Target Files** (179 remaining test files):
```
By directory:
- tests/e2e/ (50 files)
- tests/integration/ (40 files)
- tests/unit/ (89 files)
```

## Phase 4: Strategy Pattern ()

### 4.1: Core Strategies (Day 14)
**Target Files** (50 core strategies):
```
agentic_core/domain/
├── LegacyArtifacts.py → LegacyArtifactsStrategy.py

agentic_core/L0_maintenance/scripts/
├── deep_wiki_healing_strategy.py → DeepWikiHealingStrategy.py
├── git_kraken_healing_strategy.py → GitKrakenHealingStrategy.py
├── knowledge_graph_healing_strategy.py → KnowledgeGraphHealingStrategy.py
├── l6_audit_healing_strategy.py → L6AuditHealingStrategy.py
├── sovereign_healing_engine.py → SovereignHealingStrategy.py
└── ... (44 more)

agentic_core/L1_cognition/thought_engine/
├── ReasoningCache.py → ReasoningCacheStrategy.py
└── ...
```

### 4.2: Domain Strategies (Day 15)
**Target Files** (96 remaining strategies):
```
L2_execution/tool_registry/ (30 strategies)
L3_orchestration/workflow_engines/ (25 strategies)
L4_state/validation_context/ (20 strategies)
L5_safety/guardrails/ (21 strategies)
```

## Phase 5: Script Consolidation ()

### 5.1: Critical Scripts (Day 16)
**Target Files** (50 critical scripts):
```
Root level critical scripts:
├── AgentTechnicalStatus.py → agent_technical_status.py (move to ops_scripts/)
├── NuclearAuditAgent.py → nuclear_audit_agent.py (move to ops_scripts/)
├── execute_sovereignty.bat → execute_sovereignty.bat (keep as is)
├── run_guardian.bat → run_guardian.bat (keep as is)
└── ...

CI/CD related:
├── .github/workflows/*.yml (update script references)
```

### 5.2: Operational Scripts (Day 17)
**Target Files** (Verify compliance in ops_scripts/ and scripts/):
```
ops_scripts/ (95 files - all already compliant)
├── agent_disposition_analyzer.py ✓
├── aggressive_dedup.py ✓
└── ...

scripts/ (7 files - all already compliant)
├── find_hangs.py ✓
├── fix_naming_issues.py ✓
└── ...
```

### 5.3: Root-Level Scripts (Day 18)
**Target Files** (448 remaining root-level scripts):
```
Batch 1 (AM - 100 files):
├── add_heal_methods_batch.py → add_heal_methods_batch.py
├── add_heal_strategy.py → add_heal_strategy.py
├── implement_phase1_renames.py → implement_phase1_renames.py
└── ... (97 more)

Batch 2 (PM - 100 files):
├── test_always_heal_llm.py → test_always_heal_llm.py
├── test_healing_confidence.py → test_healing_confidence.py
└── ... (98 more)

Batch 3-5 (Remaining 248 files):
- Process in batches of 80-85
- Decide placement: scripts/ vs ops_scripts/ based on function
```

## Detailed File Movement Rules

### SCRIPT Placement Decision Tree:
1. **Operational/Maintenance scripts** → `ops_scripts/`
2. **Development/Utility scripts** → `scripts/`
3. **One-off analysis scripts** → `ops_scripts/`
4. **Build/CI scripts** → Keep at root or move to `scripts/`

### Import Update Strategy:
1. After each batch, run import update script
2. Update imports in:
   - Python files
   - Configuration files
   - Documentation
   - CI/CD pipelines

## Validation Checklist Per Batch

### Pre-Batch:
- [ ] Test suite passing
- [ ] Git branch created
- [ ] Rollback script ready

### Post-Batch:
- [ ] All files renamed correctly
- [ ] No broken imports
- [ ] Tests still passing
- [ ] No performance impact
- [ ] Documentation updated

## Risk Mitigation Per Phase

### Phase 1 (VALIDATOR/CONFIG):
- High risk: These affect system validation
- Mitigation: Process in small batches, validate after each

### Phase 2 (TYPES):
- Medium risk: Type definitions
- Mitigation: Update type exports, check mypy

### Phase 3 (TESTS):
- Low risk: Test naming only
- Mitigation: Ensure test discovery still works

### Phase 4 (ADAPTER/Strategy):
- High risk: Architectural pattern
- Mitigation: Verify strategy pattern compliance

### Phase 5 (SCRIPTS):
- Medium risk: Many files, low complexity
- Mitigation: Batch processing, update references

## Success Metrics

### Per Phase:
- 0 violations for target categories
- 100% test pass rate
- 0 broken imports
- All references updated

### Overall:
- 1,949 violations → 0 violations
- 67.99% → 100% compliance rate
- System fully functional

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

