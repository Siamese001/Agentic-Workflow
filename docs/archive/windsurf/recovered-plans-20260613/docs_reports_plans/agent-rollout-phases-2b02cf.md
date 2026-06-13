# Agent Rollout Phases - Breaking Down Open Scope

Detailed breakdown of Phase 7 (169 remaining agents) into actionable phases and sub-phases for systematic mixin adoption.

---

## Overview

| Phase | Scope | Agents | Duration | Risk |
|-------|-------|--------|----------|------|
| 7A | L5 Safety - Validators | 49 | TIME_REMOVED | MEDIUM |
| 7B | L5 Safety - Guardrails | 14 | TIME_REMOVED | HIGH |
| 7C | L5 Safety - Other | 22 | TIME_REMOVED | MEDIUM |
| 7D | Core Layers (L0-L4, L6) | 41 | TIME_REMOVED | LOW |
| 7E | Domain Apps (apps_rg) | 15 | TIME_REMOVED | MEDIUM |
| 7F | Domain Apps (apps_lic) | 28 | TIME_REMOVED | MEDIUM |
| **Total** | | **169** | **TIME_REMOVED** | |

---

## Phase 7A: L5 Validators (49 agents, TIME_REMOVED)

### 7A.1 Critical Validators (Week 1, Days 1-3)
**Priority:** P0 - These are referenced throughout the codebase

| Agent | Integration | Test Focus |
|-------|-------------|------------|
| FileClassificationAgent | DetectionSignal + VerificationGate | File type detection |
| BiasAuditorAgent | AuditTrail mandatory | Bias detection logging |
| HierarchyAgent | DetectionSignal for violations | Structure validation |
| LocationAgent | VerificationGate for moves | Path validation |
| StructureValidatorAgent | Full tollgate | Blueprint compliance |

### 7A.2 Code Quality Validators (Week 1, Days 4-5)
| Agent | Integration |
|-------|-------------|
| DocstringComplianceAgent | DetectionSignal |
| TypeHintValidatorAgent | DetectionSignal |
| ImportValidatorAgent | VerificationGate |
| ComplexityAnalyzerAgent | Meta-learning |
| CodeDeduplicationAgent | VerificationGate |

### 7A.3 Structural Validators (Week 2, Days 1-3)
| Agent | Integration |
|-------|-------------|
| DepthValidatorAgent | DetectionSignal + auto-fix |
| CartographerAgent | Knowledge graph |
| CanonDependencySentinelAgent | Meta-learning patterns |
| DependencyGraphAgent | DetectionSignal |
| CognitiveDispositionAgent | Meta-learning |

### 7A.4 Remaining Validators (Week 2, Days 4-5)
- Batch remaining 34 validators
- Standard FeatureFlaggedAgentMixin integration
- DetectionSignal output for all

**Checkpoint:** Run `MigrationHelper.get_migration_status()` for L5/validators

---

## Phase 7B: L5 Guardrails (14 agents, TIME_REMOVED)

### 7B.1 Security Guardrails (Days 1-3)
**Risk:** HIGH - These have security implications

| Agent | Integration | HITL |
|-------|-------------|------|
| RedSentinelAgent | Full HITL workflow | Required |
| AdversarialRedTeamerAgent | AuditTrail mandatory | Required |
| AutonomousThreatEvolutionAgent | Sandboxed execution | Required |
| ConstitutionalReviewerAgent | Human review gate | Required |

### 7B.2 Quality Guardrails (Days 4-5)
| Agent | Integration | HITL |
|-------|-------------|------|
| CodeFormatterAgent | VerificationGate | Optional |
| CostGovernorAgent | Budget tracking | Optional |
| InputMembrane | DetectionSignal | Optional |
| L5SafetyLayer | Orchestration hub | Optional |
| Remaining 6 agents | Standard integration | Optional |

**Checkpoint:** Security review of HITL configurations

---

## Phase 7C: L5 Other (22 agents, TIME_REMOVED)

### 7C.1 Policy Engine Agents (Days 1-2)
| Agent | Integration |
|-------|-------------|
| CodeHealerAgent | VerificationGate pre-check (mandatory) |
| StructureHealerAgent | Human review for moves |
| SurgicalCSTHealer | Target verification |

### 7C.2 Testing/Chaos Agents (Days 3-4)
| Agent | Integration |
|-------|-------------|
| BoundaryTestingAgent | Meta-learning |
| ChaosEngineeringAgent | AuditTrail |
| AdversarialProbeAgent | DetectionSignal |

### 7C.3 Remaining L5 Agents (Day 5)
- Batch remaining ~16 agents
- Standard FeatureFlaggedAgentMixin

**Checkpoint:** Full L5 compliance check (85 agents)

---

## Phase 7D: Core Layers (41 agents, TIME_REMOVED)

### 7D.1 L6 Observability (Week 1, Days 1-2)
| Agent | Integration |
|-------|-------------|
| MetricsAgent | Central metrics |
| TelemetryAgent | Distributed tracing |
| SovereignObservabilityAgent | Hub integration |
| Remaining 8 agents | Standard |

