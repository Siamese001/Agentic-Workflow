=========================================================================================================================================================
                                                 AGENTIC SYSTEM — FULL ZERO-LOSS ARCHITECTURE (COMPACT)
                                           (DISTRIBUTED STATE INTEGRATION WITH EXTERNAL RAG & PROMPT TAXONOMY)
=========================================================================================================================================================

=========================================================================================================================================================
  APPS_* LAYER (CLIENT INTERFACES) — ZERO INTERNAL AUTHORITY
=========================================================================================================================================================
          +-----------------------------+          +-----------------------------+          +-----------------------------+
          | apps_interactive            |          | apps_autonomous             |          | apps_admin                  |
          |-----------------------------|          |-----------------------------|          |-----------------------------|
          | - Chat UIs / CLI tools      |          | - Webhook receivers         |          | - Control Dashboards        |
          | - Human-in-the-loop views   |          | - System event listeners    |          | - Telemetry monitors        |
          +-----------------------------+          +-----------------------------+          +-----------------------------+
                        |                                          |                                          |
                        v (Initiates)                              v (Triggers)                               v (Routes via API)

=========================================================================================================================================================
  ENTRY PRODUCERS (NO AUTHORITY)                                                                              STATE BUS (ANCHOR)
=========================================================================================================================================================
      [ EXTERNAL KNOWLEDGE ]           USER REQUEST               SYSTEM EVENT               ADMIN REQUEST      [ EXTERNAL MODEL REGISTRY ]
      +--------------------+                 |                          |                          |            +-------------------------+            ^^
      |  Vector Databases  |                 v                          v                          v            |  Weights & Checkpoints  |            ||
      | [C0] & [CACHE_LOCK]|  +----------------------------+  +----------------------------+  +--------------------------------------------+            ||
      +--------------------+  | L1 – THINKING LAYER        |  | L6 – DETECTION (GUARDIAN)  |  | L4: BLUEPRINT VAULT & PROD DB              | <===========||
               |              |----------------------------|  |----------------------------|  |--------------------------------------------|            ||
               | (RAG Read)   | - [U0] USER PROMPT         |  | - [TLM] CROSS-LAYER TLM    |  | [RULES] L4 never authorizes/executes.      |            ||
               +------------->| - [C0] Context Retrieval   |  | - [SGNL] ANOMALY SIGNAL    |  | [STATE] [TMPL] REASONING, [TOOL] INVENTORY |            ||
                              | - [LOG] LOG USER INTENT    |  | - [RCA] ROOT CAUSE ANALYSIS|  | [RAG  ] [TRTH] ANCHOR KNOWLEDGE DRIFT      |            ||
                              +----------------------------+  +----------------------------+  +--------------------------------------------+            ||
                                         || (WRITE: [U0])           || (WRITE: Telemetry)                                                               ||
======================================================================================================================================================||=
  CONTROL SPINE (AUTHORITY STARTS HERE)                                                                                                               ||
======================================================================================================================================================||=
                                         |                          |                                                                                 ||
                                         v                          v                                                                                 ||
                        +-----------------------------------------------------------------------+                                                     ||
                        | L0 – ROUTING (THE FIRST AUTHORITY GATE)                               | <========================(READ: Routing Config)=====||
                        |-----------------------------------------------------------------------|                                                     ||
                        | - [JIT] Load context via "Elevator Shaft" (L0 <-> L5)                 |   +-------------------------------------------+     ||
                        | - Classifies intent vs. L4 Routing State                              |   | [ META-LEARNING & OPTIMIZATION BUS ]      |     ||
                        |                                                                       |   |-------------------------------------------|     ||
                        | ML Integration:                                                       |   | 1. [PULL] DATA (From L4 Black Box Audit)  |     ||
                        | [1. Pattern Analysis]========(Match Intent Logs)======================|==>| 2. ANALYZE: [RCA] ROOT CAUSE ANALYSIS     |     ||
                        | [2. Threshold Tuning]========(Assess Risk Limits)=====================|==>| 3. OPTIMIZE & COMMIT: Writes to L4 Anchor |====>||
                        +-----------------------------------------------------------------------+   +-------------------------------------------+     ||
                                                          v                                                                                           ||
                        +-----------------------------------------------------------------------+                                                     ||
                        | ASSEMBLY STAGE (SANDBOX AIRLOCK & DETERMINISTIC COMPOSITION)          |                                                     ||
                        |-----------------------------------------------------------------------|                                                     ||
                        | [S0] SYSTEM Rules | [I0] Identity Mixins | [D0] Tool Fences (L5)      |                                                     ||
                        | => [BLOCK] BLOCK HOSTILE INPUTS | [SPLIT] SPLIT INTO ATOMIC TASKS     |                                                     ||
                        +-----------------------------------------------------------------------+                                                     ||
                                                          v                                                                                           ||
          +-----------------------------+-----------------+-----------------+-----------------------------+                                          ||
          v                             v                                   v                             v                                          ||
