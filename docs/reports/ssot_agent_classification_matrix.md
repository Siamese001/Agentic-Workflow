# execute_ssot Agent Classification Matrix - Wave 1 Deliverable

**Generated:** 2025-01-03  
**Purpose:** Inventory and classify all agents called by execute_ssot for optimization  
**Scope:** 50 agents identified across L0-L6 layers

---

## Agent Inventory Summary

| Layer | Count | AGENT (Reasoning) | SCRIPT (Deterministic) |
|-------|-------|-------------------|------------------------|
| L0_routing | 2 | 1 | 1 |
| L1_cognition | 3 | 2 | 1 |
| L2_execution | 6 | 4 | 2 |
| L3_orchestration | 15 | 8 | 7 |
| L4_state | 0 | 0 | 0 |
| L5_safety | 24 | 12 | 12 |
| L6_observability | 0 | 0 | 0 |
| **TOTAL** | **50** | **27** | **23** |

---

## Detailed Classification Matrix

### L0_routing/reasoning/ (2 agents)

| Agent | Current | Proposed | Reasoning Complexity | L2 Phase | Rationale |
|-------|---------|----------|---------------------|----------|-----------|
| RootCustomsAgent | AGENT | **SCRIPT** | Low - AST pattern matching, deterministic routing rules | Discovery | Uses AST signals and fixed routing maps; no LLM or uncertainty |
| SSOTFolderCleanupAgent | AGENT | **SCRIPT** | Low - File operations based on static rules | Healing | Deterministic folder operations; no decision-making |

### L1_cognition/reasoning/ (3 agents)

| Agent | Current | Proposed | Reasoning Complexity | L2 Phase | Rationale |
|-------|---------|----------|---------------------|----------|-----------|
| ASTValidatorAgent | AGENT | **AGENT** | Medium - AST parsing with heuristic validation | Validation | Requires interpretation of AST structures |
| MetaLearningAgent | AGENT | **AGENT** | High - Pattern recognition, strategy adaptation | Alignment | Uses learning algorithms; true reasoning required |
| StrategicRecommendationAgent | AGENT | **SCRIPT** | Low - Rule-based recommendations | Alignment | Template-based suggestions; deterministic logic |

### L2_execution/reasoning/ (6 agents)

| Agent | Current | Proposed | Reasoning Complexity | L2 Phase | Rationale |
|-------|---------|----------|---------------------|----------|-----------|
| EmbeddingSovereignAgent | AGENT | **AGENT** | High - Embedding space navigation, semantic decisions | Execution | Complex vector operations; requires reasoning |
| RedisSovereignAgent | AGENT | **AGENT** | Medium - Cache strategy decisions | Execution | State-based decisions with uncertainty |
| SovereignMCPGatewayAgent | AGENT | **AGENT** | High - Gateway routing with failure handling | Execution | Dynamic routing decisions |
| StructuredEngineAgent | AGENT | **AGENT** | High - Structured output generation with validation | Execution | LLM-based structured generation |
| SubAtomicRegistryAgent | AGENT | **SCRIPT** | Low - Registry CRUD operations | Discovery | Deterministic registry operations |
| ToolsmithAgent | AGENT | **SCRIPT** | Low - Tool registration and lookup | Discovery | Static tool definitions |

### L3_orchestration/reasoning/ (15 agents)

