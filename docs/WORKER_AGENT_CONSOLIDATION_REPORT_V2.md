# Worker Agent Consolidation Opportunity Report V2

**Date:** January 19, 2026  
**Current Agent Count:** 270  
**Target After Consolidation:** ~180-200 agents (25-33% reduction)

---

## Executive Summary

This report identifies **12 consolidation opportunities** across the 270-agent codebase that could reduce agent count by 70-90 agents while improving maintainability, reducing code duplication, and standardizing patterns.

### Key Findings

| Pattern | Current Count | Proposed Unified | Reduction |
|---------|---------------|------------------|-----------|
| Orchestrators | 20 | 4 | -16 |
| Validators | 18 | 3 | -15 |
| Managers | 12 | 4 | -8 |
| Enforcers | 11 | 2 | -9 |
| Detectors | 11 | 2 | -9 |
| Healers | 8 | 2 | -6 |
| Routers | 7 | 2 | -5 |
| Executors | 5 | 2 | -3 |
| **Total** | **92** | **21** | **-71** |

---

## Phase 1: Orchestrator Consolidation (Priority: HIGH)

### Current State: 20 Orchestrators

**L3 Layer (10 agents):**
- `CachedOrchestratorAgent`
- `ConsolidatedOrchestratorAgent`
- `HardenedWorkflowOrchestratorAgent`
- `IntelligentOrchestratorAgent`
- `OrchestratorAgentAndScopeManagerAgent`
- `ScriptsPlanningOrchestratorAgent`
- `SelfRecoveringOrchestratorAgent`
- `SovereignRagOrchestratorAgent`
- `SovereignRedisOrchestratorAgent`
- `UnifiedOrchestratorAgent`

**Apps Layer (10 agents):**
- `HOPOrchestratorAgent`
- `LicHealingOrchestratorAgent`
- `LicWorkflowOrchestratorAgent`
- `OutreachPhase5OrchestratorAgent`
- `Phase4OrchestratorAgent`
- `Phase6OrchestratorAgent`
- `Phase7OrchestratorAgent`
- `RgHealingOrchestratorAgent`
- `RgResumeOrchestratorAgent`
- `UnifiedOrchestratorAgent` (duplicate name)

### Proposed Consolidation

#### 1.1 `CoreOrchestrationAgent` (L3)
**Merges:** `CachedOrchestratorAgent`, `HardenedWorkflowOrchestratorAgent`, `IntelligentOrchestratorAgent`, `SelfRecoveringOrchestratorAgent`, `ConsolidatedOrchestratorAgent`

**Features:**
- Caching layer for repeated orchestration patterns
- Self-recovery with automatic retry and fallback
- Intelligent routing based on task type
- Hardened error handling

**Implementation Plan:**
```python
class CoreOrchestrationAgent(L3OrchestrationBaseAgent):
    """
    Unified L3 orchestration with caching, self-recovery, and intelligent routing.
    
    Consolidates:
    - CachedOrchestratorAgent (caching)
    - HardenedWorkflowOrchestratorAgent (error handling)
    - IntelligentOrchestratorAgent (smart routing)
    - SelfRecoveringOrchestratorAgent (retry/fallback)
    """
    
    def __init__(self, cache_enabled: bool = True, max_retries: int = 3):
        self.cache = {} if cache_enabled else None
        self.max_retries = max_retries
    
    def orchestrate(self, task: Task) -> Result:
        # Check cache
        # Route intelligently
        # Execute with retry
        # Handle errors with recovery
        pass
```

**Migration Steps:**
1. Create `CoreOrchestrationAgent` with all features
2. Add factory methods for legacy instantiation patterns
3. Update imports in consuming code
4. Deprecate legacy agents with warnings
5. Archive legacy agents after 30-day deprecation period

#### 1.2 `SovereignIntegrationOrchestratorAgent` (L3)
**Merges:** `SovereignRagOrchestratorAgent`, `SovereignRedisOrchestratorAgent`

**Features:**
- Unified interface for external service orchestration
- RAG pipeline orchestration
- Redis cache orchestration
- Pluggable backend support

#### 1.3 `AppWorkflowOrchestratorAgent` (Apps)
**Merges:** `LicWorkflowOrchestratorAgent`, `OutreachPhase5OrchestratorAgent`, `Phase4/6/7OrchestratorAgent`

**Features:**
- Phase-based workflow execution
- LIC and RG workflow support
- Configurable phase definitions

#### 1.4 `AppHealingOrchestratorAgent` (Apps)
**Merges:** `LicHealingOrchestratorAgent`, `RgHealingOrchestratorAgent`

