==================================================================================================================================================
                                    AGENTIC SYSTEM — PATH C: L5 SAFETY & L2 VALIDATOR-HEALER CYCLE
                                              (A+++ ZERO-LOSS WIDESCREEN ASCII OVERWRITE)
==================================================================================================================================================

[ L3: ORCHESTRATION / ROUTED PATH ]
                | - [SHRED] Minimize blast radius via atomic intent
                | - [GATE] Block hallucination before path entry
                | (1. Proposed Action)
                v
+-------------------------------------------------------+                                         +----------------------------------------------+
| L5: SAFETY (ACTIVE GUARDIAN)                          |           (READ / WRITE)                | L4: POLICY & GUARDIAN STATE                  |
|-------------------------------------------------------| <=====================================> | - Guardian Script Definitions                  |
| - Runs BLOCKING guardian scripts                      |                                         | - Policy & Permissions Schema                  |
| - Evaluates Policy + Permissions                      |                                         | - Sandbox Constraints                          |
| - [CONF_CALIB] Risk Gate limits blind execution       |                                         +----------------------------------------------+
| - OUTCOME: ALLOW / BLOCK / ESCALATE                   |
+-------------------------------------------------------+
                |
                | (2. IF ALLOW: approved_action.json)
                v
+-------------------------------------------------------+                                         +----------------------------------------------+
| L2.1: VALIDATOR (PRE-SIDE-EFFECT)                     |               (READ)                    | L4: SCHEMA & SIGNAL STATE                    |
|-------------------------------------------------------| <=====================================> | - Schema Definitions                           |
| - Schema Retrieval & Validation                       |                                         | - Validation Parameters                        |
| - [CID] Restrict unregistered intents                 |                                         | - Historical Validation Signals              |
| - [ZERO_TRUST] Scope minimal tool access              |                                         +----------------------------------------------+
| - Sandbox Dry-run / Diff Analysis                     |
| - EMITS: boundary_snapshot.json (Baseline)            |
+-------------------------------------------------------+
                |                               |
      /-------------------\                     | (3. VALIDATION FAIL: Schema/Sim Error)
      | VALIDATION PASS?  |                     |
      \-------------------/                     |
          |           |                         |
          | YES       \-------------------------|--------------------------+
          v                                     |                          |
+---------------------------------------+       |                          |
| L2.2: EXECUTION (COMMIT AUTHORITY)    |       |                          |
|---------------------------------------|       |                          |
| - RUNS APPROVED ACTION                |       |                          |
| - SOLE DURABLE MUTATION POINT         |       |                          |
| - [QUOTA] Kill infinite compute burn  |       |                          |
| - [FEEDBACK] Inject failure context   |       |                          |
+---------------------------------------+       |                          |
          |                 |                   |                          |
          | SUCCESS         | FAILURE           |                          |
          v                 \-------------------|--------------------------+
+-------------------------------------+         |                          |
| FINAL OUTCOME LOGGING               |         |                          | (4. Error Root / Rollback Req)
|-------------------------------------|         |                          v
| - Outcome versioned                 |         |        +-------------------------------------------------------+
| - [ASYNC_SYNC] Non-blocking state   |         |        | L2.3: HEALER (RECOVERY ENGINE)                        |
| - [RECON] Verify L4 vs reality      |         |        |-------------------------------------------------------|
| - Exits Loop                        |         |        | - [UNDO] Reset state to boundary snapshot             |
+-------------------------------------+         |        | - [CIRCUIT] Kill run to prevent loop limits           |
                                                \======> | - Root Cause Analysis (Diff/Error Log)                |
                                                         | - Correction Strategy Synthesis                       |
                                                         | - EMITS: revised_action_proposal.json                 |
                                                         +-------------------------------------------------------+
                                                                             |
                                                                             | (5. REVISED PROPOSAL ROUTING)
                                                                             v
==================================================================================================================================================
                                    CYCLICAL AUTHORITY RETURN LOOP (RE-ENTER L5)
==================================================================================================================================================
| Any healed/revised plan MUST re-clear L5 Safety before retry. There is zero direct path to Execution from the Healer.                |
| [SEED] Force strict heal determinism during L3 re-entry to prevent non-deterministic hallucination drift.                            |
==================================================================================================================================================