### 7D.2 L3 Orchestration (Week 1, Days 3-4)
| Agent | Integration |
|-------|-------------|
| DagEngineAgent | Workflow tracking |
| DAGMutatorAgent | VerificationGate |
| NervousSystemAgent | Central coordination |
| Remaining 7 agents | Standard |

### 7D.3 L1 Cognition (Week 1, Day 5)
| Agent | Integration |
|-------|-------------|
| MetaLearningAgent | Self-reference |
| LLMPromptGovernorAgent | Meta-learning |
| All 7 agents | Standard |

### 7D.4 L2 Execution (Week 2, Days 1-2)
| Agent | Integration |
|-------|-------------|
| IntegrityGateExecutorAgent | VerificationGate |
| ToolsmithAgent | Tool registry |
| All 6 agents | Standard |

### 7D.5 L4 State (Week 2, Days 3-4)
| Agent | Integration |
|-------|-------------|
| GravityStateAgent | State persistence |
| UnifiedStateManagementAgent | Full integration |
| All 5 agents | Standard |

### 7D.6 L0 Maintenance (Week 2, Day 5)
| Agent | Integration |
|-------|-------------|
| BootstrapAgent | System init |
| L0MaintenanceBaseAgent | Healing coordination |

**Checkpoint:** Core layers compliance (41 agents)

---

## Phase 7E: apps_rg (15 agents, TIME_REMOVED)

### 7E.1 RG Orchestrators (Days 1-2)
| Agent | Integration |
|-------|-------------|
| RgResumeOrchestratorAgent | RGDomainMixin + Orchestration |
| RgHealingOrchestratorAgent | Full tollgate |
| RgStrategicPlannerAgent | Meta-learning |

### 7E.2 RG Quality Agents (Days 3-4)
| Agent | Integration |
|-------|-------------|
| ContentQualityAgent | DetectionSignal |
| ATSCompatibilityAgent | DetectionSignal |
| BrandComplianceAgent | DetectionSignal |
| FactCheckAgent | VerificationGate |
| SectionBalanceAgent | DetectionSignal |

### 7E.3 RG Supporting Agents (Day 5)
- Remaining 7 agents
- All use RGDomainMixin
- Domain-specific pattern storage

**Checkpoint:** apps_rg compliance (15 agents)

---

## Phase 7F: apps_lic (28 agents, TIME_REMOVED)

### 7F.1 HOP Pipeline Agents (Week 1)
| Agent | Stage | Integration |
|-------|-------|-------------|
| HOP1ProfileAnalysisAgent | Analysis | Meta-learning |
| HOP2ResearchAgent | Research | Pinecone |
| HOP3SenderGroundingAgent | Grounding | Meta-learning |
| HOP4RoutingAgent | Routing | DetectionSignal |
| HOP5GenerationAgent | Generation | Meta-learning |
| HOP6ValidationAgent | Validation | Full tollgate |
| HOP7GateDecisionAgent | Decision | **HITL Required** |
| HOP8QAReportAgent | Reporting | AuditTrail |
| HOP9IntegrationAgent | Integration | Orchestration |

### 7F.2 LIC Orchestrators (Week 2, Days 1-2)
| Agent | Integration |
|-------|-------------|
| LicHealingOrchestratorAgent | Full tollgate |
| OutreachPhase5OrchestratorAgent | Orchestration |
| GovernanceShieldAgent | **HITL Mandatory** |

### 7F.3 LIC Quality Agents (Week 2, Days 3-5)
| Agent | Integration |
|-------|-------------|
| MessageComplianceAgent | DetectionSignal |
| LeadQualityAgent | DetectionSignal |
| CampaignBalanceAgent | DetectionSignal |
| Remaining 13 agents | LICDomainMixin |

**Checkpoint:** apps_lic compliance (28 agents), HITL config review

---

## Validation Checkpoints

| After Phase | Validation | Command |
|-------------|------------|---------|
| 7A | L5/validators compliant | `pytest tests/unit/agentic_core/L5_safety/validators/` |
| 7B | Security review | Manual HITL config review |
| 7C | Full L5 compliant | `MigrationHelper.get_migration_status(l5_agents)` |
| 7D | Core layers compliant | `pytest tests/unit/agentic_core/` |
| 7E | apps_rg compliant | `pytest tests/unit/apps_rg/` |
| 7F | Full migration complete | `pytest tests/integration/test_migration_e2e.py` |

---

## Risk Mitigation Per Phase

| Phase | Primary Risk | Mitigation |
|-------|--------------|------------|
| 7A | Breaking validators | Feature flag rollout |
| 7B | Security gaps | Mandatory HITL review |
| 7C | Healer failures | VerificationGate enforcement |
| 7D | Performance | Lazy loading, caching |
| 7E | Resume quality | Domain isolation |
| 7F | Compliance | HITL mandatory for LIC |

---

## Success Criteria

- [ ] 169/169 agents with FeatureFlaggedAgentMixin
- [ ] All healing agents have VerificationGate
- [ ] All security agents have HITL workflow
- [ ] All domain agents have proper isolation
- [ ] E2E integration tests pass
- [ ] Migration compliance report shows 100%

---

**Estimated Total Duration:** TIME_REMOVED
**Created:** 2026-02-03

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

