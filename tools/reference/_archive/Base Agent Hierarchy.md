==================================================================================================================================================
                             SOVEREIGN ARCHITECTURE: HIERARCHY & CAPABILITY MAP (v4.1 — REPO-VERIFIED)
                                          agentic_core/base_agents/ — ground-truth as of agent_discovery_full.json
==================================================================================================================================================

[ LEGEND ]
! [[ ]] = ROOT FOUNDATION (The Unchangeable Core / Infrastructure SSOT)
~ ~~ ~~ = MIXIN CAPABILITY (Power-up: "Has-A" / Behavior Bundle)
+ < >   = LAYER BASE CLASS (Identity: "Is-A" / Functional Logic)
# { }   = CONCRETE AGENT (Production Instance / Final Class)
@ [ ]   = DECISION FLOW (Governance & State Mapping)

==================================================================================================================================================
[ STEP 1: ! [[ SovereignBaseAgent ]] — ROOT SINGLE SOURCE OF TRUTH (SSOT) ! ]
(Root @dataclass Foundation: Security Validation, Core Registry, V15 Gateway)
  File: agentic_core/base_agents/SovereignBaseAgent.py
==================================================================================================================================================
                                         |
                                         v
         /================================================================================================\
         | @ [ MIXIN BUNDLE INJECTED DIRECTLY INTO SovereignBaseAgent (MRO order) ]                      |
         |------------------------------------------------------------------------------------------------|
         | ~ AtomicExecutionMixin ~        (Rollback / Atomic Commit Authority)                          |
         | ~ infrastructure_mixin ~        (Core Infrastructure / Legacy Gateway)                        |
         | ~ SubatomicTestingMixin ~        (Fine-Grained Validation / Sandbox Setup)                    |
         | ~ ConfigMixin ~                 (Configuration Management)                                    |
         | ~ LLMProviderMixin ~            (LLM Provider Abstraction)                                    |
         | ~ EmbeddingMixin ~              (Embedding Model Access)                                      |
         | ~ HealingStrategyMixin ~        (Self-Repair / Rollback / AST Surgery)                       |
         | ~ ValidatorMixin ~              (Data Integrity / High-Res AST Checks)                        |
         | ~ AuditTrailMixin ~             (Black-Box Telemetry / Audit Log)                             |
         | ~ MetaLearningClientMixin ~     (Healing Pattern Memory / Redis + Pinecone)                   |
         | ~ GoldenContextMixin ~          (Anti-Context Drift / Token Overload Guard)                   |
         | ~ RuntimeSafetyMixin ~          (Process Lifecycle / Operational Safety)                      |
         \================================================================================================/
                                         |
                                         | (MRO Flow: Specialized -> Layer Base -> SovereignBaseAgent -> [Mixins] -> object)
                                         v
==================================================================================================================================================
[ STEP 2: + LAYER BASE CLASSES (agentic_core/base_agents/) + ]
(Each layer base subclasses SovereignBaseAgent — strictly downward static imports)
==================================================================================================================================================

    + < L6ObservabilityBase >   (Metrics, Dashboarding, Telemetry, Log Aggregation)
                   |              File: agentic_core/base_agents/L6ObservabilityBase.py
    + < L5SafetyBase >          (Guardrails, Gravity Checks, Policy Enforcement)
                   |              File: agentic_core/base_agents/L5SafetyBase.py
                   |              ** THE ELEVATOR SHAFT ** (Runtime Seam to L0)
    + < L4StateBase >           (Validation Context, State Ledger, Memory Persistence)
                   |              File: agentic_core/base_agents/L4StateBase.py
    + < L3OrchestrationBase >   (Workflow Coordination, Task Planning, Delegation)
                   |              File: agentic_core/base_agents/L3OrchestrationBase.py
    + < L2ExecutionBase >       (Tool Registry, MCP Protocol, Action Execution)
                   |              File: agentic_core/base_agents/L2ExecutionBase.py
    + < L1CognitionBase >       (Intent Analysis, Memory Retrieval, Meta-Learning)
                   |              File: agentic_core/base_agents/L1CognitionBase.py
    + < L0RoutingBase >         (Boot-time Routing, Healing Delegation, Root Registry)
                   |              File: agentic_core/base_agents/L0RoutingBase.py

    + < LightweightAgentBase >  (Minimal-MRO alternative: CostGuardrail, Context,
                                  Tracing, Caching, Metrics — no SovereignBaseAgent)
                                  File: agentic_core/base_agents/LightweightBase.py

==================================================================================================================================================
[ STEP 3: # PRODUCTION LEVEL: THE ACTUAL FLEET # ]
(186 Concrete Agent Classes — verified via artifacts/discovery/agent_discovery_full.json)
  Layer breakdown: L0(6) L1(12) L2(11) L3(14) L4(4) L5(84) L6(14) apps_lic(27) apps_rg(12) apps_shared(1) knowledge(1)
==================================================================================================================================================
|                                                                                                                                                |
|  # { BootstrapAgent }  # { GospelSyncAgent }  # { BenchmarkingAgent }  # { DocstringComplianceAgent }  # { ASTValidatorAgent }               |
|                                                                                                                                                |
==================================================================================================================================================

==================================================================================================================================================
                                             ARCHITECTURAL INTEGRITY GUARANTEES
==================================================================================================================================================
| 1. SSOT ANCHOR: All agents ultimately subclass [[ SovereignBaseAgent ]] for unified versioning and name registration.              |
| 2. MIXIN ATOMICITY: Capabilities like ~HealingStrategyMixin~ are modular, injected at root so all agents inherit them.             |
| 3. MRO STACKING: Class resolution follows: Specialized Mixins -> Layer Base -> SovereignBaseAgent -> [Root Mixins] -> object.      |
| 4. IMPORT HYGIENE: Static imports move strictly downward (L6->L0); upward moves occur ONLY via the L0 Elevator Shaft at runtime.   |
| 5. LIGHTWEIGHT PATH: LightweightAgentBase provides a shallow-MRO (~8 classes) alternative for simple agents that skip healing.     |
==================================================================================================================================================