**Features:**
- Unified healing orchestration for both LIC and RG
- App-specific healing strategies via configuration

---

## Phase 2: Validator Consolidation (Priority: HIGH)

### Current State: 18 Validators

**L5 Layer (14 agents):**
- `AgentRegistryValidatorAgent`
- `AsyncBlockingValidatorAgent`
- `CanonAstValidatorAgent`
- `CanonValidatorAgent`
- `CognitiveContractValidatorAgent`
- `ContextAwareValidatorAgent`
- `ExternalHttpValidatorAgent`
- `GravityValidatorAgent`
- `HealValidatorAgent`
- `HygieneValidatorAgent`
- `InputValidatorAgent`
- `PrintStatementValidatorAgent`
- `SyntaxValidatorAgent`
- `UnifiedHygieneValidatorAgent`

**L1 Layer (1 agent):**
- `UnifiedASTValidatorAgent`

**Apps Layer (3 agents):**
- `ContactValidatorAgent`
- `ContentCleanlinessValidatorAgent`
- `MessageDiversityValidatorAgent`

### Proposed Consolidation

#### 2.1 `UnifiedCodeValidatorAgent` (L5)
**Merges:** `CanonAstValidatorAgent`, `CanonValidatorAgent`, `SyntaxValidatorAgent`, `PrintStatementValidatorAgent`, `AsyncBlockingValidatorAgent`

**Features:**
- Single AST traversal for all code validation
- Configurable rule sets
- Standardized violation reporting

**Implementation Plan:**
```python
class UnifiedCodeValidatorAgent(L5SafetyBaseAgent):
    """
    Unified code validation with single AST traversal.
    
    Rule Categories:
    - syntax: Basic Python syntax validation
    - canon: Canon compliance rules
    - async: Async/blocking pattern detection
    - print: Print statement detection
    """
    
    RULE_CATEGORIES = {
        'syntax': SyntaxRules,
        'canon': CanonRules,
        'async': AsyncRules,
        'print': PrintRules,
    }
    
    def validate(self, file_path: Path, categories: List[str] = None) -> ValidationReport:
        tree = ast.parse(file_path.read_text())
        violations = []
        
        for category in (categories or self.RULE_CATEGORIES.keys()):
            rules = self.RULE_CATEGORIES[category]
            violations.extend(rules.check(tree))
        
        return ValidationReport(violations)
```

#### 2.2 `UnifiedStructureValidatorAgent` (L5)
**Merges:** `GravityValidatorAgent`, `HygieneValidatorAgent`, `UnifiedHygieneValidatorAgent`, `AgentRegistryValidatorAgent`, `CognitiveContractValidatorAgent`

**Features:**
- Structure and hierarchy validation
- Hygiene checks (duplicates, orphans)
- Registry compliance
- Contract validation

#### 2.3 `AppContentValidatorAgent` (Apps)
**Merges:** `ContactValidatorAgent`, `ContentCleanlinessValidatorAgent`, `MessageDiversityValidatorAgent`

**Features:**
- Content validation for outreach messages
- Contact validation
- Diversity/uniqueness checks

---

## Phase 3: Manager Consolidation (Priority: MEDIUM)

### Current State: 12 Managers

**L4 Layer (3 agents):**
- `UnifiedCheckpointManagerAgent`
- `ValidationContextManagerAgent`
- `UnifiedStateManagementAgent` (already consolidated)

**L5 Layer (9 agents):**
- `AgentPermissionManagerAgent`
- `BudgetManagerAgent`
- `FallbackManagerAgent`
- `FileManagerAgent`
- `FissionManagerAgent`
- `McpConnectionManagerAgent`
- `ProactiveResourceManagerAgent`
- `SecureCheckpointManagerAgent`
- `SecureConfigManagerAgent`

### Proposed Consolidation

#### 3.1 `UnifiedResourceManagerAgent` (L5)
**Merges:** `BudgetManagerAgent`, `ProactiveResourceManagerAgent`, `FallbackManagerAgent`

**Features:**
- Budget tracking and enforcement
- Resource allocation
- Proactive resource management
- Fallback strategies

#### 3.2 `UnifiedSecurityManagerAgent` (L5)
**Merges:** `AgentPermissionManagerAgent`, `SecureCheckpointManagerAgent`, `SecureConfigManagerAgent`

**Features:**
- Permission management
- Secure checkpoint handling
- Configuration security

#### 3.3 `UnifiedConnectionManagerAgent` (L5)
**Merges:** `McpConnectionManagerAgent`, `FileManagerAgent`