| Agent | Current | Proposed | Reasoning Complexity | L2 Phase | Rationale |
|-------|---------|----------|---------------------|----------|-----------|
| CoverageAgent | AGENT | **SCRIPT** | Low - Coverage metric calculation | Reporting | Deterministic calculations |
| DAGMutatorAgent | AGENT | **AGENT** | High - DAG transformation planning | Alignment | Complex graph reasoning |
| DagEngineAgent | AGENT | **AGENT** | High - Execution ordering decisions | Execution | Dynamic scheduling decisions |
| DagRuntimeInspectorAgent | AGENT | **SCRIPT** | Low - Runtime state inspection | Discovery | Read-only diagnostics |
| DomainPlannerAgent | AGENT | **AGENT** | High - Domain-specific planning | Alignment | Requires domain reasoning |
| FissionManagerAgent | AGENT | **AGENT** | Medium - Split/merge decisions | Alignment | Heuristic-based partitioning |
| GravityStateAgent | AGENT | **SCRIPT** | Low - State tracking | Validation | Deterministic state machine |
| NervousSystemAgent | AGENT | **AGENT** | High - Event coordination | Execution | Complex event handling |
| OrchestrationHandshakeAgent | AGENT | **SCRIPT** | Low - Protocol coordination | Discovery | Fixed handshake protocol |
| SemanticGatekeeperAgent | AGENT | **AGENT** | High - Semantic validation | Validation | Context-aware semantic checks |
| StateManagementAgent | AGENT | **SCRIPT** | Low - State persistence | Reporting | CRUD operations |
| SubAtomicAgent | AGENT | **SCRIPT** | Low - Atomic operation wrapper | Execution | Thin wrapper layer |
| SubatomicHopAgent | AGENT | **SCRIPT** | Low - Cross-layer routing | Routing | Static routing table |
| UnifiedAgent | AGENT | **AGENT** | High - Multi-agent coordination | Alignment | Complex coordination logic |

### L5_safety/reasoning/ (24 agents)

| Agent | Current | Proposed | Reasoning Complexity | L2 Phase | Rationale |
|-------|---------|----------|---------------------|----------|-----------|
| AdversarialProbeAgent | AGENT | **AGENT** | High - Adversarial test generation | Validation | Requires creative adversarial reasoning |
| AdversarialRedTeamerAgent | AGENT | **AGENT** | High - Attack simulation | Validation | Complex attack planning |
| ArchitectureGovernorAgent | AGENT | **AGENT** | High - Architectural compliance | Validation | Multi-dimensional compliance checking |
| ArchitectureGovernorValidatorAgent | AGENT | **SCRIPT** | Low - Validation runner | Validation | Deterministic validation |
| AutonomousThreatEvolutionAgent | AGENT | **AGENT** | High - Threat evolution modeling | Validation | Requires predictive reasoning |
| AutonomyGuardianAgent | AGENT | **AGENT** | High - Autonomy boundary enforcement | Validation | Context-aware enforcement |
| BenchmarkingAgent | AGENT | **SCRIPT** | Low - Benchmark execution | Reporting | Deterministic benchmarking |
| BootstrapAgent | AGENT | **SCRIPT** | Low - System initialization | Discovery | Fixed initialization sequence |
| BoundaryTestingAgent | AGENT | **AGENT** | High - Boundary condition discovery | Validation | Exploratory boundary finding |
| ChaosEngineeringAgent | AGENT | **AGENT** | High - Chaos experiment design | Validation | Creative failure injection |
| CodeDeduplicationAgent | AGENT | **SCRIPT** | Low - Duplicate detection | Healing | Hash-based detection |
| CodeDetectorAgent | AGENT | **SCRIPT** | Low - Pattern matching | Discovery | Regex/static analysis |
| CodeEnforcerAgent | AGENT | **SCRIPT** | Low - Rule enforcement | Healing | Deterministic enforcement |
| CodeFormatterAgent | AGENT | **SCRIPT** | Low - Code formatting | Healing | Deterministic formatting |
| CodeHealerAgent | AGENT | **AGENT** | High - Automated healing decisions | Healing | Multi-strategy healing decisions |
| CodeJanitorAgent | AGENT | **SCRIPT** | Low - Cleanup operations | Healing | Deterministic cleanup |
| CodeValidatorAgent | AGENT | **SCRIPT** | Low - Syntax/static validation | Validation | Deterministic validation |
| CognitiveDispositionAgent | AGENT | **AGENT** | High - LLM-based disposition | Alignment | Uses LLM for cognitive analysis |
| ComplexityAnalyzerAgent | AGENT | **SCRIPT** | Low - Complexity metrics | Validation | Deterministic metrics |
| ConstitutionalReviewerAgent | AGENT | **AGENT** | High - Constitutional compliance | Validation | Interpretive reasoning required |
| CostGovernorAgent | AGENT | **SCRIPT** | Low - Cost tracking | Reporting | Deterministic cost accounting |
| CredentialScannerAgent | AGENT | **SCRIPT** | Low - Credential detection | Discovery | Pattern-based detection |
| DDDAlignmentAgent | AGENT | **AGENT** | High - DDD compliance analysis | Validation | Domain reasoning required |
| DependencyPruningAgent | AGENT | **SCRIPT** | Low - Dependency cleanup | Healing | Deterministic pruning |

