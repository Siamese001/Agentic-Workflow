=========================================================================================================================================================================================================================
                                                                          AGENTIC SYSTEM — FULL ZERO-LOSS ARCHITECTURE (WIDESCREEN)
                                                                    (DISTRIBUTED STATE INTEGRATION WITH EXTERNAL RAG & PROMPT TAXONOMY)
=========================================================================================================================================================================================================================

=========================================================================================================================================================================================================================
  APPS_* LAYER (CLIENT & APPLICATION INTERFACES) — ZERO INTERNAL AUTHORITY - GENERATES RAW "WHAT" THAT ENTERS THE SYSTEM
=========================================================================================================================================================================================================================

          +-----------------------------------------+                      +-----------------------------------------+                      +-----------------------------------------+
          | apps_interactive                        |                      | apps_autonomous                         |                      | apps_admin                              |
          |-----------------------------------------|                      |-----------------------------------------|                      |-----------------------------------------|
          | - Chat UIs / CLI tools                  |                      | - Webhook receivers                     |                      | - Direct API endpoints                  |
          | - Direct API endpoints                  |                      | - Direct API endpoints                  |                      | - System event listeners                |
          | - Human-in-the-loop views               |                      | - System event listeners                |                      | - Telemetry monitors                    |
          +-----------------------------------------+                      +-----------------------------------------+                      +-----------------------------------------+
                        |                                                               |                                                               |
                        | (Initiates)                                                   | (Triggers)                                                    | (Routes via API)
                        v                                                               v                                                               v

=========================================================================================================================================================================================================================
  ENTRY PRODUCERS (NO AUTHORITY)                                                                                                                      STATE BUS (ANCHOR PORTION)
=========================================================================================================================================================================================================================

      [ EXTERNAL KNOWLEDGE ]                     USER REQUEST                                SYSTEM EVENT                               ADMIN REQUEST              [ EXTERNAL MODEL REGISTRY ]
      +--------------------+                           |                                           |                                          |                    +-------------------------+
      |  Vector Databases  |                           v                                           v                                          v                    |  Weights & Checkpoints  |
      |  NoSQL / Documents |          +------------------------------------------+  +-----------------------------------------+  +---------------------------------------------------------------+
      | [C0] & [CACHE_LOCK]|          | L1 – THINKING LAYER                      |  | L6 – DETECTION (PASSIVE GUARDIANS)      |  | L4: BLUEPRINT VAULT & PROD DB [I::IMemoryStore]               |
      +--------------------+          |------------------------------------------|  |-----------------------------------------|  |---------------------------------------------------------------|
               |                      | - Generates [U0: USER PROMPT] (ZERO auth)|  | - [TLM] CROSS-LAYER TELEMETRY           |  | [ RULES ] - L4 never authorizes. L4 never executes.           |
               | (Semantic Search)    | - Reads L4 active model version          |  | - [SGNL] ANOMALY SIGNAL GENERATOR       |  |           - Future executions use updated versions via L0.    |
               +--------------------->| - Retrieval from RAG index (READ only)   |  | - [RCA] ROOT CAUSE ANALYSIS (RCA)       |  |           - All ML improvements written as versioned updates. |
                                      | - Augments prompt with [C0] Context      |  | - Cannot decide next action             |  | [ PROMPTS]- [S0: SYSTEM] Rulebooks (ABSOLUTE Authority)       |
                                      | - Cannot approve / Cannot execute        |  | - Monitors [COG_TELEMETRY] integrity    |  |           - [I0: INSTRUCTIONAL] Mixins (GOVERNED Authority)   |
                                      | - [LOG] LOG ORIGINAL USER INTENT         |  | ML Integration:                         |  | [ STATE ] - [TMPL] REASONING TEMPLATES, [SYNC] TEAM MEMORY    |
                                      | ML Integration:                          |  | • Improves anomaly classifiers          |  |           - [TOOL] TOOL & CAPABILITY INVENTORY, Policy VC     |
                                      | • Model calibration                      |  | • Refines signal grouping               |  | [ RAG ]   - [TRTH] ANCHOR KNOWLEDGE DRIFT (IMemoryStore)      |
                                      | • Drift detection                        |  |                                         |  |           - Embedding Model Reference                         |
                                      +------------------------------------------+  +-----------------------------------------+  |           - Retrieval Top-K / Thresholds                      |
                                                || (WRITE: [U0] Proposals)                    || (WRITE: Structured Telemetry)   | [ LOGS ]  - Drift Metrics, Escalations, Meta-Learning         |
                                                =================================================================================+---------------------------------------------------------------+
                                                                             (READ: Model Config, RAG Config, Detection Config Parameters)                                                  ^^
                                                                                                                                                                                            ||
