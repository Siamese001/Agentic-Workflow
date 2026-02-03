# Comprehensive Agent Integration Migration Plan

**Date:** 2026-02-03  
**Scope:** All 171 agents across agentic_core, apps_rg, apps_lic  
**Method:** AST-verified gap analysis  
**Goal:** Full integration with target architecture components  

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Agents** | 171 |
| **Agents Needing Migration** | 171 (100%) |
| **Detection Signal Gap** | 171 agents (0% coverage) |
| **Verification Gate Gap** | 171 agents (0% coverage) |
| **Meta-Learning Gap** | 171 agents (0% coverage) |
| **HITL/Human Review Gap** | 171 agents (0% coverage) |
| **Estimated Duration** | 12-16 weeks |
| **Risk Level** | HIGH (mitigated by phased approach) |

---

## AST-Verified Current State

### Layer Distribution
| Layer | Agents | With Healing | Without Healing |
|-------|--------|--------------|-----------------|
| **Apps** | 43 | 43 | 0 |
| **L5 Safety** | 85 | 85 | 0 |
| **L6 Observability** | 11 | 11 | 0 |
| **L3 Orchestration** | 10 | 9 | 1 |
| **L1 Cognition** | 7 | 7 | 0 |
| **L2 Execution** | 6 | 6 | 0 |
| **L4 State** | 5 | 5 | 0 |
| **L0 Maintenance** | 2 | 2 | 0 |
| **Base** | 1 | 1 | 0 |
| **Tests** | 1 | 1 | 0 |

### Current Mixin Usage
| Mixin | Agents Using | % Coverage |
|-------|-------------|------------|
| SovereignBaseAgent | 130 | 76% |
| SubatomicTestingMixin | 89 | 52% |
| LICAgentBase | 16 | 9% |
| RGAgentBase | 13 | 8% |
| MCPHardenedMixin | 6 | 4% |
| HealerMixin | 5 | 3% |
| RedisCacheMixin | 3 | 2% |
| **MetaLearningMixin** | **0** | **0%** |
| **HITLMixin** | **0** | **0%** |
| **AuditTrailMixin** | **0** | **0%** |

### Critical Component Usage (AST Verified)
| Component | Agents Using | Gap |
|-----------|-------------|-----|
| DetectionSignal | 0 | 171 agents |
| VerificationGate | 0 | 171 agents |
| HumanReviewQueue | 0 | 171 agents |
| recall_or_execute | 0 | 171 agents |
| log_audit_event | 0 | 171 agents |

---

## Migration Strategy: Hierarchical Cascade

### Principle: Top-Down Inheritance Propagation

```
Phase 1: Base Agents (1 agent)
    ↓ inheritance propagates
Phase 2: Layer Base Agents (L0-L6 bases)
    ↓ inheritance propagates  
Phase 3: Domain Base Agents (RGAgentBase, LICAgentBase)
    ↓ inheritance propagates
Phase 4: Core L5 Safety Agents (85 agents)
    ↓ patterns established
Phase 5: Other Core Layers (L0-L4, L6)
    ↓ patterns replicated
Phase 6: Domain Apps (apps_rg, apps_lic)
```

By fixing base agents first, child agents automatically inherit capabilities.

---

## Phase 1: Foundation Layer (Week 1)

### 1.1 SovereignBaseAgent Enhancement
**Target:** `agentic_core/base_agents/SovereignBaseAgent.py`  
**Impact:** 130 agents inherit changes automatically

| Sub-phase | Task | Risk | Verification |
|-----------|------|------|--------------|
| 1.1.1 | Add MetaLearningMixin to inheritance | LOW | Unit test recall_or_execute |
| 1.1.2 | Add AuditTrailMixin to inheritance | LOW | Verify log_audit_event available |
| 1.1.3 | Add CostGuardrailMixin to inheritance | LOW | Verify budget tracking |
| 1.1.4 | Add optional HITLMixin base | MEDIUM | Feature flag control |
| 1.1.5 | Integration test | LOW | Run sovereign_test_suite |

**Deliverable:** All 130 SovereignBaseAgent children gain mixins

### 1.2 Layer Base Agents
**Target:** L0-L6 Base Agents  
**Impact:** Layer-specific behavior

