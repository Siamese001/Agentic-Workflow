# ULTRA ZERO-LOSS AGENT DISCOVERY REPORT
## Full Repository Analysis - January 01, 2026

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Total Agents Discovered** | 356 |
| **Total .py Files Scanned** | 2,043 |
| **Detection Coverage** | 100% (zero-loss) |

### Layer Distribution

| Layer | Count | % |
|-------|-------|---|
| L0 | 23 | 6% |
| L1 | 39 | 10% |
| L2 | 55 | 15% |
| L3 | 56 | 15% |
| L4 | 20 | 5% |
| L5 | 49 | 13% |
| apps_lic | 47 | 13% |
| apps_rg | 34 | 9% |
| apps_shared | 4 | 1% |
| tests | 19 | 5% |
| misc | 10 | 2% |

### Capability Analysis

| Capability | Count | % |
|------------|-------|---|
| **Healing Included** | 191 | 53% |
| **Memory/State** | 55 | 15% |
| **Tools Integration** | 178 | 50% |
| **Subatomic Hops** | 57 | 16% |

### Testing Compliance

| Testing Type | Count | % |
|--------------|-------|---|
| **Self-Testing** | 50 | 14% |
| **Delegated** | 3 | 0% |
| **None** | 303 | 85% |

### Sovereignty Compliance

| Metric | Count | % |
|--------|-------|---|
| **PascalCase Compliant** | 355 | 99% |
| **MCP Hardened** | 100 | 28% |

---

## DETAILED AGENT TABLES BY LAYER

### L0 Layer (23 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| AgentCapability | - | Y | - | - | - | 57 | Defines the capability of an agent  |
| AgentRegistry | - | Y | - | - | - | 57 | Registry for managing agent capabil |
| AgentRole | Enum | Y | - | - | - | 57 | Functional roles for agents in the  |
| AgentSpec | - | Y | - | - | - | 57 | Specification for creating an agent |
| AgenticWorkflowError | Exception | - | - | - | - | 68 | Base exception for agentic workflow |
| AgenticWorkflowError | Exception | - | - | - | - | 27 | Base exception for agentic workflow |
| BiasAuditor | HealerMixin | - | - | Y | - | 74 | Lightweight Bias Detection for Cont |
| BootstrapAgent | HealerMixin, L0Delegation | Y | Y | Y | D | 137 | 
    Autonomous boot integrity agen |
| GapClosureArchitect | HealerMixin, Agent | - | - | Y | - | 103 | Gap Closure Architect agent for lea |
| GravityComplianceValidator | HealerMixin | - | - | Y | - | 52 | Brief description of functionality  |
| GuardianOrchestrator | HealerMixin, SelfDiagnosi | - | - | Y | - | 77 | 
    Sovereign orchestrator for all |
| HealingOrchestrator | HealerMixin, SelfDiagnosi | - | - | Y | - | 160 | 
    Sovereign healing engine orche |
| HygieneValidator | HealerMixin, MCPHardenedM | Y | - | Y | - | 144 | 
    Detects 'Rot' within the syste |
| L0DelegationMixin | - | Y | - | - | - | 111 | Mixin providing L0 delegation-only  |
| L0DelegationTestingMixin | - | - | - | - | D | 68 | 
    Phase 2: Canonical delegated t |
| MetricsWitness | HealerMixin, SelfDiagnosi | - | - | Y | - | 70 | 
    Sovereign witness that cross-e |
| SafeSystemCommandExecutor | HealerMixin, MCPHardenedM | Y | - | Y | - | 140 | 
    A secure system command execut |
| ScriptToAgentClassifier | HealerMixin, L0Delegation | - | - | Y | D | 245 | 
    Sovereign classifier for scrip |
| ScriptsPlanningOrchestrator | HealerMixin | - | - | Y | - | 119 | Orchestrator for planning script ex |
| SovereignFilesystemMcpClient | - | Y | - | - | - | 81 | Official Filesystem MCP client for  |
| SovereignGitKrakenMcpClient | - | Y | - | - | - | 88 | Official GitKraken MCP client for s |
| SystemCommandExecutor | HealerMixin, Protocol | Y | - | Y | - | 140 | 
    Protocol for safely executing  |
| WorkflowOrchestrator | HealerMixin, MCPHardenedM | Y | Y | Y | - | 94 | Workflow orchestrator with SDK inte |

### L1 Layer (39 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| AgentCapability | Enum | - | - | - | - | 14 | Standard agent capabilities. |
| AgentContract | BaseModel | - | - | - | - | 30 | Contract specification for an agent |
| AgentIdentity | - | Y | - | - | - | 52 | Cryptographically-verified agent id |
| AgentInfo | HealerMixin, MCPHardenedM | Y | - | Y | - | 52 | Simple agent information container  |
| AgentMessage | SovereignBaseModel | Y | - | - | - | 21 | 
    Sovereign-grade message used f |
| AgentMessage | SovereignBaseModel | - | - | - | - | 22 | Brief description of functionality  |
| AgentPlan | BaseModel | Y | - | - | - | 72 | Agent execution plan with reasoning |
| AgentPlan | BaseModel | Y | - | - | - | 92 | Agent execution plan with reasoning |
| AgentResponse | - | Y | - | - | - | 82 | Response from agent execution conta |
| AgentStatus | Enum | - | - | - | - | 14 | Agent operational status. |
| AgentThoughtProcess | BaseModel | Y | - | - | - | 72 | 
    Forces the agent to show its w |
| AgentThoughtProcess | BaseModel | Y | - | - | - | 92 | 
    Forces the agent to show its w |
| AsyncBlockingValidator | HealerMixin, CanonASTVali | Y | - | Y | - | 94 | 
    Key 31: Detects blocking calls |
| BareExceptValidator | HealerMixin, CanonASTVali | Y | - | Y | - | 94 | 
    Key 5: Detects bare except: st |
| CanonValidator | HealerMixin, MCPHardenedM | Y | Y | Y | - | 292 | 
    The L5 Meta-Learner that valid |
| CognitiveContractValidator | - | - | - | - | - | 257 | Validates cognitive contracts and e |
| ConcurrencyGuardian | HealerMixin | - | - | Y | - | 105 | 
    Manages concurrent operations  |
| DangerousBuiltinsValidator | HealerMixin, CanonASTVali | Y | - | Y | - | 94 | 
    Key 42: Detects dangerous buil |
| DebuggerValidator | HealerMixin, CanonASTVali | Y | - | Y | - | 94 | 
    Key 3: Detects breakpoint() an |
