# ULTRA ZERO-LOSS AGENT DISCOVERY REPORT
## Full Repository Analysis - January 01, 2026

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Total Agents Discovered** | 401 |
| **Total .py Files Scanned** | 2,043 |
| **Detection Coverage** | 100% (zero-loss) |

### Layer Distribution

| Layer | Count | % |
|-------|-------|---|
| L0 | 11 | 2% |
| L1 | 32 | 7% |
| L2 | 68 | 16% |
| L3 | 29 | 7% |
| L4 | 22 | 5% |
| L5 | 78 | 19% |
| apps_lic | 37 | 9% |
| apps_rg | 26 | 6% |
| apps_shared | 3 | 0% |
| tests | 42 | 10% |
| misc | 53 | 13% |

### Capability Analysis

| Capability | Count | % |
|------------|-------|---|
| **Healing Included** | 49 | 12% |
| **Memory/State** | 140 | 34% |
| **Tools Integration** | 106 | 26% |
| **Subatomic Hops** | 11 | 2% |

### Testing Compliance

| Testing Type | Count | % |
|--------------|-------|---|
| **Self-Testing** | 49 | 12% |
| **Delegated** | 21 | 5% |
| **None** | 331 | 82% |

### Sovereignty Compliance

| Metric | Count | % |
|--------|-------|---|
| **PascalCase Compliant** | 385 | 96% |
| **MCP Hardened** | 12 | 2% |

---

## DETAILED AGENT TABLES BY LAYER

### L0 Layer (11 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| AgenticWorkflowError | Exception | - | - | - | - | 1 | Base exception for agentic workflow |
| BootstrapAgent | - | Y | Y | - | - | 8 | Autonomous boot integrity agent.
Ru |
| FilesystemSSOTReconcilerAgent | AutonomyMixin, AdaptiveEx | - | Y | - | - | 24 | Filesystem-level SSOT reconciler -  |
| GravityComplianceValidator | - | - | - | - | - | 1 | Brief description of functionality  |
| HygieneValidator | - | - | - | - | - | 4 | Detects 'Rot' within the system:
1. |
| L0DelegationMixin | - | Y | - | - | S | 1 | Mixin providing L0 delegation-only  |
| L0SovereignSeverity | Enum | Y | - | - | S | 1 | Sovereign event Severity levels for |
| MaintenanceBaseAgent | CanonBaseAgent, L0Delegat | Y | - | - | S | 1 | Base class for L0 Maintenance agent |
| ScriptToAgentClassifier | AutonomyMixin, AdaptiveEx | - | - | - | - | 1 | Sovereign classifier for script vs  |
| SubAtomicAgent | - | - | - | - | - | 13 | Base class for all validation agent |
| agentic_core | - | - | - | - | - | 1 | Main agentic core class. |