============================================================================================================================================================================================||===========
  CONTROL SPINE (AUTHORITY BEGINS HERE)                                                                                                                                                     ||
============================================================================================================================================================================================||===========
                                                |                                             |                                                                                             ||
                                                | Proposals / Events                          |                                                                                             ||
                                                v                                             v                                                                                             ||
                                                           +-----------------------------------------------------------------------+                                                        ||
                                                           | L0 – ROUTING (THE FIRST AUTHORITY GATE)                               | <==============================================|| (READ: Routing Config)
                                                           |-----------------------------------------------------------------------|                                                        ||
                                                           | - Classifies intent vs. L4 Routing State                              |      +---------------------------------------------------------+
                                                           | - [JIT] Load context on-demand via the "Elevator Shaft" (L0 <-> L5)   |      | [ META-LEARNING & OPTIMIZATION BUS ]                    |
                                                           | - Cannot evaluate rules / Cannot execute                              |      |---------------------------------------------------------|
                                                           |                                                                       |      | 1. ANALYZE: Patterns from Logs (Latency, Quality)       |
                                                           | ML Integration:                                                       |      | 2. OPTIMIZE: Adjusts weights, thresholds, & configs     |
                                                           | [1. Pattern Analysis ]=======================(Match Intent Logs)======|======>| 3. COMMIT: Writes new versions to L4 Anchor             |
                                                           | [2. Threshold Tuning ]=======================(Assess Risk Limits)=====|======>+---------------------------------------------------------+
                                                           | [3. Path Optimization]=======================(Optimize Routing)=======|=======================================================>||
                                                           +-----------------------------------------------------------------------+                                                        ||
                                                                                               v                                                                                            ||
                                                           +-----------------------------------------------------------------------+                                                        ||
                                                           | ASSEMBLY STAGE (SANDBOX AIRLOCK & DETERMINISTIC COMPOSITION)          |                                                        ||
                                                           |-----------------------------------------------------------------------|                                                        ||
                                                           | [S0: SYSTEM]        - Hard-coded constitutions & invariants (L4)      |                                                        ||
                                                           | [I0: INSTRUCTIONAL] - Identity & "Mixin" behaviors (L4)               |                                                        ||
                                                           | [D0: INJECTIONS]    - Semantic fences & tool constraints (L5)         |                                                        ||
                                                           | [C0: DEPENDENCY]    - Elevator Shaft/RAG injected knowledge           |                                                        ||
                                                           | [U0: USER PROMPT]   - Raw intent (L1)                                 |                                                        ||
                                                           | => Final Package = [S0] + [D0] + [I0] + [C0] + [U0]                   |                                                        ||
                                                           | => [BLOCK] BLOCK HOSTILE INPUT VECTORS (Neutralize Attack Paths)      |                                                        ||
                                                           | => [SPLIT] SPLIT INTO ATOMIC TASKS (Limit Scope, Prevent Collateral)  |                                                        ||
                                                           | - Emits: Governed Payload => Passes to Paths A / B / C / D            |                                                        ||
                                                           +-----------------------------------------------------------------------+                                                        ||
                                                                                               v                                                                                            ||
                             +-----------------------------------------+-----------------------+------------------+-----------------------------------+                                     ||
                             |                                         |                       |                  |                                   |                                     ||
                             v                                         v                       |                  v                                   v                                     ||
          +=======================================+ +=======================================+ +=======================================+ +===========================+                           ||
          | PATH A                                | | PATH B                                | | PATH C                                | | PATH D                    |                           ||
          | READ-ONLY RESPONSE                    | | POLICY CHECK FIRST                    | | EXECUTE DIRECTLY                      | | HUMAN REVIEW FIRST        |                           ||
          +=======================================+ +=======================================+ +=======================================+ +===========================+                           ||
                          |                                        |                                       |                                     |                                          ||
                          v                                        v                                       v                                     v                                          ||
          +-------------------------------+         +-------------------------------+       +-------------------------------+       +---------------------------+                               ||
          | Final Response                |         | L3 – ORCHESTRATION [IOrch]    |       | L3 – ORCHESTRATION [IOrch]    |       | L3 – ORCHESTRATION [IOrch]|                               ||
          |-------------------------------|         |-------------------------------|       |-------------------------------|       |---------------------------|                               ||
          | - No system mutation          |         | - [HNDS] SEQUENTIAL HANDSHAKE |       | - [HNDS] SEQUENTIAL HANDSHAKE |       | - Prepares review artifact|                               ||
          | - Logged outcome              |         | - [SYNC] WORK INSTRUCT SYNTH  |       | - [SYNC] WORK INSTRUCT SYNTH  |       +---------------------------+                               ||
          |                               |         | - [ESC] ESCALATE TO L5 GUARD  |       | - [ESC] ESCALATE TO L5 GUARD  |                      |                                            ||
          | ML consumes outcome           |         | - [GATE] Block hallucination  |       | ML Integration:               |                      v                                            ||
          |                               |         | - [SEED] Force strict heal    |       | [1. Efficiency Tuner]         |======(Evaluate Bottlenecks)======================================>||
          |                               |         +-------------------------------+       | [2. Planning Optimization]    |======(Tune Pipeline Efficiency)==================================>||
          +-------------------------------+                        |                        +-------------------------------+                                                                   ||
                          |                                        v                                       |                                                                                    ||
                          |                         +-------------------------------+                      |                        +---------------------------+                               ||
                          |                         | L5 – SAFETY [I::IValidator]   |                      |                        | HUMAN REVIEW              |                               ||
                          |                         |-------------------------------|                      |                        |---------------------------|                               ||
                          |                         | - [RISK] RISK TIER CLASSIFY   |                      |                        | - Manual approve/reject   |                               ||
                          |                         | - [STMP] COMPLIANCE HASH/STAMP|                      |                        |                           |                               ||
                          |                         | - [STOP] HARD STOP REJECTION  |                      |                        | ML Integration:           |                               ||
                          |                         | - [BLOCK] BLOCK HOSTILE INPUT |                      |                        | [1. Reviewer Calibration] |======(Evaluate Human Bias)====>||
                          |                         | ML Integration:               |                      v                        +---------------------------+                               ||
                          |                         | [1. Anomaly Classifier]       |======(Track False Pos/Neg)===============================================================================>||
                          |                         |                               |======(Analyze Block Accuracy)============================================================================>||
                          |                         | [2. Policy Optimization]      |======(Tune Rule Strictness)==============================================================================>||
                          |                         |                               |======(Adapt Threshold Config)============================================================================>||
                          |                         +-------------------------------+                      |                                     |                                          ||
                          |                                        |                                       |                                     | (If Approved)                            ||
                          |                                        v                                       v                                     v                                          ||
                          |                         +===========================================================================================================+                               ||
                          |                         | \\\ L2 – UNIFIED EXECUTION CORE (THE MUTATION SANDBOX & SINGULAR BOTTLENECK FOR PATHS B, C, D)        /// |                               ||
                          |                         |===========================================================================================================|                               ||
                          |                         |       [ SANDBOX EXECUTION & HEALING LOOP ]         |         [ OPTIMIZATION & RAG SYNC ]                  |                               ||
                          |                         |                                                    |                                                      |                               ||
                          |                         |  +-> [L2.1: Validator] [I::ILeaseVerifier]         |  ML Integration:                                     |                               ||
                          |                         |  |    -> [FREEZ] FREEZE CLEAN SYSTEM STATE         |  [1. Failure Classifier] =======(Learn Syntax Errors)===============================>||
                          |                         |  |    -> [CLAIM] CLAIM EXCLUSIVE WRITE ACCESS      |  [2. Resource Predictor] =======(Optimize Compute Cost)==============================>||
                          |                         |  |    -> [GUARD] PRESERVE EXISTING CODE INTEGRITY  |  [3. RL Rollback Refiner]=======(Self-Correct Heal Logic)============================>||
                          |                         |  |         v                                       |                                                      |                               ||
                          |                         |  |   [L2.2: Execution] [I::IMemoryStore]           |  [ DATA MUTATION ]         [ EXTERNAL RAG ]          |                               ||
                          |                         |  |    -> [WRITE] COMMIT VERIFIED STATE CHANGE      |  - Sandbox Snapshot Revert +--------------+          |                               ||
                          |                         |  |    -> [CEIL] TERMINATE STUCK COMPUTE CYCLES     |  - Embedding generation    | Vector Store |          |                               ||
                          |                         |  |         v                                       |  - Vector store write ---> +--------------+          |                               ||
                          |                         |  |   [Evaluation     ]--+                          |  - [TRTH] ANCHOR KNOWLEDGE | [ASYNC_SYNC] |          |                               ||
                          |                         |  |         | (Fail)     |                          |    DRIFT OVER TIME         +--------------+          |                               ||
                          |                         |  |         v            |                          |                                                      |                               ||
                          |                         |  +-- [L2.3: Healer   ]  |                          |                                                      |                               ||
                          |                         |  |   [I::IHealer]       |                          |                                                      |                               ||
                          |                         |  |-[ROOT] CAPTURE ROOT  |                          |                                                      |                               ||
                          |                         |  |-[RESET] REVERT STATE |                          |                                                      |                               ||
                          |                         |  |-[CURE] FIX AND RETRY |                          |                                                      |                               ||
                          |                         |                         |                          |                                                      |                               ||
                          |                         |  (Proceed to Decision)<-+                          |                                                      |                               ||
                          |                         +===========================================================================================================+                               ||
                          |                                                                        |                                                                                            ||
                          v                                                                        v                                                                                            ||
          +----------------------------------------------------------------------------------------------------------------------------------------------------------------+                    ||
          | FINAL DECISION / OUTCOME LOGGING                                                                                                                               |                    ||
          |----------------------------------------------------------------------------------------------------------------------------------------------------------------|                    ||
          | - Outcome and state diffs are logged and versioned                                                                                                             |                    ||
          | - [SYNC] UPDATE SHARED TEAM MEMORY (Non-blocking state update occurs only after L2.2 confirms)                                                                 |                    ||
          | - [RECON] VERIFY DATA MATCHES REALITY (Detect ghost mutations across state layers)                                                                             |                    ||
          | - Metrics captured: Execution Latency, Outcome Accuracy, Compute Cost, Human Correction Rate                                                                   |                    ||
          +----------------------------------------------------------------------------------------------------------------------------------------------------------------+                    ||
                                                                                   |                                                                                                            ||
                                                                                   +===(ZERO-LOSS LOOP: COMMIT TO L4 VIA META-LEARNING BUS)====================================================>||

