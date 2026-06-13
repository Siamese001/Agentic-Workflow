# L2 Architecture Gap Analysis & Implementation Plan-5869af

This plan performs a comprehensive gap analysis of the current agentic architecture against the four-bucket L2 structure (Pre-commit, Validation, Execution, Healing) defined in the technical mapping document, and provides a detailed phased implementation approach.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

The current Agentic-Workflow repository contains 190 agents across agentic_core (L0-L6 layers) and apps_* domains, but lacks the structured four-bucket L2 architecture specified in the technical mapping. Significant architectural refactoring is required to align with the intended design.

## Current Architecture Analysis

### agentic_core Structure (190 agents total)
- **L0_routing** (3 agents): RootCustomsAgent, SSOTFolderCleanupAgent
- **L1_cognition** (3 agents): ASTValidatorAgent, MetaLearningAgent, StrategicRecommendationAgent
- **L2_execution** (5 agents): EmbeddingSovereignAgent, SovereignMCPGatewayAgent, StructuredEngineAgent, SubAtomicRegistryAgent, ToolsmithAgent
- **L3_orchestration** (13 agents): CoverageAgent, DAGMutatorAgent, DagEngineAgent, DomainPlannerAgent, FissionManagerAgent, NervousSystemAgent, OrchestrationHandshakeAgent, SemanticGatekeeperAgent, StateManagementAgent, SubAtomicAgent, SubatomicHopAgent, UnifiedAgent
- **L4_state** (Limited agents): CheckpointManagerAgent, GravityStateAgent, PineconeSovereignAgent, CachedStateLedgerAgent
- **L5_safety** (85+ agents): Extensive validation, enforcement, and healing agents
- **L6_observability** (Limited agents): ObservabilityProbeExecutor, PerformanceAnalystAgentSimple, SovereignHealthMonitor

### apps_* Domain Structure
- **apps_lic** (38 reasoning agents): Campaign workflow, message architecture, compliance
- **apps_rg** (24 reasoning agents): Resume generation, ATS compatibility, content strategy
- **apps_shared** (9 reasoning agents): Infrastructure orchestration, shared services

## Four-Bucket L2 Structure Gap Analysis

### 1. Pre-commit Bucket (ASSEMBLY STAGE)
**Target Components (from mapping):**
- S0: System (hard-coded constitutions & invariants)
- I0: Instructional (identity & mixin behaviors)
- D0: Injections (semantic fences & tool constraints)
- C0: Dependency (RAG injected knowledge)
- U0: User Prompt (raw intent)

**Current State Gaps:**
- ❌ Missing dedicated Assembly Stage sandbox airlock
- ❌ No S0 System constitutions enforcement
- ❌ I0 Instructional mixins exist but not integrated into assembly pipeline
- ❌ D0 Injections not centralized or governed
- ❌ C0 Dependency injection exists but not structured for assembly
- ❌ U0 User prompt processing scattered across L1

### 2. Validation Bucket (L0/L5 Authority)
**Target Components:**
- L0 Routing: Central traffic control with classification, election, arbitration, dispatch
- L5 Safety: Risk classification, compliance, enforcement

**Current State Gaps:**
- ⚠️ L0 exists but lacks comprehensive routing authority
- ❌ Missing deterministic ruleset election
- ❌ No tool inventory arbitration
- ❌ L5 Safety extensive but not integrated with L0 routing decisions
- ❌ Missing policy hash correlation between layers

### 3. Execution Bucket (L2/L3 Core)
**Target Components:**
- L2 Unified Execution Core: PTC sandbox, initialization, execution, synthesis
- L3 Orchestration: Sequential handshake, conflict arbitration, tool coordination

**Current State Gaps:**
- ⚠️ L2 agents exist but lack unified PTC sandbox structure
- ❌ Missing initialization with lease verification and state freezing
- ❌ No universal write gateway enforcement
- ❌ L3 orchestration agents exist but lack sequential handshake protocol
- ❌ Missing confidence-tier healing subsystem integration