**Features:**
- MCP connection management
- File system operations
- Unified I/O interface

#### 3.4 `UnifiedProcessManagerAgent` (L5)
**Merges:** `FissionManagerAgent`, `ValidationContextManagerAgent`

**Features:**
- Process fission/fusion
- Validation context management

---

## Phase 4: Enforcer Consolidation (Priority: MEDIUM)

### Current State: 11 Enforcers

**L5 Layer (9 agents):**
- `CodeSSOTEnforcerAgent`
- `CodeStandardsEnforcerAgent` (already consolidated)
- `DocEnforcerAgent`
- `GravityEnforcerAgent`
- `HierarchyEnforcerAgent`
- `NamingEnforcerAgent`
- `PatternEnforcerAgent`
- `PythonFileSovereigntyEnforcerAgent`
- `TypeEnforcerAgent`

**Apps Layer (2 agents):**
- `ASCIIEnforcerAgent`
- `StrictDocEnforcerAgent`

### Proposed Consolidation

#### 4.1 `UnifiedCodeEnforcerAgent` (L5)
**Merges:** `CodeSSOTEnforcerAgent`, `CodeStandardsEnforcerAgent`, `PatternEnforcerAgent`, `TypeEnforcerAgent`, `PythonFileSovereigntyEnforcerAgent`

**Features:**
- SSOT enforcement
- Code standards (inheritance, patterns, type hints)
- Python file sovereignty
- Single enforcement pass

#### 4.2 `UnifiedStructureEnforcerAgent` (L5)
**Merges:** `GravityEnforcerAgent`, `HierarchyEnforcerAgent`, `NamingEnforcerAgent`, `DocEnforcerAgent`

**Features:**
- Gravity/layer enforcement
- Hierarchy compliance
- Naming conventions
- Documentation requirements

---

## Phase 5: Detector Consolidation (Priority: MEDIUM)

### Current State: 11 Detectors

**L5 Layer (8 agents):**
- `BiasDetectorAgent`
- `DeadCodeDetectorAgent`
- `DeadlockDetectorAgent`
- `DriftDetectorAgent`
- `HallucinationDetectorAgent`
- `MethodChangeDetectorAgent`
- `PromptInjectionDetectorAgent`

**L2 Layer (1 agent):**
- `MemoryLeakDetectorAgent`

**Apps Layer (2 agents):**
- `ConvergenceDetectorAgent`
- `PlaceholderDetectorAgent`

### Proposed Consolidation

#### 5.1 `UnifiedCodeDetectorAgent` (L5)
**Merges:** `DeadCodeDetectorAgent`, `DriftDetectorAgent`, `MethodChangeDetectorAgent`, `DeadlockDetectorAgent`

**Features:**
- Dead code detection
- Drift detection
- Method change tracking
- Deadlock detection

#### 5.2 `UnifiedSafetyDetectorAgent` (L5)
**Merges:** `BiasDetectorAgent`, `HallucinationDetectorAgent`, `PromptInjectionDetectorAgent`

**Features:**
- Bias detection in outputs
- Hallucination detection
- Prompt injection detection

---

## Phase 6: Healer Consolidation (Priority: LOW)

### Current State: 8 Healers

**L5 Layer (8 agents):**
- `CanonHealerAgent`
- `GravityHealerAgent`
- `HealerAgent`
- `HierarchyHealerAgent`
- `ImportHealerAgent`
- `NamingLawHealerAgent`
- `StructuralHealerAgent`
- `TerritoryHealerAgent`

### Proposed Consolidation

#### 6.1 `UnifiedCodeHealerAgent` (L5)
**Merges:** `CanonHealerAgent`, `ImportHealerAgent`, `StructuralHealerAgent`

**Features:**
- Canon compliance healing
- Import fixing
- Structural repairs

#### 6.2 `UnifiedStructureHealerAgent` (L5)
**Merges:** `GravityHealerAgent`, `HierarchyHealerAgent`, `NamingLawHealerAgent`, `TerritoryHealerAgent`

**Features:**
- Gravity/layer healing
- Hierarchy repairs
- Naming law compliance
- Territory mapping

---

## Phase 7: Router Consolidation (Priority: LOW)

### Current State: 7 Routers

**L2 Layer (5 agents):**
- `DynamicModelRouterAgent`
- `McpRouterAgent`
- `ModelRouterAgent`
- `MultiProviderRouterAgent`
- `ReasoningRouterAgent`

**Apps Layer (2 agents):**
- `OutreachSignalRouterAgent`
- `SignalRouterAgent`

