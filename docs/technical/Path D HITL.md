======================================================================================================================================================================
                                          AGENTIC SYSTEM — PATH D: HUMAN-IN-THE-LOOP & DPO FLOW (WIDESCREEN)
======================================================================================================================================================================
  [ L3: ESCALATION TO PATH D ]                       [ THE HUMAN ISOLATION AIRLOCK ]                              [ DOWNSTREAM ROUTING & FEEDBACK ]
======================================================================================================================================================================
+-----------------------------------------+        +--------------------------------------------------------------+ +------------------------------------------------+
| L3: ORCHESTRATOR (REVIEW INITIATION)    |        | HUMAN DECISION GATE (Zero Authority Sandbox)                 | | L5: THE SAFETY GUARD (RE-CLEARANCE)            |
|-----------------------------------------|        |--------------------------------------------------------------| |------------------------------------------------|
| - Prepares Review Artifact.             |=======>| - [ISOLATE] Admin has zero authority to mutate tool          | | - [RE-CLR] All MODIFY_DIFF patches MUST be     |
| - Emits `original_plan_hash`.           |        |   permissions or bypass system invariants directly.          |=|   re-evaluated by the active L5 policies.      |
| - Freezes execution pending decision.   |        |                                                              | | - If Approved -> Mints [AUTH] Stamp.           |
+-----------------------------------------+        | [ THE DECISION MATRIX ]                                      | | - Routes to L2 PTC Sandbox for execution.      |
                                                   | 1. [APPROVE]     -> Fast-tracks to L5 [AUTH] Stamp.          | +------------------------------------------------+
                                                   | 2. [REJECT]      -> Aborts wave, re-routes to L1.            |                      | (Executes)
                                                   | 3. [MODIFY_DIFF] -> Human provides `structured_patch_schema`.|                      v
                                                   |                     MUST reference `original_plan_hash`.     | +------------------------------------------------+
                                                   |                     MUST use only allowlisted tools.         | | L6 / PATH D FEEDBACK: RLHF DPO GENERATION      |
                                                   +--------------------------------------------------------------+ |------------------------------------------------|
                                                                     | (Emits HumanDecisionArtifact)                | 1. Extracts `original_plan` (Control) and      |
                                                                     v                                              |    `human_patch` (Candidate).                  |
                                                   +--------------------------------------------------------------+ | 2. Builds `DPOPair` deterministically.         |
                                                   | [ THE FORCED ROUTING INVARIANT ]                             |=| 3. Routes to Stage 6 Meta-Learning Pipeline.   |
                                                   |--------------------------------------------------------------| | 4. `RLHFOptimizer.propose_from_dpo()` tunes    |
                                                   | - Humans CANNOT push patches directly to L2 Sandbox.         | |    future L3 orchestration weights.            |
                                                   | - Output strictly routed to L5 for Mandatory Re-Clear.       | +------------------------------------------------+
                                                   +--------------------------------------------------------------+
                                                                     | (Forces Patch down the Elevator Shaft)
                                                                     v
======================================================================================================================================================================
  CORE PATH D & DPO DATA CONTRACTS
======================================================================================================================================================================
| [5] HumanDecisionArtifact : [trace_id, policy_hash, reviewer_id, action:[APPROVE|MODIFY|REJECT], patch_schema, sig] -> MODIFY MUST re-clear L5. |
| [13] DPOPair              : [example_id:{control_hash, candidate_hash}, human_decision:APPROVE|REJECT, reasons] -> Built deterministically from Path D. |
| [RLHF] DPO Integration    : dpo_batch_bytes + RLHFOptimizer.propose_from_dpo() -> Emits threshold ChangePackage in Stage 6.                   |
======================================================================================================================================================================