### 4. Healing Bucket (L6 Meta-learning)
**Target Components:**
- L6 Observability: Anomaly detection, RCA, pattern analysis
- Meta-learning Pipeline: Audit, telemetry, RCA, propose, validate, commit

**Current State Gaps:**
- ⚠️ L6 observability agents exist but limited in scope
- ❌ Missing comprehensive anomaly detection engine
- ❌ No structured RCA (Root Cause Analysis) pipeline
- ❌ Meta-learning pipeline exists but not integrated with healing
- ❌ Missing pattern analysis and optimization feedback loops

## Implementation Plan by Phases

### Phase 1: Foundation & Assembly Stage (Weeks 1-2)
**Scope:** Establish Pre-commit bucket infrastructure

**Wave 1.1: Assembly Stage Framework**
- Create `agentic_core/L2_execution/assembly/` directory structure
- Implement `AssemblyStageAgent.py` with S0/I0/D0/C0/U0 composition
- Add `SandboxAirlock.py` for deterministic composition validation
- Create `ConstitutionEnforcer.py` for S0 hard-coded rules

**Wave 1.2: Instructional & Dependency Integration**
- Refactor existing I0 mixins into assembly pipeline
- Centralize D0 injections under `agentic_core/L2_execution/assembly/injections/`
- Implement C0 RAG context injection with governance controls
- Add U0 user prompt preprocessing with intent extraction

**Wave 1.3: Assembly Validation**
- Create comprehensive tests for assembly stage components
- Add integration tests with existing L0/L5 layers
- Validate deterministic composition behavior

### Phase 2: Validation Authority Integration (Weeks 3-4)
**Scope:** Strengthen L0/L5 validation bucket

**Wave 2.1: L0 Routing Enhancement**
- Extend `RootCustomsAgent` with full routing authority
- Add deterministic ruleset election mechanism
- Implement tool inventory arbitration
- Add policy hash correlation and signature verification

**Wave 2.2: L5 Safety Integration**
- Create `SafetyAuthorityAgent.py` to coordinate with L0
- Implement risk tier classification with confidence scoring
- Add compliance hash verification and audit trails
- Integrate existing L5 validators into unified pipeline

**Wave 2.3: Policy Enforcement Bridge**
- Build L0↔L5 communication protocol
- Implement policy escalation and remediation workflows
- Add unified audit logging across validation layers

### Phase 3: Unified Execution Core (Weeks 5-6)
**Scope:** Implement L2/L3 execution bucket

**Wave 3.1: PTC Sandbox Infrastructure**
- Create `PTCSandboxAgent.py` with initialization, execution, synthesis phases
- Implement `LeaseVerifier.py` for signed plan validation
- Add `StateFreezer.py` for clean system state management
- Create `UniversalWriteGateway.py` for single mutation authority

**Wave 3.2: L3 Orchestration Protocol**
- Refactor existing orchestration agents into sequential handshake protocol
- Implement `ConflictArbitrationAgent.py` with weight/role resolution
- Add `ToolCoordinationAgent.py` for overlap management and hallucination prevention
- Create `ExecutionSynthesizer.py` for result aggregation and validation

**Wave 3.3: Healing Integration**
- Integrate confidence-tier healing subsystem into execution pipeline
- Add `HealingEscalationRouter.py` for tier selection logic
- Implement `RemediationDispatcher.py` with allowlist guards
- Create healing outcome feedback loops

### Phase 4: Observability & Meta-Learning (Weeks 7-8)
**Scope:** Complete L6 healing bucket

**Wave 4.1: Anomaly Detection Engine**
- Enhance existing L6 agents with comprehensive anomaly detection
- Implement `AnomalyEngineAgent.py` with drift detection and signal generation
- Add `TelemetryBroadcaster.py` for structured event emission
- Create `ArchivalSystem.py` for raw metrics storage

**Wave 4.2: RCA & Pattern Analysis**
- Implement `RootCauseAnalysisEngine.py` for failure classification
- Add `PatternAnalysisEngine.py` for flapping and drift spike detection
- Create `HealingOutcomeAggregator.py` for feedback collection
- Build semantic retrieval integration for C0 context