### L1 Layer (32 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| AgentCapability | Enum | - | - | - | - | 1 | Standard agent capabilities. |
| AgentIdentity | - | - | - | - | - | 1 | Cryptographically-verified agent id |
| AgentInfo | - | - | - | - | - | 1 | Simple agent information container  |
| AgentInfo | - | - | - | - | - | 1 | Simple agent information container. |
| AgentStatus | Enum | - | - | - | - | 1 | Agent operational status. |
| AsyncBlockingValidator | CanonASTValidator | - | - | - | - | 1 | Key 31: Detects blocking calls in a |
| BareExceptValidator | CanonASTValidator | - | - | - | - | 1 | Key 5: Detects bare except: stateme |
| CanonBaseAgent | - | - | Y | - | - | 10 | Base class for all validation agent |
| CanonValidator | - | - | Y | - | - | 1 | The L5 Meta-Learner that validates  |
| DangerousBuiltinsValidator | CanonASTValidator | - | - | - | - | 1 | Key 42: Detects dangerous builtin f |
| DebuggerValidator | CanonASTValidator | - | - | - | - | 1 | Key 3: Detects breakpoint() and pdb |
| DependencyGraph | - | - | - | Y | - | 2 | Builds a directed graph of imports  |
| DependencySentinelAgent | - | - | Y | - | - | 1 | Guards the codebase against illegal |
| DependencyViolation | - | - | Y | - | - | 1 | Represents a dependency rule Violat |
| DocumentationAgent | SubAtomicAgent | - | - | - | - | 4 | KEYS: 21 (Missing Docstrings)
ROLE: |
| DummyAgentCard | - | - | - | - | - | 1 | TODO: Add docstring. |
| EmptyExceptValidator | CanonASTValidator | - | - | - | - | 1 | Key 4: Detects empty except blocks  |
| EvalExecValidator | CanonASTValidator | - | - | - | - | 1 | Key 6: Detects eval() and exec() ca |
| ExternalHttpValidator | CanonASTValidator | - | - | - | - | 1 | Key 23: Detects forbidden HTTP libr |
| GenerativeGuard | CanonBaseAgentInterface | Y | Y | Y | - | 4 | KEYS: 45 (Dead Code/Runaway Generat |
| GovernanceAgent | - | - | - | Y | - | 2 | Enforces architectural governance l |
| HealerAgent | CanonBaseAgentInterface | Y | Y | Y | - | 4 | KEYS: 48 (Syntax Repair), 49 (Struc |
| ImportAnalyzer | NodeVisitor | - | Y | - | - | 1 | AST visitor to extract import infor |
| MetaLearningAgent | - | - | - | - | - | 2 | Sovereign meta-learning engine.
Acc |
| NamingAgent | SubAtomicAgent | - | - | - | - | 4 | KEYS: 47 (Naming Conventions)
ROLE: |
| OrchestratorAgentAndScopeManager | - | Y | Y | Y | - | 26 | Manages the creation of the subatom |
| PrintStatementValidator | CanonASTValidator | - | - | - | - | 1 | Key 2: Detects print() statements u |
| ReflectionAgent | - | - | Y | - | S | 1 | Agent responsible for learning from |
| SubAtomicAgent | - | - | - | - | - | 4 | Base class stub for pattern agents. |
| SubAtomicAgent | - | - | - | - | - | 4 | Stub base class for quality agents. |
| SystemArchitect | CanonBaseAgentInterface | Y | Y | Y | - | 4 | KEYS: 40 (Metaclasses), 41 (Deep Ne |
| UiValidationAgent | SubAtomicAgent | - | - | - | - | 4 | ROLE: UI Pattern Validator. Uses Fi |

### L2 Layer (68 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| ArchitectureGovernorAgent | SubAtomicAgent | Y | Y | - | - | 4 | Unified Architecture Governor.
Enfo |
| BenchmarkingAgent | SubAtomicAgent | Y | - | - | - | 5 | ROLE: Measures execution time and e |
| BlastRadius | - | Y | Y | - | - | 5 | Blast radius analysis for a modifie |
| CanonBaseAgent | CanonBaseAgentInterface | - | - | - | - | 1 | Implementation of canon agent base  |
| CanonBaseAgent | CanonBaseAgentInterface | - | - | - | - | 1 | Implementation of canon agent base  |
| CanonBaseAgent | ABC | - | - | - | S | 36 | Base class for Canon Validator agen |
| CanonValidatorEngineZlm | - | - | - | - | - | 1 | Brief description of functionality  |
| CartographerAgent | SubAtomicAgent | Y | Y | - | - | 7 | ROLE: Memory & Embedding. Maps the  |
| CitationMap | - | - | - | - | - | 1 | Brief description of functionality  |
| CodeDeduplicationAgent | - | - | - | - | - | 12 | Batch agent for detecting and optio |
| CodeJanitorAgent | CanonBaseAgent | Y | - | Y | - | 5 | Code Janitor validates syntax, styl |
| ComplexityProfile | - | Y | Y | - | - | 4 | Comprehensive complexity profile fo |
| ConcurrencyGuardianAgent | SubAtomicAgent | Y | - | - | - | 6 | Unified concurrency safety agent.
C |
| ContextCuratorAgent | SubAtomicAgent | Y | Y | - | - | 70 | The Context Curator - Prompt Engine |
| ContextSnapshot | - | Y | Y | - | - | 70 | Snapshot of context at a point in t |
| DeepResearchOutput | - | - | - | - | - | 1 | Brief description of functionality  |
| DependencyDiplomatAgent | SubAtomicAgent | Y | Y | - | - | 5 | The Dependency Diplomat - Graph Opt |
| DependencySentinelAgent | SubAtomicAgent | Y | Y | - | - | 4 | KEYS: 7 (Star Imports), 8 (Relative |
| DistilledPattern | - | Y | Y | - | - | 6 | Represents a distilled pattern read |
| DocEnforcerAgent | SubAtomicAgent | Y | Y | - | - | 7 | ROLE: Documentation Surgeon. |
| DynamicModelRouterAgent | SubAtomicAgent | Y | Y | - | - | 4 | The Throttler - Dynamic Model Route |
| FinancialProofPoint | - | - | - | - | - | 1 | Brief description of functionality  |
| GitAgent | - | - | - | - | - | 8 | Agent for managing git operations a |
| GitAgent | SubAtomicAgent | Y | - | - | - | 5 | ROLE: Manages Version Control (Bran |
| HandoffSummary | - | Y | Y | - | - | 70 | Compressed summary for stage handof |
| HealerAgent | CanonBaseAgent | Y | Y | Y | S | 11 | Healer Agent provides autonomous co |
| HealingDiffAnalyzer | - | Y | Y | - | - | 6 | Analyzes before/after code to ident |
| HealingSuccess | - | Y | Y | - | - | 6 | Represents a successful healing ope |
| HistorianAgent | SubAtomicAgent | Y | - | - | - | 5 | ROLE: Records all validation events |
| ImportNode | - | Y | Y | - | - | 5 | Represents a file in the import gra |
| IntegrityGateExecutorAgent | - | - | - | - | - | 1 | Executor for integrity gate validat |
| IntegrityGateResult | - | - | - | - | - | 1 | Brief description of functionality  |
| KeyExecutive | - | - | - | - | - | 1 | Brief description of functionality  |
| KeyTechnology | - | - | - | - | - | 1 | Brief description of functionality  |
| LeadershipLayer | - | - | - | - | - | 1 | Brief description of functionality  |
| MemoryArchitectAgent | SubAtomicAgent | Y | Y | - | - | 6 | Autonomous Knowledge Distillation A |
| ModelTier | str, Enum | Y | Y | - | - | 4 | Model tiers based on capability and |
| NamingEnforcerAgent | SubAtomicAgent | Y | Y | - | - | 7 | ROLE: Semantic Naming Guardian. |
| OmniContextAgent | SubAtomicAgent | Y | Y | - | - | 7 | ROLE: Wisdom & Semantic Retrieval.  |
| PatternEnforcerAgent | SubAtomicAgent | Y | - | - | - | 5 | KEYS: 26-39 (Pattern Checks)
ROLE:  |
| RedSentinelAgent | SubAtomicAgent | Y | - | - | - | 6 | Red team sentinel for adversarial s |
| ReflectionAgent | SubAtomicAgent | Y | Y | - | S | 5 | ROLE: Consolidation and self-critiq |
| RoutingDecision | - | Y | Y | - | - | 4 | Model routing decision with rationa |
| SafetyInspectorAgent | SubAtomicAgent | Y | - | - | - | 6 | Enforces Security Protocols: Keys 0 |
| SecurityEnforcerAgent | SubAtomicAgent | Y | - | - | - | 6 | Security enforcement agent for addi |
| SherlockAgent | SubAtomicAgent | Y | - | - | - | 4 | ROLE: Root Cause Analysis. Triggere |
| SovereignActionPlaneAgent | IActionPlane | - | - | Y | S | 38 | Sovereign action plane with Toolsmi |
| SovereignSandbox | - | - | - | Y | S | 38 | Secure execution environment for to |
| SovereignSeverity | Enum | - | - | - | S | 36 | Sovereign event Severity levels for |
| SovereignToolsmith | - | - | - | Y | S | 38 | Toolsmith implementation for dynami |
| StrategicLayer | - | - | - | - | - | 1 | Brief description of functionality  |
| StrategicPlannerAgent | SubAtomicAgent | Y | Y | - | S | 5 | ROLE: High-level strategist.
Analyz |
| StrategistAgent | SubAtomicAgent | Y | Y | - | - | 7 | ROLE: Proactive Architecture. Ident |
| StructuralEngineerAgent | SubAtomicAgent | Y | - | - | - | 5 | KEYS: 18 (Many Parameters), 20 (Lar |
| StructuralEngineerAgent | CanonBaseAgent | Y | - | Y | - | 4 | Structural Engineer validates code  |
| SubAtomicAgent | - | - | - | - | - | 13 | Base class for all validation agent |
| SubatomicTestingMixin | - | - | - | - | S | 36 | Mixin providing L2 subatomic testin |
| SystemArchitect | CanonBaseAgent | Y | - | Y | - | 7 | System Architect validates core arc |
| SystemArchitectAgent | CanonBaseAgent | Y | - | Y | - | 18 | System Architect validates core arc |
| TechnicalLayer | - | - | - | - | - | 1 | Brief description of functionality  |
| TestPilotAgent | SubAtomicAgent | Y | - | - | - | 4 | ROLE: Integration Guardian. Runs py |
| ToolsmithAgent | SubAtomicAgent | Y | - | - | - | 4 | ROLE: Dynamic Tool Forger.
Creates  |
| TypeEnforcerAgent | SubAtomicAgent | Y | Y | - | - | 7 | ROLE: Type Guardian. Enforces PEP 4 |
| ValidationRejectionReason | Enum | - | - | - | - | 1 | Brief description of functionality  |
| Violation | - | - | - | - | - | 1 | Brief description of functionality  |
| _SubatomicEnginePlaceholder | - | - | - | - | S | 36 | Placeholder for the Subatomic Engin |
| _fission_managerPlaceholder | - | - | - | - | S | 36 | Placeholder for the Fission Manager |
| _safety_guardrailPlaceholder | - | - | - | - | S | 36 | Placeholder for the Safety Guardrai |

### L3 Layer (29 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| AgentFactory | - | Y | - | - | - | 1 | Centralized factory for sovereign a |
| AgentRegistry | - | - | - | - | - | 1 | Mock AgentRegistry for type hinting |
| AgentRegistryValidatorAgent | - | - | - | - | - | 1 | L3 Orchestration: Agent Registry Va |
| AgentRole | Enum | - | - | - | - | 1 | Brief description of functionality  |
| DagEngineAgent | - | - | - | - | - | 1 | Lightweight DAG engine for workflow |
| DagExecutionResult | - | - | - | - | - | 1 | Result from DAG execution. |
| DispatchOutreachToolsAgent | - | - | - | - | - | 1 | Executor for outreach domain. |
| DispatchResumeToolsAgent | - | - | - | - | - | 1 | Executor for resume domain with Tit |
| MetaLearningAgent | AutonomyMixin, AdaptiveEx | - | Y | - | - | 1 | Sovereign meta-learning agent that  |
| MockAgent | - | - | Y | - | - | 1 | - |
| NervousSystemAgent | - | - | Y | - | - | 1 | Core orchestrator that coordinates  |
| NervousSystemArchitectureGovernance | - | - | Y | - | - | 1 | Handles architecture validation and |
| NervousSystemCheckpointing | - | - | Y | - | - | 1 | Handles checkpointing operations fo |
| NervousSystemInterventionManager | - | - | Y | - | - | 1 | Manages human intervention requests |
| NervousSystemPhaseExecution | - | - | Y | - | - | 1 | Manages the execution of phases (se |
| NervousSystemPhaseOrchestrator | - | - | Y | - | - | 1 | Orchestrates the execution of all p |
| NervousSystemResultReporting | - | - | Y | - | - | 1 | Handles mission result generation a |
| NervousSystemStateManagement | - | - | Y | - | - | 1 | Handles state persistence and retri |
| SemanticGatekeeperAgent | - | - | - | - | - | 1 | Gatekeeper that controls agent exec |
| SemanticTerritoryMapperAgent | - | - | - | - | - | 1 | L3 Orchestration: Semantic Territor |
| SemanticTerritoryMapperAgent | - | - | Y | - | - | 4 | The Intelligent Brain that maps fil |
| SovereignDependencyError | Exception | - | Y | - | S | 1 | Raised when a required dependency i |
| SubatomicHopAgent | - | - | Y | - | S | 1 | Sovereign SubatomicHop with Depende |
| Task | - | - | - | - | - | 1 | Individual Task in the DAG. |
| TaskStatus | Enum | - | - | - | - | 1 | Status of a Task in the DAG. |
| TaskType | Enum | - | - | - | - | 1 | Type of Task in the DAG. |
| TerritoryHealerAgent | - | - | - | Y | - | 1 | L3 Orchestration: Territory Healing |
| TerritoryHealerAgent | - | - | Y | - | - | 4 | Enforces exhaustive territory compl |
| TestPilotAgent | - | - | Y | Y | S | 81 | TestPilot agent with property-based |

### L4 Layer (22 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| AutonomousCheckpointManagerAgent | - | - | Y | - | - | 1 | Manages state checkpoints with auto |
| AutonomousCheckpointManagerAgent | - | - | Y | - | - | 1 | Manages state checkpoints with auto |
| AutonomousStateGuardianAgent | - | Y | Y | - | - | 1 | L4 State Guardian that autonomously |
| AutonomousStateGuardianAgent | - | Y | Y | - | - | 1 | L4 State Guardian that autonomously |
| CanonValidator | - | - | Y | - | - | 1 | The Gatekeeper logic that enforces  |
| Checkpoint | - | - | Y | - | - | 1 | Represents a state Checkpoint. |
| ImpactAnalysis | - | Y | - | - | - | 8 | Analysis of schema change impact. |
| L4SovereignSeverity | Enum | Y | Y | - | S | 9 | Sovereign event Severity levels for |
| L4SubatomicTestingMixin | - | Y | Y | - | S | 9 | Mixin providing L4 subatomic testin |
| PineconeSovereignAgent | - | - | Y | Y | - | 3 | Sovereign Pinecone controller — zer |
| PineconeSovereignAgent | - | - | Y | - | - | 1 | Mock Pinecone Sovereign Agent. |
| RecoveryResult | - | - | Y | - | - | 1 | Result of a recovery operation. |
| RedisSovereignAgent | - | - | Y | - | - | 1 | Sovereign Redis controller — harden |
| SchemaChange | - | Y | - | - | - | 8 | Represents a proposed schema change |
| SchemaDefinition | - | Y | - | - | - | 8 | Represents a Pydantic model or data |
| SchemaEvolverAgent | SubAtomicAgent | Y | - | - | - | 8 | The Structural Guard - Schema Evolu |
| SchemaRegistry | - | Y | - | - | - | 8 | Registry of all schemas in the code |
| SovereignPineconeMcpClient | MCPHardenedMixin | - | Y | - | S | 1 | Official Pinecone MCP client — L3 r |
| SovereignPineconeStoreAgent | - | - | Y | - | - | 1 | ADAPTER: Legacy Interface -> New MC |
| SovereignRedisMcpClient | MCPHardenedMixin | - | Y | - | S | 1 | Official Redis MCP client for sover |
| StateBaseAgent | CanonBaseAgent, L4Subatom | Y | Y | - | S | 9 | Base class for L4 State agents with |
| SubAtomicRegistryAgent | - | - | Y | - | - | 3 | Sovereign method registry — live, h |

### L5 Layer (78 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| AdversarialRedTeamerAgent | SubAtomicAgent | Y | - | - | S | 39 | The Skeptic - Adversarial Red Team  |
| AtomicClaim | - | Y | - | - | - | 30 | Represents an atomic Claim (proposi |
| AutonomousThreatEvolutionAgent | - | - | - | - | - | 1 | L5: Self-healing security agent |
| AutonomousThreatEvolutionAgent | - | - | - | - | - | 1 | L5: Self-healing security agent |
| BaseAgent | - | - | - | - | - | 1 | Stub for BaseAgent - TODO: Replace  |
| BiasDetectorAgent | BaseAgent | - | - | - | - | 1 | Runs local bias detection with dyna |
| CapabilityVisitor | NodeVisitor | - | Y | - | S | 1 | - |
| ClaimEmbedder | - | Y | - | - | - | 30 | Handles generating embeddings for c |
| ClaimExtractor | - | Y | - | - | - | 30 | Handles extraction of atomic claims |
| ClaimVerifier | - | Y | - | - | - | 30 | Handles verifying claims against a  |
| CodeFormatterAgent | - | - | - | - | - | 1 | Atomic agent: Enforces consistent f |
| CodeSSOTEnforcerAgent | - | - | - | Y | - | 1 | Ultra high-signal code-level SSOT e |
| Config | - | - | - | - | - | 3 | - |
| ConstitutionalReviewerAgent | BaseAgent | - | - | - | - | 1 | Performs final constitutional revie |
| DependencyPruningAgent | - | - | - | - | - | 3 | Batch agent: Detects and removes un |
| DocstringComplianceAgent | - | - | - | Y | - | 3 | Ensures public functions, classes,  |
| DuplicateCodeDetectorAgent | - | - | - | - | - | 3 | Batch agent: Detects exact duplicat |
| FileCleanupAgent | - | - | - | - | - | 5 | Batch agent: Identifies and removes |
| FilenameUniquenessGuardianAgent | - | - | Y | - | - | 3 | Batch agent that enforces unique fi |
| FilesystemAgent | - | - | Y | Y | - | 1 | Autonomous agent for physical files |
| GeneratedTest | - | Y | Y | Y | - | 134 | Represents a generated test case. |
| GitHygieneAgent | - | - | - | - | - | 1 | Batch agent: Enforces Git repositor |
| GovernanceAgent | AutonomyMixin, AdaptiveEx | - | - | - | - | 1 | Sovereign governance agent that mak |
| GravityEnforcerAgent | CachedSafetyShield | - | Y | Y | - | 2 | The "Neural Link" stabilizer that e |
| GravityLeakRepairAgent | - | - | - | Y | - | 6 | Converts forbidden static imports f |
| HallucinationHunterAgent | SubAtomicAgent | Y | - | - | - | 30 | The Hallucination Hunter - Ground T |
| HealValidator | - | - | - | - | S | 2 | Multi-stage validator for LLM-heale |
| HealerAgent | - | - | - | Y | - | 12 | Autonomous Conductor for structural |
| HierarchyAgent | - | - | Y | - | S | 1 | Autonomous agent for hierarchical s |
| HygieneGuardianAgent | CanonBaseAgent | Y | - | Y | - | 2 | Validates Canon Key 45: Shared Util |
| ImportAgent | - | - | Y | - | - | 1 | Autonomous agent for import convent |
| ImportUpdater | NodeVisitor | - | - | Y | - | 12 | AST engine to verify and suggest im |
| ImportValidationVisitor | NodeVisitor | - | Y | - | - | 1 | [SUPREME COURT GATEKEEPER]
Structur |
| InferenceTypeHintAgent | - | - | - | Y | - | 19 | Uses LLM inference to add accurate  |
| InputValidationError | Exception | - | - | - | - | 3 | Raised when input validation fails. |
| InputValidator | - | - | - | - | - | 3 | Validates input data against schema |
| IntegrityReport | - | Y | - | - | - | 30 | Data integrity audit report. |
| L5IntegrityGateExecutorAgent | - | - | - | - | - | 1 | L5+ Integrity Gate Executor with Tw |
| L5SignalType | str, Enum | - | - | - | - | 1 | Specific signal types emitted by th |
| LocationAgent | - | - | - | - | - | 1 | Autonomous agent responsible for te |
| MCPGuardianAgent | - | - | Y | - | S | 3 | L5 Safety Guardian for MCP integrat |
| MethodChange | - | Y | Y | Y | - | 134 | Represents a changed method requiri |
| MethodChangeDetector | - | Y | Y | Y | - | 134 | Detects method changes between two  |
| NeuralAutoImmuneAgent | AutonomyMixin, AdaptiveEx | - | Y | - | - | 2 | Sovereign auto-immune response — is |
| NeuralAutoImmuneAgent | - | - | Y | - | - | 1 | - |
| PIISanitizerAgent | BaseAgent | - | - | - | - | 1 | Performs local PII detection using  |
| PascalSovereigntyEnforcerAgent | CanonBaseAgent, ASTEnforc | Y | Y | - | S | 4 | L5 Safety agent — enforces PascalCa |
| PromptInjectionDetectorAgent | BaseAgent | - | - | - | - | 1 | Detects prompt-injection attacks. |
| RedTeamAgent | - | - | - | - | - | 3 | Sovereign red-teaming agent for gua |
| RedTeamResult | - | Y | - | - | S | 39 | Result of a red team test. |
| RegressionOracleAgent | SubAtomicAgent | Y | Y | Y | - | 134 | The Regression Oracle - Automated T |
| RegressionTestGenerator | - | Y | Y | Y | - | 134 | Generates pytest code and creates t |
| RegressionTestRunner | - | Y | Y | Y | - | 134 | Runs generated tests, performs self |
| RuleType | Enum | - | - | - | - | 1 | Types of safety rules. |
| SafetyRule | - | - | - | - | - | 1 | Represents a safety rule. |
| SelfUpdatingSafetyEngineAgent | - | - | - | - | - | 1 | Safety engine that learns and adapt |
| SignalBusInterface | Protocol | - | - | - | - | 1 | Protocol for a signal bus emitter.
 |
| SovereignSeverity | Enum | Y | Y | - | S | 4 | Sovereign event Severity levels. |
| SovereignSeverity | Enum | Y | - | - | S | 1 | Sovereign event Severity levels. |
| TerritoryHealerAgent | - | - | Y | Y | - | 4 | Enforces exhaustive territory compl |
| TestCoverageGuardianAgent | - | - | - | - | - | 25 | Ultimate verification agent: Enforc |
| TestSovereigntyAgent | CanonBaseAgent | Y | - | - | S | 1 | L5 specialist — advanced sovereign  |
| ThreatDetection | - | - | - | - | - | 1 | Result of threat detection. |
| ThreatLevel | Enum | - | - | - | - | 1 | Threat Severity levels. |
| ThreatPattern | - | - | - | - | - | 1 | Represents a detected threat patter |
| TypeHintEnforcementAgent | - | - | - | Y | - | 2 | Ensures public functions, methods,  |
| TypeHintFixer | NodeTransformer | - | - | Y | - | 2 | AST transformer that adds Missing t |
| UnusedCleanupAgent | - | - | - | - | - | 1 | Atomic agent: Removes unused import |
| UsageVisitor | NodeVisitor | - | Y | - | - | 1 | - |
| ValidatedInput | BaseModel | - | - | - | - | 3 | Base model for validated input. |
| ValidationCategory | str, Enum | - | - | - | - | 1 | Categories of validation checks. |
| ValidationIssue | - | - | - | - | - | 1 | A single validation issue. |
| ValidationResult | - | - | - | - | - | 1 | Result of validation with all issue |
| ValidationRule | - | - | - | - | - | 3 | Rule for validating input. |
| ValidationSeverity | str, Enum | - | - | - | - | 1 | Severity levels for validation issu |
| ValidationType | Enum | - | - | - | - | 3 | Types of validation. |
| VerificationResult | - | Y | - | - | - | 30 | Result of Claim verification. |
| VulnerabilityTest | - | Y | - | - | S | 39 | Represents a vulnerability test cas |

### apps_lic Layer (37 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| ASCIIEnforcer | - | - | - | - | - | 1 | Enforce ASCII-only characters for L |
| AgentStatus | Enum | - | - | - | S | 1 | Agent execution status |
| AgentStatus | Enum | - | - | - | S | 1 | Agent execution status |
| BaseAgent | - | - | - | - | S | 5 | Stub for BaseAgent - TODO: Replace  |
| CampaignBalanceAgent | OutreachAgent | - | - | - | - | 1 | Ensures campaign elements are balan |
| ConstraintFeasibilityChecker | - | - | - | - | - | 1 | Pre-flight check for constraint sat |
| ContactValidatorAgent | OutreachAgent | - | - | - | - | 1 | Validates contact information. |
| ContentCleanlinessValidator | - | - | - | - | - | 1 | Forbidden verbs and weak language d |
| DeliverabilityAgent | OutreachAgent | - | - | - | - | 1 | Checks email deliverability factors |
| ErrorCodeRegistry | - | - | - | - | - | 1 | Centralized error codes with remedi |
| HOP1ProfileAnalysisAgent | MCPHardenedMixin | - | Y | - | - | 24 | v13.1: HOP-1 - Profile Analysis wit |
| HOP2ResearchAgent | MCPHardenedMixin | - | Y | - | S | 63 | v13.1: Research Agent - Vector-stor |
| HOP3SenderGroundingAgent | MCPHardenedMixin | - | Y | - | - | 24 | v13.1: HOP-3 - Sender Grounding Ext |
| HOP4RoutingAgent | MCPHardenedMixin | - | Y | - | - | 24 | v13.1: HOP-4 - Routing Decision wit |
| HOP5GenerationAgent | MCPHardenedMixin | - | Y | - | S | 63 | v13.1: Generation Agent - N-candida |
| HOP6ValidationAgent | MCPHardenedMixin | - | Y | - | S | 63 | v13.1: Validation Agent - Rule-base |
| HOP7GateDecisionAgent | MCPHardenedMixin | - | Y | - | - | 24 | v13.1: HOP-7 - Gate Decision Agent  |
| HOP8QAReportAgent | MCPHardenedMixin | - | Y | - | S | 63 | v13.1: QA Report Agent - Persistent |
| IntelligenceLibrarian | MCPHardenedMixin | - | Y | - | - | 16 | v13.1: Offline research agent that  |
| InternalAgent | - | - | - | - | S | 5 | v12.0: UPGRADED to primary intellig |
| LeadQualityAgent | OutreachAgent | - | - | - | - | 1 | Validates and scores lead quality. |
| MessageComplianceAgent | OutreachAgent | - | - | - | - | 1 | Ensures message compliance with reg |
| MessageDiversityValidator | - | - | - | - | - | 1 | Prevent repetitive messages using c |
| OrganizationAgent | - | - | - | - | S | 5 | v12.0: DEMOTED to secondary fact-ch |
| OutreachAgent | ABC | - | - | - | - | 2 | Abstract base class for all outreac |
| OutreachAgentFactory | - | - | - | - | - | 6 | Factory for creating outreach agent |
| OutreachLearningAgent | OutreachAgent | - | Y | - | - | 1 | Learning agent for outreach campaig |
| OutreachProactiveAgent | OutreachAgent | - | - | - | - | 1 | Agent that proactively identifies a |
| OutreachReflectionAgent | OutreachAgent | - | - | - | - | 1 | Reflects on execution and suggests  |
| PlaceholderDetector | - | - | - | - | - | 1 | Comprehensive placeholder detection |
| RecipientAgent | - | - | - | - | S | 5 | v12.0: DEMOTED to secondary fact-ch |
| S2_SupervisorAgent | - | - | - | - | S | 5 | v12.0: Updated coordination logic f |
| TestContactValidatorAgent | - | - | Y | - | - | 5 | Tests for ContactValidatorAgent. |
| TestLeadQualityAgent | - | - | Y | - | - | 5 | Tests for LeadQualityAgent. |
| TestMessageComplianceAgent | - | - | Y | - | - | 5 | Tests for MessageComplianceAgent. |
| TestOutreachProactiveAgent | - | - | - | - | - | 1 | Tests for OutreachProactiveAgent. |
| ValidationAgent | - | - | - | - | - | 1 | NEW v11.6: Comprehensive validation |

### apps_rg Layer (26 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| ATSCompatibilityAgent | ResumeAgent | - | Y | - | - | 1 | Validates ATS (Applicant Tracking S |
| AgentFactory | - | - | - | Y | - | 6 | Factory for creating agent instance |
| BrandComplianceAgent | ResumeAgent | - | Y | - | - | 1 | Ensures brand voice and professiona |
| ContentQualityAgent | ResumeAgent | - | Y | - | - | 1 | Validates resume content quality.

 |
| FactCheckAgent | ResumeAgent | - | Y | - | - | 1 | Verifies claims against user profil |
| ProactiveAgent | ResumeAgent | - | - | - | - | 1 | Agent that proactively identifies a |
| ReflectionAgent | ResumeAgent | - | Y | - | - | 1 | Learns from execution and records i |
| ResumeAgent | ABC | - | - | - | - | 1 | Base class for all resume generatio |
| ResumeLearningAgent | - | - | Y | - | - | 5 | Agent that combines all Phase 3 lea |
| SectionBalanceAgent | ResumeAgent | - | Y | - | - | 1 | Ensures proper section balance and  |
| TestATSCompatibilityAgent | - | - | - | - | - | 1 | Tests for ATSCompatibilityAgent. |
| TestAgentCoordination | - | - | - | - | - | 1 | Tests for multi-agent coordination. |
| TestAgentFactory | - | - | - | - | - | 1 | Tests for AgentFactory class. |
| TestBrandComplianceAgent | - | - | - | - | - | 1 | Tests for BrandComplianceAgent. |
| TestContentQualityAgent | - | - | - | - | - | 1 | Tests for ContentQualityAgent. |
| TestFactCheckAgent | - | - | - | - | - | 1 | Tests for FactCheckAgent. |
| TestMetricsWithAgents | - | - | - | - | - | 2 | Integration tests for MetricsCollec |
| TestProactiveAgent | - | - | - | - | - | 1 | Tests for ProactiveAgent. |
| TestReflectionAgent | - | - | - | - | - | 1 | Tests for ReflectionAgent. |
| TestResilientMutatorWithAgents | - | - | - | Y | - | 21 | Integration tests for ResilientMuta |
| TestResumeLearningAgent | - | - | Y | - | - | 1 | Tests for ResumeLearningAgent class |
| TestResumeLearningAgentIntegration | - | - | - | - | D | 1 | Integration tests for ResumeLearnin |
| TestSectionBalanceAgent | - | - | - | - | - | 1 | Tests for SectionBalanceAgent. |
| TestValidationAgent | - | - | - | - | - | 1 | Tests for ValidationAgent class. |
| TestValidatorWithResumeProcessing | - | - | - | - | - | 2 | Integration tests for ValidationAge |
| ValidationAgent | - | - | - | - | - | 11 | Pattern enforcement and code qualit |

### apps_shared Layer (3 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| CanonBaseAgentInterface | ABC | - | - | - | - | 1 | - |
| CanonBaseAgentInterfaceImpl | ABC | - | - | - | - | 1 | Sovereign interface for all canon a |
| StateValidator | - | - | Y | - | - | 11 | Validates state files against expec |

### tests Layer (42 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| MockContext | - | - | - | - | - | 6 | Mock context for testing. |
| TestASTNormalization | TestCase | Y | - | - | - | 10 | Test AST normalization methods. |
| TestAgentDiscovery | - | Y | - | - | D | 1 | E2E tests for agent discovery and r |
| TestAgentFileValidation | - | Y | Y | - | D | 12 | Test validation of Agent files. |
| TestAgentHierarchy | - | Y | - | - | S | 1 | Test agent hierarchy and inheritanc |
| TestAgentRegistry | - | Y | Y | - | D | 1 | Test AGENT_REGISTRY from structure_ |
| TestBasicNamingValidation | - | Y | Y | - | D | 12 | Test basic naming validation for un |
| TestClient | MCPHardenedMixin | - | Y | - | S | 1 | - |
| TestCodeDeduplicationAST | TestCase | Y | - | - | - | 10 | Test AST fingerprinting for code de |
| TestCodeDeduplicationAgent | TestCase | Y | - | - | D | 11 | Test suite for L2 CodeDeduplication |
| TestDuplicateCodeDetectorAgent | TestCase | Y | - | - | D | 11 | Test suite for L5 DuplicateCodeDete |
| TestExemptions | - | Y | Y | - | D | 12 | Test file and directory exemptions. |
| TestFileCleanupAgent | TestCase | - | - | - | - | 6 | Test FileCleanupAgent functionality |
| TestFileTypeDetection | - | Y | Y | - | D | 12 | Test file type category detection. |
| TestHealerAgentASTDiff | TestCase | - | - | Y | - | 3 | Test AST-based diff application for |
| TestHealerAgentIntegration | TestCase | - | - | Y | - | 3 | Integration tests for AST-based hea |
| TestHealerAgentPerformance | TestCase | - | - | Y | - | 3 | Performance tests for AST operation |
| TestIntegrationFileCleanup | TestCase | - | - | - | - | 6 | Integration tests for FileCleanupAg |
| TestL0MaintenanceAgents | - | Y | Y | - | D | 1 | L0 Maintenance Layer: Scripts, logs |
| TestL1CognitionAgents | - | Y | Y | - | D | 1 | L1 Cognition Layer: Thought engine, |
| TestL2ExecutionAgents | - | Y | Y | - | D | 1 | L2 Execution Layer: Tool registry,  |
| TestL3OrchestrationAgents | - | Y | Y | - | D | 1 | L3 Orchestration Layer: Workflow en |
| TestL4StateAgents | - | Y | Y | - | D | 1 | L4 State Layer: Validation context, |
| TestL5SafetyAgents | - | Y | Y | - | D | 1 | L5 Safety Layer: Guardrails, valida |
| TestNamingAgentFallback | TestCase | - | - | - | - | 2 | Test fallback behavior when tree-si |
| TestNamingAgentPerformance | TestCase | - | - | - | - | 2 | Test performance improvements with  |
| TestNamingAgentTreeSitter | TestCase | - | - | - | - | 2 | Test tree-sitter multi-language sym |
| TestNonPythonFileValidation | - | Y | Y | - | D | 12 | Test validation of non-Python files |
| TestRunMethod | - | Y | Y | - | D | 12 | Test the run() method for scanning  |
| TestScriptFileValidation | - | Y | Y | - | D | 12 | Test validation of script files. |
| TestWordCounting | - | Y | Y | - | D | 12 | Test word counting in filenames. |
| agent_response | - | - | - | - | D | 1 | Brief description of functionality  |
| git_agent | - | - | - | - | - | 1 | ROLE: Remote GitOps. Manages checkp |
| test_agentic_core_model | - | - | - | Y | D | 1 | Test agentic_core domain model. |
| test_git_agent_branching_logic | - | - | - | - | - | 1 | Verifies GitAgent branch creation a |
| test_git_agent_critical_failure | - | - | - | - | - | 1 | Verifies GitAgent handles critical  |
| test_git_agent_error_handling | - | - | - | - | - | 1 | Verifies GitAgent handles errors gr |
| test_git_agent_remote_push | - | - | - | - | - | 1 | Verifies GitAgent remote push opera |
| test_git_agent_streamer_integration | - | - | - | - | - | 1 | Verifies GitAgent broadcasts to the |
| test_multi_agent_coordination | - | - | - | Y | - | 16 | Test coordinated healing across mul |
| test_multi_agent_scenarios | - | - | - | - | - | 1 | E2E tests for multi-agent scenarios |
| toolsmith_agent | - | - | Y | - | - | 5 | ROLE: Dynamic Agency. Creates diagn |

### misc Layer (53 agents)

| Agent Name | Inheritance | Tools | Memory | Healing | Testing | LOC | Description |
|------------|-------------|-------|--------|---------|---------|-----|-------------|
| ASTDeadCodeVisitor | NodeVisitor | - | - | - | - | 2 | Enhanced AST visitor that tracks de |
| AgentContract | BaseModel | - | - | - | - | 1 | Contract specification for an agent |
| AgentInfo | - | - | - | Y | - | 8 | Information about a discovered agen |
| AgentInfo | - | - | - | Y | - | 16 | - |
| AgentMessage | SovereignBaseModel | - | - | - | - | 1 | Sovereign-grade message used for in |
| AgentMessage | SovereignBaseModel | - | - | - | - | 1 | Brief description of functionality  |
| AgentPlan | BaseModel | - | Y | - | S | 1 | - |
| AgentPlan | BaseModel | - | - | - | - | 1 | Agent execution plan with reasoning |
| AgentPlan | BaseModel | - | - | - | - | 1 | Agent execution plan with reasoning |
| AgentResponse | - | - | Y | - | - | 1 | Response from agent execution conta |
| AgentThoughtProcess | BaseModel | - | - | - | - | 1 | Forces the agent to show its work b |
| AgentThoughtProcess | BaseModel | - | - | - | - | 1 | Forces the agent to show its work b |
| BenchmarkContext | - | - | Y | - | - | 1 | Context manager for benchmarking. |
| BenchmarkResult | - | - | Y | - | - | 1 | - |
| BenchmarkResultActual | - | - | Y | - | - | 1 | Result of a single benchmark measur |
| BenchmarkSuite | - | - | Y | - | - | 1 | Collection of benchmarks for a spec |
| BenchmarkingAgent | - | - | Y | - | - | 1 | Measures and tracks performance met |
| CanonAstValidator | NodeVisitor | - | - | - | - | 1 | [L6 INFRASTRUCTURE] Base AST visito |
| CognitiveContractValidator | - | - | - | - | - | 18 | Validates cognitive contracts and e |
| ContextAwareValidator | - | - | - | Y | - | 1 | Base class for intelligent validato |
| CoordinateObservabilityOperationsAg | - | - | - | - | - | 6 | Orchestrator for operations domain. |
| CostReport | - | Y | - | - | - | 6 | Comprehensive cost report. |
| DeadCodeDetectorAgent | - | - | - | - | - | 2 | Sovereign dead code auditor that id |
| DriftDetectorAgent | - | - | - | - | - | 1 | Detects files that have drifted out |
| DriftDetectorAgent | - | - | - | - | - | 1 | Naming/Compliance: Drift Detection |
| FileAudit | - | Y | - | - | - | 6 | Audit record for a single file. |
| GlobalComplianceAggregatorAgent | - | - | - | - | - | 1 | Naming/Compliance: Global Complianc |
| HealingMetrics | - | Y | - | - | - | 6 | Metrics for a single healing attemp |
| HierarchyEnforcerAgent | - | - | - | - | - | 10 | Enforces the canonical L4 hierarchy |
| MetricsAgent | - | - | Y | - | - | 2 | MetricsAgent: Sovereign quantitativ |
| MockSpan | - | - | - | - | - | 4 | - |
| MockTracer | - | - | - | - | - | 4 | - |
| NamingAgent | - | - | Y | Y | - | 1 | Autonomous agent for naming law com |
| NamingLawHealerAgent | - | - | - | - | - | 5 | L1 Cognition: High-Signal Naming La |
| NamingNormalizationAgent | - | - | - | Y | - | 3 | Normalizes filenames and public sym |
| NoOpSpan | - | - | - | - | - | 4 | - |
| NonConformingAgentFinder | NodeVisitor | - | - | Y | - | 6 | - |
| OperationResult | - | - | - | - | - | 6 | Result of operation. |
| OperationResult | - | - | - | - | - | 1 | Result of operation. |
| OrchestrationResult | - | - | - | - | - | 6 | Result of orchestration. |
| PlacementResult | - | - | Y | Y | - | 1 | - |
| PredictiveCostAuditorAgent | SubAtomicAgent | Y | - | - | - | 6 | The Efficiency Guard - Predictive C |
| ReportingAgent | - | - | - | - | - | 2 | Autonomous diagnostic agent for com |
| ResidualAgentMessage | - | - | - | - | - | 1 | Lightweight runtime message format  |
| ResidualAgentMessage | - | - | Y | - | - | 1 | Message in agent conversation (Resi |
| SignatureVerifierAgent | - | - | - | - | - | 6 | function class for inspection domai |
| Span | - | - | - | - | - | 4 | Represents a single tracing Span. |
| StepResult | - | - | - | - | - | 6 | Result of orchestration step. |
| StepStatus | Enum | - | - | - | - | 6 | StepStatus implementation. |
| TalentIntelligenceAgent | - | - | Y | - | - | 3 | Production agent for talent intelli |
| TelemetryAgent | - | - | - | - | - | 3 | Autonomous telemetry emission agent |
| TracingAgent | - | - | - | - | - | 4 | Autonomous distributed tracing agen |
| TrackObservabilityCostAgent | - | - | - | - | - | 1 | function class for standard domain. |

---

## COMPLIANCE HIGHLIGHTS

### Non-Compliant Agents (L2-L4 without Self-Testing)

**Count: 99**

- `SubAtomicAgent` (L2) - base.py
- `CanonBaseAgent` (L2) - base_agents_canon_base_agent_impl.py
- `CanonBaseAgent` (L2) - canon_base_agent_impl.py
- `CodeDeduplicationAgent` (L2) - CodeDeduplicationAgent.py
- `CodeJanitorAgent` (L2) - CodeJanitorAgent.py
- `ContextSnapshot` (L2) - ContextCuratorAgent.py
- `HandoffSummary` (L2) - ContextCuratorAgent.py
- `ContextCuratorAgent` (L2) - ContextCuratorAgent.py
- `ImportNode` (L2) - DependencyDiplomatAgent.py
- `BlastRadius` (L2) - DependencyDiplomatAgent.py
- `DependencyDiplomatAgent` (L2) - DependencyDiplomatAgent.py
- `ModelTier` (L2) - DynamicModelRouterAgent.py
- `RoutingDecision` (L2) - DynamicModelRouterAgent.py
- `ComplexityProfile` (L2) - DynamicModelRouterAgent.py
- `DynamicModelRouterAgent` (L2) - DynamicModelRouterAgent.py
- `StructuralEngineerAgent` (L2) - engineering.py
- `PatternEnforcerAgent` (L2) - engineering.py
- `GitAgent` (L2) - GitAgent.py
- `ArchitectureGovernorAgent` (L2) - governance.py
- `DependencySentinelAgent` (L2) - governance.py
- ... and 79 more

### L0 Agents Without Delegation

**Count: 11**

- `L0SovereignSeverity` - Sovereign event Severity levels for L0 delegation.
- `L0DelegationMixin` - Mixin providing L0 delegation-only capabilities.


- `MaintenanceBaseAgent` - Base class for L0 Maintenance agents with delegati
- `BootstrapAgent` - Autonomous boot integrity agent.
Runs before any v
- `SubAtomicAgent` - Base class for all validation agents with async su
- `agentic_core` - Main agentic core class.
- `FilesystemSSOTReconcilerAgent` - Filesystem-level SSOT reconciler - updates bluepri
- `GravityComplianceValidator` - Brief description of functionality and purpose.
- `HygieneValidator` - Detects 'Rot' within the system:
1. Dead Code (Orp
- `AgenticWorkflowError` - Base exception for agentic workflow.
- `ScriptToAgentClassifier` - Sovereign classifier for script vs agent constitut

### Agents with Healing Capability

**Count: 49**

- `DependencyGraph` (L1)
- `GenerativeGuard` (L1)
- `GovernanceAgent` (L1)
- `HealerAgent` (L1)
- `OrchestratorAgentAndScopeManager` (L1)
- `SystemArchitect` (L1)
- `CodeJanitorAgent` (L2)
- `HealerAgent` (L2)
- `SovereignActionPlaneAgent` (L2)
- `SovereignSandbox` (L2)
- `SovereignToolsmith` (L2)
- `StructuralEngineerAgent` (L2)
- `SystemArchitect` (L2)
- `SystemArchitectAgent` (L2)
- `TerritoryHealerAgent` (L3)
- `TestPilotAgent` (L3)
- `PineconeSovereignAgent` (L4)
- `CodeSSOTEnforcerAgent` (L5)
- `DocstringComplianceAgent` (L5)
- `FilesystemAgent` (L5)
- `GeneratedTest` (L5)
- `GravityEnforcerAgent` (L5)
- `GravityLeakRepairAgent` (L5)
- `HealerAgent` (L5)
- `HygieneGuardianAgent` (L5)
- `ImportUpdater` (L5)
- `InferenceTypeHintAgent` (L5)
- `MethodChange` (L5)
- `MethodChangeDetector` (L5)
- `RegressionOracleAgent` (L5)
- `RegressionTestGenerator` (L5)
- `RegressionTestRunner` (L5)
- `TerritoryHealerAgent` (L5)
- `TypeHintEnforcementAgent` (L5)
- `TypeHintFixer` (L5)
- `AgentFactory` (apps_rg)
- `TestResilientMutatorWithAgents` (apps_rg)
- `TestHealerAgentASTDiff` (tests)
- `TestHealerAgentIntegration` (tests)
- `TestHealerAgentPerformance` (tests)
- `test_agentic_core_model` (tests)
- `test_multi_agent_coordination` (tests)
- `AgentInfo` (misc)
- `AgentInfo` (misc)
- `ContextAwareValidator` (misc)
- `NamingAgent` (misc)
- `NamingNormalizationAgent` (misc)
- `NonConformingAgentFinder` (misc)
- `PlacementResult` (misc)

---

## PHASE 4: VALIDATION EXAMPLES

### L0 Layer Examples

**L0SovereignSeverity**
- Path: `agentic_core\L0_maintenance\bases\MaintenanceBaseAgent.py`
- Inheritance: Enum
- Key Methods: None
- Healing: No
- Testing: Self
- Description: Sovereign event Severity levels for L0 delegation.

**L0DelegationMixin**
- Path: `agentic_core\L0_maintenance\bases\MaintenanceBaseAgent.py`
- Inheritance: None
- Key Methods: None
- Healing: No
- Testing: Self
- Description: Mixin providing L0 delegation-only capabilities.

L0 Table Decision:
- Basic Sel

**MaintenanceBaseAgent**
- Path: `agentic_core\L0_maintenance\bases\MaintenanceBaseAgent.py`
- Inheritance: CanonBaseAgent, L0DelegationMixin
- Key Methods: None
- Healing: No
- Testing: Self
- Description: Base class for L0 Maintenance agents with delegation-only testing.

L0 Table Dec

### L1 Layer Examples

**CanonValidator**
- Path: `agentic_core\L1_cognition\thought_engine\agent_logic.py`
- Inheritance: None
- Key Methods: __init__, _extract_ast_error_message, _validate_ast_match, _process_l1_match, _process_l2_match
- Healing: No
- Testing: None
- Description: The L5 Meta-Learner that validates code against the Canon.

This class implement

**AgentCapability**
- Path: `agentic_core\L1_cognition\thought_engine\agent_registry_enums.py`
- Inheritance: Enum
- Key Methods: None
- Healing: No
- Testing: None
- Description: Standard agent capabilities.

**AgentStatus**
- Path: `agentic_core\L1_cognition\thought_engine\agent_registry_enums.py`
- Inheritance: Enum
- Key Methods: None
- Healing: No
- Testing: None
- Description: Agent operational status.

### L2 Layer Examples

**SubAtomicAgent**
- Path: `agentic_core\L2_execution\tool_registry\base.py`
- Inheritance: None
- Key Methods: __init__, can_run
- Healing: No
- Testing: None
- Description: Base class for all validation agents with async support.

**CanonBaseAgent**
- Path: `agentic_core\L2_execution\tool_registry\base_agents_canon_base_agent_impl.py`
- Inheritance: CanonBaseAgentInterface
- Key Methods: __init__, validate_state
- Healing: No
- Testing: None
- Description: Implementation of canon agent base — lives in Execution context.

This class pro

**CanonBaseAgent**
- Path: `agentic_core\L2_execution\tool_registry\canon_base_agent_impl.py`
- Inheritance: CanonBaseAgentInterface
- Key Methods: __init__, validate_state
- Healing: No
- Testing: None
- Description: Implementation of canon agent base — lives in Execution context.

This class pro

### L3 Layer Examples

**MetaLearningAgent**
- Path: `agentic_core\L3_orchestration\meta_learning\MetaLearningAgent.py`
- Inheritance: AutonomyMixin, AdaptiveExecutionMixin, SelfDiagnosisMixin
- Key Methods: __init__
- Healing: No
- Testing: None
- Description: Sovereign meta-learning agent that evolves system behavior over time.
Now harden

**AgentRegistryValidatorAgent**
- Path: `agentic_core\L3_orchestration\workflow_engines\AgentRegistryValidatorAgent.py`
- Inheritance: None
- Key Methods: __init__, validate_agent_exists, validate_registry, run_validation
- Healing: No
- Testing: None
- Description: L3 Orchestration: Agent Registry Validation
Ensures all agents defined in CANON_

**AgentFactory**
- Path: `agentic_core\L3_orchestration\workflow_engines\agent_factory.py`
- Inheritance: None
- Key Methods: create_healer_agent
- Healing: No
- Testing: None
- Description: Centralized factory for sovereign agent injection.

Phase 9A DDD Compliance:
- O

### L4 Layer Examples

**L4SovereignSeverity**
- Path: `agentic_core\L4_state\bases\StateBaseAgent.py`
- Inheritance: Enum
- Key Methods: None
- Healing: No
- Testing: Self
- Description: Sovereign event Severity levels for L4 subatomic testing.

**L4SubatomicTestingMixin**
- Path: `agentic_core\L4_state\bases\StateBaseAgent.py`
- Inheritance: None
- Key Methods: _run_state_sandbox_tests
- Healing: No
- Testing: Self
- Description: Mixin providing L4 subatomic testing capabilities.

L4 Table Decision:
- Basic S

**StateBaseAgent**
- Path: `agentic_core\L4_state\bases\StateBaseAgent.py`
- Inheritance: CanonBaseAgent, L4SubatomicTestingMixin
- Key Methods: None
- Healing: No
- Testing: Self
- Description: Base class for L4 State agents with subatomic testing.

L4 Table Decision:
- Bas

### L5 Layer Examples

**MCPGuardianAgent**
- Path: `agentic_core\L5_safety\agents\MCPGuardianAgent.py`
- Inheritance: None
- Key Methods: __init__, _emit_critique
- Healing: No
- Testing: Self
- Description: L5 Safety Guardian for MCP integration compliance.

Validates that all MCP integ

**GravityLeakRepairAgent**
- Path: `agentic_core\L5_safety\gravity\GravityLeakRepairAgent.py`
- Inheritance: None
- Key Methods: __init__
- Healing: Yes
- Testing: None
- Description: Converts forbidden static imports from higher layers (L4/L5) into dynamic import

**ImportValidationVisitor**
- Path: `agentic_core\L5_safety\gravity\ImportAgent.py`
- Inheritance: NodeVisitor
- Key Methods: __init__
- Healing: No
- Testing: None
- Description: [SUPREME COURT GATEKEEPER]
Structural visitor to identify imported vs used modul

---

## DISCOVERY VALIDATION

- **Expected agents**: 63+ core + apps
- **Discovered agents**: 401
- **Core agents (L0-L5)**: 240
- **Apps agents**: 66
- **Test agents**: 42
- **Misc agents**: 53

**VALIDATION: PASSED** - Discovery exceeds expected count with zero-loss scanning.

---

*Report generated by Ultra Agent Discovery Scanner*