### Proposed Consolidation

#### 7.1 `UnifiedModelRouterAgent` (L2)
**Merges:** `DynamicModelRouterAgent`, `ModelRouterAgent`, `MultiProviderRouterAgent`, `ReasoningRouterAgent`

**Features:**
- Dynamic model selection
- Multi-provider support
- Reasoning-based routing
- Cost optimization

#### 7.2 `UnifiedSignalRouterAgent` (Apps)
**Merges:** `OutreachSignalRouterAgent`, `SignalRouterAgent`

**Features:**
- Signal routing for both LIC and RG
- Configurable routing rules

---

## Phase 8: Executor Consolidation (Priority: LOW)

### Current State: 5 Executors

**L3 Layer (1 agent):**
- `DagExecutorAgent`

**L5 Layer (3 agents):**
- `IntegrityGateExecutorAgent`
- `L5IntegrityGateExecutorAgent`
- `SafetyExecutorAgent`

**Apps Layer (1 agent):**
- `OutreachValidationExecutorAgent`

### Proposed Consolidation

#### 8.1 `UnifiedSafetyExecutorAgent` (L5)
**Merges:** `IntegrityGateExecutorAgent`, `L5IntegrityGateExecutorAgent`, `SafetyExecutorAgent`

**Features:**
- Integrity gate execution
- Safety checks
- Unified execution interface

---

## Implementation Timeline

### Sprint 1 (Week 1-2): Orchestrator Consolidation
- [ ] Create `CoreOrchestrationAgent`
- [ ] Create `SovereignIntegrationOrchestratorAgent`
- [ ] Migrate L3 orchestrators
- [ ] Update tests

### Sprint 2 (Week 3-4): Validator Consolidation
- [ ] Create `UnifiedCodeValidatorAgent`
- [ ] Create `UnifiedStructureValidatorAgent`
- [ ] Migrate L5 validators
- [ ] Update tests

### Sprint 3 (Week 5-6): Manager & Enforcer Consolidation
- [ ] Create unified managers
- [ ] Create unified enforcers
- [ ] Migrate and test

### Sprint 4 (Week 7-8): Detector, Healer, Router, Executor Consolidation
- [ ] Create remaining unified agents
- [ ] Complete migration
- [ ] Archive deprecated agents

---

## Testing Strategy

### For Each Consolidation Phase:

1. **Unit Tests**
   - All existing tests must pass on unified agent
   - Add tests for new combined functionality
   - Test backward compatibility via factory methods

2. **Integration Tests**
   - Test unified agent in full workflow
   - Verify no regression in dependent systems

3. **Migration Tests**
   - Test legacy agent → unified agent migration
   - Verify deprecation warnings work correctly

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking changes | Medium | High | Factory methods for backward compatibility |
| Performance regression | Low | Medium | Benchmark before/after consolidation |
| Missing functionality | Medium | High | Comprehensive feature mapping before merge |
| Test coverage gaps | Medium | Medium | Require 100% test pass before deprecation |

---

## Success Metrics

1. **Agent Count Reduction:** 270 → 180-200 (25-33% reduction)
2. **Code Duplication:** Reduce by 40%+
3. **Test Coverage:** Maintain or improve current 88%
4. **Healing Coverage:** Maintain 99%
5. **Performance:** No regression in critical paths

---

## Appendix A: Full Agent Inventory by Pattern

### Orchestrators (20)
| Agent | Layer | Status |
|-------|-------|--------|
| CachedOrchestratorAgent | L3 | Consolidate → CoreOrchestrationAgent |
| ConsolidatedOrchestratorAgent | L3 | Consolidate → CoreOrchestrationAgent |
| HardenedWorkflowOrchestratorAgent | L3 | Consolidate → CoreOrchestrationAgent |
| IntelligentOrchestratorAgent | L3 | Consolidate → CoreOrchestrationAgent |
| OrchestratorAgentAndScopeManagerAgent | L3 | Consolidate → CoreOrchestrationAgent |
| ScriptsPlanningOrchestratorAgent | L3 | Keep (specialized) |
| SelfRecoveringOrchestratorAgent | L3 | Consolidate → CoreOrchestrationAgent |
| SovereignRagOrchestratorAgent | L3 | Consolidate → SovereignIntegrationOrchestratorAgent |
| SovereignRedisOrchestratorAgent | L3 | Consolidate → SovereignIntegrationOrchestratorAgent |
| UnifiedOrchestratorAgent | L3 | Keep (already unified) |
| HOPOrchestratorAgent | Apps | Keep (HOP-specific) |
| LicHealingOrchestratorAgent | Apps | Consolidate → AppHealingOrchestratorAgent |
| LicWorkflowOrchestratorAgent | Apps | Consolidate → AppWorkflowOrchestratorAgent |
| OutreachPhase5OrchestratorAgent | Apps | Consolidate → AppWorkflowOrchestratorAgent |
| Phase4OrchestratorAgent | Apps | Consolidate → AppWorkflowOrchestratorAgent |
| Phase6OrchestratorAgent | Apps | Consolidate → AppWorkflowOrchestratorAgent |
| Phase7OrchestratorAgent | Apps | Consolidate → AppWorkflowOrchestratorAgent |
| RgHealingOrchestratorAgent | Apps | Consolidate → AppHealingOrchestratorAgent |
| RgResumeOrchestratorAgent | Apps | Keep (RG-specific) |
| UnifiedOrchestratorAgent | Apps | Merge with L3 version |