**Wave 4.3: Meta-Learning Pipeline**
- Complete existing meta-learning pipeline integration
- Add `ChangePackageProposer.py` with version store and approval gates
- Implement `ShadowEvaluator.py` and `OscillationDetector.py`
- Create `DampeningValidators.py` for stability controls

### Phase 5: Cross-Cutting Integration (Weeks 9-10)
**Scope:** System-wide integration and optimization

**Wave 5.1: Inter-Bucket Communication**
- Implement standardized protocols between all four buckets
- Add unified logging and telemetry across buckets
- Create system-wide audit trails and reproducibility

**Wave 5.2: Performance & Reliability**
- Optimize inter-bucket communication latency
- Add circuit breakers and fallback mechanisms
- Implement comprehensive error handling and recovery

**Wave 5.3: Governance & Compliance**
- Add system-wide governance dashboards
- Implement compliance reporting and audit trails
- Create operational runbooks and monitoring

## Detailed File Changes by Phase

### Phase 1 File Structure
```
agentic_core/L2_execution/assembly/
├── __init__.py
├── AssemblyStageAgent.py
├── SandboxAirlock.py
├── constitutions/
│   ├── __init__.py
│   ├── SystemConstitutions.py
│   └── ConstitutionEnforcer.py
├── injections/
│   ├── __init__.py
│   ├── SemanticFence.py
│   └── ToolConstraints.py
├── dependencies/
│   ├── __init__.py
│   ├── RAGContextInjector.py
│   └── KnowledgeRetriever.py
└── prompts/
    ├── __init__.py
    ├── UserIntentProcessor.py
    └── IntentExtractor.py
```

### Key Implementation Details

**Assembly Stage Composition:**
```python
@dataclass
class AssemblyPackage:
    s0_constitutions: List[SystemConstitution]
    i0_instructions: List[InstructionalMixin]
    d0_injections: List[SemanticFence]
    c0_dependencies: RAGContext
    u0_prompt: UserIntent
    signature: str  # HMAC-SHA256 of canonical JSON
```

**PTC Sandbox Flow:**
1. **Initialization**: Validate signed plan, verify tool budget, freeze state
2. **Execution**: Enforce tool contracts, universal write gateway, structured stdout
3. **Healing**: Confidence-tier escalation, remediation dispatch
4. **Synthesis**: Aggregate outputs, validate schema, emit transcript

**Healing Tier Selection:**
- **LOCAL_AGENT** (confidence ≥ 0.75): Fast local healing
- **QWEN_VLLM** (0.40 ≤ confidence < 0.75): Mid-tier escalation
- **GEMINI_2_5_PRO** (confidence < 0.40): High-tier escalation

## Success Criteria

### Phase Completion Metrics
- **Phase 1**: Assembly stage operational with 100% deterministic composition
- **Phase 2**: L0/L5 validation integrated with <100ms routing decisions
- **Phase 3**: PTC sandbox active with universal write gateway enforcement
- **Phase 4**: Meta-learning pipeline processing healing outcomes with pattern detection
- **Phase 5**: End-to-end four-bucket architecture with <5% failure rate

### Quality Gates
- All existing 190 agents remain functional
- New architecture passes comprehensive test suite
- Performance benchmarks meet or exceed current metrics
- Governance and compliance requirements satisfied

## Risk Mitigation

### Technical Risks
- **Complexity**: Incremental implementation with backward compatibility
- **Performance**: Comprehensive benchmarking and optimization
- **Integration**: Extensive testing and gradual rollout

### Operational Risks
- **Disruption**: Parallel development with feature flags
- **Training**: Documentation and knowledge transfer sessions
- **Monitoring**: Enhanced observability and alerting

## Conclusion

This implementation plan transforms the current agent ecosystem into a structured four-bucket L2 architecture that aligns with the technical specification. The phased approach minimizes risk while delivering incremental value, ultimately providing a more robust, scalable, and governable agentic system.

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

