==================================================================================================================================================
                             SOVEREIGN ARCHITECTURE: HIERARCHY & CAPABILITY MAP (v4.0 — HARDENED)
                                          (A+++++ ZERO-LOSS WIDESCREEN ASCII OVERWRITE)
==================================================================================================================================================

[ LEGEND ]
! [[ ]] = ROOT FOUNDATION (The Unchangeable Core / Infrastructure SSOT)
~ ~~ ~~ = MIXIN CAPABILITY (Power-up: "Has-A" / Behavior Bundle)
+ < >   = LAYER TEMPLATE (Identity: "Is-A" / Functional Logic)
# { }   = CONCRETE AGENT (Production Instance / Final Class)
@ [ ]   = DECISION FLOW (Governance & State Mapping)

==================================================================================================================================================
[ STEP 1: ! [[ SovereignBaseAgent ]] — ROOT SINGLE SOURCE OF TRUTH (SSOT) ! ]
(Grandparent Foundation: Versioning, Name, Core Registry)
==================================================================================================================================================
                                         |
                                         v
         /================================================================================================\
         | @ [ MIXIN BUNDLE: CAPABILITY DEFINITION ]                                                      |
         |------------------------------------------------------------------------------------------------|
         | ~ HealerMixin ~              (Self-Repair / Rollback / AST Surgery)             |
         | ~ MCPHardenedMixin ~         (Security / Multi-Source Auth / Audit)           |
         | ~ RateLimitMixin ~           (Resource Protection / Token Budgets)                |
         | ~ StateValidationMixin ~     (Data Integrity / High-Res AST Checks)             |
         | ~ ContextPropagationMixin ~  (Distributed Tracing / Memory Manager)             |
         | ~ SubatomicTestingMixin ~    (Fine-Grained Validation / Sandbox Setup)           |
         \================================================================================================/
                                         |
                                         | (MRO Inheritance Path: Core -> Mixins -> Layer)
                                         v
==================================================================================================================================================
[ STEP 2: + LAYER LEVEL: THE ACTIVE TEMPLATES + ]
(Layer Leads Select Mixins per Identity — Strictly Downward Static Imports)
==================================================================================================================================================

    + < L6ObservabilityBaseAgent > (Metrics, Dashboarding, Passive Detection)
                   |
    + < L5SafetyBaseAgent >        (Guardrails, EvaluatorBase, Policy Enforcement)
                   |               ** THE ELEVATOR SHAFT ** (Runtime Seam to L0)
    + < L4StateBaseAgent >         (Knowledge, RAG, Redis/Pinecone, Drift State)
                   |
    + < OrchestrationBaseAgent >   (SupervisorBase, Task Planning, Delegation)
                   |
    + < L2ExecutionBaseAgent >     (ToolInterfaceBase, Sandbox, AST Commit Authority)
                   |
    + < L1CognitionAgent >         (Reasoning, Adaptive Execution, Proposal Gen)
                   |
    + < L0MaintenanceAgent >       (Housekeeping, Foundation Loader, Root Registry)

==================================================================================================================================================
[ STEP 3: # PRODUCTION LEVEL: THE ACTUAL FLEET # ]
(268 Concrete Instance Classes — Final Mixin Inheritance)
==================================================================================================================================================
|                                                                                                                                                |
|    # { BootstrapAgent }    # { GospelSyncAgent }    # { HealAgent }    # { SovereignRAGAgent }                                                |
|                                                                                                                                                |
==================================================================================================================================================

==================================================================================================================================================
                                             ARCHITECTURAL INTEGRITY GUARANTEES
==================================================================================================================================================
| 1. SSOT ANCHOR: All agents ultimately subclass [[ SovereignBaseAgent ]] for unified versioning and name registration.              |
| 2. MIXIN ATOMICITY: Capabilities like ~HealerMixin~ are modular, allowing agents to "Has-A" specific behaviors without core mutation.|
| 3. MRO STACKING: Class resolution follows the strict path: Foundation -> Mixins -> Layer Identity -> Concrete Instance.       |
| 4. IMPORT HYGIENE: Static imports move strictly downward (L6->L0); upward moves occur ONLY via the L0 Elevator Shaft at runtime.    |
| 5. RESOLUTION SYMMETRY: L2.2 and L2.3 utilize the ~HealerMixin~ surgical manifests for zero-loss, AST-based system recovery.      |
==================================================================================================================================================