| DependencySentinel | HealerMixin, MCPHardenedM | Y | - | Y | - | 378 | 
    KEYS: 7 (Star Imports), 8 (Rel |
| DependencySentinelAgent | HealerMixin, MCPHardenedM | Y | Y | Y | - | 154 | 
    Guards the codebase against il |
| DummyAgentCard | HealerMixin | - | - | Y | - | 27 | TODO: Add docstring. |
| EmptyExceptValidator | HealerMixin, CanonASTVali | Y | - | Y | - | 94 | 
    Key 4: Detects empty except bl |
| EvalExecValidator | HealerMixin, CanonASTVali | Y | - | Y | - | 94 | 
    Key 6: Detects eval() and exec |
| ExternalHttpValidator | HealerMixin, CanonASTVali | Y | - | Y | - | 94 | 
    Key 23: Detects forbidden HTTP |
| GenerativeGuard | HealerMixin, MCPHardenedM | Y | - | Y | - | 301 | 
    KEYS: 45 (Dead Code/Runaway Ge |
| GovernanceAgent | HealerMixin, MCPHardenedM | Y | - | Y | - | 337 | 
    Enforces architectural governa |
| HealerAgent | HealerMixin, CanonBaseAge | Y | - | Y | - | 301 | 
    KEYS: 48 (Syntax Repair), 49 ( |
| IOrchestrator | HealerMixin, MCPHardenedM | Y | - | Y | - | 31 | Interface for the orchestrator (Ner |
| IOrchestrator | ABC | Y | - | - | - | 56 | Interface for the Orchestrator (Ner |
| IntelligentOrchestrator | HealerMixin | Y | - | Y | - | 74 | Orchestrates all validation agents  |
| MetaLearningAgent | HealerMixin | Y | - | Y | - | 109 | 
    Sovereign meta-learning engine |
| PrintStatementValidator | HealerMixin, CanonASTVali | Y | - | Y | - | 94 | 
    Key 2: Detects print() stateme |
| ReasoningRouter | HealerMixin | Y | - | Y | - | 121 | Routes tasks to appropriate reasoni |
| ReflectionAgent | HealerMixin, MCPHardenedM | Y | Y | Y | - | 137 | 
    Agent responsible for learning |
| ResidualAgentMessage | - | Y | - | - | - | 21 | 
    Lightweight runtime message fo |
| ResidualAgentMessage | - | Y | - | - | - | 82 | Message in agent conversation (Resi |
| SovereignCognitivePlane | HealerMixin, ICognitivePl | Y | - | Y | - | 52 | Sovereign cognitive plane with in-m |
| SystemArchitect | HealerMixin, CanonBaseAge | Y | - | Y | - | 301 | 
    KEYS: 40 (Metaclasses), 41 (De |

### L2 Layer (55 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| AgentPlan | BaseModel | Y | - | - | - | 320 | - |
| AutonomyMixin | - | - | - | - | - | 45 | - |
| BiasAuditor | - | - | - | - | - | 45 | Audits text for potential bias. |
| CanonAstValidator | NodeVisitor | - | - | - | - | 62 | 
    [L6 INFRASTRUCTURE] Base AST v |
| CodeDeduplicationAgent | HealerMixin | - | - | Y | S | 260 | 
    Batch agent for detecting and  |
| ContextAwareValidator | - | - | - | - | - | 74 | 
    Base class for intelligent val |
| ContextCuratorAgent | SubAtomicAgent | Y | - | Y | S | 197 | 
    The Context Curator - Prompt E |
| DeadCodeDetectorAgent | HealerMixin | - | - | Y | - | 230 | 
    Sovereign dead code auditor th |
| DeadlockDetector | HealerMixin | - | - | Y | - | 644 | ROLE: Deadlock Guardian. Detects po |
| DriftDetectorAgent | HealerMixin | - | - | Y | - | 26 | Detects files that have drifted out |
| DriftDetectorAgent | HealerMixin | - | - | Y | - | 13 | Naming/Compliance: Drift Detection |
| DynamicModelRouterAgent | SubAtomicAgent | Y | - | Y | S | 248 | 
    The Throttler - Dynamic Model  |
| GitAgent | HealerMixin, MCPHardenedM | Y | - | Y | S | 186 | 
    Agent for managing git operati |
| GlobalComplianceAggregatorAgent | HealerMixin | - | - | Y | - | 14 | Naming/Compliance: Global Complianc |
| HierarchyHealer | - | - | - | - | - | 27 | 
    [L3 AGENT] The Structural Surg |
| ImportHealer | - | - | - | - | - | 101 | 
    Automatically fixes import sta |
| IntegrityGateExecutor | HealerMixin | - | - | Y | - | 232 | Brief description of functionality  |
| IntegrityGateExecutor | HealerMixin | - | - | Y | - | 111 | Brief description of functionality  |
| IntegrityGateExecutor | HealerMixin | - | - | Y | - | 206 | Brief description of functionality  |
| IntegrityGateExecutorAgent | HealerMixin | - | - | Y | S | 211 | Executor for integrity gate validat |
| L2SelfTestingMixin | MCPHardenedMixin, Subatom | Y | - | Y | S | 54 | 
    Alias for SubatomicTestingMixi |
| MemoryArchitectAgent | MCPHardenedMixin, SubAtom | Y | Y | Y | S | 244 | 
    Autonomous Knowledge Distillat |
| MemoryLeakDetector | HealerMixin | - | - | Y | - | 644 | ROLE: Memory Guardian. Detects and  |
| NamingAgent | HealerMixin, MCPHardenedM | Y | Y | Y | - | 872 | 
    Autonomous agent for naming la |
| NamingLawHealerAgent | HealerMixin | Y | - | Y | - | 135 | 
    L1 Cognition: High-Signal Nami |
| NamingNormalizationAgent | HealerMixin | - | - | Y | - | 83 | 
    Normalizes filenames and publi |
| OmniContext | SubAtomicAgent | Y | - | Y | S | 52 | 
    ROLE: Global Architectural Con |
| PeerIntelligenceAuditor | HealerMixin | - | - | Y | - | 111 | 
    K.2.5 - Multi-Hop RAG Analysis |
| ReflectionAgent | SubAtomicAgent | Y | - | Y | S | 67 | 
    ROLE: Consolidation and self-c |
| SafetyExecutor | HealerMixin | - | - | Y | - | 24 | 
    Executes resume safety validat |
| SherlockAgent | SubAtomicAgent | Y | - | Y | S | 132 | 
    ROLE: Root Cause Analysis. Tri |
| SovereignActionPlaneAgent | HealerMixin, MCPHardenedM | Y | - | Y | S | 194 | Sovereign action plane with Toolsmi |
| SovereignDeepWikiClient | - | Y | Y | - | - | 122 | 
    DeepWiki MCP Client for L6 Obs |
| SovereignFetchClient | MCPHardenedMixin | Y | - | - | - | 41 | Ultra-hardened Fetch MCP client — e |
| SovereignFetchMcpClient | - | Y | - | - | - | 129 | 
    Fetch MCP Client for sanitized |
| SovereignFigmaClient | - | Y | - | - | - | 77 | Ultra-hardened Figma client — elimi |
| SovereignGitClient | - | - | - | - | - | 93 | Sovereign Git client - audit + safe |
| SovereignHttpClient | - | - | Y | - | - | 114 | Sovereign HTTP client - audit + saf |
| SovereignPineconeClient | - | - | Y | - | - | 84 | Sovereign Pinecone client - audit + |
| SovereignPineconeStore | - | - | Y | - | - | 60 | Sovereign wrapper for Pinecone serv |
| SovereignPlaywrightMcpClient | - | Y | - | - | - | 126 | 
    Playwright MCP Client for visu |
| SovereignRedisClient | - | - | Y | - | - | 109 | Sovereign Redis client - audit + sa |
| SovereignRedisOrchestrator | HealerMixin, MCPHardenedM | Y | Y | Y | - | 87 | Brief description of functionality  |
| SovereignRedisOrchestrator | HealerMixin, MCPHardenedM | Y | Y | Y | - | 87 | Brief description of functionality  |
| SovereigntyAuditor | HealerMixin, MCPHardenedM | Y | Y | Y | - | 108 | 
    Sovereignty Audit Engine for M |
| SprawlInspector | HealerMixin | - | - | Y | - | 49 | Brief description of functionality  |
| StrategicPlannerAgent | SubAtomicAgent | Y | - | Y | S | 67 | 
    ROLE: High-level strategist.
  |
| StructuralEngineerAgent | CanonBaseAgent | Y | - | Y | S | 142 | 
    Structural Engineer validates  |
| SubatomicTestingMixin | MCPHardenedMixin | Y | - | Y | - | 299 | Mixin providing L2 subatomic testin |
| SubatomicTestingMixin | - | Y | - | Y | S | 54 | 
    Phase 1: Canonical self-testin |
| SystemArchitect | CanonBaseAgent | Y | - | Y | S | 59 | 
    System Architect validates cor |
| SystemArchitectAgent | CanonBaseAgent | Y | - | Y | S | 52 | 
    System Architect validates cor |
| TestPilotAgent | SubAtomicAgent | Y | - | Y | S | 132 | 
    ROLE: Integration Guardian. Ru |
| ToolsmithAgent | SubAtomicAgent | Y | - | Y | S | 132 | 
    ROLE: Dynamic Tool Forger.
    |
| ToolsmithAgent | HealerMixin, MCPHardenedM | Y | - | Y | - | 204 | 
    Creates and manages tools dyna |

### L3 Layer (56 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| AgentFactory | HealerMixin | Y | - | Y | - | 77 | 
    Centralized factory for sovere |
| AgentGym | HealerMixin | - | - | Y | - | 131 | Agent Gym for self-evolution and be |
| AgentPermissionManager | HealerMixin | Y | - | Y | - | 86 | Manages agent permissions with Cont |
| AgentRegistry | HealerMixin | - | - | Y | - | 350 | Mock AgentRegistry for type hinting |
| AgentRegistryValidatorAgent | HealerMixin | - | - | Y | S | 72 | 
    L3 Orchestration: Agent Regist |
| AgentRole | Enum | - | - | - | - | 350 | Brief description of functionality  |
| AutonomicMonitor | HealerMixin | - | - | Y | - | 93 | Autonomic immune system for agent h |
| BenchmarkingAgent | HealerMixin | Y | - | Y | - | 229 | 
    Measures and tracks performanc |
| CachedOrchestrator | HealerMixin, MCPHardenedM | Y | Y | Y | - | 59 | 
    Sovereign L3 orchestration bas |
| ContextCurator | HealerMixin | Y | - | Y | - | 120 | Curates and manages the context win |
| CoordinateObservabilityOperationsAg | HealerMixin | - | - | Y | - | 56 | Orchestrator for operations domain. |
| DAGManager | HealerMixin | - | - | Y | - | 411 | Manages the dynamic DAG with mutati |
| DAGMutator | HealerMixin | - | - | Y | - | 411 | Handles the actual graph mutations. |
| DagEngineAgent | HealerMixin | - | - | Y | S | 212 | Lightweight DAG engine for workflow |
| DagExecutor | HealerMixin | - | - | Y | - | 41 | Executes Directed Acyclic Graphs of |
| DagManager | HealerMixin | - | - | Y | - | 350 | Mock DAGManager for type hinting. |
| DagRuntimeInspector | HealerMixin | - | - | Y | - | 30 | Diagnostics engine for inspection d |
| DeadlockDetector | HealerMixin | - | - | Y | - | 192 | 
    Detects potential deadlocks in |
| DispatchOutreachToolsAgent | HealerMixin, MCPHardenedM | Y | - | Y | S | 26 | Executor for outreach domain. |
| DispatchResumeToolsAgent | HealerMixin, MCPHardenedM | Y | - | Y | S | 67 | Executor for resume domain with Tit |
| HallucinationDetector | HealerMixin | - | - | Y | - | 13 | Stub implementation of hallucinatio |
| HardenedWorkflowOrchestrator | HealerMixin | - | - | Y | - | 22 | 
    Thin wrapper for Hardened Work |
| HierarchyEnforcerAgent | HealerMixin | - | - | Y | - | 149 | 
    Enforces the canonical L4 hier |
| IOrchestrator | HealerMixin, ABC | Y | - | Y | - | 111 | Interface for the Orchestrator (Ner |
| L3SubatomicTestingMixin | MCPHardenedMixin | Y | - | Y | S | 133 | Mixin providing L3 subatomic testin |
| McpRouter | HealerMixin, MCPHardenedM | Y | Y | Y | - | 52 | 
    L3 Orchestration switchboard:  |
| MemoryLeakDetector | HealerMixin | - | - | Y | - | 159 | 
    Detects memory leaks in the ag |
| MetaLearningAgent | HealerMixin, SelfDiagnosi | - | - | Y | S | 122 | 
    Sovereign meta-learning agent  |
| MetricsAgent | HealerMixin, MCPHardenedM | Y | Y | Y | - | 171 | 
    MetricsAgent: Sovereign quanti |
| MockAgent | HealerMixin | Y | - | Y | S | 879 | - |
| ModelRouter | HealerMixin | - | - | Y | - | 86 | Dynamic model router for cost-optim |
| NervousSystemAgent | HealerMixin | Y | - | Y | S | 879 | Core orchestrator that coordinates  |
| NervousSystemPhaseOrchestrator | HealerMixin | Y | - | Y | - | 879 | Orchestrates the execution of all p |
| PredictiveCostAuditorAgent | SubAtomicAgent | Y | - | Y | S | 212 | 
    The Efficiency Guard - Predict |
| ReportingAgent | HealerMixin, MCPHardenedM | Y | - | Y | - | 82 | 
    Autonomous diagnostic agent fo |
| ResumeOrchestrator | HealerMixin | - | - | Y | - | 38 | Orchestrate the multi-hop resume ge |
| SelfRecoveringOrchestrator | HealerMixin | - | - | Y | - | 280 | 
    Orchestrator that automaticall |
| SemanticGatekeeperAgent | HealerMixin | - | - | Y | S | 54 | 
    Gatekeeper that controls agent |
| SemanticTerritoryMapperAgent | HealerMixin | - | - | Y | S | 13 | L3 Orchestration: Semantic Territor |
| SemanticTerritoryMapperAgent | HealerMixin, MCPHardenedM | Y | Y | Y | S | 138 | 
    The Intelligent Brain that map |
| SignatureVerifierAgent | HealerMixin | - | - | Y | - | 29 | function class for inspection domai |
| SovereignDeepWikiClient | - | Y | Y | - | - | 122 | 
    DeepWiki MCP Client for L6 Obs |
| SovereignMcpRouter | HealerMixin, MCPHardenedM | Y | Y | Y | - | 139 | Ultra-hardened L3 MCP switchboard — |
| SovereignRagOrchestrator | HealerMixin | - | - | Y | - | 107 | Brief description of functionality  |
| SubatomicHop | HealerMixin | - | - | Y | - | 350 | Mock SubatomicHop for type hinting. |
| SubatomicHopAgent | HealerMixin | Y | - | Y | S | 141 | 
    Sovereign SubatomicHop with De |
| SubatomicOrchestrator | HealerMixin | - | - | Y | - | 350 | Implementation for SubatomicOrchest |
| TaskMonitor | HealerMixin | - | - | Y | - | 192 | Monitors a single asyncio Task. |
| TelemetryAgent | HealerMixin | - | - | Y | - | 147 | 
    Autonomous telemetry emission  |
| TerritoryHealerAgent | HealerMixin | - | - | Y | S | 13 | L3 Orchestration: Territory Healing |
| TerritoryHealerAgent | HealerMixin, MCPHardenedM | Y | Y | Y | S | 197 | 
    Enforces exhaustive territory  |
| TestPilotAgent | HealerMixin, MCPHardenedM | Y | - | Y | S | 191 | 
    TestPilot agent with property- |
| TokenBudgetInspector | HealerMixin | - | - | Y | - | 30 | Diagnostics engine for inspection d |
| TracingAgent | HealerMixin | - | - | Y | - | 254 | 
    Autonomous distributed tracing |
| TrackObservabilityCostAgent | HealerMixin | - | - | Y | - | 27 | function class for standard domain. |
| WorkflowBlueprint | HealerMixin | - | - | Y | - | 350 | Mock WorkflowBlueprint for type hin |

### L4 Layer (20 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| AtomicBlackboard | MCPHardenedMixin | Y | Y | - | - | 223 | 
    Thread-safe blackboard for man |
| AutonomousCheckpointManagerAgent | HealerMixin | - | - | Y | S | 203 | 
    Manages state checkpoints with |
| AutonomousCheckpointManagerAgent | HealerMixin | - | - | Y | S | 203 | 
    Manages state checkpoints with |
| AutonomousStateGuardianAgent | HealerMixin | Y | - | Y | S | 159 | 
    L4 State Guardian that autonom |
| AutonomousStateGuardianAgent | HealerMixin | Y | - | Y | S | 159 | 
    L4 State Guardian that autonom |
| CachedStateLedger | MCPHardenedMixin | Y | Y | - | - | 103 | 
    Sovereign L4 state base — Redi |
| CanonValidator | HealerMixin, MCPHardenedM | Y | Y | Y | - | 203 | 
    The Gatekeeper logic that enfo |
| L4SubatomicTestingMixin | MCPHardenedMixin | Y | - | Y | S | 147 | Mixin providing L4 subatomic testin |
| PineconeSovereignAgent | HealerMixin, MCPHardenedM | Y | Y | Y | S | 260 | 
    Sovereign Pinecone controller  |
| PineconeSovereignAgent | HealerMixin, MCPHardenedM | Y | Y | Y | S | 15 | Mock Pinecone Sovereign Agent. |
| RedisDistributedLock | MCPHardenedMixin | Y | Y | - | - | 447 | 
    Redis-based distributed lock f |
| RedisHotCache | MCPHardenedMixin | Y | Y | - | - | 447 | 
    Redis-based hot cache with loc |
| RedisSovereignAgent | HealerMixin, MCPHardenedM | Y | Y | Y | S | 72 | 
    Sovereign Redis controller — h |
| SchemaEvolverAgent | SubAtomicAgent | Y | - | Y | S | 203 | 
    The Structural Guard - Schema  |
| SovereignGraphClient | - | Y | Y | - | - | 138 | 
    Client for the Knowledge Graph |
| SovereignPineconeMcpClient | MCPHardenedMixin | Y | Y | - | - | 109 | 
    Official Pinecone MCP client — |
| SovereignPineconeStoreAgent | HealerMixin, MCPHardenedM | Y | Y | Y | S | 103 | 
    ADAPTER: Legacy Interface -> N |
| SovereignRedisMcpClient | MCPHardenedMixin | Y | Y | - | - | 91 | Official Redis MCP client for sover |
| SovereignSemanticCache | MCPHardenedMixin | Y | Y | - | - | 81 | Ultra-hardened hybrid semantic cach |
| SubAtomicRegistryAgent | HealerMixin, MCPHardenedM | Y | Y | Y | S | 113 | 
    Sovereign method registry — li |

### L5 Layer (49 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| AutonomousThreatEvolutionAgent | HealerMixin | - | - | Y | - | 76 | L5: Self-healing security agent |
| AutonomousThreatEvolutionAgent | HealerMixin | - | - | Y | - | 76 | L5: Self-healing security agent |
| BaseAgent | HealerMixin | - | - | Y | - | 167 | Stub for BaseAgent - TODO: Replace  |
| BiasAuditor | HealerMixin | - | - | Y | - | 148 | Lightweight Bias Detection for Cont |
| BiasDetectorAgent | HealerMixin, BaseAgent | - | - | Y | - | 167 | Runs local bias detection with dyna |
| CodeFormatterAgent | HealerMixin, MCPHardenedM | Y | - | Y | - | 35 | 
    Atomic agent: Enforces consist |
| CodeSSOTEnforcerAgent | HealerMixin, MCPHardenedM | Y | - | Y | - | 88 | 
    Ultra high-signal code-level S |
| ComplianceOrchestrator | HealerMixin, MCPHardenedM | Y | Y | Y | - | 521 | 
    L5 Sovereign Compliance Orches |
| ConstitutionalReviewerAgent | HealerMixin, BaseAgent | - | - | Y | - | 167 | Performs final constitutional revie |
| DependencyPruningAgent | HealerMixin, MCPHardenedM | Y | - | Y | - | 72 | 
    Batch agent: Detects and remov |
| DocstringComplianceAgent | HealerMixin | - | - | Y | - | 61 | 
    Ensures public functions, clas |
| DuplicateCodeDetectorAgent | HealerMixin | - | - | Y | - | 90 | 
    Batch agent: Detects exact dup |
| FileCleanupAgent | HealerMixin | - | - | Y | - | 129 | 
    Batch agent: Identifies and re |
| FilenameUniquenessGuardianAgent | HealerMixin, MCPHardenedM | Y | Y | Y | - | 108 | 
    Batch agent that enforces uniq |
| FilesystemAgent | HealerMixin | - | - | Y | - | 199 | 
    Autonomous agent for physical  |
| GitHygieneAgent | HealerMixin, MCPHardenedM | Y | - | Y | - | 96 | 
    Batch agent: Enforces Git repo |
| GovernanceAgent | HealerMixin, AutonomyMixi | - | - | Y | - | 126 | 
    Sovereign governance agent tha |
| GravityEnforcerAgent | HealerMixin, CachedSafety | - | - | Y | - | 88 | 
    The "Neural Link" stabilizer t |
| GravityLeakRepairAgent | HealerMixin | - | - | Y | - | 58 | 
    Converts forbidden static impo |
| HallucinationHunterAgent | SubAtomicAgent | Y | - | Y | S | 291 | 
    The Hallucination Hunter - Gro |
| HealValidator | HealerMixin, MCPHardenedM | Y | - | Y | - | 229 | 
    Multi-stage validator for LLM- |
| HealerAgent | HealerMixin, MCPHardenedM | Y | - | Y | - | 787 | 
    Autonomous Conductor for struc |
| HierarchyAgent | HealerMixin, MCPHardenedM | Y | Y | Y | - | 340 | 
    Autonomous agent for hierarchi |
| HierarchyHealer | HealerMixin, MCPHardenedM | Y | - | Y | - | 229 | 
    L5 Hierarchy Healer Agent
     |
| HygieneGuardianAgent | MCPHardenedMixin, CanonBa | Y | - | Y | S | 51 | 
    Validates Canon Key 45: Shared |
| ImportAgent | HealerMixin | - | - | Y | - | 212 | 
    Autonomous agent for import co |
| InferenceTypeHintAgent | HealerMixin | - | - | Y | - | 71 | 
    Uses LLM inference to add accu |
| InputValidator | HealerMixin | - | - | Y | - | 289 | Validates input data against schema |
| L5IntegrityGateExecutorAgent | HealerMixin | - | - | Y | - | 399 | 
    L5+ Integrity Gate Executor wi |
| LocationAgent | HealerMixin, MCPHardenedM | Y | - | Y | - | 186 | 
    Autonomous agent responsible f |
| MCPGuardianAgent | HealerMixin, MCPHardenedM | Y | Y | Y | - | 140 | 
    L5 Safety Guardian for MCP int |
| MCPHardenedMixin | - | Y | Y | - | - | 144 | 
    Mixin providing hardened MCP o |
| MethodChangeDetector | HealerMixin, MCPHardenedM | Y | Y | Y | - | 316 | Detects method changes between two  |
| NeuralAutoImmuneAgent | HealerMixin, MCPHardenedM | Y | Y | Y | - | 12 | - |
| PIISanitizerAgent | HealerMixin, BaseAgent | - | - | Y | - | 167 | Performs local PII detection using  |
| PascalSovereigntyEnforcerAgent | MCPHardenedMixin, CanonBa | Y | - | Y | S | 176 | L5 Safety agent — enforces PascalCa |
| PromptInjectionDetectorAgent | HealerMixin, BaseAgent | - | - | Y | - | 167 | Detects prompt-injection attacks. |
| RedSentinel | HealerMixin | Y | - | Y | - | 127 | 
    Active defense system that gen |
| RedTeamAgent | HealerMixin | - | - | Y | - | 83 | 
    Sovereign red-teaming agent fo |
| RegressionOracleAgent | SubAtomicAgent | Y | Y | Y | S | 316 | 
    The Regression Oracle - Automa |
| SafetyInspector | HealerMixin, MCPHardenedM | Y | - | Y | - | 165 | 
    L5 Safety Inspector with Socra |
| SelfUpdatingSafetyEngineAgent | HealerMixin, MCPHardenedM | Y | - | Y | - | 220 | 
    Safety engine that learns and  |
| SovereignLlmRouterMcpClient | - | Y | - | - | - | 40 | Official LLM Router MCP client for  |
| TerritoryHealerAgent | HealerMixin, MCPHardenedM | Y | Y | Y | - | 168 | 
    Enforces exhaustive territory  |
| TestCoverageGuardianAgent | HealerMixin, MCPHardenedM | Y | - | Y | - | 307 | 
    Ultimate verification agent: E |
| TestSovereigntyAgent | MCPHardenedMixin, CanonBa | Y | - | Y | S | 162 | L5 specialist — advanced sovereign  |
| TypeHintEnforcementAgent | HealerMixin | Y | - | Y | - | 85 | 
    Ensures public functions, meth |
| TypeHintFixer | HealerMixin, NodeTransfor | Y | - | Y | - | 85 | 
    AST transformer that adds Miss |
| UnusedCleanupAgent | HealerMixin, MCPHardenedM | Y | - | Y | - | 33 | 
    Atomic agent: Removes unused i |

### apps_lic Layer (47 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| ASCIIEnforcer | - | - | - | - | - | 411 | 
    Enforce ASCII-only characters  |
| AgentStatus | Enum | Y | - | - | - | 122 | Agent execution status |
| AgentStatus | Enum | Y | - | - | - | 135 | Agent execution status |
| BaseAgent | - | - | - | - | - | 640 | Stub for BaseAgent - TODO: Replace  |
| CampaignBalanceAgent | OutreachAgent | - | - | - | - | 229 | Ensures campaign elements are balan |
| CampaignPlanner | OutreachAgent | - | - | - | - | 229 | Strategic campaign planning agent. |
| ContactValidatorAgent | OutreachAgent | - | - | - | - | 229 | Validates contact information. |
| ContentCleanlinessValidator | - | - | - | - | - | 411 | 
    Forbidden verbs and weak langu |
| DeliverabilityAgent | OutreachAgent | - | - | - | - | 229 | Checks email deliverability factors |
| FailureClassifier | Enum | Y | - | - | - | 122 | 
    Classifies S6 validation failu |
| FailureClassifier | Enum | Y | - | - | - | 135 | 
    Classifies S6 validation failu |
| HOP1ProfileAnalysisAgent | MCPHardenedMixin | Y | - | - | - | 369 | 
    v13.1: HOP-1 - Profile Analysi |
| HOP2ResearchAgent | MCPHardenedMixin | Y | - | - | - | 760 | 
    v13.1: Research Agent - Vector |
| HOP3SenderGroundingAgent | MCPHardenedMixin | Y | - | - | - | 369 | 
    v13.1: HOP-3 - Sender Groundin |
| HOP4RoutingAgent | MCPHardenedMixin | Y | - | - | - | 369 | 
    v13.1: HOP-4 - Routing Decisio |
| HOP5GenerationAgent | MCPHardenedMixin | Y | - | - | - | 760 | 
    v13.1: Generation Agent - N-ca |
| HOP6ValidationAgent | MCPHardenedMixin | Y | - | - | - | 760 | 
    v13.1: Validation Agent - Rule |
| HOP7GateDecisionAgent | MCPHardenedMixin | Y | - | - | - | 369 | 
    v13.1: HOP-7 - Gate Decision A |
| HOP8QAReportAgent | MCPHardenedMixin | Y | - | - | - | 760 | 
    v13.1: QA Report Agent - Persi |
| HOPOrchestrator | - | Y | - | - | - | 760 | 
    v13.0: HOP-based Workflow Orch |
| HOPOrchestrator | - | Y | - | - | - | 369 | 
    v13.0: Example orchestrator sh |
| IntelligenceLibrarian | MCPHardenedMixin | Y | - | - | - | 350 | 
    v13.1: Offline research agent  |
| InternalAgent | - | - | - | - | - | 640 | 
    v12.0: UPGRADED to primary int |
| LeadQualityAgent | OutreachAgent | - | - | - | - | 229 | Validates and scores lead quality. |
| MessageComplianceAgent | OutreachAgent | - | - | - | - | 229 | Ensures message compliance with reg |
| MessageDiversityValidator | - | - | - | - | - | 411 | 
    Prevent repetitive messages us |
| OrganizationAgent | - | - | - | - | - | 640 | 
    v12.0: DEMOTED to secondary fa |
| OutreachAgent | ABC | - | - | - | - | 33 | 
    Abstract base class for all ou |
| OutreachAgentFactory | - | - | - | - | - | 293 | Factory for creating outreach agent |
| OutreachCapabilityMonitor | - | - | - | - | - | 348 | 
    Monitors outreach agent capabi |
| OutreachHealingOrchestrator | - | - | - | - | - | 293 | Orchestrates the complete self-heal |
| OutreachLearningAgent | OutreachAgent | - | - | - | - | 215 | 
    Learning agent for outreach ca |
| OutreachPhase5Orchestrator | HealerMixin | - | - | Y | - | 227 | 
    Orchestrates Phase 5 observabi |
| OutreachProactiveAgent | OutreachAgent | - | - | - | - | 348 | 
    Agent that proactively identif |
| OutreachReflectionAgent | OutreachAgent | - | - | - | - | 229 | Reflects on execution and suggests  |
| OutreachSignalRouter | - | - | - | - | - | 293 | Routes signals to appropriate agent |
| OutreachTestPilot | OutreachAgent | - | - | - | - | 229 | Runs validation tests on the campai |
| OutreachValidationExecutor | ValidationGateExecutor | - | - | - | - | 259 | Extended validation executor for ou |
| PlaceholderDetector | - | - | - | - | - | 411 | 
    Comprehensive placeholder dete |
| RecipientAgent | - | - | - | - | - | 640 | 
    v12.0: DEMOTED to secondary fa |
| S2_SupervisorAgent | - | - | - | - | - | 640 | 
    v12.0: Updated coordination lo |
| TemplateOptimizer | OutreachAgent | - | - | - | - | 229 | Optimizes message templates for eng |
| TestContactValidatorAgent | - | - | - | - | - | 254 | Tests for ContactValidatorAgent. |
| TestLeadQualityAgent | - | - | - | - | - | 254 | Tests for LeadQualityAgent. |
| TestMessageComplianceAgent | - | - | - | - | - | 254 | Tests for MessageComplianceAgent. |
| TestOutreachProactiveAgent | - | - | - | - | - | 254 | Tests for OutreachProactiveAgent. |
| ValidationAgent | - | - | - | - | - | 411 | 
    NEW v11.6: Comprehensive valid |

### apps_rg Layer (34 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| ATSCompatibilityAgent | ResumeAgent | - | - | - | - | 418 | 
    Validates ATS (Applicant Track |
| AgentFactory | - | - | - | - | - | 334 | Factory for creating agent instance |
| BrandComplianceAgent | ResumeAgent | - | - | - | - | 418 | 
    Ensures brand voice and profes |
| CapabilityMonitor | - | - | - | - | - | 331 | 
    Monitors agent capabilities an |
| ContentQualityAgent | ResumeAgent | - | - | - | - | 418 | 
    Validates resume content quali |
| ConvergenceDetector | - | - | - | - | - | 334 | Detects when the system has converg |
| FactCheckAgent | ResumeAgent | - | - | - | - | 418 | 
    Verifies claims against user p |
| HealingOrchestrator | - | - | - | - | - | 334 | Orchestrates the complete self-heal |
| Phase4Orchestrator | - | - | - | - | - | 607 | 
    Orchestrates all Phase 4 compo |
| Phase6Orchestrator | - | Y | - | - | - | 578 | 
    Orchestrates all Phase 6 intel |
| Phase7Orchestrator | - | Y | - | - | - | 560 | 
    Orchestrates all Phase 7 gover |
| ProactiveAgent | ResumeAgent | - | - | - | - | 331 | 
    Agent that proactively identif |
| ReflectionAgent | ResumeAgent | - | - | - | - | 418 | 
    Learns from execution and reco |
| ResumeAgent | ABC | - | - | - | - | 49 | 
    Base class for all resume gene |
| ResumeLearningAgent | - | - | Y | - | - | 527 | 
    Agent that combines all Phase  |
| ResumeOrchestrator | - | - | - | - | - | 38 | Orchestrate the multi-hop resume ge |
| SectionBalanceAgent | ResumeAgent | - | - | - | - | 418 | 
    Ensures proper section balance |
| SignalRouter | - | - | - | - | - | 334 | Routes signals to appropriate agent |
| StrategicPlanner | ResumeAgent | - | - | - | - | 418 | 
    Plans execution strategy based |
| StrictDocEnforcer | - | Y | - | - | - | 560 | 
    Enforces type contract complia |
| TemplateOptimizer | ResumeAgent | - | - | - | - | 418 | 
    Optimizes template selection b |
| TestATSCompatibilityAgent | - | - | - | - | - | 273 | Tests for ATSCompatibilityAgent. |
| TestAgentCoordination | - | - | - | - | - | 218 | Tests for multi-agent coordination. |
| TestAgentFactory | - | - | - | - | - | 238 | Tests for AgentFactory class. |
| TestBrandComplianceAgent | - | - | - | - | - | 273 | Tests for BrandComplianceAgent. |
| TestContentQualityAgent | - | - | - | - | - | 273 | Tests for ContentQualityAgent. |
| TestFactCheckAgent | - | - | - | - | - | 273 | Tests for FactCheckAgent. |
| TestProactiveAgent | - | - | - | - | - | 269 | Tests for ProactiveAgent. |
| TestReflectionAgent | - | - | - | - | - | 273 | Tests for ReflectionAgent. |
| TestResilientMutatorWithAgents | - | - | - | - | - | 144 | Integration tests for ResilientMuta |
| TestResumeLearningAgent | - | - | Y | - | - | 322 | Tests for ResumeLearningAgent class |
| TestResumeLearningAgentIntegration | - | - | - | - | - | 243 | Integration tests for ResumeLearnin |
| TestSectionBalanceAgent | - | - | - | - | - | 273 | Tests for SectionBalanceAgent. |
| UnifiedOrchestrator | - | Y | - | - | - | 578 | 
    Multi-phase execution orchestr |

### apps_shared Layer (4 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| BaseTaskExecutor | HealerMixin | - | - | Y | - | 99 | 
    Base class for task execution  |
| CanonBaseAgentInterface | ABC | - | - | - | - | 14 | - |
| CanonBaseAgentInterfaceImpl | ABC | - | - | - | - | 14 | Sovereign interface for all canon a |
| StateValidator | HealerMixin, MCPHardenedM | Y | - | Y | - | 288 | 
    Validates state files against  |

### tests Layer (19 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| TestAgentDiscovery | - | Y | - | - | - | 123 | E2E tests for agent discovery and r |
| TestAgentFileValidation | - | Y | - | - | - | 201 | Test validation of Agent files. |
| TestAgentHierarchy | - | Y | - | - | - | 126 | Test agent hierarchy and inheritanc |
| TestAgentRegistry | - | Y | Y | - | - | 280 | Test AGENT_REGISTRY from structure_ |
| TestCodeDeduplicationAgent | TestCase | Y | - | - | - | 134 | Test suite for L2 CodeDeduplication |
| TestDuplicateCodeDetectorAgent | TestCase | Y | - | - | - | 134 | Test suite for L5 DuplicateCodeDete |
| TestFileCleanupAgent | TestCase | - | - | - | - | 151 | Test FileCleanupAgent functionality |
| TestHealerAgentASTDiff | TestCase | - | - | - | - | 126 | Test AST-based diff application for |
| TestHealerAgentIntegration | TestCase | - | - | - | - | 126 | Integration tests for AST-based hea |
| TestHealerAgentPerformance | TestCase | - | - | - | - | 126 | Performance tests for AST operation |
| TestL0MaintenanceAgents | - | Y | Y | - | - | 280 | L0 Maintenance Layer: Scripts, logs |
| TestL1CognitionAgents | - | Y | Y | - | - | 280 | L1 Cognition Layer: Thought engine, |
| TestL2ExecutionAgents | - | Y | Y | - | - | 280 | L2 Execution Layer: Tool registry,  |
| TestL3OrchestrationAgents | - | Y | Y | - | - | 280 | L3 Orchestration Layer: Workflow en |
| TestL4StateAgents | - | Y | Y | - | - | 280 | L4 State Layer: Validation context, |
| TestL5SafetyAgents | - | Y | Y | - | - | 280 | L5 Safety Layer: Guardrails, valida |
| TestNamingAgentFallback | TestCase | - | - | - | - | 86 | Test fallback behavior when tree-si |
| TestNamingAgentPerformance | TestCase | - | - | - | - | 86 | Test performance improvements with  |
| TestNamingAgentTreeSitter | TestCase | - | - | - | - | 86 | Test tree-sitter multi-language sym |

### misc Layer (10 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| AgentInfo | - | - | - | - | - | 357 | Information about a discovered agen |
| AgentInfo | - | - | - | - | - | 273 | - |
| AgentValidation | - | Y | - | - | - | 294 | Validation results for a single age |
| MultiProviderRouter | - | - | - | - | - | 328 | - |
| MultiProviderRouter | - | Y | - | - | - | 468 | Production router with intelligent  |
| NonConformingAgentFinder | NodeVisitor | - | - | - | - | 103 | - |
| Phase5Validator | - | Y | - | - | - | 294 | Full system validation for ultra ze |
| SystemValidator | - | Y | Y | - | - | 204 | Full system validation for sovereig |
| TalentIntelligenceAgent | - | - | - | - | - | 328 | Production agent for talent intelli |
| WorkflowOrchestrator | - | - | - | - | - | 328 | Orchestrates the complete agentic w |

---

## COMPLIANCE HIGHLIGHTS

### Non-Compliant Agents (L2-L4 without Self-Testing)

**Count: 86**

- `AgentPlan` (L2) - subatomic_hop_BROKEN.py
- `AutonomyMixin` (L2) - autonomy_mixin.py
- `BiasAuditor` (L2) - bias_auditor.py
- `CanonAstValidator` (L2) - ast_validator.py
- `ContextAwareValidator` (L2) - context_aware_validator.py
- `DeadCodeDetectorAgent` (L2) - DeadCodeDetectorAgent.py
- `DeadlockDetector` (L2) - concurrency.py
- `DriftDetectorAgent` (L2) - DriftDetectionDriftDetectorAgent.py
- `DriftDetectorAgent` (L2) - DriftDetectorAgent.py
- `GlobalComplianceAggregatorAgent` (L2) - GlobalComplianceAggregatorAgent.py
- `HierarchyHealer` (L2) - hierarchy_healer.py
- `ImportHealer` (L2) - import_healer.py
- `IntegrityGateExecutor` (L2) - executive_title_composer.py
- `IntegrityGateExecutor` (L2) - peer_intelligence_auditor_impl.py
- `IntegrityGateExecutor` (L2) - section_scope_integrator.py
- `MemoryLeakDetector` (L2) - concurrency.py
- `NamingAgent` (L2) - NamingAgent.py
- `NamingLawHealerAgent` (L2) - NamingLawHealerAgent.py
- `NamingNormalizationAgent` (L2) - NamingNormalizationAgent.py
- `PeerIntelligenceAuditor` (L2) - peer_intelligence_auditor_impl.py
- ... and 66 more

### L0 Agents Without Delegation

**Count: 20**

- `AgentCapability` - Defines the capability of an agent role.
- `AgentRegistry` - Registry for managing agent capabilities and speci
- `AgentRole` - Functional roles for agents in the system.
- `AgentSpec` - Specification for creating an agent instance.
- `AgenticWorkflowError` - Base exception for agentic workflow errors at L0.
- `AgenticWorkflowError` - Base exception for agentic workflow.
- `BiasAuditor` - Lightweight Bias Detection for Content Quality.

 
- `GapClosureArchitect` - Gap Closure Architect agent for leadership compete
- `GravityComplianceValidator` - Brief description of functionality and purpose.
- `GuardianOrchestrator` - 
    Sovereign orchestrator for all available L0 g
- `HealingOrchestrator` - 
    Sovereign healing engine orchestrator.
    Co
- `HygieneValidator` - 
    Detects 'Rot' within the system:
    1. Dead 
- `L0DelegationMixin` - Mixin providing L0 delegation-only capabilities.
 
- `MetricsWitness` - 
    Sovereign witness that cross-examines L6 obse
- `SafeSystemCommandExecutor` - 
    A secure system command executor that prevent
- `ScriptsPlanningOrchestrator` - Orchestrator for planning script execution operati
- `SovereignFilesystemMcpClient` - Official Filesystem MCP client for sovereign file 
- `SovereignGitKrakenMcpClient` - Official GitKraken MCP client for sovereign versio
- `SystemCommandExecutor` - 
    Protocol for safely executing system commands
- `WorkflowOrchestrator` - Workflow orchestrator with SDK integration.

### Agents with Healing Capability

**Count: 191**

- `BiasAuditor` (L0)
- `BootstrapAgent` (L0)
- `GapClosureArchitect` (L0)
- `GravityComplianceValidator` (L0)
- `GuardianOrchestrator` (L0)
- `HealingOrchestrator` (L0)
- `HygieneValidator` (L0)
- `MetricsWitness` (L0)
- `SafeSystemCommandExecutor` (L0)
- `ScriptToAgentClassifier` (L0)
- `ScriptsPlanningOrchestrator` (L0)
- `SystemCommandExecutor` (L0)
- `WorkflowOrchestrator` (L0)
- `AgentInfo` (L1)
- `AsyncBlockingValidator` (L1)
- `BareExceptValidator` (L1)
- `CanonValidator` (L1)
- `ConcurrencyGuardian` (L1)
- `DangerousBuiltinsValidator` (L1)
- `DebuggerValidator` (L1)
- `DependencySentinel` (L1)
- `DependencySentinelAgent` (L1)
- `DummyAgentCard` (L1)
- `EmptyExceptValidator` (L1)
- `EvalExecValidator` (L1)
- `ExternalHttpValidator` (L1)
- `GenerativeGuard` (L1)
- `GovernanceAgent` (L1)
- `HealerAgent` (L1)
- `IOrchestrator` (L1)
- `IntelligentOrchestrator` (L1)
- `MetaLearningAgent` (L1)
- `PrintStatementValidator` (L1)
- `ReasoningRouter` (L1)
- `ReflectionAgent` (L1)
- `SovereignCognitivePlane` (L1)
- `SystemArchitect` (L1)
- `CodeDeduplicationAgent` (L2)
- `ContextCuratorAgent` (L2)
- `DeadCodeDetectorAgent` (L2)
- `DeadlockDetector` (L2)
- `DriftDetectorAgent` (L2)
- `DriftDetectorAgent` (L2)
- `DynamicModelRouterAgent` (L2)
- `GitAgent` (L2)
- `GlobalComplianceAggregatorAgent` (L2)
- `IntegrityGateExecutor` (L2)
- `IntegrityGateExecutor` (L2)
- `IntegrityGateExecutor` (L2)
- `IntegrityGateExecutorAgent` (L2)
- `L2SelfTestingMixin` (L2)
- `MemoryArchitectAgent` (L2)
- `MemoryLeakDetector` (L2)
- `NamingAgent` (L2)
- `NamingLawHealerAgent` (L2)
- `NamingNormalizationAgent` (L2)
- `OmniContext` (L2)
- `PeerIntelligenceAuditor` (L2)
- `ReflectionAgent` (L2)
- `SafetyExecutor` (L2)
- `SherlockAgent` (L2)
- `SovereignActionPlaneAgent` (L2)
- `SovereignRedisOrchestrator` (L2)
- `SovereignRedisOrchestrator` (L2)
- `SovereigntyAuditor` (L2)
- `SprawlInspector` (L2)
- `StrategicPlannerAgent` (L2)
- `StructuralEngineerAgent` (L2)
- `SubatomicTestingMixin` (L2)
- `SubatomicTestingMixin` (L2)
- `SystemArchitect` (L2)
- `SystemArchitectAgent` (L2)
- `TestPilotAgent` (L2)
- `ToolsmithAgent` (L2)
- `ToolsmithAgent` (L2)
- `AgentFactory` (L3)
- `AgentGym` (L3)
- `AgentPermissionManager` (L3)
- `AgentRegistry` (L3)
- `AgentRegistryValidatorAgent` (L3)
- `AutonomicMonitor` (L3)
- `BenchmarkingAgent` (L3)
- `CachedOrchestrator` (L3)
- `ContextCurator` (L3)
- `CoordinateObservabilityOperationsAgent` (L3)
- `DAGManager` (L3)
- `DAGMutator` (L3)
- `DagEngineAgent` (L3)
- `DagExecutor` (L3)
- `DagManager` (L3)
- `DagRuntimeInspector` (L3)
- `DeadlockDetector` (L3)
- `DispatchOutreachToolsAgent` (L3)
- `DispatchResumeToolsAgent` (L3)
- `HallucinationDetector` (L3)
- `HardenedWorkflowOrchestrator` (L3)
- `HierarchyEnforcerAgent` (L3)
- `IOrchestrator` (L3)
- `L3SubatomicTestingMixin` (L3)
- `McpRouter` (L3)
- `MemoryLeakDetector` (L3)
- `MetaLearningAgent` (L3)
- `MetricsAgent` (L3)
- `MockAgent` (L3)
- `ModelRouter` (L3)
- `NervousSystemAgent` (L3)
- `NervousSystemPhaseOrchestrator` (L3)
- `PredictiveCostAuditorAgent` (L3)
- `ReportingAgent` (L3)
- `ResumeOrchestrator` (L3)
- `SelfRecoveringOrchestrator` (L3)
- `SemanticGatekeeperAgent` (L3)
- `SemanticTerritoryMapperAgent` (L3)
- `SemanticTerritoryMapperAgent` (L3)
- `SignatureVerifierAgent` (L3)
- `SovereignMcpRouter` (L3)
- `SovereignRagOrchestrator` (L3)
- `SubatomicHop` (L3)
- `SubatomicHopAgent` (L3)
- `SubatomicOrchestrator` (L3)
- `TaskMonitor` (L3)
- `TelemetryAgent` (L3)
- `TerritoryHealerAgent` (L3)
- `TerritoryHealerAgent` (L3)
- `TestPilotAgent` (L3)
- `TokenBudgetInspector` (L3)
- `TracingAgent` (L3)
- `TrackObservabilityCostAgent` (L3)
- `WorkflowBlueprint` (L3)
- `AutonomousCheckpointManagerAgent` (L4)
- `AutonomousCheckpointManagerAgent` (L4)
- `AutonomousStateGuardianAgent` (L4)
- `AutonomousStateGuardianAgent` (L4)
- `CanonValidator` (L4)
- `L4SubatomicTestingMixin` (L4)
- `PineconeSovereignAgent` (L4)
- `PineconeSovereignAgent` (L4)
- `RedisSovereignAgent` (L4)
- `SchemaEvolverAgent` (L4)
- `SovereignPineconeStoreAgent` (L4)
- `SubAtomicRegistryAgent` (L4)
- `AutonomousThreatEvolutionAgent` (L5)
- `AutonomousThreatEvolutionAgent` (L5)
- `BaseAgent` (L5)
- `BiasAuditor` (L5)
- `BiasDetectorAgent` (L5)
- `CodeFormatterAgent` (L5)
- `CodeSSOTEnforcerAgent` (L5)
- `ComplianceOrchestrator` (L5)
- `ConstitutionalReviewerAgent` (L5)
- `DependencyPruningAgent` (L5)
- `DocstringComplianceAgent` (L5)
- `DuplicateCodeDetectorAgent` (L5)
- `FileCleanupAgent` (L5)
- `FilenameUniquenessGuardianAgent` (L5)
- `FilesystemAgent` (L5)
- `GitHygieneAgent` (L5)
- `GovernanceAgent` (L5)
- `GravityEnforcerAgent` (L5)
- `GravityLeakRepairAgent` (L5)
- `HallucinationHunterAgent` (L5)
- `HealValidator` (L5)
- `HealerAgent` (L5)
- `HierarchyAgent` (L5)
- `HierarchyHealer` (L5)
- `HygieneGuardianAgent` (L5)
- `ImportAgent` (L5)
- `InferenceTypeHintAgent` (L5)
- `InputValidator` (L5)
- `L5IntegrityGateExecutorAgent` (L5)
- `LocationAgent` (L5)
- `MCPGuardianAgent` (L5)
- `MethodChangeDetector` (L5)
- `NeuralAutoImmuneAgent` (L5)
- `PIISanitizerAgent` (L5)
- `PascalSovereigntyEnforcerAgent` (L5)
- `PromptInjectionDetectorAgent` (L5)
- `RedSentinel` (L5)
- `RedTeamAgent` (L5)
- `RegressionOracleAgent` (L5)
- `SafetyInspector` (L5)
- `SelfUpdatingSafetyEngineAgent` (L5)
- `TerritoryHealerAgent` (L5)
- `TestCoverageGuardianAgent` (L5)
- `TestSovereigntyAgent` (L5)
- `TypeHintEnforcementAgent` (L5)
- `TypeHintFixer` (L5)
- `UnusedCleanupAgent` (L5)
- `OutreachPhase5Orchestrator` (apps_lic)
- `BaseTaskExecutor` (apps_shared)
- `StateValidator` (apps_shared)

---

## PHASE 4: VALIDATION EXAMPLES

### L0 Layer Examples

**AgentCapability**
- Path: `agentic_core\L0_maintenance\scripts\runtime_registry_agent_capabilities.py`
- Inheritance: None
- Key Methods: None
- Healing: No
- Testing: None
- Description: Defines the capability of an agent role.

**AgentRegistry**
- Path: `agentic_core\L0_maintenance\scripts\runtime_registry_agent_capabilities.py`
- Inheritance: None
- Key Methods: __init__, get_capability, register_agent, get_agent_spec, list_roles, run
- Healing: No
- Testing: None
- Description: Registry for managing agent capabilities and specifications.

**AgentRole**
- Path: `agentic_core\L0_maintenance\scripts\runtime_registry_agent_capabilities.py`
- Inheritance: Enum
- Key Methods: None
- Healing: No
- Testing: None
- Description: Functional roles for agents in the system.

### L1 Layer Examples

**AgentCapability**
- Path: `agentic_core\L1_cognition\thought_engine\agent_registry_enums.py`
- Inheritance: Enum
- Key Methods: None
- Healing: No
- Testing: None
- Description: Standard agent capabilities.

**AgentContract**
- Path: `agentic_core\schemas\models\core_contracts.py`
- Inheritance: BaseModel
- Key Methods: None
- Healing: No
- Testing: None
- Description: Contract specification for an agent.

**AgentIdentity**
- Path: `agentic_core\L1_cognition\thought_engine\spiffe_manager_types.py`
- Inheritance: None
- Key Methods: is_expired, is_valid, to_dict, get_namespace, get_agent_name
- Healing: No
- Testing: None
- Description: Cryptographically-verified agent identity.

    Based on SPIFFE ID format: spiffe://trust-domain/pat

### L2 Layer Examples

**AgentPlan**
- Path: `agentic_core\runtime\shared_runtime\subatomic_hop_BROKEN.py`
- Inheritance: BaseModel
- Key Methods: None
- Healing: No
- Testing: None

**AutonomyMixin**
- Path: `agentic_core\patterns\agent_roles\autonomy_mixin.py`
- Inheritance: None
- Key Methods: __init__, should_act_proactively, _system_healthy_for_proactivity, _detect_action_opportunity, proactive_execute
- Healing: No
- Testing: None

**BiasAuditor**
- Path: `agentic_core\runtime\shared_runtime\bias_auditor.py`
- Inheritance: None
- Key Methods: __init__, audit, check_bias_type
- Healing: No
- Testing: None
- Description: Audits text for potential bias.

### L3 Layer Examples

**AgentFactory**
- Path: `agentic_core\L3_orchestration\workflow_engines\agent_factory.py`
- Inheritance: HealerMixin
- Key Methods: _create_impl, create_system_architect, create_healer_agent, create_generative_guard, create_code_janitor, create_dependency_sentinel, create_safety_inspector, create_pattern_enforcer
- Healing: Yes
- Testing: None
- Description: 
    Centralized factory for sovereign agent injection.
    
    Phase 9A DDD Compliance:
    - Only

**AgentGym**
- Path: `agentic_core\L3_orchestration\workflow_engines\agent_gym_impl.py`
- Inheritance: HealerMixin
- Key Methods: __init__, register_scenario, run_benchmark, _execute_test_cases, _create_benchmark_result, _log_benchmark_start, run_training_session, get_scenario, list_scenarios, get_session_history
- Healing: Yes
- Testing: None
- Description: Agent Gym for self-evolution and benchmarking.

    Features:
    - Offline simulation environment
 

**AgentPermissionManager**
- Path: `agentic_core\L3_orchestration\workflow_engines\agent_permissions_impl.py`
- Inheritance: HealerMixin
- Key Methods: __init__, grant_permission, revoke_permission, check_permission, list_permissions, _load_default_permissions
- Healing: Yes
- Testing: None
- Description: Manages agent permissions with Control Plane integration.

    Provides:
    - Identity-based Permis

### L4 Layer Examples

**AtomicBlackboard**
- Path: `agentic_core\L4_state\validation_context\blackboard.py`
- Inheritance: MCPHardenedMixin
- Key Methods: __init__, acquire_lease, release_lease, extend_lease, wait_for_lease, get_health_score, update_health_score, check_regression, revert_file, store_healing_pattern
- Healing: No
- Testing: None
- Description: 
    Thread-safe blackboard for managing validation state.
    
    Features:
    - Lease-based file

**AutonomousCheckpointManagerAgent**
- Path: `agentic_core\L4_state\validation_context\AutonomousCheckpointManagerAgent.py`
- Inheritance: HealerMixin
- Key Methods: __init__, _run_self_tests, _load_checkpoints, _save_checkpoint_index, _calculate_file_hash, _generate_checkpoint_id, create_checkpoint, auto_checkpoint_if_needed, verify_checkpoint, rollback_to_checkpoint
- Healing: Yes
- Testing: Self
- Description: 
    Manages state checkpoints with automatic recovery capabilities.
    
    Features:
    - Automa

**AutonomousCheckpointManagerAgent**
- Path: `agentic_core\L4_state\validation_context\autonomous_checkpoint_manager.py`
- Inheritance: HealerMixin
- Key Methods: __init__, _run_self_tests, _load_checkpoints, _save_checkpoint_index, _calculate_file_hash, _generate_checkpoint_id, create_checkpoint, auto_checkpoint_if_needed, verify_checkpoint, rollback_to_checkpoint
- Healing: Yes
- Testing: Self
- Description: 
    Manages state checkpoints with automatic recovery capabilities.
    
    Features:
    - Automa

### L5 Layer Examples

**AutonomousThreatEvolutionAgent**
- Path: `agentic_core\L5_safety\guardrails\AutonomousThreatEvolutionAgent.py`
- Inheritance: HealerMixin
- Key Methods: __init__, run, threat_evolution_loop, _perform_evolution_cycle, _load_recent_detections, _analyze_patterns, stop, get_status, set_evolution_interval, set_confidence_threshold
- Healing: Yes
- Testing: None
- Description: L5: Self-healing security agent

**AutonomousThreatEvolutionAgent**
- Path: `agentic_core\L5_safety\guardrails\autonomous_threat_evolution.py`
- Inheritance: HealerMixin
- Key Methods: __init__, run, threat_evolution_loop, _perform_evolution_cycle, _load_recent_detections, _analyze_patterns, stop, get_status, set_evolution_interval, set_confidence_threshold
- Healing: Yes
- Testing: None
- Description: L5: Self-healing security agent

**BaseAgent**
- Path: `agentic_core\L5_safety\guardrails\campaign_guardrails.py`
- Inheritance: HealerMixin
- Key Methods: __init__, log_info
- Healing: Yes
- Testing: None
- Description: Stub for BaseAgent - TODO: Replace with sovereign equivalent

---

## DISCOVERY VALIDATION

- **Expected agents**: 63+ core + apps
- **Discovered agents**: 356
- **Core agents (L0-L5)**: 242
- **Apps agents**: 85
- **Test agents**: 19
- **Misc agents**: 10

**VALIDATION: PASSED** - Discovery exceeds expected count with zero-loss scanning.

---

*Report generated by Ultra Agent Discovery Scanner*