| Sub-phase | Agent | Location | Special Integration |
|-----------|-------|----------|---------------------|
| 1.2.1 | L0MaintenanceBaseAgent | `L0_maintenance/scripts/` | Healing priority |
| 1.2.2 | L1CognitionBaseAgent | `base_agents/` | Memory integration |
| 1.2.3 | L2ExecutionBaseAgent | `base_agents/` | MCP integration |
| 1.2.4 | L3OrchestrationBaseAgent | `base_agents/` | Workflow tracking |
| 1.2.5 | L4StateBaseAgent | `base_agents/` | State persistence |
| 1.2.6 | L5SafetyBaseAgent | `base_agents/` | VerificationGate mandatory |
| 1.2.7 | L6ObservabilityBaseAgent | `base_agents/` | Metrics integration |

### 1.3 HealerMixin Enhancement
**Target:** `agentic_core/base_agents/healer_mixin.py`  
**Impact:** All healing agents get verification

| Sub-phase | Task | Risk |
|-----------|------|------|
| 1.3.1 | Add VerificationGate in __init__ | LOW |
| 1.3.2 | Add pre-check in heal() method | MEDIUM |
| 1.3.3 | Add HumanReviewQueue for high-risk | MEDIUM |
| 1.3.4 | Add DetectionSignal return type | LOW |

---

## Phase 2: Domain Base Agents (Week 2)

### 2.1 RGAgentBase Enhancement
**Target:** `apps_rg/shared/RGAgentBase.py`  
**Impact:** 13 apps_rg agents inherit changes

| Sub-phase | Task | Integration |
|-----------|------|-------------|
| 2.1.1 | Inherit from enhanced SovereignBaseAgent | Auto |
| 2.1.2 | Add PineconeVectorMixin for content search | Domain-specific |
| 2.1.3 | Add resume/content domain DetectionSignals | Domain-specific |
| 2.1.4 | Integration test with RG workflow | Validation |

### 2.2 LICAgentBase Enhancement
**Target:** `apps_lic/shared/LICAgentBase.py`  
**Impact:** 16 apps_lic agents inherit changes

| Sub-phase | Task | Integration |
|-----------|------|-------------|
| 2.2.1 | Inherit from enhanced SovereignBaseAgent | Auto |
| 2.2.2 | Add outreach domain DetectionSignals | Domain-specific |
| 2.2.3 | Add campaign tracking mixins | Domain-specific |
| 2.2.4 | Integration test with LIC workflow | Validation |

### 2.3 SubatomicTestingMixin Enhancement
**Target:** `agentic_core/base_agents/subatomic_testing_mixin.py`  
**Impact:** 89 agents with self-testing

| Sub-phase | Task | Integration |
|-----------|------|-------------|
| 2.3.1 | Add DetectionSignal output for test failures | P0 |
| 2.3.2 | Add meta-learning for test patterns | P1 |
| 2.3.3 | Add audit logging for test runs | P1 |

---

## Phase 3: L5 Safety Layer (Weeks 3-5)

### 3.1 Validators Sub-Phase (Week 3)
**Target:** `agentic_core/L5_safety/validators/` (50+ agents)

#### 3.1.1 Critical Validators First
| Agent | Priority | Special Integration |
|-------|----------|---------------------|
| FileClassificationAgent | P0 | DetectionSignal + VerificationGate |
| BiasAuditorAgent | P0 | AuditTrail mandatory |
| CanonDependencySentinelAgent | P0 | Meta-learning for patterns |
| CartographerAgent | P0 | Knowledge graph integration |
| CodeDeduplicationAgent | P0 | VerificationGate for dedup |

#### 3.1.2 Structural Validators
| Agent | Integration Pattern |
|-------|---------------------|
| HierarchyAgent | DetectionSignal for violations |
| LocationAgent | VerificationGate for moves |
| DepthValidatorAgent | DetectionSignal + auto-fix |
| StructureValidatorAgent | Full tollgate integration |

#### 3.1.3 Code Quality Validators
| Agent | Integration Pattern |
|-------|---------------------|
| DocstringComplianceAgent | DetectionSignal |
| TypeHintValidatorAgent | DetectionSignal |
| ImportValidatorAgent | VerificationGate |
| ComplexityAnalyzerAgent | Meta-learning |

### 3.2 Guardrails Sub-Phase (Week 4)
**Target:** `agentic_core/L5_safety/guardrails/` (30+ agents)

