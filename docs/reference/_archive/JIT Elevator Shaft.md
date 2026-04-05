======================================================================================================================================================================
                                          AGENTIC SYSTEM — THE "ELEVATOR SHAFT" (JIT STATE SYNCHRONIZATION)
======================================================================================================================================================================
  [ THE TOP LAYER: INGESTION & OBSERVABILITY ]                                [ THE SIDE LAYER: THE SOURCE OF TRUTH ]
+---------------------------------------------------+                         +--------------------------------------------------------------------------------------+
| L1: COGNITIVE STUDIO / L6: OBSERVABILITY          |                         | L4: STATE, MEMORY & PERSISTENCE (THE READ-ONLY STATE BUS)                            |
|---------------------------------------------------|                         |--------------------------------------------------------------------------------------|
| - [L1] Ingests Intent & Priming Context           |======(Read-Only)=======>| - P1: COGNITIVE REGISTRY (Active Models, System Prompts, RAG Singleton Factory)      |
| - [L6] ANOMALY ENGINE: Active Drift Scores,       |                         | - P2: CAPABILITY REGISTRY (Tool Availability, API Credentials, L4 Policy Configs)    |
|        Threat Signals                             |                         | - P3: WORKFLOW MEMORY (Active Job States, Dependency DAGs)                           |
+---------------------------------------------------+                         +--------------------------------------------------------------------------------------+
                          |                                                                             ||
                          |                                                                             || (The Elevator Shaft - Vertical Read-Only State Bus)
                          v                                                                             ||
========================================================================================================||============================================================
  [ L0: ROUTING & TRAFFIC CONTROL ]                                                                     ||
+-----------------------------------------------------------------------------------------+             ||
| L0: JIT STATE INJECTION                                                                 |<============||
|-----------------------------------------------------------------------------------------|             ||
| - [JIT] Load context on-demand via the "Elevator Shaft" (L0 <-> L5).                    |             ||
| - [PULL] Active Routing Weights, Toggles, and RLHF Heuristics.                          |             ||
| - [PULL] Current Tool Inventory, Budget Forecast, & Rate Limits.                        |             ||
| - [PULL] L1 Intent vs. L6 Anomaly/Drift Scores (Correlate Risk).                        |             ||
|                                                                                         |             ||
| - [!] JIT fetch ensures L0 routes using the exact same state that L5 will use to verify.|             ||
+-----------------------------------------------------------------------------------------+             ||
                          |                                                                             ||
                          v (Dispatches Plan to PATH A / B / C / D)                                     ||
+-----------------------------------------------------------------------------------------+             ||
| L3: ORCHESTRATION (PATH B / PATH C / PATH D)                                            |             ||
|-----------------------------------------------------------------------------------------|             ||
| - Proposes sequenced DAG execution plan or patched `MODIFY_DIFF`.                       |             ||
| - Resolves simultaneous escalations before handing off to Safety.                       |             ||
|                                                                                         |             ||
| L3 ORCHESTRATION ENGINES:                                                               |             ||
| - DAGManager: Manages execution DAG with dependency resolution                          |             ||
| - Orchestrator: Central nervous system (modes: HEALING, REASONING, VALIDATION, UNIFIED) |             ||
| - DecompositionOrchestrator: Multi-agent task decomposition engine                      |             ||
| - AutonomousExecutionEngine: Executes action nodes with tool invocation                 |             ||
| - ActionNode: Individual DAG node with tool intent and dependencies                     |             ||
| - ToolIntentExecutor: Executes tool calls with capability token validation              |             ||
+-----------------------------------------------------------------------------------------+             ||
                          |                                                                             ||
                          v (Passes DAG / Patches to Safety Guard)                                      ||
========================================================================================================||============================================================
  [ L5: SAFETY & COMPLIANCE GUARD ]                                                                     ||
+-----------------------------------------------------------------------------------------+             ||
| L5: JIT POLICY HYDRATION                                                                |<============||
|-----------------------------------------------------------------------------------------|             ||
| - Evaluates proposed DAG against the freshest L4 policies.                              |             ||
| - Mints Compliance Hash/Stamp.                                                          |             ||
| - [PULL] Active Risk Threshold Configs & L4 Policy Configs.                             |             ||
| - [PULL] Dynamic Safety Rule Strictness (Tuned by Meta-Learning).                       |             ||
| - [PULL] Historical Path D Override Logs (To evaluate False Positives).                 |             ||
|                                                                                         |             ||
| - [!] Evaluates the proposed plan against the mathematical present, not the past.       |             ||
+-----------------------------------------------------------------------------------------+             ||
                          |                                                                             ||
                          v (Grants Auth Stamp / Handoff to Sandbox)                                    ||
========================================================================================================||============================================================
  [ L2: UNIFIED EXECUTION CORE ]                                                                        ||
+-----------------------------------------------------------------------------------------+             ||
| L2: JIT CAPABILITY PROVISIONING                                                         |<============||
|-----------------------------------------------------------------------------------------|             ||
| - Initializes the SandboxEnvelope.                                                      |             ||
| - Establishes [FREEZE] state.                                                           |             ||
| - [PULL] ToolBudget Caps (compute_ms, memory_mb, stdout_bytes).                         |             ||
| - [PULL] CapabilityToken (Scoped + Unexpired credentials).                              |             ||
| - [PULL] [C0] RAG Informational Context (Seed Packs from Singleton Factory).            |             ||
|                                                                                         |             ||
| - [!] Once L2 pulls state, the `[FREEZE]` locks the environment. Elevator bottoms out.  |             ||
+-----------------------------------------------------------------------------------------+             ||
                          |                                                                             ||
                          v (Immutable Execution Context Frozen)                                        \/
======================================================================================================================================================================
  CORE SYNCHRONIZATION DATA CONTRACTS
======================================================================================================================================================================
| [JIT] State Invariant   : Context loaded on-demand via the Elevator Shaft MUST match the SemanticClock of the active request.                                      |
| [2] SandboxEnvelope     : [InstructionPacket, ToolBudget] -> Bound to the specific CapabilityToken pulled during the JIT sync.                                     |
| [TRTH] Knowledge Anchor : RAG Embeddings ([C0]) pulled down the shaft are strictly Informational ONLY. Never mutates routes/safety/tiers.                          |
| [25] ActionNode         : [node_id, tool_intent, dependencies, status, result] -> Individual DAG execution node                                                    |
| [26] OrchestratorMode   : Enum[HEALING, REASONING, VALIDATION, UNIFIED] -> Orchestration mode selector                                                             |
| [27] WorkflowContext    : [workflow_id, current_phase, state_snapshot] -> Execution context for orchestration                                                      |
======================================================================================================================================================================