---

## Consolidation Opportunities

### Duplicate/Overlapping Pairs

| Pair | Recommendation | Savings |
|------|----------------|---------|
| CodeHealerAgent + CodeJanitorAgent | Merge - Janitor becomes Healer mode | 1 agent |
| CodeValidatorAgent + CodeDetectorAgent | Merge - Detector becomes Validator mode | 1 agent |
| BoundaryTestingAgent + AdversarialProbeAgent | Merge - Probe becomes Boundary sub-mode | 1 agent |
| ArchitectureGovernorAgent + ArchitectureGovernorValidatorAgent | Merge - Validator becomes Governor sub-mode | 1 agent |
| StateManagementAgent + GravityStateAgent | Merge - State ops consolidated | 1 agent |

**Potential Savings: 5 agents → scripts or merged**

---

## L2 Lifecycle Phase Mapping

| L2 Phase | Primary Agents | Secondary Agents | Gap Analysis |
|----------|----------------|------------------|--------------|
| Discovery | RootCustomsAgent, SSOTFolderCleanupAgent, SubAtomicRegistryAgent, ToolsmithAgent, BootstrapAgent, CodeDetectorAgent, CredentialScannerAgent | DagRuntimeInspectorAgent, OrchestrationHandshakeAgent | All phases covered |
| Validation | ASTValidatorAgent, SemanticGatekeeperAgent, CodeValidatorAgent, ComplexityAnalyzerAgent, ArchitectureGovernorAgent | ArchitectureGovernorValidatorAgent, BoundaryTestingAgent, AdversarialProbeAgent | All phases covered |
| Alignment | MetaLearningAgent, StrategicRecommendationAgent, DomainPlannerAgent, FissionManagerAgent, UnifiedAgent, CognitiveDispositionAgent, DDDAlignmentAgent | DAGMutatorAgent | All phases covered |
| Execution | EmbeddingSovereignAgent, RedisSovereignAgent, SovereignMCPGatewayAgent, StructuredEngineAgent, DagEngineAgent, NervousSystemAgent, SubAtomicAgent, SubatomicHopAgent | CodeHealerAgent, CodeEnforcerAgent | All phases covered |
| Healing | CodeJanitorAgent, CodeFormatterAgent, CodeDeduplicationAgent, DependencyPruningAgent | (merged with Healer) | All phases covered |
| Reporting | CoverageAgent, BenchmarkingAgent, CostGovernorAgent, StateManagementAgent | — | All phases covered |

---

## Flag Conflicts Identified

| Location | Flag | Conflict | Resolution |
|----------|------|----------|------------|
| execute_ssot_cli.py | `--heal` | UWG has heal jurisdiction; per-agent heal overrides | Remove `--heal` from CLI; rely on UWG |
| execute_ssot_entrypoint.py | `--no-heal` | Conflicts with UWG default behavior | Remove; UWG controls via policy |
| Individual agents | `heal_override` | Agents override UWG decisions | Deprecate; route through UWG policy |

---

## Recommendations Summary

### Immediate Actions (Wave 2)
1. Convert 23 SCRIPT-classified agents to `*_util.py` scripts
2. Consolidate 5 duplicate/overlapping agent pairs
3. Remove conflicting heal flags from execute_ssot entrypoints

### Medium-term (Wave 3)
1. Ensure all L2 phases have explicit PTC (Phase Transition Contract) emitters
2. Standardize agent base class initialization
3. Add missing lifecycle hooks

### Long-term (Wave 4)
1. Harden entrypoint error handling
2. Document agent registry
3. Add integration tests for full lifecycle

---

## Next Steps

1. **Wave 2:** Execute flag consolidation and script conversion
2. **Wave 3:** Align L2 lifecycle phases
3. **Wave 4:** Standardize and harden

**Approval Required:** Proceed with Wave 2?