#### 3.2.1 Security Guardrails
| Agent | Integration | Risk |
|-------|-------------|------|
| RedSentinelAgent | Full HITL workflow | HIGH |
| AdversarialRedTeamerAgent | AuditTrail mandatory | HIGH |
| AutonomousThreatEvolutionAgent | Sandboxed execution | HIGH |
| ConstitutionalReviewerAgent | Human review gate | MEDIUM |

#### 3.2.2 Quality Guardrails
| Agent | Integration | Risk |
|-------|-------------|------|
| CodeFormatterAgent | VerificationGate | LOW |
| CostGovernorAgent | Already has budget logic | LOW |
| InputMembrane | DetectionSignal output | LOW |
| L5SafetyLayer | Orchestration hub | MEDIUM |

### 3.3 Healers Sub-Phase (Week 5)
**Target:** All healing agents

#### 3.3.1 Core Healers
| Agent | Integration | Mandatory |
|-------|-------------|-----------|
| CodeHealerAgent | VerificationGate pre-check | YES |
| StructureHealerAgent | Human review for moves | YES |
| SurgicalCSTHealer | Target verification | YES |

#### 3.3.2 Pattern: Healing with Verification
```python
def heal(self, violation: dict) -> dict:
    # P0: Verify target exists
    if not self.verification_gate.verify_action(
        file_path=violation['file_path'],
        action_type=violation['fix_type'],
        target_node=violation['target']
    ):
        return {'status': 'skipped', 'reason': 'target_not_found'}
    
    # P0: Check risk level
    signal = DetectionSignal.from_violation(violation)
    if signal.classify_risk_level() == 'high':
        # Route to human review
        request = self.review_queue.submit_for_review(
            context_bundle=self._build_context(violation, signal)
        )
        return {'status': 'pending_review', 'request_id': request.request_id}
    
    # Execute fix
    result = self._do_heal(violation)
    
    # P0: Learn from outcome
    await self.learn_experience(
        context=f"heal:{violation['type']}:{violation['file_hash']}",
        result=result
    )
    
    return result
```

---

## Phase 4: Core Layers L0-L4, L6 (Weeks 6-8)

### 4.1 L6 Observability (Week 6)
**Target:** 11 agents

| Agent | Integration | Priority |
|-------|-------------|----------|
| MetricsAgent | Central metrics collection | P0 |
| TelemetryAgent | Distributed tracing | P1 |
| TracingAgent | Span management | P1 |
| PerformanceAnalystAgent | Meta-learning for patterns | P2 |
| SovereignObservabilityAgent | Hub integration | P0 |

### 4.2 L3 Orchestration (Week 6)
**Target:** 10 agents

| Agent | Integration | Priority |
|-------|-------------|----------|
| DagEngineAgent | Workflow tracking | P0 |
| DAGMutatorAgent | VerificationGate for DAG changes | P0 |
| DecompositionOrchestratorAgent | Meta-learning | P1 |
| FissionManagerAgent | Human review for splits | P1 |
| NervousSystemAgent | Central coordination | P0 |

### 4.3 L1 Cognition (Week 7)
**Target:** 7 agents

| Agent | Integration | Priority |
|-------|-------------|----------|
| BudgetAgent | Cost tracking (already partial) | P1 |
| LLMPromptGovernorAgent | Meta-learning for prompts | P0 |
| MetaLearningAgent | Self-reference integration | P0 |
| SovereignCognitivePlaneAgent | Full meta-learning | P0 |
| UnifiedASTValidatorAgent | DetectionSignal | P0 |

### 4.4 L2 Execution (Week 7)
**Target:** 6 agents

| Agent | Integration | Priority |
|-------|-------------|----------|
| EmbeddingSovereignAgent | Vector integration | P0 |
| ToolsmithAgent | Tool registration | P1 |
| HistorianAgent | Audit trail | P1 |
| IntegrityGateExecutorAgent | VerificationGate | P0 |
| PeerIntelligenceAuditorAgent | Meta-learning | P1 |

### 4.5 L4 State (Week 8)
**Target:** 5 agents

| Agent | Integration | Priority |
|-------|-------------|----------|
| GravityStateAgent | State persistence | P0 |
| StateValidatorAgent | DetectionSignal | P0 |
| UiValidationAgent | DetectionSignal | P1 |
| UnifiedCheckpointManagerAgent | Audit trail | P0 |
| UnifiedStateManagementAgent | Full integration | P0 |