### Validators (18)
| Agent | Layer | Status |
|-------|-------|--------|
| UnifiedASTValidatorAgent | L1 | Keep (already unified) |
| AgentRegistryValidatorAgent | L5 | Consolidate → UnifiedStructureValidatorAgent |
| AsyncBlockingValidatorAgent | L5 | Consolidate → UnifiedCodeValidatorAgent |
| CanonAstValidatorAgent | L5 | Consolidate → UnifiedCodeValidatorAgent |
| CanonValidatorAgent | L5 | Consolidate → UnifiedCodeValidatorAgent |
| CognitiveContractValidatorAgent | L5 | Consolidate → UnifiedStructureValidatorAgent |
| ContextAwareValidatorAgent | L5 | Keep (specialized) |
| ExternalHttpValidatorAgent | L5 | Keep (external integration) |
| GravityValidatorAgent | L5 | Consolidate → UnifiedStructureValidatorAgent |
| HealValidatorAgent | L5 | Keep (healing validation) |
| HygieneValidatorAgent | L5 | Consolidate → UnifiedStructureValidatorAgent |
| InputValidatorAgent | L5 | Keep (input validation) |
| PrintStatementValidatorAgent | L5 | Consolidate → UnifiedCodeValidatorAgent |
| SyntaxValidatorAgent | L5 | Consolidate → UnifiedCodeValidatorAgent |
| UnifiedHygieneValidatorAgent | L5 | Keep (already unified) |
| ContactValidatorAgent | Apps | Consolidate → AppContentValidatorAgent |
| ContentCleanlinessValidatorAgent | Apps | Consolidate → AppContentValidatorAgent |
| MessageDiversityValidatorAgent | Apps | Consolidate → AppContentValidatorAgent |

---

## Appendix B: Backward Compatibility Strategy

For each consolidated agent, provide factory methods:

```python
# In unified agent file
def create_legacy_cached_orchestrator(**kwargs) -> CoreOrchestrationAgent:
    """Factory for backward compatibility with CachedOrchestratorAgent."""
    warnings.warn(
        "CachedOrchestratorAgent is deprecated. Use CoreOrchestrationAgent.",
        DeprecationWarning
    )
    return CoreOrchestrationAgent(cache_enabled=True, **kwargs)

def create_legacy_self_recovering_orchestrator(**kwargs) -> CoreOrchestrationAgent:
    """Factory for backward compatibility with SelfRecoveringOrchestratorAgent."""
    warnings.warn(
        "SelfRecoveringOrchestratorAgent is deprecated. Use CoreOrchestrationAgent.",
        DeprecationWarning
    )
    return CoreOrchestrationAgent(max_retries=3, **kwargs)
```

---

## Appendix C: Registry Update Template

After each consolidation phase, update `SubAtomicRegistryAgent`:

```python
UNIFIED_AGENT_MAPPING = {
    # Phase 1: Orchestrator Consolidation
    "CachedOrchestratorAgent": CoreOrchestrationAgent,
    "HardenedWorkflowOrchestratorAgent": CoreOrchestrationAgent,
    "IntelligentOrchestratorAgent": CoreOrchestrationAgent,
    "SelfRecoveringOrchestratorAgent": CoreOrchestrationAgent,
    
    # Phase 2: Validator Consolidation
    "CanonAstValidatorAgent": UnifiedCodeValidatorAgent,
    "CanonValidatorAgent": UnifiedCodeValidatorAgent,
    "SyntaxValidatorAgent": UnifiedCodeValidatorAgent,
    # ... etc
}
```

---

**Report Generated:** January 19, 2026  
**Author:** Cascade AI  
**Version:** 2.0