=============================================================================================================================================================================================================
  CRITICAL DISSEMINATION GUARANTEES
=============================================================================================================================================================================================================
| 1. NO SKIPPING THE SAFETY GATES: Prevents un-governed direct execution.                                                                                                                                   |
| 2. ALWAYS ATTACH THE SAFETY FENCES: Stops agents from exceeding roles.                                                                                                                                    |
| 3. ONLY LOAD DATA WHEN NEEDED: Keeps context windows lean/accurate.                                                                                                                                       |
| 4. HEALED PLANS MUST RE-CLEAR SAFETY: Erases "trust" for corrected actions.                                                                                                                               |
| 5. DON'T LOSE DATA ON ERROR: Ensures healers have full context.                                                                                                                                           |
| 6. ISOLATE EVERY CHANGE IN SANDBOX: Zero durable damage on failure.                                                                                                                                       |
| 7. ONLY USE PRE-APPROVED SYSTEM TOOLS: Physically blocks rogue function calls.                                                                                                                            |
| 8. BREAK TASKS INTO TINY PIECES: Minimizes blast radius of errors.                                                                                                                                        |
| 9. PROTECT KNOWLEDGE FROM AGENT DRIFT: Prevents agents from corrupting truth.                                                                                                                             |
| 10. STOP AGENTS FROM BURNING MONEY: Kills infinite loops and spikes.                                                                                                                                      |
| 11. FRESH DATA ONLY AT RUNTIME: Prevents outdated "context rot."                                                                                                                                          |
| 12. RECORD THE WHY, NOT WHAT: Focuses telemetry on decision logic.                                                                                                                                        |
| 13. REMOVE ALL PROMPT HIJACK ATTEMPTS: Neutralizes "ignore instructions" attacks.                                                                                                                         |
| 14. SHARE MEMORY ACROSS ALL AGENTS: Prevents agents from colliding/stalling.                                                                                                                              |
| 15. DOUBLE-CHECK DATA MATCHES THE WORLD: Detects "ghost" or hidden mutations.                                                                                                                             |
=============================================================================================================================================================================================================