### 4.6 L0 Maintenance (Week 8)
**Target:** 2 agents

| Agent | Integration | Priority |
|-------|-------------|----------|
| BootstrapAgent | System initialization | P0 |
| L0MaintenanceBaseAgent | Healing coordination | P0 |

---

## Phase 5: Domain Applications (Weeks 9-12)

### 5.1 apps_rg Integration (Weeks 9-10)
**Target:** 21 agents in apps_rg

#### 5.1.1 RG Engines (Week 9)
| Agent | Domain | Integration |
|-------|--------|-------------|
| ATSCompatibilityAgent | Resume | DetectionSignal |
| BrandComplianceAgent | Resume | DetectionSignal |
| CampaignPlannerAgent | Resume | Meta-learning |
| ContentQualityAgent | Resume | DetectionSignal |
| ContentStrategyAgent | Resume | Meta-learning |
| FactCheckAgent | Resume | VerificationGate |
| ProactiveAgent | Resume | Meta-learning |
| RgHealingOrchestratorAgent | Resume | Full tollgate |
| RgReflectionAgent | Resume | Meta-learning |
| RgResumeOrchestratorAgent | Resume | Orchestration hub |
| RgStrategicPlannerAgent | Resume | Meta-learning |
| RgTemplateOptimizerAgent | Resume | Pinecone search |
| SectionBalanceAgent | Resume | DetectionSignal |

#### 5.1.2 RG Tools & Shared (Week 10)
| Agent | Domain | Integration |
|-------|--------|-------------|
| DispatchResumeToolsAgent | Resume | Tool registry |
| GapClosureArchitectAgent | Resume | Meta-learning |

### 5.2 apps_lic Integration (Weeks 11-12)
**Target:** 22 agents in apps_lic

#### 5.2.1 HOP Pipeline Agents (Week 11)
| Agent | Stage | Integration |
|-------|-------|-------------|
| HOP1ProfileAnalysisAgent | Analysis | Meta-learning |
| HOP2ResearchAgent | Research | Pinecone search |
| HOP3SenderGroundingAgent | Grounding | Meta-learning |
| HOP4RoutingAgent | Routing | DetectionSignal |
| HOP5GenerationAgent | Generation | Meta-learning |
| HOP6ValidationAgent | Validation | Full tollgate |
| HOP7GateDecisionAgent | Decision | HITL integration |
| HOP8QAReportAgent | Reporting | Audit trail |
| HOP9IntegrationAgent | Integration | Orchestration |

#### 5.2.2 LIC Supporting Agents (Week 12)
| Agent | Domain | Integration |
|-------|--------|-------------|
| CampaignBalanceAgent | Outreach | DetectionSignal |
| DeliverabilityAgent | Outreach | Meta-learning |
| DispatchOutreachToolsAgent | Outreach | Tool registry |
| GovernanceShieldAgent | Outreach | HITL mandatory |
| IntelligenceLibrarianAgent | Outreach | Pinecone search |
| LeadQualityAgent | Outreach | DetectionSignal |
| LicHealingOrchestratorAgent | Outreach | Full tollgate |
| LicReflectionAgent | Outreach | Meta-learning |
| LicTemplateOptimizerAgent | Outreach | Pinecone search |
| MessageComplianceAgent | Outreach | DetectionSignal |
| MessageDiversityValidatorAgent | Outreach | Meta-learning |
| OutreachLearningAgent | Outreach | Meta-learning |
| OutreachPhase5OrchestratorAgent | Outreach | Orchestration |
| OutreachProactiveAgent | Outreach | Meta-learning |
| OutreachSignalRouterAgent | Outreach | DetectionSignal |
| OutreachValidationExecutorAgent | Outreach | Full tollgate |
| PlaceholderDetectorAgent | Outreach | DetectionSignal |
| AppContentValidatorAgent | Outreach | DetectionSignal |

---

## Phase 6: Validation & Hardening (Weeks 13-14)

### 6.1 Integration Testing
| Test Suite | Scope | Verification |
|------------|-------|--------------|
| MRO Tests | All agents | No inheritance conflicts |
| MetaLearning Tests | recall_or_execute | Cache hit/miss |
| Tollgate Tests | Full workflow | Detection → Validation → Review → Heal |
| Performance Tests | Latency | <100ms overhead |
| Chaos Tests | Failures | Graceful degradation |