+=======================+     +=======================+           +=======================+     +=======================+                             ||
| PATH A: READ-ONLY     |     | PATH B: POLICY FIRST  |           | PATH C: EXECUTE DIRECT|     | PATH D: HUMAN REVIEW  |                             ||
+=======================+     +=======================+           +=======================+     +=======================+                             ||
           |                             |                                   |                             |                                          ||
           v                             v                                   v                             v                                          ||
+-----------------------+     +-----------------------+           +-----------------------+     +-----------------------+                             ||
| Final Response        |     | L3 – ORCHESTRATOR     |           | L3 – ORCHESTRATION    |     | L3 – ORCHESTRATOR     |                             ||
|-----------------------|     |-----------------------|           |-----------------------|     |-----------------------|                             ||
| - No system mutation  |     | - [HNDS] HANDSHAKE    |           | - [HNDS] HANDSHAKE    |     | - [MANUAL] Approve    |                             ||
| - Logged outcome      |     | - [SYNC] INSTR SYNTH  |           | - [SYNC] INSTR SYNTH  |     | - [ESC ] To Senior    |                             ||
|                       |     | - [ESC ] TO L5 GUARD  |           | - [ESC ] TO L5 GUARD  |     +-----------------------+                             ||
| ML consumes outcome   |     | - [GATE] Block Halluc |           |    [IF] VIOLATION?    |                |                                          ||
+-----------------------+     +-----------------------+           <=(Yes)===+=== (No)===>      +-------(If Approved)------->||                        ||
           |                             |                                  |                  v                            ||                        ||
           |                             v                                  |       +-----------------------+               ||                        ||
           |                  +-----------------------+                     |       | L5 – SAFETY GATE      | <=============+                         ||
           |                  | L5 – SAFETY GATE      | <===================+       |-----------------------|                                         ||
           |                  |-----------------------|                             | - [STMP] COMPLIANCE   |                                         ||
           |                  | - [RISK] RISK TIER    |                             | - [STOP] HARD STOP    |                                         ||
           |                  | - [STMP] COMPLIANCE   |                             | - [BLOCK] HOSTILE     |======(Evaluate Human Bias)=============>||
           |                  | - [STOP] HARD STOP    |                             +-----------------------+                                         ||
           |                  +-----------------------+                                        |                                                      ||
           |                             |                                                     | (Pass)                                               ||
           |      [RE-ROUTE L1] <==(Fail)+---(Pass)==> [AUTH] STAMP WORK CONTRACT (Paths B & C) |                                                      ||
           |                             v                                                     v                                                      ||
           |           +=======================================================================================================+                      ||
           |           | \\\ L2 – UNIFIED EXECUTION CORE (MUTATION SANDBOX & SINGULAR BOTTLENECK)                          /// |                      ||
           |           |=======================================================================================================|                      ||
           |           |  +-> [L2.1: Validator]  -> [FREEZ] CLEAN STATE | [CLAIM] EXCLUSIVE WRITE | [GUARD] INTEGRITY        |                      ||
           |           |  |   [L2.2: Execution]  -> [WRITE] COMMIT VERIFIED CHANGE | [CEIL] TERMINATE STUCK CYCLES         |                      ||
           |           |  |   [L2.3: Healer   ]  -> [ROOT] CAPTURE ROOT | [RESET] REVERT STATE | [CURE] FIX AND RETRY        |                      ||
           |           +=======================================================================================================+                      ||
           |                                                      |                                                                                   ||
           v                                                      v                                                                                   ||
+------------------------------------------------------------------------------------------------------------------------------+                      ||
| FINAL DECISION / OUTCOME LOGGING (SYNC TEAM MEMORY | RECON DATA MATCHES REALITY)                                             |                      ||
+------------------------------------------------------------------------------------------------------------------------------+                      ||
                                                          |                                                                                           ||
                                                          +===(ZERO-LOSS LOOP: COMMIT TO L4 VIA META-LEARNING BUS)===================================>||

=========================================================================================================================================================
  CRITICAL DISSEMINATION GUARANTEES (5-WORD MAX)
=========================================================================================================================================================
| 1. NO SKIPPING SAFETY GATES | 4. HEALS MUST RE-CLEAR SAFETY | 7. ONLY USE APPROVED TOOLS    | 10. STOP AGENTS BURNING MONEY | 13. REMOVE HIJACK ATTEMPTS |
| 2. ALWAYS ATTACH FENCES     | 5. DON'T LOSE DATA ON ERROR   | 8. BREAK TASKS INTO PIECES    | 11. FRESH DATA ONLY AT RUNTIME| 14. SHARE MEMORY ALL AGENTS|
| 3. LOAD DATA ONLY AS NEEDED | 6. ISOLATE CHANGES IN SANDBOX | 9. PROTECT FROM AGENT DRIFT   | 12. RECORD THE WHY, NOT WHAT  | 15. DOUBLE-CHECK DATA MATCH|
=========================================================================================================================================================