### 6.2 Feature Flag Rollout
| Flag | Default | Description |
|------|---------|-------------|
| USE_META_LEARNING | true | Enable recall_or_execute |
| USE_VERIFICATION_GATE | true | Enable target verification |
| USE_HUMAN_REVIEW | true | Enable HITL routing |
| USE_DETECTION_SIGNAL | true | Enable structured output |
| USE_AUDIT_TRAIL | true | Enable cryptographic logging |

### 6.3 Monitoring Setup
| Metric | Target | Alert |
|--------|--------|-------|
| Cache Hit Rate | >70% | <50% |
| Verification Pass Rate | >95% | <90% |
| Human Review Queue Depth | <10 | >50 |
| Circuit Breaker Trips | 0 | >5/hour |

---

## Phase 7: Documentation & Training (Weeks 15-16)

### 7.1 Developer Documentation
- Integration patterns guide
- Mixin usage examples
- Troubleshooting guide
- MRO conflict resolution

### 7.2 Operational Runbooks
- Human review queue management
- Circuit breaker reset procedures
- Meta-learning cache invalidation
- Emergency rollback procedures

---

## Risk Mitigation Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| MRO Conflicts | MEDIUM | HIGH | Test each mixin combination |
| Performance Degradation | MEDIUM | MEDIUM | Feature flags, lazy loading |
| Human Review Bottleneck | LOW | HIGH | Auto-approve low-risk |
| Meta-Learning False Positives | MEDIUM | MEDIUM | Confidence thresholds |
| Infrastructure Dependency | LOW | HIGH | Graceful degradation |
| Breaking Changes | MEDIUM | HIGH | Incremental rollout |

---

## Success Metrics

| Milestone | Agents Integrated | Architecture Coverage |
|-----------|-------------------|----------------------|
| Phase 1 Complete | 130 (via inheritance) | 40% |
| Phase 2 Complete | 159 | 55% |
| Phase 3 Complete | 170 | 85% |
| Phase 4 Complete | 171 | 90% |
| Phase 5 Complete | 171 | 95% |
| Phase 6 Complete | 171 | 100% |

---

## Appendix A: Integration Pattern Templates

### A.1 Standard Agent Integration
```python
class MyAgent(
    MetaLearningMixin,       # P0 - recall_or_execute
    AuditTrailMixin,         # P1 - cryptographic logging
    CostGuardrailMixin,      # P1 - budget enforcement
    SovereignBaseAgent
):
    def __init__(self):
        super().__init__()
        self.verification_gate = VerificationGate()
        self.review_queue = HumanReviewQueue()
    
    def execute(self, task) -> DetectionSignal:
        return self.recall_or_execute(
            context=f"{self.__class__.__name__}:{task.hash}",
            execution_fn=lambda: self._do_execute(task)
        )
```

### A.2 Healing Agent Integration
```python
class MyHealer(
    MetaLearningMixin,
    AuditTrailMixin,
    HealerMixin,
    SovereignBaseAgent
):
    def heal(self, violation: dict) -> dict:
        # Pre-check
        if not self.verification_gate.verify_action(...):
            return {'status': 'skipped'}
        
        # Risk routing
        signal = DetectionSignal.from_violation(violation)
        if signal.classify_risk_level() == 'high':
            return self.submit_for_review(violation)
        
        # Execute with learning
        return self.recall_or_execute(
            context=f"heal:{violation['type']}",
            execution_fn=lambda: self._do_heal(violation)
        )
```

---

## Appendix B: Agent Inventory by Phase

### Phase 1 Agents (1)
- SovereignBaseAgent

### Phase 2 Agents (7)
- L0MaintenanceBaseAgent, L1CognitionBaseAgent, L2ExecutionBaseAgent
- L3OrchestrationBaseAgent, L4StateBaseAgent, L5SafetyBaseAgent
- L6ObservabilityBaseAgent

### Phase 3 Agents (85)
- All agents in `agentic_core/L5_safety/`

### Phase 4 Agents (41)
- L0: 2 agents, L1: 7 agents, L2: 6 agents
- L3: 10 agents, L4: 5 agents, L6: 11 agents

### Phase 5 Agents (43)
- apps_rg: 21 agents
- apps_lic: 22 agents

---

**Report Generated:** 2026-02-03T10:15:00-05:00  
**Analysis Method:** AST-based pattern matching with full file reads  
**Confidence:** HIGH (verified via integration_gap_analyzer.py)
